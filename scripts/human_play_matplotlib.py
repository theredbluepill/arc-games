"""Interactive human play with matplotlib — ARC-AGI-3 action mapping.

Keyboard matches human-facing docs (WASD + Space and Arrow + F); clicks send ACTION6
with x,y in 0–63 display space. See https://docs.arcprize.org/actions
"""

from __future__ import annotations

from typing import Any

import numpy as np
from arcengine import FrameDataRaw, GameAction, GameState

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


def _last_palette_frame(frame_data: FrameDataRaw) -> np.ndarray | None:
    frames = frame_data.frame
    if not frames:
        return None
    return np.asarray(frames[-1])


def _frame_to_rgb(frame: np.ndarray, scale: int) -> np.ndarray:
    from arc_agi.rendering import COLOR_MAP, frame_to_rgb_array

    return frame_to_rgb_array(0, frame, scale=scale, color_map=COLOR_MAP)


_KEY_ACTIONS: dict[str, GameAction] = {
    # WASD + arrows → ACTION1–4 (semantic up/down/left/right in the UI)
    "w": GameAction.ACTION1,
    "up": GameAction.ACTION1,
    "s": GameAction.ACTION2,
    "down": GameAction.ACTION2,
    "a": GameAction.ACTION3,
    "left": GameAction.ACTION3,
    "d": GameAction.ACTION4,
    "right": GameAction.ACTION4,
    # ACTION5
    " ": GameAction.ACTION5,
    "f": GameAction.ACTION5,
}


def run_interactive_matplotlib(environment: Any, *, scale: int = 6) -> int:
    """Open a matplotlib window; return number of env.step calls performed."""
    if plt is None:
        raise ImportError(
            "matplotlib is required for --mode human. Install with: uv add matplotlib"
        )

    import matplotlib as mpl

    # Matplotlib binds s→save, f→fullscreen, r→home, arrows→nav, etc. Clear
    # keymaps for this session so WASD / F / R reach the game.
    _no_mpl_keys = {k: [] for k in mpl.rcParams if str(k).startswith("keymap.")}

    total_env_steps = 0

    with mpl.rc_context(rc=_no_mpl_keys):
        fig, ax = plt.subplots(figsize=(6.5, 6.5))
        fig.canvas.manager.set_window_title("ARC-AGI-3 — human play")

        obs = environment.reset()
        if obs is None:
            raise RuntimeError("environment.reset() failed")

        pal = _last_palette_frame(obs)
        if pal is None:
            raise RuntimeError("no frame after reset")

        rgb = _frame_to_rgb(pal, scale)
        im = ax.imshow(rgb, origin="upper", interpolation="nearest")
        ax.set_axis_off()

        def _avail() -> set[int]:
            if obs is None or not obs.available_actions:
                return set()
            return set(obs.available_actions)

        def _refresh_title(msg: str = "") -> None:
            if obs is None:
                return
            st = obs.state.name if hasattr(obs.state, "name") else str(obs.state)
            a = obs.available_actions
            extra = f" {msg}" if msg else ""
            ax.set_title(
                f"{extra}state={st}  levels={obs.levels_completed}/{obs.win_levels}  "
                f"avail={a}\n"
                "WASD/Arrows 1–4  Space/F ACTION5  Click ACTION6  Ctrl/Cmd+Z undo  R reset  Q quit",
                fontsize=9,
            )

        def _paint() -> None:
            nonlocal obs
            pal2 = _last_palette_frame(obs) if obs else None
            if pal2 is not None:
                im.set_array(_frame_to_rgb(pal2, scale))
            _refresh_title()

        def _terminal() -> bool:
            if obs is None:
                return True
            return obs.state in (GameState.WIN, GameState.GAME_OVER)

        def _do_reset() -> None:
            nonlocal obs
            out = environment.reset()
            if out is None:
                _refresh_title("reset failed — ")
                fig.canvas.draw_idle()
                return
            obs = out
            _paint()
            fig.canvas.draw_idle()

        def _do_step(action: GameAction, data: dict[str, Any] | None = None) -> None:
            nonlocal obs, total_env_steps
            if obs is None:
                return
            if _terminal() and action not in (GameAction.ACTION7,):
                return
            if action.value not in _avail():
                _refresh_title(f"{action.name} unavailable — ")
                fig.canvas.draw_idle()
                return
            out = environment.step(
                action,
                data=data,
                reasoning={"source": "human_matplotlib"},
            )
            if out is None:
                _refresh_title("step failed — ")
                fig.canvas.draw_idle()
                return
            obs = out
            total_env_steps += 1
            _paint()
            fig.canvas.draw_idle()

        def on_key(event: Any) -> None:
            if event.key is None:
                return
            key = event.key

            if key in ("q", "escape"):
                plt.close(fig)
                return
            if key.lower() == "r":
                _do_reset()
                return

            if key in ("ctrl+z", "ctrl+Z", "cmd+z", "meta+z"):
                _do_step(GameAction.ACTION7)
                return

            act = _KEY_ACTIONS.get(key)
            if act is None and len(key) == 1:
                act = _KEY_ACTIONS.get(key.lower())
            if act is not None:
                _do_step(act)

        def on_click(event: Any) -> None:
            if event.inaxes != ax or event.xdata is None or event.ydata is None:
                return
            if event.button != 1:
                return
            if GameAction.ACTION6.value not in _avail():
                _refresh_title("ACTION6 unavailable — ")
                fig.canvas.draw_idle()
                return
            xd = float(event.xdata)
            yd = float(event.ydata)
            xi = int(np.clip(xd // scale, 0, 63))
            yi = int(np.clip(yd // scale, 0, 63))
            _do_step(GameAction.ACTION6, data={"x": xi, "y": yi})

        _refresh_title()
        fig.canvas.draw_idle()

        fig.canvas.mpl_connect("key_press_event", on_key)
        fig.canvas.mpl_connect("button_press_event", on_click)

        plt.tight_layout()
        plt.show(block=True)

    return total_env_steps
