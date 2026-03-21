from arcengine import (
    ARCBaseGame,
    Camera,
    Level,
    RenderableUserDisplay,
    Sprite,
)


class Tp02UI(RenderableUserDisplay):
    """One-way warps: orange exit arrows on source cells + orange HUD chevron."""

    CAMERA_W = 16
    CAMERA_H = 16
    ARROW = 12  # orange — reads distinct from magenta portals

    def __init__(self) -> None:
        self._directed: list[tuple[tuple[int, int], tuple[int, int]]] = []
        self._difficulty = 1

    def update(
        self,
        directed_pairs: list,
        difficulty: int,
    ) -> None:
        self._difficulty = difficulty
        self._directed = []
        for a, b in directed_pairs or []:
            self._directed.append((tuple(a), tuple(b)))

    @classmethod
    def _grid_to_frame_pixel(cls, gx: int, gy: int) -> tuple[int, int]:
        cw, ch = cls.CAMERA_W, cls.CAMERA_H
        scale = min(64 // cw, 64 // ch)
        x_pad = (64 - cw * scale) // 2
        y_pad = (64 - ch * scale) // 2
        return gx * scale + scale // 2 + x_pad, gy * scale + scale // 2 + y_pad

    @staticmethod
    def _plot(frame, h: int, w: int, px: int, py: int, c: int) -> None:
        if 0 <= px < w and 0 <= py < h:
            frame[py, px] = c

    @classmethod
    def _arrow_step(cls, ax: int, ay: int, bx: int, by: int) -> tuple[int, int]:
        dx, dy = bx - ax, by - ay
        if dx == 0 and dy == 0:
            return 0, 0
        adx, ady = abs(dx), abs(dy)
        if adx >= ady and adx > 0:
            return (1 if dx > 0 else -1), 0
        if ady > 0:
            return 0, (1 if dy > 0 else -1)
        return 0, 0

    def render_interface(self, frame):
        import numpy as np

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape
        # Legend: orange chevron (one-way) bottom-left
        for px, py in ((1, h - 2), (2, h - 2), (2, h - 3), (3, h - 2), (3, h - 4), (4, h - 2)):
            self._plot(frame, h, w, px, py, self.ARROW)
        pal = [10, 11, 12, 14, 15]
        di = max(0, min(len(pal) - 1, self._difficulty - 1))
        self._plot(frame, h, w, 1, h - 4, pal[di])

        for (ax, ay), (bx, by) in self._directed:
            cx, cy = self._grid_to_frame_pixel(ax, ay)
            sx, sy = self._arrow_step(ax, ay, bx, by)
            if sx == 0 and sy == 0:
                continue
            for k in (2, 4, 6):
                self._plot(frame, h, w, cx + sx * k, cy + sy * k, self.ARROW)
            # Arrowhead
            tx, ty = cx + sx * 7, cy + sy * 7
            if sx != 0:
                self._plot(frame, h, w, tx, ty, self.ARROW)
                self._plot(frame, h, w, tx - sx, ty + 1, self.ARROW)
                self._plot(frame, h, w, tx - sx, ty - 1, self.ARROW)
            else:
                self._plot(frame, h, w, tx, ty, self.ARROW)
                self._plot(frame, h, w, tx + 1, ty - sy, self.ARROW)
                self._plot(frame, h, w, tx - 1, ty - sy, self.ARROW)

        return frame


sprites = {
    "player": Sprite(
        pixels=[[9]],
        name="player",
        visible=True,
        collidable=True,
        tags=["player"],
    ),
    "portal": Sprite(
        pixels=[[7]],
        name="portal",
        visible=True,
        collidable=False,
        tags=["portal"],
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


def lvl(sl, grid_size, difficulty, directed_pairs):
    return Level(
        sprites=sl,
        grid_size=grid_size,
        data={"difficulty": difficulty, "directed_pairs": directed_pairs},
    )


# Layouts emphasize **irreversible** routing: destination tiles are “cold” (no back-warp).
levels = [
    lvl(
        [
            sprites["player"].clone().set_position(0, 3),
            sprites["portal"].clone().set_position(2, 3),
            sprites["portal"].clone().set_position(6, 3),
            sprites["target"].clone().set_position(7, 3),
        ]
        + [sprites["wall"].clone().set_position(4, y) for y in range(8)],
        (8, 8),
        1,
        [[(2, 3), (6, 3)]],
    ),
    lvl(
        [
            sprites["player"].clone().set_position(0, 6),
            sprites["portal"].clone().set_position(2, 6),
            sprites["portal"].clone().set_position(6, 1),
            sprites["target"].clone().set_position(7, 1),
        ]
        + [sprites["wall"].clone().set_position(4, y) for y in range(8) if y not in (1, 6)],
        (8, 8),
        2,
        [[(2, 6), (6, 1)]],
    ),
    lvl(
        [
            sprites["player"].clone().set_position(0, 3),
            sprites["portal"].clone().set_position(1, 3),
            sprites["portal"].clone().set_position(5, 3),
            sprites["portal"].clone().set_position(1, 6),
            sprites["portal"].clone().set_position(5, 6),
            sprites["target"].clone().set_position(7, 6),
        ]
        + [sprites["wall"].clone().set_position(4, y) for y in range(8) if y not in (3, 6)],
        (8, 8),
        3,
        [[(1, 3), (5, 3)], [(1, 6), (5, 6)]],
    ),
    lvl(
        [
            sprites["player"].clone().set_position(0, 4),
            sprites["portal"].clone().set_position(2, 4),
            sprites["portal"].clone().set_position(8, 4),
            sprites["target"].clone().set_position(9, 0),
        ]
        + [sprites["wall"].clone().set_position(5, y) for y in range(8) if y != 4],
        (10, 8),
        4,
        [[(2, 4), (8, 4)]],
    ),
    lvl(
        [
            sprites["player"].clone().set_position(1, 1),
            sprites["portal"].clone().set_position(3, 1),
            sprites["portal"].clone().set_position(5, 5),
            sprites["portal"].clone().set_position(1, 5),
            sprites["portal"].clone().set_position(5, 1),
            sprites["target"].clone().set_position(6, 6),
        ]
        + [
            sprites["wall"].clone().set_position(x, y)
            for x, y in [(2, 2), (4, 2), (2, 4), (4, 4)]
        ],
        (8, 8),
        5,
        [[(3, 1), (5, 5)], [(1, 5), (5, 1)]],
    ),
]

BACKGROUND_COLOR = 5
PADDING_COLOR = 4


class Tp02(ARCBaseGame):
    """Directed portals: only listed **from→to** tiles teleport; exit cells never pull you back."""

    def __init__(self) -> None:
        self._ui = Tp02UI()
        super().__init__(
            "tp02",
            levels,
            Camera(0, 0, 16, 16, BACKGROUND_COLOR, PADDING_COLOR, [self._ui]),
            False,
            1,
            [1, 2, 3, 4],
        )

    def on_set_level(self, level: Level) -> None:
        self._player = self.current_level.get_sprites_by_tag("player")[0]
        self._targets = self.current_level.get_sprites_by_tag("target")
        pairs = level.get_data("directed_pairs") or []
        self._warp_from: dict[tuple[int, int], tuple[int, int]] = {}
        for a, b in pairs:
            self._warp_from[tuple(a)] = tuple(b)
        self._ui.update(pairs, level.get_data("difficulty") or 1)

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

        if not sprite or not sprite.is_collidable:
            self._player.set_position(new_x, new_y)

        pos = (self._player.x, self._player.y)
        if pos in self._warp_from:
            dest = self._warp_from[pos]
            self._player.set_position(dest[0], dest[1])

        for t in self._targets:
            if self._player.x == t.x and self._player.y == t.y:
                self.next_level()
                break

        self.complete_action()
