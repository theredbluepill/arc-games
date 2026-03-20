#!/usr/bin/env python3
"""Solve pt01 levels 1–3 with ACTION6 and write assets/pt01.gif (64×64)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
from PIL import Image

from arc_agi import Arcade, OperationMode
from arcengine import GameAction

ROOT = Path(__file__).resolve().parents[1]

_COLOR_HEX = {
    0: "#FFFFFFFF",
    1: "#CCCCCCFF",
    2: "#999999FF",
    3: "#666666FF",
    4: "#333333FF",
    5: "#000000FF",
    6: "#E53AA3FF",
    7: "#FF7BCCFF",
    8: "#F93C31FF",
    9: "#1E93FFFF",
    10: "#88D8F1FF",
    11: "#FFDC00FF",
    12: "#FF851BFF",
    13: "#921231FF",
    14: "#4FCC30FF",
    15: "#A356D6FF",
}

_LUT = np.zeros((256, 3), dtype=np.uint8)
for i, hx in _COLOR_HEX.items():
    r = int(hx[1:3], 16)
    g = int(hx[3:5], 16)
    b = int(hx[5:7], 16)
    _LUT[i] = (r, g, b)


def _load_pt01_helpers():
    path = ROOT / "environment_files" / "pt01" / "v1" / "pt01.py"
    spec = importlib.util.spec_from_file_location("pt01_gif", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.get_sprite_rotation


def _frame_to_rgb(frame: np.ndarray) -> Image.Image:
    flat = frame.astype(np.int16).clip(0, 15)
    rgb = _LUT[flat]
    return Image.fromarray(rgb, mode="RGB")


def _build_click_plan(game, get_sprite_rotation) -> list[tuple[int, int]]:
    clicks: list[tuple[int, int]] = []
    for sp in game._rotatables:
        tgt = game._get_target_rotation_for_sprite(sp)
        cur = get_sprite_rotation(sp)
        n = ((tgt - cur) % 360) // 90
        clicks.extend([(sp.x + 1, sp.y + 1)] * n)
    return clicks


def main() -> None:
    out = ROOT / "assets" / "pt01.gif"
    out.parent.mkdir(parents=True, exist_ok=True)
    get_sprite_rotation = _load_pt01_helpers()

    arc = Arcade(
        environments_dir=str(ROOT / "environment_files"),
        operation_mode=OperationMode.OFFLINE,
    )
    env = arc.make("pt01-v1", seed=0, render_mode=None)
    res = env.reset()
    game = env._game

    images: list[Image.Image] = []

    def push_repeats(arr: np.ndarray, n: int) -> None:
        base = _frame_to_rgb(arr)
        for _ in range(n):
            images.append(base.copy())

    push_repeats(res.frame[0], 8)

    levels_to_show = 3
    for _ in range(levels_to_show):
        game = env._game
        plan = _build_click_plan(game, get_sprite_rotation)
        for x, y in plan:
            res = env.step(GameAction.ACTION6, data={"x": x, "y": y})
            push_repeats(res.frame[0], 2)
        push_repeats(res.frame[0], 10)
        if res.state.name == "WIN":
            break

    images[0].save(
        out,
        save_all=True,
        append_images=images[1:],
        duration=120,
        loop=0,
        optimize=False,
    )
    print(f"Wrote {out} ({len(images)} frames)")


if __name__ == "__main__":
    main()
