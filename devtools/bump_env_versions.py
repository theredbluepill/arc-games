#!/usr/bin/env python3
"""Rename environment package dirs to the PR head commit short SHA (ls20-style).

When ``environment_files/<stem>/<old_ver>/`` changes between ``base`` and ``head``,
copy that tree to ``environment_files/<stem>/<short8>/``, rewrite ``metadata.json``
(``game_id``, ``local_dir``), and remove ``old_ver``.

Skips stems in ``STEMS_SKIP_BUMP`` (legacy / reference packages). No-op if changed
files already live under ``<stem>/<short8>/`` matching ``head``.

Stdlib only. Intended for CI (see ``.github/workflows/bump-env-versions.yml``).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV = ROOT / "environment_files"

_ENV_LINE = re.compile(
    r"^environment_files/(?P<stem>[a-z0-9]+)/(?P<ver>[^/]+)/",
    re.IGNORECASE,
)

# Same idea as check_registry STEMS_OMITTED_FROM_GAMES — do not auto-retag these.
STEMS_SKIP_BUMP = frozenset({"vc33", "ls20", "ft09"})


def _run_git(args: list[str]) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout.strip()


def short_sha8(full_sha: str) -> str:
    """8-char hex prefix, unique in this repo."""
    out = _run_git(["rev-parse", "--short=8", full_sha])
    if not re.fullmatch(r"[0-9a-f]{8}", out):
        raise SystemExit(f"unexpected short sha {out!r} for {full_sha!r}")
    return out


def diff_names(base: str, head: str) -> list[str]:
    """Files changed on ``head`` since it diverged from ``base`` (merge-base diff)."""
    mb = _run_git(["merge-base", base, head])
    proc = subprocess.run(
        ["git", "diff", "--name-only", mb, head],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    return [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]


def stems_and_src_versions(lines: list[str]) -> dict[str, str]:
    """Map stem -> single source version dir name (from diff paths)."""
    stem_to_vers: dict[str, set[str]] = {}
    for line in lines:
        m = _ENV_LINE.match(line.replace("\\", "/"))
        if not m:
            continue
        stem, ver = m.group("stem"), m.group("ver")
        stem_to_vers.setdefault(stem, set()).add(ver)
    out: dict[str, str] = {}
    for stem, vers in stem_to_vers.items():
        if len(vers) > 1:
            raise SystemExit(
                f"{stem}: multiple version dirs touched in one PR: {sorted(vers)}"
            )
        out[stem] = next(iter(vers))
    return out


def patch_metadata(meta_path: Path, stem: str, new_ver: str) -> None:
    data = json.loads(meta_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{meta_path}: metadata must be an object")
    data["game_id"] = f"{stem}-{new_ver}"
    data["local_dir"] = f"environment_files/{stem}/{new_ver}".replace("\\", "/")
    data["date_downloaded"] = datetime.now(UTC).isoformat()
    meta_path.write_text(
        json.dumps(data, indent=2) + "\n",
        encoding="utf-8",
    )


def bump_stem(stem: str, src_ver: str, dest_ver: str, *, dry_run: bool) -> bool:
    """Return True if filesystem changed."""
    if stem in STEMS_SKIP_BUMP:
        print(f"  skip stem {stem} (STEMS_SKIP_BUMP)")
        return False

    stem_dir = ENV / stem
    src = stem_dir / src_ver
    dest = stem_dir / dest_ver
    if not src.is_dir():
        print(f"  skip {stem}: missing {src}", file=sys.stderr)
        return False
    meta_src = src / "metadata.json"
    if not meta_src.is_file():
        print(f"  skip {stem}: no metadata in {src_ver}", file=sys.stderr)
        return False

    if src_ver == dest_ver:
        print(f"  skip {stem}: already at {dest_ver}")
        return False

    if dest.exists():
        raise SystemExit(f"{dest}: destination exists; resolve manually")

    print(f"  {stem}: {src_ver} -> {dest_ver}")
    if dry_run:
        return True

    shutil.copytree(src, dest)
    patch_metadata(dest / "metadata.json", stem, dest_ver)
    shutil.rmtree(src)
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", required=True, help="Git ref (e.g. PR base SHA)")
    ap.add_argument("--head", required=True, help="Git ref (e.g. PR head SHA)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    head_full = _run_git(["rev-parse", args.head])
    dest_ver = short_sha8(head_full)

    changed = diff_names(args.base, args.head)
    mapping = stems_and_src_versions(changed)

    any_change = False
    for stem, src_ver in sorted(mapping.items()):
        # Already only touching the canonical folder for this head?
        if src_ver == dest_ver:
            print(f"  skip {stem}: changes already under {dest_ver}")
            continue
        if bump_stem(stem, src_ver, dest_ver, dry_run=args.dry_run):
            any_change = True

    if not any_change and not mapping:
        print("bump_env_versions: no environment_files changes in diff")
    elif not any_change:
        print("bump_env_versions: nothing to rename")
    else:
        print("bump_env_versions: done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
