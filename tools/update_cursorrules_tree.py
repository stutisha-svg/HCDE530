"""
Regenerate the directory tree inside .cursorrules between markers.

Uses `git ls-files` when available (respects .gitignore for tracked files).
Falls back to walking the repo root (skipping .git) if not a git repo.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

START = "<!-- DIRECTORY_TREE_START -->"
END = "<!-- DIRECTORY_TREE_END -->"

ROOT = Path(__file__).resolve().parents[1]


def cursorrules_file() -> Path | None:
    """Prefer root `.cursorrules`; use `week2/.cursorrules` if that is where it lives."""
    for candidate in (ROOT / ".cursorrules", ROOT / "week2" / ".cursorrules"):
        if candidate.is_file():
            return candidate
    return None


def git_tracked_and_untracked() -> list[str] | None:
    try:
        r = subprocess.run(
            [
                "git",
                "-C",
                str(ROOT),
                "ls-files",
                "--cached",
                "--others",
                "--exclude-standard",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if r.returncode != 0:
        return None
    lines = [ln.strip().replace("\\", "/") for ln in r.stdout.splitlines() if ln.strip()]
    return sorted(set(lines))


def walk_files() -> list[str]:
    skip = {".git"}
    out: list[str] = []
    for p in ROOT.rglob("*"):
        rel = p.relative_to(ROOT).as_posix()
        if any(part in skip or part.startswith(".git") for part in p.relative_to(ROOT).parts):
            continue
        if p.is_file():
            out.append(rel)
    return sorted(set(out))


def build_tree_lines(paths: list[str]) -> list[str]:
    """One line per path, repo-relative, sorted (unambiguous vs depth-only indent)."""
    return sorted(paths)


def format_block(paths: list[str]) -> str:
    inner = build_tree_lines(paths)
    body = "\n".join(inner) if inner else "(no files listed)"
    return f"{START}\n```\n{body}\n```\n{END}"


def inject_tree(content: str, block: str) -> str:
    if START in content and END in content:
        pre, rest = content.split(START, 1)
        _, post = rest.split(END, 1)
        return pre.rstrip() + "\n\n" + block.strip() + "\n\n" + post.lstrip()
    return content.rstrip() + "\n\n## Directory structure\n\n" + block + "\n"


def main() -> int:
    cursorrules = cursorrules_file()
    if cursorrules is None:
        return 0
    paths = git_tracked_and_untracked()
    if paths is None:
        paths = walk_files()
    block = format_block(paths)
    text = cursorrules.read_text(encoding="utf-8")
    new_text = inject_tree(text, block)
    if new_text != text:
        cursorrules.write_text(new_text, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
