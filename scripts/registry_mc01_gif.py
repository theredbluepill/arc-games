"""Registry GIF for mc01: tandem pair + lead order; generic BFS tracks only one ``player``."""

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
    safe_env_step,
)

_NUM_TO_ACT: dict[int, GameAction] = {
    1: GameAction.ACTION1,
    2: GameAction.ACTION2,
    3: GameAction.ACTION3,
    4: GameAction.ACTION4,
    5: GameAction.ACTION5,
}

_MOVE_DELTAS: dict[int, tuple[int, int]] = {
    1: (0, -1),
    2: (0, 1),
    3: (-1, 0),
    4: (1, 0),
}


def _mc01_cell_blocks_move(
    level: Level,
    gw: int,
    gh: int,
    nx: int,
    ny: int,
    self_xy: tuple[int, int],
    other_xy: tuple[int, int],
) -> bool:
    if not (0 <= nx < gw and 0 <= ny < gh):
        return True
    sp = level.get_sprite_at(nx, ny, ignore_collidable=True)
    if not sp:
        return False
    if "wall" in sp.tags:
        return True
    if "player" in sp.tags and (nx, ny) == other_xy:
        return True
    return False


def _mc01_apply_action(
    level: Level,
    a: int,
    b: int,
    c: int,
    d: int,
    lead: int,
    act: int,
) -> tuple[int, int, int, int, int] | None:
    gw, gh = level.grid_size
    if act == 5:
        return (a, b, c, d, 1 - lead)
    if act not in (1, 2, 3, 4):
        return None
    dx, dy = _MOVE_DELTAS[act]
    if lead == 0:
        o0, o1 = (a, b), (c, d)
    else:
        o0, o1 = (c, d), (a, b)
    t1 = (o0[0] + dx, o0[1] + dy)
    t2 = (o1[0] + dx, o1[1] + dy)
    if t1 == o1 and t2 == o0:
        return (c, d, a, b, lead)
    if _mc01_cell_blocks_move(level, gw, gh, t1[0], t1[1], o0, o1) or _mc01_cell_blocks_move(
        level, gw, gh, t2[0], t2[1], o1, o0
    ):
        return None
    if lead == 0:
        return (t1[0], t1[1], t2[0], t2[1], lead)
    return (t2[0], t2[1], t1[0], t1[1], lead)


def _mc01_goal_tuple(level: Level) -> tuple[int, int, int, int]:
    g1 = level.get_sprites_by_tag("g1")[0]
    g2 = level.get_sprites_by_tag("g2")[0]
    return (g1.x, g1.y, g2.x, g2.y)


def _mc01_is_goal(state: tuple[int, int, int, int, int], goal4: tuple[int, int, int, int]) -> bool:
    a, b, c, d, _ = state
    return (a, b, c, d) == goal4


def _mc01_bfs_first_action(
    level: Level,
    start: tuple[int, int, int, int, int],
    goal4: tuple[int, int, int, int],
) -> GameAction | None:
    if _mc01_is_goal(start, goal4):
        return None
    q: deque[tuple[int, int, int, int, int]] = deque([start])
    prev: dict[
        tuple[int, int, int, int, int],
        tuple[tuple[int, int, int, int, int], int] | None,
    ] = {start: None}
    found: tuple[int, int, int, int, int] | None = None

    while q:
        st = q.popleft()
        if _mc01_is_goal(st, goal4):
            found = st
            break
        a, b, c, d, ld = st
        for act in (1, 2, 3, 4, 5):
            nst = _mc01_apply_action(level, a, b, c, d, ld, act)
            if nst is None:
                continue
            if nst not in prev:
                prev[nst] = (st, act)
                q.append(nst)

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


def _mc01_blocked_move_actions(
    level: Level, state: tuple[int, int, int, int, int]
) -> list[int]:
    a, b, c, d, ld = state
    out: list[int] = []
    for act in (1, 2, 3, 4):
        if _mc01_apply_action(level, a, b, c, d, ld, act) is None:
            out.append(act)
    return out


def _inject_tandem_fails(
    env: Any,
    res_holder: list[Any],
    level: Level,
    state: tuple[int, int, int, int, int],
    snap,
    *,
    count: int = 2,
    hold: int = 4,
) -> None:
    blocked = _mc01_blocked_move_actions(level, state)
    if not blocked:
        return
    seq: list[int] = []
    for ba in blocked:
        if len(seq) >= count:
            break
        seq.append(ba)
    while len(seq) < count:
        seq.append(blocked[0])
    for act in seq[:count]:
        res_holder[0] = safe_env_step(env, _NUM_TO_ACT[act], reasoning={})
        snap(hold)


def record_mc01_registry_gif(
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
    fail_hold = int(o.get("mc01_fail_hold_frames", 5))
    level_hold = int(o.get("mc01_level_hold_frames", 16))

    arc = offline_arcade(root)
    env = arc.make(full_game_id_for_stem(game_id), seed=0, render_mode=None)
    res_holder: list[Any] = [env.reset()]
    images: list = []

    def snap(times: int) -> None:
        fr = _frame_layer0(res_holder[0])
        if fr:
            append_frame_repeats(images, fr[0], times)

    snap(8)
    n_authored = len(env._game._levels)
    L = min(target_levels, max(1, n_authored))
    fail_done: set[int] = set()
    step_abort = False
    prev_li = env._game.level_index

    try:
        for _tick in range(8000):
            if len(images) > 8000:
                break
            res = res_holder[0]
            if res.state in (GameState.WIN, GameState.GAME_OVER):
                break
            lc = getattr(res, "levels_completed", 0) or 0
            if lc >= L:
                break

            level = env._game.current_level
            li = env._game.level_index
            p1 = level.get_sprites_by_tag("p1")[0]
            p2 = level.get_sprites_by_tag("p2")[0]
            lead = int(getattr(env._game, "_lead", 0))
            state = (p1.x, p1.y, p2.x, p2.y, lead)
            goal4 = _mc01_goal_tuple(level)

            if li not in fail_done:
                _inject_tandem_fails(
                    env, res_holder, level, state, snap, count=2, hold=fail_hold
                )
                fail_done.add(li)
                snap(2)
                continue

            act = _mc01_bfs_first_action(level, state, goal4)
            if act is None:
                if verbose:
                    print(f"  {game_id}: mc01 BFS stuck at level {li} state {state}")
                snap(1)
                break
            res_holder[0] = safe_env_step(env, act, reasoning={})
            snap(2)
            li_now = env._game.level_index
            if li_now != prev_li:
                snap(level_hold)
                prev_li = li_now
    except _StepAbort as ex:
        step_abort = True
        if verbose:
            print(f"  {game_id}: mc01 step abort ({ex})")

    snap(12)
    if step_abort and verbose:
        print(f"  {game_id}: mc01 registry GIF partial, {len(images)} frames")

    _cap_gif_frames(images, max_gif)
    if verbose:
        print(f"  {game_id}: mc01 registry GIF, {len(images)} frames (cap {max_gif})")
    return res_holder[0], images


REGISTRY_RECORDERS: dict[str, Any] = {"mc01": record_mc01_registry_gif}
