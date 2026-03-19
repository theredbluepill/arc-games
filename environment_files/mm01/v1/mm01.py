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
HIDDEN_COLOR = 4

COLORS = [8, 9, 11, 12, 14, 15, 10, 6]

TILE_SIZE = 2
GRID_OFFSET_X = 2
GRID_OFFSET_Y = 2


def make_tile_sprite(color: int, name: str, tags: list) -> Sprite:
    pixels = [[color] * TILE_SIZE for _ in range(TILE_SIZE)]
    return Sprite(
        pixels=pixels,
        name=name,
        visible=True,
        collidable=False,
        tags=tags,
    )


def make_hidden_sprite(slot_index: int) -> Sprite:
    pixels = [[HIDDEN_COLOR] * TILE_SIZE for _ in range(TILE_SIZE)]
    return Sprite(
        pixels=pixels,
        name=f"hidden_{slot_index}",
        visible=True,
        collidable=False,
        tags=["hidden", f"slot_{slot_index}"],
    )


class Mm01UI(RenderableUserDisplay):
    def __init__(self, pairs_remaining: int, mismatches: int) -> None:
        self._pairs_remaining = pairs_remaining
        self._mismatches = mismatches
        self._max_mismatches = 5
        self._click_pos = None
        self._click_frames = 0

    def update(self, pairs_remaining: int, mismatches: int) -> None:
        self._pairs_remaining = pairs_remaining
        self._mismatches = mismatches

    def set_click(self, x: int, y: int) -> None:
        self._click_pos = (x, y)
        self._click_frames = 5

    def render_interface(self, frame):
        if self._click_frames > 0:
            self._click_frames -= 1
        return frame


def create_level(seed: int) -> Level:
    import random

    rng = random.Random(seed)

    slot_colors = []
    for color in COLORS:
        slot_colors.append(color)
        slot_colors.append(color)

    rng.shuffle(slot_colors)

    sprites = []
    for i in range(16):
        row = i // 4
        col = i % 4
        x = GRID_OFFSET_X + col * TILE_SIZE
        y = GRID_OFFSET_Y + row * TILE_SIZE

        hidden = make_hidden_sprite(i)
        hidden.set_position(x, y)
        sprites.append(hidden)

    return Level(
        sprites=sprites,
        grid_size=(8, 8),
        data={
            "slot_colors": slot_colors,
            "seed": seed,
        },
        name=f"Level {seed}",
    )


class Mm01(ARCBaseGame):
    def __init__(self) -> None:
        self._ui = Mm01UI(8, 0)
        super().__init__(
            "mm01",
            levels,
            Camera(0, 0, 8, 8, BACKGROUND_COLOR, PADDING_COLOR, [self._ui]),
            False,
            1,
            [6],
        )

    def _generate_levels(self, seed: int) -> list:
        levels = []
        for i in range(5):
            levels.append(create_level(seed + i))
        return levels

    def on_set_level(self, level: Level) -> None:
        self._slot_colors = level.get_data("slot_colors")
        self._slots = [[None for _ in range(4)] for _ in range(4)]
        self._matched = [False] * 16
        self._flipped = []
        self._pairs_remaining = 8
        self._mismatches = 0
        self._waiting_for_flip_back = False
        self._flip_back_timer = 0

        for sprite in self.current_level.get_sprites_by_tag("hidden"):
            for tag in sprite.tags:
                if tag.startswith("slot_"):
                    slot_idx = int(tag.split("_")[1])
                    row = slot_idx // 4
                    col = slot_idx % 4
                    self._slots[row][col] = sprite

        self._ui.update(self._pairs_remaining, self._mismatches)

    def _get_slot_from_click(self, click_x: int, click_y: int):
        col = (click_x - GRID_OFFSET_X) // TILE_SIZE
        row = (click_y - GRID_OFFSET_Y) // TILE_SIZE

        if 0 <= row < 4 and 0 <= col < 4:
            return row, col
        return None, None

    def _flip_slot(self, row: int, col: int) -> bool:
        slot_idx = row * 4 + col
        if self._matched[slot_idx]:
            return False

        for tile in self._flipped:
            if tile[0] == row and tile[1] == col:
                return False

        return True

    def _get_tile_color(self, slot_idx: int) -> int:
        return self._slot_colors[slot_idx]

    def _create_revealed_sprite(self, color: int, slot_idx: int) -> Sprite:
        pixels = [[color] * TILE_SIZE for _ in range(TILE_SIZE)]
        return Sprite(
            pixels=pixels,
            name=f"revealed_{slot_idx}",
            visible=True,
            collidable=False,
            tags=["revealed", f"slot_{slot_idx}"],
        )

    def step(self) -> None:
        if self._waiting_for_flip_back:
            self._flip_back_timer -= 1
            if self._flip_back_timer <= 0:
                self._do_flip_back()
                self._waiting_for_flip_back = False
            self.complete_action()
            return

        if self.action.id.value == 6:
            x = self.action.data.get("x", 0)
            y = self.action.data.get("y", 0)
            self._ui.set_click(x, y)

            row, col = self._get_slot_from_click(x, y)
            if row is None:
                self.complete_action()
                return

            slot_idx = row * 4 + col

            if self._matched[slot_idx]:
                self.complete_action()
                return

            if not self._flip_slot(row, col):
                self.complete_action()
                return

            color = self._get_tile_color(slot_idx)
            sprite = self._slots[row][col]

            revealed = self._create_revealed_sprite(color, slot_idx)
            revealed.set_position(sprite.x, sprite.y)
            self.current_level.add_sprite(revealed)
            sprite.visible = False

            self._flipped.append((row, col, slot_idx, color))

            if len(self._flipped) == 2:
                first = self._flipped[0]
                second = self._flipped[1]

                if first[3] == second[3]:
                    self._matched[first[2]] = True
                    self._matched[second[2]] = True
                    self._pairs_remaining -= 1
                    self._flipped = []
                    self._ui.update(self._pairs_remaining, self._mismatches)

                    if self._pairs_remaining == 0:
                        self.next_level()
                else:
                    self._mismatches += 1
                    self._ui.update(self._pairs_remaining, self._mismatches)
                    self._waiting_for_flip_back = True
                    self._flip_back_timer = 2

                    if self._mismatches >= 5:
                        self.lose()

        self.complete_action()

    def _do_flip_back(self) -> None:
        for row, col, slot_idx, color in self._flipped:
            sprite = self._slots[row][col]
            sprite.visible = True

            for s in list(self.current_level._sprites):
                if f"slot_{slot_idx}" in s.tags and "revealed" in s.tags:
                    self.current_level.remove_sprite(s)

        self._flipped = []


levels = [
    create_level(0),
    create_level(1),
    create_level(2),
    create_level(3),
    create_level(4),
]
