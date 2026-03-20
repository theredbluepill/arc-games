"""Pipe drop: ACTION6 cycles empty / H / V straight pipe on floor; connect cyan source to yellow sink (orthogonal flow)."""

from collections import deque

from arcengine import (
    ARCBaseGame,
    Camera,
    GameAction,
    Level,
    RenderableUserDisplay,
    Sprite,
)


class Pd01UI(RenderableUserDisplay):
    def __init__(self, ok: bool) -> None:
        self._ok = ok

    def update(self, ok: bool) -> None:
        self._ok = ok

    def render_interface(self, frame):
        import numpy as np

        if not isinstance(frame, np.ndarray):
            return frame
        h, _w = frame.shape
        frame[h - 2, 2] = 14 if self._ok else 8
        return frame


sprites = {
    "wall": Sprite(
        pixels=[[3]],
        name="wall",
        visible=True,
        collidable=True,
        tags=["wall"],
    ),
    "source": Sprite(
        pixels=[[10]],
        name="source",
        visible=True,
        collidable=False,
        tags=["source"],
    ),
    "sink": Sprite(
        pixels=[[11]],
        name="sink",
        visible=True,
        collidable=False,
        tags=["sink"],
    ),
    "pipe": Sprite(
        pixels=[[12]],
        name="pipe",
        visible=True,
        collidable=False,
        tags=["pipe"],
    ),
}


def mk(
    walls: list[tuple[int, int]],
    src: tuple[int, int],
    snk: tuple[int, int],
    d: int,
) -> Level:
    sl: list[Sprite] = [sprites["wall"].clone().set_position(wx, wy) for wx, wy in walls]
    sl.append(sprites["source"].clone().set_position(*src))
    sl.append(sprites["sink"].clone().set_position(*snk))
    return Level(sprites=sl, grid_size=(10, 10), data={"difficulty": d})


levels = [
    mk([(x, 0) for x in range(10)] + [(x, 9) for x in range(10)] + [(0, y) for y in range(10)] + [(9, y) for y in range(10)], (1, 5), (8, 5), 1),
    mk([(x, 0) for x in range(10)] + [(x, 9) for x in range(10)] + [(0, y) for y in range(10)] + [(9, y) for y in range(10)], (5, 1), (5, 8), 2),
    mk([(x, 0) for x in range(10)] + [(x, 9) for x in range(10)] + [(0, y) for y in range(10)] + [(9, y) for y in range(10)], (1, 1), (8, 8), 3),
    mk([(x, 0) for x in range(10)] + [(x, 9) for x in range(10)] + [(0, y) for y in range(10)] + [(9, y) for y in range(10)], (2, 5), (7, 5), 4),
    mk([(x, 0) for x in range(10)] + [(x, 9) for x in range(10)] + [(0, y) for y in range(10)] + [(9, y) for y in range(10)], (1, 8), (8, 1), 5),
]

BACKGROUND_COLOR = 5
PADDING_COLOR = 4
DX = (0, 1, 0, -1)
DY = (-1, 0, 1, 0)


class Pd01(ARCBaseGame):
    def __init__(self) -> None:
        self._ui = Pd01UI(False)
        super().__init__(
            "pd01",
            levels,
            Camera(0, 0, 16, 16, BACKGROUND_COLOR, PADDING_COLOR, [self._ui]),
            False,
            1,
            [1, 2, 3, 4, 6],
        )

    def on_set_level(self, level: Level) -> None:
        self._source = self.current_level.get_sprites_by_tag("source")[0]
        self._sink = self.current_level.get_sprites_by_tag("sink")[0]
        self._pipes: dict[tuple[int, int], str] = {}
        self._pipe_sprites: dict[tuple[int, int], Sprite] = {}
        self._check()

    def _wall_at(self, x: int, y: int) -> bool:
        sp = self.current_level.get_sprite_at(x, y, ignore_collidable=True)
        return bool(sp and "wall" in sp.tags)

    def _kind_at(self, x: int, y: int) -> str | None:
        if self._source.x == x and self._source.y == y:
            return "S"
        if self._sink.x == x and self._sink.y == y:
            return "K"
        return self._pipes.get((x, y))

    def _opens(self, k: str | None, di: int) -> bool:
        if k == "S" or k == "K":
            return True
        if k == "h":
            return di in (1, 3)
        if k == "v":
            return di in (0, 2)
        return False

    def _connected(self) -> bool:
        sx, sy = self._source.x, self._source.y
        tx, ty = self._sink.x, self._sink.y
        q = deque([(sx, sy)])
        seen = {(sx, sy)}
        while q:
            x, y = q.popleft()
            if x == tx and y == ty:
                return True
            for di in range(4):
                nx, ny = x + DX[di], y + DY[di]
                gw, gh = self.current_level.grid_size
                if not (0 <= nx < gw and 0 <= ny < gh):
                    continue
                if self._wall_at(nx, ny):
                    continue
                ka = self._kind_at(x, y)
                kb = self._kind_at(nx, ny)
                if not self._opens(ka, di):
                    continue
                opp = (di + 2) % 4
                if not self._opens(kb, opp):
                    continue
                if (nx, ny) not in seen:
                    seen.add((nx, ny))
                    q.append((nx, ny))
        return False

    def _check(self) -> None:
        ok = self._connected()
        self._ui.update(ok)
        if ok:
            self.next_level()

    def step(self) -> None:
        if self.action.id == GameAction.ACTION6:
            raw_x = self.action.data.get("x", 0)
            raw_y = self.action.data.get("y", 0)
            g = self.camera.display_to_grid(int(raw_x), int(raw_y))
            if g is None:
                self.complete_action()
                return
            gx, gy = g
            if self._wall_at(gx, gy):
                self.complete_action()
                return
            if (self._source.x, self._source.y) == (gx, gy) or (self._sink.x, self._sink.y) == (gx, gy):
                self.complete_action()
                return
            cur = self._pipes.get((gx, gy))
            nxt = "h" if cur is None else ("v" if cur == "h" else None)
            if cur is not None:
                sp_old = self._pipe_sprites.pop((gx, gy), None)
                if sp_old:
                    self.current_level.remove_sprite(sp_old)
            if nxt is not None:
                ps = sprites["pipe"].clone().set_position(gx, gy)
                self.current_level.add_sprite(ps)
                self._pipe_sprites[(gx, gy)] = ps
                self._pipes[(gx, gy)] = nxt
            else:
                self._pipes.pop((gx, gy), None)
            self._check()
            self.complete_action()
            return

        self.complete_action()
