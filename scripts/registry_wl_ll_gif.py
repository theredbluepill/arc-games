"""Registry GIF capture for wl01 (bridge chasms + walk) and ll01 (Conway + toggles)."""

from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Any

from arcengine import GameAction, GameState, Level
from env_resolve import full_game_id_for_stem
from gif_common import append_frame_repeats, grid_cell_center_display, offline_arcade
from registry_gif_lib import _cap_gif_frames, _frame_layer0, _StepAbort, safe_env_step

# --- wl01 ---


def _wl01_chasm_positions(level: Level) -> list[tuple[int, int]]:
    pts = sorted({(s.x, s.y) for s in level.get_sprites_by_tag("chasm")})
    return pts


def _wl01_goal(level: Level) -> tuple[int, int]:
    g = level.get_sprites_by_tag("goal")[0]
    return (g.x, g.y)


def _wl01_player_pos(level: Level) -> tuple[int, int]:
    p = level.get_sprites_by_tag("player")[0]
    return (p.x, p.y)


def _wl01_walkable(level: Level, x: int, y: int) -> bool:
    sp = level.get_sprite_at(x, y, ignore_collidable=True)
    if sp is None:
        return True
    if "wall" in sp.tags or "hazard" in sp.tags or "chasm" in sp.tags:
        return False
    return True


def _wl01_bfs_path_to_adjacent_hazard(
    level: Level, start: tuple[int, int], hazard: tuple[int, int]
) -> list[int] | None:
    """Path of UDLR ints so the last step enters ``hazard`` (one step before is ortho-adjacent)."""
    hx, hy = hazard
    gw, gh = level.grid_size
    best: list[int] | None = None
    for dx, dy, a_last in ((1, 0, 4), (-1, 0, 3), (0, 1, 2), (0, -1, 1)):
        bx, by = hx - dx, hy - dy
        if not (0 <= bx < gw and 0 <= by < gh):
            continue
        if not _wl01_walkable(level, bx, by):
            continue
        sub = _wl01_bfs_path(level, start, (bx, by))
        if sub is not None:
            cand = sub + [a_last]
            if best is None or len(cand) < len(best):
                best = cand
    return best


def _wl01_bfs_path(level: Level, start: tuple[int, int], goal: tuple[int, int]) -> list[int] | None:
    """Return list of action ints 1–4 (UDLR) from start to goal, or None."""
    gw, gh = level.grid_size
    if start == goal:
        return []
    deltas = [(-1, 0, 3), (1, 0, 4), (0, -1, 1), (0, 1, 2)]
    q: deque[tuple[int, int]] = deque([start])
    prev: dict[tuple[int, int], tuple[tuple[int, int], int] | None] = {start: None}
    while q:
        x, y = q.popleft()
        if (x, y) == goal:
            out: list[int] = []
            cur: tuple[int, int] | None = goal
            while cur is not None and cur != start:
                p = prev.get(cur)
                if p is None:
                    break
                par, act = p
                out.append(act)
                cur = par
            out.reverse()
            return out
        for dx, dy, act in deltas:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < gw and 0 <= ny < gh):
                continue
            if not _wl01_walkable(level, nx, ny):
                continue
            if (nx, ny) in prev:
                continue
            prev[(nx, ny)] = ((x, y), act)
            q.append((nx, ny))
    return None


_ACT_MAP: dict[int, GameAction] = {
    1: GameAction.ACTION1,
    2: GameAction.ACTION2,
    3: GameAction.ACTION3,
    4: GameAction.ACTION4,
}


def _wl01_click6(env: Any, gx: int, gy: int) -> Any:
    level = env._game.current_level
    gw, gh = level.grid_size
    cx, cy = grid_cell_center_display(gx, gy, grid_w=gw, grid_h=gh)
    return safe_env_step(env, GameAction.ACTION6, reasoning={}, data={"x": cx, "y": cy})


def record_wl01_registry_gif(
    game_id: str,
    root: Path,
    *,
    overrides: dict[str, Any] | None = None,
    verbose: bool = False,
    seed: int = 0,
) -> tuple[Any, list]:
    _ = seed
    o = dict(overrides or {})
    max_gif = int(o.get("max_gif_frames", 900))
    level_hold = int(o.get("wl01_level_hold_frames", 20))
    target_levels = int(o.get("target_levels", 0)) or 4

    arc = offline_arcade(root)
    env = arc.make(full_game_id_for_stem(game_id), seed=0, render_mode=None)
    res = env.reset()
    images: list = []

    def snap_repeats(times: int) -> None:
        nonlocal res
        fr = _frame_layer0(res)
        if fr:
            append_frame_repeats(images, fr[0], times)

    snap_repeats(8)
    step_abort = False

    try:
        # Fail 1: level 1 — walk into chasm.
        for _ in range(4):
            res = safe_env_step(env, GameAction.ACTION4, reasoning={})
            snap_repeats(2)
        res = safe_env_step(env, GameAction.ACTION4, reasoning={})
        snap_repeats(16)
        res = env.reset()
        snap_repeats(10)

        # Clear early levels, then fail 2 on first hazard level (index 2).
        hazard_fail_level = 2
        while (
            res.state not in (GameState.GAME_OVER,)
            and env._game.level_index < hazard_fail_level
        ):
            level = env._game.current_level
            for gx, gy in _wl01_chasm_positions(level):
                res = _wl01_click6(env, gx, gy)
                snap_repeats(2)
            start = _wl01_player_pos(level)
            goal = _wl01_goal(level)
            path = _wl01_bfs_path(level, start, goal)
            if path is None:
                if verbose:
                    print(f"  {game_id}: no BFS path on level {env._game.level_index}")
                break
            for a in path:
                res = safe_env_step(env, _ACT_MAP[a], reasoning={})
                snap_repeats(2)
            snap_repeats(level_hold)

        # Fail 2: bridge first, then step into red hazard (level index 2).
        if res.state not in (GameState.GAME_OVER,) and env._game.level_index == hazard_fail_level:
            level = env._game.current_level
            for gx, gy in _wl01_chasm_positions(level):
                res = _wl01_click6(env, gx, gy)
                snap_repeats(2)
            level = env._game.current_level
            hz = [(s.x, s.y) for s in level.get_sprites_by_tag("hazard")]
            if hz:
                start = _wl01_player_pos(level)
                path2 = _wl01_bfs_path_to_adjacent_hazard(level, start, hz[0])
                if path2:
                    for a in path2:
                        res = safe_env_step(env, _ACT_MAP[a], reasoning={})
                        snap_repeats(2)
                    snap_repeats(18)

        # Optional: continue clearing if not game over and user asked more levels.
        while (
            res.state not in (GameState.GAME_OVER, GameState.WIN)
            and (getattr(res, "levels_completed", 0) or 0) < target_levels
        ):
            level = env._game.current_level
            for gx, gy in _wl01_chasm_positions(level):
                res = _wl01_click6(env, gx, gy)
                snap_repeats(2)
            start = _wl01_player_pos(level)
            goal = _wl01_goal(level)
            path = _wl01_bfs_path(level, start, goal)
            if path is None:
                break
            for a in path:
                res = safe_env_step(env, _ACT_MAP[a], reasoning={})
                snap_repeats(2)
            snap_repeats(level_hold)
    except _StepAbort as ex:
        step_abort = True
        if verbose:
            print(f"  {game_id}: wl01 step abort ({ex})")

    snap_repeats(12)
    _cap_gif_frames(images, max_gif)
    if verbose:
        print(f"  {game_id}: wl01 registry GIF, {len(images)} frames")
    return res, images


# --- ll01 (Conway + toggle + advance) ---


def _ll_neighbors8(x: int, y: int, alive: set[tuple[int, int]]) -> int:
    c = 0
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            if (x + dx, y + dy) in alive:
                c += 1
    return c


def _ll_conway_step(alive: set[tuple[int, int]], walls: set[tuple[int, int]], gw: int, gh: int) -> set[tuple[int, int]]:
    nxt: set[tuple[int, int]] = set()
    cand: set[tuple[int, int]] = set(alive)
    for x, y in alive:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < gw and 0 <= ny < gh:
                    cand.add((nx, ny))
    for x, y in cand:
        if (x, y) in walls:
            continue
        n = _ll_neighbors8(x, y, alive)
        live = (x, y) in alive
        if live and n in (2, 3):
            nxt.add((x, y))
        elif not live and n == 3:
            nxt.add((x, y))
    return nxt


def _ll01_parse_level(level: Level) -> tuple[set[tuple[int, int]], set[tuple[int, int]], int, int]:
    walls: set[tuple[int, int]] = set()
    for s in level.get_sprites():
        if "wall" in s.tags:
            walls.add((s.x, s.y))
    raw = level.get_data("target_cells") or []
    target = {tuple(int(t) for t in p) for p in raw}
    need = int(level.get_data("need_generations") or 1)
    max_tog = int(level.get_data("max_toggles") or 100)
    return walls, target, need, max_tog


def _ll01_wall_set(level: Level) -> set[tuple[int, int]]:
    return {(s.x, s.y) for s in level.get_sprites() if "wall" in s.tags}


def _ll01_toggle_cell_options(
    level: Level, gw: int, gh: int, *, widen: int = 0
) -> list[tuple[int, int]]:
    """Patches around each target anchor; ``widen`` 0=tight 4×4, 1=6×6, 2=Manhattan≤9 from targets."""
    wall_set = _ll01_wall_set(level)
    allow: set[tuple[int, int]] = set()
    anchors = [tuple(int(t) for t in p) for p in (level.get_data("target_anchors") or [])]
    span = 2 + widen
    for ax, ay in anchors:
        for dx in range(-span, span + 2):
            for dy in range(-span, span + 2):
                x, y = ax + dx, ay + dy
                if 0 <= x < gw and 0 <= y < gh and (x, y) not in wall_set:
                    allow.add((x, y))
    if not allow and level.get_data("target_cells"):
        raw = level.get_data("target_cells") or []
        xs = [int(p[0]) for p in raw]
        ys = [int(p[1]) for p in raw]
        pad = 2
        for y in range(max(0, min(ys) - pad), min(gh, max(ys) + pad + 1)):
            for x in range(max(0, min(xs) - pad), min(gw, max(xs) + pad + 1)):
                if (x, y) not in wall_set:
                    allow.add((x, y))
    return sorted(allow)


def _ll01_toggle_target_plus_neighbors(level: Level, gw: int, gh: int) -> list[tuple[int, int]]:
    wall_set = _ll01_wall_set(level)
    raw = level.get_data("target_cells") or []
    tgt = {tuple(int(t) for t in p) for p in raw}
    allow: set[tuple[int, int]] = set()
    for x, y in tgt:
        allow.add((x, y))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in wall_set:
                allow.add((nx, ny))
    return sorted(allow)


def _ll01_bfs_solve(
    walls: set[tuple[int, int]],
    target: set[tuple[int, int]],
    need: int,
    max_toggles: int,
    toggle_cells: list[tuple[int, int]],
    gw: int,
    gh: int,
    visit_cap: int,
) -> list[tuple[str, int, int]] | None:
    start = (frozenset(), 0, max_toggles)
    q: deque[tuple[frozenset, int, int]] = deque([start])
    came_from: dict[tuple[frozenset, int, int], tuple[tuple[frozenset, int, int], tuple[str, int, int]]] = {}
    visits = 0
    win_prev: tuple[frozenset, int, int] | None = None

    while q and visits < visit_cap:
        alive_f, gen, tog_left = q.popleft()
        visits += 1
        alive = set(alive_f)

        if gen < need:
            na = _ll_conway_step(alive, walls, gw, gh)
            ng = gen + 1
            if ng == need and na == target:
                win_prev = (alive_f, gen, tog_left)
                break
            if ng < need:
                key = (frozenset(na), ng, tog_left)
                if key not in came_from:
                    came_from[key] = ((alive_f, gen, tog_left), ("5", 0, 0))
                    q.append(key)

        if tog_left > 0:
            for x, y in toggle_cells:
                nxt = set(alive)
                if (x, y) in nxt:
                    nxt.remove((x, y))
                else:
                    nxt.add((x, y))
                key = (frozenset(nxt), gen, tog_left - 1)
                if key not in came_from:
                    came_from[key] = ((alive_f, gen, tog_left), ("6", x, y))
                    q.append(key)

    if win_prev is None:
        return None

    seq: list[tuple[str, int, int]] = []
    cur: tuple[frozenset, int, int] | None = win_prev
    while cur is not None and cur != start:
        prev_op = came_from.get(cur)
        if prev_op is None:
            return None
        prev, op = prev_op
        seq.append(op)
        cur = prev
    seq.reverse()
    return seq + [("5", 0, 0)]


def _ll01_cap_toggle_cells(
    cells: list[tuple[int, int]], target: set[tuple[int, int]], max_n: int
) -> list[tuple[int, int]]:
    if len(cells) <= max_n or not target:
        return cells
    cx = sum(p[0] for p in target) / len(target)
    cy = sum(p[1] for p in target) / len(target)
    ranked = sorted(cells, key=lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2)
    return ranked[:max_n]


def _ll01_search_plan(level: Level, gw: int, gh: int) -> list[tuple[str, int, int]] | None:
    """Return ops ('6',x,y) / ('5',0,0); None if search fails."""
    walls, target, need, max_toggles = _ll01_parse_level(level)
    attempts: list[tuple[list[tuple[int, int]], int]] = []
    for widen in (0, 1):
        cells = _ll01_toggle_cell_options(level, gw, gh, widen=widen)
        if cells:
            cells = _ll01_cap_toggle_cells(cells, target, max_n=36)
            cap = 70_000 if widen == 0 else 100_000
            attempts.append((cells, cap))
    raw_tc = level.get_data("target_cells") or []
    if len(raw_tc) <= 4:
        ring = _ll01_toggle_target_plus_neighbors(level, gw, gh)
        if ring:
            attempts.append((_ll01_cap_toggle_cells(ring, target, max_n=24), 80_000))
    seen: set[tuple[tuple[int, int], ...]] = set()
    for cells, cap in attempts:
        key = tuple(cells)
        if key in seen:
            continue
        seen.add(key)
        got = _ll01_bfs_solve(
            walls, target, need, max_toggles, list(cells), gw, gh, cap
        )
        if got is not None:
            return got
    return None


def _ll01_click6(env: Any, gx: int, gy: int) -> Any:
    level = env._game.current_level
    gw, gh = level.grid_size
    cx, cy = grid_cell_center_display(gx, gy, grid_w=gw, grid_h=gh)
    return safe_env_step(env, GameAction.ACTION6, reasoning={}, data={"x": cx, "y": cy})


def record_ll01_registry_gif(
    game_id: str,
    root: Path,
    *,
    overrides: dict[str, Any] | None = None,
    verbose: bool = False,
    seed: int = 0,
) -> tuple[Any, list]:
    _ = seed
    o = dict(overrides or {})
    max_gif = int(o.get("max_gif_frames", 1100))
    level_hold = int(o.get("ll01_level_hold_frames", 22))
    solve_n = int(o.get("ll01_solve_levels", 0)) or int(o.get("target_levels", 0)) or 2

    arc = offline_arcade(root)
    env = arc.make(full_game_id_for_stem(game_id), seed=0, render_mode=None)
    res = env.reset()
    images: list = []
    n_levels = len(env._game._levels)

    def snap_repeats(times: int) -> None:
        nonlocal res
        fr = _frame_layer0(res)
        if fr:
            append_frame_repeats(images, fr[0], times)

    snap_repeats(8)
    step_abort = False
    gw, gh = 32, 32

    try:
        # Fail 1: advance N times from empty — final generation check fails (HUD shows wrong state).
        lv0 = env._game.current_level
        _, _, need0, _ = _ll01_parse_level(lv0)
        for _ in range(need0):
            res = safe_env_step(env, GameAction.ACTION5, reasoning={})
            snap_repeats(2)
        snap_repeats(18)
        res = env.reset()
        snap_repeats(10)

        cleared = 0
        while cleared < min(solve_n, n_levels) and res.state not in (
            GameState.GAME_OVER,
            GameState.WIN,
        ):
            level = env._game.current_level
            plan = _ll01_search_plan(level, gw, gh)
            if plan is None:
                if verbose:
                    print(f"  {game_id}: ll01 no plan for level {env._game.level_index}")
                break
            for op in plan:
                if op[0] == "6":
                    res = _ll01_click6(env, op[1], op[2])
                else:
                    res = safe_env_step(env, GameAction.ACTION5, reasoning={})
                snap_repeats(2)
            snap_repeats(level_hold)
            cleared += 1

        # Fail 2: on next level, burn exact-N advances from empty (visible lose on HUD check).
        if (
            res.state not in (GameState.GAME_OVER,)
            and env._game.level_index < n_levels
        ):
            _, _, need_l, _ = _ll01_parse_level(env._game.current_level)
            for _ in range(need_l):
                res = safe_env_step(env, GameAction.ACTION5, reasoning={})
                snap_repeats(2)
            snap_repeats(18)

    except _StepAbort as ex:
        step_abort = True
        if verbose:
            print(f"  {game_id}: ll01 step abort ({ex})")

    snap_repeats(12)
    _cap_gif_frames(images, max_gif)
    if verbose:
        print(f"  {game_id}: ll01 registry GIF, {len(images)} frames")
    return res, images


REGISTRY_RECORDERS: dict[str, Any] = {
    "wl01": record_wl01_registry_gif,
    "ll01": record_ll01_registry_gif,
}
