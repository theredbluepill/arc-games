"""Weak floor: brown tiles collapse to lethal holes after you leave. Maze walls force routing; each level has a tight move budget (lose if you run out before the goal)."""

from arcengine import (
    ARCBaseGame,
    Camera,
    Level,
    RenderableUserDisplay,
    Sprite,
)

GW = GH = 10


class Wk01UI(RenderableUserDisplay):
    """Bottom-right: red = hole death or out of moves; maroon in play. Bottom-left weak-floor cue. Top: move budget (yellow = left, gray = spent)."""

    def __init__(self) -> None:
        self._fail = False
        self._steps_left = 0
        self._step_cap = 1

    def update(
        self,
        *,
        fail: bool | None = None,
        steps_left: int | None = None,
        step_cap: int | None = None,
    ) -> None:
        if fail is not None:
            self._fail = fail
        if steps_left is not None:
            self._steps_left = steps_left
        if step_cap is not None:
            self._step_cap = max(1, step_cap)

    def render_interface(self, frame):
        import numpy as np

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape
        br = 8 if self._fail else 13
        bl = 8 if self._fail else 13
        for dy in range(4):
            for dx in range(4):
                frame[h - 4 + dy, w - 4 + dx] = br
        for dy in range(3):
            for dx in range(3):
                frame[h - 4 + dy, dx] = bl
        cap = min(self._step_cap, 14)
        for i in range(cap):
            cx = 1 + i * 2
            if cx >= w:
                break
            col = 11 if i < self._steps_left else 3
            frame[1, cx] = col
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
    "weak": Sprite(
        pixels=[[13]],
        name="weak",
        visible=True,
        collidable=False,
        tags=["weak"],
    ),
    "hole": Sprite(
        pixels=[[5]],
        name="hole",
        visible=True,
        collidable=True,
        tags=["hole"],
    ),
    "wall": Sprite(
        pixels=[[3]],
        name="wall",
        visible=True,
        collidable=True,
        tags=["wall"],
    ),
}


def _level_from_ascii(
    rows: list[str],
    *,
    max_steps: int,
    difficulty: int,
) -> Level:
    """# wall, . floor, P start, G goal, w weak (still walkable until collapsed)."""
    free: set[tuple[int, int]] = set()
    player_pos: tuple[int, int] | None = None
    goal_pos: tuple[int, int] | None = None
    weak_cells: list[tuple[int, int]] = []
    for y, row in enumerate(rows):
        if len(row) != GW:
            raise ValueError(f"row {y} width {len(row)} != {GW}")
        for x, ch in enumerate(row):
            if ch == "#":
                continue
            free.add((x, y))
            if ch == "P":
                player_pos = (x, y)
            elif ch == "G":
                goal_pos = (x, y)
            elif ch == "w":
                weak_cells.append((x, y))
            elif ch != ".":
                raise ValueError(f"bad char {ch!r} at {x},{y}")
    if player_pos is None or goal_pos is None:
        raise ValueError("P and G required")
    sl: list[Sprite] = []
    for x in range(GW):
        for y in range(GH):
            if (x, y) not in free:
                sl.append(sprites["wall"].clone().set_position(x, y))
    for wx, wy in weak_cells:
        sl.append(sprites["weak"].clone().set_position(wx, wy))
    px, py = player_pos
    gx, gy = goal_pos
    sl.append(sprites["player"].clone().set_position(px, py))
    sl.append(sprites["target"].clone().set_position(gx, gy))
    return Level(
        sprites=sl,
        grid_size=(GW, GH),
        data={"difficulty": difficulty, "max_steps": max_steps},
    )


def _corridor_level(
    *,
    y_row: int,
    weak_xs: list[int],
    max_steps: int,
    difficulty: int,
) -> Level:
    rows = []
    for y in range(GH):
        line = []
        for x in range(GW):
            if y == y_row:
                if x == 0:
                    line.append("P")
                elif x == GW - 1:
                    line.append("G")
                elif x in weak_xs:
                    line.append("w")
                else:
                    line.append(".")
            else:
                line.append("#")
        rows.append("".join(line))
    return _level_from_ascii(rows, max_steps=max_steps, difficulty=difficulty)


levels = [
    _corridor_level(y_row=5, weak_xs=[3, 6], max_steps=12, difficulty=1),
    _level_from_ascii(
        [
            "##########",
            "#P.......#",
            "#.######.#",
            "#.#....#.#",
            "#.#.##.#.#",
            "#.#.##.#.#",
            "#.#....#.#",
            "#.######.#",
            "#.......G#",
            "##########",
        ],
        max_steps=22,
        difficulty=2,
    ),
    _level_from_ascii(
        [
            "##########",
            "#P#......#",
            "#.#.####.#",
            "#...#..#.#",
            "###.#..#.#",
            "#...#..#.#",
            "#.###..#.#",
            "#.....ww.#",
            "#.######G#",
            "##########",
        ],
        max_steps=25,
        difficulty=3,
    ),
    _level_from_ascii(
        [
            "##########",
            "#P.......#",
            "#.#######.",
            "#.#.....#.",
            "#.#.#.#.#.",
            "#.#.#.#.#.",
            "#.#.....#.",
            "#.#######.",
            "#.......G#",
            "##########",
        ],
        max_steps=22,
        difficulty=4,
    ),
    _level_from_ascii(
        [
            "##########",
            "#P..#....#",
            "#.##.#.#.#",
            "#....#.#.#",
            "###.##.#.#",
            "#...#..#.#",
            "#.#.#.##.#",
            "#.#....w.#",
            "#.######G#",
            "##########",
        ],
        max_steps=20,
        difficulty=5,
    ),
]

BACKGROUND_COLOR = 5
PADDING_COLOR = 4


class Wk01(ARCBaseGame):
    def __init__(self) -> None:
        self._ui = Wk01UI()
        super().__init__(
            "wk01",
            levels,
            Camera(0, 0, 16, 16, BACKGROUND_COLOR, PADDING_COLOR, [self._ui]),
            False,
            1,
            [1, 2, 3, 4],
        )

    def on_set_level(self, level: Level) -> None:
        self._player = self.current_level.get_sprites_by_tag("player")[0]
        self._targets = self.current_level.get_sprites_by_tag("target")
        cap = int(self.current_level.get_data("max_steps") or 999)
        self._step_cap = max(1, cap)
        self._steps_remaining = self._step_cap
        self._ui.update(
            fail=False,
            steps_left=self._steps_remaining,
            step_cap=self._step_cap,
        )

    def _collapse_weak(self, left_pos: tuple[int, int]) -> None:
        wx, wy = left_pos
        sp = self.current_level.get_sprite_at(wx, wy, ignore_collidable=True)
        if sp and "weak" in sp.tags:
            self.current_level.remove_sprite(sp)
            hole = sprites["hole"].clone().set_position(wx, wy)
            self.current_level.add_sprite(hole)

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

        prev = (self._player.x, self._player.y)
        new_x = self._player.x + dx
        new_y = self._player.y + dy
        grid_w, grid_h = self.current_level.grid_size
        if not (0 <= new_x < grid_w and 0 <= new_y < grid_h):
            self.complete_action()
            return

        sprite = self.current_level.get_sprite_at(new_x, new_y, ignore_collidable=True)

        if sprite and "wall" in sprite.tags:
            self.complete_action()
            return

        if sprite and "hole" in sprite.tags:
            self._ui.update(fail=True, steps_left=self._steps_remaining, step_cap=self._step_cap)
            self.lose()
            self.complete_action()
            return

        if not sprite or not sprite.is_collidable:
            self._collapse_weak(prev)
            self._player.set_position(new_x, new_y)
            self._steps_remaining -= 1

            for t in self._targets:
                if self._player.x == t.x and self._player.y == t.y:
                    self.next_level()
                    self.complete_action()
                    return

            if self._steps_remaining <= 0:
                self._ui.update(fail=True, steps_left=0, step_cap=self._step_cap)
                self.lose()
                self.complete_action()
                return

            self._ui.update(
                fail=False,
                steps_left=self._steps_remaining,
                step_cap=self._step_cap,
            )

        self.complete_action()
