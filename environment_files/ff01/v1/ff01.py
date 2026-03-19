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

BACKGROUND_COLOR = 5
PADDING_COLOR = 4
FILL_COLOR = 11
WRONG_COLOR = 8


class Ff01UI(RenderableUserDisplay):
    def __init__(self, attempts: int, filled: bool) -> None:
        self._attempts = attempts
        self._filled = filled
        self._click_pos = None
        self._click_frames = 0
        self._game_over = False
        self._win = False

    def update(
        self, attempts: int, filled: bool, game_over: bool = False, win: bool = False
    ) -> None:
        self._attempts = attempts
        self._filled = filled
        self._game_over = game_over
        self._win = win

    def set_click(self, x: int, y: int) -> None:
        self._click_pos = (x, y)
        self._click_frames = 8

    def render_interface(self, frame):
        import numpy as np

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape

        if self._click_pos and self._click_frames > 0:
            cx, cy = self._click_pos
            if 0 <= cx < w and 0 <= cy < h:
                for ox, oy in [
                    (0, -2),
                    (0, 2),
                    (-2, 0),
                    (2, 0),
                    (0, -1),
                    (0, 1),
                    (-1, 0),
                    (1, 0),
                ]:
                    px, py = cx + ox, cy + oy
                    if 0 <= px < w and 0 <= py < h:
                        frame[py, px] = 14
                frame[cy, cx] = 8
            self._click_frames -= 1
        else:
            self._click_pos = None

        if self._game_over:
            if self._win:
                frame[2, 2] = 14
                frame[2, 3] = 14
                frame[2, 4] = 14
            else:
                frame[2, 2] = 8
                frame[2, 3] = 8
                frame[2, 4] = 8
        else:
            for i in range(3):
                if i < self._attempts:
                    frame[2, 2 + i] = 11
                else:
                    frame[2, 2 + i] = 3

        return frame


class Ff01(ARCBaseGame):
    def __init__(self) -> None:
        self._ui = Ff01UI(3, False)
        super().__init__(
            "ff01",
            levels,
            Camera(0, 0, 12, 12, BACKGROUND_COLOR, PADDING_COLOR, [self._ui]),
            False,
            1,
            [6],
        )

    def on_set_level(self, level: Level) -> None:
        self._interior_cells = self.current_level.get_data("interior_cells")
        self._attempts = self.current_level.get_data("attempts")
        self._filled = False
        self._game_over = False
        self._outline_sprites = self.current_level.get_sprites_by_tag("outline")
        self._outline_positions = set()
        for s in self._outline_sprites:
            self._outline_positions.add((s.x, s.y))
        self._update_ui()

    def _update_ui(self) -> None:
        self._ui.update(
            self._attempts,
            self._filled,
            self._game_over,
            hasattr(self, "_win") and self._win,
        )

    def _is_inside_shape(self, x: int, y: int) -> bool:
        return (x, y) in self._interior_cells

    def _fill_area(self, cells: list, color: int) -> None:
        fill_sprite = Sprite(
            pixels=[[color]],
            name=f"fill_{len(self.current_level._sprites)}",
            visible=True,
            collidable=False,
            tags=["fill"],
        )
        for cx, cy in cells:
            cell_sprite = fill_sprite.clone().set_position(cx, cy)
            self.current_level.add_sprite(cell_sprite)

    def step(self) -> None:
        if self._game_over:
            self.complete_action()
            return

        if self.action.id.value == 6:
            x = self.action.data.get("x", 0)
            y = self.action.data.get("y", 0)

            grid_x = x // 5
            grid_y = y // 5

            self._ui.set_click(x, y)

            if self._is_inside_shape(grid_x, grid_y):
                self._fill_area(self._interior_cells, FILL_COLOR)
                self._filled = True
                self._game_over = True
                self._win = True
                self.next_level()
            else:
                self._attempts -= 1
                if self._attempts <= 0:
                    self._game_over = True
                    self._win = False
                    all_cells = [(x, y) for x in range(12) for y in range(12)]
                    outside = [c for c in all_cells if c not in self._interior_cells]
                    self._fill_area(outside, WRONG_COLOR)

            self._update_ui()

        self.complete_action()


WALL = Sprite(
    pixels=[[3]],
    name="wall",
    visible=True,
    collidable=True,
    tags=["outline"],
)


def make_square_outline(x: int, y: int, size: int):
    sprites_list = []
    for i in range(size):
        sprites_list.append(WALL.clone().set_position(x + i, y))
        sprites_list.append(WALL.clone().set_position(x + i, y + size - 1))
        if i > 0 and i < size - 1:
            sprites_list.append(WALL.clone().set_position(x, y + i))
            sprites_list.append(WALL.clone().set_position(x + size - 1, y + i))
    return sprites_list


def make_interior(x: int, y: int, size: int):
    return [(x + i, y + j) for i in range(1, size - 1) for j in range(1, size - 1)]


def make_l_shape():
    sprites_list = []
    positions = []
    for x in range(3, 9):
        sprites_list.append(WALL.clone().set_position(x, 3))
        positions.append((x, 3))
        sprites_list.append(WALL.clone().set_position(x, 8))
        positions.append((x, 8))
    for y in range(3, 9):
        sprites_list.append(WALL.clone().set_position(3, y))
        positions.append((3, y))
        if y < 6:
            sprites_list.append(WALL.clone().set_position(8, y))
            positions.append((8, y))
    for x in range(3, 6):
        sprites_list.append(WALL.clone().set_position(x, 5))
        positions.append((x, 5))
    return sprites_list, positions


def make_t_shape():
    sprites_list = []
    positions = []
    for x in range(2, 10):
        sprites_list.append(WALL.clone().set_position(x, 2))
        positions.append((x, 2))
        sprites_list.append(WALL.clone().set_position(x, 7))
        positions.append((x, 7))
    for y in range(2, 8):
        sprites_list.append(WALL.clone().set_position(5, y))
        positions.append((5, y))
        sprites_list.append(WALL.clone().set_position(6, y))
        positions.append((6, y))
    return sprites_list, positions


def make_cross_shape():
    sprites_list = []
    positions = []
    for x in range(3, 9):
        sprites_list.append(WALL.clone().set_position(x, 5))
        positions.append((x, 5))
        sprites_list.append(WALL.clone().set_position(x, 6))
        positions.append((x, 6))
    for y in range(3, 9):
        sprites_list.append(WALL.clone().set_position(5, y))
        positions.append((5, y))
        sprites_list.append(WALL.clone().set_position(6, y))
        positions.append((6, y))
    return sprites_list, positions


def make_z_shape():
    sprites_list = []
    positions = []
    for x in range(2, 10):
        sprites_list.append(WALL.clone().set_position(x, 2))
        positions.append((x, 2))
        sprites_list.append(WALL.clone().set_position(x, 9))
        positions.append((x, 9))
    for y in range(2, 10):
        sprites_list.append(WALL.clone().set_position(2, y))
        positions.append((2, y))
        sprites_list.append(WALL.clone().set_position(9, y))
        positions.append((9, y))
    return sprites_list, positions


level1_sprites = make_square_outline(4, 4, 4)
level1_interior = make_interior(4, 4, 4)

level2_sprites = make_square_outline(3, 3, 6)
level2_interior = make_interior(3, 3, 6)

level3_sprites, level3_positions = make_l_shape()
level3_interior = [(x, y) for x in range(4, 8) for y in range(4, 5)]

level4_sprites, level4_positions = make_t_shape()
level4_interior = [(x, y) for x in range(5, 7) for y in range(3, 7)]

level5_sprites, level5_positions = make_cross_shape()
level5_interior = [(x, y) for x in range(5, 7) for y in range(5, 7)]

levels = [
    Level(
        sprites=level1_sprites,
        grid_size=(12, 12),
        data={
            "interior_cells": level1_interior,
            "attempts": 3,
        },
        name="Level 1",
    ),
    Level(
        sprites=level2_sprites,
        grid_size=(12, 12),
        data={
            "interior_cells": level2_interior,
            "attempts": 3,
        },
        name="Level 2",
    ),
    Level(
        sprites=level3_sprites,
        grid_size=(12, 12),
        data={
            "interior_cells": [
                (4, 4),
                (5, 4),
                (6, 4),
                (7, 4),
                (4, 5),
                (5, 5),
                (6, 5),
                (7, 5),
                (4, 6),
                (5, 6),
                (6, 6),
                (7, 6),
            ],
            "attempts": 3,
        },
        name="Level 3",
    ),
    Level(
        sprites=level4_sprites,
        grid_size=(12, 12),
        data={
            "interior_cells": level4_interior,
            "attempts": 3,
        },
        name="Level 4",
    ),
    Level(
        sprites=level5_sprites,
        grid_size=(12, 12),
        data={
            "interior_cells": level5_interior,
            "attempts": 3,
        },
        name="Level 5",
    ),
]
