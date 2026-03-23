"""ng04: two-layer cell colors — ACTION6 cycles layer visible color; match both targets."""

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

G = 6
CAM = 16
COLS = (8, 9, 11, 14)


class Ng04UI(RenderableUserDisplay):
    def __init__(
        self,
        level_index: int = 0,
        num_levels: int = 1,
        ticks: int = 1,
        layer: int = 0,
    ) -> None:
        self._level_index = level_index
        self._num_levels = num_levels
        self._ticks = ticks
        self._layer = layer
        self._state = None
        self._flash_ttl = 0

    def update(
        self,
        *,
        level_index: int | None = None,
        num_levels: int | None = None,
        ticks: int | None = None,
        layer: int | None = None,
        layer_flash_ttl: int | None = None,
        state=None,
    ) -> None:
        if level_index is not None:
            self._level_index = level_index
        if num_levels is not None:
            self._num_levels = num_levels
        if ticks is not None:
            self._ticks = ticks
        if layer is not None:
            self._layer = layer
        if layer_flash_ttl is not None:
            self._flash_ttl = max(0, int(layer_flash_ttl))
        if state is not None:
            self._state = state

    def render_interface(self, frame):
        import numpy as np

        from arcengine import GameState

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape
        if self._flash_ttl > 0:
            frame[h - 2, 0] = frame[h - 2, 1] = 11
            self._flash_ttl -= 1
        else:
            frame[h - 2, 0] = 14 if self._layer == 0 else 3
            frame[h - 2, 1] = 14 if self._layer == 1 else 3
        _r_dots(frame, h, w, self._level_index, self._num_levels, 0)
        _r_ticks(frame, h, w, self._ticks)
        go = self._state == GameState.GAME_OVER
        win = self._state == GameState.WIN
        _r_bar(frame, h, w, go, win)
        return frame


def cell(x: int, y: int, c: int) -> Sprite:
    return Sprite(
        pixels=[[c]], name="c", visible=True, collidable=False, tags=["cell"]
    ).clone().set_position(x, y)


def mk(fg: list[list[int]], bg: list[list[int]], targ_fg, targ_bg, d: int) -> Level:
    sl = []
    for y in range(G):
        for x in range(G):
            sl.append(cell(x, y, COLS[fg[y][x] % 4]))
    return Level(
        sprites=sl,
        grid_size=(G, G),
        data={
            "fg": fg,
            "bg": bg,
            "target_fg": targ_fg,
            "target_bg": targ_bg,
            "difficulty": d,
        },
    )


def z():
    return [[0 for _ in range(G)] for _ in range(G)]


levels = [
    mk(z(), z(), [[1, 0, 0, 0, 0, 0]] * G, z(), 1),
    mk([[1 if x == y else 0 for x in range(G)] for y in range(G)], z(), [[1 if x == y else 0 for x in range(G)] for y in range(G)], z(), 2),
    mk([[x % 4 for x in range(G)] for y in range(G)], z(), [[x % 4 for x in range(G)] for y in range(G)], z(), 3),
    mk(z(), [[1, 0, 0, 0, 0, 0]] * G, z(), [[1, 0, 0, 0, 0, 0]] * G, 4),
    mk([[0, 1, 2, 3, 0, 1]] * G, z(), [[0, 1, 2, 3, 0, 1]] * G, z(), 5),
    mk(z(), z(), z(), z(), 6),
    mk([[2] * G for _ in range(G)], [[3] * G for _ in range(G)], [[2] * G for _ in range(G)], [[3] * G for _ in range(G)], 7),
]


class Ng04(ARCBaseGame):
    def __init__(self) -> None:
        self._ui = Ng04UI(0, len(levels), 1)
        super().__init__(
            "ng04",
            levels,
            Camera(0, 0, CAM, CAM, BG, PAD, [self._ui]),
            False,
            1,
            [1, 2, 3, 4, 6],
        )


    def _sync_ui(self, *, layer_flash_ttl: int | None = None) -> None:
        self._ui.update(
            level_index=self.level_index,
            num_levels=len(levels),
            ticks=1,
            layer=self._layer,
            layer_flash_ttl=layer_flash_ttl,
            state=self._state,
        )

    def on_set_level(self, level: Level) -> None:
        self._fg = [list(r) for r in level.get_data("fg")]
        self._bg = [list(r) for r in level.get_data("bg")]
        self._tfg = [list(r) for r in level.get_data("target_fg")]
        self._tbg = [list(r) for r in level.get_data("target_bg")]
        self._layer = 0
        self._ref()
        self._sync_ui(layer_flash_ttl=0)

    def _ref(self) -> None:
        for s in list(self.current_level.get_sprites_by_tag("cell")):
            self.current_level.remove_sprite(s)
        src = self._fg if self._layer == 0 else self._bg
        for y in range(G):
            for x in range(G):
                self.current_level.add_sprite(
                    cell(x, y, COLS[src[y][x] % 4])
                )

    def _win(self) -> bool:
        return self._fg == self._tfg and self._bg == self._tbg

    def step(self) -> None:
        if self.action.id == GameAction.ACTION6:
            c = self.camera.display_to_grid(
                self.action.data.get("x", 0), self.action.data.get("y", 0)
            )
            if c:
                gx, gy = int(c[0]), int(c[1])
                if 0 <= gx < G and 0 <= gy < G:
                    if self._layer == 0:
                        self._fg[gy][gx] = (self._fg[gy][gx] + 1) % 4
                    else:
                        self._bg[gy][gx] = (self._bg[gy][gx] + 1) % 4
                    self._ref()
                    if self._win():
                        self.next_level()
            else:
                self._layer = 1 - self._layer
                self._ref()
                self._sync_ui(layer_flash_ttl=12)
                self.complete_action()
                return
            self._sync_ui()
            self.complete_action()
            return
        self._sync_ui()
        self.complete_action()
