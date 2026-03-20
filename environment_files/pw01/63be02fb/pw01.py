"""Weighted plates: two yellow plates must both have a crate on them; then reach the green goal."""

from arcengine import (
    ARCBaseGame,
    Camera,
    Level,
    RenderableUserDisplay,
    Sprite,
)


class Pw01UI(RenderableUserDisplay):
    def __init__(self, ok: int) -> None:
        self._ok = ok

    def update(self, ok: int) -> None:
        self._ok = ok

    def render_interface(self, frame):
        import numpy as np

        if not isinstance(frame, np.ndarray):
            return frame
        h, _w = frame.shape
        for i in range(min(self._ok, 5)):
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
    "block": Sprite(
        pixels=[[15]],
        name="block",
        visible=True,
        collidable=True,
        tags=["block"],
    ),
    "plate": Sprite(
        pixels=[[11]],
        name="plate",
        visible=True,
        collidable=False,
        tags=["plate"],
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
}


def mk(sl: list, d: int) -> Level:
    return Level(sprites=sl, grid_size=(10, 10), data={"difficulty": d})


levels = [
    mk(
        [
            sprites["player"].clone().set_position(0, 5),
            sprites["block"].clone().set_position(2, 4),
            sprites["block"].clone().set_position(2, 6),
            sprites["plate"].clone().set_position(4, 4),
            sprites["plate"].clone().set_position(4, 6),
            sprites["goal"].clone().set_position(8, 5),
        ],
        1,
    ),
    mk(
        [
            sprites["player"].clone().set_position(1, 1),
            sprites["block"].clone().set_position(3, 3),
            sprites["block"].clone().set_position(3, 5),
            sprites["plate"].clone().set_position(5, 3),
            sprites["plate"].clone().set_position(5, 5),
            sprites["goal"].clone().set_position(8, 8),
        ],
        2,
    ),
    mk(
        [
            sprites["player"].clone().set_position(0, 0),
            sprites["block"].clone().set_position(1, 2),
            sprites["block"].clone().set_position(2, 1),
            sprites["plate"].clone().set_position(4, 2),
            sprites["plate"].clone().set_position(2, 4),
            sprites["goal"].clone().set_position(9, 9),
        ]
        + [sprites["wall"].clone().set_position(6, y) for y in range(10) if y not in (4, 5)],
        3,
    ),
    mk(
        [
            sprites["player"].clone().set_position(2, 5),
            sprites["block"].clone().set_position(3, 4),
            sprites["block"].clone().set_position(3, 6),
            sprites["plate"].clone().set_position(5, 4),
            sprites["plate"].clone().set_position(5, 6),
            sprites["goal"].clone().set_position(8, 5),
        ],
        4,
    ),
    mk(
        [
            sprites["player"].clone().set_position(1, 5),
            sprites["block"].clone().set_position(2, 3),
            sprites["block"].clone().set_position(2, 7),
            sprites["plate"].clone().set_position(6, 3),
            sprites["plate"].clone().set_position(6, 7),
            sprites["goal"].clone().set_position(8, 5),
        ],
        5,
    ),
]

BACKGROUND_COLOR = 5
PADDING_COLOR = 4


class Pw01(ARCBaseGame):
    def __init__(self) -> None:
        self._ui = Pw01UI(0)
        super().__init__(
            "pw01",
            levels,
            Camera(0, 0, 16, 16, BACKGROUND_COLOR, PADDING_COLOR, [self._ui]),
            False,
            1,
            [1, 2, 3, 4],
        )

    def on_set_level(self, level: Level) -> None:
        self._player = self.current_level.get_sprites_by_tag("player")[0]
        self._goal = self.current_level.get_sprites_by_tag("goal")[0]
        self._plates = list(self.current_level.get_sprites_by_tag("plate"))
        self._blocks = list(self.current_level.get_sprites_by_tag("block"))
        self._sync()

    def _both_plated(self) -> bool:
        for p in self._plates:
            hit = False
            for b in self._blocks:
                if b.x == p.x and b.y == p.y:
                    hit = True
                    break
            if not hit:
                return False
        return True

    def _sync(self) -> None:
        self._ui.update(2 if self._both_plated() else 0)

    def step(self) -> None:
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

        if sp and "block" in sp.tags:
            bx, by = nx + dx, ny + dy
            if not (0 <= bx < gw and 0 <= by < gh):
                self.complete_action()
                return
            behind = self.current_level.get_sprite_at(bx, by, ignore_collidable=True)
            if behind and ("block" in behind.tags or "wall" in behind.tags):
                self.complete_action()
                return
            sp.set_position(bx, by)
            self._player.set_position(nx, ny)
        elif not sp or not sp.is_collidable:
            self._player.set_position(nx, ny)

        self._sync()

        if self._both_plated() and self._player.x == self._goal.x and self._player.y == self._goal.y:
            self.next_level()

        self.complete_action()
