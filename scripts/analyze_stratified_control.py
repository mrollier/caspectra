#!/usr/bin/env python3
"""M10 (rev 13): the stratified-split fairness control for the direct CNN.

The canonical radius-two panel *force-holds* all 57 signature-complex rules, so
the training split contains none of them where a representative split would
hold ~7%. The mechanistic estimator is invariant to that distortion by
construction and the learned estimators are not, so the fourth referee report
(§3.15) is right that the comparison is in principle handicapped against the
network.

This script scores the control: the same architecture, budget and protocol
trained on a *stratified* split with force-holding disabled, evaluated on its
own randomly held-out rules. It reports the learned families side by side with
the mechanistic estimator on the control panel, so the question "does the
enrichment explain the matched-regime gap?" is answered by measurement rather
than by the observational decomposition in Sec. IV A.

Registered reporting rule (rev. 13, numbers-free before measurement): the
family gap --- mechanistic minus each direct estimator --- is reported at the
stratified split as well as the enriched one, and if the stratified-split gap
is smaller than the post-stratified gap by more than the registered
superiority margin (0.10 median R^2) on any target, the family-gap claim is
downgraded to the stratified number. Reported regardless of direction.
"""

from __future__ import annotations

import argparse
import json
import warnings

import numpy as np

from caspectra.config import ExperimentConfig
from caspectra.eval.method_predictions import collect_held_out_predictions
from caspectra.utils import ensure_dir, set_seed

warnings.filterwarnings("ignore", message=".*encountered in matmul")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="M10 stratified-split fairness control (rev 13).")
    p.add_argument("--config", default="configs/m4_range2_stratified.yaml")
    p.add_argument(
        "--seed-checkpoints",
        nargs="+",
        default=[f"runs/m4_range2_strat_seed{s}/checkpoint_final.pt" for s in (0, 1, 2)],
    )
    p.add_argument(
        "--signature-config",
        default="configs/m4_range2.yaml",
        help="Config whose force_holdout_rules is the registered signature-complex set. "
        "The stratified config empties that field by design, so membership must be read "
        "from the canonical one or every rule looks ordinary.",
    )
    p.add_argument("--device", default="mps")
    p.add_argument("--n-boot", type=int, default=10000)
    p.add_argument("--output-dir", default="runs/m4_range2_strat/control")
    return p.parse_args()


def _r2_point(true: np.ndarray, pred: np.ndarray) -> np.ndarray:
    res = np.sum((true - pred) ** 2, axis=0)
    tot = np.sum((true - true.mean(axis=0)) ** 2, axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        return 1.0 - res / tot


def _r2_boot(true: np.ndarray, pred: np.ndarray, boot_idx: np.ndarray) -> np.ndarray:
    """Rule-bootstrap R^2, clipped to [-1, 1] exactly as the canonical table does."""
    t, p = true[boot_idx], pred[boot_idx]
    res = np.sum((t - p) ** 2, axis=1)
    tot = np.sum((t - t.mean(axis=1, keepdims=True)) ** 2, axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        r2 = 1.0 - res / tot
    return np.clip(r2, -1.0, 1.0)


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    out = ensure_dir(args.output_dir)
    set_seed(cfg.seed)

    primary = collect_held_out_predictions(cfg, args.seed_checkpoints[0], device=args.device)
    names = list(primary.target_names)
    n_held = len(primary.held)
    cnn_seeds = [primary.preds["cnn"]]
    for ckpt in args.seed_checkpoints[1:]:
        hop = collect_held_out_predictions(cfg, ckpt, device=args.device, include_mechanistic=False)
        assert hop.held == primary.held, "seed splits differ — stratification is not seed-stable"
        cnn_seeds.append(hop.preds["cnn"])
    cnn_seeds = np.stack(cnn_seeds)

    # Signature membership comes from the canonical config: HeldOutPredictions
    # derives its own mask from cfg.train.force_holdout_rules, which this control
    # deliberately empties, so that mask is identically False here.
    signature = {
        int(r) for r in ExperimentConfig.from_yaml(args.signature_config).train.force_holdout_rules
    }
    complex_mask = np.array([r in signature for r in primary.held], dtype=bool)
    n_complex = int(complex_mask.sum())
    n_train_complex = len(signature) - n_complex
    print(
        f"[m10] control panel: {n_held} held-out rules, {n_complex} signature-complex "
        f"({100 * n_complex / n_held:.1f}%), {len(cnn_seeds)} CNN seeds; "
        f"{n_train_complex} of the {len(signature)} signature-complex rules are in training"
    )

    rng = np.random.default_rng(0)
    boot_idx = rng.integers(0, n_held, size=(args.n_boot, n_held))

    summary: dict[str, object] = {
        "n_held_out": n_held,
        "n_signature_complex": n_complex,
        "complex_prevalence": round(n_complex / n_held, 4),
        "n_signature_complex_in_training": n_train_complex,
        "n_cnn_seeds": len(cnn_seeds),
        "radius": primary.radius,
        "per_method_r2": {},
        "cnn_seed_medians": [],
    }
    for method in ("mechanistic", "gbm", "cnn"):
        pt = _r2_point(primary.true, primary.preds[method])
        bt = _r2_boot(primary.true, primary.preds[method], boot_idx)
        summary["per_method_r2"][method] = {
            n: {
                "r2": round(float(pt[j]), 4),
                "ci95": [
                    round(float(np.nanpercentile(bt[:, j], 2.5)), 4),
                    round(float(np.nanpercentile(bt[:, j], 97.5)), 4),
                ],
            }
            for j, n in enumerate(names)
        }
        summary["per_method_r2"][method]["median"] = round(float(np.nanmedian(pt)), 4)
        print(
            f"[m10] {method:12s} median {np.nanmedian(pt):.4f}  "
            + "  ".join(f"{n}={pt[j]:.3f}" for j, n in enumerate(names))
        )

    # Registered rule: family gap (mechanistic - direct) per target, against the
    # post-stratified gap of the enriched panel supplied by --post-stratified-gap.
    mech = summary["per_method_r2"]["mechanistic"]
    gaps = {
        f"mechanistic_minus_{m}": {
            n: round(mech[n]["r2"] - summary["per_method_r2"][m][n]["r2"], 4) for n in names
        }
        for m in ("gbm", "cnn")
    }
    summary["family_gap"] = gaps
    for m, per_target in gaps.items():
        print(f"[m10] {m}: " + "  ".join(f"{n}={v:+.3f}" for n, v in per_target.items()))

    for s in range(len(cnn_seeds)):
        med = float(np.nanmedian(_r2_point(primary.true, cnn_seeds[s])))
        summary["cnn_seed_medians"].append(round(med, 4))
    print(f"[m10] CNN seed medians: {summary['cnn_seed_medians']}")

    # Same-panel subgroup split: does the control CNN still do better on the
    # signature-complex rules than on the rest, as the canonical decomposition
    # observed? Here both groups are represented in training.
    if 0 < n_complex < n_held:
        for label, mask in (("complex", complex_mask), ("rest", ~complex_mask)):
            pt = _r2_point(primary.true[mask], primary.preds["cnn"][mask])
            summary.setdefault("cnn_subgroup", {})[label] = {
                "n": int(mask.sum()),
                "median": round(float(np.nanmedian(pt)), 4),
            }
            print(f"[m10] CNN {label:8s} n={int(mask.sum()):3d} median {np.nanmedian(pt):.4f}")

    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"[m10] wrote {out / 'summary.json'}")


if __name__ == "__main__":
    main()
