# MIT License
#
# Copyright (c) 2026 ARC Prize Foundation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from arcengine import (
    ARCBaseGame,
    Camera,
    Level,
    RenderableUserDisplay,
    Sprite,
)


class Tb01UI(RenderableUserDisplay):
    def __init__(self, wood: int, capacity: int, bridges: int) -> None:
        self._wood = wood
        self._capacity = capacity
        self._bridges = bridges

    def update(self, wood: int, capacity: int, bridges: int) -> None:
        self._wood = wood
        self._capacity = capacity
        self._bridges = bridges

    def render_interface(self, frame):
        import numpy as np

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape
        for i in range(self._wood):
            frame[1, 1 + i] = 12
        for i in range(self._capacity - self._wood):
            frame[1, 1 + self._wood + i] = 4
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
    "wood": Sprite(
        pixels=[[12]],
        name="wood",
        visible=True,
        collidable=False,
        tags=["wood"],
    ),
    "water": Sprite(
        pixels=[[10]],
        name="water",
        visible=True,
        collidable=False,
        tags=["water"],
    ),
    "bridge": Sprite(
        pixels=[[14]],
        name="bridge",
        visible=True,
        collidable=False,
        tags=["bridge"],
    ),
    "bank": Sprite(
        pixels=[[4]],
        name="bank",
        visible=True,
        collidable=False,
        tags=["bank"],
    ),
}


def make_tb_level(
    grid_size,
    player_pos,
    goal_pos,
    water_coords,
    wood_coords,
    bank_coords,
    difficulty,
    step_limit,
    wood_capacity,
):
    sprite_list = [
        sprites["player"].clone().set_position(*player_pos),
        sprites["goal"].clone().set_position(*goal_pos),
    ]
    for wc in water_coords:
        sprite_list.append(sprites["water"].clone().set_position(*wc))
    for wc in wood_coords:
        sprite_list.append(sprites["wood"].clone().set_position(*wc))
    for bc in bank_coords:
        sprite_list.append(sprites["bank"].clone().set_position(*bc))
    return Level(
        sprites=sprite_list,
        grid_size=grid_size,
        data={
            "difficulty": difficulty,
            "step_limit": step_limit,
            "wood_capacity": wood_capacity,
        },
    )


def make_bank_grid(width, height, exclude_rows=None, exclude_cols=None):
    """Generate bank coordinates for the entire grid, excluding water rows/cols."""
    coords = []
    for y in range(height):
        for x in range(width):
            if exclude_rows and y in exclude_rows:
                continue
            if exclude_cols and x in exclude_cols:
                continue
            coords.append((x, y))
    return coords


levels = [
    make_tb_level(
        (8, 8),
        (1, 1),
        (7, 4),
        [(2, 3), (3, 3), (4, 3), (5, 3)],  # River at row 3, 4 tiles wide
        [(1, 2), (6, 2), (1, 4), (6, 4)],  # 4 wood pieces (different positions)
        [(0, y) for y in range(8)]
        + [(x, y) for x in range(1, 8) for y in range(8) if (x < 2 or x > 5) or y != 3],
        1,
        20,
        3,
    ),
    make_tb_level(
        (10, 10),
        (1, 2),
        (9, 5),
        [(2, 4), (3, 4), (4, 4), (5, 4), (6, 4)],  # River at row 4, 5 tiles wide
        [(1, 3), (7, 3), (1, 5), (7, 5), (4, 3)],
        [(0, y) for y in range(10)]
        + [
            (x, y)
            for x in range(1, 10)
            for y in range(10)
            if (x < 2 or x > 6) or y != 4
        ],
        2,
        25,
        3,
    ),
    make_tb_level(
        (12, 12),
        (1, 2),
        (11, 6),
        [
            (2, 5),
            (3, 5),
            (4, 5),
            (5, 5),
            (6, 5),
            (7, 5),
        ],  # River at row 5, 6 tiles wide
        [(1, 4), (8, 4), (1, 6), (8, 6), (4, 4), (8, 4)],
        [(0, y) for y in range(12)]
        + [
            (x, y)
            for x in range(1, 12)
            for y in range(12)
            if (x < 2 or x > 7) or y != 5
        ],
        3,
        30,
        3,
    ),
    make_tb_level(
        (14, 14),
        (1, 3),
        (13, 8),
        [
            (2, 6),
            (3, 6),
            (4, 6),
            (5, 6),
            (6, 6),
            (7, 6),
            (8, 6),
        ],  # River at row 6, 7 tiles wide
        [(1, 5), (9, 5), (1, 7), (9, 7), (4, 5), (7, 7), (6, 5)],
        [(0, y) for y in range(14)]
        + [
            (x, y)
            for x in range(1, 14)
            for y in range(14)
            if (x < 2 or x > 8) or y != 6
        ],
        4,
        40,
        3,
    ),
    make_tb_level(
        (16, 16),
        (1, 3),
        (15, 10),
        [
            (2, 7),
            (3, 7),
            (4, 7),
            (5, 7),
            (6, 7),
            (7, 7),
            (8, 7),
            (9, 7),
        ],  # River at row 7, 8 tiles wide
        [(1, 6), (10, 6), (1, 8), (10, 8), (4, 6), (7, 8), (6, 6), (9, 8)],
        [(0, y) for y in range(16)]
        + [
            (x, y)
            for x in range(1, 16)
            for y in range(16)
            if (x < 2 or x > 9) or y != 7
        ],
        5,
        50,
        3,
    ),
]

BACKGROUND_COLOR = 5
PADDING_COLOR = 4


class Tb01(ARCBaseGame):
    """Bridge Builder - Collect wood to build bridges across water."""

    def __init__(self) -> None:
        self._ui = Tb01UI(0, 3, 0)
        super().__init__(
            "tb01",
            levels,
            Camera(0, 0, 16, 16, BACKGROUND_COLOR, PADDING_COLOR, [self._ui]),
            False,
            1,
            [1, 2, 3, 4, 6],
        )

    def on_set_level(self, level: Level) -> None:
        self._player = self.current_level.get_sprites_by_tag("player")[0]
        self._goal = self.current_level.get_sprites_by_tag("goal")
        self._wood_inventory = 0
        self._wood_capacity = level.get_data("wood_capacity")
        self._step_limit = level.get_data("step_limit")
        self._steps = 0
        self._bridges_built = 0
        self._ui.update(self._wood_inventory, self._wood_capacity, self._bridges_built)

    def _check_goal(self) -> None:
        for g in self._goal:
            if self._player.x == g.x and self._player.y == g.y:
                self.next_level()
                return

    def _drop_wood(self) -> None:
        sprite = self.current_level.get_sprite_at(
            self._player.x, self._player.y, ignore_collidable=True
        )
        if sprite and "water" in sprite.tags and self._wood_inventory > 0:
            sprite.color_remap(10, 14)
            sprite.tags.remove("water")
            sprite.tags.append("bridge")
            self._wood_inventory -= 1
            self._bridges_built += 1
            self._ui.update(
                self._wood_inventory, self._wood_capacity, self._bridges_built
            )

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
        elif self.action.id.value == 6:
            self._drop_wood()
            self.complete_action()
            return

        new_x = self._player.x + dx
        new_y = self._player.y + dy

        grid_w, grid_h = self.current_level.grid_size
        if not (0 <= new_x < grid_w and 0 <= new_y < grid_h):
            self.complete_action()
            return

        sprite = self.current_level.get_sprite_at(new_x, new_y, ignore_collidable=True)

        if sprite and "bridge" in sprite.tags:
            self._player.set_position(new_x, new_y)
            self._check_goal()
            self.complete_action()
            return

        if sprite and "water" in sprite.tags:
            if self._wood_inventory > 0:
                sprite.color_remap(10, 14)
                sprite.tags.remove("water")
                sprite.tags.append("bridge")
                self._wood_inventory -= 1
                self._bridges_built += 1
                self._ui.update(
                    self._wood_inventory, self._wood_capacity, self._bridges_built
                )
                self._player.set_position(new_x, new_y)
                self._check_goal()
            else:
                self._player.set_position(new_x, new_y)
                self.lose()
                self.complete_action()
                return
            self.complete_action()
            return

        if sprite and "wood" in sprite.tags:
            if self._wood_inventory < self._wood_capacity:
                self.current_level.remove_sprite(sprite)
                self._wood_inventory += 1
                self._ui.update(
                    self._wood_inventory, self._wood_capacity, self._bridges_built
                )
            self._player.set_position(new_x, new_y)
            self._check_goal()
            self.complete_action()
            return

        if not sprite or not sprite.is_collidable:
            self._player.set_position(new_x, new_y)
            self._check_goal()

        self._steps += 1
        if self._steps >= self._step_limit:
            self.lose()

        self.complete_action()
