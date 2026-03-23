"""pk02: two-click an adjacent pair to claim a marked ribbon edge; cover all."""

from __future__ import annotations

from arcengine import ARCBaseGame, Camera, GameAction, Level, RenderableUserDisplay, Sprite

BG, PAD = 5, 4
G = 10
RIB = Sprite(pixels=[[12]], name="r", visible=True, collidable=False, tags=["ribbon"])
MARK = Sprite(pixels=[[2]], name="m", visible=True, collidable=False, tags=["edge_mark"])


class Pk02UI(RenderableUserDisplay):
    def __init__(self, pend: bool, done: int, tot: int) -> None:
        self._p, self._d, self._t = pend, done, tot
        self._click: tuple[int, int] | None = None
        self._reject_frames = 0

    def update(self, pend: bool, done: int, tot: int) -> None:
        self._p, self._d, self._t = pend, done, tot

    def set_click(self, fx: int, fy: int) -> None:
        self._click = (fx, fy)

    def flash_reject(self, frames: int = 6) -> None:
        self._reject_frames = frames

    def render_interface(self, frame):
        import numpy as np

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape
        frame[h - 2, 2] = 11 if self._p else 5
        for i in range(min(self._d, 12)):
            frame[h - 2, 4 + i] = 14
        if self._reject_frames > 0:
            for dx in range(2):
                for dy in range(2):
                    px, py = w - 2 + dx, dy
                    if 0 <= px < w and 0 <= py < h:
                        frame[py, px] = 8
            self._reject_frames -= 1
        if self._click:
            cx, cy = self._click
            for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
                px, py = cx + dx, cy + dy
                if 0 <= px < w and 0 <= py < h:
                    frame[py, px] = 10
            self._click = None
        return frame


def norm_edge(a: tuple[int, int], b: tuple[int, int]) -> frozenset:
    return frozenset({a, b})


def mk(edges: list[tuple[tuple[int, int], tuple[int, int]]], d: int) -> Level:
    sl: list[Sprite] = []
    verts: set[tuple[int, int]] = set()
    for (x1, y1), (x2, y2) in edges:
        verts.add((x1, y1))
        verts.add((x2, y2))
    for vx, vy in sorted(verts):
        sl.append(MARK.clone().set_position(vx, vy))
    return Level(
        sprites=sl,
        grid_size=(G, G),
        data={"edges": [[[a[0], a[1]], [b[0], b[1]]] for a, b in edges], "difficulty": d},
    )


levels = [
    mk([((2, 2), (3, 2)), ((3, 2), (3, 3)), ((2, 3), (3, 3)), ((2, 2), (2, 3))], 1),
    mk([((1, 1), (2, 1)), ((2, 1), (2, 2)), ((1, 2), (2, 2)), ((1, 1), (1, 2))], 2),
    mk([((4, 4), (5, 4)), ((5, 4), (5, 5)), ((4, 5), (5, 5)), ((4, 4), (4, 5))], 3),
    mk(
        [
            ((2, 3), (3, 3)),
            ((3, 3), (3, 4)),
            ((2, 4), (3, 4)),
            ((2, 3), (2, 4)),
            ((5, 5), (6, 5)),
            ((6, 5), (6, 6)),
        ],
        4,
    ),
    mk(
        [
            ((1, 2), (2, 2)),
            ((2, 2), (2, 3)),
            ((1, 3), (2, 3)),
            ((1, 2), (1, 3)),
            ((6, 1), (7, 1)),
            ((7, 1), (7, 2)),
        ],
        5,
    ),
    mk(
        [
            ((2, 2), (3, 2)),
            ((3, 2), (4, 2)),
            ((2, 3), (3, 3)),
            ((3, 3), (4, 3)),
        ],
        6,
    ),
    mk(
        [
            ((2, 5), (3, 5)),
            ((3, 5), (3, 6)),
            ((2, 6), (3, 6)),
            ((2, 5), (2, 6)),
            ((5, 2), (6, 2)),
            ((6, 2), (6, 3)),
            ((5, 3), (6, 3)),
            ((5, 2), (5, 3)),
        ],
        7,
    ),
]


class Pk02(ARCBaseGame):
    def __init__(self) -> None:
        self._ui = Pk02UI(False, 0, 1)
        super().__init__(
            "pk02",
            levels,
            Camera(0, 0, 16, 16, BG, PAD, [self._ui]),
            False,
            1,
            [6],
        )

    def _grid_to_frame_pixel(self, gx: int, gy: int) -> tuple[int, int]:
        cam = self.camera
        cw, ch = cam.width, cam.height
        scale = min(int(64 / cw), int(64 / ch))
        x_pad = int((64 - (cw * scale)) / 2)
        y_pad = int((64 - (ch * scale)) / 2)
        px = gx * scale + scale // 2 + x_pad
        py = gy * scale + scale // 2 + y_pad
        return px, py

    def on_set_level(self, level: Level) -> None:
        raw = level.get_data("edges") or []
        self._left: set[frozenset] = set()
        for a, b in raw:
            p, q = (int(a[0]), int(a[1])), (int(b[0]), int(b[1]))
            if abs(p[0] - q[0]) + abs(p[1] - q[1]) == 1:
                self._left.add(frozenset({p, q}))
        self._pend = None
        self._tot = len(self._left)
        self._ui.update(False, 0, self._tot)

    def step(self) -> None:
        if self.action.id != GameAction.ACTION6:
            self.complete_action()
            return
        hit = self.camera.display_to_grid(
            self.action.data.get("x", 0), self.action.data.get("y", 0)
        )
        if not hit:
            self._ui.flash_reject()
            self.complete_action()
            return
        gx, gy = int(hit[0]), int(hit[1])
        self._ui.set_click(*self._grid_to_frame_pixel(gx, gy))
        if self._pend is None:
            self._pend = (gx, gy)
            self._ui.update(True, self._tot - len(self._left), self._tot)
            self.complete_action()
            return
        ax, ay = self._pend
        self._pend = None
        e = frozenset({(ax, ay), (gx, gy)})
        if abs(ax - gx) + abs(ay - gy) != 1 or e not in self._left:
            self._ui.flash_reject()
            self._ui.update(False, self._tot - len(self._left), self._tot)
            self.complete_action()
            return
        self._left.remove(e)
        mx, my = (ax + gx) // 2, (ay + gy) // 2
        self.current_level.add_sprite(RIB.clone().set_position(mx, my))
        done = self._tot - len(self._left)
        self._ui.update(False, done, self._tot)
        if not self._left:
            self.next_level()
        self.complete_action()
