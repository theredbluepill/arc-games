# Similarity report triage

[`similar_games_report.py`](similar_games_report.py) compares **one canonical package per stem** (default: prefer an 8-character hex version dir when present) using:

| Signal | Meaning |
|--------|---------|
| **meta/registry** | Jaccard overlap on `metadata.json` training fields + tags + [GAMES.md](../GAMES.md) row text (category, grid, description, actions). |
| **text** | Same bags plus module docstring and metadata description. |
| **code** | Jaccard on whitespace/comment-stripped tokens; **1.0** if full normalized source SHA256 matches. |
| **levels** | SHA256 of the `levels = …` assignment source (if parsable); **0** if either game has no `levels` assign. |

High **composite** scores are hints, not proof of redundancy.

## Labels in the report

- **tutorial_series** — `ez01`–`ez04`; similarity is expected.
- **same_prefix_numbered_family** — e.g. `fs01`/`fs02`/`fs03`; intentional rule variants.
- **cross_name_in_description** — one stem name appears in the other’s GAMES description (often “like X”).
- **suspicious_overlap** — `no` for tutorials and same-prefix families; `yes` means worth a human pass.

## Triage steps (per high-scoring pair)

1. **Read both `{stem}.py` docstrings and `step()`** — Is the rule difference clear from observation and fair per [AGENTS.md](../AGENTS.md)?
2. **Compare levels** — Same layout with a small rule delta can be valid (e.g. `ml02` / `ml03`). Same layout *and* same transition logic is a red flag.
3. **Smoke load** — `uv run python devtools/smoke_games.py` (or `run_game.py`) after any edit.

## Improvement matrix

| Finding | Action |
|---------|--------|
| Unrelated stems, high code + level fingerprint match | Differentiate rules, HUD, or level sets; avoid cosmetic-only benchmark IDs. |
| Intentional family, weak docs | Sharpen the GAMES.md row so the **one rule delta** is obvious; add “variant of `xy01`” where helpful. |
| Same mechanic, different stems | Prefer distinct failure modes, step budgets, or topology; state which cognitive skill each stem tests. |
| Metadata vs code mismatch | Align `training_metadata` / tags with real `step()` behavior. |

## Regenerating the report

```bash
uv run python devtools/similar_games_report.py --top-k 12 --min-score 0.25
```

Or run the same command from a local `Makefile` if you keep one (the repo gitignores `Makefile` so it stays out of version control).

Tune **weights** (`--w-meta`, `--w-text`, `--w-code`, `--w-level`) and **threshold** (`--min-score`) when a family dominates the list.

The Markdown report includes **Suspicious overlap components** (connected components over pairs marked suspicious). At the default `--min-score`, cross-family links are dense, so you often get **one large component**—use the sorted **pair table** for fine-grained work, or pass **`--suspicious-min-score 0.40`** (or higher) to build components from **stronger** edges only while keeping the pair table threshold unchanged. JSON field: `suspicious_components`; option echo: `options.suspicious_min_score`.

## Resolved notes (maintenance log)

- **`in01` / `pm01`**: Previously shared an identical `levels = …` block; **pm01** and **in01** now use distinct authored layouts (ink mazes vs prime-step corridors). Re-run the report and expect **lvl** similarity between them to drop.
- **`av01` / `sb01`**: Rules in code are the same “fall into empty below” step; **sb01** levels were rewritten to new geometry and **GAMES.md** spells out the shared rule vs distinct layouts / sprite color.
- **`sv*` vs `wm*`**: High **code** + **lvl** overlap is largely **shared boilerplate** and unrelated survival vs click mechanics—treat as a **false positive** unless a diff shows copied level data.
- **Registry pass**: Many **Variant of `xy01`** prefixes and pipe/HUD clarifications were added in [GAMES.md](../GAMES.md); plumbing stems gained distinct **metadata tags** / **physics_rules** strings.
- **wm\* vs sv\***: Identical `levels = [create_level(i) for i in range(1, 6)]` text caused a false **levels** match; **wm01–wm03** now use `(1, 2, 3, 4, 5)` so the fingerprint differs without changing gameplay.
- **Priority batch (coverage / dp–dv / meters / sand / P2 blurbs)**: [GAMES.md](../GAMES.md) revisit-rule leads for **va01, bd01, hm01, gl01, tr01, vp01, cf01**; **dp01**/**dv01** HUD corner cues + descriptions; **bt01**/**tm01** contrast + **bt01** HUD marker; **cq01**/**tw01**/**vp01**/**pw01**; **sp01**/**sp04**/**ab01** + metadata; **pb04**/**sk04** mechanics + grid **10×10**; adjacency/drill/melt/dig/swap; escort/chase; **gp01**/**lo01**/**lo05**; **bl01**/**rc01**, **fg01**/**kb01**, **pb01**/**sk01**, **lf01**/**rh01**, **rb01**/**tf01**.

## Reference stems

`vc33`, `ls20`, and `ft09` are omitted from the default scan (not in [GAMES.md](../GAMES.md) public table). Pass `--include-reference` to compare them.
