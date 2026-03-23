# Generated notebooks (one task per stem)

These `.ipynb` files are produced by:

```bash
python benchmarks/kaggle/export_kaggle_notebooks_all_stems.py
```

They are gitignored by default (large, reproducible). Override `max_steps` / `grid_size` per stem in `benchmarks/kaggle/notebook_export_overrides.json`.

The four canonical tasks under `../` come from `rebuild_kaggle_notebooks.py` instead.

Use a **Python 3.12** Kaggle Notebook kernel.
