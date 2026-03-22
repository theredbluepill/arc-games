"""Strict solvability for partially observable / hidden-layout stems (wave 4).

These games require either enumerating hidden worlds consistent with observations,
or author-time witnesses. The harness reports ``unknown`` with a fixed criteria note.
"""

from __future__ import annotations

from .types import LevelVerdict, VerdictStatus

# Minesweepers, beacons, fog-of-war style hidden boards.
PARTIAL_OBS_STEMS: frozenset[str] = frozenset(
    {
        "ms01",
        "ms02",
        "ms03",
        "ms04",
        "bn01",
        "bn02",
        "bn03",
        "bn04",
        "fg01",
        "ng01",
    }
)

WAVE4_NOTE = (
    "wave4_partial_obs: verifier needs hidden-layout enumeration or author-time "
    "unique-solution witness; not automated in this harness."
)


def partial_obs_verdict(stem: str, level_index: int) -> LevelVerdict:
    return LevelVerdict(
        stem=stem,
        level_index=level_index,
        status=VerdictStatus.UNKNOWN,
        solver="partial_obs",
        notes=WAVE4_NOTE,
        extra={"criteria": "existential_quantify_hidden_state_or_csp"},
    )
