"""Timed / survival stems (wave 3).

Product-graph search over ``(frame_or_hud_key, phase_counters)`` is stem-specific.
For stems that encode all salient state in the rendered frame (e.g. ``sv01`` meters in HUD),
``engine_bfs`` with larger ``max_depth`` / ``max_nodes`` is often sufficient.

Stems with reflex-only wins (``wm01``–``wm04``) remain ``tooling_gap`` until a discretized
hit-window model exists.
"""

from __future__ import annotations

SURVIVAL_INFLATED_STEMS: frozenset[str] = frozenset(
    {
        "sv01",
        "sv02",
        "sv03",
        "hd01",
        "tg01",
        "tm01",
    }
)

REFLEX_TOOLING_GAP_STEMS: frozenset[str] = frozenset(
    {
        "wm01",
        "wm02",
        "wm03",
        "wm04",
        "sg01",
        "sg04",
    }
)

WAVE3_REFLEX_NOTE = (
    "wave3_reflex: discrete timing/reflex policy not modeled; needs product graph on "
    "clock phase + UI state or manual certification."
)
