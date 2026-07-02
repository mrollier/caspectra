"""Leave-rules-out splits for the amortization-transfer gate (criterion 6).

Criterion 6 (EVALUATION_CRITERIA.md rev 2) requires the invariant regressor to
generalize to rules never seen in training, so the split must hold out whole
*rules*, not initial conditions. The split is stratified by Wolfram class so
every behaviour regime appears on both sides — with one deliberate exception:
class IV has only two members, {54, 110}, so per the 2026-07-02 decision rule
**110 is forced into the hold-out set and 54 into training** (the headline
number then includes transfer to an unseen complex rule; the swapped variant is
run afterwards as a robustness check).
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

__all__ = ["leave_rules_out_split"]


def leave_rules_out_split(
    rules: Sequence[int] | np.ndarray,
    class_labels: Sequence[int] | np.ndarray,
    *,
    holdout_fraction: float = 0.2,
    seed: int = 0,
    force_holdout: Sequence[int] = (110,),
    force_train: Sequence[int] = (54,),
) -> tuple[list[int], list[int]]:
    """Split ``rules`` into (train, holdout), stratified by ``class_labels``.

    Within each class, ``round(holdout_fraction * class_size)`` rules go to the
    hold-out set (at least one when the class has ≥ 2 free members), after the
    forced assignments are honoured. Returns sorted lists; every rule appears in
    exactly one side.
    """
    rules = [int(r) for r in rules]
    class_labels = np.asarray(class_labels)
    if len(rules) != len(class_labels):
        raise ValueError("rules and class_labels must have equal length")
    forced_holdout = {int(r) for r in force_holdout}
    forced_train = {int(r) for r in force_train}
    if forced_holdout & forced_train:
        raise ValueError(f"rules forced both ways: {sorted(forced_holdout & forced_train)}")
    unknown = (forced_holdout | forced_train) - set(rules)
    if unknown:
        raise ValueError(f"forced rules not in the rule list: {sorted(unknown)}")

    rng = np.random.default_rng(seed)
    holdout: set[int] = set(forced_holdout)
    for cls in np.unique(class_labels):
        members = [r for r, c in zip(rules, class_labels) if c == cls]
        free = [r for r in members if r not in forced_holdout and r not in forced_train]
        already = sum(1 for r in members if r in forced_holdout)
        n_target = int(round(holdout_fraction * len(members)))
        n_pick = max(0, n_target - already)
        if n_pick == 0 and already == 0 and len(free) >= 2:
            n_pick = 1  # every class contributes at least one hold-out rule
        n_pick = min(n_pick, len(free))
        holdout.update(int(r) for r in rng.choice(free, size=n_pick, replace=False))

    train = sorted(set(rules) - holdout)
    return train, sorted(holdout)
