#!/usr/bin/env python3
"""R6 (EVALUATION_CRITERIA.md rev 7): independent validation of the complex label.

Answers the circularity objection (concern 8): the damage-signature "complex"
label must be checked against an *independent* criterion. We use the
localized-seed / periodic-localization detector (:mod:`caspectra.eval.gliders`),
a different observable from the twin-run damage-from-random-ICs signature, and
report agreement / false-positive / false-negative rates.

On the 88 ECAs there is also literature ground truth: the damage signature
selects exactly {54, 106, 110}, and {54, 110} are the canonical class-IV /
glider-supporting ECAs — so the ECA agreement is validation against human
knowledge, not a tautology. On range-2 (no literature ground truth) we report the
independent detector's agreement with the damage signature on a uniform sample,
with the known ether-front false negatives disclosed.

Usage::

    python scripts/validate_glider_signature.py --radius 1
    python scripts/validate_glider_signature.py --radius 2 --n-rules 300
"""

from __future__ import annotations

import argparse

import numpy as np

from caspectra.ca.eca import independent_rules
from caspectra.ca.range_ca import sample_rules
from caspectra.eval.dynamics import damage_spreading_features
from caspectra.eval.gliders import is_glider, localized_seed_metrics
from caspectra.eval.regimes import COMPLEX_SIGNATURE, COMPLEX_SIGNATURE_ECA, is_complex
from caspectra.utils import ensure_dir, save_json


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="R6 independent glider validation (rev 7).")
    p.add_argument("--radius", type=int, default=1)
    p.add_argument("--n-rules", type=int, default=300, help="Sampled rules for radius >= 2.")
    p.add_argument("--width", type=int, default=127, help="Ring for the damage signature.")
    p.add_argument("--seed-width", type=int, default=255, help="Ring for the localized-seed test.")
    p.add_argument("--n-pairs", type=int, default=256)
    p.add_argument("--output-dir", default="runs/analysis/glider_validation")
    return p.parse_args()


def _rates(sig: np.ndarray, det: np.ndarray) -> dict:
    """Agreement / FP / FN of the detector relative to the damage signature, over
    rules where the detector applies (finite ``det``)."""
    ok = np.isfinite(det.astype(float))
    s, d = sig[ok].astype(bool), det[ok].astype(bool)
    n = int(ok.sum())
    agree = float(np.mean(s == d)) if n else float("nan")
    # "positive" = damage-signature complex; FP/FN of the detector vs that label.
    fp = float(np.mean(d & ~s)) if n else float("nan")
    fn = float(np.mean(~d & s)) if n else float("nan")
    return {
        "n_detector_applicable": n,
        "agreement": round(agree, 4),
        "detector_false_positive_rate": round(fp, 4),
        "detector_false_negative_rate": round(fn, 4),
    }


def main() -> None:
    args = parse_args()
    out = ensure_dir(args.output_dir)
    radius = args.radius

    if radius == 1:
        rules = independent_rules()
        signature = COMPLEX_SIGNATURE_ECA
    else:
        rules = sample_rules(args.n_rules, radius, np.random.default_rng(0))
        signature = COMPLEX_SIGNATURE

    sig_flags, det_flags, records = [], [], []
    for r in rules:
        if radius == 1:
            feats = damage_spreading_features(
                int(r), width=args.width, n_pairs=args.n_pairs, rng=np.random.default_rng(int(r))
            )
        else:
            from caspectra.ca.range_ca import RangeCA

            feats = damage_spreading_features(
                simulator=RangeCA(int(r), radius),
                width=args.width,
                n_pairs=args.n_pairs,
                rng=np.random.default_rng(int(r)),
            )
        sig = is_complex(feats, signature)
        m = localized_seed_metrics(
            int(r), radius, width=args.seed_width, rng=np.random.default_rng(int(r) + 7)
        )
        det = is_glider(m)
        sig_flags.append(sig)
        det_flags.append(np.nan if det is None else det)
        if sig or det:
            records.append(
                {
                    "rule": int(r),
                    "damage_complex": bool(sig),
                    "detector_glider": None if det is None else bool(det),
                    **m,
                }
            )

    sig_arr = np.array(sig_flags, dtype=bool)
    det_arr = np.array(det_flags, dtype=float)
    summary = {
        "radius": radius,
        "n_rules": len(rules),
        "damage_signature_complex_count": int(sig_arr.sum()),
        "damage_signature_complex_fraction": round(float(sig_arr.mean()), 4),
        "rates_vs_damage_signature": _rates(sig_arr, det_arr),
        "flagged_rules": records[:60],
    }
    if radius == 1:
        summary["eca_damage_signature_set"] = sorted(int(r) for r, s in zip(rules, sig_flags) if s)

    save_json(summary, out / f"summary_r{radius}.json")
    print(f"[r6] radius={radius}  {len(rules)} rules")
    print(f"[r6] damage-signature complex: {int(sig_arr.sum())} " f"({100 * sig_arr.mean():.1f}%)")
    if radius == 1:
        print(
            f"[r6] ECA damage-signature set: {summary['eca_damage_signature_set']} "
            f"(literature class-IV anchors 54, 110)"
        )
    print(f"[r6] independent detector vs damage signature: {summary['rates_vs_damage_signature']}")
    print(f"[r6] wrote {out}/summary_r{radius}.json")


if __name__ == "__main__":
    main()
