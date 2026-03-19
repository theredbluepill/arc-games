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

SEQUENCE_COLORS = {
    "red": 8,
    "blue": 9,
    "green": 14,
    "yellow": 11,
    "orange": 12,
    "purple": 15,
    "cyan": 10,
    "magenta": 6,
}


class Sq01UI(RenderableUserDisplay):
    def __init__(self, sequence: list, progress: int) -> None:
        self._sequence = sequence
        self._progress = progress
        self._click_pos = None
        self._click_frames = 0
        self._game_over = False
        self._win = False

    def update(self, sequence: list, progress: int) -> None:
        self._sequence = sequence
        self._progress = progress

    def set_game_over(self, win: bool) -> None:
        self._game_over = True
        self._win = win

    def set_click(self, x: int, y: int) -> None:
        self._click_pos = (x, y)
        self._click_frames = 5

    def render_interface(self, frame):
        import numpy as np

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape

        if self._click_pos and self._click_frames > 0:
            cx, cy = self._click_pos
            if 0 <= cx < w and 0 <= cy < h:
                frame[cy, cx] = 8
            self._click_frames -= 1
        else:
            self._click_pos = None

        if self._game_over:
            row = 1
            for i, color_name in enumerate(self._sequence):
                color = SEQUENCE_COLORS.get(color_name, 11)
                for dy in range(2):
                    for dx in range(2):
                        px = i * 3 + dx
                        py = row + dy
                        if 0 <= px < w and 0 <= py < h:
                            if self._win:
                                frame[py, px] = 14
                            else:
                                frame[py, px] = 8
            return frame

        row = 1
        for i, color_name in enumerate(self._sequence):
            color = SEQUENCE_COLORS.get(color_name, 11)
            is_current = i == self._progress
            for dy in range(2):
                for dx in range(2):
                    px = i * 3 + dx
                    py = row + dy
                    if 0 <= px < w and 0 <= py < h:
                        if is_current:
                            frame[py, px] = 0
                        else:
                            frame[py, px] = 3

        for i, color_name in enumerate(self._sequence[: self._progress]):
            color = SEQUENCE_COLORS.get(color_name, 11)
            for dy in range(2):
                for dx in range(2):
                    px = i * 3 + dx
                    py = row + dy
                    if 0 <= px < w and 0 <= py < h:
                        frame[py, px] = color

        return frame


sprites = {
    color: Sprite(
        pixels=[[color_val, color_val], [color_val, color_val]],
        name=f"{color}_block",
        visible=True,
        collidable=False,
        tags=["sequence_item", f"color_{color}"],
    )
    for color, color_val in SEQUENCE_COLORS.items()
}


def make_sequence_level(
    grid_size: tuple,
    sequence: list,
    block_positions: dict,
    difficulty: int,
):
    sprite_list = []
    for color_name in sequence:
        pos = block_positions.get(color_name)
        if pos and color_name in sprites:
            sprite = sprites[color_name].clone().set_position(pos[0], pos[1])
            sprite_list.append(sprite)

    step_limit = 20 + len(sequence) * 10

    return Level(
        sprites=sprite_list,
        grid_size=grid_size,
        data={
            "sequence": sequence,
            "block_positions": block_positions,
            "difficulty": difficulty,
            "step_limit": step_limit,
        },
        name=f"Level {difficulty}",
    )


levels = [
    make_sequence_level(
        (8, 8),
        ["red", "blue", "green"],
        {
            "red": (1, 3),
            "blue": (5, 2),
            "green": (3, 5),
        },
        1,
    ),
    make_sequence_level(
        (8, 8),
        ["red", "blue", "green", "yellow"],
        {
            "red": (1, 2),
            "blue": (6, 3),
            "green": (3, 5),
            "yellow": (5, 6),
        },
        2,
    ),
    make_sequence_level(
        (8, 8),
        ["red", "blue", "green", "yellow", "purple"],
        {
            "red": (1, 1),
            "blue": (6, 2),
            "green": (3, 4),
            "yellow": (5, 5),
            "purple": (2, 6),
        },
        3,
    ),
    make_sequence_level(
        (8, 8),
        ["red", "blue", "green", "yellow", "purple", "cyan"],
        {
            "red": (1, 1),
            "blue": (6, 2),
            "green": (3, 3),
            "yellow": (5, 4),
            "purple": (2, 5),
            "cyan": (6, 6),
        },
        4,
    ),
    make_sequence_level(
        (8, 8),
        ["red", "blue", "green", "yellow", "purple", "cyan", "orange"],
        {
            "red": (1, 1),
            "blue": (6, 1),
            "green": (2, 3),
            "yellow": (5, 3),
            "purple": (1, 5),
            "cyan": (6, 5),
            "orange": (3, 6),
        },
        5,
    ),
]


class Sq01(ARCBaseGame):
    def __init__(self) -> None:
        self._ui = Sq01UI([], 0)
        super().__init__(
            "sq01",
            levels,
            Camera(0, 0, 8, 8, BACKGROUND_COLOR, PADDING_COLOR, [self._ui]),
            False,
            1,
            [6],
        )

    def on_set_level(self, level: Level) -> None:
        self._sequence = level.get_data("sequence")
        self._block_positions = level.get_data("block_positions")
        self._step_limit = level.get_data("step_limit")
        self._steps = 0
        self._progress = 0
        self._game_over = False
        self._ui.update(self._sequence, self._progress)
        self._color_to_sprite = {}
        for sprite in self.current_level.get_sprites_by_tag("sequence_item"):
            for tag in sprite.tags:
                if tag.startswith("color_"):
                    color_name = tag.replace("color_", "")
                    self._color_to_sprite[color_name] = sprite
                    break

    def step(self) -> None:
        if self._game_over:
            self.complete_action()
            return

        if self.action.id.value == 6:
            x = self.action.data.get("x", 0)
            y = self.action.data.get("y", 0)

            self._ui.set_click(x, y)

            clicked_sprite = None
            for color_name, sprite in self._color_to_sprite.items():
                sx, sy = sprite.x, sprite.y
                if sx <= x < sx + 2 and sy <= y < sy + 2:
                    clicked_sprite = sprite
                    break

            if clicked_sprite:
                expected_color = self._sequence[self._progress]
                for tag in clicked_sprite.tags:
                    if tag.startswith("color_"):
                        clicked_color = tag.replace("color_", "")
                        break

                if clicked_color == expected_color:
                    self.current_level.remove_sprite(clicked_sprite)
                    del self._color_to_sprite[clicked_color]
                    self._progress += 1
                    self._ui.update(self._sequence, self._progress)

                    if self._progress >= len(self._sequence):
                        self._game_over = True
                        self._ui.set_game_over(True)
                        self.next_level()
                else:
                    self._game_over = True
                    self._ui.set_game_over(False)
                    self.lose()
            else:
                self._game_over = True
                self._ui.set_game_over(False)
                self.lose()

        self._steps += 1
        if not self._game_over and self._steps >= self._step_limit:
            self._game_over = True
            self._ui.set_game_over(False)
            self.lose()

        self.complete_action()
