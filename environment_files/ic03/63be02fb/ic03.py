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



def _r_xticks(frame, h, w, value, cap, y=None, fc=10, ec=3):
    row = (h - 2) if y is None else y
    m = min(cap, max(0, w - 2))
    v = max(0, min(value, m))
    for i in range(m):
        _rp(frame, h, w, 1 + i, row, fc if i < v else ec)


class Ic03UI(RenderableUserDisplay):
    def __init__(
        self,
        targets_remaining: int,
        slide_cap: int = 3,
        level_index: int = 0,
        num_levels: int = 5,
    ) -> None:
        self._targets = targets_remaining
        self._slide_cap = slide_cap
        self._level_index = level_index
        self._num_levels = num_levels
        self._state: GameState | None = None

    def update(
        self,
        targets_remaining: int,
        *,
        slide_cap: int | None = None,
        level_index: int | None = None,
        num_levels: int | None = None,
        state: GameState | None = None,
    ) -> None:
        self._targets = targets_remaining
        if slide_cap is not None:
            self._slide_cap = slide_cap
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
        _r_xticks(frame, h, w, self._slide_cap, 6, y=h - 2)
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


def make_level(sl, grid_size, difficulty, slide_cap):
    return Level(
        sprites=sl,
        grid_size=grid_size,
        data={"difficulty": difficulty, "slide_cap": slide_cap},
    )


levels = [
    make_level(
        [
            sprites["player"].clone().set_position(1, 6),
            sprites["target"].clone().set_position(1, 1),
            sprites["wall"].clone().set_position(1, 0),
        ],
        (8, 8),
        1,
        3,
    ),
    make_level(
        [
            sprites["player"].clone().set_position(1, 6),
            sprites["target"].clone().set_position(6, 1),
            sprites["wall"].clone().set_position(1, 3),
            sprites["wall"].clone().set_position(2, 3),
            sprites["wall"].clone().set_position(3, 3),
            sprites["wall"].clone().set_position(4, 3),
            sprites["wall"].clone().set_position(5, 3),
            sprites["wall"].clone().set_position(6, 3),
        ],
        (8, 8),
        2,
        2,
    ),
    make_level(
        [
            sprites["player"].clone().set_position(0, 0),
            sprites["target"].clone().set_position(7, 7),
        ]
        + [sprites["wall"].clone().set_position(x, 4) for x in range(8) if x != 3],
        (8, 8),
        3,
        4,
    ),
    # Replaced unsolvable 10×8 layout; capped slide cannot reach prior goal from (1,1).
    make_level(
        [
            sprites["player"].clone().set_position(1, 6),
            sprites["target"].clone().set_position(6, 1),
            sprites["wall"].clone().set_position(3, 3),
        ],
        (8, 8),
        4,
        3,
    ),
    make_level(
        [
            sprites["player"].clone().set_position(0, 0),
            sprites["target"].clone().set_position(7, 7),
        ],
        (8, 8),
        5,
        1,
    ),
]

BACKGROUND_COLOR = 5
PADDING_COLOR = 4


class Ic03(ARCBaseGame):
    """Each move slides at most K cells in that direction (K per level), unless blocked sooner."""

    def __init__(self) -> None:
        self._ui = Ic03UI(0)
        super().__init__(
            "ic03",
            levels,
            Camera(0, 0, 16, 16, BACKGROUND_COLOR, PADDING_COLOR, [self._ui]),
            False,
            1,
            [1, 2, 3, 4],
        )

    def on_set_level(self, level: Level) -> None:
        self._player = self.current_level.get_sprites_by_tag("player")[0]
        self._targets = self.current_level.get_sprites_by_tag("target")
        self._cap = int(level.get_data("slide_cap") or 3)
        self._ui.update(
            len(self._targets),
            slide_cap=self._cap,
            level_index=self.level_index,
            num_levels=len(levels),
            state=self._state,
        )

    def _blocked(self, x: int, y: int) -> bool:
        sprite = self.current_level.get_sprite_at(x, y, ignore_collidable=True)
        if not sprite:
            return False
        return "wall" in sprite.tags or "hazard" in sprite.tags

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
        steps = 0
        while steps < self._cap:
            nx, ny = px + dx, py + dy
            if not (0 <= nx < grid_w and 0 <= ny < grid_h):
                break
            if self._blocked(nx, ny):
                break
            px, py = nx, ny
            steps += 1

        self._player.set_position(px, py)

        for t in self._targets:
            if self._player.x == t.x and self._player.y == t.y:
                self.next_level()
                break

        self._ui.update(
            len(self._targets),
            slide_cap=self._cap,
            level_index=self.level_index,
            num_levels=len(levels),
            state=self._state,
        )
        self.complete_action()
