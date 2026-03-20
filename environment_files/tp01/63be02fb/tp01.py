from arcengine import (
    ARCBaseGame,
    Camera,
    Level,
    RenderableUserDisplay,
    Sprite,
)


class Tp01UI(RenderableUserDisplay):
    """Bidirectional pairs: magenta badge + pair-count ticks + ↔ hint (white flanking)."""

    def __init__(self, difficulty: int, n_pairs: int) -> None:
        self._difficulty = difficulty
        self._n_pairs = n_pairs

    def update(self, difficulty: int, n_pairs: int) -> None:
        self._difficulty = difficulty
        self._n_pairs = n_pairs

    def render_interface(self, frame):
        import numpy as np

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape
        # 2×2 magenta = both link ends stay active (contrast tp03 burn)
        for dy in range(2):
            for dx in range(2):
                frame[h - 3 + dy, w - 4 + dx] = 7
        # ↔ : white caps flanking the block
        frame[h - 3, w - 5] = 1
        frame[h - 3, w - 2] = 1
        # Pair count (magenta ticks)
        for i in range(min(6, max(0, self._n_pairs))):
            frame[h - 1, 1 + i] = 7
        # Difficulty accent (level hue)
        palette = [10, 11, 12, 14, 15]
        d = max(0, min(len(palette) - 1, self._difficulty - 1))
        frame[h - 2, 1] = palette[d]
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


def lvl(sprites_list, grid_size, difficulty, portal_pairs):
    return Level(
        sprites=sprites_list,
        grid_size=grid_size,
        data={"difficulty": difficulty, "portal_pairs": portal_pairs},
    )


# Each level has a **full** wall barrier so the yellow goal is unreachable without
# stepping through a magenta portal pair (bidirectional warp).
levels = [
    lvl(
        [
            sprites["player"].clone().set_position(0, 3),
            sprites["portal"].clone().set_position(2, 3),
            sprites["portal"].clone().set_position(5, 3),
            sprites["target"].clone().set_position(6, 3),
        ]
        + [sprites["wall"].clone().set_position(4, y) for y in range(8)],
        (8, 8),
        1,
        [[(2, 3), (5, 3)]],
    ),
    lvl(
        [
            sprites["player"].clone().set_position(1, 1),
            sprites["portal"].clone().set_position(2, 2),
            sprites["portal"].clone().set_position(4, 2),
            sprites["target"].clone().set_position(6, 6),
        ]
        + [sprites["wall"].clone().set_position(3, y) for y in range(8)],
        (8, 8),
        2,
        [[(2, 2), (4, 2)]],
    ),
    lvl(
        [
            sprites["player"].clone().set_position(1, 3),
            sprites["portal"].clone().set_position(2, 1),
            sprites["portal"].clone().set_position(5, 5),
            sprites["portal"].clone().set_position(2, 5),
            sprites["portal"].clone().set_position(5, 1),
            sprites["target"].clone().set_position(6, 4),
        ]
        + [sprites["wall"].clone().set_position(4, y) for y in range(8)],
        (8, 8),
        3,
        [[(2, 1), (5, 5)], [(2, 5), (5, 1)]],
    ),
    lvl(
        [
            sprites["player"].clone().set_position(1, 4),
            sprites["portal"].clone().set_position(2, 4),
            sprites["portal"].clone().set_position(8, 4),
            sprites["target"].clone().set_position(9, 2),
        ]
        + [sprites["wall"].clone().set_position(5, y) for y in range(8)],
        (10, 8),
        4,
        [[(2, 4), (8, 4)]],
    ),
    lvl(
        [
            sprites["player"].clone().set_position(1, 2),
            sprites["portal"].clone().set_position(2, 3),
            sprites["portal"].clone().set_position(2, 5),
            sprites["target"].clone().set_position(7, 6),
        ]
        + [sprites["wall"].clone().set_position(x, 4) for x in range(8)],
        (8, 8),
        5,
        [[(2, 3), (2, 5)]],
    ),
]

BACKGROUND_COLOR = 5
PADDING_COLOR = 4


class Tp01(ARCBaseGame):
    """Symmetric portal pairs: either tile warps to its partner (same rule both ways)."""

    def __init__(self) -> None:
        self._ui = Tp01UI(0, 0)
        super().__init__(
            "tp01",
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
        self._ui.update(level.get_data("difficulty") or 0, len(pairs))

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
            self._player.set_position(dest[0], dest[1])

        for t in self._targets:
            if self._player.x == t.x and self._player.y == t.y:
                self.next_level()
                break

        self.complete_action()
