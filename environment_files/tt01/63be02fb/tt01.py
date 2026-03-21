from arcengine import (
    ARCBaseGame,
    Camera,
    GameState,
    Level,
    RenderableUserDisplay,
    Sprite,
)


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


class Tt01UI(RenderableUserDisplay):
    def __init__(self, targets_remaining: int, level_index: int = 0, num_levels: int = 3) -> None:
        self._targets = targets_remaining
        self._level_index = level_index
        self._num_levels = num_levels
        self._state: GameState | None = None

    def update(
        self,
        targets_remaining: int,
        *,
        level_index: int | None = None,
        num_levels: int | None = None,
        state: GameState | None = None,
    ) -> None:
        self._targets = targets_remaining
        if level_index is not None:
            self._level_index = level_index
        if num_levels is not None:
            self._num_levels = num_levels
        if state is not None:
            self._state = state

    def render_interface(self, frame):
        import numpy as np

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape
        _r_dots(frame, h, w, self._level_index, self._num_levels, 0)
        _r_ticks(frame, h, w, self._targets)
        go = self._state == GameState.GAME_OVER
        win = self._state == GameState.WIN
        _r_bar(frame, h, w, go, win)
        return frame


sprites = {
    "player": Sprite(
        pixels=[[9]],
        name="player",
        visible=True,
        collidable=True,
        tags=["player"],
    ),
    "target": Sprite(
        pixels=[[11]],
        name="target",
        visible=True,
        collidable=False,
        tags=["target"],
    ),
    "wall": Sprite(
        pixels=[[3]],
        name="wall",
        visible=True,
        collidable=True,
        tags=["wall"],
    ),
    "hazard": Sprite(
        pixels=[[8]],
        name="hazard",
        visible=True,
        collidable=True,
        tags=["hazard"],
    ),
}

levels = [
    Level(
        sprites=[
            sprites["player"].clone().set_position(1, 1),
            sprites["target"].clone().set_position(3, 3),
            sprites["target"].clone().set_position(5, 2),
            sprites["target"].clone().set_position(2, 5),
            sprites["wall"].clone().set_position(2, 2),
            sprites["wall"].clone().set_position(4, 4),
            sprites["wall"].clone().set_position(6, 1),
            sprites["hazard"].clone().set_position(7, 3),
        ],
        grid_size=(8, 8),
        data={"difficulty": 1},
    ),
    Level(
        sprites=[
            sprites["player"].clone().set_position(2, 2),
            sprites["target"].clone().set_position(6, 6),
            sprites["target"].clone().set_position(8, 3),
            sprites["target"].clone().set_position(4, 10),
            sprites["target"].clone().set_position(12, 8),
            sprites["wall"].clone().set_position(3, 3),
            sprites["wall"].clone().set_position(5, 5),
            sprites["wall"].clone().set_position(7, 7),
            sprites["wall"].clone().set_position(10, 4),
            sprites["wall"].clone().set_position(8, 12),
            sprites["hazard"].clone().set_position(6, 4),
            sprites["hazard"].clone().set_position(10, 10),
        ],
        grid_size=(16, 16),
        data={"difficulty": 2},
    ),
    Level(
        sprites=[
            sprites["player"].clone().set_position(5, 5),
            sprites["target"].clone().set_position(10, 10),
            sprites["target"].clone().set_position(15, 5),
            sprites["target"].clone().set_position(8, 18),
            sprites["target"].clone().set_position(20, 12),
            sprites["target"].clone().set_position(3, 20),
            sprites["wall"].clone().set_position(6, 6),
            sprites["wall"].clone().set_position(12, 8),
            sprites["wall"].clone().set_position(18, 15),
            sprites["wall"].clone().set_position(10, 20),
            sprites["wall"].clone().set_position(5, 12),
            sprites["wall"].clone().set_position(15, 3),
            sprites["wall"].clone().set_position(20, 20),
            sprites["hazard"].clone().set_position(8, 8),
            sprites["hazard"].clone().set_position(14, 14),
            sprites["hazard"].clone().set_position(18, 6),
        ],
        grid_size=(24, 24),
        data={"difficulty": 3},
    ),
]

BACKGROUND_COLOR = 5
PADDING_COLOR = 4


class Tt01(ARCBaseGame):
    """Collection game with pre-defined levels. Player collects targets."""

    def __init__(self) -> None:
        self._ui = Tt01UI(0)
        super().__init__(
            "tt01",
            levels,
            Camera(0, 0, 24, 24, BACKGROUND_COLOR, PADDING_COLOR, [self._ui]),
            False,
            1,
            [1, 2, 3, 4],
        )

    def on_set_level(self, level: Level) -> None:
        self._player = self.current_level.get_sprites_by_tag("player")[0]
        self._targets = self.current_level.get_sprites_by_tag("target")
        self._ui.update(
            len(self._targets),
            level_index=self.level_index,
            num_levels=len(levels),
            state=self._state,
        )

    def step(self) -> None:
        dx = 0
        dy = 0
        moved = False

        if self.action.id.value == 1:
            dy = -1
            moved = True
        elif self.action.id.value == 2:
            dy = 1
            moved = True
        elif self.action.id.value == 3:
            dx = -1
            moved = True
        elif self.action.id.value == 4:
            dx = 1
            moved = True

        if not moved:
            self.complete_action()
            return

        new_x = self._player.x + dx
        new_y = self._player.y + dy

        grid_w, grid_h = self.current_level.grid_size
        if 0 <= new_x < grid_w and 0 <= new_y < grid_h:
            sprite = self.current_level.get_sprite_at(
                new_x, new_y, ignore_collidable=True
            )

            if sprite and "target" in sprite.tags:
                self.current_level.remove_sprite(sprite)
                self._targets.remove(sprite)
                self._player.set_position(new_x, new_y)
                self._ui.update(
                    len(self._targets),
                    level_index=self.level_index,
                    num_levels=len(levels),
                    state=self._state,
                )
            elif not sprite or not sprite.is_collidable:
                self._player.set_position(new_x, new_y)

        if len(self._targets) == 0:
            self.next_level()

        self._ui.update(
            len(self._targets),
            level_index=self.level_index,
            num_levels=len(levels),
            state=self._state,
        )
        self.complete_action()
