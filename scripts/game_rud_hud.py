"""Shared minimal HUD drawing for environment `RenderableUserDisplay` classes.

Environment games load this file via ``importlib`` (see ``_grh()`` helper in each stem).
"""

from __future__ import annotations

from typing import Any


def plot(frame: Any, h: int, w: int, x: int, y: int, c: int) -> None:
    if 0 <= x < w and 0 <= y < h:
        frame[y, x] = c


def draw_level_dots(
    frame: Any, h: int, w: int, level_index: int, num_levels: int, y: int = 0
) -> None:
    """One marker per level: done=green, current=yellow, future=gray."""
    cap = min(num_levels, 14)
    for i in range(cap):
        cx = 1 + i * 2
        if cx >= w:
            break
        if i < level_index:
            c = 14
        elif i == level_index:
            c = 11
        else:
            c = 3
        plot(frame, h, w, cx, y, c)


def draw_target_ticks(
    frame: Any, h: int, w: int, targets_remaining: int, max_ticks: int = 8, y: int | None = None
) -> None:
    row = (h - 1) if y is None else y
    n = max(0, min(targets_remaining, max_ticks))
    for i in range(n):
        plot(frame, h, w, 1 + i, row, 11)


def draw_extra_ticks(
    frame: Any,
    h: int,
    w: int,
    value: int,
    max_ticks: int,
    y: int | None = None,
    filled_color: int = 10,
    empty_color: int = 3,
) -> None:
    """Generic horizontal tick bar (e.g. budget, moves)."""
    row = (h - 2) if y is None else y
    cap = min(max_ticks, max(0, w - 2))
    v = max(0, min(value, cap))
    for i in range(cap):
        plot(frame, h, w, 1 + i, row, filled_color if i < v else empty_color)


def draw_game_state_bar(
    frame: Any, h: int, w: int, *, game_over: bool, win: bool, row: int | None = None
) -> None:
    r = (h - 3) if row is None else row
    if not (game_over or win) or r < 0 or r >= h:
        return
    c = 14 if win else 8
    for x in range(min(w, 16)):
        plot(frame, h, w, x, r, c)


def draw_click_ring(
    frame: Any,
    h: int,
    w: int,
    cx: int,
    cy: int,
    *,
    phase: int,
    radius_mod: int = 4,
    color: int = 12,
) -> None:
    r = (phase % radius_mod) + 1
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if max(abs(dx), abs(dy)) != r:
                continue
            plot(frame, h, w, cx + dx, cy + dy, color)


def draw_click_plus(
    frame: Any, h: int, w: int, cx: int, cy: int, arm: int = 2, color: int = 11
) -> None:
    for d in range(-arm, arm + 1):
        plot(frame, h, w, cx + d, cy, color)
        plot(frame, h, w, cx, cy + d, color)
