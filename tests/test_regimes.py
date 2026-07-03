"""Tests for eval/regimes.py — the pre-registered complex signatures (M4)."""

from __future__ import annotations

import numpy as np

from caspectra.ca.eca import independent_rules
from caspectra.ca.range_ca import RangeCA, embed_eca
from caspectra.eval.dynamics import damage_spreading_features
from caspectra.eval.regimes import (
    COMPLEX_SIGNATURE_ECA,
    complex_mask,
    curated_anchors,
    is_complex,
)


def test_eca_signature_selects_class_iv_on_ecas() -> None:
    """Provenance: across the 88 ECA reps the ECA-protocol signature selects
    exactly the canonical class-IV set {54, 106, 110} — no additive/chaotic
    false positives. This is the calibration the method was validated against."""
    reps = independent_rules()
    targets = np.stack(
        [
            damage_spreading_features(r, width=127, n_pairs=256, rng=np.random.default_rng(r))
            for r in reps
        ]
    )
    flagged = [r for r, m in zip(reps, complex_mask(targets, COMPLEX_SIGNATURE_ECA)) if m]
    assert flagged == [54, 106, 110]


def test_range2_signature_includes_class_iv_excludes_order_and_chaos() -> None:
    """M4 primary calibration on the range-2 protocol (embedded anchors): the
    class-IV cluster is flagged; clear order and clear chaos are not."""
    embedded = {r: RangeCA(embed_eca(r, 2), 2) for r in (0, 204, 184, 18, 30, 90, 54, 110, 106)}
    v = {
        r: damage_spreading_features(
            simulator=sim, width=127, n_pairs=256, rng=np.random.default_rng(r)
        )
        for r, sim in embedded.items()
    }
    for r in (54, 110, 106):  # class IV + borderline -> complex
        assert is_complex(v[r]), f"rule {r} should be flagged complex under range-2 protocol"
    for r in (0, 204, 184, 18, 30, 90):  # order / traffic / chaos / additive-ballistic -> not
        assert not is_complex(v[r]), f"rule {r} should NOT be flagged complex"


def test_is_complex_default_is_range2() -> None:
    # range-2 complex sits at sub-ballistic rate ~0.2 with high survival.
    assert is_complex(np.array([0.96, 0.10, 0.22, 0.52]))
    assert not is_complex(np.array([1.0, 0.30, 0.99, 0.26]))  # ballistic additive
    assert not is_complex(np.array([0.60, 0.10, 0.22, 0.52]))  # survival too low
    assert not is_complex(np.array([0.0, 0.0, 0.0, 0.0]))  # dead


def test_curated_anchors_are_valid_range2_rules() -> None:
    anchors = curated_anchors(2)
    assert set(anchors) >= {"eca54_complex", "eca110_complex"}
    assert all(0 <= r < 2**32 for r in anchors.values())
