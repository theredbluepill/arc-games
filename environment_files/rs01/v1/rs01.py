from arcengine import (
    ARCBaseGame,
    Camera,
    Level,
    RenderableUserDisplay,
    Sprite,
)


class Rs01UI(RenderableUserDisplay):
    def __init__(self, safe_color: int) -> None:
        self._safe_color = safe_color

    def update(self, safe_color: int) -> None:
        self._safe_color = safe_color

    def render_interface(self, frame):
        import numpy as np

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape
        for x in range(w):
            frame[0, x] = self._safe_color
        return frame


sprites = {
    "player": Sprite(
        pixels=[[9]],
        name="player",
        visible=True,
        collidable=True,
        tags=["player"],
    ),
    "wall": Sprite(
        pixels=[[3]],
        name="wall",
        visible=True,
        collidable=True,
        tags=["wall"],
    ),
    8: Sprite(
        pixels=[[8]],
        name="target_red",
        visible=True,
        collidable=False,
        tags=["target"],
    ),
    11: Sprite(
        pixels=[[11]],
        name="target_yellow",
        visible=True,
        collidable=False,
        tags=["target"],
    ),
    14: Sprite(
        pixels=[[14]],
        name="target_green",
        visible=True,
        collidable=False,
        tags=["target"],
    ),
    15: Sprite(
        pixels=[[15]],
        name="target_purple",
        visible=True,
        collidable=False,
        tags=["target"],
    ),
}


def make_signpost_level(
    grid_size,
    player_pos,
    target_positions_colors,
    wall_coords,
    safe_colors,
    cycle_interval,
    difficulty,
):
    sprite_list = [
        sprites["player"].clone().set_position(*player_pos),
    ]
    for pos, color in target_positions_colors:
        sprite_list.append(sprites[color].clone().set_position(*pos))
    for wp in wall_coords:
        sprite_list.append(sprites["wall"].clone().set_position(*wp))
    return Level(
        sprites=sprite_list,
        grid_size=grid_size,
        data={
            "safe_colors": safe_colors,
            "cycle_interval": cycle_interval,
            "difficulty": difficulty,
        },
    )


levels = [
    make_signpost_level(
        (8, 8),
        (1, 1),
        [((3, 3), 8), ((5, 5), 8), ((3, 5), 14), ((5, 3), 14)],
        [],
        [8, 14],
        15,
        1,
    ),
    make_signpost_level(
        (8, 8),
        (1, 1),
        [
            ((3, 3), 8),
            ((5, 5), 8),
            ((3, 5), 14),
            ((5, 3), 14),
            ((2, 4), 11),
            ((4, 2), 11),
        ],
        [],
        [8, 14, 11],
        12,
        2,
    ),
    make_signpost_level(
        (12, 12),
        (2, 2),
        [
            ((5, 5), 8),
            ((7, 7), 8),
            ((9, 5), 8),
            ((5, 9), 14),
            ((7, 5), 14),
            ((9, 7), 14),
            ((3, 6), 11),
            ((6, 3), 11),
            ((10, 10), 11),
        ],
        [],
        [8, 14, 11],
        10,
        3,
    ),
    make_signpost_level(
        (16, 16),
        (2, 2),
        [
            ((5, 5), 8),
            ((10, 10), 8),
            ((7, 7), 14),
            ((12, 12), 14),
            ((5, 10), 11),
            ((10, 5), 11),
            ((7, 13), 15),
            ((13, 7), 15),
        ],
        [(4, 4), (6, 4), (4, 6), (8, 8), (9, 8), (8, 9), (11, 11)],
        [8, 14, 11, 15],
        10,
        4,
    ),
    make_signpost_level(
        (16, 16),
        (2, 2),
        [
            ((5, 5), 8),
            ((7, 7), 8),
            ((10, 10), 8),
            ((6, 6), 14),
            ((8, 8), 14),
            ((11, 11), 14),
            ((5, 11), 11),
            ((11, 5), 11),
            ((7, 12), 11),
            ((12, 7), 15),
            ((13, 8), 15),
            ((8, 13), 15),
        ],
        [
            (4, 4),
            (5, 4),
            (6, 5),
            (7, 6),
            (8, 7),
            (9, 8),
            (10, 9),
            (11, 10),
            (4, 10),
            (10, 4),
        ],
        [8, 14, 11, 15],
        8,
        5,
    ),
]

BACKGROUND_COLOR = 5
PADDING_COLOR = 4


class Rs01(ARCBaseGame):
    """Rule Switcher - Collect colored targets. A signpost shows which color is currently SAFE."""

    def __init__(self) -> None:
        self._ui = Rs01UI(8)
        super().__init__(
            "rs01",
            levels,
            Camera(0, 0, 16, 16, BACKGROUND_COLOR, PADDING_COLOR, [self._ui]),
            False,
            1,
            [1, 2, 3, 4],
        )

    def on_set_level(self, level: Level) -> None:
        self._player = self.current_level.get_sprites_by_tag("player")[0]
        self._targets = list(self.current_level.get_sprites_by_tag("target"))
        self._safe_colors = level.get_data("safe_colors")
        self._cycle_interval = level.get_data("cycle_interval")
        self._cycle_index = 0
        self._safe_color = self._safe_colors[0]
        self._all_cycled = False
        self._steps = 0
        self._ui.update(self._safe_color)

    def _cycle_signpost(self) -> None:
        self._cycle_index = (self._cycle_index + 1) % len(self._safe_colors)
        self._safe_color = self._safe_colors[self._cycle_index]
        if self._cycle_index == 0:
            self._all_cycled = True

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

        if sprite and "target" in sprite.tags:
            target_color = sprite.pixels[0][0]
            if target_color == self._safe_color:
                self.current_level.remove_sprite(sprite)
                self._targets.remove(sprite)
                self._player.set_position(new_x, new_y)
            elif self._all_cycled:
                self.current_level.remove_sprite(sprite)
                self._targets.remove(sprite)
                self._player.set_position(new_x, new_y)
            else:
                self.lose()
        elif not sprite or not sprite.is_collidable:
            self._player.set_position(new_x, new_y)

        self._steps += 1
        if self._steps % self._cycle_interval == 0:
            self._cycle_signpost()
            self._ui.update(self._safe_color)

        if len(self._targets) == 0:
            self.next_level()

        self.complete_action()
