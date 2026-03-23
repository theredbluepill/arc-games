#!/usr/bin/env python3
"""Generate one Kaggle benchmark notebook per game stem under ``environment_files/``.

Each notebook embeds the **shared** task fragment from
``arc_kaggle_notebook_template.py`` (between ``<<<KAGGLE_TASK_SHARED_*>>>`` markers)
plus a single ``@kbench.task`` that calls ``run_game_with_llm`` with
``_full_game_id("<stem>")`` so the published dataset’s ``metadata.json`` always
wins (SHA dirs, ``v1``, etc.).

Grid size defaults are probed at export time via ``arc.make`` + first level
``grid_size`` (fallback 24). Optional per-stem overrides live in
``notebook_export_overrides.json`` next to this script.

Does **not** overwrite the four canonical notebooks from
``rebuild_kaggle_notebooks.py`` — default output is ``notebooks/all/``.

Usage::

    python benchmarks/kaggle/export_kaggle_notebooks_all_stems.py
    python benchmarks/kaggle/export_kaggle_notebooks_all_stems.py -o benchmarks/kaggle/notebooks/all
    python benchmarks/kaggle/export_kaggle_notebooks_all_stems.py --stems ez01,sk01 --no-probe
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

KAGGLE_DIR = Path(__file__).resolve().parent
REPO_ROOT = KAGGLE_DIR.parent.parent
ENV_DIR = REPO_ROOT / "environment_files"
TEMPLATE_PATH = KAGGLE_DIR / "arc_kaggle_notebook_template.py"
OVERRIDES_PATH = KAGGLE_DIR / "notebook_export_overrides.json"

STEM_SKIP_DEFAULT = frozenset({"vc33", "ls20", "ft09"})
STEM_RE = re.compile(r"^[a-z]{2}\d{2}$")

DEFAULT_MAX_STEPS_FALLBACK = 200
DEFAULT_GRID_FALLBACK = 24

# Match tighter budgets from the original four-notebook suite where we did not override.
DEFAULT_MAX_STEPS_BY_STEM: dict[str, int] = {
    "ez01": 30,
    "sv01": 80,
}

_SHARED_BEGIN = "# <<<KAGGLE_TASK_SHARED_BEGIN>>>"
_SHARED_END = "# <<<KAGGLE_TASK_SHARED_END>>>"


def extract_shared_fragment(template_text: str) -> str:
    # Markers also appear in the module docstring; slice the code cell only.
    anchor = "# --- Cell 2: Task and wrapper ---"
    region_start = template_text.index(anchor)
    i = template_text.index(_SHARED_BEGIN, region_start)
    j = template_text.index(_SHARED_END, i + len(_SHARED_BEGIN))
    after = template_text.find("\n", i) + 1
    return template_text[after:j].rstrip()


def _load_rebuild_module():
    path = KAGGLE_DIR / "rebuild_kaggle_notebooks.py"
    spec = importlib.util.spec_from_file_location("_rebuild_kaggle_nb", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def discover_stems(*, skip: frozenset[str]) -> list[str]:
    if not ENV_DIR.is_dir():
        raise SystemExit(f"missing {ENV_DIR}")
    out: list[str] = []
    for stem_path in sorted(ENV_DIR.iterdir(), key=lambda p: p.name.lower()):
        if not stem_path.is_dir():
            continue
        stem = stem_path.name
        if stem in skip:
            continue
        if not STEM_RE.match(stem):
            continue
        ok = False
        for ver in stem_path.iterdir():
            if ver.is_dir() and (ver / "metadata.json").is_file():
                ok = True
                break
        if ok:
            out.append(stem)
    return out


def read_title(stem: str) -> str:
    stem_path = ENV_DIR / stem
    for ver in sorted(stem_path.iterdir(), key=lambda p: p.name.lower()):
        if not ver.is_dir():
            continue
        meta = ver / "metadata.json"
        if not meta.is_file():
            continue
        try:
            data = json.loads(meta.read_text(encoding="utf-8"))
            t = data.get("title")
            if isinstance(t, str) and t.strip():
                return t.strip()
        except (OSError, json.JSONDecodeError):
            pass
    return stem


def load_overrides() -> dict:
    if not OVERRIDES_PATH.is_file():
        return {}
    try:
        raw = json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise SystemExit(f"{OVERRIDES_PATH}: {e}") from e
    return raw if isinstance(raw, dict) else {}


def stem_overrides(overrides_root: dict, stem: str) -> dict:
    stems = overrides_root.get("stems")
    if isinstance(stems, dict) and stem in stems and isinstance(stems[stem], dict):
        return stems[stem]
    return {}


def probe_grid_size(stem: str) -> int:
    scripts = REPO_ROOT / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from env_resolve import full_game_id_for_stem  # noqa: E402

    try:
        from arc_agi import Arcade, OperationMode  # noqa: E402
    except ImportError as e:
        raise SystemExit(
            "arc-agi / arcengine required for --probe (default). "
            "Install with `pip install arc-agi` (see https://docs.arcprize.org) or pass --no-probe."
        ) from e

    arc = Arcade(
        environments_dir=str(ENV_DIR),
        operation_mode=OperationMode.OFFLINE,
    )
    gid = full_game_id_for_stem(stem)
    env = arc.make(gid, seed=0, render_mode=None)
    if env is None:
        return DEFAULT_GRID_FALLBACK
    obs = env.reset()
    if obs is None:
        return DEFAULT_GRID_FALLBACK
    try:
        gw, gh = env._game.current_level.grid_size
        return min(64, max(8, max(int(gw), int(gh))))
    except Exception:
        return DEFAULT_GRID_FALLBACK


def max_steps_for_stem(stem: str, o: dict) -> int:
    if "max_steps" in o:
        return int(o["max_steps"])
    return int(DEFAULT_MAX_STEPS_BY_STEM.get(stem, DEFAULT_MAX_STEPS_FALLBACK))


def build_task_py(
    shared: str,
    stem: str,
    *,
    title: str,
    grid_size: int,
    max_steps: int,
) -> str:
    safe_title = title.replace("\\", "\\\\").replace('"', '\\"')
    fn = f"arc_interactive_{stem}"
    task_name = f"arc_interactive_{stem}"
    cell3 = (
        "\n\n# --- Cell 3: Run this task on Kaggle ---\n"
        f"{fn}.run(llm=kbench.llm, seed=0, max_steps={max_steps})\n"
    )
    body = f'''

@kbench.task(name="{task_name}")
def {fn}(llm, seed: int = 0, max_steps: int = {max_steps}):
    """ARC-AGI-3 {stem}: {safe_title}"""
    arc = Arcade(environments_dir=ENVIRONMENTS_DIR, operation_mode=OperationMode.OFFLINE)
    levels_completed, _, _ = run_game_with_llm(
        arc, _full_game_id("{stem}"), llm, seed, max_steps, {grid_size}
    )
    kbench.assertions.assert_true(
        levels_completed >= 1,
        expectation="Complete at least 1 level (or survival segment).",
    )
'''
    return shared + body + cell3


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=KAGGLE_DIR / "notebooks" / "all",
        help="Directory for *.ipynb (default: benchmarks/kaggle/notebooks/all)",
    )
    ap.add_argument(
        "--stems",
        type=str,
        default="",
        help="Comma-separated stems only (default: all discoverable except --skip)",
    )
    ap.add_argument(
        "--skip",
        type=str,
        default=",".join(sorted(STEM_SKIP_DEFAULT)),
        help="Comma-separated stems to skip (default: vc33,ls20,ft09)",
    )
    ap.add_argument(
        "--no-probe",
        action="store_true",
        help=f"Do not load Arcade; use grid_size from overrides or {DEFAULT_GRID_FALLBACK}",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Print stems and parameters only",
    )
    args = ap.parse_args()

    skip = frozenset(s.strip() for s in args.skip.split(",") if s.strip())
    if args.stems.strip():
        stems = [s.strip() for s in args.stems.split(",") if s.strip()]
    else:
        stems = discover_stems(skip=skip)

    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")
    shared = extract_shared_fragment(template_text)

    overrides_root = load_overrides()
    skip_file = overrides_root.get("skip")
    if isinstance(skip_file, list):
        stems = [s for s in stems if s not in frozenset(skip_file)]

    reb = _load_rebuild_module()
    out_dir: Path = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    for stem in stems:
        if stem in skip:
            continue
        if not STEM_RE.match(stem):
            print(f"skip {stem!r} (stem pattern)", flush=True)
            continue
        o = stem_overrides(overrides_root, stem)
        grid = int(o["grid_size"]) if "grid_size" in o else None
        if grid is None and not args.no_probe:
            grid = probe_grid_size(stem)
        elif grid is None:
            grid = DEFAULT_GRID_FALLBACK
        ms = max_steps_for_stem(stem, o)
        title = read_title(stem)
        if args.dry_run:
            print(f"{stem}: grid_size={grid} max_steps={ms} title={title!r}", flush=True)
            continue

        task_py = build_task_py(shared, stem, title=title, grid_size=grid, max_steps=ms)
        code = reb.bootstrap_cell_from_task(task_py)
        md = (
            f"{reb.SECTION_12_MARKDOWN}\n\n---\n\n"
            f"# ARC benchmark: **{stem}**\n\n"
            f"{title}\n\n"
            "**Kernel:** Python **3.12** (Kaggle Notebook). The code cell runs `pip install` then the task.\n\n"
            "Attach a dataset whose root contains **`environment_files/`** (this stem must be present). "
            "Use [`Arcade`](https://docs.arcprize.org/toolkit/arc_agi) with "
            "`environments_dir` and `OperationMode.OFFLINE` for local games.\n\n"
            "See `benchmarks/kaggle/notebooks/README.md`.\n"
        )
        nb = reb.build_notebook(md, code)
        fname = f"arc-interactive-{stem}.ipynb"
        path = out_dir / fname
        path.write_text(json.dumps(nb, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {path} ({len(code)} chars code cell)", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
