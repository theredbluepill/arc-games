"""Wave 2 — Lights-Out–style linear algebra (GF(2)).

Orthogonal neighbor toggles on a **full** ``n×n`` torus-free board admit an ``O(n^6)`` Gaussian
elimination solver. **Walls / masks** in authored ``lo01``–``lo05`` levels change the operator per
cell, so the harness defaults to :func:`solvers.engine_bfs.engine_bfs_single_level` with
``allowed_action_ids={6}`` for those stems.

To add a fast path: export per-level toggle masks from the game module and build the sparse
GF(2) matrix row-per-click.
"""

from __future__ import annotations


def nullspace_hint_orth_full_grid(n: int) -> str:
    """Return a short note about kernel dimension for classic orthogonal Lights Out on ``n×n``."""
    # Parity / dimension facts are textbook; we only document intent for authors.
    return f"orth_full_grid_{n}x{n}: use GF(2) with (I+A) x = b; walls require per-level matrix."
