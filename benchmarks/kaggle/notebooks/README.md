# Kaggle task notebooks

Source of truth for task code is **`../arc_kaggle_notebook_template.py`** (all four `@kbench.task` definitions in one file). Copy cells into [Create new task](https://www.kaggle.com/benchmarks/tasks/new), then **+ Add data** and attach a dataset with a non-empty **`environment_files/`** tree (same layout as this repo). Kaggle mounts under **`/kaggle/input/datasets/<user>/<dataset-name>/`** — this repo prefers **`/kaggle/input/datasets/poonszesen/arc-interactive`**, then falls back to any mount with `environment_files/`. Skipping **Add data** yields **`Available games: []`** / `Failed to create environment`.

**Kernel:** Use **Python 3.12** (Kaggle Notebook). The regenerated `.ipynb` bootstrap runs `pip install` with the packages in [`PIP_PKGS_KAGGLE_WORKER`](../rebuild_kaggle_notebooks.py), then `exec(TASK_SCRIPT)`. The embedded bootstrap prints **`[arc-benchmark-bootstrap]`** lines (pip install runs **without** `-q` so progress shows in logs).

| `@kbench.task` name | Game stem | `max_steps` in template |
|---------------------|-----------|-------------------------|
| `arc_ez01_go_up` | ez01 | 30 |
| `arc_sk01_sokoban` | sk01 | 200 |
| `arc_tt01_collect` | tt01 | 200 |
| `arc_sv01_survive` | sv01 | 80 |

Task code resolves the full `game_id` from `environment_files/<stem>/…/metadata.json` (see `_full_game_id` in `arc_kaggle_notebook_template.py`). Load environments with [`Arcade`](https://docs.arcprize.org/toolkit/arc_agi) and `environments_dir` + `OperationMode.OFFLINE` for local games.

**Regenerate canonical four:** `python3 benchmarks/kaggle/rebuild_kaggle_notebooks.py` writes `benchmarks/kaggle/notebooks/*.ipynb`.

**All stems:** `python benchmarks/kaggle/export_kaggle_notebooks_all_stems.py` writes `benchmarks/kaggle/notebooks/all/arc-interactive-<stem>.ipynb` for every registry-style stem (skips `vc33`, `ls20`, `ft09` by default). Override probing with `notebook_export_overrides.json` (`stems.<stem>.max_steps` / `grid_size`).

**Worker deps:** install the same set as `PIP_PKGS_KAGGLE_WORKER` (currently: `arc-agi`, `arcengine`, `numpy`, `hishel[httpx]>=1.1`, `openai`, `google-genai`, `panel`, `docker`, `protobuf`, `joblib`, `jupyter-client`, `nest-asyncio`, `playwright`, `ipython`). Do **not** `pip install google` — use **`google-genai`** only. **Playwright** may still need browser binaries (`playwright install`) if something imports Chromium.

## Choosing a model (`kbench.llms`)

The template’s last line calls **`kbench.llm`** (platform default for that run). In a benchmark notebook you can list what your session actually supports:

```python
import kaggle_benchmarks as kbench
list(kbench.llms.keys())
```

That returns provider ids such as `google/gemini-2.5-flash`, `anthropic/claude-sonnet-4-5@20250929`, `deepseek-ai/deepseek-v3.2`, etc. (the list changes as Kaggle updates offerings).

To **force** a specific handle for an interactive run, pass it into `.run` instead of `kbench.llm`:

```python
arc_ez01_go_up.run(llm=kbench.llms["google/gemini-2.5-flash"], seed=0, max_steps=30)
```

Use any key that appears in `list(kbench.llms.keys())`. Edit the **`*.run(llm=...)`** line in `arc_kaggle_notebook_template.py`.

**Note:** Official **benchmark leaderboard** runs may still bind models the UI selects; explicit `kbench.llms[...]` lets you pick which **logical model** to call from the notebook.

**If you still see `PermissionDeniedError: User location not supported` after switching to e.g. `google/gemini-2.5-flash`:** the `kaggle_benchmarks` client often talks to Kaggle’s **Model Proxy** using an **OpenAI-compatible HTTP stack** (you will still see `openai.*` in the traceback). The block is usually on **that proxy / region**, not on “wrong Gemini vs OpenAI id”. Trying other keys from `list(kbench.llms.keys())` is still worth one attempt (different providers may differ), but if **every** model fails the same way, only **Kaggle** (supported regions, account eligibility, or support) can resolve it—not a change in ARC notebook code.

## Model API / “User location not supported”

If the log shows **`openai.PermissionDeniedError: User location not supported for this model/API`** (or similar) when `kbench.llm` calls the hosted model, your ARC task and **dataset path are fine** (e.g. you already see *Successfully loaded game class Ez01…*).

That error comes from the **benchmark’s model endpoint** (provider geo / eligibility), not from `environment_files`. Mitigations:

- Use **`kbench.llms["google/gemini-2.5-flash"]`** (or another non–blocked provider from `list(kbench.llms.keys())`) in `.run(...)` while testing in the notebook.
- In the **Benchmark / task** UI, pick a **different model** for leaderboard runs ([Kaggle Benchmarks docs](https://www.kaggle.com/docs/benchmarks), competition rules).
- **Kaggle support** / forums if nothing in `kbench.llms` works from your region.

Local smoke tests without any Model Proxy calls: `python -m benchmarks.kaggle.run_task_kbench_mock`.
