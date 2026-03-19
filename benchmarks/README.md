# ARC-AGI-3 Benchmarks

Benchmarks for evaluating AI models on ARC-AGI-3 games, including Kaggle benchmark tasks (e.g. [Measuring Progress Toward AGI](https://www.kaggle.com/competitions/kaggle-measuring-agi)).

## Structure

- **`arc_game_wrapper.py`** – Run ARC games with an LLM: frame → text prompt, parse digit actions, game loop. Stops on `WIN`, `LOSE`, `LOST`, or **`GAME_OVER`** (e.g. sv01 death). Prompts treat ACTION1–7 as **game-defined** (IDs 1–4 are not guaranteed to mean up/down/left/right; see [ARC Actions](https://docs.arcprize.org/actions)). Use `default_action_help()` for 4- vs 5-ID prompts without hard-coding semantics.
- **`mock_llms.py`** – `ReplayMockLLM` / `ConstantMockLLM` for local smoke tests without the Model Proxy.
- **`kaggle/`** – `@kbench.task` definitions using [kaggle-benchmarks](https://pypi.org/project/kaggle-benchmarks/).

## Kaggle tasks (executive / cognitive suite)

| Task name | Game | Grid crop | Default `max_steps` | Success |
|-----------|------|-----------|---------------------|---------|
| `arc_ez01_go_up` | ez01-v1 | 8 | 30 | ≥ 1 level |
| `arc_sk01_sokoban` | sk01-v1 | 16 | 200 | ≥ 1 level |
| `arc_tt01_collect` | tt01-v1 | 24 | 200 | ≥ 1 level |
| `arc_sv01_survive` | sv01-v1 | 24 | 80 | ≥ 1 level (60 survival steps each) |

Source of truth: `benchmarks/kaggle/arc_tasks.py` (`ARC_TASK_NAMES`).  
`benchmarks/kaggle/arc_ez01_task.py` re-exports `arc_ez01_go_up` for backward compatibility.

### Running locally

Configure a `.env` in the repo root (Model Proxy):

```env
MODEL_PROXY_URL=https://mp-staging.kaggle.net/models/openapi
MODEL_PROXY_API_KEY=your_token
LLM_DEFAULT=google/gemini-2.5-flash
```

Obtain `MODEL_PROXY_API_KEY` from the [Kaggle Models API onboarding](https://www.kaggle.com/models-api-onboarding-packet).

Then:

```bash
uv run python -m benchmarks.kaggle.arc_ez01_task
```

Wrapper smoke test (always move up on ez01, no kaggle_benchmarks):

```bash
uv run python -m benchmarks.run_task_test
```

All four `@kbench.task` entries with **mock** LLMs (no proxy HTTP to a real model):

```bash
uv run python -m benchmarks.kaggle.run_task_kbench_mock
```

### Publishing to Kaggle Benchmarks

1. **Dataset** – Zip and upload **`environment_files/`** (full tree is simplest so every `*-v1` game resolves).
2. **Task notebook** – [Create new task](https://www.kaggle.com/benchmarks/tasks/new), attach the dataset, paste from `benchmarks/kaggle/arc_ez01_kaggle_notebook.py` (install `arc-agi` + `ARCEngine` in the first cell). Create **one notebook per task** or duplicate the run cell and change which `*.run(...)` you call.
3. **Benchmark** – Add each published task to your benchmark; see [Kaggle Benchmarks docs](https://www.kaggle.com/docs/benchmarks).

## Adding more games

Call `run_game_with_llm(..., game_id="…-v1", grid_size=<camera width>, max_steps=…)` from a new `@kbench.task` in `arc_tasks.py`, and add a row above. For mocks, record a digit string with `ReplayMockLLM` (see `MOCK_*` constants in `arc_tasks.py`).
