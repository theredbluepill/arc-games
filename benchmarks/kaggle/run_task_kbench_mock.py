#!/usr/bin/env python3
"""Run arc_ez01_go_up through the real @kbench.task wrapper with a mock LLM.

kaggle_benchmarks loads a default model at import time, which requires
MODEL_PROXY_URL, MODEL_PROXY_API_KEY, and LLM_DEFAULT. For local CI without
a real proxy, this module sets placeholder values only when unset so the
import succeeds; the task still uses MockLLM (no network).
"""

from __future__ import annotations

import os
import sys


def main() -> None:
    os.environ.setdefault(
        "MODEL_PROXY_URL", "https://mp-staging.kaggle.net/models/openapi"
    )
    os.environ.setdefault("MODEL_PROXY_API_KEY", "local-mock-not-for-production")
    os.environ.setdefault("LLM_DEFAULT", "google/gemini-2.5-flash")

    # Import after env so kaggle_benchmarks can initialize
    from benchmarks.run_task_test import MockLLM
    from benchmarks.kaggle.arc_ez01_task import arc_ez01_go_up

    run = arc_ez01_go_up.run(llm=MockLLM(), seed=0, max_steps=30)
    if run.status.name != "SUCCESS":
        print(f"FAIL: expected SUCCESS, got {run.status}", file=sys.stderr)
        sys.exit(1)
    print("OK: arc_ez01_go_up @kbench.task completed with MockLLM")


if __name__ == "__main__":
    main()
