"""Tandem: two players move with the same delta each step. Both must stand on their own green goals. ACTION5 swaps which avatar is checked first for collisions (lead)."""

from __future__ import annotations

from arcengine import (
    ARCBaseGame,
    Camera,
    Level,
    RenderableUserDisplay,
    Sprite,
)

BACKGROUND_COLOR = 5
PADDING_COLOR = 4
CAM = 16


class Mc01UI(RenderableUserDisplay):
    def __init__(self, lead: int) -> None:
        self._lead = lead
        self._blocked = 0

    def clear_feedback(self) -> None:
        self._blocked = 0

    def flash_blocked(self, frames: int = 8) -> None:
        self._blocked = max(self._blocked, frames)

    def tick_blocked(self) -> None:
        if self._blocked > 0:
            self._blocked -= 1

    def update(self, lead: int) -> None:
        self._lead = lead

    def render_interface(self, frame):
        import numpy as np

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape
        c = 9 if self._lead == 0 else 10
        frame[h - 2, 2] = c
        # "L" glyph: lead avatar moves first for collision resolution.
        frame[h - 2, 4] = c
        frame[h - 2, 5] = c
        frame[h - 3, 4] = c
        if self._blocked > 0:
            frame[h - 1, w - 3] = 8
        return frame


sprites = {
    "p1": Sprite(
        pixels=[[9]],
        name="p1",
        visible=True,
        collidable=True,
        tags=["player", "p1"],
    ),
    "p2": Sprite(
        pixels=[[10]],
        name="p2",
        visible=True,
        collidable=True,
        tags=["player", "p2"],
    ),
    "goal1": Sprite(
        pixels=[[11]],
        name="goal1",
        visible=True,
        collidable=False,
        tags=["goal", "g1"],
    ),
    "goal2": Sprite(
        pixels=[[14]],
        name="goal2",
        visible=True,
        collidable=False,
        tags=["goal", "g2"],
    ),
    "wall": Sprite(
        pixels=[[3]],
        name="wall",
        visible=True,
        collidable=True,
        tags=["wall"],
    ),
}


def mk(
    a: tuple[int, int],
    b: tuple[int, int],
    ga: tuple[int, int],
    gb: tuple[int, int],
    walls: list[tuple[int, int]],
    diff: int,
) -> Level:
    sl = [
        sprites["p1"].clone().set_position(*a),
        sprites["p2"].clone().set_position(*b),
        sprites["goal1"].clone().set_position(*ga),
        sprites["goal2"].clone().set_position(*gb),
    ]
    for wx, wy in walls:
        sl.append(sprites["wall"].clone().set_position(wx, wy))
    return Level(sprites=sl, grid_size=(CAM, CAM), data={"difficulty": diff})


levels = [
    # Narrow corridor teaches joint motion before open layouts.
    # Goals must match the start (p2−p1) offset — here (1,0) — under tandem + swap.
    mk((2, 8), (3, 8), (12, 8), (13, 8), [(x, 6) for x in range(16) if x != 8], 1),
    mk((1, 1), (14, 1), (1, 14), (14, 14), [(8, y) for y in range(16) if y != 7], 2),
    # Vertical wall with gap at (8,8); same-row start/goals (lead order around the slit).
    mk((2, 8), (3, 8), (12, 8), (13, 8), [(8, y) for y in range(16) if y != 8], 3),
    # Empty grid: offset (1,0) preserved from start to goals.
    mk((0, 0), (1, 0), (14, 8), (15, 8), [], 4),
    mk((4, 4), (11, 4), (4, 11), (11, 11), [(8, y) for y in range(16)], 5),
]


class Mc01(ARCBaseGame):
    def __init__(self) -> None:
        self._ui = Mc01UI(0)
        super().__init__(
            "mc01",
            levels,
            Camera(0, 0, CAM, CAM, BACKGROUND_COLOR, PADDING_COLOR, [self._ui]),
            False,
            1,
            [1, 2, 3, 4, 5],
        )

    def on_set_level(self, level: Level) -> None:
        self._p1 = self.current_level.get_sprites_by_tag("p1")[0]
        self._p2 = self.current_level.get_sprites_by_tag("p2")[0]
        self._lead = 0
        self._ui.clear_feedback()
        self._ui.update(self._lead)

    def _blocked(self, x: int, y: int, ignore: Sprite | None) -> bool:
        sp = self.current_level.get_sprite_at(x, y, ignore_collidable=True)
        if not sp:
            return False
        if "wall" in sp.tags:
            return True
        if "player" in sp.tags and sp is not ignore:
            return True
        return False

    def step(self) -> None:
        self._ui.tick_blocked()
        aid = self.action.id.value
        if aid == 5:
            self._lead = 1 - self._lead
            self._ui.update(self._lead)
            self.complete_action()
            return

        dx = dy = 0
        if aid == 1:
            dy = -1
        elif aid == 2:
            dy = 1
        elif aid == 3:
            dx = -1
        elif aid == 4:
            dx = 1
        else:
            self.complete_action()
            return

        order = [self._p1, self._p2] if self._lead == 0 else [self._p2, self._p1]
        t1 = (order[0].x + dx, order[0].y + dy)
        t2 = (order[1].x + dx, order[1].y + dy)

        if t1 == (order[1].x, order[1].y) and t2 == (order[0].x, order[0].y):
            order[0].set_position(t1[0], t1[1])
            order[1].set_position(t2[0], t2[1])
        elif self._blocked(t1[0], t1[1], order[0]) or self._blocked(
            t2[0], t2[1], order[1]
        ):
            self._ui.flash_blocked()
            self.complete_action()
            return
        else:
            order[0].set_position(t1[0], t1[1])
            order[1].set_position(t2[0], t2[1])

        g1 = self.current_level.get_sprites_by_tag("g1")[0]
        g2 = self.current_level.get_sprites_by_tag("g2")[0]
        ok1 = self._p1.x == g1.x and self._p1.y == g1.y
        ok2 = self._p2.x == g2.x and self._p2.y == g2.y
        if ok1 and ok2:
            self.next_level()

        self.complete_action()
