"""Registry GIF recorders for sg04 (dual-arm commits), cw01 (2-SAT toggles).

Generic registry_gif_lib BFS has no ``player`` on these stems; scripted captures
show level advance, budget HUD (sg04), and click feedback (cw01).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from arcengine import GameAction, GameState

from env_resolve import full_game_id_for_stem
from gif_common import append_frame_repeats, grid_cell_center_display, offline_arcade
from registry_gif_lib import _cap_gif_frames, safe_env_step

A5, A6 = GameAction.ACTION5, GameAction.ACTION6


def _snap(res: Any, images: list, times: int) -> None:
    fr = getattr(res, "frame", None) or []
    if fr:
        append_frame_repeats(images, fr[0], times)


def record_sg04_registry_gif(
    game_id: str,
    root: Path,
    *,
    overrides: dict[str, Any] | None,
    verbose: bool,
    seed: int,
) -> tuple[Any, list]:
    _ = verbose, seed
    o = dict(overrides or {})
    max_gif = int(o.get("max_gif_frames", 520))
    arc = offline_arcade(root)
    env = arc.make(full_game_id_for_stem(game_id), seed=0, render_mode=None)
    res_box: list[Any] = [env.reset()]
    images: list = []
    _snap(res_box[0], images, 6)

    def stp(rep: int = 3) -> None:
        r = safe_env_step(env, A5, reasoning={}, data={})
        res_box[0] = r
        _snap(r, images, rep)

    # Level 1: six alternating productive commits (3 + 3).
    for _ in range(6):
        stp(5)
    _snap(res_box[0], images, 14)
    # Level 2: burn commits until step budget hits zero (visible lose).
    while res_box[0].state not in (GameState.WIN, GameState.GAME_OVER):
        stp(3)
        if len(images) > 2500:
            break
    _snap(res_box[0], images, 18)
    _cap_gif_frames(images, max_gif)
    return res_box[0], images


def _cw_disp(gx: int, gy: int) -> dict[str, int]:
    x, y = grid_cell_center_display(gx, gy, grid_w=12, grid_h=12)
    return {"x": x, "y": y}


def record_cw01_registry_gif(
    game_id: str,
    root: Path,
    *,
    overrides: dict[str, Any] | None,
    verbose: bool,
    seed: int,
) -> tuple[Any, list]:
    _ = verbose, seed
    o = dict(overrides or {})
    max_gif = int(o.get("max_gif_frames", 520))
    target_levels = int(o.get("target_levels", 0)) or 3
    arc = offline_arcade(root)
    env = arc.make(full_game_id_for_stem(game_id), seed=0, render_mode=None)
    res_box: list[Any] = [env.reset()]
    images: list = []
    _snap(res_box[0], images, 8)

    def stp(act: GameAction, *, data: dict[str, int] | None = None, rep: int = 4) -> None:
        r = safe_env_step(env, act, reasoning={}, data=data or {})
        res_box[0] = r
        _snap(r, images, rep)

    for _lv in range(min(target_levels, len(env._game._levels))):
        if res_box[0].state in (GameState.WIN, GameState.GAME_OVER):
            break
        li0 = env._game.level_index
        stp(A6, data=_cw_disp(0, 0), rep=3)
        stp(A6, data=_cw_disp(0, 11), rep=3)
        for _ in range(40):
            if env._game.level_index != li0 or res_box[0].state == GameState.WIN:
                break
            for sp in env._game.current_level.get_sprites_by_tag("lit"):
                stp(A6, data=_cw_disp(int(sp.x), int(sp.y)), rep=3)
                if env._game.level_index != li0 or res_box[0].state == GameState.WIN:
                    break
        _snap(res_box[0], images, 14)

    _cap_gif_frames(images, max_gif)
    return res_box[0], images


REGISTRY_RECORDERS = {
    "sg04": record_sg04_registry_gif,
    "cw01": record_cw01_registry_gif,
}
