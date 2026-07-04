#!/usr/bin/env python3
"""R1 (EVALUATION_CRITERIA.md rev 7): per-target paired inference + equivalence.

The referee's core statistical objection: failing a +0.10 superiority threshold
is not evidence of equivalence, and reporting the CNN's seed spread while treating
the baseline as deterministic is inadequate. This script fixes both. On the
checkpoint's held-out rules it collects every method's per-rule prediction
(:func:`collect_held_out_predictions`) and, per target, computes the paired
difference in R^2 between methods with a **rule-level cluster bootstrap** (the
unit of resampling is the held-out rule), then classifies each pair/target as:

* **A superior**  — point Delta R^2 >= 0.10 and the 95% CI excludes 0 above;
* **equivalent**  — the 90% CI lies entirely within (-delta, +delta), delta=0.05 (TOST);
* **B superior**  — mirror of "A superior";
* **inconclusive**— otherwise (underpowered).

Reported per target (never only the 4-target median), with the reliability
ceiling (R3) attached for context when available.

Usage::

    python scripts/analyze_paired_stats.py --config configs/lever_a_local.yaml \
        --checkpoint runs/lever_a_local_seed0/checkpoint_final.pt
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from caspectra.config import ExperimentConfig
from caspectra.eval.method_predictions import collect_held_out_predictions
from caspectra.utils import ensure_dir, save_json, set_seed

DELTA = 0.05  # pre-registered practical-equivalence margin (rev 7 R1)
SUP = 0.10  # pre-registered superiority margin (rev 6 S1 / rev 7 R1)
PAIRS = [("mechanistic", "gbm"), ("mechanistic", "cnn"), ("cnn", "gbm")]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="R1 paired inference + equivalence (rev 7).")
    p.add_argument("--config", required=True)
    p.add_argument("--checkpoint", required=True, help="CNN checkpoint (its stored split is used).")
    p.add_argument("--device", default="mps")
    p.add_argument("--n-boot", type=int, default=10000)
    p.add_argument("--output-dir", default=None, help="Default <train.output_dir>/paired_stats.")
    return p.parse_args()


def _r2_boot(true: np.ndarray, pred: np.ndarray, boot_idx: np.ndarray) -> np.ndarray:
    """R^2 per target for every bootstrap resample. Returns ``(B, F)``."""
    t = true[boot_idx]  # (B, N, F)
    p = pred[boot_idx]
    res = np.sum((t - p) ** 2, axis=1)
    tot = np.sum((t - t.mean(axis=1, keepdims=True)) ** 2, axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        return 1.0 - res / tot


def _r2_point(true: np.ndarray, pred: np.ndarray) -> np.ndarray:
    res = np.sum((true - pred) ** 2, axis=0)
    tot = np.sum((true - true.mean(axis=0)) ** 2, axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        return 1.0 - res / tot


def _classify(point: float, ci95: tuple[float, float], ci90: tuple[float, float]) -> str:
    lo95, hi95 = ci95
    lo90, hi90 = ci90
    if -DELTA < lo90 and hi90 < DELTA:
        return "equivalent"
    if point >= SUP and lo95 > 0:
        return "A_superior"
    if point <= -SUP and hi95 < 0:
        return "B_superior"
    return "inconclusive"


def _load_ceiling(cfg) -> dict | None:
    path = Path(f"{cfg.train.output_dir}/reliability/summary.json")
    if path.exists():
        return json.loads(path.read_text()).get("per_feature")
    return None


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    out = ensure_dir(args.output_dir or f"{cfg.train.output_dir}/paired_stats")
    set_seed(cfg.seed)

    hop = collect_held_out_predictions(cfg, args.checkpoint, device=args.device)
    names = hop.target_names
    N = len(hop.held)
    print(f"[r1] radius={hop.radius}  {N} held-out rules  methods={list(hop.preds)}")

    rng = np.random.default_rng(0)
    boot_idx = rng.integers(0, N, size=(args.n_boot, N))

    r2_point = {m: _r2_point(hop.true, p) for m, p in hop.preds.items()}
    r2_boot = {m: _r2_boot(hop.true, p, boot_idx) for m, p in hop.preds.items()}
    ceiling = _load_ceiling(cfg)

    summary = {
        "radius": hop.radius,
        "n_held_out": N,
        "delta_equivalence": DELTA,
        "superiority_margin": SUP,
        "per_method_median_r2": {m: round(float(np.nanmedian(v)), 4) for m, v in r2_point.items()},
        "per_method_r2": {
            m: {n: round(float(v), 4) for n, v in zip(names, vals)} for m, vals in r2_point.items()
        },
        "pairs": {},
    }
    if ceiling is not None:
        summary["ceiling_r2"] = {n: ceiling[n]["ceiling_r2"] for n in names}

    for a, b in PAIRS:
        if a not in r2_boot or b not in r2_boot:
            continue
        d_boot = r2_boot[a] - r2_boot[b]  # (B, F)
        d_point = r2_point[a] - r2_point[b]  # (F,)
        per_target = {}
        for j, n in enumerate(names):
            col = d_boot[:, j]
            col = col[np.isfinite(col)]
            ci95 = (float(np.percentile(col, 2.5)), float(np.percentile(col, 97.5)))
            ci90 = (float(np.percentile(col, 5.0)), float(np.percentile(col, 95.0)))
            per_target[n] = {
                "delta_r2": round(float(d_point[j]), 4),
                "ci95": [round(ci95[0], 4), round(ci95[1], 4)],
                "prob_a_better": round(float(np.mean(col > 0)), 4),
                "verdict": _classify(float(d_point[j]), ci95, ci90),
            }
        summary["pairs"][f"{a}_minus_{b}"] = per_target

    save_json(summary, out / "summary.json")

    print("[r1] per-method median R²:", summary["per_method_median_r2"])
    for pair, pt in summary["pairs"].items():
        print(f"[r1] {pair}:")
        for n, d in pt.items():
            print(
                f"       {n:>16}  ΔR²={d['delta_r2']:+.3f}  "
                f"CI95[{d['ci95'][0]:+.3f},{d['ci95'][1]:+.3f}]  {d['verdict']}"
            )
    print(f"[r1] wrote {out}/summary.json")


if __name__ == "__main__":
    main()
