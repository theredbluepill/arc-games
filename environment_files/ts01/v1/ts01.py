import random

from arcengine import (
    ARCBaseGame,
    Camera,
    Level,
    RenderableUserDisplay,
    Sprite,
)


class Ts01UI(RenderableUserDisplay):
    def __init__(
        self, targets_remaining: int, bomb_countdown: int, has_bomb: bool
    ) -> None:
        self._targets = targets_remaining
        self._countdown = bomb_countdown
        self._has_bomb = has_bomb

    def update(
        self, targets_remaining: int, bomb_countdown: int, has_bomb: bool
    ) -> None:
        self._targets = targets_remaining
        self._countdown = bomb_countdown
        self._has_bomb = has_bomb

    def render_interface(self, frame):
        import numpy as np

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape

        if self._has_bomb:
            color = 8 if self._countdown <= 3 else 11
            for dy in range(2):
                for dx in range(2):
                    frame[1 + dy, w - 4 + dx] = color

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
        pixels=[[13]],
        name="hazard",
        visible=True,
        collidable=True,
        tags=["hazard"],
    ),
    "bomb": Sprite(
        pixels=[[8]],
        name="bomb",
        visible=True,
        collidable=False,
        tags=["bomb"],
    ),
}


def create_level(level_num: int):
    levels_data = {
        1: {
            "grid_size": (8, 8),
            "targets": [(2, 2), (5, 2), (2, 5), (5, 5), (3, 3)],
            "walls": [(1, 1), (4, 3), (3, 4), (6, 6)],
            "hazards": [(7, 0), (0, 7)],
            "player_start": (0, 0),
            "bomb_countdown": 15,
            "bombs_to_spawn": 1,
            "targets_before_bomb": 2,
        },
        2: {
            "grid_size": (10, 10),
            "targets": [(3, 3), (7, 3), (5, 5), (3, 7), (7, 7), (9, 1)],
            "walls": [(2, 2), (4, 4), (6, 6), (8, 2), (2, 8)],
            "hazards": [(9, 9), (0, 5), (5, 0)],
            "player_start": (0, 0),
            "bomb_countdown": 12,
            "bombs_to_spawn": 1,
            "targets_before_bomb": 2,
        },
        3: {
            "grid_size": (12, 12),
            "targets": [(3, 3), (9, 3), (6, 6), (3, 9), (9, 9), (1, 6), (6, 1)],
            "walls": [(2, 2), (4, 4), (8, 8), (10, 4), (4, 10)],
            "hazards": [(11, 11), (0, 0), (7, 5), (5, 7)],
            "player_start": (0, 0),
            "bomb_countdown": 10,
            "bombs_to_spawn": 2,
            "targets_before_bomb": 2,
        },
        4: {
            "grid_size": (14, 14),
            "targets": [
                (3, 3),
                (10, 3),
                (7, 7),
                (3, 10),
                (10, 10),
                (5, 5),
                (9, 5),
                (5, 9),
            ],
            "walls": [(2, 2), (4, 4), (6, 6), (8, 8), (10, 10), (12, 4), (4, 12)],
            "hazards": [(13, 13), (0, 0), (13, 0), (0, 13)],
            "player_start": (0, 7),
            "bomb_countdown": 8,
            "bombs_to_spawn": 2,
            "targets_before_bomb": 2,
        },
        5: {
            "grid_size": (16, 16),
            "targets": [
                (3, 3),
                (12, 3),
                (7, 7),
                (3, 12),
                (12, 12),
                (7, 3),
                (3, 7),
                (12, 7),
                (7, 12),
                (15, 15),
            ],
            "walls": [(5, 5), (10, 10), (5, 10), (10, 5)],
            "hazards": [(15, 0), (0, 15), (7, 0), (0, 7)],
            "player_start": (0, 0),
            "bomb_countdown": 8,
            "bombs_to_spawn": 3,
            "targets_before_bomb": 2,
        },
    }

    data = levels_data[level_num]
    level_sprites = [sprites["player"].clone().set_position(*data["player_start"])]

    for pos in data["targets"]:
        level_sprites.append(sprites["target"].clone().set_position(*pos))

    for pos in data["walls"]:
        level_sprites.append(sprites["wall"].clone().set_position(*pos))

    for pos in data["hazards"]:
        level_sprites.append(sprites["hazard"].clone().set_position(*pos))

    return Level(
        sprites=level_sprites,
        grid_size=data["grid_size"],
        data={
            "bomb_countdown_init": data["bomb_countdown"],
            "bombs_to_spawn": data["bombs_to_spawn"],
            "targets_before_bomb": data["targets_before_bomb"],
        },
    )


levels = [create_level(i) for i in range(1, 6)]

BACKGROUND_COLOR = 5
PADDING_COLOR = 4


class Ts01(ARCBaseGame):
    def __init__(self) -> None:
        self._ui = Ts01UI(0, 0, False)
        super().__init__(
            "ts01",
            levels,
            Camera(0, 0, 16, 16, BACKGROUND_COLOR, PADDING_COLOR, [self._ui]),
            False,
            1,
            [1, 2, 3, 4, 5],
        )

    def on_set_level(self, level: Level) -> None:
        self._player = self.current_level.get_sprites_by_tag("player")[0]
        self._targets = self.current_level.get_sprites_by_tag("target")
        self._bomb_sprite = None
        self._bomb_countdown = 0
        self._bomb_countdown_init = level.get_data("bomb_countdown_init")
        self._bombs_to_spawn = level.get_data("bombs_to_spawn")
        self._bombs_defused = 0
        self._targets_before_bomb = level.get_data("targets_before_bomb")
        self._targets_collected_since_last_bomb = 0
        self._total_targets_collected = 0
        self._total_targets = len(self._targets)
        self._ui.update(len(self._targets), 0, False)

    def _spawn_bomb(self) -> None:
        if self._bomb_sprite:
            return
        if self._bombs_defused >= self._bombs_to_spawn:
            return

        grid_w, grid_h = self.current_level.grid_size
        empty = []
        for y in range(grid_h):
            for x in range(grid_w):
                sprite = self.current_level.get_sprite_at(x, y, ignore_collidable=True)
                if sprite is None:
                    empty.append((x, y))
                elif sprite == self._player:
                    pass
                else:
                    sprite_at_pos = self.current_level.get_sprite_at(x, y)
                    if sprite_at_pos is None or sprite_at_pos == self._player:
                        empty.append((x, y))

        valid_empty = []
        for x, y in empty:
            sprite = self.current_level.get_sprite_at(x, y, ignore_collidable=True)
            if sprite is None:
                valid_empty.append((x, y))

        if not valid_empty:
            return

        x, y = random.choice(valid_empty)
        bomb = sprites["bomb"].clone().set_position(x, y)
        self.current_level.add_sprite(bomb)
        self._bomb_sprite = bomb
        self._bomb_countdown = self._bomb_countdown_init
        self._ui.update(len(self._targets), self._bomb_countdown, True)

    def _check_spawn_bomb(self) -> None:
        if self._bomb_sprite:
            return
        if self._bombs_defused >= self._bombs_to_spawn:
            return
        if self._total_targets_collected >= self._total_targets:
            return

        self._total_targets_collected += 1
        self._targets_collected_since_last_bomb += 1

        if self._targets_collected_since_last_bomb >= self._targets_before_bomb:
            self._targets_collected_since_last_bomb = 0
            self._spawn_bomb()

    def _defuse_bomb(self) -> None:
        if not self._bomb_sprite:
            return

        px, py = self._player.x, self._player.y
        bx, by = self._bomb_sprite.x, self._bomb_sprite.y

        if abs(px - bx) + abs(py - by) == 1:
            self.current_level.remove_sprite(self._bomb_sprite)
            self._bomb_sprite = None
            self._bombs_defused += 1
            self._ui.update(len(self._targets), 0, False)

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
        elif self.action.id.value == 5:
            self._defuse_bomb()
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

        if sprite and "hazard" in sprite.tags:
            self.lose()
            self.complete_action()
            return

        if sprite and "target" in sprite.tags:
            self.current_level.remove_sprite(sprite)
            self._targets.remove(sprite)
            self._player.set_position(new_x, new_y)
            self._check_spawn_bomb()
        elif not sprite or not sprite.is_collidable:
            self._player.set_position(new_x, new_y)

        if self._bomb_sprite:
            self._bomb_countdown -= 1
            self._ui.update(len(self._targets), self._bomb_countdown, True)
            if self._bomb_countdown <= 0:
                self.lose()
                self.complete_action()
                return

        if len(self._targets) == 0 and not self._bomb_sprite:
            self.next_level()

        self.complete_action()
