# ARC-AGI-3 Benchmarks

Benchmarks for evaluating AI models on ARC-AGI-3 games, including Kaggle benchmark tasks.

## Structure

- **`arc_game_wrapper.py`** – Reusable wrapper to run ARC games with an LLM agent. Serializes game state to text, parses action responses, and runs the game loop.
- **`kaggle/`** – Kaggle benchmark tasks using the [kaggle-benchmarks](https://pypi.org/project/kaggle-benchmarks/) library.

## Sample Task: arc_ez01_go_up

Evaluates an LLM playing **ez01 (Go Up)** – the simplest ARC game (4 movement actions). The LLM receives the grid each step and must output the next action. Success = complete at least 1 level within 30 steps.

### Running Locally

Local runs require the Kaggle Model Proxy. Configure a `.env` file in the repo root:

```env
MODEL_PROXY_URL=https://mp-staging.kaggle.net/models/openapi
MODEL_PROXY_API_KEY=your_token
LLM_DEFAULT=google/gemini-2.5-flash
```

Obtain `MODEL_PROXY_API_KEY` from the [Kaggle Models API onboarding](https://www.kaggle.com/models-api-onboarding-packet).

Then run from the repo root:

```bash
uv run python -m benchmarks.kaggle.arc_ez01_task
```

To verify the wrapper without the Kaggle proxy (mock LLM, always moves up):

```bash
uv run python -m benchmarks.run_task_test
```

### Publishing to a Kaggle Benchmark (including private)

1. **Create a dataset** with the game files:
   - Go to [Kaggle Datasets](https://www.kaggle.com/datasets) → **New dataset**
   - Upload a zip of `environment_files/` (or the full repo)
   - Name it e.g. `arc-interactive` and publish (private or public)

2. **Create the task notebook**:
   - Go to [Create new task](https://www.kaggle.com/benchmarks/tasks/new)
   - Click **+ Add data** and attach your dataset (e.g. `poonszesen/arc-interactive`)
   - Use the template in `benchmarks/kaggle/arc_ez01_kaggle_notebook.py`:
     - Cell 1: `!pip install -q git+https://github.com/arcprize/arc-agi.git git+https://github.com/arcprize/ARCEngine.git`
     - Cell 2: Paste the task and wrapper code (update `INPUT_DIR` if your dataset path differs)
     - Cell 3: `arc_ez01_go_up.run(llm=kbench.llm, seed=0, max_steps=30)`
   - Run the notebook to generate the task

3. **Add the task to your benchmark**:
   - Open your benchmark (e.g. [poonszesen/arc-interactive](https://www.kaggle.com/benchmarks/poonszesen/arc-interactive))
   - Click **Edit** → **Add task** → select your newly created task
   - Add models to evaluate if needed

See [Kaggle Benchmarks documentation](https://www.kaggle.com/docs/benchmarks) for full details.

## Adding More Tasks

Use `arc_game_wrapper.run_game_with_llm()` with different `game_id` values (e.g. `sk01-v1`, `tb01-v1`) and adjust `grid_size` and `max_steps` per game. Add new `@kbench.task` functions in `benchmarks/kaggle/`.
