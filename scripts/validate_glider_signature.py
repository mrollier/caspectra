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
from caspectra.eval.gliders import GLIDER_SIGNATURE, is_glider, localized_seed_metrics
from caspectra.eval.regimes import COMPLEX_SIGNATURE, COMPLEX_SIGNATURE_ECA, is_complex
from caspectra.utils import ensure_dir, save_json

# ECA literature ground truth (rule_labels_PROVENANCE.md): the canonical class-IV /
# glider-supporting elementary rules under the reflect/complement orbit. Rule 106
# is a documented borderline case and is reported separately, not as ground truth.
ECA_CLASS_IV_TRUTH = {54, 110}
ECA_CLASS_IV_BORDERLINE = {106}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="R6 independent glider validation (rev 7).")
    p.add_argument("--radius", type=int, default=1)
    p.add_argument("--n-rules", type=int, default=300, help="Sampled rules for radius >= 2.")
    p.add_argument("--width", type=int, default=127, help="Ring for the damage signature.")
    p.add_argument("--seed-width", type=int, default=255, help="Ring for the localized-seed test.")
    p.add_argument("--n-pairs", type=int, default=256)
    p.add_argument(
        "--horizon",
        type=int,
        default=None,
        help="Rev-13 M12: override the derived damage horizon. The default differs "
        "between radii at fixed width (62 for ECA, 30 for radius two), so cross-space "
        "prevalence comparisons are horizon-confounded; --horizon 30 matches them.",
    )
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


def _confusion(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Full confusion matrix + rate summary of ``y_pred`` against ``y_true``.

    Concern 9: raw agreement is misleading when positives are rare, so we report
    the counts and the rate quartet (sensitivity, specificity, precision, F1,
    balanced accuracy) explicitly. Restricted to rules where ``y_pred`` is finite.
    """
    ok = np.isfinite(y_pred.astype(float))
    t, p = y_true[ok].astype(bool), y_pred[ok].astype(bool)
    tp = int(np.sum(t & p))
    fp = int(np.sum(~t & p))
    tn = int(np.sum(~t & ~p))
    fn = int(np.sum(t & ~p))
    sens = tp / (tp + fn) if (tp + fn) else float("nan")
    spec = tn / (tn + fp) if (tn + fp) else float("nan")
    prec = tp / (tp + fp) if (tp + fp) else float("nan")
    f1 = (
        2 * prec * sens / (prec + sens)
        if prec and sens and np.isfinite(prec) and np.isfinite(sens)
        else float("nan")
    )
    bal = np.nanmean([sens, spec])
    return {
        "n": int(ok.sum()),
        "n_positive": tp + fn,
        "n_negative": tn + fp,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "sensitivity": round(sens, 4),
        "specificity": round(spec, 4),
        "precision": round(prec, 4),
        "f1": round(f1, 4),
        "balanced_accuracy": round(float(bal), 4),
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
                int(r),
                width=args.width,
                n_pairs=args.n_pairs,
                rng=np.random.default_rng(int(r)),
                n_steps=args.horizon,
            )
        else:
            from caspectra.ca.range_ca import RangeCA

            feats = damage_spreading_features(
                simulator=RangeCA(int(r), radius),
                width=args.width,
                n_pairs=args.n_pairs,
                rng=np.random.default_rng(int(r)),
                n_steps=args.horizon,
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
        "detector_settings": (
            dict(GLIDER_SIGNATURE._asdict())
            if hasattr(GLIDER_SIGNATURE, "_asdict")
            else str(GLIDER_SIGNATURE)
        ),
        "damage_signature_complex_count": int(sig_arr.sum()),
        "damage_signature_complex_fraction": round(float(sig_arr.mean()), 4),
        # Concern 9: full confusion matrix of detector vs the damage signature,
        # not just raw agreement (which rare positives make misleading).
        "detector_vs_damage_signature_confusion": _confusion(sig_arr, det_arr),
        "rates_vs_damage_signature": _rates(sig_arr, det_arr),
        "detector_failure_modes": {
            "rule_54": "ether front advances at light speed; localized-seed detector "
            "misses it (disclosed, not tuned away)"
        },
        "flagged_rules": records[:60],
    }
    if radius == 1:
        rule_arr = np.array([int(r) for r in rules])
        truth = np.isin(rule_arr, list(ECA_CLASS_IV_TRUTH))
        summary["eca_damage_signature_set"] = sorted(int(r) for r, s in zip(rules, sig_flags) if s)
        summary["eca_literature_class_iv_truth"] = sorted(ECA_CLASS_IV_TRUTH)
        # Both observables scored against the literature ground truth.
        summary["damage_signature_vs_literature_confusion"] = _confusion(
            truth, sig_arr.astype(float)
        )
        summary["detector_vs_literature_confusion"] = _confusion(truth, det_arr)

    save_json(summary, out / f"summary_r{radius}.json")
    print(f"[r6] radius={radius}  {len(rules)} rules")
    print(f"[r6] damage-signature complex: {int(sig_arr.sum())} " f"({100 * sig_arr.mean():.1f}%)")
    if radius == 1:
        print(
            f"[r6] ECA damage-signature set: {summary['eca_damage_signature_set']} "
            f"(literature class-IV truth {sorted(ECA_CLASS_IV_TRUTH)}, "
            f"borderline {sorted(ECA_CLASS_IV_BORDERLINE)})"
        )
        print(
            "[r6] damage-signature vs literature: "
            f"{summary['damage_signature_vs_literature_confusion']}"
        )
        print(f"[r6] detector vs literature:        {summary['detector_vs_literature_confusion']}")
    print(
        "[r6] detector vs damage signature confusion: "
        f"{summary['detector_vs_damage_signature_confusion']}"
    )
    print(f"[r6] wrote {out}/summary_r{radius}.json")


if __name__ == "__main__":
    main()
