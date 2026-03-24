"""Registry GIF recorders for GAMES.md 218–237 stems with weak generic captures.

Stems without ``player`` often exit early in ``registry_gif_lib``; these tours
cycle ACTION5/6 with display-mapped clicks, resetting on WIN/GAME_OVER so HUD
(level dots, bars, lose) shows across multiple episodes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from arcengine import GameAction, GameState

from env_resolve import full_game_id_for_stem
from gif_common import append_frame_repeats, grid_cell_center_display, offline_arcade
from registry_gif_lib import _cap_gif_frames, safe_env_step

A5, A6 = GameAction.ACTION5, GameAction.ACTION6


def _snap(res: Any, images: list, times: int) -> None:
    fr = getattr(res, "frame", None) or []
    if fr:
        append_frame_repeats(images, fr[0], times)


def _tour(
    game_id: str,
    root: Path,
    *,
    gw: int,
    gh: int,
    n_steps: int,
    mode: Literal["a5_a6", "a5_only", "a6_only"],
    overrides: dict[str, Any] | None,
    verbose: bool,
    seed: int,
    rep: int = 3,
) -> tuple[Any, list]:
    _ = verbose, seed
    o = dict(overrides or {})
    max_gif = int(o.get("max_gif_frames", 520))
    rep = int(o.get("registry_218_rep", rep))
    arc = offline_arcade(root)
    env = arc.make(full_game_id_for_stem(game_id), seed=0, render_mode=None)
    res_box: list[Any] = [env.reset()]
    images: list = []
    _snap(res_box[0], images, 8)

    for i in range(n_steps):
        if res_box[0].state in (GameState.WIN, GameState.GAME_OVER):
            res_box[0] = env.reset()
            _snap(res_box[0], images, 10)
        gx = (i * 5 + 1) % gw
        gy = (i * 3 + 2) % gh
        cx, cy = grid_cell_center_display(gx, gy, grid_w=gw, grid_h=gh)
        if mode == "a6_only":
            r = safe_env_step(env, A6, reasoning={}, data={"x": cx, "y": cy})
        elif mode == "a5_only":
            r = safe_env_step(env, A5, reasoning={}, data={})
        else:
            if (i % 4) != 2:
                r = safe_env_step(env, A5, reasoning={}, data={})
            else:
                r = safe_env_step(env, A6, reasoning={}, data={"x": cx, "y": cy})
        res_box[0] = r
        _snap(r, images, rep)
    _snap(res_box[0], images, 14)
    _cap_gif_frames(images, max_gif)
    return res_box[0], images


def record_sy04_registry_gif(
    game_id: str,
    root: Path,
    *,
    overrides: dict[str, Any] | None,
    verbose: bool,
    seed: int,
) -> tuple[Any, list]:
    _ = verbose, seed
    g = 11
    o = dict(overrides or {})
    max_gif = int(o.get("max_gif_frames", 520))
    rep = int(o.get("registry_218_rep", 3))
    n = int(o.get("registry_218_sy04_steps", 160))
    arc = offline_arcade(root)
    env = arc.make(full_game_id_for_stem(game_id), seed=0, render_mode=None)
    res_box: list[Any] = [env.reset()]
    images: list = []
    _snap(res_box[0], images, 8)
    pairs = [(x, y) for x in range(g) for y in range(g) if x > y]
    for i in range(n):
        if res_box[0].state in (GameState.WIN, GameState.GAME_OVER):
            res_box[0] = env.reset()
            _snap(res_box[0], images, 10)
        x, y = pairs[i % len(pairs)]
        cx, cy = grid_cell_center_display(x, y, grid_w=g, grid_h=g)
        r = safe_env_step(env, A6, reasoning={}, data={"x": cx, "y": cy})
        res_box[0] = r
        _snap(r, images, rep)
    _snap(res_box[0], images, 14)
    _cap_gif_frames(images, max_gif)
    return res_box[0], images


def record_ab01_registry_gif(
    game_id: str,
    root: Path,
    *,
    overrides: dict[str, Any] | None,
    verbose: bool,
    seed: int,
) -> tuple[Any, list]:
    o = dict(overrides or {})
    n = int(o.get("registry_218_ab01_steps", 220))
    return _tour(
        game_id,
        root,
        gw=10,
        gh=10,
        n_steps=n,
        mode="a6_only",
        overrides=o,
        verbose=verbose,
        seed=seed,
        rep=3,
    )


def record_sp04_registry_gif(
    game_id: str,
    root: Path,
    *,
    overrides: dict[str, Any] | None,
    verbose: bool,
    seed: int,
) -> tuple[Any, list]:
    o = dict(overrides or {})
    n = int(o.get("registry_218_sp04_steps", 200))
    return _tour(
        game_id,
        root,
        gw=12,
        gh=12,
        n_steps=n,
        mode="a6_only",
        overrides=o,
        verbose=verbose,
        seed=seed,
        rep=3,
    )


def record_ph04_registry_gif(
    game_id: str,
    root: Path,
    *,
    overrides: dict[str, Any] | None,
    verbose: bool,
    seed: int,
) -> tuple[Any, list]:
    o = dict(overrides or {})
    n = int(o.get("registry_218_ph04_steps", 100))
    return _tour(
        game_id,
        root,
        gw=8,
        gh=8,
        n_steps=n,
        mode="a5_only",
        overrides=o,
        verbose=verbose,
        seed=seed,
        rep=3,
    )


def record_zm04_registry_gif(
    game_id: str,
    root: Path,
    *,
    overrides: dict[str, Any] | None,
    verbose: bool,
    seed: int,
) -> tuple[Any, list]:
    o = dict(overrides or {})
    n = int(o.get("registry_218_zm04_steps", 200))
    return _tour(
        game_id,
        root,
        gw=12,
        gh=12,
        n_steps=n,
        mode="a5_a6",
        overrides=o,
        verbose=verbose,
        seed=seed,
        rep=3,
    )


def record_rp04_registry_gif(
    game_id: str,
    root: Path,
    *,
    overrides: dict[str, Any] | None,
    verbose: bool,
    seed: int,
) -> tuple[Any, list]:
    o = dict(overrides or {})
    n = int(o.get("registry_218_rp04_steps", 200))
    return _tour(
        game_id,
        root,
        gw=12,
        gh=12,
        n_steps=n,
        mode="a5_a6",
        overrides=o,
        verbose=verbose,
        seed=seed,
        rep=3,
    )


def record_tc04_registry_gif(
    game_id: str,
    root: Path,
    *,
    overrides: dict[str, Any] | None,
    verbose: bool,
    seed: int,
) -> tuple[Any, list]:
    o = dict(overrides or {})
    n = int(o.get("registry_218_tc04_steps", 180))
    return _tour(
        game_id,
        root,
        gw=10,
        gh=10,
        n_steps=n,
        mode="a5_a6",
        overrides=o,
        verbose=verbose,
        seed=seed,
        rep=3,
    )


def record_sf04_registry_gif(
    game_id: str,
    root: Path,
    *,
    overrides: dict[str, Any] | None,
    verbose: bool,
    seed: int,
) -> tuple[Any, list]:
    o = dict(overrides or {})
    n = int(o.get("registry_218_sf04_steps", 200))
    return _tour(
        game_id,
        root,
        gw=16,
        gh=16,
        n_steps=n,
        mode="a5_a6",
        overrides=o,
        verbose=verbose,
        seed=seed,
        rep=3,
    )


def record_df04_registry_gif(
    game_id: str,
    root: Path,
    *,
    overrides: dict[str, Any] | None,
    verbose: bool,
    seed: int,
) -> tuple[Any, list]:
    o = dict(overrides or {})
    n = int(o.get("registry_218_df04_steps", 160))
    return _tour(
        game_id,
        root,
        gw=10,
        gh=10,
        n_steps=n,
        mode="a5_a6",
        overrides=o,
        verbose=verbose,
        seed=seed,
        rep=3,
    )


def record_ih01_registry_gif(
    game_id: str,
    root: Path,
    *,
    overrides: dict[str, Any] | None,
    verbose: bool,
    seed: int,
) -> tuple[Any, list]:
    o = dict(overrides or {})
    n = int(o.get("registry_218_ih01_steps", 160))
    return _tour(
        game_id,
        root,
        gw=10,
        gh=10,
        n_steps=n,
        mode="a5_a6",
        overrides=o,
        verbose=verbose,
        seed=seed,
        rep=3,
    )


REGISTRY_RECORDERS = {
    "ab01": record_ab01_registry_gif,
    "sy04": record_sy04_registry_gif,
    "ph04": record_ph04_registry_gif,
    "sp04": record_sp04_registry_gif,
    "zm04": record_zm04_registry_gif,
    "rp04": record_rp04_registry_gif,
    "tc04": record_tc04_registry_gif,
    "sf04": record_sf04_registry_gif,
    "df04": record_df04_registry_gif,
    "ih01": record_ih01_registry_gif,
}
