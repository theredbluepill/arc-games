"""
Kaggle notebook template for arc_ez01_go_up task.

Paste into a new Kaggle task notebook at: https://www.kaggle.com/benchmarks/tasks/new

Prerequisites:
  1. Add dataset with environment_files/ez01/v1/ (ez01.py, metadata.json)
  2. Publish dataset, then add it to this notebook via "+ Add data"
"""

# --- Cell 1: Install dependencies (run first) ---
# !pip install -q git+https://github.com/arcprize/arc-agi.git git+https://github.com/arcprize/ARCEngine.git

# --- Cell 2: Task and wrapper ---
import sys
from pathlib import Path

# Add dataset path (adjust if your dataset name differs)
INPUT_DIR = Path("/kaggle/input/arc-interactive")
if not INPUT_DIR.exists():
    # Fallback: try common dataset mount paths
    for p in ["/kaggle/input/arc-interactive-games", "/kaggle/input/arc-interactive"]:
        if Path(p).exists():
            INPUT_DIR = Path(p)
            break
ENVIRONMENTS_DIR = str(INPUT_DIR / "environment_files")
sys.path.insert(0, str(INPUT_DIR))

import kaggle_benchmarks as kbench
from arc_agi import Arcade, OperationMode

# Copy of run_game_with_llm and helpers (inline for Kaggle)
import re
from arcengine import GameAction

_ACTION_MAP = {
    1: GameAction.ACTION1, 2: GameAction.ACTION2, 3: GameAction.ACTION3,
    4: GameAction.ACTION4, 5: GameAction.ACTION5, 6: GameAction.ACTION6,
    7: GameAction.ACTION7,
}


def serialize_frame_to_text(frame, grid_size=8):
    import numpy as np
    if not frame:
        return "(no frame)"
    arr = np.asarray(frame[0])
    region = arr[:min(grid_size, arr.shape[0]), :min(grid_size, arr.shape[1])]
    lines = []
    for row in region:
        chars = []
        for cell in row:
            val = int(cell)
            chars.append("." if val == 0 else (str(val) if val < 10 else chr(ord("a") + val - 10)))
        lines.append("".join(chars))
    return "\n".join(lines)


def parse_action(response, available_actions):
    for pattern in [r"\bACTION([1-7])\b", r"\bACTION\s*([1-7])\b", r"\b([1-7])\b"]:
        m = re.search(pattern, response.strip().upper(), re.IGNORECASE)
        if m:
            num = int(m.group(1))
            if num in available_actions and num in _ACTION_MAP:
                return _ACTION_MAP[num]
    return _ACTION_MAP.get(available_actions[0] if available_actions else 1, GameAction.ACTION1)


def run_game_with_llm(arc, game_id, llm, seed=0, max_steps=50, grid_size=8):
    env = arc.make(game_id, seed=seed, render_mode=None)
    if env is None:
        raise RuntimeError(f"Failed to create environment for {game_id}")
    obs = env.reset()
    if obs is None:
        raise RuntimeError(f"Failed to reset for {game_id}")
    info = getattr(env, "info", None)
    title = getattr(info, "title", game_id) if info else game_id
    desc = getattr(info, "description", "Reach the goal.") if info else "Reach the goal."
    action_help = f"Available actions: {getattr(obs, 'available_actions', [1,2,3,4])}. Reply with a single digit."
    steps_used = 0
    levels_completed = getattr(obs, "levels_completed", 0) or 0
    while steps_used < max_steps:
        state_name = getattr(getattr(obs, "state", None), "name", "UNKNOWN")
        if state_name in ("WIN", "LOSE", "LOST"):
            break
        grid_text = serialize_frame_to_text(getattr(obs, "frame", []), grid_size)
        avail = getattr(obs, "available_actions", [1, 2, 3, 4])
        prompt = f'You are playing "{title}": {desc}\n\nGrid:\n{grid_text}\n\nStep {steps_used+1}/{max_steps}. {action_help}'
        response = llm.prompt(prompt)
        action = parse_action(response, avail)
        obs = env.step(action, reasoning={"step": steps_used + 1})
        steps_used += 1
        if obs is None:
            break
        levels_completed = getattr(obs, "levels_completed", levels_completed) or levels_completed
    return levels_completed, steps_used, obs


@kbench.task(name="arc_ez01_go_up")
def arc_ez01_go_up(llm, seed: int = 0, max_steps: int = 30):
    """Play ARC-AGI-3 ez01 (Go Up): reach the target by moving up. Output 1-4 each turn."""
    arc = Arcade(environments_dir=ENVIRONMENTS_DIR, operation_mode=OperationMode.OFFLINE)
    levels_completed, _, _ = run_game_with_llm(arc, "ez01-v1", llm, seed, max_steps, 8)
    kbench.assertions.assert_true(levels_completed >= 1, expectation="Complete at least 1 level.")

# --- Cell 3: Run the task ---
arc_ez01_go_up.run(llm=kbench.llm, seed=0, max_steps=30)
