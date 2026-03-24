"""Registry GIF for fw01 (wildfire + splash): scripted fail on fire, reset, clear + exit, level-2 burn."""

from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Any

from arcengine import GameAction, GameState, Level

from env_resolve import full_game_id_for_stem
from gif_common import append_frame_repeats, grid_cell_center_display, offline_arcade
from registry_gif_lib import _cap_gif_frames, safe_env_step

_DELTA_ACT: dict[tuple[int, int], GameAction] = {
    (0, -1): GameAction.ACTION1,
    (0, 1): GameAction.ACTION2,
    (-1, 0): GameAction.ACTION3,
    (1, 0): GameAction.ACTION4,
}


def _frame0(res: Any) -> list:
    return getattr(res, "frame", None) or []


def _walls(level: Level) -> set[tuple[int, int]]:
    return {(s.x, s.y) for s in level.get_sprites() if "wall" in s.tags}


def _fires(level: Level) -> set[tuple[int, int]]:
    return {(s.x, s.y) for s in level.get_sprites_by_tag("fire")}


def _fw_bfs_moves(
    walls: set[tuple[int, int]],
    start: tuple[int, int],
    goal: tuple[int, int],
    gw: int,
    gh: int,
    *,
    forbidden: set[tuple[int, int]],
) -> list[GameAction] | None:
    if start == goal:
        return []
    q: deque[tuple[int, int]] = deque([start])
    prev: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    while q:
        x, y = q.popleft()
        if (x, y) == goal:
            out: list[GameAction] = []
            cx, cy = x, y
            while prev[(cx, cy)] is not None:
                px, py = prev[(cx, cy)]
                dx, dy = cx - px, cy - py
                out.append(_DELTA_ACT[(dx, dy)])
                cx, cy = px, py
            out.reverse()
            return out
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            nx, ny = x + dx, y + dy
            if not (0 <= nx < gw and 0 <= ny < gh):
                continue
            if (nx, ny) in walls or (nx, ny) in forbidden:
                continue
            if (nx, ny) not in prev:
                prev[(nx, ny)] = (x, y)
                q.append((nx, ny))
    return None


def record_fw01_registry_gif(
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
    level_hold = int(o.get("fw01_level_hold_frames", 20))
    move_rep = int(o.get("fw01_move_repeat_frames", 2))
    splash_rep = int(o.get("fw01_splash_repeat_frames", 3))

    arc = offline_arcade(root)
    env = arc.make(full_game_id_for_stem(game_id), seed=0, render_mode=None)
    res = env.reset()
    images: list = []

    def snap(times: int) -> None:
        fr = _frame0(res)
        if fr:
            append_frame_repeats(images, fr[0], times)

    def step_act(act: GameAction, *, data: dict | None = None, rep: int = move_rep) -> None:
        nonlocal res
        res = safe_env_step(env, act, reasoning={}, data=data or {})
        snap(rep)

    snap(8)

    # Fail 1 — L0: walk onto the mid-line fire (HUD game-over bar).
    for _ in range(13):
        step_act(GameAction.ACTION4)
    snap(20)
    res = env.reset()
    snap(10)

    # L0 solve: splash fire cell, walk to goal.
    gw, gh = env._game.current_level.grid_size
    cx, cy = grid_cell_center_display(15, 12, grid_w=gw, grid_h=gh)
    step_act(GameAction.ACTION6, data={"x": cx, "y": cy}, rep=splash_rep)
    for _ in range(18):
        step_act(GameAction.ACTION4)
    snap(level_hold)

    # Fail 2 — L1: path beside (10,10), then step into fire (spread may grow during walk).
    if res.state not in (GameState.GAME_OVER,) and env._game.level_index == 1:
        lv = env._game.current_level
        walls = _walls(lv)
        forb = _fires(lv)
        px, py = env._game._player.x, env._game._player.y
        # Approach (10,10) from the west; last move east onto the fire tile.
        approach = (9, 10)
        if (10, 10) in forb and approach not in forb:
            plan = _fw_bfs_moves(
                walls, (px, py), approach, gw, gh, forbidden=forb
            )
            if plan is not None:
                for a in plan:
                    step_act(a)
                step_act(GameAction.ACTION4)
                snap(20)

    snap(12)
    _cap_gif_frames(images, max_gif)
    if verbose:
        print(f"  {game_id}: fw01 registry GIF, {len(images)} frames")
    return res, images


REGISTRY_RECORDERS: dict[str, Any] = {
    "fw01": record_fw01_registry_gif,
}
