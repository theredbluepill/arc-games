"""ic01 — frictionless ice movement on a grid.

**One ACTION1–4 press = one slide in that direction**, not one step:

- From your stop cell, you keep moving cell-by-cell in that direction until the *next* cell
  would leave the grid **or** hit a **wall** (gray) or **hazard** (red). You never enter those;
  you **stop on the last empty cell** before the block or edge.

- The **yellow goal** is *not* solid: it does not block a slide. If your slide path crosses the
  goal, you **land on it** and the level clears. A **wall past the goal** (see level 1) is used
  when designers need you to **stop exactly** on the goal tile instead of sliding past.

This is **not** the same as ic02 (torus wrap) — here the grid edge always stops you.
"""

from arcengine import (
    ARCBaseGame,
    Camera,
    Level,
    RenderableUserDisplay,
    Sprite,
)


class Ic01UI(RenderableUserDisplay):
    """Bottom-right HUD: light blue = sliding ice; yellow = your stop cell is a goal."""

    def __init__(self, on_goal: bool) -> None:
        self._on_goal = on_goal

    def update(self, on_goal: bool) -> None:
        self._on_goal = on_goal

    def render_interface(self, frame):
        import numpy as np

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape
        color = 11 if self._on_goal else 10
        for dy in range(4):
            for dx in range(4):
                frame[h - 4 + dy, w - 4 + dx] = color
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


def make_level(sprites_list, grid_size, difficulty):
    return Level(
        sprites=sprites_list,
        grid_size=grid_size,
        data={"difficulty": difficulty},
    )


# Ice reachability is not full-grid: opposite corners like (1,6)→(6,1) can be impossible
# on an empty board. Each layout below is BFS-checked under slide-to-block physics.
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
    make_level(
        [
            sprites["player"].clone().set_position(0, 0),
            sprites["target"].clone().set_position(7, 7),
        ],
        (8, 8),
        2,
    ),
    make_level(
        [
            sprites["player"].clone().set_position(0, 0),
            sprites["target"].clone().set_position(7, 7),
            sprites["hazard"].clone().set_position(4, 4),
        ],
        (8, 8),
        3,
    ),
    make_level(
        [
            sprites["player"].clone().set_position(0, 0),
            sprites["target"].clone().set_position(9, 0),
        ]
        + [sprites["wall"].clone().set_position(x, 4) for x in range(10) if x != 5],
        (10, 8),
        4,
    ),
    make_level(
        [
            sprites["player"].clone().set_position(0, 7),
            sprites["target"].clone().set_position(7, 0),
            sprites["hazard"].clone().set_position(3, 3),
            sprites["hazard"].clone().set_position(4, 3),
            sprites["hazard"].clone().set_position(3, 4),
            sprites["hazard"].clone().set_position(4, 4),
        ],
        (8, 8),
        5,
    ),
]

BACKGROUND_COLOR = 5
PADDING_COLOR = 4


class Ic01(ARCBaseGame):
    """Ice grid: each cardinal action is a full slide until edge, wall, or hazard (see module doc)."""

    def __init__(self) -> None:
        self._ui = Ic01UI(False)
        super().__init__(
            "ic01",
            levels,
            Camera(0, 0, 16, 16, BACKGROUND_COLOR, PADDING_COLOR, [self._ui]),
            False,
            1,
            [1, 2, 3, 4],
        )

    def on_set_level(self, level: Level) -> None:
        self._player = self.current_level.get_sprites_by_tag("player")[0]
        self._targets = self.current_level.get_sprites_by_tag("target")
        self._sync_ui()

    def _on_goal_cell(self) -> bool:
        return any(
            self._player.x == t.x and self._player.y == t.y for t in self._targets
        )

    def _sync_ui(self) -> None:
        self._ui.update(self._on_goal_cell())

    def _blocked(self, x: int, y: int) -> bool:
        """Walls and hazards stop a slide; targets and empty floor do not."""
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
        # Slide: absorb the whole ray in one action (unlike normal 1-cell movement).
        while True:
            nx, ny = px + dx, py + dy
            if not (0 <= nx < grid_w and 0 <= ny < grid_h):
                break
            if self._blocked(nx, ny):
                break
            px, py = nx, ny

        self._player.set_position(px, py)
        self._sync_ui()

        for t in self._targets:
            if self._player.x == t.x and self._player.y == t.y:
                self.next_level()
                break

        self.complete_action()
