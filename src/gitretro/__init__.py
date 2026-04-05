import subprocess
import time
from pathlib import Path

import rich_click as click
from google.genai.errors import ClientError
from rich import print
from rich.table import Table

from . import gemini, git, mdbook, prompts

_HTTP_TOO_MANY_REQUESTS = 429
_MAX_RETRY_DELAY = 300

RETRO_DIR = Path(".gitretro")


def parse_range(range_: str) -> tuple[str, str]:
    if ".." not in range_:
        msg = "must be in format <from>..<to>"
        raise click.BadParameter(msg)
    from_, to_ = range_.split("..", 1)
    return git.rev_parse(from_), git.rev_parse(to_)


def _parse_retry_delay(e: ClientError) -> int:
    for detail in e.details or []:
        if not isinstance(detail, dict):
            continue
        if detail.get("@type", "").endswith("RetryInfo"):
            raw = detail.get("retryDelay", "")
            if raw.rstrip("s").isdigit():
                return int(raw.rstrip("s"))
    return _MAX_RETRY_DELAY


def _generate_with_retry(file: str, diff: str) -> str | None:
    try:
        while True:
            account, client, wait = gemini.pick_with_wait()
            if wait > 0:
                if wait >= _MAX_RETRY_DELAY:
                    print(
                        f"[yellow]All accounts rate limited, delay too long"
                        f" ({wait:.0f}s), skipping {file}[/yellow]"
                    )
                    return None
                print(
                    f"[yellow]All accounts rate limited,"
                    f" waiting {wait:.0f}s for {account.email}...[/yellow]"
                )
                time.sleep(wait)
            try:
                res = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompts.DIFF.format(diff=diff),
                )
            except ClientError as e:
                if e.code != _HTTP_TOO_MANY_REQUESTS:
                    raise
                delay = _parse_retry_delay(e)
                gemini.mark_rate_limited(account.email, delay)
                print(
                    f"[yellow]Rate limited on {account.email}"
                    f" for {delay}s, switching account...[/yellow]"
                )
            else:
                return res.text or ""
    except ClientError as e:
        print(f"[red]API error for {file}: {e}[/red]")
        return None


@click.group()
def main() -> None:
    pass


@main.command()
@click.argument("range_", metavar="<from>..<to>")
@click.option("--force", is_flag=True, help="overwrite existing retrospective")
def create(range_: str, force: bool) -> None:
    from_, to_ = parse_range(range_)
    from_short = git.rev_parse_short(from_)
    to_short = git.rev_parse_short(to_)
    retro_dir = RETRO_DIR / f"retro-{from_short}-{to_short}"
    if retro_dir.exists() and not force:
        print(f"[red]Retrospective already exists: {retro_dir}[/red]")
        raise SystemExit(1)
    files = git.diff_names(from_, to_)
    contents: dict[str, str] = {}
    for file in files:
        print(f"[cyan]Generating {file}...[/cyan]")
        content = _generate_with_retry(file, git.diff_patch(from_, to_, file))
        if content is not None:
            contents[file] = content
    mdbook.create(retro_dir, files, contents)
    print(f"[green]Retrospective written to {retro_dir}[/green]")


@main.command()
@click.argument("range_", metavar="<from>..<to>")
def serve(range_: str) -> None:
    from_, to_ = parse_range(range_)
    from_short = git.rev_parse_short(from_)
    to_short = git.rev_parse_short(to_)
    retro_dir = RETRO_DIR / f"retro-{from_short}-{to_short}"
    mdbook.serve(retro_dir)


@main.command(name="list")
def list_() -> None:
    if not RETRO_DIR.exists():
        print("[yellow]No retrospectives found.[/yellow]")
        return
    retros = sorted(RETRO_DIR.glob("retro-*-*"))
    if not retros:
        print("[yellow]No retrospectives found.[/yellow]")
        return
    table = Table(show_header=True, header_style="bold")
    table.add_column("range")
    table.add_column("commits")
    for retro in retros:
        name = retro.name[len("retro-") :]
        from_short, to_short = name.split("-", 1)
        range_str = f"{from_short}..{to_short}"
        try:
            commits = git.log_oneline(from_short, to_short)
            commits_str = "\n".join(commits)
        except subprocess.CalledProcessError:
            commits_str = ""
        table.add_row(range_str, commits_str)
    print(table)
