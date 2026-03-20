#!/usr/bin/env python3
"""Write remaining plan-30 game packages. Run: uv run python scripts/plan30_write_remaining.py"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / "environment_files"


def pkg(stem: str, title: str, desc: str, tags: list[str], grid: list[int], actions: int, py: str) -> None:
    d = ENV / stem / "v1"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{stem}.py").write_text(py.strip() + "\n", encoding="utf-8")
    meta = {
        "game_id": f"{stem}-v1",
        "title": title,
        "description": desc,
        "default_fps": 20,
        "baseline_actions": [15],
        "tags": tags,
        "local_dir": f"environment_files/{stem}/v1",
        "date_created": "2026-03-20",
        "training_metadata": {
            "pcg_type": [],
            "grid_range": grid,
            "action_space": actions,
            "physics_rules": tags[:3] if tags else ["movement"],
            "reward_structure": "checkpoint-on-level-pass",
            "episode_count": 1000000,
        },
        "date_downloaded": "2026-03-20T12:00:00+00:00",
    }
    (d / "metadata.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    names = [
        "plan30_games_body",
        "plan30_games_body2",
        "plan30_games_body3",
        "plan30_games_body4",
    ]
    n = 0
    for name in names:
        path = ROOT / "scripts" / f"{name}.py"
        if not path.is_file():
            continue
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            sys.exit(f"bad {path}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for spec_t in mod.ALL:
            pkg(*spec_t)
            n += 1
    print("wrote", n, "packages under environment_files/")


if __name__ == "__main__":
    main()
