"""rr01: ball rolls with persistent heading; on a ramp tile ACTION5 first rotates heading CW, then steps one cell. ACTION6 toggles ramp on an empty cell (not wall / ball / exit)."""

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

G = 12
CAM = 16
DX = (1, 0, -1, 0)
DY = (0, 1, 0, -1)


class Rr01UI(RenderableUserDisplay):
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


W = Sprite(pixels=[[3]], name="w", visible=True, collidable=True, tags=["wall"])
B = Sprite(pixels=[[9]], name="b", visible=True, collidable=False, tags=["ball"])
E = Sprite(pixels=[[14]], name="e", visible=True, collidable=False, tags=["exit"])
R = Sprite(pixels=[[6]], name="r", visible=True, collidable=False, tags=["ramp"])


def bd() -> list[tuple[int, int]]:
    return (
        [(x, 0) for x in range(G)]
        + [(x, G - 1) for x in range(G)]
        + [(0, y) for y in range(G)]
        + [(G - 1, y) for y in range(G)]
    )


def mk(
    ramps: list[tuple[int, int]],
    ball: tuple[int, int],
    exitp: tuple[int, int],
    difficulty: int,
    *,
    initial_dir: int = 0,
) -> Level:
    sl: list[Sprite] = [W.clone().set_position(x, y) for x, y in bd()]
    for x, y in ramps:
        sl.append(R.clone().set_position(x, y))
    sl.append(B.clone().set_position(*ball))
    sl.append(E.clone().set_position(*exitp))
    return Level(
        sprites=sl,
        grid_size=(G, G),
        data={
            "ramps": [list(p) for p in ramps],
            "difficulty": difficulty,
            "initial_dir": initial_dir,
        },
    )


# All levels verified A5-solvable from initial_dir (default 0) with authored ramps.
levels = [
    mk([], (2, 6), (10, 6), 1),
    mk([(1, 5), (1, 7), (3, 6), (3, 7)], (2, 6), (10, 5), 2),
    mk([(10, 1)], (1, 1), (10, 10), 3),
    mk([(9, 2)], (2, 2), (9, 9), 4),
    mk([(6, 2), (6, 9)], (5, 2), (5, 9), 5),
    mk([(10, 5)], (2, 5), (10, 8), 6),
    mk([(8, 3)], (3, 3), (8, 8), 7),
]


class Rr01(ARCBaseGame):
    def __init__(self) -> None:
        self._ui = Rr01UI(0, len(levels), 1)
        super().__init__(
            "rr01",
            levels,
            Camera(0, 0, CAM, CAM, BG, PAD, [self._ui]),
            False,
            1,
            [5, 6],
        )


    def _sync_ui(self) -> None:
        self._ui.update(
            level_index=self.level_index,
            num_levels=len(levels),
            ticks=1,
            state=self._state,
        )

    def on_set_level(self, level: Level) -> None:
        self._ball = self.current_level.get_sprites_by_tag("ball")[0]
        self._ex = self.current_level.get_sprites_by_tag("exit")[0]
        self._ramp = {
            (s.x, s.y) for s in self.current_level.get_sprites_by_tag("ramp")
        }
        self._dir = int(self.current_level.get_data("initial_dir") or 0) % 4

    def _toggle_ramp(self, gx: int, gy: int) -> None:
        if (gx, gy) in self._wall_cells():
            return
        if (gx, gy) == (self._ball.x, self._ball.y) or (gx, gy) == (
            self._ex.x,
            self._ex.y,
        ):
            return
        if (gx, gy) in self._ramp:
            self._ramp.discard((gx, gy))
            for s in list(self.current_level.get_sprites_by_tag("ramp")):
                if s.x == gx and s.y == gy:
                    self.current_level.remove_sprite(s)
        else:
            self._ramp.add((gx, gy))
            self.current_level.add_sprite(R.clone().set_position(gx, gy))

    def step(self) -> None:
        if self.action.id == GameAction.ACTION6:
            c = self.camera.display_to_grid(
                self.action.data.get("x", 0), self.action.data.get("y", 0)
            )
            if c:
                self._toggle_ramp(int(c[0]), int(c[1]))
            self._sync_ui()
            self.complete_action()
            return
        if self.action.id == GameAction.ACTION5:
            bx, by = self._ball.x, self._ball.y
            d = self._dir
            if (bx, by) in self._ramp:
                d = (d + 1) % 4
                self._dir = d
            nx, ny = bx + DX[d], by + DY[d]
            if not (0 <= nx < G and 0 <= ny < G):
                self._sync_ui()
                self.complete_action()
                return
            sp = self.current_level.get_sprite_at(nx, ny, ignore_collidable=True)
            if sp and "wall" in sp.tags:
                self._sync_ui()
                self.complete_action()
                return
            self._ball.set_position(nx, ny)
            if nx == self._ex.x and ny == self._ex.y:
                self.next_level()
            self._sync_ui()
            self.complete_action()
            return
        self._sync_ui()
        self.complete_action()

    def _wall_cells(self) -> set[tuple[int, int]]:
        return {(s.x, s.y) for s in self.current_level.get_sprites_by_tag("wall")}
