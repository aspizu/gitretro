from .command import Command

cli = Command.from_which("git")


def rev_parse(ref: str) -> str:
    return cli.cmd("rev-parse").args(ref).output()


def rev_parse_short(ref: str) -> str:
    return cli.cmd("rev-parse").args("--short", ref).output()


def diff_names(from_: str, to_: str) -> list[str]:
    return cli.cmd("diff").args("--name-only", f"{from_}..{to_}").output().splitlines()


def diff_patch(from_: str, to_: str, file: str) -> str:
    return cli.cmd("diff --patch").args(f"{from_}..{to_}", file).output()


def log_oneline(from_: str, to_: str) -> list[str]:
    return cli.cmd("log").args("--oneline", f"{from_}..{to_}").output().splitlines()
