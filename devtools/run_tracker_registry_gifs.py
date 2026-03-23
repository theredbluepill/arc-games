#!/usr/bin/env python3
"""Batch registry GIFs for tracker stems (see registry_gif_tracker_stems.txt).

Writes assets/{stem}.gif and devtools/registry_gif_batch_status.csv with
showcase_fallback=Y when verbose capture reported fallback (skill gap).
Run from repo root: uv run python devtools/run_tracker_registry_gifs.py
"""

from __future__ import annotations

import contextlib
import csv
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from gif_common import save_gif  # noqa: E402
from registry_gif_lib import load_overrides, record_registry_gif  # noqa: E402


def main() -> int:
    stem_path = ROOT / "devtools/registry_gif_tracker_stems.txt"
    stems = [s.strip() for s in stem_path.read_text(encoding="utf-8").splitlines() if s.strip()]
    overrides_all = load_overrides(ROOT)
    status_path = ROOT / "devtools/registry_gif_batch_status.csv"
    with status_path.open("w", newline="", encoding="utf-8") as sf:
        csv.writer(sf).writerow(
            ["stem", "ok", "showcase_fallback", "frames", "error"]
        )

    failed = 0
    for stem in stems:
        buf = io.StringIO()
        err = ""
        fb = False
        nframes = 0
        try:
            ovr = overrides_all.get(stem)
            ovr_dict = ovr if isinstance(ovr, dict) else None
            duration_ms = 150
            if ovr_dict and "gif_duration_ms" in ovr_dict:
                duration_ms = int(ovr_dict["gif_duration_ms"])
            with contextlib.redirect_stdout(buf):
                _, images = record_registry_gif(
                    stem, ROOT, overrides=ovr_dict, verbose=True, seed=0
                )
            fb = "showcase fallback" in buf.getvalue()
            nframes = len(images)
            save_gif(ROOT / "assets" / f"{stem}.gif", images, duration_ms=duration_ms)
        except Exception as e:  # noqa: BLE001
            err = f"{type(e).__name__}: {e}"
            failed += 1
        with status_path.open("a", newline="", encoding="utf-8") as sf:
            csv.writer(sf).writerow(
                [stem, "yes" if not err else "no", "Y" if fb else "N", nframes, err]
            )
        tag = "FAIL" if err else "ok"
        extra = " fallback" if fb and not err else ""
        print(f"{stem} {tag}{extra} {nframes} frames")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
