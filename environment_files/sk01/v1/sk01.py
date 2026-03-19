from arcengine import (
    ARCBaseGame,
    Camera,
    Level,
    RenderableUserDisplay,
    Sprite,
)


class Sk01UI(RenderableUserDisplay):
    def __init__(self, remaining: int) -> None:
        self._remaining = remaining

    def update(self, remaining: int) -> None:
        self._remaining = remaining

    def render_interface(self, frame):
        import numpy as np

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape
        color = 11 if self._remaining == 0 else 14
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
    "block": Sprite(
        pixels=[[15]],
        name="block",
        visible=True,
        collidable=True,
        tags=["block"],
    ),
    "block_done": Sprite(
        pixels=[[14]],
        name="block_done",
        visible=True,
        collidable=True,
        tags=["block", "done"],
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
}


def make_wall_level(
    grid_size, player_pos, block_positions, target_positions, wall_coords, difficulty
):
    sprite_list = [
        sprites["player"].clone().set_position(*player_pos),
    ]
    for bp in block_positions:
        sprite_list.append(sprites["block"].clone().set_position(*bp))
    for tp in target_positions:
        sprite_list.append(sprites["target"].clone().set_position(*tp))
    for wp in wall_coords:
        sprite_list.append(sprites["wall"].clone().set_position(*wp))
    return Level(
        sprites=sprite_list,
        grid_size=grid_size,
        data={"difficulty": difficulty, "step_limit": 50 + difficulty * 20},
    )


levels = [
    make_wall_level(
        (8, 8),
        (1, 1),
        [(3, 3)],
        [(5, 5)],
        [],
        1,
    ),
    make_wall_level(
        (8, 8),
        (0, 0),
        [(3, 2)],
        [(6, 5)],
        [],
        2,
    ),
    make_wall_level(
        (8, 8),
        (1, 1),
        [(3, 3)],
        [(5, 5)],
        [(2, 3), (3, 2), (4, 3), (3, 4)],
        3,
    ),
    make_wall_level(
        (8, 8),
        (0, 0),
        [(2, 2)],
        [(6, 6)],
        [(1, 2), (2, 1), (3, 2), (2, 3), (5, 5)],
        4,
    ),
    make_wall_level(
        (16, 16),
        (1, 1),
        [(4, 4), (6, 8)],
        [(12, 12), (10, 10)],
        [
            (3, 4),
            (4, 3),
            (5, 4),
            (4, 5),
            (5, 8),
            (6, 7),
            (7, 8),
            (6, 9),
            (9, 10),
            (10, 9),
            (11, 10),
            (10, 11),
        ],
        5,
    ),
    make_wall_level(
        (16, 16),
        (0, 0),
        [(3, 3), (7, 5), (11, 7)],
        [(14, 14), (12, 12), (10, 10)],
        [(2, 3), (3, 2), (6, 5), (5, 6), (10, 7), (11, 6)],
        6,
    ),
    make_wall_level(
        (16, 16),
        (7, 7),
        [(5, 5), (9, 5), (7, 3), (7, 9)],
        [(2, 2), (13, 2), (2, 13), (13, 13)],
        [(4, 5), (6, 5), (8, 5), (10, 5), (5, 4), (5, 6), (9, 4), (9, 6)],
        7,
    ),
]

BACKGROUND_COLOR = 5
PADDING_COLOR = 4


class Sk01(ARCBaseGame):
    """Push blocks onto target pads. Color feedback shows blocks on targets."""

    def __init__(self) -> None:
        self._ui = Sk01UI(0)
        super().__init__(
            "sk01",
            levels,
            Camera(0, 0, 16, 16, BACKGROUND_COLOR, PADDING_COLOR, [self._ui]),
            False,
            1,
            [1, 2, 3, 4],
        )

    def on_set_level(self, level: Level) -> None:
        self._player = self.current_level.get_sprites_by_tag("player")[0]
        self._blocks = self.current_level.get_sprites_by_tag("block")
        self._targets = self.current_level.get_sprites_by_tag("target")
        self._step_limit = level.get_data("step_limit")
        self._steps = 0
        self._ui.update(len(self._blocks))

    def _block_on_target(self, block, targets):
        for t in targets:
            if block.x == t.x and block.y == t.y:
                return True
        return False

    def _check_stuck(self, block, targets, blocks):
        if self._block_on_target(block, targets):
            return False
        px, py = block.x, block.y
        is_corner = True
        for other in blocks:
            if other is block:
                continue
            if other.x == px and other.y == py:
                return True
        return False

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

        if sprite and "block" in sprite.tags:
            block_new_x = new_x + dx
            block_new_y = new_y + dy
            if not (0 <= block_new_x < grid_w and 0 <= block_new_y < grid_h):
                self.complete_action()
                return
            block_behind = self.current_level.get_sprite_at(
                block_new_x, block_new_y, ignore_collidable=True
            )
            if block_behind and "block" in block_behind.tags:
                self.complete_action()
                return
            if block_behind and "wall" in block_behind.tags:
                self.complete_action()
                return
            sprite.set_position(block_new_x, block_new_y)
            if self._block_on_target(sprite, self._targets):
                sprite.color_remap(15, 14)
                sprite.tags.append("done")
            self._player.set_position(new_x, new_y)
        elif not sprite or not sprite.is_collidable:
            self._player.set_position(new_x, new_y)

        self._steps += 1
        remaining = sum(1 for b in self._blocks if "done" not in b.tags)
        self._ui.update(remaining)

        if remaining == 0:
            self.next_level()
        elif self._steps >= self._step_limit:
            self.lose()

        self.complete_action()
