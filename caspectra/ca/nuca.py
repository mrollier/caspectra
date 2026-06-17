"""Non-uniform cellular automata (nuCA) — interface stub only.

This documents the eventual extension point (BUILD_BRIEF.md §0, §3.9, §7) without
building it. A non-uniform CA mixes two ECA rules across the lattice: each cell
follows either ``rule_a`` or ``rule_b`` according to a per-cell ``rule_mask``
(e.g. a 50/50 mixture of rule 110 and rule 54). The phenotype/behaviour of such
mixtures is the eventual research target; the validation work is done first on
uniform ECAs.

The class deliberately mirrors :class:`caspectra.ca.eca.ECASimulator`'s
``evolve`` / ``random_diagram`` surface so the rest of the pipeline (dataset,
training, evaluation) can treat it as a drop-in source of spacetime diagrams
once implemented. Every simulation method currently raises
:class:`NotImplementedError`.

**Intended implementation (not built yet):** build both 8-entry rule tables;
at each time step compute, for every cell, the next value from its 3-cell
neighbourhood under *its own* rule (selected by ``rule_mask``), under periodic
boundary conditions — i.e. the same vectorised update as the ECA but with the
rule table gathered per-cell from the mask.
"""

from __future__ import annotations

import numpy as np

__all__ = ["NonUniformCA"]


class NonUniformCA:
    """A two-rule non-uniform CA (interface stub — see module docstring).

    Parameters
    ----------
    rule_a, rule_b:
        The two Wolfram rule numbers (0-255) to mix.
    rule_mask:
        A 1-D array of length ``width`` assigning each cell to a rule: ``0`` ->
        ``rule_a``, ``1`` -> ``rule_b``.
    """

    def __init__(self, rule_a: int, rule_b: int, rule_mask: np.ndarray) -> None:
        self.rule_a = rule_a
        self.rule_b = rule_b
        self.rule_mask = np.asarray(rule_mask, dtype=np.uint8)

    def evolve(self, initial_row: np.ndarray, n_steps: int) -> np.ndarray:
        """Evolve a non-uniform CA. **Not implemented** — extension point."""
        raise NotImplementedError(
            "NonUniformCA is an interface stub (BUILD_BRIEF.md §3.9, §7). "
            "Implement per-cell rule selection from rule_mask before use."
        )

    def random_diagram(self, width: int, n_steps: int, rng: np.random.Generator) -> np.ndarray:
        """Evolve from a random initial row. **Not implemented** — extension point."""
        raise NotImplementedError("NonUniformCA is an interface stub (BUILD_BRIEF.md §3.9, §7).")
