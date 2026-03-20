#!/usr/bin/env python3
"""List GAMES.md preview status and whether linked assets/*.gif files exist."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_games_table(md: str) -> list[tuple[str, str]]:
    """Split markdown table rows on ``|``; keep empty cells (empty Preview is ``''``)."""
    rows: list[tuple[str, str]] = []
    for line in md.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|-"):
            continue
        parts = [p.strip() for p in line.split("|")]
        # leading/trailing empty from outer pipes
        if len(parts) < 9 or parts[1] == "Game":
            continue
        game_id = parts[1]
        if not re.match(r"^[a-z]{2}\d{2}$", game_id):
            continue
        preview_cell = parts[6] if len(parts) > 6 else ""
        rows.append((game_id, preview_cell))
    return rows


def _asset_refs(preview_cell: str) -> list[str]:
    return re.findall(r"assets/([a-z]{2}\d{2})\.gif", preview_cell)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--missing-files",
        action="store_true",
        help="List markdown-linked GIFs with no file on disk",
    )
    parser.add_argument(
        "--empty-preview",
        action="store_true",
        help="List games whose Preview cell has no image markdown",
    )
    args = parser.parse_args()
    root = _repo_root()
    md_path = root / "GAMES.md"
    text = md_path.read_text(encoding="utf-8")
    rows = parse_games_table(text)
    assets_dir = root / "assets"

    empty = [(g, p) for g, p in rows if "![" not in p]
    missing: list[tuple[str, str]] = []
    for g, p in rows:
        for ref in _asset_refs(p):
            if not (assets_dir / f"{ref}.gif").is_file():
                missing.append((ref, f"linked from row {g}"))

    if not args.missing_files and not args.empty_preview:
        print(f"Games in table: {len(rows)}")
        print(f"Empty preview cells: {len(empty)}")
        print(f"Linked GIFs missing on disk: {len(missing)}")
        if empty:
            print("\nEmpty preview game IDs:")
            print(" ".join(g for g, _ in empty))
        if missing:
            print("\nMissing asset files:")
            for ref, why in missing:
                print(f"  {ref}.gif ({why})")
        return

    if args.empty_preview:
        for g, _ in empty:
            print(g)
    if args.missing_files:
        seen: set[str] = set()
        for ref, why in missing:
            if ref in seen:
                continue
            seen.add(ref)
            print(f"{ref}.gif\t{why}")


if __name__ == "__main__":
    main()
