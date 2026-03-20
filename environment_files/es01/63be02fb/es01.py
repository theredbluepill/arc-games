"""Escort: NPC steps one cell toward you each turn; both you and the NPC must reach their goals."""

from arcengine import (
    ARCBaseGame,
    Camera,
    Level,
    RenderableUserDisplay,
    Sprite,
)


class Es01UI(RenderableUserDisplay):
    def __init__(self, d: int) -> None:
        self._d = d

    def update(self, d: int) -> None:
        self._d = d

    def render_interface(self, frame):
        import numpy as np

        if not isinstance(frame, np.ndarray):
            return frame
        h, _w = frame.shape
        for i in range(min(self._d, 12)):
            frame[h - 2, 1 + i] = 7
        return frame


sprites = {
    "player": Sprite(
        pixels=[[9]],
        name="player",
        visible=True,
        collidable=True,
        tags=["player"],
    ),
    "npc": Sprite(
        pixels=[[6]],
        name="npc",
        visible=True,
        collidable=True,
        tags=["npc"],
    ),
    "goal_p": Sprite(
        pixels=[[14]],
        name="goal_p",
        visible=True,
        collidable=False,
        tags=["goal", "player_goal"],
    ),
    "goal_n": Sprite(
        pixels=[[10]],
        name="goal_n",
        visible=True,
        collidable=False,
        tags=["goal", "npc_goal"],
    ),
    "wall": Sprite(
        pixels=[[3]],
        name="wall",
        visible=True,
        collidable=True,
        tags=["wall"],
    ),
}


def mk(sl: list, d: int) -> Level:
    return Level(sprites=sl, grid_size=(10, 10), data={"difficulty": d})


levels = [
    mk(
        [
            sprites["player"].clone().set_position(1, 5),
            sprites["npc"].clone().set_position(8, 5),
            sprites["goal_p"].clone().set_position(3, 5),
            sprites["goal_n"].clone().set_position(6, 5),
        ],
        1,
    ),
    mk(
        [
            sprites["player"].clone().set_position(0, 5),
            sprites["npc"].clone().set_position(9, 5),
            sprites["goal_p"].clone().set_position(2, 5),
            sprites["goal_n"].clone().set_position(7, 5),
        ],
        2,
    ),
    mk(
        [
            sprites["player"].clone().set_position(1, 1),
            sprites["npc"].clone().set_position(8, 8),
            sprites["goal_p"].clone().set_position(4, 1),
            sprites["goal_n"].clone().set_position(5, 8),
        ],
        3,
    ),
    mk(
        [
            sprites["player"].clone().set_position(2, 5),
            sprites["npc"].clone().set_position(7, 5),
            sprites["goal_p"].clone().set_position(4, 5),
            sprites["goal_n"].clone().set_position(5, 5),
            sprites["wall"].clone().set_position(5, 4),
            sprites["wall"].clone().set_position(5, 6),
        ],
        4,
    ),
    mk(
        [
            sprites["player"].clone().set_position(0, 0),
            sprites["npc"].clone().set_position(9, 9),
            sprites["goal_p"].clone().set_position(8, 0),
            sprites["goal_n"].clone().set_position(1, 9),
        ],
        5,
    ),
]

BACKGROUND_COLOR = 5
PADDING_COLOR = 4


class Es01(ARCBaseGame):
    def __init__(self) -> None:
        self._ui = Es01UI(1)
        super().__init__(
            "es01",
            levels,
            Camera(0, 0, 16, 16, BACKGROUND_COLOR, PADDING_COLOR, [self._ui]),
            False,
            1,
            [1, 2, 3, 4],
        )

    def on_set_level(self, level: Level) -> None:
        self._player = self.current_level.get_sprites_by_tag("player")[0]
        self._npc = self.current_level.get_sprites_by_tag("npc")[0]
        self._goal_p = [s for s in self.current_level.get_sprites_by_tag("goal") if "player_goal" in s.tags][0]
        self._goal_n = [s for s in self.current_level.get_sprites_by_tag("goal") if "npc_goal" in s.tags][0]
        self._ui.update(int(level.get_data("difficulty") or 1))

    def _blocked(self, x: int, y: int, ignore: Sprite | None = None) -> bool:
        gw, gh = self.current_level.grid_size
        if not (0 <= x < gw and 0 <= y < gh):
            return True
        sp = self.current_level.get_sprite_at(x, y, ignore_collidable=True)
        if sp is ignore:
            return False
        if not sp:
            return False
        if "goal" in sp.tags:
            return False
        return sp.is_collidable

    def _move_npc(self) -> None:
        px, py = self._player.x, self._player.y
        nx, ny = self._npc.x, self._npc.y
        cand: list[tuple[int, int]] = []
        if px > nx:
            cand.append((nx + 1, ny))
        elif px < nx:
            cand.append((nx - 1, ny))
        if py > ny:
            cand.append((nx, ny + 1))
        elif py < ny:
            cand.append((nx, ny - 1))
        for tx, ty in cand:
            if not self._blocked(tx, ty, ignore=self._npc):
                self._npc.set_position(tx, ty)
                return

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

        if dx == 0 and dy == 0:
            self.complete_action()
            return

        nx = self._player.x + dx
        ny = self._player.y + dy
        gw, gh = self.current_level.grid_size
        if not (0 <= nx < gw and 0 <= ny < gh):
            self.complete_action()
            return

        sp = self.current_level.get_sprite_at(nx, ny, ignore_collidable=True)
        if sp and "wall" in sp.tags:
            self.complete_action()
            return
        if sp and "npc" in sp.tags:
            self.complete_action()
            return

        if not sp or not sp.is_collidable:
            self._player.set_position(nx, ny)

        self._move_npc()

        if self._npc.x == self._player.x and self._npc.y == self._player.y:
            self.lose()
            self.complete_action()
            return

        on_p = self._player.x == self._goal_p.x and self._player.y == self._goal_p.y
        on_n = self._npc.x == self._goal_n.x and self._npc.y == self._goal_n.y
        if on_p and on_n:
            self.next_level()

        self.complete_action()
