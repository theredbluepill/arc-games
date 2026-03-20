"""Rotating hazard: a lethal row index advances every N steps; lose if you stand on it when active."""

from arcengine import (
    ARCBaseGame,
    Camera,
    Level,
    RenderableUserDisplay,
    Sprite,
)


class Rh01UI(RenderableUserDisplay):
    def __init__(self, row: int) -> None:
        self._row = row

    def update(self, row: int) -> None:
        self._row = row

    def render_interface(self, frame):
        import numpy as np

        if not isinstance(frame, np.ndarray):
            return frame
        h, _w = frame.shape
        for i in range(min(self._row + 1, 12)):
            frame[h - 2, 1 + i] = 8
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
}


def mk(sl: list, d: int, n: int) -> Level:
    return Level(sprites=sl, grid_size=(10, 10), data={"difficulty": d, "period": n})


levels = [
    mk(
        [
            sprites["player"].clone().set_position(0, 0),
            sprites["goal"].clone().set_position(9, 9),
        ],
        1,
        4,
    ),
    mk(
        [
            sprites["player"].clone().set_position(1, 1),
            sprites["goal"].clone().set_position(8, 8),
        ],
        2,
        3,
    ),
    mk(
        [
            sprites["player"].clone().set_position(0, 5),
            sprites["goal"].clone().set_position(9, 5),
            sprites["wall"].clone().set_position(5, 5),
        ],
        3,
        3,
    ),
    mk(
        [
            sprites["player"].clone().set_position(2, 2),
            sprites["goal"].clone().set_position(7, 7),
        ],
        4,
        2,
    ),
    mk(
        [
            sprites["player"].clone().set_position(0, 9),
            sprites["goal"].clone().set_position(9, 0),
        ],
        5,
        2,
    ),
]

BACKGROUND_COLOR = 5
PADDING_COLOR = 4


class Rh01(ARCBaseGame):
    def __init__(self) -> None:
        self._ui = Rh01UI(0)
        super().__init__(
            "rh01",
            levels,
            Camera(0, 0, 16, 16, BACKGROUND_COLOR, PADDING_COLOR, [self._ui]),
            False,
            1,
            [1, 2, 3, 4],
        )

    def on_set_level(self, level: Level) -> None:
        self._player = self.current_level.get_sprites_by_tag("player")[0]
        self._goal = self.current_level.get_sprites_by_tag("goal")[0]
        self._period = int(level.get_data("period") or 3)
        self._ticks = 0
        self._danger_y = 9
        gw, _gh = self.current_level.grid_size
        self._ui.update(self._danger_y % max(gw, 1))

    def _tick_hazard(self) -> None:
        self._ticks += 1
        if self._ticks >= self._period:
            self._ticks = 0
            _gw, gh = self.current_level.grid_size
            self._danger_y = (self._danger_y + 1) % gh
            self._ui.update(self._danger_y)

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

        nx = self._player.x + dx
        ny = self._player.y + dy
        gw, gh = self.current_level.grid_size
        moved = False
        if dx != 0 or dy != 0:
            if (0 <= nx < gw and 0 <= ny < gh):
                sp = self.current_level.get_sprite_at(nx, ny, ignore_collidable=True)
                if not (sp and "wall" in sp.tags):
                    self._player.set_position(nx, ny)
                    moved = True

        self._tick_hazard()

        if self._player.y == self._danger_y:
            self.lose()
            self.complete_action()
            return

        if self._player.x == self._goal.x and self._player.y == self._goal.y:
            self.next_level()

        self.complete_action()
