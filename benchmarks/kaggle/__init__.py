"""Kaggle benchmark tasks for ARC-AGI-3 games.

Imports from ``kaggle_benchmarks`` happen only when task symbols are accessed, so
``python -m benchmarks.kaggle.run_task_kbench_mock`` can set proxy env defaults first.
"""

from __future__ import annotations

__all__ = [
    "ARC_TASK_NAMES",
    "arc_ez01_go_up",
    "arc_sk01_sokoban",
    "arc_tt01_collect",
    "arc_sv01_survive",
]


def __getattr__(name: str):
    if name in __all__:
        from benchmarks.kaggle import arc_tasks

        return getattr(arc_tasks, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted({*globals(), *__all__})
