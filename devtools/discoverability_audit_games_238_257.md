# Discoverability audit — GAMES.md rows 238–257

Per [`.agents/skills/check-arc-game-discoverable/SKILL.md`](../.agents/skills/check-arc-game-discoverable/SKILL.md): cold-start learning from **observation + actions** only (not `GAMES.md` / metadata).

| Stem | Verdict | Notes / gaps |
|------|---------|----------------|
| wm04 | **unknown** (playtest) | Mole/hole + hit counter + penalty strip; goal inferable with play. Confirm without prior. |
| sg04 | **unknown** (playtest) | **Fixed:** commit budget now shown as 8-segment light-blue bar (`Sg04UI`, row `h-4`). Alternating arm + dual targets still need one session to interpret. |
| ng04 | **unknown** (playtest) | Multi-layer path edit; logic-heavy. |
| bn04 | **unknown** (playtest) | Axis reveal + flags; family cue from layout. |
| sk04 | **unknown** (playtest) | Fixed player + adjacency pull; motion teaches pull. |
| pb04 | **unknown** (playtest) | Winch direction HUD + pads/crates; no movement. |
| rr01 | **unknown** (playtest) | Heading + ramp tick; green exit visible. |
| hn04 | **unknown** (playtest) | Classic Hanoi with peg select + pick/drop + reject flash. |
| kv04 | **unknown** (playtest) | Two ladders / branch cycling + verify. |
| rs04 | **unknown** (playtest) | XOR-phase collect; abstract HUD. |
| ms04 | **unknown** (playtest) | Edge-adjacent clues + flags; minesweeper-like deduction. |
| cw01 | **unknown** (playtest) | 2-SAT-style toggles; `_ticks` 8 vs 2 when satisfied teaches partial state. |
| cx01 | **unknown** (playtest) | Graph cut / gates + S–T. |
| cu01 | **unknown** (playtest) | Tool toggle + place; cover yellow. |
| cv01 | **unknown** (playtest) | List coloring by click-cycle. |
| mm04 | **unknown** (playtest) | Memory match + peek; familiar genre. |
| mm05 | **unknown** (playtest) | Sticky match adjacency rule; needs play to learn constraint. |
| fe02 | **unknown** (playtest) | Vote tallies + ratify + `a,b,c`; rich HUD but mapping vote→rule is abstract. |

**Blind playtest:** No session was run in this pass. To claim **yes** for any stem, run the skill’s short protocol (level 1, few minutes, then elicit goal + one action semantics without docs).

**Remediation already applied**

- **sg04** — Symptom: step budget invisible before `lose()`. Fix: budget bar in `environment_files/sg04/v1/sg04.py` (`Sg04UI.render_interface`, `update(..., left=, max_steps=)`).

---

## Registry GIF follow-up ([`generate-arc-game-gif`](../.agents/skills/generate-arc-game-gif/SKILL.md))

| Stem | Recorder | Notes |
|------|----------|--------|
| wm04–pb04, rr01–ms04, cx01–cv01 | `registry_gif_lib` generic | Batch `ok`; eyeball for fail legibility. |
| mm04, mm05, fe02 | `registry_mm_fe_gif` | Scripted; **fe02** `target_levels: 4` in [`registry_gif_overrides.json`](../scripts/registry_gif_overrides.json). |
| sg04, cw01 | [`registry_sg_cw_gif.py`](../scripts/registry_sg_cw_gif.py) | No `player` on grid — avoids 64-frame generic stub; **sg04** shows L1 clear + L2 timeout; **cw01** misclicks + greedy clause clears. |
| Overrides | [`registry_gif_overrides.json`](../scripts/registry_gif_overrides.json) | **sg04** / **cw01** timing + **fe02** depth as above. |

Refresh command: `uv run python scripts/render_arc_game_gif.py --from wm04 --through fe02`.
