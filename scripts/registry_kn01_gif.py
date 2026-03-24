"""Registry GIF for kn01: generic BFS assumes cardinal moves; knight uses banked L-steps + ACTION5."""

from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Any

from arcengine import GameAction, GameState, Level

from env_resolve import full_game_id_for_stem
from gif_common import append_frame_repeats, offline_arcade
from registry_gif_lib import (
    _cap_gif_frames,
    _frame_layer0,
    _StepAbort,
    registry_bfs_goals,
    safe_env_step,
    walk_blocked,
)

_NUM_TO_ACT: dict[int, GameAction] = {
    1: GameAction.ACTION1,
    2: GameAction.ACTION2,
    3: GameAction.ACTION3,
    4: GameAction.ACTION4,
    5: GameAction.ACTION5,
}

_BANK_A = ((-2, -1), (-2, 1), (2, -1), (2, 1))
_BANK_B = ((-1, -2), (-1, 2), (1, -2), (1, 2))
_BANKS = (_BANK_A, _BANK_B)


def _kn01_bfs_first_action(
    level: Level,
    goals: set[tuple[int, int]],
    start: tuple[int, int, int],
) -> GameAction | None:
    sx, sy, sb = start
    if (sx, sy) in goals:
        return None
    q: deque[tuple[int, int, int]] = deque([start])
    prev: dict[tuple[int, int, int], tuple[tuple[int, int, int], int] | None] = {
        start: None
    }
    found: tuple[int, int, int] | None = None
    w, h = level.grid_size

    while q:
        x, y, b = q.popleft()
        if (x, y) in goals:
            found = (x, y, b)
            break
        nb = 1 - b
        toggle_next = (x, y, nb)
        if toggle_next not in prev:
            prev[toggle_next] = ((x, y, b), 5)
            q.append(toggle_next)
        for i in range(4):
            dx, dy = _BANKS[b][i]
            nx, ny = x + dx, y + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if walk_blocked(level, nx, ny, goals):
                continue
            nxt = (nx, ny, b)
            if nxt not in prev:
                prev[nxt] = ((x, y, b), i + 1)
                q.append(nxt)

    if found is None:
        return None
    cur = found
    while True:
        info = prev[cur]
        assert info is not None
        pstate, act = info
        if pstate == start:
            return _NUM_TO_ACT[act]
        cur = pstate


def _kn01_blocked_move_indices(
    level: Level, goals: set[tuple[int, int]], x: int, y: int, bank: int
) -> list[int]:
    w, h = level.grid_size
    out: list[int] = []
    for i in range(4):
        dx, dy = _BANKS[bank][i]
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h):
            out.append(i + 1)
        elif walk_blocked(level, nx, ny, goals):
            out.append(i + 1)
    return out


def _inject_knight_fails(
    env: Any,
    res: Any,
    level: Level,
    goals: set[tuple[int, int]],
    bank: int,
    snap,
    *,
    count: int = 2,
    hold: int = 3,
) -> Any:
    players = level.get_sprites_by_tag("player")
    if not players:
        return res
    x, y = players[0].x, players[0].y
    blocked = _kn01_blocked_move_indices(level, goals, x, y, bank)
    if not blocked:
        return res
    seq: list[int] = []
    for idx in blocked:
        if len(seq) >= count:
            break
        seq.append(idx)
    while len(seq) < count:
        seq.append(blocked[0])
    for move_i in seq[:count]:
        res = safe_env_step(env, _NUM_TO_ACT[move_i], reasoning={})
        snap(hold)
    return res


def record_kn01_registry_gif(
    game_id: str,
    root: Path,
    *,
    overrides: dict[str, Any] | None = None,
    verbose: bool = False,
    seed: int = 0,
) -> tuple[Any, list]:
    _ = seed
    o = dict(overrides or {})
    max_gif = int(o.get("max_gif_frames", 520))
    target_levels = int(o.get("target_levels", 0)) or 4
    fail_hold = int(o.get("kn01_fail_hold_frames", 5))
    level_hold = int(o.get("kn01_level_hold_frames", 14))

    arc = offline_arcade(root)
    env = arc.make(full_game_id_for_stem(game_id), seed=0, render_mode=None)
    res = env.reset()
    images: list = []

    def snap(times: int) -> None:
        nonlocal res
        fr = _frame_layer0(res)
        if fr:
            append_frame_repeats(images, fr[0], times)

    snap(8)
    n_authored = len(env._game._levels)
    L = min(target_levels, max(1, n_authored))
    fail_done: set[int] = set()
    step_abort = False
    prev_li = env._game.level_index

    try:
        for _tick in range(4000):
            if len(images) > 4000:
                break
            if res.state in (GameState.WIN, GameState.GAME_OVER):
                break
            lc = getattr(res, "levels_completed", 0) or 0
            if lc >= L:
                break

            level = env._game.current_level
            li = env._game.level_index
            goals = registry_bfs_goals(level, game_id)
            bank = int(getattr(env._game, "_bank", 0))
            players = level.get_sprites_by_tag("player")

            if li not in fail_done and players:
                res = _inject_knight_fails(
                    env,
                    res,
                    level,
                    goals,
                    bank,
                    snap,
                    count=2,
                    hold=fail_hold,
                )
                fail_done.add(li)
                snap(2)
                continue

            if not players:
                snap(1)
                continue

            p = players[0]
            act = _kn01_bfs_first_action(level, goals, (p.x, p.y, bank))
            if act is None:
                snap(1)
                break
            res = safe_env_step(env, act, reasoning={})
            snap(1)
            li_now = env._game.level_index
            if li_now != prev_li:
                snap(level_hold)
                prev_li = li_now
    except _StepAbort as ex:
        step_abort = True
        if verbose:
            print(f"  {game_id}: kn01 step abort ({ex})")

    snap(12)
    if step_abort and verbose:
        print(f"  {game_id}: kn01 registry GIF partial, {len(images)} frames")

    _cap_gif_frames(images, max_gif)
    if verbose:
        print(f"  {game_id}: kn01 registry GIF, {len(images)} frames (cap {max_gif})")
    return res, images


REGISTRY_RECORDERS: dict[str, Any] = {"kn01": record_kn01_registry_gif}
