"""Routed delivery: each parcel color is a distinct order for a matching customer. Per-order deadlines (elapsed steps) model SLAs; global step budget still applies. ACTION5 picks up / drops on the correct customer only; otherwise pings the nearest useful stop (matching customer if carrying, else nearest parcel)."""

from __future__ import annotations

from arcengine import (
    ARCBaseGame,
    Camera,
    GameAction,
    Level,
    RenderableUserDisplay,
    Sprite,
)

BACKGROUND_COLOR = 5
PADDING_COLOR = 4
CAM_W = CAM_H = 48

WALL_C = 3
PLAYER_C = 9

# Item / customer identity colors (palette from AGENTS.md) — each active order uses one color per level.
C_ORANGE = 12
C_RED = 8
C_GREEN = 14
C_YELLOW = 11


def _parcel(color: int) -> Sprite:
    return Sprite(
        pixels=[[color]],
        name=f"parcel_{color}",
        visible=True,
        collidable=False,
        tags=["parcel"],
    )


def _customer(color: int) -> Sprite:
    return Sprite(
        pixels=[[color]],
        name=f"customer_{color}",
        visible=True,
        collidable=False,
        tags=["customer"],
    )


class Dd01UI(RenderableUserDisplay):
    def __init__(
        self,
        holding_color: int | None,
        pending: int,
        urgent: bool,
        ping: tuple[int, int] | None,
        ping_frames: int,
    ) -> None:
        self._holding_color = holding_color
        self._pending = pending
        self._urgent = urgent
        self._ping = ping
        self._ping_frames = ping_frames

    def update(
        self,
        holding_color: int | None,
        pending: int,
        urgent: bool,
        ping: tuple[int, int] | None,
        ping_frames: int,
    ) -> None:
        self._holding_color = holding_color
        self._pending = pending
        self._urgent = urgent
        self._ping = ping
        self._ping_frames = ping_frames

    def render_interface(self, frame):
        import numpy as np

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape
        hc = self._holding_color if self._holding_color is not None else 2
        frame[h - 2, 2] = hc
        frame[h - 2, 3] = 8 if self._urgent else 5
        for i in range(min(self._pending, 14)):
            frame[h - 2, 5 + i] = 11
        if self._ping and self._ping_frames > 0:
            px, py = self._ping
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                x, y = px + dx, py + dy
                if 0 <= x < w and 0 <= y < h:
                    frame[y, x] = 7
        return frame


sprites = {
    "wall": Sprite(
        pixels=[[WALL_C]],
        name="wall",
        visible=True,
        collidable=True,
        tags=["wall"],
    ),
    "player": Sprite(
        pixels=[[PLAYER_C]],
        name="player",
        visible=True,
        collidable=True,
        tags=["player"],
    ),
}


def mk(
    walls: list[tuple[int, int]],
    player: tuple[int, int],
    orders: list[tuple[int, int, int, int]],
    customers: list[tuple[int, int, int]],
    max_steps: int,
    diff: int,
) -> Level:
    """orders: (x, y, color, deadline_elapsed) — fail when elapsed >= deadline and that order is not done."""
    sl: list[Sprite] = []
    for wx, wy in walls:
        sl.append(sprites["wall"].clone().set_position(wx, wy))
    sl.append(sprites["player"].clone().set_position(player[0], player[1]))
    for x, y, c, _d in orders:
        sl.append(_parcel(c).clone().set_position(x, y))
    for x, y, c in customers:
        sl.append(_customer(c).clone().set_position(x, y))
    order_payload = [{"x": x, "y": y, "color": c, "deadline": d} for x, y, c, d in orders]
    return Level(
        sprites=sl,
        grid_size=(CAM_W, CAM_H),
        data={"difficulty": diff, "max_steps": max_steps, "orders": order_payload},
    )


def _row_wall(y, x0, x1):
    return [(x, y) for x in range(x0, x1)]


levels = [
    mk(
        [],
        (4, 24),
        [
            (10, 24, C_ORANGE, 320),
            (14, 24, C_RED, 340),
        ],
        [(40, 24, C_ORANGE), (36, 24, C_RED)],
        420,
        1,
    ),
    mk(
        _row_wall(30, 5, 43) + _row_wall(18, 5, 25),
        (6, 6),
        [
            (12, 12, C_ORANGE, 380),
            (20, 8, C_RED, 480),
        ],
        [(42, 42, C_ORANGE), (38, 10, C_RED)],
        560,
        2,
    ),
    mk(
        [(24, y) for y in range(48) if y % 6 not in (0, 1)],
        (4, 24),
        [
            (30, 10, C_ORANGE, 320),
            (34, 38, C_RED, 420),
            (10, 40, C_GREEN, 520),
        ],
        [(44, 24, C_ORANGE), (40, 8, C_RED), (8, 8, C_GREEN)],
        620,
        3,
    ),
    mk(
        [(x, x) for x in range(48) if 10 < x < 38 and x % 4 != 0],
        (5, 40),
        [
            (20, 20, C_ORANGE, 400),
            (28, 28, C_RED, 480),
            (12, 30, C_GREEN, 560),
        ],
        [(45, 5, C_ORANGE), (40, 45, C_RED), (25, 5, C_GREEN)],
        640,
        4,
    ),
    mk(
        [(15, y) for y in range(48) if y % 4 != 2]
        + [(32, y) for y in range(48) if y % 4 != 0],
        (2, 24),
        [
            (24, 8, C_ORANGE, 340),
            (24, 40, C_RED, 420),
            (8, 24, C_GREEN, 500),
            (40, 24, C_YELLOW, 580),
        ],
        [(46, 24, C_ORANGE), (2, 46, C_RED), (46, 8, C_GREEN), (8, 2, C_YELLOW)],
        720,
        5,
    ),
]


class Dd01(ARCBaseGame):
    PING_FRAMES = 24
    URGENT_LEAD = 36

    def _grid_to_frame_pixel(self, gx: int, gy: int) -> tuple[int, int]:
        cam = self.camera
        cw, ch = cam.width, cam.height
        scale = min(64 // cw, 64 // ch)
        x_pad = (64 - cw * scale) // 2
        y_pad = (64 - ch * scale) // 2
        return gx * scale + scale // 2 + x_pad, gy * scale + scale // 2 + y_pad

    def __init__(self) -> None:
        self._ui = Dd01UI(None, 0, False, None, 0)
        super().__init__(
            "dd01",
            levels,
            Camera(0, 0, CAM_W, CAM_H, BACKGROUND_COLOR, PADDING_COLOR, [self._ui]),
            False,
            1,
            [1, 2, 3, 4, 5],
        )

    def on_set_level(self, level: Level) -> None:
        self._player = self.current_level.get_sprites_by_tag("player")[0]
        self._max_budget = int(self.current_level.get_data("max_steps") or 500)
        self._steps = self._max_budget
        raw = self.current_level.get_data("orders") or []
        self._orders: list[dict] = [
            {
                "sx": int(o["x"]),
                "sy": int(o["y"]),
                "color": int(o["color"]),
                "deadline": int(o["deadline"]),
                "phase": "ground",
            }
            for o in raw
        ]
        self._carrying_oid: int | None = None
        self._ping_pos: tuple[int, int] | None = None
        self._ping_frames = 0
        self._sync_ui()

    def _elapsed(self) -> int:
        return self._max_budget - self._steps

    def _parcels(self) -> list[Sprite]:
        return self.current_level.get_sprites_by_tag("parcel")

    def _customers(self) -> list[Sprite]:
        return self.current_level.get_sprites_by_tag("customer")

    def _pending_count(self) -> int:
        return sum(1 for o in self._orders if o["phase"] != "done")

    def _urgent_deadline(self) -> bool:
        e = self._elapsed()
        for o in self._orders:
            if o["phase"] == "done":
                continue
            if o["deadline"] - e <= self.URGENT_LEAD:
                return True
        return False

    def _check_order_deadlines(self) -> None:
        e = self._elapsed()
        for o in self._orders:
            if o["phase"] == "done":
                continue
            if e >= o["deadline"]:
                self.lose()
                return

    def _sync_ui(self) -> None:
        hc = None
        if self._carrying_oid is not None:
            hc = int(self._orders[self._carrying_oid]["color"])
        self._ui.update(
            hc,
            self._pending_count(),
            self._urgent_deadline(),
            self._ping_pos,
            self._ping_frames,
        )

    def _burn(self) -> bool:
        self._steps -= 1
        self._sync_ui()
        if self._steps <= 0:
            self.lose()
            return True
        return False

    def _nearest_customer_for_color(self, color: int) -> Sprite | None:
        px, py = self._player.x, self._player.y
        best: Sprite | None = None
        best_d = 10**9
        for c in self._customers():
            if int(c.pixels[0][0]) != color:
                continue
            d = abs(c.x - px) + abs(c.y - py)
            if d < best_d:
                best_d = d
                best = c
        return best

    def _nearest_parcel(self) -> Sprite | None:
        px, py = self._player.x, self._player.y
        best: Sprite | None = None
        best_d = 10**9
        for p in self._parcels():
            d = abs(p.x - px) + abs(p.y - py)
            if d < best_d:
                best_d = d
                best = p
        return best

    def _ping_target(self) -> Sprite | None:
        if self._carrying_oid is not None:
            col = int(self._orders[self._carrying_oid]["color"])
            return self._nearest_customer_for_color(col)
        return self._nearest_parcel()

    def step(self) -> None:
        if self._ping_frames > 0:
            self._ping_frames -= 1
            if self._ping_frames == 0:
                self._ping_pos = None
            self._sync_ui()

        aid = self.action.id

        if aid in (GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4):
            dx = dy = 0
            if aid == GameAction.ACTION1:
                dy = -1
            elif aid == GameAction.ACTION2:
                dy = 1
            elif aid == GameAction.ACTION3:
                dx = -1
            elif aid == GameAction.ACTION4:
                dx = 1
            nx, ny = self._player.x + dx, self._player.y + dy
            gw, gh = self.current_level.grid_size
            if 0 <= nx < gw and 0 <= ny < gh:
                sp = self.current_level.get_sprite_at(nx, ny, ignore_collidable=True)
                if sp and "wall" in sp.tags:
                    pass
                elif not sp or not sp.is_collidable:
                    self._player.set_position(nx, ny)
                elif "parcel" in sp.tags or "customer" in sp.tags:
                    self._player.set_position(nx, ny)
            self._sync_ui()
            if self._burn():
                self.complete_action()
                return
            self._check_order_deadlines()
            self._sync_ui()
            self.complete_action()
            return

        if aid == GameAction.ACTION5:
            px, py = self._player.x, self._player.y
            parcel_here = self.current_level.get_sprite_at(
                px, py, tag="parcel", ignore_collidable=True
            )
            customer_here = self.current_level.get_sprite_at(
                px, py, tag="customer", ignore_collidable=True
            )

            if self._carrying_oid is None and parcel_here:
                oid = None
                for i, o in enumerate(self._orders):
                    if o["phase"] == "ground" and o["sx"] == px and o["sy"] == py:
                        oid = i
                        break
                if oid is not None:
                    self.current_level.remove_sprite(parcel_here)
                    self._orders[oid]["phase"] = "carried"
                    self._carrying_oid = oid
            elif self._carrying_oid is not None and customer_here:
                want = int(customer_here.pixels[0][0])
                held = int(self._orders[self._carrying_oid]["color"])
                if want == held:
                    self._orders[self._carrying_oid]["phase"] = "done"
                    self._carrying_oid = None
            else:
                tgt = self._ping_target()
                if tgt:
                    self._ping_pos = self._grid_to_frame_pixel(tgt.x, tgt.y)
                    self._ping_frames = self.PING_FRAMES

            if self._pending_count() == 0 and self._carrying_oid is None:
                self.next_level()

            self._sync_ui()
            if self._burn():
                self.complete_action()
                return
            self._check_order_deadlines()
            self._sync_ui()
            self.complete_action()
            return

        self.complete_action()
