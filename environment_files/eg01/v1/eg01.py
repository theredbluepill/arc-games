"""Hamming target: cycle each cell 0–3 with ACTION6; win when Hamming distance to target ≤ D."""

from __future__ import annotations

from arcengine import (
    ARCBaseGame,
    Camera,
    GameAction,
    Level,
    RenderableUserDisplay,
    Sprite,
)

BACKGROUND_COLOR = 5
PADDING_COLOR = 4
GW = GH = 6
CAM = 16
BASE = [2, 6, 9, 11]
GHOST = [5, 4, 3, 7]


class Eg01UI(RenderableUserDisplay):
    CLICK_ANIM_FRAMES = 16

    def __init__(self, ham: int, max_d: int) -> None:
        self._ham = ham
        self._max_d = max_d
        self._target: list[list[int]] = [[0] * GW for _ in range(GH)]
        self._click_pos: tuple[int, int] | None = None
        self._click_frames = 0

    def update(
        self,
        ham: int,
        max_d: int,
        target: list[list[int]] | None = None,
    ) -> None:
        self._ham = ham
        self._max_d = max_d
        if target is not None:
            self._target = [row[:] for row in target]

    def set_click(self, fx: int, fy: int) -> None:
        self._click_pos = (fx, fy)
        self._click_frames = Eg01UI.CLICK_ANIM_FRAMES

    @staticmethod
    def _plot_px(frame, fh: int, fw: int, px: int, py: int, c: int) -> None:
        if 0 <= px < fw and 0 <= py < fh:
            frame[py, px] = c

    def render_interface(self, frame):
        import numpy as np

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape
        ok = self._ham <= self._max_d
        frame[h - 2, 2] = 14 if ok else 8
        frame[h - 2, 4] = 10
        ox, oy = 40, 6
        for yy in range(GH):
            for xx in range(GW):
                st = self._target[yy][xx] % 4
                c = GHOST[st]
                px, py = ox + xx, oy + yy
                if 0 <= px < w and 0 <= py < h:
                    frame[py, px] = c
        for i in range(min(self._max_d, 12)):
            frame[h - 2, 16 + i] = 11
        if self._click_pos and self._click_frames > 0:
            cx, cy = self._click_pos
            for r in (1, 2):
                for dy in range(-r, r + 1):
                    for dx in range(-r, r + 1):
                        if abs(dx) + abs(dy) == r:
                            self._plot_px(frame, h, w, cx + dx, cy + dy, 12)
            self._click_frames -= 1
        else:
            self._click_pos = None
        return frame


def cell_sprite(st: int) -> Sprite:
    return Sprite(
        pixels=[[BASE[st % 4]]],
        name="cell",
        visible=True,
        collidable=False,
        tags=["cell"],
    )


def mk(init: list[list[int]], target: list[list[int]], max_d: int, diff: int) -> Level:
    return Level(
        sprites=[],
        grid_size=(GW, GH),
        data={
            "difficulty": diff,
            "init": init,
            "target": target,
            "max_hamming": max_d,
        },
    )


def _zeros() -> list[list[int]]:
    return [[0 for _ in range(GW)] for _ in range(GH)]


def _t3() -> list[list[int]]:
    t = _zeros()
    for x, y in ((2, 2), (3, 2), (2, 3)):
        t[y][x] = 1
    return t


levels = [
    mk(_zeros(), _t3(), 0, 1),
    mk(_zeros(), [[1 if y == 2 and x in (1, 2, 3, 4) else 0 for x in range(GW)] for y in range(GH)], 0, 2),
    mk([[1 for x in range(GW)] for y in range(GH)], _zeros(), 2, 3),
    mk(_zeros(), [[(x + y) % 2 for x in range(GW)] for y in range(GH)], 4, 4),
    mk(_zeros(), [[(x * y) % 4 for x in range(GW)] for y in range(GH)], 6, 5),
    mk(_zeros(), [[1 if x in (1, 4) and y in (1, 4) else 0 for x in range(GW)] for y in range(GH)], 0, 6),
    mk(_zeros(), [[(x + 2 * y) % 4 for x in range(GW)] for y in range(GH)], 8, 7),
]


class Eg01(ARCBaseGame):
    def __init__(self) -> None:
        self._ui = Eg01UI(99, 0)
        super().__init__(
            "eg01",
            levels,
            Camera(0, 0, CAM, CAM, BACKGROUND_COLOR, PADDING_COLOR, [self._ui]),
            False,
            1,
            [1, 2, 3, 4, 6],
        )

    def on_set_level(self, level: Level) -> None:
        self._g = [row[:] for row in self.current_level.get_data("init")]
        self._target = self.current_level.get_data("target")
        self._max_d = int(self.current_level.get_data("max_hamming") or 0)
        self._paint()
        self._sync_ui()

    def _sync_ui(self) -> None:
        self._ui.update(self._hamming(), self._max_d, target=self._target)

    def _paint(self) -> None:
        for s in list(self.current_level.get_sprites_by_tag("cell")):
            self.current_level.remove_sprite(s)
        for y in range(GH):
            for x in range(GW):
                self.current_level.add_sprite(
                    cell_sprite(self._g[y][x]).set_position(x, y),
                )

    def _hamming(self) -> int:
        d = 0
        for y in range(GH):
            for x in range(GW):
                if self._g[y][x] != self._target[y][x]:
                    d += 1
        return d

    def _grid_to_frame_pixel(self, gx: int, gy: int) -> tuple[int, int]:
        cam = self.camera
        cw, ch = cam.width, cam.height
        scale = min(int(64 / cw), int(64 / ch))
        x_pad = int((64 - (cw * scale)) / 2)
        y_pad = int((64 - (ch * scale)) / 2)
        return gx * scale + scale // 2 + x_pad, gy * scale + scale // 2 + y_pad

    def step(self) -> None:
        if self.action.id.value in (1, 2, 3, 4):
            self.complete_action()
            return

        if self.action.id != GameAction.ACTION6:
            self.complete_action()
            return

        px = self.action.data.get("x", 0)
        py = self.action.data.get("y", 0)
        coords = self.camera.display_to_grid(px, py)
        if not coords:
            self.complete_action()
            return
        gx, gy = coords
        if not (0 <= gx < GW and 0 <= gy < GH):
            self.complete_action()
            return

        self._ui.set_click(*self._grid_to_frame_pixel(gx, gy))
        self._g[gy][gx] = (self._g[gy][gx] + 1) % 4
        self._paint()
        self._sync_ui()
        if self._hamming() <= self._max_d:
            self.next_level()

        self.complete_action()
