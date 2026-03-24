"""sg04: dual score arms — ACTION5 commits +1 to arm A or B alternating."""

from __future__ import annotations

from arcengine import ARCBaseGame, Camera, GameAction, Level, RenderableUserDisplay

BG, PAD = 5, 4


class Sg04UI(RenderableUserDisplay):
    def __init__(
        self,
        a: int,
        b: int,
        ta: int,
        tb: int,
        next_arm: int = 0,
        *,
        left: int = 0,
        max_steps: int = 1,
    ) -> None:
        self._a, self._b, self._ta, self._tb = a, b, ta, tb
        self._next = next_arm
        self._left = left
        self._max_steps = max(1, max_steps)

    def update(
        self,
        a: int,
        b: int,
        ta: int,
        tb: int,
        next_arm: int | None = None,
        *,
        left: int | None = None,
        max_steps: int | None = None,
    ) -> None:
        self._a, self._b, self._ta, self._tb = a, b, ta, tb
        if next_arm is not None:
            self._next = next_arm
        if left is not None:
            self._left = left
        if max_steps is not None:
            self._max_steps = max(1, max_steps)

    def render_interface(self, frame):
        import numpy as np

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape
        ms = self._max_steps
        lv = max(0, self._left)
        # Eight segments: how many still "charged" (learnable commit budget).
        n_budget = min(8, (lv * 8 + ms - 1) // ms) if ms else 0
        for i in range(min(8, w - 1)):
            frame[h - 4, 1 + i] = 10 if i < n_budget else 3
        frame[h - 3, 0] = 14 if self._next == 0 else 11
        for i in range(min(self._ta, 8)):
            frame[h - 2, 1 + i] = 14 if i < self._a else 4
        for i in range(min(self._tb, 8)):
            frame[h - 1, 1 + i] = 11 if i < self._b else 4
        return frame


def mk(ta: int, tb: int, max_steps: int, d: int) -> Level:
    return Level(
        sprites=[],
        grid_size=(8, 8),
        data={"ta": ta, "tb": tb, "max_steps": max_steps, "difficulty": d},
    )


levels = [
    mk(3, 3, 30, 1),
    mk(4, 2, 35, 2),
    mk(2, 5, 40, 3),
    mk(5, 5, 50, 4),
    mk(3, 6, 55, 5),
    mk(6, 3, 60, 6),
    mk(4, 4, 45, 7),
]


class Sg04(ARCBaseGame):
    def __init__(self) -> None:
        self._hud = Sg04UI(0, 0, 1, 1, 0, left=0, max_steps=1)
        super().__init__(
            "sg04",
            levels,
            Camera(0, 0, 8, 8, BG, PAD, [self._hud]),
            False,
            1,
            [5],
        )

    def on_set_level(self, level: Level) -> None:
        self._ta = int(level.get_data("ta") or 3)
        self._tb = int(level.get_data("tb") or 3)
        self._a = self._b = 0
        self._arm = 0
        self._max_steps = int(level.get_data("max_steps") or 40)
        self._left = self._max_steps
        self._hud.update(
            self._a,
            self._b,
            self._ta,
            self._tb,
            self._arm,
            left=self._left,
            max_steps=self._max_steps,
        )

    def step(self) -> None:
        if self.action.id == GameAction.ACTION5:
            if self._left <= 0:
                self._hud.update(
                    self._a,
                    self._b,
                    self._ta,
                    self._tb,
                    self._arm,
                    left=0,
                    max_steps=self._max_steps,
                )
                self.lose()
                self.complete_action()
                return
            self._left -= 1
            if self._arm == 0 and self._a < self._ta:
                self._a += 1
            elif self._arm == 1 and self._b < self._tb:
                self._b += 1
            self._arm = 1 - self._arm
            self._hud.update(
                self._a,
                self._b,
                self._ta,
                self._tb,
                self._arm,
                left=self._left,
                max_steps=self._max_steps,
            )
            if self._a >= self._ta and self._b >= self._tb:
                self.next_level()
            self.complete_action()
            return
        self.complete_action()
