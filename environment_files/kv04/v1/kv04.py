"""kv04: two parallel resistor ladders — ACTION1–3 cycle branch A; ACTION4 cycles r3 on branch B; ACTION5 verify both node pairs."""

from __future__ import annotations

from fractions import Fraction

from arcengine import ARCBaseGame, Camera, GameAction, GameState, Level, RenderableUserDisplay


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


class Kv04UI(RenderableUserDisplay):
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

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape
        _r_dots(frame, h, w, self._level_index, self._num_levels, 0)
        _r_ticks(frame, h, w, self._ticks)
        go = self._state == GameState.GAME_OVER
        win = self._state == GameState.WIN
        _r_bar(frame, h, w, go, win)
        return frame


def _cycle(x: int) -> int:
    opts = (1, 2, 4)
    i = opts.index(x) if x in opts else 0
    return opts[(i + 1) % 3]


def _v(r0: int, r1: int, r2: int) -> tuple[Fraction, Fraction]:
    s = r0 + r1 + r2
    if s == 0:
        return Fraction(0), Fraction(0)
    return Fraction(12 * (r1 + r2), s), Fraction(12 * r2, s)


def mk(d, r0, r1, r2, r3, r4, r5, t1, t2, t3, t4):
    return Level(
        sprites=[],
        grid_size=(8, 8),
        data={
            "difficulty": d,
            "r0": r0,
            "r1": r1,
            "r2": r2,
            "r3": r3,
            "r4": r4,
            "r5": r5,
            "t1n": t1[0],
            "t1d": t1[1],
            "t2n": t2[0],
            "t2d": t2[1],
            "t3n": t3[0],
            "t3d": t3[1],
            "t4n": t4[0],
            "t4d": t4[1],
        },
    )


levels = [
    mk(1, 2, 4, 2, 2, 4, 2, (8, 1), (4, 1), (8, 1), (4, 1)),
    mk(2, 1, 1, 1, 2, 2, 2, (9, 1), (3, 1), (10, 1), (2, 1)),
    mk(3, 1, 2, 4, 1, 2, 4, (8, 1), (4, 1), (8, 1), (4, 1)),
    mk(4, 2, 2, 2, 1, 1, 1, (10, 1), (2, 1), (9, 1), (3, 1)),
    mk(5, 1, 2, 1, 2, 4, 2, (4, 1), (2, 1), (8, 1), (4, 1)),
    mk(6, 4, 2, 1, 1, 2, 4, (6, 1), (2, 1), (8, 1), (4, 1)),
    mk(7, 2, 1, 4, 4, 1, 2, (10, 1), (8, 1), (10, 1), (2, 1)),
]


class Kv04(ARCBaseGame):
    def __init__(self) -> None:
        self._ui = Kv04UI(0, len(levels), 1)
        super().__init__(
            "kv04",
            levels,
            Camera(0, 0, 8, 8, 5, 4, [self._ui]),
            False,
            1,
            [1, 2, 3, 4, 5],
        )

    def _tick_hud(self) -> int:
        s = self._r0 + self._r1 + self._r2 + self._r3 + self._r4 + self._r5
        return min(8, max(1, (s % 8) + 1))

    def _sync_ui(self) -> None:
        self._ui.update(
            level_index=self.level_index,
            num_levels=len(levels),
            ticks=self._tick_hud(),
            state=self._state,
        )

    def on_set_level(self, level: Level) -> None:
        d = level.get_data
        self._r0 = int(d("r0"))
        self._r1 = int(d("r1"))
        self._r2 = int(d("r2"))
        self._r3 = int(d("r3"))
        self._r4 = int(d("r4"))
        self._r5 = int(d("r5"))
        self._t1 = Fraction(int(d("t1n")), int(d("t1d")))
        self._t2 = Fraction(int(d("t2n")), int(d("t2d")))
        self._t3 = Fraction(int(d("t3n")), int(d("t3d")))
        self._t4 = Fraction(int(d("t4n")), int(d("t4d")))
        self._sync_ui()

    def step(self) -> None:
        aid = self.action.id
        if aid == GameAction.ACTION1:
            self._r0 = _cycle(self._r0)
        elif aid == GameAction.ACTION2:
            self._r1 = _cycle(self._r1)
        elif aid == GameAction.ACTION3:
            self._r2 = _cycle(self._r2)
        elif aid == GameAction.ACTION4:
            self._r3 = _cycle(self._r3)
        elif aid == GameAction.ACTION5:
            v1, v2 = _v(self._r0, self._r1, self._r2)
            v3, v4 = _v(self._r3, self._r4, self._r5)
            if v1 == self._t1 and v2 == self._t2 and v3 == self._t3 and v4 == self._t4:
                self.next_level()
        self._sync_ui()
        self.complete_action()
