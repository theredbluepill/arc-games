"""
Kaggle benchmark task: ARC-AGI-3 ez01 (Go Up).

Re-exports the shared task from ``arc_tasks`` so existing imports and
``python -m benchmarks.kaggle.arc_ez01_task`` keep working.
"""

from __future__ import annotations

from benchmarks.kaggle.arc_tasks import arc_ez01_go_up

__all__ = ["arc_ez01_go_up"]

if __name__ == "__main__":
    import kaggle_benchmarks as kbench

    arc_ez01_go_up.run(llm=kbench.llm, seed=0, max_steps=30)
