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


class Ic02UI(RenderableUserDisplay):
    def __init__(
        self,
        targets_remaining: int,
        level_index: int = 0,
        num_levels: int = 5,
    ) -> None:
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


def make_level(sl, grid_size, difficulty):
    return Level(sprites=sl, grid_size=grid_size, data={"difficulty": difficulty})


levels = [
    make_level(
        [
            sprites["player"].clone().set_position(1, 6),
            sprites["target"].clone().set_position(1, 1),
            sprites["wall"].clone().set_position(1, 0),
        ],
        (8, 8),
        1,
    ),
    # Wall one cell past the goal on the slide axis stops the torus orbit on that line.
    make_level(
        [
            sprites["player"].clone().set_position(2, 6),
            sprites["target"].clone().set_position(2, 2),
            sprites["wall"].clone().set_position(2, 1),
        ],
        (8, 8),
        2,
    ),
    make_level(
        [
            sprites["player"].clone().set_position(6, 2),
            sprites["target"].clone().set_position(6, 6),
            sprites["wall"].clone().set_position(6, 7),
        ],
        (8, 8),
        3,
    ),
    make_level(
        [
            sprites["player"].clone().set_position(1, 3),
            sprites["target"].clone().set_position(5, 3),
            sprites["wall"].clone().set_position(6, 3),
        ],
        (8, 8),
        4,
    ),
    make_level(
        [
            sprites["player"].clone().set_position(6, 4),
            sprites["target"].clone().set_position(2, 4),
            sprites["wall"].clone().set_position(1, 4),
        ],
        (8, 8),
        5,
    ),
]

BACKGROUND_COLOR = 5
PADDING_COLOR = 4


class Ic02(ARCBaseGame):
    """Ice slide on a torus: leaving an edge wraps to the opposite side."""

    def __init__(self) -> None:
        self._ui = Ic02UI(0)
        super().__init__(
            "ic02",
            levels,
            Camera(0, 0, 16, 16, BACKGROUND_COLOR, PADDING_COLOR, [self._ui]),
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

    def _blocked(self, x: int, y: int) -> bool:
        sprite = self.current_level.get_sprite_at(x, y, ignore_collidable=True)
        if not sprite:
            return False
        return "wall" in sprite.tags or "hazard" in sprite.tags

    def _wrap_step(self, x: int, y: int, dx: int, dy: int, gw: int, gh: int) -> tuple[int, int]:
        nx = x + dx
        ny = y + dy
        if nx < 0:
            nx = gw - 1
        elif nx >= gw:
            nx = 0
        if ny < 0:
            ny = gh - 1
        elif ny >= gh:
            ny = 0
        return nx, ny

    def step(self) -> None:
        dx = 0
        dy = 0
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

        grid_w, grid_h = self.current_level.grid_size
        px, py = self._player.x, self._player.y
        for _ in range(grid_w * grid_h):
            nx, ny = self._wrap_step(px, py, dx, dy, grid_w, grid_h)
            if self._blocked(nx, ny):
                break
            px, py = nx, ny

        self._player.set_position(px, py)

        for t in self._targets:
            if self._player.x == t.x and self._player.y == t.y:
                self.next_level()
                break

        self._ui.update(
            len(self._targets),
            level_index=self.level_index,
            num_levels=len(levels),
            state=self._state,
        )
        self.complete_action()
