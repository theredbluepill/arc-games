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

# Pinned for reproducible ``pip install`` on Kaggle papermill (3.11) before ``uv run``.
UV_PIP_SPEC = "uv==0.10.11"

BOOTSTRAP_TAG = "[arc-benchmark-bootstrap]"

# Single source of truth for both ``pip`` (3.12+) and ``uv run --with`` (3.11 path).
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


def _bootstrap_cell_source_lines() -> list[str]:
    """Lines of Python source for ``_bootstrap()`` embedded in the notebook (no leading cell header)."""
    tag = BOOTSTRAP_TAG
    n = len(PIP_PKGS_KAGGLE_WORKER)
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
        "    if sys.version_info >= (3, 12):",
        '        _log("pip install worker deps (verbose pip; no -q)")',
        "        subprocess.check_call(",
        "            [",
        "                sys.executable,",
        '                "-m",',
        '                "pip",',
        '                "install",',
    ]
    for pkg in PIP_PKGS_KAGGLE_WORKER:
        lines.append(f'                "{pkg}",')
    lines.extend(
        [
            "            ],",
            "            env=env,",
            "        )",
            '        _log("pip finished; exec TASK_SCRIPT as __main__")',
            '        exec(compile(code, str(out), "exec"), {"__name__": "__main__"})',
            '        _log("exec returned")',
            "        return",
            "",
            f'    _log("kernel < 3.12: pip install {UV_PIP_SPEC}")',
            "    subprocess.check_call(",
            f'        [sys.executable, "-m", "pip", "install", "-q", "{UV_PIP_SPEC}"],',
            "        env=env,",
            "    )",
            '    _log(f"uv run --python 3.12 with '
            + str(n)
            + ' --with pkgs -> {out.name}")',
            "    subprocess.check_call(",
            "        [",
            "            sys.executable,",
            '            "-m",',
            '            "uv",',
            '            "run",',
            '            "--python",',
            '            "3.12",',
        ]
    )
    for pkg in PIP_PKGS_KAGGLE_WORKER:
        lines.extend(['            "--with",', f'            "{pkg}",'])
    lines.extend(
        [
            '            "python",',
            "            str(out),",
            "        ],",
            "        env=env,",
            "    )",
            '    _log("uv subprocess exited ok")',
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
    print("[rebuild_kaggle_notebooks]", "worker pip/uv packages:", len(PIP_PKGS_KAGGLE_WORKER), flush=True)
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
