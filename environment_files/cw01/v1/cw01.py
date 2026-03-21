"""cw01: 2-SAT style — literals on a line; **ACTION6** toggles; all clauses must have a true literal."""

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

CAM = 16


class Cw01UI(RenderableUserDisplay):
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


def lit(x, y, var: int, neg: bool):
    c = 8 if neg else 9
    return Sprite(
        pixels=[[c]],
        name="l",
        visible=True,
        collidable=False,
        tags=["lit", f"v{var}", "neg" if neg else "pos"],
    ).clone().set_position(x, y)


def mk(clauses: list[list[tuple[int, int, int, bool]]], d: int) -> Level:
    sl: list[Sprite] = []
    for ci, cl in enumerate(clauses):
        for x, y, v, ng in cl:
            sl.append(lit(x, y + ci * 3, v, ng))
    return Level(
        sprites=sl,
        grid_size=(12, 12),
        data={"clauses": clauses, "difficulty": d},
    )


levels = [
    mk([[(2, 1, 0, False), (4, 1, 1, True)], [(2, 1, 1, False), (4, 1, 0, True)]], 1),
    mk(
        [
            [(1, 1, 0, False), (3, 1, 1, False)],
            [(5, 1, 0, True), (7, 1, 1, True)],
            [(2, 1, 0, True), (6, 1, 1, False)],
        ],
        2,
    ),
    mk([[(2, 2, 0, False), (5, 2, 0, True)], [(3, 2, 1, False), (6, 2, 1, True)]], 3),
    mk([[(1, 1, 0, False)], [(3, 1, 0, True)], [(5, 1, 1, False)]], 4),
    mk([[(2, 1, 0, False), (4, 1, 1, True), (6, 1, 0, True)]], 5),
    mk([[(1, 1, 0, False), (4, 1, 1, False)], [(2, 1, 0, True), (5, 1, 1, True)]], 6),
    mk([[(2, 1, 0, False), (5, 1, 1, True)], [(3, 1, 1, False), (6, 1, 0, True)], [(4, 1, 0, True), (7, 1, 1, False)]], 7),
]


class Cw01(ARCBaseGame):
    def __init__(self) -> None:
        self._ui = Cw01UI(0, len(levels), 1)
        super().__init__(
            "cw01",
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
            ticks=8 if self._sat() else 2,
            state=self._state,
        )

    def on_set_level(self, level: Level) -> None:
        self._val = [False, False]
        self._clauses = level.get_data("clauses")

    def _sat(self) -> bool:
        for cl in self._clauses:
            ok = False
            for _x, _y, v, neg in cl:
                t = self._val[int(v) % 2]
                if neg:
                    t = not t
                if t:
                    ok = True
            if not ok:
                return False
        return True

    def step(self) -> None:
        if self.action.id != GameAction.ACTION6:
            self._sync_ui()
            self.complete_action()
            return
        c = self.camera.display_to_grid(
            self.action.data.get("x", 0), self.action.data.get("y", 0)
        )
        if c:
            sp = self.current_level.get_sprite_at(
                int(c[0]), int(c[1]), ignore_collidable=True
            )
            if sp and "lit" in sp.tags:
                for t in sp.tags:
                    if t.startswith("v") and t[1:].isdigit():
                        vi = int(t[1:]) % 2
                        self._val[vi] = not self._val[vi]
                        break
        if self._sat():
            self.next_level()
        self._sync_ui()
        self.complete_action()
