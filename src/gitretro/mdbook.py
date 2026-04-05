from pathlib import Path

from .command import Command


def serve(retro_dir: Path) -> None:
    Command.from_which("mdbook").args("serve", "--open", str(retro_dir)).run()


def create(retro_dir: Path, files: list[str], contents: dict[str, str]) -> None:
    src = retro_dir / "src"
    src.mkdir(parents=True, exist_ok=True)
    (retro_dir / "book.toml").write_text(
        '[book]\ntitle = "Retrospective"\nsrc = "src"\n'
    )
    (src / "README.md").write_text("# Retrospective\n")
    summary_lines = ["# Summary\n", "\n- [Overview](./README.md)\n"]
    seen_dirs: set[str] = set()
    for file in files:
        md_path = Path(file + ".md")
        parts = file.split("/")
        for depth in range(1, len(parts)):
            dir_path = "/".join(parts[:depth])
            if dir_path not in seen_dirs:
                seen_dirs.add(dir_path)
                indent = "    " * (depth - 1)
                label = parts[depth - 1]
                stub = src / Path(dir_path + "/README.md")
                stub.parent.mkdir(parents=True, exist_ok=True)
                stub.write_text(f"# {label}\n")
                summary_lines.append(f"{indent}- [{label}](./{dir_path}/README.md)\n")
        indent = "    " * (len(parts) - 1)
        label = parts[-1]
        summary_lines.append(f"{indent}- [{label}](./{md_path})\n")
        dest = src / md_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(contents.get(file, ""))
    (src / "SUMMARY.md").write_text("".join(summary_lines))
