#!/usr/bin/env python3
"""Regenerate ``benchmarks/kaggle/notebooks/*.ipynb`` for Kaggle Benchmark (papermill) + local use.

- **Python 3.12+ kernel:** ``pip install`` + ``exec(TASK_SCRIPT)`` in-process.
- **Python 3.11 papermill workers:** ``pip install`` pinned ``uv`` (see ``UV_PIP_SPEC``) then
  ``uv run --python 3.12`` so ``arc-agi`` (PyPI ``requires-python >= 3.12``) runs in a 3.12 subprocess.

Template body is sliced from ``arc_kaggle_notebook_template.py``. Do **not** install PyPI
``kaggle-benchmarks`` in the uv subprocess: it pins ``hishel==0.1.5``, which conflicts with
``hishel.httpx`` required by ``/benchmarks/src/kaggle_benchmarks`` on the worker.

Usage::

    python3 benchmarks/kaggle/rebuild_kaggle_notebooks.py
"""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "arc_kaggle_notebook_template.py"
NOTEBOOK_DIR = ROOT / "notebooks"

# Pinned for reproducible ``pip install`` on Kaggle papermill (3.11) before ``uv run``.
UV_PIP_SPEC = "uv==0.10.11"


def base_task_script() -> str:
    text = TEMPLATE.read_text(encoding="utf-8")
    start = text.index("import sys\nfrom pathlib import Path")
    end = text.index("# --- Cell 3:")
    return text[start:end].rstrip()


CELL3 = "\n\n# --- Cell 3: Run one task (duplicate cell or notebook per task on Kaggle) ---\n"

NOTEBOOKS: list[dict[str, str]] = [
    {
        "filename": "arc-interactive-ez01-go-up.ipynb",
        "md": dedent(
            """
            # ARC benchmark: ez01 (Go Up)

            **Kernels:** On **Python 3.12+**, installs `arc-agi` / `arcengine` and runs in this session.
            **Kaggle Benchmark (papermill) on 3.11** cannot import `arc-agi`; this cell uses
            **`uv run --python 3.12`** to run the same code under 3.12 (needs network for the first run).

            Attach a dataset whose root contains **`environment_files/`** (see repo `benchmarks/kaggle/notebooks/README.md`).
            """
        ).strip(),
        "run": "arc_ez01_go_up.run(llm=kbench.llm, seed=0, max_steps=30)",
    },
    {
        "filename": "arc-interactive-sk01-sokoban.ipynb",
        "md": dedent(
            """
            # ARC benchmark: sk01 (Sokoban)

            **Kernels:** Same as ez01 notebook — **3.12+** in-process, **3.11** via **`uv run --python 3.12`**.

            Attach **`environment_files/`** via **+ Add data**.
            """
        ).strip(),
        "run": "arc_sk01_sokoban.run(llm=kbench.llm, seed=0, max_steps=200)",
    },
    {
        "filename": "arc-interactive-tt01-collect.ipynb",
        "md": dedent(
            """
            # ARC benchmark: tt01 (Collect)

            **Kernels:** Same as ez01 notebook — **3.12+** in-process, **3.11** via **`uv run --python 3.12`**.

            Attach **`environment_files/`** via **+ Add data**.
            """
        ).strip(),
        "run": "arc_tt01_collect.run(llm=kbench.llm, seed=0, max_steps=200)",
    },
    {
        "filename": "arc-interactive-sv01-survive.ipynb",
        "md": dedent(
            """
            # ARC benchmark: sv01 (Survive)

            **Kernels:** Same as ez01 notebook — **3.12+** in-process, **3.11** via **`uv run --python 3.12`**.

            Attach **`environment_files/`** via **+ Add data**.
            """
        ).strip(),
        "run": "arc_sv01_survive.run(llm=kbench.llm, seed=0, max_steps=80)",
    },
]


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
    footer = (
        "''').strip()\n"
        "\n"
        "\n"
        "def _bootstrap() -> None:\n"
        "    code = TASK_SCRIPT\n"
        "    work = Path(\"/kaggle/working\")\n"
        "    if not work.is_dir():\n"
        "        work = Path(tempfile.gettempdir())\n"
        "    out = work / \"_arc_benchmark_task.py\"\n"
        "    out.write_text(code, encoding=\"utf-8\")\n"
        "    env = os.environ.copy()\n"
        "\n"
        "    if sys.version_info >= (3, 12):\n"
        "        subprocess.check_call(\n"
        "            [\n"
        "                sys.executable,\n"
        "                \"-m\",\n"
        "                \"pip\",\n"
        "                \"install\",\n"
        "                \"-q\",\n"
        "                \"arc-agi\",\n"
        "                \"arcengine\",\n"
        "                \"numpy\",\n"
        "                \"hishel[httpx]>=1.1\",\n"
        "                \"openai\",\n"
        "                \"google-genai\",\n"
        "                \"panel\",\n"
        "                \"docker\",\n"
        "                \"protobuf\",\n"
        "            ],\n"
        "            env=env,\n"
        "        )\n"
        "        exec(compile(code, str(out), \"exec\"), {\"__name__\": \"__main__\"})\n"
        "        return\n"
        "\n"
        "    subprocess.check_call(\n"
        f'        [sys.executable, \"-m\", \"pip\", \"install\", \"-q\", \"{UV_PIP_SPEC}\"],\n'
        "        env=env,\n"
        "    )\n"
        "    subprocess.check_call(\n"
        "        [\n"
        "            sys.executable,\n"
        "            \"-m\",\n"
        "            \"uv\",\n"
        "            \"run\",\n"
        "            \"--python\",\n"
        "            \"3.12\",\n"
        "            \"--with\",\n"
        "            \"arc-agi\",\n"
        "            \"--with\",\n"
        "            \"arcengine\",\n"
        "            \"--with\",\n"
        "            \"numpy\",\n"
        "            \"--with\",\n"
        "            \"hishel[httpx]>=1.1\",\n"
        "            \"--with\",\n"
        "            \"openai\",\n"
        "            \"--with\",\n"
        "            \"google-genai\",\n"
        "            \"--with\",\n"
        "            \"panel\",\n"
        "            \"--with\",\n"
        "            \"docker\",\n"
        "            \"--with\",\n"
        "            \"protobuf\",\n"
        "            \"python\",\n"
        "            str(out),\n"
        "        ],\n"
        "        env=env,\n"
        "    )\n"
        "\n"
        "\n"
        "_bootstrap()\n"
    )
    task = task_py if task_py.endswith("\n") else task_py + "\n"
    return header + task + footer


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
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    base = base_task_script()
    for spec in NOTEBOOKS:
        task_py = base + CELL3 + spec["run"] + "\n"
        code = bootstrap_cell_from_task(task_py)
        nb = build_notebook(spec["md"], code)
        path = NOTEBOOK_DIR / spec["filename"]
        path.write_text(json.dumps(nb, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
