#!/usr/bin/env python3
"""Run all ARC @kbench.task entries with mock LLMs (no Model Proxy calls)."""

from __future__ import annotations

import os
import sys


def main() -> None:
    os.environ.setdefault(
        "MODEL_PROXY_URL", "https://mp-staging.kaggle.net/models/openapi"
    )
    os.environ.setdefault("MODEL_PROXY_API_KEY", "local-mock-not-for-production")
    os.environ.setdefault("LLM_DEFAULT", "google/gemini-2.5-flash")

    from benchmarks.kaggle.arc_tasks import (
        MOCK_SK01_L1_DIGITS,
        MOCK_SV01_L1_DIGITS,
        MOCK_TT01_L1_DIGITS,
        arc_ez01_go_up,
        arc_sk01_sokoban,
        arc_sv01_survive,
        arc_tt01_collect,
    )
    from benchmarks.mock_llms import ReplayMockLLM
    from benchmarks.run_task_test import MockLLM

    cases: list[tuple[str, object, dict]] = [
        (
            "arc_ez01_go_up",
            arc_ez01_go_up,
            {"llm": MockLLM(), "seed": 0, "max_steps": 30},
        ),
        (
            "arc_sk01_sokoban",
            arc_sk01_sokoban,
            {
                "llm": ReplayMockLLM(MOCK_SK01_L1_DIGITS, "1"),
                "seed": 0,
                "max_steps": 24,
            },
        ),
        (
            "arc_tt01_collect",
            arc_tt01_collect,
            {
                "llm": ReplayMockLLM(MOCK_TT01_L1_DIGITS, "1"),
                "seed": 0,
                "max_steps": 20,
            },
        ),
        (
            "arc_sv01_survive",
            arc_sv01_survive,
            {
                "llm": ReplayMockLLM(MOCK_SV01_L1_DIGITS, "5"),
                "seed": 0,
                "max_steps": 70,
            },
        ),
    ]

    for name, task, kwargs in cases:
        run = task.run(**kwargs)
        if run.status.name != "SUCCESS":
            print(f"FAIL: {name} -> {run.status}", file=sys.stderr)
            sys.exit(1)
        print(f"OK: {name}")

    print("OK: all arc @kbench.task mocks passed")


if __name__ == "__main__":
    main()
