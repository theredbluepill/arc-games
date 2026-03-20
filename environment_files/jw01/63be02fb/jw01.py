"""Jigsaw swap: ACTION6 on a trigger cell swaps two fixed axis-aligned rectangles (same area)."""

from arcengine import (
    ARCBaseGame,
    Camera,
    GameAction,
    Level,
    RenderableUserDisplay,
    Sprite,
)


class Jw01UI(RenderableUserDisplay):
    def __init__(self, swaps: int) -> None:
        self._swaps = swaps

    def update(self, swaps: int) -> None:
        self._swaps = swaps

    def render_interface(self, frame):
        import numpy as np

        if not isinstance(frame, np.ndarray):
            return frame
        h, _w = frame.shape
        for i in range(min(self._swaps, 8)):
            frame[h - 2, 1 + i] = 11
        return frame


sprites = {
    "player": Sprite(
        pixels=[[9]],
        name="player",
        visible=True,
        collidable=True,
        tags=["player"],
    ),
    "goal": Sprite(
        pixels=[[14]],
        name="goal",
        visible=True,
        collidable=False,
        tags=["goal"],
    ),
    "wall": Sprite(
        pixels=[[3]],
        name="wall",
        visible=True,
        collidable=True,
        tags=["wall"],
    ),
    "trigger": Sprite(
        pixels=[[6]],
        name="trigger",
        visible=True,
        collidable=False,
        tags=["trigger"],
    ),
    "box": Sprite(
        pixels=[[15]],
        name="box",
        visible=True,
        collidable=True,
        tags=["box"],
    ),
}


def mk(sl: list, d: int, ra: tuple[int, int, int, int], rb: tuple[int, int, int, int]) -> Level:
    return Level(
        sprites=sl,
        grid_size=(10, 10),
        data={"difficulty": d, "rect_a": list(ra), "rect_b": list(rb)},
    )


levels = [
    mk(
        [
            sprites["player"].clone().set_position(0, 5),
            sprites["goal"].clone().set_position(9, 5),
            sprites["trigger"].clone().set_position(5, 0),
            sprites["box"].clone().set_position(2, 5),
            sprites["wall"].clone().set_position(4, 5),
        ],
        1,
        (1, 4, 2, 1),
        (6, 4, 2, 1),
    ),
    mk(
        [
            sprites["player"].clone().set_position(1, 1),
            sprites["goal"].clone().set_position(8, 8),
            sprites["trigger"].clone().set_position(5, 9),
            sprites["box"].clone().set_position(2, 2),
            sprites["wall"].clone().set_position(5, 5),
        ],
        2,
        (2, 2, 2, 2),
        (6, 6, 2, 2),
    ),
    mk(
        [
            sprites["player"].clone().set_position(0, 0),
            sprites["goal"].clone().set_position(9, 9),
            sprites["trigger"].clone().set_position(9, 0),
        ]
        + [sprites["wall"].clone().set_position(3, y) for y in range(4, 7)],
        3,
        (4, 4, 2, 1),
        (7, 4, 2, 1),
    ),
    mk(
        [
            sprites["player"].clone().set_position(2, 5),
            sprites["goal"].clone().set_position(7, 5),
            sprites["trigger"].clone().set_position(0, 0),
            sprites["box"].clone().set_position(3, 5),
        ],
        4,
        (1, 3, 3, 1),
        (6, 3, 3, 1),
    ),
    mk(
        [
            sprites["player"].clone().set_position(1, 5),
            sprites["goal"].clone().set_position(8, 5),
            sprites["trigger"].clone().set_position(5, 5),
        ],
        5,
        (2, 4, 2, 2),
        (6, 4, 2, 2),
    ),
]

BACKGROUND_COLOR = 5
PADDING_COLOR = 4


def _cells(x: int, y: int, w: int, h: int) -> list[tuple[int, int]]:
    return [(x + dx, y + dy) for dx in range(w) for dy in range(h)]


class Jw01(ARCBaseGame):
    def __init__(self) -> None:
        self._ui = Jw01UI(0)
        super().__init__(
            "jw01",
            levels,
            Camera(0, 0, 16, 16, BACKGROUND_COLOR, PADDING_COLOR, [self._ui]),
            False,
            1,
            [1, 2, 3, 4, 6],
        )

    def on_set_level(self, level: Level) -> None:
        self._player = self.current_level.get_sprites_by_tag("player")[0]
        self._goal = self.current_level.get_sprites_by_tag("goal")[0]
        ra = level.get_data("rect_a") or [1, 4, 2, 1]
        rb = level.get_data("rect_b") or [6, 4, 2, 1]
        self._ra = tuple(int(x) for x in ra)
        self._rb = tuple(int(x) for x in rb)
        self._swap_count = 0
        self._ui.update(0)

    def _swap_rects(self) -> None:
        x0, y0, w0, h0 = self._ra
        x1, y1, w1, h1 = self._rb
        ca = _cells(x0, y0, w0, h0)
        cb = _cells(x1, y1, w1, h1)
        if len(ca) != len(cb):
            return
        staged: list[
            tuple[Sprite | None, Sprite | None, int, int, int, int]
        ] = []
        for (ax, ay), (bx, by) in zip(ca, cb):
            sa = self.current_level.get_sprite_at(ax, ay, ignore_collidable=True)
            sb = self.current_level.get_sprite_at(bx, by, ignore_collidable=True)
            if sa and "trigger" in sa.tags:
                sa = None
            if sb and "trigger" in sb.tags:
                sb = None
            staged.append((sa, sb, ax, ay, bx, by))
        k = 0
        for sa, sb, _ax, _ay, _bx, _by in staged:
            if sa:
                sa.set_position(200 + k, 0)
                k += 1
            if sb:
                sb.set_position(200 + k, 0)
                k += 1
        for sa, sb, ax, ay, bx, by in staged:
            if sa:
                sa.set_position(bx, by)
            if sb:
                sb.set_position(ax, ay)
        self._player = self.current_level.get_sprites_by_tag("player")[0]
        self._goal = self.current_level.get_sprites_by_tag("goal")[0]
        self._swap_count += 1
        self._ui.update(self._swap_count)

    def step(self) -> None:
        if self.action.id == GameAction.ACTION6:
            raw_x = self.action.data.get("x", 0)
            raw_y = self.action.data.get("y", 0)
            g = self.camera.display_to_grid(int(raw_x), int(raw_y))
            if g is None:
                self.complete_action()
                return
            gx, gy = g
            sp = self.current_level.get_sprite_at(gx, gy, ignore_collidable=True)
            if sp and "trigger" in sp.tags:
                self._swap_rects()
            self.complete_action()
            return

        dx = dy = 0
        if self.action.id.value == 1:
            dy = -1
        elif self.action.id.value == 2:
            dy = 1
        elif self.action.id.value == 3:
            dx = -1
        elif self.action.id.value == 4:
            dx = 1

        if dx == 0 and dy == 0:
            self.complete_action()
            return

        nx = self._player.x + dx
        ny = self._player.y + dy
        gw, gh = self.current_level.grid_size
        if not (0 <= nx < gw and 0 <= ny < gh):
            self.complete_action()
            return

        sp = self.current_level.get_sprite_at(nx, ny, ignore_collidable=True)
        if sp and "wall" in sp.tags:
            self.complete_action()
            return
        if sp and "trigger" in sp.tags:
            self.complete_action()
            return
        if sp and "box" in sp.tags:
            bx, by = nx + dx, ny + dy
            if not (0 <= bx < gw and 0 <= by < gh):
                self.complete_action()
                return
            behind = self.current_level.get_sprite_at(bx, by, ignore_collidable=True)
            if behind and ("wall" in behind.tags or "box" in behind.tags):
                self.complete_action()
                return
            sp.set_position(bx, by)
            self._player.set_position(nx, ny)
        elif not sp or not sp.is_collidable:
            self._player.set_position(nx, ny)

        if self._player.x == self._goal.x and self._player.y == self._goal.y:
            self.next_level()

        self.complete_action()
