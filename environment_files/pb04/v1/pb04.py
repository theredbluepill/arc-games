"""pb04: winch cell — ACTION5 pulls nearest crate one step along (dx,dy) toward winch."""

from __future__ import annotations

from arcengine import ARCBaseGame, Camera, GameAction, GameState, Level, RenderableUserDisplay, Sprite

BG, PAD = 5, 4


def _rp(frame, h, w, x, y, c):
    if 0 <= x < w and 0 <= y < h:
        frame[y, x] = c


def _r_dots(frame, h, w, li, n, y0=0):
    for i in range(min(n, 14)):
        cx = 1 + i * 2
        if cx >= w:
            break
        c = 14 if i < li else (11 if i == li else 3)
        _rp(frame, h, w, cx, y0, c)


def _r_ticks(frame, h, w, n, y=None):
    row = (h - 1) if y is None else y
    for i in range(max(0, min(n, 8))):
        _rp(frame, h, w, 1 + i, row, 11)


def _r_bar(frame, h, w, game_over, win):
    if not (game_over or win):
        return
    r = h - 3
    if r < 0:
        return
    c = 14 if win else 8
    for x in range(min(w, 16)):
        _rp(frame, h, w, x, r, c)

G = 10
CAM = 16

WCH = Sprite(pixels=[[10]], name="w", visible=True, collidable=False, tags=["winch"])
C = Sprite(pixels=[[11]], name="c", visible=True, collidable=True, tags=["crate"])
K = Sprite(pixels=[[14]], name="k", visible=True, collidable=False, tags=["pad"])


class Pb04UI(RenderableUserDisplay):
    def __init__(
        self,
        level_index: int = 0,
        num_levels: int = 1,
        ticks: int = 1,
        dx: int = 0,
        dy: int = 0,
    ) -> None:
        self._level_index = level_index
        self._num_levels = num_levels
        self._ticks = ticks
        self._dx, self._dy = dx, dy
        self._state = None

    def update(
        self,
        *,
        level_index: int | None = None,
        num_levels: int | None = None,
        ticks: int | None = None,
        dx: int | None = None,
        dy: int | None = None,
        state=None,
    ) -> None:
        if level_index is not None:
            self._level_index = level_index
        if num_levels is not None:
            self._num_levels = num_levels
        if ticks is not None:
            self._ticks = ticks
        if dx is not None:
            self._dx = dx
        if dy is not None:
            self._dy = dy
        if state is not None:
            self._state = state

    def render_interface(self, frame):
        import numpy as np

        from arcengine import GameState

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape
        bg = 5
        hi = 11
        if w > 4:
            frame[h - 2, w - 4] = hi if self._dx < 0 else bg
            frame[h - 2, w - 3] = hi if self._dx > 0 else bg
            frame[h - 2, w - 2] = hi if self._dy < 0 else bg
            frame[h - 2, w - 1] = hi if self._dy > 0 else bg
        _r_dots(frame, h, w, self._level_index, self._num_levels, 0)
        _r_ticks(frame, h, w, self._ticks)
        go = self._state == GameState.GAME_OVER
        win = self._state == GameState.WIN
        _r_bar(frame, h, w, go, win)
        return frame


def mk(wx, wy, dx, dy, crates, pads, d):
    sl = [WCH.clone().set_position(wx, wy)]
    for x, y in crates:
        sl.append(C.clone().set_position(x, y))
    for x, y in pads:
        sl.append(K.clone().set_position(x, y))
    return Level(
        sprites=sl,
        grid_size=(G, G),
        data={"winch": [wx, wy], "dir": [dx, dy], "difficulty": d},
    )


levels = [
    mk(2, 5, 1, 0, [(5, 5)], [(7, 5)], 1),
    mk(1, 4, 0, 1, [(4, 6)], [(4, 2)], 2),
    mk(8, 5, -1, 0, [(5, 5)], [(2, 5)], 3),
    mk(3, 3, 1, 1, [(5, 5)], [(7, 7)], 4),
    mk(2, 8, 0, -1, [(2, 5)], [(2, 2)], 5),
    mk(6, 6, -1, 0, [(8, 6)], [(4, 6)], 6),
    mk(5, 5, 1, 0, [(7, 5)], [(9, 5)], 7),
]


class Pb04(ARCBaseGame):
    def __init__(self) -> None:
        self._ui = Pb04UI(0, len(levels), 1)
        super().__init__(
            "pb04",
            levels,
            Camera(0, 0, CAM, CAM, BG, PAD, [self._ui]),
            False,
            1,
            [5],
        )


    def _sync_ui(self) -> None:
        self._ui.update(
            level_index=self.level_index,
            num_levels=len(levels),
            ticks=1,
            dx=self._dx,
            dy=self._dy,
            state=self._state,
        )

    def on_set_level(self, level: Level) -> None:
        w = level.get_data("winch")
        self._wx, self._wy = int(w[0]), int(w[1])
        dr = level.get_data("dir")
        self._dx, self._dy = int(dr[0]), int(dr[1])
        self._sync_ui()

    def step(self) -> None:
        if self.action.id != GameAction.ACTION5:
            self._sync_ui()
            self.complete_action()
            return
        crates = self.current_level.get_sprites_by_tag("crate")
        if not crates:
            self._sync_ui()
            self.complete_action()
            return
        cr = min(
            crates,
            key=lambda s: abs(s.x - self._wx) + abs(s.y - self._wy),
        )
        nx = cr.x - self._dx
        ny = cr.y - self._dy
        if 0 <= nx < G and 0 <= ny < G:
            sp = self.current_level.get_sprite_at(nx, ny, ignore_collidable=True)
            if not sp or "crate" not in sp.tags:
                cr.set_position(nx, ny)
        pads = {(s.x, s.y) for s in self.current_level.get_sprites_by_tag("pad")}
        cpos = {(s.x, s.y) for s in self.current_level.get_sprites_by_tag("crate")}
        if pads and pads <= cpos:
            self.next_level()
        self._sync_ui()
        self.complete_action()
