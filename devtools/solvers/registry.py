"""Map stems to verification strategies."""

from __future__ import annotations

from enum import Enum

from .partial_obs import PARTIAL_OBS_STEMS
from .survival_wave3 import REFLEX_TOOLING_GAP_STEMS, SURVIVAL_INFLATED_STEMS


class SolverKind(str, Enum):
    ENGINE_BFS = "engine_bfs"
    ENGINE_BFS_ACTION6_ONLY = "engine_bfs_action6_only"
    PUSH = "push"
    PB03 = "pb03"
    SWITCH_ALL = "switch_all"
    SWITCH_OR = "switch_or"
    SWITCH_K = "switch_k"
    PARTIAL_OBS = "partial_obs"
    TOOLING_GAP = "tooling_gap"
    STOCHASTIC_GAP = "stochastic_gap"
    PLANNER_GAP = "planner_gap"


STOCHASTIC_STEMS: frozenset[str] = frozenset({"tb03"})

# Multi-objective / routing / placement beyond cheap frame BFS (false exhaust risk).
PLANNER_TOOLING_STEMS: frozenset[str] = frozenset(
    {
        "as01",
        "bp01",
        "cr01",
        "dd01",
        "es01",
        "fc01",
        "mc01",
        "ob01",
        "rn01",
        "tb01",
        "tb02",
        "wl01",
        "wp01",
        "zm01",
        "zm04",
    }
)

PLANNER_NOTE = (
    "planner_tooling: logistics / multi-agent / bridge routing needs dedicated "
    "search model; skipped generic frame BFS to avoid false counterexamples."
)

# Games documented as using RNG for layout / spawns in ways that strict fixed-seed
# exhaustiveness has not been wired here.
STOCHASTIC_NOTE = (
    "stochastic: strict proof requires fixed-seed outcome exhaustiveness or "
    "deterministic redesign; not implemented in this harness."
)


def solver_kind_for_stem(stem: str) -> SolverKind:
    if stem in PARTIAL_OBS_STEMS:
        return SolverKind.PARTIAL_OBS
    if stem in REFLEX_TOOLING_GAP_STEMS:
        return SolverKind.TOOLING_GAP
    if stem in STOCHASTIC_STEMS:
        return SolverKind.STOCHASTIC_GAP
    if stem in PLANNER_TOOLING_STEMS:
        return SolverKind.PLANNER_GAP
    if stem == "pb03":
        return SolverKind.PB03
    if stem in {"sk01", "sk02", "pb01", "pb02"}:
        return SolverKind.PUSH
    if stem == "fs01":
        return SolverKind.SWITCH_ALL
    if stem == "fs02":
        return SolverKind.SWITCH_OR
    if stem == "fs03":
        return SolverKind.SWITCH_K
    if stem.startswith("lo") and stem[2:].isdigit():
        return SolverKind.ENGINE_BFS_ACTION6_ONLY
    if stem.startswith("gp") and stem[2:].isdigit():
        return SolverKind.ENGINE_BFS_ACTION6_ONLY
    if stem.startswith("ff") and stem[2:].isdigit():
        return SolverKind.ENGINE_BFS_ACTION6_ONLY
    return SolverKind.ENGINE_BFS


def engine_bfs_limits(stem: str, *, quick: bool = False) -> tuple[int, int, int]:
    """Return (max_nodes, max_depth, max_click_cells)."""
    if stem in SURVIVAL_INFLATED_STEMS:
        return (400_000, 180, 2500) if quick else (800_000, 220, 2500)
    return (120_000, 90, 2500) if quick else (250_000, 110, 2500)
