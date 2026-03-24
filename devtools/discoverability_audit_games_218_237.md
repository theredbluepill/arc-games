# Discoverability audit — GAMES.md rows 218–237

Per [`.agents/skills/check-arc-game-discoverable/SKILL.md`](../.agents/skills/check-arc-game-discoverable/SKILL.md): cold-start learning from **observation + actions** only (not `GAMES.md` / metadata).

| Stem | Verdict | Notes / gaps |
|------|---------|----------------|
| sy04 | **unknown** (playtest) | Diagonal template vs mirror half; **move budget** + progress ticks in [`Sy04UI`](environment_files/sy04/v1/sy04.py); `player_block` toggles on upper triangle. |
| dm04 | **unknown** (playtest) | L-tromino triple pick; spatial. |
| pk02 | **unknown** (playtest) | Edge-claim ribbon; two-click pattern. |
| fl04 | **unknown** (playtest) | `player` + path; A/B and length cap from HUD/layout. |
| lw04 | **unknown** (playtest) | Same family as fl04 with turn budget. |
| sf04 | **unknown** (playtest) | Rotate stencil + paint; HUD shows rotation / progress ([`Sf04UI`](environment_files/sf04/v1/sf04.py)). |
| sp04 | **unknown** (playtest) | Sandpile + sinks; step bar + target sum bar ([`Sp04UI`](environment_files/sp04/v1/sp04.py)). |
| ll04 | **unknown** (playtest) | Torus Life + step/toggle. |
| ab01 | **unknown** (playtest) | Stability + **(total mod P) == R**; P/R and mod strip in [`Ab01UI`](environment_files/ab01/v1/ab01.py). |
| df04 | **unknown** (playtest) | Diffuse + vent; band probe + step bar + click ping ([`Df04UI`](environment_files/df04/v1/df04.py)). |
| ih01 | **unknown** (playtest) | Chill + heater toggles; warm count HUD ([`Ih01UI`](environment_files/ih01/v1/ih01.py)). |
| tc04 | **unknown** (playtest) | Conveyor step + rotate arrows. |
| zm04 | **unknown** (playtest) | Strain switch + spread + block; infection bar ([`Zm04UI`](environment_files/zm04/v1/zm04.py)). |
| pu04 | **unknown** (playtest) | Pipe cycle on cells; plumbing layout. |
| pd04 | **unknown** (playtest) | Plus junction toggles. |
| ck04 | **unknown** (playtest) | Directed wire rotate to exit. |
| rp04 | **unknown** (playtest) | Pulse + relay toggle; lamp progress ([`Rp04UI`](environment_files/rp04/v1/rp04.py)). |
| ph04 | **unknown** (playtest) | 1×8 row op + mod R; target row + steps in [`Ph04UI`](environment_files/ph04/v1/ph04.py). |
| ml04 | **unknown** (playtest) | Stepped laser + mirror cycle. |
| pj04 | **unknown** (playtest) | Bolt + mirror place. |

**Blind playtest:** Not run in this pass. To claim **yes**, use the skill’s short protocol on level 1 without docs.

**Concrete gaps (code review):** None flagged that hide win-critical state entirely; sims above expose counters/bars suitable for hypothesis testing, subject to playtest.

---

## Registry GIF follow-up ([`generate-arc-game-gif`](../.agents/skills/generate-arc-game-gif/SKILL.md))

| Stem | Recorder | Notes |
|------|----------|--------|
| dm04, pk02, fl04, lw04, ll04, pu04, pd04, ck04, ml04, pj04 | `registry_gif_lib` generic | Player or exploration path; batch `ok` in prior runs. |
| ab01, sy04, ph04, sp04, zm04, rp04, tc04, sf04, df04, ih01 | [`registry_218_gif.py`](../scripts/registry_218_gif.py) | Scripted **ACTION5/6** tours + resets on WIN/GAME_OVER for stems that had very short generic captures (no `player` BFS anchor). |
| Overrides | [`registry_gif_overrides.json`](../scripts/registry_gif_overrides.json) | Existing **sf04, sy04, sp04, ab01, zm04, tc04, df04, ih01** tuning retained; **ph04** adds `registry_218_ph04_steps` / `gif_duration_ms`. |

Refresh command: `uv run python scripts/render_arc_game_gif.py --from sy04 --through pj04`.
