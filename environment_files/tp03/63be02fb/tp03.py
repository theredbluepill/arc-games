from arcengine import (
    ARCBaseGame,
    Camera,
    Level,
    RenderableUserDisplay,
    Sprite,
)


class Tp03UI(RenderableUserDisplay):
    """Single-use pairs: yellow pair-budget ticks + white burn flash on warp exit."""

    CAMERA_W = 16
    CAMERA_H = 16

    def __init__(self) -> None:
        self._pairs_left = 0
        self._difficulty = 1
        self._burn_gx = -1
        self._burn_gy = -1
        self._burn_frames = 0

    def update(self, pairs_left: int, difficulty: int) -> None:
        self._pairs_left = max(0, pairs_left)
        self._difficulty = difficulty

    def start_burn(self, gx: int, gy: int) -> None:
        self._burn_gx = gx
        self._burn_gy = gy
        self._burn_frames = 6

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

    def render_interface(self, frame):
        import numpy as np

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape
        # “Consumable” cue: dim cross-out vs tp01’s solid 2×2 badge
        for dy in range(2):
            for dx in range(2):
                frame[h - 3 + dy, w - 4 + dx] = 3
        frame[h - 3, w - 3] = 11

        pal = [10, 11, 12, 14, 15]
        di = max(0, min(len(pal) - 1, self._difficulty - 1))
        self._plot(frame, h, w, w - 2, h - 3, pal[di])

        for i in range(min(8, self._pairs_left)):
            self._plot(frame, h, w, 2 + i, h - 1, 11)

        if self._burn_frames > 0 and self._burn_gx >= 0:
            cx, cy = self._grid_to_frame_pixel(self._burn_gx, self._burn_gy)
            c = 1 if self._burn_frames > 3 else 11
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    if max(abs(dx), abs(dy)) in (1, 2):
                        self._plot(frame, h, w, cx + dx, cy + dy, c)
            self._burn_frames -= 1
        else:
            self._burn_frames = 0

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


def lvl(sl, grid_size, difficulty, portal_pairs):
    return Level(
        sprites=sl,
        grid_size=grid_size,
        data={"difficulty": difficulty, "portal_pairs": portal_pairs},
    )


levels = [
    lvl(
        [
            sprites["player"].clone().set_position(0, 3),
            sprites["portal"].clone().set_position(2, 3),
            sprites["portal"].clone().set_position(6, 3),
            sprites["target"].clone().set_position(7, 3),
        ],
        (8, 8),
        1,
        [[(2, 3), (6, 3)]],
    ),
    lvl(
        [
            sprites["player"].clone().set_position(1, 1),
            sprites["portal"].clone().set_position(1, 5),
            sprites["portal"].clone().set_position(5, 5),
            sprites["target"].clone().set_position(6, 1),
        ]
        + [sprites["wall"].clone().set_position(3, y) for y in range(6)],
        (8, 8),
        2,
        [[(1, 5), (5, 5)]],
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
        3,
        [[(2, 4), (8, 4)]],
    ),
    lvl(
        [
            sprites["player"].clone().set_position(0, 0),
            sprites["portal"].clone().set_position(1, 1),
            sprites["portal"].clone().set_position(6, 6),
            sprites["target"].clone().set_position(7, 0),
        ],
        (8, 8),
        4,
        [[(1, 1), (6, 6)]],
    ),
    lvl(
        [
            sprites["player"].clone().set_position(1, 1),
            sprites["portal"].clone().set_position(2, 2),
            sprites["portal"].clone().set_position(5, 5),
            sprites["target"].clone().set_position(6, 6),
        ]
        + [sprites["wall"].clone().set_position(3, y) for y in range(8) if y != 4],
        (8, 8),
        5,
        [[(2, 2), (5, 5)]],
    ),
]

BACKGROUND_COLOR = 5
PADDING_COLOR = 4


class Tp03(ARCBaseGame):
    """Symmetric pairs like tp01, but each link **burns out**: both cells clear after one warp."""

    def __init__(self) -> None:
        self._ui = Tp03UI()
        super().__init__(
            "tp03",
            levels,
            Camera(0, 0, 16, 16, BACKGROUND_COLOR, PADDING_COLOR, [self._ui]),
            False,
            1,
            [1, 2, 3, 4],
        )

    def on_set_level(self, level: Level) -> None:
        self._player = self.current_level.get_sprites_by_tag("player")[0]
        self._targets = self.current_level.get_sprites_by_tag("target")
        pairs = level.get_data("portal_pairs") or []
        self._portal_to_partner: dict[tuple[int, int], tuple[int, int]] = {}
        for a, b in pairs:
            ta, tb = tuple(a), tuple(b)
            self._portal_to_partner[ta] = tb
            self._portal_to_partner[tb] = ta
        self._sync_ui()

    def _sync_ui(self) -> None:
        left = len(self._portal_to_partner) // 2
        self._ui.update(left, self.current_level.get_data("difficulty") or 1)

    def _purge_pair(self, src: tuple[int, int], dest: tuple[int, int]) -> None:
        for sp in list(self.current_level.get_sprites_by_tag("portal")):
            if (sp.x, sp.y) in (src, dest):
                self.current_level.remove_sprite(sp)
        self._portal_to_partner.pop(src, None)
        self._portal_to_partner.pop(dest, None)

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
        if pos in self._portal_to_partner:
            dest = self._portal_to_partner[pos]
            self._purge_pair(pos, dest)
            self._player.set_position(dest[0], dest[1])
            self._ui.start_burn(dest[0], dest[1])
            self._sync_ui()

        for t in self._targets:
            if self._player.x == t.x and self._player.y == t.y:
                self.next_level()
                break

        self.complete_action()
