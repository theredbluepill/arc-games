#!/usr/bin/env python3
"""Quick reachability checks for plan-35 movement games (orthogonal BFS on authored level 0).

Does not model game-specific rules (snake body, prime steps, etc.) — those need hand review.
"""

from __future__ import annotations

import sys
from collections import deque
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = _ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from env_resolve import load_stem_game_py  # noqa: E402


def orth_bfs(
    grid_w: int,
    grid_h: int,
    walls: set[tuple[int, int]],
    start: tuple[int, int],
    goal: tuple[int, int],
) -> bool:
    q = deque([start])
    seen = {start}
    while q:
        x, y = q.popleft()
        if (x, y) == goal:
            return True
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            nx, ny = x + dx, y + dy
            if not (0 <= nx < grid_w and 0 <= ny < grid_h):
                continue
            if (nx, ny) in walls:
                continue
            if (nx, ny) not in seen:
                seen.add((nx, ny))
                q.append((nx, ny))
    return False


def wall_set_from_level(mod) -> tuple[int, int, set[tuple[int, int]], tuple[int, int], tuple[int, int]]:
    lv = mod.levels[0]
    gw, gh = lv.grid_size
    walls: set[tuple[int, int]] = set()
    start = goal = (0, 0)
    for s in lv._sprites:
        if "wall" in s.tags:
            walls.add((s.x, s.y))
        if "player" in s.tags:
            start = (s.x, s.y)
        if "goal" in s.tags:
            goal = (s.x, s.y)
    return gw, gh, walls, start, goal


def main() -> int:
    stems = ["rk01", "vp01", "cq01", "tw01", "kb01"]
    for stem in stems:
        mod = load_stem_game_py(stem, f"{stem}_check")
        gw, gh, walls, start, goal = wall_set_from_level(mod)
        ok = orth_bfs(gw, gh, walls, start, goal)
        print(f"{stem} L0 orth-reachable goal: {ok}")
        if not ok:
            return 1
    print("sn01/pm01/jw01: require rule-aware search — not checked here.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
