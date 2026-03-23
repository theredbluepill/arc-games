from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class VerdictStatus(StrEnum):
    PROVED = "proved"
    COUNTEREXAMPLE = "counterexample"
    UNKNOWN = "unknown"
    TOOLING_GAP = "tooling_gap"
    ERROR = "error"


@dataclass
class LevelVerdict:
    stem: str
    level_index: int
    status: VerdictStatus
    solver: str
    notes: str = ""
    nodes_expanded: int = 0
    depth: int | None = None
    extra: dict[str, Any] = field(default_factory=dict)
