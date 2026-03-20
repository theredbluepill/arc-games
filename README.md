# ARC-AGI-3 Games

A collection of games for the ARC-AGI-3 benchmark.

## Games

See [GAMES.md](GAMES.md) for the complete game registry with previews.

## Quick Run

```bash
uv run python run_game.py --game <game_id> --version v1
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for full documentation on running and creating games.

## Kaggle Benchmarks

If you’ve finished Kaggle-side setup—a **dataset** whose root contains **`environment_files/`**, one or more **published benchmark tasks** built from [`benchmarks/kaggle/arc_kaggle_notebook_template.py`](benchmarks/kaggle/arc_kaggle_notebook_template.py), and those tasks **added to a benchmark**—you’re aligned with this repo’s layout. Operational details (bootstrap deps for papermill vs Python 3.12, optional notebook regeneration, model proxy / region notes) live in **[`benchmarks/README.md`](benchmarks/README.md)** and **[`benchmarks/kaggle/notebooks/README.md`](benchmarks/kaggle/notebooks/README.md)**.

Local checks without calling the hosted model:

```bash
uv run python -m benchmarks.kaggle.run_task_kbench_mock
```
