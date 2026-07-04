#!/usr/bin/env python3
"""R2 (EVALUATION_CRITERIA.md rev 7): incremental-value / stacking test.

The referee's "particularly important" experiment: regress the target on the five
single-diagram statistics, then test whether the CNN's prediction explains any
held-out residual variation under cross-fitting. If not, the learned
representation carries no information about the target beyond the cheap features —
the rigorous form of "the deep model adds nothing."

On the checkpoint's held-out rules we take the rule-averaged 5 baseline features,
the CNN prediction, and (for contrast) the mechanistic prediction, and compute
cross-validated incremental R^2 per target for augmenting one method's regressors
with another's. The CNN is given its best shot: all four of its predicted targets
enter as extra regressors. A rule-level bootstrap puts a CI on each increment;
"adds value" iff the increment exceeds the pre-registered margin (0.02) with a CI
excluding 0.

Usage::

    python scripts/validate_stacking.py --config configs/m4_range2.yaml \
        --checkpoint runs/m4_range2_seed0/checkpoint_final.pt
"""

from __future__ import annotations

import argparse

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from caspectra.config import ExperimentConfig
from caspectra.eval.method_predictions import collect_held_out_predictions
from caspectra.utils import ensure_dir, save_json, set_seed

MARGIN = 0.02  # pre-registered incremental-value margin (rev 7 R2)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="R2 stacking / incremental-value test (rev 7).")
    p.add_argument("--config", required=True)
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--device", default="mps")
    p.add_argument("--n-boot", type=int, default=10000)
    p.add_argument("--output-dir", default=None, help="Default <train.output_dir>/stacking.")
    return p.parse_args()


def _cv_predict(X: np.ndarray, y: np.ndarray, *, n_splits=5, repeats=4) -> np.ndarray:
    """Repeated-KFold out-of-fold predictions (ridge on standardised regressors)."""
    n_splits = min(n_splits, len(y))
    acc = np.zeros(len(y))
    for rep in range(repeats):
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=rep)
        p = np.zeros(len(y))
        for tr, te in kf.split(X):
            model = make_pipeline(StandardScaler(), Ridge(alpha=1.0))
            model.fit(X[tr], y[tr])
            p[te] = model.predict(X[te])
        acc += p
    return acc / repeats


def _incremental_r2(base_pred, aug_pred, y, boot_idx):
    """Bootstrap distribution of the incremental R^2 (aug over base) over rows."""
    yb = y[boot_idx]  # (B, N)
    tot = np.sum((yb - yb.mean(axis=1, keepdims=True)) ** 2, axis=1)
    res_base = np.sum((yb - base_pred[boot_idx]) ** 2, axis=1)
    res_aug = np.sum((yb - aug_pred[boot_idx]) ** 2, axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        return (res_base - res_aug) / tot  # (B,)


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    out = ensure_dir(args.output_dir or f"{cfg.train.output_dir}/stacking")
    set_seed(cfg.seed)

    hop = collect_held_out_predictions(cfg, args.checkpoint, device=args.device)
    names = hop.target_names
    N = len(hop.held)
    X_base = hop.features  # (N, 5)
    X_cnn = hop.preds["cnn"]  # (N, 4)
    X_mech = hop.preds["mechanistic"]  # (N, 4)
    print(f"[r2] radius={hop.radius}  {N} held-out rules")

    rng = np.random.default_rng(0)
    boot_idx = rng.integers(0, N, size=(args.n_boot, N))

    # Regressor blocks for each "does A add value over B?" question.
    blocks = {
        "cnn_over_features": (X_base, np.hstack([X_base, X_cnn])),
        "features_over_cnn": (X_cnn, np.hstack([X_cnn, X_base])),
        "mechanistic_over_features": (X_base, np.hstack([X_base, X_mech])),
    }

    def _r2(pred: np.ndarray, y: np.ndarray) -> float:
        tot = float(np.sum((y - y.mean()) ** 2))
        return 1.0 - float(np.sum((y - pred) ** 2)) / tot if tot > 0 else float("nan")

    summary = {"radius": hop.radius, "n_held_out": N, "margin": MARGIN, "increments": {}}
    for key, (Xb, Xa) in blocks.items():
        per_target = {}
        for j, n in enumerate(names):
            base_pred = _cv_predict(Xb, hop.true[:, j])
            aug_pred = _cv_predict(Xa, hop.true[:, j])
            dist = _incremental_r2(base_pred, aug_pred, hop.true[:, j], boot_idx)
            dist = dist[np.isfinite(dist)]
            point = float(np.median(dist))
            ci = [float(np.percentile(dist, 2.5)), float(np.percentile(dist, 97.5))]
            per_target[n] = {
                "incremental_r2": round(point, 4),
                "ci95": [round(ci[0], 4), round(ci[1], 4)],
                # Reviewer (round 2, editorial 4): the reader must see the full
                # stacked model's performance, not only the increment.
                "base_model_r2": round(_r2(base_pred, hop.true[:, j]), 4),
                "stacked_model_r2": round(_r2(aug_pred, hop.true[:, j]), 4),
                "adds_value": bool(point > MARGIN and ci[0] > 0),
            }
        summary["increments"][key] = per_target

    save_json(summary, out / "summary.json")
    for key, pt in summary["increments"].items():
        print(f"[r2] {key}:")
        for n, d in pt.items():
            print(
                f"       {n:>16}  inc R²={d['incremental_r2']:+.3f}  "
                f"CI95[{d['ci95'][0]:+.3f},{d['ci95'][1]:+.3f}]  "
                f"base {d['base_model_r2']:.3f} -> stacked {d['stacked_model_r2']:.3f}  "
                f"adds_value={d['adds_value']}"
            )
    print(f"[r2] wrote {out}/summary.json")


if __name__ == "__main__":
    main()
