#!/usr/bin/env python3
"""Compare ONLINE ARC catalog stems to local ``environment_files`` stems.

Uses :meth:`Arcade.get_environments` in ``OperationMode.ONLINE`` (see
https://docs.arcprize.org/toolkit/list-games). Requires ``ARC_API_KEY``.

Stem rule: first segment of ``game_id`` before the first hyphen (lowercased),
e.g. ``ls20-cb3b57cc`` → ``ls20``. IDs with no hyphen use the full string as
the stem.

A **conflict** exists when some remote game shares a stem with a local package
but its full ``game_id`` is not exactly any local ``metadata.json`` game_id
(same artifact mirrored remotely is ignored).

Stems to ignore are parsed from the **Examples** section of the create-arc-game
skill: lines that mention ``environment_files/<stem>/<8-hex>/`` (concrete
version dir). Placeholder paths such as ``<version>`` are not counted. If no
skill file or no matching paths are found, a built-in default set is used.

When there are no conflicts, this script writes nothing (avoids noisy bot PRs).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_DIR = ROOT / "environment_files"
REPORT_DIR = ROOT / "devtools" / "reports"
JSON_PATH = REPORT_DIR / "official_stem_overlap.json"
MD_PATH = REPORT_DIR / "official_stem_overlap.md"

# Tried in order; first existing file wins (keep copies in sync).
_CREATE_ARC_GAME_SKILL_PATHS: tuple[Path, ...] = (
    ROOT / "skills" / "create-arc-game" / "SKILL.md",
    ROOT / ".opencode" / "skills" / "create-arc-game" / "SKILL.md",
    ROOT / ".agents" / "skills" / "create-arc-game" / "SKILL.md",
)

# If the skill is missing or ``## Examples`` has no concrete ``.../xxxxxxxx/`` paths.
_DEFAULT_OFFICIAL_REFERENCE_STEMS = frozenset({"vc33", "ls20", "ft09"})

_EXAMPLES_HEADER = re.compile(r"(?m)^## Examples\s*$")
_CONCRETE_ENV_PATH = re.compile(
    r"environment_files/([a-z0-9]+)/[0-9a-f]{8}/",
    re.IGNORECASE,
)


def load_ignored_reference_stems() -> tuple[frozenset[str], str | None]:
    """Stems from create-arc-game SKILL ``## Examples``; optional source path."""
    for path in _CREATE_ARC_GAME_SKILL_PATHS:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        m = _EXAMPLES_HEADER.search(text)
        if not m:
            return frozenset(_DEFAULT_OFFICIAL_REFERENCE_STEMS), str(
                path.relative_to(ROOT)
            )
        rest = text[m.end() :]
        m2 = re.search(r"(?m)^## ", rest)
        section = rest[: m2.start()] if m2 else rest
        stems = {s.lower() for s in _CONCRETE_ENV_PATH.findall(section)}
        rel = str(path.relative_to(ROOT))
        if stems:
            return frozenset(stems), rel
        return frozenset(_DEFAULT_OFFICIAL_REFERENCE_STEMS), rel
    return frozenset(_DEFAULT_OFFICIAL_REFERENCE_STEMS), None


def stem_from_game_id(game_id: str) -> str:
    return game_id.split("-", 1)[0].lower()


def discover_local_packages() -> tuple[set[str], set[str], dict[str, list[str]]]:
    """Return (local_stems, all_local_game_ids, stem -> list of game_ids)."""
    stems: set[str] = set()
    all_ids: set[str] = set()
    by_stem: dict[str, list[str]] = defaultdict(list)
    if not ENV_DIR.is_dir():
        return stems, all_ids, dict(by_stem)
    for stem_path in sorted(ENV_DIR.iterdir(), key=lambda p: p.name.lower()):
        if not stem_path.is_dir():
            continue
        stem = stem_path.name
        for ver_path in sorted(stem_path.iterdir(), key=lambda p: p.name.lower()):
            if not ver_path.is_dir():
                continue
            meta = ver_path / "metadata.json"
            if not meta.is_file():
                continue
            try:
                data = json.loads(meta.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            gid = data.get("game_id")
            if not isinstance(gid, str) or not gid:
                continue
            stems.add(stem)
            all_ids.add(gid)
            by_stem[stem].append(gid)
    return stems, all_ids, {k: sorted(v) for k, v in by_stem.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force-write",
        action="store_true",
        help="Write reports even when there are no conflicts (for debugging).",
    )
    args = parser.parse_args()

    if not os.environ.get("ARC_API_KEY", "").strip():
        print(
            "error: ARC_API_KEY is not set or empty "
            "(set in .env locally or GitHub Actions secret).",
            file=sys.stderr,
        )
        return 1

    from arc_agi import Arcade, OperationMode

    ignored_stems, skill_source = load_ignored_reference_stems()

    local_stems, local_game_ids, stem_to_local_ids = discover_local_packages()

    arc = Arcade(
        environments_dir=str(ENV_DIR.relative_to(ROOT)),
        operation_mode=OperationMode.ONLINE,
    )
    getter = getattr(arc, "get_environments", None)
    if not callable(getter):
        print("error: Arcade.get_environments is not available", file=sys.stderr)
        return 1

    try:
        remote_infos = getter()
    except BaseException as e:
        print(f"error: get_environments() failed: {e!r}", file=sys.stderr)
        return 1

    if remote_infos is None:
        print("error: get_environments() returned None", file=sys.stderr)
        return 1

    # Remote entries whose game_id is exactly a local package (mirrored / same).
    remote_by_stem: dict[str, list[dict[str, str]]] = defaultdict(list)
    for info in remote_infos:
        gid = getattr(info, "game_id", None)
        if not isinstance(gid, str) or not gid:
            continue
        if gid in local_game_ids:
            continue
        st = stem_from_game_id(gid)
        title = getattr(info, "title", "") or ""
        remote_by_stem[st].append({"game_id": gid, "title": title})

    conflicts: list[dict[str, object]] = []
    for stem in sorted(local_stems):
        if stem in ignored_stems:
            continue
        remotes = remote_by_stem.get(stem, [])
        if not remotes:
            continue
        conflicts.append(
            {
                "stem": stem,
                "local_game_ids": stem_to_local_ids.get(stem, []),
                "remote_examples": remotes,
            }
        )

    remote_count = len(remote_infos)
    print(f"remote_game_count={remote_count}")
    print(f"local_stem_count={len(local_stems)}")
    print(
        "ignored_official_reference_stems=" + ",".join(sorted(ignored_stems))
    )
    print(
        "ignored_official_reference_stems_source="
        + (skill_source or "default_builtin")
    )
    print(f"conflict_stem_count={len(conflicts)}")

    if not conflicts and not args.force_write:
        return 0

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    checked_at = datetime.now(UTC).isoformat()
    payload = {
        "checked_at_utc": checked_at,
        "remote_game_count": remote_count,
        "local_stem_count": len(local_stems),
        "ignored_official_reference_stems": sorted(ignored_stems),
        "ignored_official_reference_stems_source": skill_source or "default_builtin",
        "conflicts": conflicts,
    }
    JSON_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    md_lines = [
        "# Official vs community stem overlap",
        "",
        f"- **Checked (UTC)**: `{checked_at}`",
        f"- **Remote games (ONLINE catalog)**: {remote_count}",
        f"- **Local stems** (`environment_files/`): {len(local_stems)}",
        f"- **Conflicting stems**: {len(conflicts)}",
        "",
        "Remote entries listed here share a **stem** with a local package but use a "
        "different full `game_id` than any local `metadata.json`. Rename the "
        "community stem (and related paths / registry rows) to avoid catalog "
        "clashes in `NORMAL` mode.",
        "",
        "See [CONTRIBUTING.md](../CONTRIBUTING.md) (environment package layout, "
        "`metadata.json`, `GAMES.md`).",
        "",
        "**Ignored stems** (from create-arc-game `## Examples`, concrete "
        "`environment_files/<stem>/<8-hex>/` paths"
        + (
            f" in `{skill_source}`"
            if skill_source
            else " — skill missing; using built-in default"
        )
        + "): "
        + ", ".join(f"`{s}`" for s in sorted(ignored_stems))
        + ".",
        "",
    ]
    if conflicts:
        md_lines.extend(["## Conflicts", ""])
        for c in conflicts:
            st = c["stem"]
            md_lines.append(f"### `{st}`")
            md_lines.append("")
            md_lines.append("**Local `game_id` values:**")
            for gid in c["local_game_ids"]:
                md_lines.append(f"- `{gid}`")
            md_lines.append("")
            md_lines.append("**Remote catalog (examples):**")
            for ex in c["remote_examples"]:
                md_lines.append(f"- `{ex['game_id']}` — {ex['title']}")
            md_lines.append("")
    else:
        md_lines.append("No stem conflicts detected.")
        md_lines.append("")

    MD_PATH.write_text("\n".join(md_lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
