#!/usr/bin/env python3
"""Emit stem → ``record_registry_gif`` dispatch bucket CSV (see ``registry_gif_dispatch_bucket``)."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO / "scripts"))

from registry_gif_lib import registry_gif_dispatch_bucket  # noqa: E402


def _parse_games_md(path: Path) -> list[tuple[str, str]]:
    """Return (stem, actions_column) for each data row."""
    text = path.read_text(encoding="utf-8")
    rows: list[tuple[str, str]] = []
    for line in text.splitlines():
        if not line.startswith("| "):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 8:
            continue
        stem = parts[1]
        if not re.fullmatch(r"[a-z]{2}\d{2}", stem):
            continue
        actions = parts[7] if len(parts) > 7 else ""
        rows.append((stem, actions))
    return rows


def _load_override_stems(path: Path) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return set(data.keys())


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--games-md",
        type=Path,
        default=_REPO / "GAMES.md",
        help="Path to GAMES.md",
    )
    ap.add_argument(
        "--overrides",
        type=Path,
        default=_REPO / "scripts" / "registry_gif_overrides.json",
        help="Path to registry_gif_overrides.json",
    )
    ap.add_argument(
        "-o",
        "--output",
        type=Path,
        default=_REPO / "devtools" / "registry_gif_dispatch.csv",
        help="Output CSV path",
    )
    args = ap.parse_args()

    override_stems = _load_override_stems(args.overrides)
    rows = _parse_games_md(args.games_md)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "stem",
                "dispatch_bucket",
                "has_registry_override",
                "actions_uses_click_or_action6",
                "actions_column",
            ]
        )
        for stem, actions_col in rows:
            bucket = registry_gif_dispatch_bucket(stem)
            clickish = bool(
                re.search(r"\b6\s*:", actions_col, re.I)
                or re.search(r"ACTION6", actions_col, re.I)
                or re.search(r"Click", actions_col, re.I)
            )
            w.writerow(
                [
                    stem,
                    bucket,
                    "yes" if stem in override_stems else "no",
                    "yes" if clickish else "no",
                    actions_col.replace("\n", " ").strip(),
                ]
            )

    generic_click = sum(
        1
        for s, a in rows
        if registry_gif_dispatch_bucket(s) == "generic"
        and (
            re.search(r"\b6\s*:", a, re.I)
            or re.search(r"ACTION6", a, re.I)
            or re.search(r"Click", a, re.I)
        )
    )
    print(f"Wrote {args.output} ({len(rows)} stems).")
    print(f"generic + click/ACTION6 hint: {generic_click} stems")


if __name__ == "__main__":
    main()
