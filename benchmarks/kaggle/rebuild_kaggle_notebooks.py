#!/usr/bin/env python3
"""Regenerate ``benchmarks/kaggle/notebooks/*.ipynb`` for Kaggle Notebook (Python **3.12**).

Bootstrap: ``pip install`` worker packages (see ``PIP_PKGS_KAGGLE_WORKER``), then
``exec(TASK_SCRIPT)`` in-process. No ``uv`` subprocess.

Template body is sliced from ``arc_kaggle_notebook_template.py``. Do **not** install PyPI
``kaggle-benchmarks`` in pip alongside conflicting pins; the worker injects
``/benchmarks/src/kaggle_benchmarks``.

Usage::

    python3 benchmarks/kaggle/rebuild_kaggle_notebooks.py

Extra deps mirror PyPI ``kaggle-benchmarks`` where the worker’s injected source imports them.
Use ``google-genai`` only (not the ``google`` metapackage) for ``from google import genai``.

Playwright may still need ``playwright install`` (browser binaries) if a code path uses it.
"""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "arc_kaggle_notebook_template.py"
NOTEBOOK_DIR = ROOT / "notebooks"

BOOTSTRAP_TAG = "[arc-benchmark-bootstrap]"

# Packages installed by the notebook bootstrap before ``exec(TASK_SCRIPT)`` (Kaggle Notebook 3.12).
PIP_PKGS_KAGGLE_WORKER: tuple[str, ...] = (
    "arc-agi",
    "arcengine",
    "numpy",
    "hishel[httpx]>=1.1",
    "openai",
    "google-genai",
    "panel",
    "docker",
    "protobuf",
    "joblib",
    "jupyter-client",
    "nest-asyncio",
    "playwright",
    "ipython",
)


def base_taskscript_body() -> str:
    text = TEMPLATE.read_text(encoding="utf-8")
    start = text.index("import sys\nfrom pathlib import Path")
    end = text.index("# --- Cell 3:")
    return text[start:end].rstrip()


CELL3 = "\n\n# --- Cell 3: Run one task (duplicate cell or notebook per task on Kaggle) ---\n"

# Shared opening for benchmark notebooks (export script imports this).
SECTION_12_MARKDOWN = dedent(
    """
    ## 1. What for?

    > The intelligence of a system is a measure of its skill-acquisition efficiency over a scope of tasks, with respect to priors, experience, and generalization difficulty.
    > — François Chollet, *[On the Measure of Intelligence](https://arxiv.org/abs/1911.01547)* (2019)

    These games stress **reasoning, planning, and interactive control**—easy for many humans, hard for typical LLMs—rather than memorized templates. Same idea as **[ARC-AGI-3](https://arcprize.org/arc-agi/3/)**: **action efficiency** and generalization matter.

    ## 2. Why use ARC-Interactive?

    - **250+** games in **[GAMES.md](https://github.com/theredbluepill/arc-interactive/blob/main/GAMES.md)** alongside the [official ARC-AGI-3 list](https://docs.arcprize.org/available-games).
    - Patterns in **[AGENTS.md](https://github.com/theredbluepill/arc-interactive/blob/main/AGENTS.md)** and skills under **[`.opencode/skills/`](https://github.com/theredbluepill/arc-interactive/tree/main/.opencode/skills)** (mirrored [`skills/`](https://github.com/theredbluepill/arc-interactive/tree/main/skills/)).
    - Contribute via **[CONTRIBUTING.md](https://github.com/theredbluepill/arc-interactive/blob/main/CONTRIBUTING.md#creating-a-new-game)**.
    """
).strip()


NOTEBOOKS: list[dict[str, str]] = [
    {
        "filename": "arc-interactive-ez01-go-up.ipynb",
        "md": dedent(
            f"""
            {SECTION_12_MARKDOWN}

            ---

            # ARC benchmark: ez01 (Go Up)

            **Kernel:** Python **3.12** (Kaggle Notebook). The code cell installs dependencies with `pip`, then runs the task.

            Attach a dataset whose root contains **`environment_files/`**. Load games with [`Arcade`](https://docs.arcprize.org/toolkit/arc_agi) and `environments_dir` pointing at that tree (`OperationMode.OFFLINE` for local only).

            See `benchmarks/kaggle/notebooks/README.md` for details.
            """
        ).strip(),
        "run": "arc_ez01_go_up.run(llm=kbench.llm, seed=0, max_steps=30)",
    },
    {
        "filename": "arc-interactive-sk01-sokoban.ipynb",
        "md": dedent(
            f"""
            {SECTION_12_MARKDOWN}

            ---

            # ARC benchmark: sk01 (Sokoban)

            **Kernel:** Python **3.12** (Kaggle Notebook). Attach **`environment_files/`** via **+ Add data**.

            [`Arcade`](https://docs.arcprize.org/toolkit/arc_agi) + `OperationMode.OFFLINE` + local `environments_dir`.
            """
        ).strip(),
        "run": "arc_sk01_sokoban.run(llm=kbench.llm, seed=0, max_steps=200)",
    },
    {
        "filename": "arc-interactive-tt01-collect.ipynb",
        "md": dedent(
            f"""
            {SECTION_12_MARKDOWN}

            ---

            # ARC benchmark: tt01 (Collect)

            **Kernel:** Python **3.12** (Kaggle Notebook). Attach **`environment_files/`** via **+ Add data**.

            [`Arcade`](https://docs.arcprize.org/toolkit/arc_agi) + `OperationMode.OFFLINE` + local `environments_dir`.
            """
        ).strip(),
        "run": "arc_tt01_collect.run(llm=kbench.llm, seed=0, max_steps=200)",
    },
    {
        "filename": "arc-interactive-sv01-survive.ipynb",
        "md": dedent(
            f"""
            {SECTION_12_MARKDOWN}

            ---

            # ARC benchmark: sv01 (Survive)

            **Kernel:** Python **3.12** (Kaggle Notebook). Attach **`environment_files/`** via **+ Add data**.

            [`Arcade`](https://docs.arcprize.org/toolkit/arc_agi) + `OperationMode.OFFLINE` + local `environments_dir`.
            """
        ).strip(),
        "run": "arc_sv01_survive.run(llm=kbench.llm, seed=0, max_steps=80)",
    },
]


def _bootstrap_cell_source_lines() -> list[str]:
    """Lines of Python source for ``_bootstrap()`` embedded in the notebook (no leading cell header)."""
    tag = BOOTSTRAP_TAG
    lines: list[str] = [
        "def _bootstrap() -> None:",
        "    def _log(msg: str) -> None:",
        f'        print("{tag}", msg, flush=True)',
        "",
        '    _log("start")',
        "    code = TASK_SCRIPT",
        '    work = Path("/kaggle/working")',
        "    if not work.is_dir():",
        "        work = Path(tempfile.gettempdir())",
        '    out = work / "_arc_benchmark_task.py"',
        '    _log(f"writing task script -> {out} ({len(code)} chars)")',
        "    out.write_text(code, encoding=\"utf-8\")",
        "    env = os.environ.copy()",
        '    _log(f"kernel {sys.version_info.major}.{sys.version_info.minor} exec={sys.executable}")',
        "",
        '    _log("pip install worker deps (Kaggle Notebook 3.12)")',
        "    subprocess.check_call(",
        "        [",
        "            sys.executable,",
        '            "-m",',
        '            "pip",',
        '            "install",',
    ]
    for pkg in PIP_PKGS_KAGGLE_WORKER:
        lines.append(f'            "{pkg}",')
    lines.extend(
        [
            "        ],",
            "        env=env,",
            "    )",
            '    _log("pip finished; exec TASK_SCRIPT as __main__")',
            '    exec(compile(code, str(out), "exec"), {"__name__": "__main__"})',
            '    _log("exec returned")',
        ]
    )
    return lines


def bootstrap_cell_from_task(task_py: str) -> str:
    if "'''" in task_py:
        raise ValueError("task source must not contain ''' — use \"\"\" in docstrings only")

    header = (
        "import os\n"
        "import subprocess\n"
        "import sys\n"
        "import tempfile\n"
        "import textwrap\n"
        "from pathlib import Path\n"
        "\n"
        "TASK_SCRIPT = textwrap.dedent(r'''\n"
    )
    mid = "".join(task_py if task_py.endswith("\n") else task_py + "\n")
    foot_close = "''').strip()\n\n\n"
    boot_lines = "\n".join(_bootstrap_cell_source_lines()) + "\n\n\n_bootstrap()\n"
    return header + mid + foot_close + boot_lines


def to_ipynb_lines(src: str) -> list[str]:
    if not src:
        return []
    return [ln + "\n" for ln in src.split("\n")]


def build_notebook(md: str, code: str) -> dict:
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": to_ipynb_lines(md),
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": to_ipynb_lines(code),
                "outputs": [],
                "execution_count": None,
            },
        ],
    }


def main() -> None:
    print("[rebuild_kaggle_notebooks]", "template:", TEMPLATE, flush=True)
    print("[rebuild_kaggle_notebooks]", "worker pip packages:", len(PIP_PKGS_KAGGLE_WORKER), flush=True)
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    base = base_taskscript_body()
    for spec in NOTEBOOKS:
        task_py = base + CELL3 + spec["run"] + "\n"
        code = bootstrap_cell_from_task(task_py)
        nb = build_notebook(spec["md"], code)
        path = NOTEBOOK_DIR / spec["filename"]
        path.write_text(json.dumps(nb, indent=1) + "\n", encoding="utf-8")
        print("[rebuild_kaggle_notebooks] wrote", path, f"({len(code)} chars code cell)", flush=True)


if __name__ == "__main__":
    main()
