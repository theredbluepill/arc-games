#!/usr/bin/env python3
"""One-shot: replace stub ``class U`` + wire ``self._ui`` for compact Plan-style games."""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ENV = REPO / "environment_files"

BOOT = """
import importlib.util
from pathlib import Path

_hudm_cache = None


def _hudm():
    global _hudm_cache
    if _hudm_cache is None:
        for _d in Path(__file__).resolve().parents:
            _p = _d / "scripts" / "game_rud_hud.py"
            if _p.is_file():
                _s = importlib.util.spec_from_file_location("_arc_grh", _p)
                if _s is None or _s.loader is None:
                    continue
                _hudm_cache = importlib.util.module_from_spec(_s)
                _s.loader.exec_module(_hudm_cache)
                break
        else:
            raise RuntimeError("scripts/game_rud_hud.py not found")
    return _hudm_cache


"""

UCLASS = """class U(RenderableUserDisplay):
    def __init__(self, num_levels: int) -> None:
        self._num_levels = num_levels
        self._level_index = 0
        self._state = None
        self._ticks = 1

    def update(
        self,
        *,
        level_index: int | None = None,
        state=None,
        ticks: int | None = None,
    ) -> None:
        if level_index is not None:
            self._level_index = level_index
        if state is not None:
            self._state = state
        if ticks is not None:
            self._ticks = ticks

    def render_interface(self, f):
        import numpy as np

        from arcengine import GameState

        H = _hudm()
        if not isinstance(f, np.ndarray):
            return f
        h, w = f.shape
        H.draw_level_dots(f, h, w, self._level_index, self._num_levels, 0)
        H.draw_target_ticks(f, h, w, self._ticks)
        go = self._state == GameState.GAME_OVER
        win = self._state == GameState.WIN
        H.draw_game_state_bar(f, h, w, game_over=go, win=win)
        return f
"""

SYNC_BODY = """        self._ui.update(level_index=self.level_index, state=self._state, ticks=1)
"""

STUB_PATTERNS = [
    r'class U\(RenderableUserDisplay\):\s*\n\s*def render_interface\(self, f\): return f',
    r'class U\(RenderableUserDisplay\):\s*\n\s*def render_interface\(self, f\):\s*\n\s*return f',
]


def ensure_gamestate_import(src: str) -> str:
    if "GameState" in src:
        return src
    return re.sub(
        r"from arcengine import (\([^)]+\))",
        lambda m: m.group(0).replace(")", ", GameState)"),
        src,
        count=1,
    )


def replace_stub_u(src: str) -> str:
    for pat in STUB_PATTERNS:
        if re.search(pat, src):
            src = re.sub(pat, UCLASS.strip(), src, count=1)
            break
    else:
        raise ValueError("stub U not found")
    return src


def inject_boot_after_imports(src: str) -> str:
    if "_hudm_cache" in src:
        return src
    lines = src.splitlines(keepends=True)
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        if line.startswith("from arcengine import") or line.startswith("import "):
            i += 1
            while i < len(lines) and (lines[i].strip() == "" or not lines[i][0].isalpha()):
                if lines[i].strip() == "":
                    out.append(lines[i])
                    i += 1
                    break
                out.append(lines[i])
                i += 1
            out.append(BOOT)
            continue
        i += 1
    return "".join(out)


def camera_use_ui_instance(src: str, stem: str) -> str:
    """Camera(..., [U()]) -> self._ui = U(len(levels)); Camera(..., [self._ui])."""
    if "[U()]" not in src and "[ U() ]" not in src:
        return src
    # Find class Name(ARCBaseGame) and __init__
    m = re.search(r"class (\w+)\(ARCBaseGame\):\s*\n\s*def __init__\(self\)", src)
    if not m:
        m = re.search(r"class (\w+)\(ARCBaseGame\):\s*\n\s*def __init__\(self\) -> None:", src)
    if not m:
        raise ValueError(f"{stem}: no __init__")
    cls = m.group(1)
    # super().__init__(... Camera(..., [U()]) ...)
    src2 = src.replace("[U()]", "[self._ui]")
    if src2 == src:
        src2 = re.sub(r"\[\s*U\(\)\s*\]", "[self._ui]", src)
    if "[self._ui]" not in src2:
        raise ValueError(f"{stem}: camera pattern")
    init_pat = rf"(class {cls}\(ARCBaseGame\):\s*\n\s*def __init__\(self\)(?: -> None)?:\s*\n)"
    repl = rf"\1        self._ui = U(len(levels))\n        "
    src2, n = re.subn(init_pat, repl, src2, count=1)
    if n != 1:
        raise ValueError(f"{stem}: inject self._ui failed")
    return src2


def inject_sync(src: str, stem: str) -> str:
    call = "        self._ui.update(level_index=self.level_index, state=self._state, ticks=1)\n"
    if "self._ui.update" in src:
        return src
    if "def on_set_level" in src:
        src = re.sub(
            r"(def on_set_level\(self[^\)]*\)[^:]*:\s*(?:\n[^\n]+)+)",
            lambda m: m.group(1).rstrip() + "\n" + call if call.strip() not in m.group(1) else m.group(1),
            src,
            count=1,
        )
    # append before each complete_action in step — too broad; only last line of step
    lines = src.splitlines()
    out = []
    in_step = False
    depth = 0
    for i, line in enumerate(lines):
        out.append(line)
        if re.match(r"\s*def step\(self\)", line):
            in_step = True
            depth = 0
        if in_step:
            depth += line.count(":")  # crude
        if in_step and "self.complete_action()" in line and "def " not in line:
            indent = len(line) - len(line.lstrip())
            prev = lines[i - 1] if i else ""
            if "_ui.update" not in prev:
                out.insert(-1, " " * indent + "self._ui.update(level_index=self.level_index, state=self._state, ticks=1)")
    return "\n".join(out)


def patch_file(path: Path) -> None:
    stem = path.parent.parent.name
    src = path.read_text(encoding="utf-8")
    if "class U(RenderableUserDisplay)" not in src:
        return
    if "def update" in src and "num_levels" in src and "_hudm_cache" in src:
        return
    src = ensure_gamestate_import(src)
    src = replace_stub_u(src)
    src = inject_boot_after_imports(src)
    src = camera_use_ui_instance(src, stem)
    # naive: add update before every complete_action in step - use simpler approach
    if "self._ui.update" not in src:
        src = re.sub(
            r"(def on_set_level\(self[^\)]*\)[^:]*:\n(?:.*\n)*?)(\n    def |\nclass )",
            lambda m: m.group(1) + "        self._ui.update(level_index=self.level_index, state=self._state, ticks=1)\n" + m.group(2),
            src,
            count=1,
        )
        # before final complete in step: insert before last complete_action in file that's in step
        parts = src.rsplit("self.complete_action()", 1)
        if len(parts) == 2 and "def step" in parts[0]:
            last = parts[0].rsplit("\n", 1)
            if len(last) == 2:
                indent = len(last[1]) - len(last[1].lstrip()) if last[1].strip() else 8
                ins = " " * max(indent, 8) + "self._ui.update(level_index=self.level_index, state=self._state, ticks=1)\n"
                if ins.strip() not in parts[0]:
                    src = parts[0] + "\n" + ins + "        self.complete_action()" + parts[1]
    path.write_text(src, encoding="utf-8")
    print("patched", path)


def main() -> None:
    files = [
        ENV / "at01/v1/at01.py",
        ENV / "cf01/v1/cf01.py",
        ENV / "ec01/v1/ec01.py",
        ENV / "fb01/v1/fb01.py",
        ENV / "fc01/v1/fc01.py",
        ENV / "gc01/v1/gc01.py",
        ENV / "hn01/v1/hn01.py",
        ENV / "lk01/v1/lk01.py",
        ENV / "lp01/v1/lp01.py",
        ENV / "pj01/v1/pj01.py",
        ENV / "qt01/v1/qt01.py",
        ENV / "sc01/v1/sc01.py",
        ENV / "sr01/v1/sr01.py",
        ENV / "tk01/v1/tk01.py",
        ENV / "vt01/v1/vt01.py",
        ENV / "wb01/v1/wb01.py",
    ]
    for p in files:
        if p.is_file():
            patch_file(p)


if __name__ == "__main__":
    main()
