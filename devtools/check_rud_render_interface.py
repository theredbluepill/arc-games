#!/usr/bin/env python3
"""Fail if any environment game defines a no-op RenderableUserDisplay.render_interface.

Heuristic (aligned with generate-arc-game-gif / RUD HUD audit): the first parameter
after ``self`` must either be subscript-assigned (e.g. ``frame[y, x] = c``) or passed
as an argument to a call inside ``render_interface``.

Run: python3 devtools/check_rud_render_interface.py
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ENV = REPO / "environment_files"

# Plan games called out as "thin strip" HUD only — mechanical check passes; GIFs may
# still be hard to read. See .agents/skills/generate-arc-game-gif/SKILL.md.
THIN_STRIP_PLAN_STEMS = ("ep01", "tf01", "rb01", "au01", "dn01")


def _bases_include_rud(bases: list[ast.expr]) -> bool:
    for b in bases:
        if isinstance(b, ast.Name) and b.id == "RenderableUserDisplay":
            return True
        if isinstance(b, ast.Attribute) and b.attr == "RenderableUserDisplay":
            return True
    return False


def _frame_param_name(args: ast.arguments) -> str | None:
    pos = [a for a in args.args if a.arg != "self"]
    if not pos:
        return None
    return pos[0].arg


def _render_interface_meaningful(body: list[ast.stmt], frame_name: str) -> bool:
    class V(ast.NodeVisitor):
        def __init__(self) -> None:
            self.ok = False

        def visit_Assign(self, node: ast.Assign) -> None:
            for t in node.targets:
                if self._frame_subscript_store(t):
                    self.ok = True
            self.generic_visit(node)

        def visit_AugAssign(self, node: ast.AugAssign) -> None:
            if self._frame_subscript_store(node.target):
                self.ok = True
            self.generic_visit(node)

        def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
            if node.target and self._frame_subscript_store(node.target):
                self.ok = True
            self.generic_visit(node)

        def visit_Call(self, node: ast.Call) -> None:
            for a in node.args:
                if self._is_frame_ref(a):
                    self.ok = True
            for kw in node.keywords:
                if kw.value and self._is_frame_ref(kw.value):
                    self.ok = True
            self.generic_visit(node)

        def _frame_subscript_store(self, t: ast.expr) -> bool:
            return (
                isinstance(t, ast.Subscript)
                and isinstance(t.value, ast.Name)
                and t.value.id == frame_name
            )

        def _is_frame_ref(self, e: ast.expr) -> bool:
            return isinstance(e, ast.Name) and e.id == frame_name

    v = V()
    for stmt in body:
        v.visit(stmt)
    return v.ok


def _check_file(path: Path) -> list[str]:
    issues: list[str] = []
    try:
        src = path.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(path))
    except SyntaxError as e:
        return [f"{path}: syntax error: {e}"]

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        if not _bases_include_rud(node.bases):
            continue
        for item in node.body:
            if not isinstance(item, ast.FunctionDef) or item.name != "render_interface":
                continue
            frame = _frame_param_name(item.args)
            if not frame:
                issues.append(f"{path}:{item.lineno}: {node.name}.render_interface: no frame param")
                continue
            if not _render_interface_meaningful(item.body, frame):
                issues.append(
                    f"{path}:{item.lineno}: {node.name}.render_interface({frame}): "
                    "no frame subscript store and no call passing frame"
                )
    return issues


def main() -> int:
    if not ENV.is_dir():
        print(f"missing {ENV}", file=sys.stderr)
        return 2
    all_issues: list[str] = []
    for py in sorted(ENV.rglob("*.py")):
        all_issues.extend(_check_file(py))
    if all_issues:
        print("RenderableUserDisplay.render_interface must draw on the frame or pass it to helpers:\n")
        for line in all_issues:
            print(line)
        return 1
    print("OK: all render_interface methods pass the mechanical HUD check.")
    if THIN_STRIP_PLAN_STEMS:
        print(
            "Note: thin-strip Plan-style stems (manual GIF checklist): "
            + ", ".join(THIN_STRIP_PLAN_STEMS)
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
