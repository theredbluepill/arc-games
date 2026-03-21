#!/usr/bin/env python3
"""Inject inline RUD helpers + stub ``U`` HUD into compact Plan-style games."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / "environment_files"

U_BLOCK = '''
def _rp(frame, h, w, x, y, c):
    if 0 <= x < w and 0 <= y < h:
        frame[y, x] = c


def _r_dots(frame, h, w, li, n, y0=0):
    for i in range(min(n, 14)):
        cx = 1 + i * 2
        if cx >= w:
            break
        c = 14 if i < li else (11 if i == li else 3)
        _rp(frame, h, w, cx, y0, c)


def _r_bar(frame, h, w, game_over, win):
    if not (game_over or win):
        return
    r = h - 3
    if r < 0:
        return
    c = 14 if win else 8
    for x in range(min(w, 16)):
        _rp(frame, h, w, x, r, c)


class U(RenderableUserDisplay):
    def __init__(self, num_levels: int) -> None:
        self._num_levels = num_levels
        self._level_index = 0
        self._state = None

    def update(self, *, level_index: int | None = None, state=None) -> None:
        if level_index is not None:
            self._level_index = level_index
        if state is not None:
            self._state = state

    def render_interface(self, f):
        import numpy as np

        from arcengine import GameState

        if not isinstance(f, np.ndarray):
            return f
        h, w = f.shape
        _r_dots(f, h, w, self._level_index, self._num_levels, 0)
        go = self._state == GameState.GAME_OVER
        win = self._state == GameState.WIN
        _r_bar(f, h, w, go, win)
        return f
'''

SYNC = "        self._ui.update(level_index=self.level_index, state=self._state)\n"


def patch_plan_compact(path: Path) -> None:
    s = path.read_text(encoding="utf-8")
    if "def _rp(" in s:
        return
    if "class U(RenderableUserDisplay)" not in s:
        return
    # GameState import
    if "GameState" not in s:
        s = s.replace(
            "from arcengine import ARCBaseGame",
            "from arcengine import ARCBaseGame, GameState",
            1,
        )
        s = s.replace(
            "from arcengine import ARCBaseGame, Camera, GameAction, Level, RenderableUserDisplay, Sprite",
            "from arcengine import ARCBaseGame, Camera, GameAction, GameState, Level, RenderableUserDisplay, Sprite",
            1,
        )
    # Remove old U class variants
    s = re.sub(
        r"class U\(RenderableUserDisplay\):.*?(?=\ndef |\nclass [A-Z]|\n[A-Za-z_][a-z0-9_]* = |\nlevels = )",
        U_BLOCK.strip() + "\n",
        s,
        count=1,
        flags=re.DOTALL,
    )
    # Camera [U()] -> self._ui
    s = s.replace("[U()]", "[self._ui]")
    # inject self._ui = U(len(levels)) before super in game __init__
    s = re.sub(
        r"(class \w+\(ARCBaseGame\):\s*\n\s*def __init__\(self\)(?: -> None)?:\s*\n)(\s*super\(\).__init__)",
        r"\1        self._ui = U(len(levels))\n\2",
        s,
        count=1,
    )
    # on_set_level: append sync before next def at class level
    if SYNC.strip() not in s:

        def on_tail(m: re.Match[str]) -> str:
            body = m.group(1)
            if "_ui.update" in body:
                return m.group(0)
            return m.group(0).replace(body, body.rstrip() + "\n" + SYNC)

        s = re.sub(
            r"(def on_set_level\(self[^\)]*\)[^:]*:(?:\n(?:    .*)+))",
            on_tail,
            s,
            count=1,
        )
    # step: prepend sync before each self.complete_action() not preceded by _ui.update
    lines = s.splitlines(keepends=True)
    out = []
    in_step = False
    for i, line in enumerate(lines):
        if re.match(r"^\s*def step\(self\)", line):
            in_step = True
        elif in_step and re.match(r"^\s{4}def \w", line):
            in_step = False
        if in_step and "self.complete_action()" in line and "_ui.update" not in line:
            ind = re.match(r"^(\s*)", line)
            sp = ind.group(1) if ind else "        "
            out.append(f"{sp}self._ui.update(level_index=self.level_index, state=self._state)\n")
        out.append(line)
    s = "".join(out)
    path.write_text(s, encoding="utf-8")
    print("plan", path)


def patch_named_frame_ui(path: Path, class_name: str, extra_update_fields: str = "") -> None:
    """Replace noop *UI with standard HUD; caller wires game updates separately if needed."""
    s = path.read_text(encoding="utf-8")
    if "def _rp(" in s:
        return
    helpers = """

def _rp(frame, h, w, x, y, c):
    if 0 <= x < w and 0 <= y < h:
        frame[y, x] = c


def _r_dots(frame, h, w, li, n, y0=0):
    for i in range(min(n, 14)):
        cx = 1 + i * 2
        if cx >= w:
            break
        c = 14 if i < li else (11 if i == li else 3)
        _rp(frame, h, w, cx, y0, c)


def _r_ticks(frame, h, w, n, y=None):
    row = (h - 1) if y is None else y
    for i in range(max(0, min(n, 8))):
        _rp(frame, h, w, 1 + i, row, 11)


def _r_bar(frame, h, w, game_over, win):
    if not (game_over or win):
        return
    r = h - 3
    if r < 0:
        return
    c = 14 if win else 8
    for x in range(min(w, 16)):
        _rp(frame, h, w, x, r, c)

"""
    # insert after docstring or first import
    ins_at = 0
    if s.startswith('"""'):
        ins_at = s.index("\n", s.index('"""') + 3) + 1
    # after from __future__ if present
    if "from __future__" in s[:200]:
        ins_at = s.index("\n", s.index("from __future__")) + 1
    # find first arcengine import line and append after full import
    m = re.search(r"^from arcengine import[^\n]+\n(?:\s+[^\n]+\n)*", s, re.M)
    if m:
        pos = m.end()
        frag = s[:pos] + helpers
        rest = s[pos:]
        if "GameState" not in frag:
            frag = frag.replace(
                "from arcengine import ARCBaseGame, Camera, GameAction, Level, RenderableUserDisplay, Sprite",
                "from arcengine import ARCBaseGame, Camera, GameAction, GameState, Level, RenderableUserDisplay, Sprite",
                1,
            )
            frag = frag.replace(
                "from arcengine import ARCBaseGame, Camera, Level, RenderableUserDisplay, Sprite",
                "from arcengine import ARCBaseGame, Camera, GameState, Level, RenderableUserDisplay, Sprite",
                1,
            )
        s = frag + rest
    else:
        s = helpers + s
    # replace class body - match class_name
    ui_re = rf"class {class_name}\(RenderableUserDisplay\):\s*\n(?:\s+.*\n)*?\s+def render_interface\(self, frame\):\s*\n\s+return frame\n"
    new_ui = f"""class {class_name}(RenderableUserDisplay):
    def __init__(self, level_index: int = 0, num_levels: int = 1, ticks: int = 1) -> None:
        self._level_index = level_index
        self._num_levels = num_levels
        self._ticks = ticks
        self._state = None

    def update(
        self,
        *,
        level_index: int | None = None,
        num_levels: int | None = None,
        ticks: int | None = None,
        state=None,
    ) -> None:
        if level_index is not None:
            self._level_index = level_index
        if num_levels is not None:
            self._num_levels = num_levels
        if ticks is not None:
            self._ticks = ticks
        if state is not None:
            self._state = state

    def render_interface(self, frame):
        import numpy as np

        from arcengine import GameState

        if not isinstance(frame, np.ndarray):
            return frame
        h, w = frame.shape
        _r_dots(frame, h, w, self._level_index, self._num_levels, 0)
        _r_ticks(frame, h, w, self._ticks)
        go = self._state == GameState.GAME_OVER
        win = self._state == GameState.WIN
        _r_bar(frame, h, w, go, win)
        return frame
"""
    s2, n = re.subn(ui_re, new_ui, s, count=1)
    if n != 1:
        raise RuntimeError(f"no UI match {path} {class_name}")
    path.write_text(s2, encoding="utf-8")
    print("named", path, class_name)


def main() -> None:
    plans = [
        "cf01/v1/cf01.py",
        "ec01/v1/ec01.py",
        "fb01/v1/fb01.py",
        "fc01/v1/fc01.py",
        "gc01/v1/gc01.py",
        "hn01/v1/hn01.py",
        "lk01/v1/lk01.py",
        "lp01/v1/lp01.py",
        "pj01/v1/pj01.py",
        "qt01/v1/qt01.py",
        "sr01/v1/sr01.py",
        "tk01/v1/tk01.py",
        "vt01/v1/vt01.py",
        "wb01/v1/wb01.py",
    ]
    for rel in plans:
        patch_plan_compact(ENV / rel)
    patch_plan_compact(ENV / "sc01/v1/sc01.py")
    # hn04 multiline U
    p = ENV / "hn04/v1/hn04.py"
    txt = p.read_text(encoding="utf-8")
    if "def _rp(" not in txt:
        txt = txt.replace(
            "from arcengine import ARCBaseGame, Camera, GameAction, Level, RenderableUserDisplay, Sprite",
            "from arcengine import ARCBaseGame, Camera, GameAction, GameState, Level, RenderableUserDisplay, Sprite",
        )
        txt = re.sub(
            r"class U\(RenderableUserDisplay\):\s*\n\s*def render_interface\(self, f\):\s*\n\s*return f\n",
            U_BLOCK.strip() + "\n",
            txt,
            count=1,
        )
        txt = txt.replace("[U()]", "[self._ui]")
        txt = re.sub(
            r"(class Hn04\(ARCBaseGame\):\s*\n\s*def __init__\(self\) -> None:\s*\n)(\s*super\(\).__init__)",
            r"\1        self._ui = U(len(levels))\n\2",
            txt,
            count=1,
        )
        if "self._ui.update" not in txt:
            txt = re.sub(
                r"(def on_set_level\(self, level: Level\) -> None:\s*(?:\n(?:        .*)+))",
                lambda m: m.group(1).rstrip() + "\n        self._ui.update(level_index=self.level_index, state=self._state)\n",
                txt,
                count=1,
            )
        lines = txt.splitlines(keepends=True)
        out = []
        in_step = False
        for line in lines:
            if re.match(r"^\s*def step\(self\)", line):
                in_step = True
            elif in_step and re.match(r"^\s{4}def \w", line):
                in_step = False
            if in_step and "self.complete_action()" in line and "_ui.update" not in line:
                sp = re.match(r"^(\s*)", line).group(1)
                out.append(f"{sp}self._ui.update(level_index=self.level_index, state=self._state)\n")
            out.append(line)
        p.write_text("".join(out), encoding="utf-8")
        print("hn04")

    named = [
        ("cu01/v1/cu01.py", "Cu01UI"),
        ("cv01/v1/cv01.py", "Cv01UI"),
        ("cw01/v1/cw01.py", "Cw01UI"),
        ("cx01/v1/cx01.py", "Cx01UI"),
        ("kv04/v1/kv04.py", "Kv04UI"),
        ("ml04/v1/ml04.py", "Ml04UI"),
        ("ms04/v1/ms04.py", "Ms04UI"),
        ("ng04/v1/ng04.py", "Ng04UI"),
        ("pb04/v1/pb04.py", "Pb04UI"),
        ("pt05/v1/pt05.py", "Pt05UI"),
        ("rr01/v1/rr01.py", "Rr01UI"),
        ("sk04/v1/sk04.py", "Sk04UI"),
        ("tt01/63be02fb/tt01.py", "Tt01UI"),
        ("tt02/63be02fb/tt02.py", "Tt02UI"),
        ("tt03/63be02fb/tt03.py", "Tt03UI"),
    ]
    for rel, cn in named:
        patch_named_frame_ui(ENV / rel, cn)


if __name__ == "__main__":
    main()
