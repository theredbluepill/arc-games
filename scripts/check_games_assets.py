#!/usr/bin/env python3
"""Exit non-zero if GAMES.md references a preview GIF that is missing on disk."""

from __future__ import annotations

import sys
from pathlib import Path

from gif_inventory import parse_games_table


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    md = (root / "GAMES.md").read_text(encoding="utf-8")
    assets = root / "assets"
    empty: list[str] = []
    missing: list[str] = []
    for gid, preview in parse_games_table(md):
        if "![" not in preview.strip():
            empty.append(gid)
            continue
        if not (assets / f"{gid}.gif").is_file():
            missing.append(gid)
    if empty:
        print("Rows with empty Preview column:", ", ".join(empty), file=sys.stderr)
    if missing:
        print("Missing assets/*.gif for:", ", ".join(missing), file=sys.stderr)
    if empty or missing:
        sys.exit(1)
    print("All GAMES.md preview GIFs present.")


if __name__ == "__main__":
    main()
