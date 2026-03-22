"""Golden checks for solvability harness (real env transitions)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
DEVTOOLS = ROOT / "devtools"
for p in (str(ROOT), str(SCRIPTS), str(DEVTOOLS)):
    if p not in sys.path:
        sys.path.insert(0, p)

from arc_agi import Arcade, OperationMode  # noqa: E402
from arcengine import GameAction, GameState  # noqa: E402
from solvability_common import (  # noqa: E402
    canonical_version_for_stem,
    full_game_id_canonical,
)
from solvers.engine_bfs import engine_bfs_single_level  # noqa: E402
from solvers.push_switch import verify_push_stem, verify_switch_stem  # noqa: E402


class SolvabilityGoldenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.arcade = Arcade(
            environments_dir=str(ROOT / "environment_files"),
            operation_mode=OperationMode.OFFLINE,
        )

    def test_co01_engine_bfs_level0(self) -> None:
        env = self.arcade.make(full_game_id_canonical("co01"), seed=0, render_mode=None)
        assert env is not None
        bfs = engine_bfs_single_level(
            env,
            level_index=0,
            max_nodes=80_000,
            max_depth=80,
            max_click_cells=2500,
            allowed_action_ids=None,
        )
        self.assertTrue(bfs.ok, bfs.reason)

    def test_sk01_push_plan_level0(self) -> None:
        stem = "sk01"
        env = self.arcade.make(full_game_id_canonical(stem), seed=0, render_mode=None)
        assert env is not None
        v = canonical_version_for_stem(stem)
        ok, msg = verify_push_stem(env, stem, v, 0, variant="default")
        self.assertTrue(ok, msg)

    def test_fs01_switch_plan_level0(self) -> None:
        stem = "fs01"
        env = self.arcade.make(full_game_id_canonical(stem), seed=0, render_mode=None)
        assert env is not None
        v = canonical_version_for_stem(stem)
        ok, msg = verify_switch_stem(env, stem, v, 0, mode="all")
        self.assertTrue(ok, msg)

    def test_action6_step_lo01(self) -> None:
        env = self.arcade.make(full_game_id_canonical("lo01"), seed=0, render_mode=None)
        assert env is not None
        env.reset()
        r = env.step(GameAction.ACTION6, data={"x": 1, "y": 1}, reasoning={})
        assert r is not None
        self.assertNotEqual(r.state, GameState.GAME_OVER)


if __name__ == "__main__":
    unittest.main()
