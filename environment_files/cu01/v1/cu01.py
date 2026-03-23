"""cu01: cover **yellow** cells with **dominoes** (2 orth-adjacent clicks) or **L-trominoes** (3 clicks); **ACTION5** switches tool."""

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


class Cu01UI(RenderableUserDisplay):
    def __init__(self, level_index: int = 0, num_levels: int = 1, ticks: int = 1) -> None:
        self._level_index = level_index
        self._num_levels = num_levels
        self._ticks = ticks
        self._state = None
        self._tool_mode = 0
        self._reject_frames = 0

    def update(
        self,
        *,
        level_index: int | None = None,
        num_levels: int | None = None,
        ticks: int | None = None,
        state=None,
        tool_mode: int | None = None,
        reject_pulse: bool = False,
    ) -> None:
        if level_index is not None:
            self._level_index = level_index
        if num_levels is not None:
            self._num_levels = num_levels
        if ticks is not None:
            self._ticks = ticks
        if state is not None:
            self._state = state
        if tool_mode is not None:
            self._tool_mode = int(tool_mode) % 2
        if reject_pulse:
            self._reject_frames = 8

    def render_interface(self, frame):
        import numpy as np

        from arcengine import GameState

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape
        _r_dots(frame, h, w, self._level_index, self._num_levels, 0)
        _r_ticks(frame, h, w, self._ticks)
        if w > 2 and h > 3:
            frame[1, w - 2] = 11 if self._tool_mode == 0 else 6
        if self._reject_frames > 0:
            for x in range(max(0, w - 5), w):
                frame[min(h - 1, 2), x] = 8
            self._reject_frames -= 1
        go = self._state == GameState.GAME_OVER
        win = self._state == GameState.WIN
        _r_bar(frame, h, w, go, win)
        return frame


def floor(x: int, y: int) -> Sprite:
    return (
        Sprite(
            pixels=[[1]],
            name="f",
            visible=True,
            collidable=False,
            tags=["floor"],
        )
        .clone()
        .set_position(x, y)
    )


def yel(x: int, y: int) -> Sprite:
    return (
        Sprite(
            pixels=[[11]],
            name="y",
            visible=True,
            collidable=False,
            tags=["yellow", "floor"],
        )
        .clone()
        .set_position(x, y)
    )


def mk(yellow: set[tuple[int, int]], d: int) -> Level:
    sl: list[Sprite] = []
    for y in range(G):
        for x in range(G):
            if (x, y) in yellow:
                sl.append(yel(x, y))
            else:
                sl.append(floor(x, y))
    return Level(
        sprites=sl,
        grid_size=(G, G),
        data={"yellow": [list(p) for p in yellow], "difficulty": d},
    )


levels = [
    mk({(2, 2), (3, 2), (2, 3), (3, 3)}, 1),
    mk({(1, 1), (2, 1), (1, 2), (2, 2), (4, 4), (5, 4)}, 2),
    mk({(x, 5) for x in range(2, 8)}, 3),
    mk({(2, y) for y in range(2, 6)} | {(3, y) for y in range(2, 6)}, 4),
    mk({(1, 1), (2, 1), (1, 2), (2, 2), (5, 5), (6, 5), (5, 6), (6, 6)}, 5),
    mk({(3, 3), (4, 3), (5, 3), (3, 4), (3, 5)}, 6),
    mk({(x, y) for x in range(4, 7) for y in range(4, 7)} - {(5, 5)}, 7),
]


def _is_l_shape(cells: list[tuple[int, int]]) -> bool:
    if len(set(cells)) != 3:
        return False
    xs = [c[0] for c in cells]
    ys = [c[1] for c in cells]
    if max(xs) - min(xs) > 1 or max(ys) - min(ys) > 1:
        return False
    if len(set(xs)) == 1 or len(set(ys)) == 1:
        return False
    return True


class Cu01(ARCBaseGame):
    def __init__(self) -> None:
        self._ui = Cu01UI(0, len(levels), 1)
        super().__init__(
            "cu01",
            levels,
            Camera(0, 0, CAM, CAM, BG, PAD, [self._ui]),
            False,
            1,
            [5, 6],
        )

    def _sync_ui(self) -> None:
        rem = min(8, max(0, len(self._yellow) - len(self._covered)))
        self._ui.update(
            level_index=self.level_index,
            num_levels=len(levels),
            ticks=rem,
            state=self._state,
            tool_mode=self._mode,
        )

    def on_set_level(self, level: Level) -> None:
        self._yellow = {tuple(int(t) for t in p) for p in level.get_data("yellow")}
        self._covered: set[tuple[int, int]] = set()
        self._mode = 0
        self._picks: list[tuple[int, int]] = []
        self._sync_ui()

    def _paint_covered(self, gx: int, gy: int) -> None:
        sp = self.current_level.get_sprite_at(gx, gy, ignore_collidable=True)
        if sp and "yellow" in sp.tags:
            sp.pixels = [[14]]

    def step(self) -> None:
        if self.action.id == GameAction.ACTION5:
            self._mode = 1 - self._mode
            self._picks = []
            self._sync_ui()
            self.complete_action()
            return
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
        if (gx, gy) not in self._yellow or (gx, gy) in self._covered:
            self._picks = []
            self._sync_ui()
            self.complete_action()
            return
        self._picks.append((gx, gy))
        if self._mode == 0:
            if len(self._picks) == 2:
                a, b = self._picks
                if abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1:
                    self._covered.add(a)
                    self._covered.add(b)
                    self._paint_covered(*a)
                    self._paint_covered(*b)
                else:
                    self._ui.update(reject_pulse=True)
                self._picks = []
        else:
            if len(self._picks) == 3:
                pts = self._picks
                if _is_l_shape(pts):
                    for p in pts:
                        self._covered.add(p)
                        self._paint_covered(*p)
                else:
                    self._ui.update(reject_pulse=True)
                self._picks = []
        if self._covered >= self._yellow:
            self.next_level()
        self._sync_ui()
        self.complete_action()
