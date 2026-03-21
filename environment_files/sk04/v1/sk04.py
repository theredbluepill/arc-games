"""sk04: fixed player — ACTION6 on orth-adjacent crate pulls it one step toward player."""

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

P = Sprite(pixels=[[9]], name="p", visible=True, collidable=True, tags=["player"])
C = Sprite(pixels=[[11]], name="c", visible=True, collidable=True, tags=["crate"])
K = Sprite(pixels=[[14]], name="k", visible=True, collidable=False, tags=["pad"])


class Sk04UI(RenderableUserDisplay):
    def __init__(self, level_index: int = 0, num_levels: int = 1, ticks: int = 1) -> None:
        self._level_index = level_index
        self._num_levels = num_levels
        self._ticks = ticks
        self._state = None

    def update(
        self,
        *,
        level_index: int | None = None,
        num_levels: int | None = None,
        ticks: int | None = None,
        state=None,
    ) -> None:
        if level_index is not None:
            self._level_index = level_index
        if num_levels is not None:
            self._num_levels = num_levels
        if ticks is not None:
            self._ticks = ticks
        if state is not None:
            self._state = state

    def render_interface(self, frame):
        import numpy as np

        from arcengine import GameState

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape
        _r_dots(frame, h, w, self._level_index, self._num_levels, 0)
        _r_ticks(frame, h, w, self._ticks)
        go = self._state == GameState.GAME_OVER
        win = self._state == GameState.WIN
        _r_bar(frame, h, w, go, win)
        return frame


def mk(px, py, crates, pads, d):
    sl = [P.clone().set_position(px, py)]
    for x, y in crates:
        sl.append(C.clone().set_position(x, y))
    for x, y in pads:
        sl.append(K.clone().set_position(x, y))
    return Level(
        sprites=sl,
        grid_size=(G, G),
        data={"difficulty": d},
    )


def bd():
    return (
        [(x, 0) for x in range(G)]
        + [(x, G - 1) for x in range(G)]
        + [(0, y) for y in range(G)]
        + [(G - 1, y) for y in range(G)]
    )


levels = [
    mk(2, 5, [(4, 5)], [(7, 5)], 1),
    mk(1, 4, [(3, 4), (5, 4)], [(8, 4)], 2),
    mk(2, 2, [(5, 2)], [(8, 8)], 3),
    mk(3, 6, [(6, 6)], [(8, 6)], 4),
    mk(1, 1, [(4, 4), (6, 6)], [(8, 8)], 5),
    mk(2, 7, [(5, 7)], [(7, 7)], 6),
    mk(4, 4, [(6, 4), (4, 6)], [(8, 4), (8, 6)], 7),
]


class Sk04(ARCBaseGame):
    def __init__(self) -> None:
        self._ui = Sk04UI(0, len(levels), 1)
        super().__init__(
            "sk04",
            levels,
            Camera(0, 0, CAM, CAM, BG, PAD, [self._ui]),
            False,
            1,
            [6],
        )


    def _sync_ui(self) -> None:
        self._ui.update(
            level_index=self.level_index,
            num_levels=len(levels),
            ticks=1,
            state=self._state,
        )

    def on_set_level(self, level: Level) -> None:
        self._player = self.current_level.get_sprites_by_tag("player")[0]

    def step(self) -> None:
        if self.action.id != GameAction.ACTION6:
            self._sync_ui()
            self.complete_action()
            return
        c = self.camera.display_to_grid(
            self.action.data.get("x", 0), self.action.data.get("y", 0)
        )
        if not c:
            self._sync_ui()
            self.complete_action()
            return
        gx, gy = int(c[0]), int(c[1])
        px, py = self._player.x, self._player.y
        if abs(gx - px) + abs(gy - py) != 1:
            self._sync_ui()
            self.complete_action()
            return
        cr = self.current_level.get_sprite_at(gx, gy, ignore_collidable=True)
        if not cr or "crate" not in cr.tags:
            self._sync_ui()
            self.complete_action()
            return
        dx = px - gx
        dy = py - gy
        nx, ny = gx + dx, gy + dy
        if 0 <= nx < G and 0 <= ny < G:
            sp = self.current_level.get_sprite_at(nx, ny, ignore_collidable=True)
            if not sp or "crate" not in sp.tags:
                cr.set_position(nx, ny)
        pads = {(s.x, s.y) for s in self.current_level.get_sprites_by_tag("pad")}
        crates = {(s.x, s.y) for s in self.current_level.get_sprites_by_tag("crate")}
        if pads and pads <= crates:
            self.next_level()
        self._sync_ui()
        self.complete_action()
