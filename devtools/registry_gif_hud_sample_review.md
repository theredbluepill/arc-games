# Registry GIF — sample HUD review (generate-arc-game-gif skill)

This supplements the machine-readable dispatch map in [`registry_gif_dispatch.csv`](registry_gif_dispatch.csv). Regenerate the CSV with:

`uv run python scripts/registry_gif_dispatch_report.py`

The skill checklist lives in [`.agents/skills/generate-arc-game-gif/SKILL.md`](../.agents/skills/generate-arc-game-gif/SKILL.md) (level progression, **real** fail legibility in `render_interface`, non-static HUD, ACTION6 click feedback in 64×64 space, no recorder-only FX).

## Aggregate counts (250 stems)

From `registry_gif_dispatch.csv` (see `dispatch_bucket` column):

| Bucket | Count | Notes |
|--------|------:|-------|
| `generic` | 173 | BFS + `inject_wall_fails` (wall/OOB bumps), optional showcase fallback |
| `rk_jw` | 12 | `registry_rk_jw_gif` planners |
| `pk_ec` | 12 | `registry_pk_ec_gif.PK_EC_RECORDERS` |
| `mechanic_showcase` | 6 | `nw01`, `bd01`, `gr01`, `dt01`, `wk01`, `rf01` |
| `push_solver` | 4 | `pb01`, `pb02`, `sk01`, `sk02` |
| `switch_door` | 3 | `fs01`–`fs03` |
| `portal_pair` | 3 | `tp01`–`tp03` |
| `ice_slide` | 3 | `ic01`–`ic03` |
| `visit_all` | 3 | `va01`–`va03` |
| Remaining single-stem buckets | 31 | e.g. `pb03`, `mo01`, `lw01`, `ml01`, `tw01`, `fc01`, `gc01`, … |

**`generic` + click/ACTION6 hint** (from `actions_uses_click_or_action6` in CSV): **94** stems. These are the highest-risk for “registry GIF ≠ skill-complete” unless the HUD shows designed failures and the generic recorder happens to surface them.

## Sample stems vs skill checklist

Abbreviations: **L** = level progression readable on frame, **F** = distinct fail / game-over / budget feedback in HUD (not only grid), **D** = counters/modes change via `update`, **A6** = click/ping in final frame space for several frames where ACTION6 matters.

| Stem | Dispatch | L | F | D | A6 | Notes |
|------|----------|---|---|---|-----|-------|
| `tt01` | generic | Y | Y | Y | n/a | `Tt01UI`: level dots, target ticks, `_r_bar` for WIN/GAME_OVER ([`tt01.py`](../environment_files/tt01/63be02fb/tt01.py)). Generic capture still mostly wall-bump “fails”. |
| `ju01` | generic | Y | partial | Y | n/a | Movement-only; fail states depend on hazard rules—verify HUD tints if any. |
| `wm01` | generic | Y | Y | Y | Y | `Wm01UI`: level color, lives, checkpoint dots, **`set_click`** yellow + ([`wm01.py`](../environment_files/wm01/63be02fb/wm01.py)). Strong GIF-ready UI; generic recorder may not show mole miss / life loss beats reliably. |
| `pt01` | generic | Y | partial | Y | Y | `Pt01UI` has `set_click` + pattern HUD ([`pt01.py`](../environment_files/pt01/63be02fb/pt01.py)). |
| `ff01` | generic | Y | partial | Y | Y | Flood-fill + sq01-style click ripple (per `GAMES.md`); verify `set_click` / frame math like `sq01`. |
| `sq01` | generic | Y | Y | Y | Y | Sequence + lives + **`_grid_to_frame_pixel`** for clicks ([`sq01.py`](../environment_files/sq01/63be02fb/sq01.py)); skill reference family. |
| `mm01` | generic | Y | Y | Y | Y | Skill cites mm01 for ACTION6 UX; timer / match feedback in UI. |
| `bn01` | generic | Y | partial | Y | n/a | Beacon/flag counts in `Bn01UI`; wrong-flag lose is a **rule** fail—generic BFS will not deliberately trigger it. |
| `ck01` | generic | partial | partial | weak | no | `Ck01UI` is a **single** corner pixel (green vs red) for last test result ([`ck01.py`](../environment_files/ck01/63be02fb/ck01.py)); no click ping; limited “story” on frame for multi-level + two fail types. |
| `gp01` | `gp01` | Y | partial | Y | Y | Dedicated recorder in `registry_ex_gp_lo_gif`; UI tuned for paint/hints. |

## Takeaways

1. **Structural HUD**: Sampled games define `RenderableUserDisplay` subclasses with real `render_interface` / `update` usage; weakest sampled HUD surface is **`ck01`** (minimal strip).
2. **Skill vs `generic` recorder**: Even strong UIs (`wm01`, `sq01`, `mm01`) rely on **game logic during capture** for true fail clips; **`inject_wall_fails`** alone does not satisfy the skill’s “1–2 failed cases” requirement.
3. **Next steps for strict compliance**: For high-value `generic` + click stems, extend **`registry_gif_lib`** / **`registry_gif_overrides.json`** (per skill)—after confirming the UI exposes lose/budget/test states clearly.

Dispatch labels are defined by **`registry_gif_dispatch_bucket`** in [`scripts/registry_gif_lib.py`](../scripts/registry_gif_lib.py) (built-in branches + [`registry_gif_recorders.py`](../scripts/registry_gif_recorders.py) for merged per-stem recorders). Add new specialized stems via **`REGISTRY_RECORDERS`** in a helper module and one import line in **`_build_tables`** there.
