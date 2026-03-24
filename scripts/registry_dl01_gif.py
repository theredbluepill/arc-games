"""Registry GIF for dl01 (delay-line queue): generic BFS ignores pending moves."""

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
    blocked_cardinal_actions,
    goal_positions_set,
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
_DELTA: dict[int, tuple[int, int]] = {
    1: (0, -1),
    2: (0, 1),
    3: (-1, 0),
    4: (1, 0),
}


def _dl01_can_enter(level: Level, x: int, y: int, walk_goals: set[tuple[int, int]]) -> bool:
    w, h = level.grid_size
    if not (0 <= x < w and 0 <= y < h):
        return False
    return not walk_blocked(level, x, y, walk_goals)


def _dl01_simulate_step(
    level: Level,
    walk_goals: set[tuple[int, int]],
    win_goals: set[tuple[int, int]],
    px: int,
    py: int,
    qt: tuple[tuple[int, int], ...],
    act: int,
) -> tuple[tuple[int, int, tuple[tuple[int, int], ...]], bool, bool]:
    """Return (new_state, won, blocked). ``win_goals`` may differ from ``walk_goals`` (nav targets)."""
    if act == 5:
        return (px, py, ()), False, False
    q = deque(qt)
    blocked = False
    if q:
        dx, dy = q.popleft()
        nx, ny = px + dx, py + dy
        if not _dl01_can_enter(level, nx, ny, walk_goals):
            blocked = True
        else:
            px, py = nx, ny
            if (px, py) in win_goals:
                return (px, py, tuple(q)), True, False
    q.append(_DELTA[act])
    while len(q) > 3:
        q.popleft()
    return (px, py, tuple(q)), False, blocked


def _dl01_bfs_first_action(
    level: Level,
    walk_goals: set[tuple[int, int]],
    win_goals: set[tuple[int, int]],
    start: tuple[int, int, tuple[tuple[int, int], ...]],
) -> GameAction | None:
    """Shortest plan in (pos, queue) space; first action toward ``win_goals``."""
    if (start[0], start[1]) in win_goals and not start[2]:
        return None
    q_bfs: deque[tuple[int, int, tuple[tuple[int, int], ...]]] = deque([start])
    seen = {start}
    first_act: dict[tuple[int, int, tuple[tuple[int, int], ...]], int] = {}

    while q_bfs:
        st = q_bfs.popleft()
        px, py, qt = st
        for act in range(1, 6):
            nst, won, _ = _dl01_simulate_step(level, walk_goals, win_goals, px, py, qt, act)
            if won:
                return _NUM_TO_ACT[act if st == start else first_act[st]]
            if nst not in seen:
                seen.add(nst)
                first_act[nst] = act if st == start else first_act[st]
                q_bfs.append(nst)
    return None


def _dl01_next_action(env: Any, *, win_goals: set[tuple[int, int]] | None = None) -> GameAction | None:
    game = env._game
    level = game.current_level
    walk_goals = goal_positions_set(level)
    wg = win_goals if win_goals is not None else walk_goals
    p = game._player
    start = (p.x, p.y, tuple(tuple(t) for t in game._q))
    return _dl01_bfs_first_action(level, walk_goals, wg, start)


def _dl01_navigate_to(env: Any, res: Any, target: set[tuple[int, int]], snap, max_steps: int = 200) -> Any:
    for _ in range(max_steps):
        if (env._game._player.x, env._game._player.y) in target:
            return res
        act = _dl01_next_action(env, win_goals=target)
        if act is None:
            return res
        res = safe_env_step(env, act, reasoning={})
        snap(1)
    return res


def _dl01_inject_two_bumps(
    env: Any,
    res: Any,
    snap,
    *,
    fail_hold: int,
) -> Any:
    """Two queue-driven wall/OOB bumps, then clear queue (ACTION5)."""
    level = env._game.current_level
    walk_goals = goal_positions_set(level)
    p = env._game._player
    pos = (p.x, p.y)
    blocked = blocked_cardinal_actions(level, pos, walk_goals)

    if not blocked:
        tx, ty = pos
        res = _dl01_navigate_to(env, res, {(tx, 0)}, snap)
        p = env._game._player
        pos = (p.x, p.y)
        blocked = blocked_cardinal_actions(level, pos, walk_goals)

    bump_act = blocked[0] if blocked else GameAction.ACTION1
    for _ in range(2):
        res = safe_env_step(env, bump_act, reasoning={})
        snap(2)
    res = safe_env_step(env, GameAction.ACTION5, reasoning={})
    snap(2)
    snap(fail_hold)
    return res


def record_dl01_registry_gif(
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
    fail_hold = int(o.get("dl01_fail_hold_frames", 16))

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

    try:
        for _tick in range(2400):
            if len(images) > 4000:
                break
            if res.state in (GameState.WIN, GameState.GAME_OVER):
                break
            lc = getattr(res, "levels_completed", 0) or 0
            if lc >= L:
                break

            li = env._game.level_index
            if li not in fail_done:
                res = _dl01_inject_two_bumps(env, res, snap, fail_hold=fail_hold)
                fail_done.add(li)
                continue

            act = _dl01_next_action(env)
            if act is None:
                break
            res = safe_env_step(env, act, reasoning={})
            snap(1)
    except _StepAbort as ex:
        step_abort = True
        if verbose:
            print(f"  {game_id}: dl01 step abort ({ex})")

    snap(10)
    if step_abort and verbose:
        print(f"  {game_id}: dl01 registry GIF partial, {len(images)} frames")

    _cap_gif_frames(images, max_gif)
    if verbose:
        print(f"  {game_id}: dl01 registry GIF, {len(images)} frames (cap {max_gif})")
    return res, images


DL01_REGISTRY_RECORDERS: dict[str, Any] = {"dl01": record_dl01_registry_gif}
