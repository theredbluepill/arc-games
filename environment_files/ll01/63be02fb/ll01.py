"""Generations lock: toggle cells with ACTION6; ACTION5 runs one Conway generation. After exactly N advances, the live set must match the target.

Goal cues (HUD / overlay): light-gray rectangle + light-magenta pin per remaining 2×2 target block (see bottom legend); hidden once that block is fully live.
"""

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
CAM_W = CAM_H = 32
LIVE_C = 14
WALL_C = 3
# Goal hints (subtle): dim frame + anchor pin per authored 2×2 target block
HINT_FRAME_C = 2
HINT_ANCHOR_C = 7


class Ll01UI(RenderableUserDisplay):
    def __init__(
        self,
        gen: int,
        need: int,
        toggles: int,
        anchors: list[tuple[int, int]],
        alive: set[tuple[int, int]],
    ) -> None:
        self._gen = gen
        self._need = need
        self._toggles = toggles
        self._anchors = anchors
        self._alive = alive

    def update(
        self,
        gen: int,
        need: int,
        toggles: int,
        anchors: list[tuple[int, int]],
        alive: set[tuple[int, int]],
    ) -> None:
        self._gen = gen
        self._need = need
        self._toggles = toggles
        self._anchors = anchors
        self._alive = alive

    @staticmethod
    def _plot(frame, h: int, w: int, fx: int, fy: int, c: int) -> None:
        if 0 <= fx < w and 0 <= fy < h:
            frame[fy, fx] = c

    def _draw_goal_hints(self, frame, h: int, w: int) -> None:
        scale = min(64 // CAM_W, 64 // CAM_H)
        pad_x = (w - CAM_W * scale) // 2
        pad_y = (h - CAM_H * scale) // 2

        for ax, ay in self._anchors:
            block = {(ax, ay), (ax + 1, ay), (ax, ay + 1), (ax + 1, ay + 1)}
            if block <= self._alive:
                continue
            x0 = pad_x + ax * scale
            y0 = pad_y + ay * scale
            x1 = x0 + 2 * scale - 1
            y1 = y0 + 2 * scale - 1
            for fx in range(x0, x1 + 1):
                self._plot(frame, h, w, fx, y0, HINT_FRAME_C)
                self._plot(frame, h, w, fx, y1, HINT_FRAME_C)
            for fy in range(y0, y1 + 1):
                self._plot(frame, h, w, x0, fy, HINT_FRAME_C)
                self._plot(frame, h, w, x1, fy, HINT_FRAME_C)
            pin_x = x0 + scale // 2
            pin_y = y0 + scale // 2
            self._plot(frame, h, w, pin_x, pin_y, HINT_ANCHOR_C)

    def render_interface(self, frame):
        import numpy as np

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape
        self._draw_goal_hints(frame, h, w)
        for i in range(min(self._need, 12)):
            frame[h - 2, 1 + i * 2] = 11 if i < self._gen else 2
        for i in range(min(self._toggles, 20)):
            frame[h - 1, 1 + i] = 9
        # Tiny legend: magenta pin · dim frame (only if any hint may show)
        if self._anchors:
            frame[h - 3, 1] = HINT_ANCHOR_C
            frame[h - 3, 2] = HINT_FRAME_C
        return frame


sprites = {
    "wall": Sprite(
        pixels=[[WALL_C]],
        name="wall",
        visible=True,
        collidable=True,
        tags=["wall"],
    ),
    "live": Sprite(
        pixels=[[LIVE_C]],
        name="live",
        visible=True,
        collidable=False,
        tags=["live"],
    ),
}


def mk(
    walls: list[tuple[int, int]],
    target: list[tuple[int, int]],
    need_gens: int,
    max_toggles: int,
    diff: int,
    target_anchors: list[tuple[int, int]],
) -> Level:
    sl: list[Sprite] = []
    for wx, wy in walls:
        sl.append(sprites["wall"].clone().set_position(wx, wy))
    return Level(
        sprites=sl,
        grid_size=(CAM_W, CAM_H),
        data={
            "difficulty": diff,
            "target_cells": [list(p) for p in target],
            "target_anchors": [list(p) for p in target_anchors],
            "need_generations": need_gens,
            "max_toggles": max_toggles,
        },
    )


def _block(ax: int, ay: int) -> list[tuple[int, int]]:
    return [(ax, ay), (ax + 1, ay), (ax, ay + 1), (ax + 1, ay + 1)]


def _pit_walls_around_block(ax: int, ay: int) -> list[tuple[int, int]]:
    """Walls on a 4×4 ring; interior is exactly the 2×2 at (ax, ay)..(ax+1, ay+1) (no goal overlay)."""
    out: list[tuple[int, int]] = []
    for x in range(ax - 1, ax + 3):
        for y in range(ay - 1, ay + 3):
            if not (ax <= x <= ax + 1 and ay <= y <= ay + 1):
                out.append((x, y))
    return out


def _merge_walls(*chunks: list[tuple[int, int]]) -> list[tuple[int, int]]:
    s: set[tuple[int, int]] = set()
    for ch in chunks:
        s.update(ch)
    return sorted(s)


# Stable 2×2 blocks; after each generation the pattern is unchanged if it matches the block.
# Difficulty ramps: more generations, tighter toggle budgets, busier topology, extra targets.
levels = [
    # Level 1: single pit (tutorial).
    mk(_pit_walls_around_block(15, 15), _block(15, 15), 2, 52, 1, [(15, 15)]),
    # Level 2: barrier + clutter below; must commit to more CA steps.
    mk(
        [(x, 14) for x in range(10, 22)]
        + [(12, y) for y in range(16, 22)]
        + [(19, y) for y in range(16, 21)],
        _block(18, 10),
        3,
        78,
        2,
        [(18, 10)],
    ),
    # Level 3: two close blocks (one-cell gutter); more generations.
    mk([], _block(6, 6) + _block(10, 6), 4, 112, 3, [(6, 6), (10, 6)]),
    # Level 4: tall splitter wall; target in a side pocket.
    mk([(16, y) for y in range(32) if 8 <= y <= 22], _block(22, 12), 4, 138, 4, [(22, 12)]),
    # Level 5: diagonal pair + mid-field wall to damp accidental traffic.
    mk(
        [(x, 16) for x in range(12, 20)],
        _block(5, 5) + _block(25, 25),
        5,
        175,
        5,
        [(5, 5), (25, 25)],
    ),
    # Level 6: three isolated pits — twelve exact cells, long run of steps, lean toggle budget.
    mk(
        _merge_walls(
            _pit_walls_around_block(4, 4),
            _pit_walls_around_block(15, 15),
            _pit_walls_around_block(26, 26),
        ),
        _block(4, 4) + _block(15, 15) + _block(26, 26),
        6,
        42,
        6,
        [(4, 4), (15, 15), (26, 26)],
    ),
]


class Ll01(ARCBaseGame):
    def __init__(self) -> None:
        self._ui = Ll01UI(0, 1, 0, [], set())
        super().__init__(
            "ll01",
            levels,
            Camera(0, 0, CAM_W, CAM_H, BACKGROUND_COLOR, PADDING_COLOR, [self._ui]),
            False,
            1,
            [1, 2, 3, 4, 5, 6],
        )

    def on_set_level(self, level: Level) -> None:
        raw = self.current_level.get_data("target_cells") or []
        self._target = {tuple(int(t) for t in p) for p in raw}
        ar = self.current_level.get_data("target_anchors") or []
        self._anchors = [tuple(int(t) for t in p) for p in ar]
        self._need = int(self.current_level.get_data("need_generations") or 1)
        self._tog_left = int(self.current_level.get_data("max_toggles") or 100)
        self._gen_count = 0
        self._sync_ui()

    def _alive(self) -> set[tuple[int, int]]:
        return {(s.x, s.y) for s in self.current_level.get_sprites_by_tag("live")}

    def _sync_ui(self) -> None:
        self._ui.update(
            self._gen_count,
            self._need,
            self._tog_left,
            self._anchors,
            self._alive(),
        )

    def _neighbors(self, x: int, y: int) -> int:
        c = 0
        for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
            if (x + dx, y + dy) in self._alive():
                c += 1
        return c

    def _step_conway(self) -> None:
        gw, gh = self.current_level.grid_size
        cur = self._alive()
        nxt: set[tuple[int, int]] = set()
        for y in range(gh):
            for x in range(gw):
                sp = self.current_level.get_sprite_at(x, y, ignore_collidable=True)
                if sp and "wall" in sp.tags:
                    continue
                n = self._neighbors(x, y)
                live = (x, y) in cur
                if live and n in (2, 3):
                    nxt.add((x, y))
                elif not live and n == 3:
                    nxt.add((x, y))
        for s in list(self.current_level.get_sprites_by_tag("live")):
            self.current_level.remove_sprite(s)
        for x, y in nxt:
            self.current_level.add_sprite(sprites["live"].clone().set_position(x, y))

    def step(self) -> None:
        aid = self.action.id

        if aid in (
            GameAction.ACTION1,
            GameAction.ACTION2,
            GameAction.ACTION3,
            GameAction.ACTION4,
        ):
            self.complete_action()
            return

        if aid == GameAction.ACTION5:
            self._step_conway()
            self._gen_count += 1
            self._sync_ui()
            if self._gen_count == self._need:
                if self._alive() == self._target:
                    self.next_level()
                else:
                    self.lose()
            elif self._gen_count > self._need:
                self.lose()
            self.complete_action()
            return

        if aid != GameAction.ACTION6:
            self.complete_action()
            return

        if self._tog_left <= 0:
            self.complete_action()
            return

        x = self.action.data.get("x", 0)
        y = self.action.data.get("y", 0)
        coords = self.camera.display_to_grid(x, y)
        if coords is None:
            self.complete_action()
            return
        gx, gy = coords
        gw, gh = self.current_level.grid_size
        if not (0 <= gx < gw and 0 <= gy < gh):
            self.complete_action()
            return

        sp = self.current_level.get_sprite_at(gx, gy, ignore_collidable=True)
        if sp and "wall" in sp.tags:
            self.complete_action()
            return

        hit = next(
            (s for s in self.current_level.get_sprites_by_tag("live") if s.x == gx and s.y == gy),
            None,
        )
        if hit:
            self.current_level.remove_sprite(hit)
        else:
            self.current_level.add_sprite(sprites["live"].clone().set_position(gx, gy))

        self._tog_left -= 1
        self._sync_ui()
        self.complete_action()
