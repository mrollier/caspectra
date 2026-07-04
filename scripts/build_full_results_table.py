#!/usr/bin/env python3
"""C5 (EVALUATION_CRITERIA.md rev 8): the complete per-target results table.

The second referee (concern 6) requires, for *every* task and target (not only
ECA, not only a single "reference seed"): the held-out rule count, each method's
R^2 with a rule-bootstrap CI, the CNN's mean and spread across seeds, the paired
Delta R^2 with interval and superiority/equivalence/inconclusive verdict, and the
relevant reliability benchmark. This script assembles all of that from the cached
held-out predictions (:func:`collect_held_out_predictions`) across the available
training seeds, reports the TOST verdict at three margins (delta in {0.02, 0.05,
0.10}; concern 6), and emits a LaTeX table body for the manuscript.

It also reports the **baseline's repeated-outer-split** R^2 distribution (concern
6: "fixed split + bootstrap is not enough"): the five-statistic regressor is
refit on many random leave-rules-out training sets and evaluated on each held
set, quantifying training-panel/split variance. The mechanistic estimator is
**split-invariant** (no trained parameters — its per-rule prediction does not
depend on which rules are held out), which is stated rather than resampled.

Usage::

    python scripts/build_full_results_table.py --config configs/m4_range2.yaml \
        --seed-checkpoints runs/m4_range2_seed{0,1,2,3,4}/checkpoint_final.pt
"""

from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler

from caspectra.config import ExperimentConfig
from caspectra.data.splits import leave_rules_out_split
from caspectra.data.targets import TARGET_NAMES, load_or_compute_invariant_targets
from caspectra.eval.baselines import compute_baseline_features
from caspectra.eval.labels import load_rule_labels
from caspectra.eval.method_predictions import collect_held_out_predictions
from caspectra.factory import build_dataset
from caspectra.utils import ensure_dir, save_json, set_seed

# Apple-Accelerate BLAS emits spurious matmul RuntimeWarnings on non-contiguous
# views inside sklearn; results are unaffected (verified against contiguous runs).
warnings.filterwarnings("ignore", message=".*encountered in matmul")

DELTAS = [0.02, 0.05, 0.10]
SUP = 0.10
PAIRS = [("mechanistic", "gbm"), ("mechanistic", "cnn"), ("cnn", "gbm")]
LABELS = {"mechanistic": "mechanistic", "gbm": "5 statistics", "ridge": "ridge", "cnn": "deep CNN"}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="C5 complete per-target results table (rev 8).")
    p.add_argument("--config", required=True)
    p.add_argument("--seed-checkpoints", nargs="+", required=True, help="All seed checkpoints.")
    p.add_argument("--device", default="mps")
    p.add_argument("--n-boot", type=int, default=10000)
    p.add_argument("--repeated-splits", type=int, default=50, help="Outer splits for baseline var.")
    p.add_argument("--output-dir", default=None)
    return p.parse_args()


def _r2_point(true, pred):
    res = np.sum((true - pred) ** 2, axis=0)
    tot = np.sum((true - true.mean(axis=0)) ** 2, axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        return 1.0 - res / tot


def _r2_boot(true, pred, boot_idx):
    t, p = true[boot_idx], pred[boot_idx]
    res = np.sum((t - p) ** 2, axis=1)
    tot = np.sum((t - t.mean(axis=1, keepdims=True)) ** 2, axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        r2 = 1.0 - res / tot
    # Clip pathological tails: a bootstrap resample with near-zero target variance
    # gives |R^2| >> 1 (SS_tot -> 0), which are numerical artifacts, not signal.
    # Legitimate R^2 <= 1; floor the lower tail at -1 for stable CIs.
    return np.clip(r2, -1.0, 1.0)


def _verdict(point, col, delta):
    lo95, hi95 = np.percentile(col, [2.5, 97.5])
    lo90, hi90 = np.percentile(col, [5.0, 95.0])
    if -delta < lo90 and hi90 < delta:
        return "equivalent"
    if point >= SUP and lo95 > 0:
        return "A_superior"
    if point <= -SUP and hi95 < 0:
        return "B_superior"
    return "inconclusive"


def _reliability(cfg):
    path = Path(f"{cfg.train.output_dir}/reliability/summary.json")
    if not path.exists():
        return {}, {}
    per = json.loads(path.read_text()).get("per_feature", {})
    icc = {n: per[n].get("icc", per[n].get("ceiling_r2")) for n in per}
    agr = {n: per[n].get("agreement_r2") for n in per}
    return icc, agr


def _baseline_repeated_splits(cfg, n_splits):
    """Median per-target R^2 of the 5-stat GBM over random leave-rules-out splits."""
    ds = build_dataset(cfg.data, training=False)
    reps = np.asarray(ds.equiv_reps)
    rules = sorted({int(r) for r in reps})
    targets = load_or_compute_invariant_targets(
        rules,
        width=cfg.data.grid_size,
        ic_density=cfg.targets.ic_density,
        n_pairs=cfg.targets.n_pairs,
        seed=cfg.targets.seed,
        cache_dir=cfg.data.cache_dir,
        radius=cfg.data.radius,
    )
    true_by_rule = {r: targets[i] for i, r in enumerate(rules)}
    labels = load_rule_labels(cfg.eval.rule_labels_csv)
    strata = (
        np.array([int(labels.wolfram.get(int(r), -1)) for r in rules])
        if labels and labels.has_wolfram
        else np.zeros(len(rules))
    )
    feats = compute_baseline_features(ds.images, radius=cfg.data.radius)
    y = np.stack([true_by_rule[int(r)] for r in reps])
    per_split = []
    for s in range(n_splits):
        tr_rules, ho_rules = leave_rules_out_split(
            rules,
            strata,
            holdout_fraction=cfg.train.holdout_fraction,
            seed=1000 + s,
            force_holdout=cfg.train.force_holdout_rules,
            force_train=cfg.train.force_train_rules,
        )
        tr, ho = np.isin(reps, tr_rules), np.isin(reps, ho_rules)
        sc = StandardScaler().fit(feats[tr])
        Xtr, Xho = sc.transform(feats[tr]), sc.transform(feats[ho])
        preds = np.stack(
            [
                GradientBoostingRegressor(random_state=0).fit(Xtr, y[tr, j]).predict(Xho)
                for j in range(len(TARGET_NAMES))
            ],
            axis=1,
        )
        # rule-average over held diagrams
        ho_reps = reps[ho]
        held = sorted(set(int(r) for r in ho_reps))
        pm = np.stack([preds[ho_reps == r].mean(axis=0) for r in held])
        tm = np.stack([true_by_rule[r] for r in held])
        per_split.append(_r2_point(tm, pm))
    arr = np.stack(per_split)  # (n_splits, F)
    return {
        n: {
            "median": round(float(np.nanmedian(arr[:, j])), 4),
            "p05": round(float(np.nanpercentile(arr[:, j], 5)), 4),
            "p95": round(float(np.nanpercentile(arr[:, j], 95)), 4),
        }
        for j, n in enumerate(TARGET_NAMES)
    }


def _baseline_loo_eca(cfg):
    """Leave-one-orbit-out cross-fit R^2 of the 5-stat GBM over all 88 ECA reps.

    The dataset's rules *are* the orbit representatives, so leaving one rule out
    is leaving one orbit out (the reviewer's suggested orbit-respecting CV). Every
    rule is predicted exactly once, out of fold; the cross-fit R^2 uses all 88.
    """
    ds = build_dataset(cfg.data, training=False)
    reps = np.asarray(ds.equiv_reps)
    rules = sorted({int(r) for r in reps})
    targets = load_or_compute_invariant_targets(
        rules,
        width=cfg.data.grid_size,
        ic_density=cfg.targets.ic_density,
        n_pairs=cfg.targets.n_pairs,
        seed=cfg.targets.seed,
        cache_dir=cfg.data.cache_dir,
        radius=cfg.data.radius,
    )
    true_by_rule = {r: targets[i] for i, r in enumerate(rules)}
    feats = compute_baseline_features(ds.images, radius=cfg.data.radius)
    y = np.stack([true_by_rule[int(r)] for r in reps])
    oof = np.empty((len(rules), len(TARGET_NAMES)))
    for i, r in enumerate(rules):
        tr, ho = reps != r, reps == r
        sc = StandardScaler().fit(feats[tr])
        Xtr, Xho = sc.transform(feats[tr]), sc.transform(feats[ho])
        oof[i] = [
            GradientBoostingRegressor(random_state=0).fit(Xtr, y[tr, j]).predict(Xho).mean()
            for j in range(len(TARGET_NAMES))
        ]
    truth = np.stack([true_by_rule[r] for r in rules])
    r2 = _r2_point(truth, oof)
    return {n: round(float(r2[j]), 4) for j, n in enumerate(TARGET_NAMES)}


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    out = ensure_dir(args.output_dir or f"{cfg.train.output_dir}/full_table")
    set_seed(cfg.seed)

    # Primary seed: mechanistic + ridge + gbm + cnn(seed0). Extra seeds: cnn only.
    primary = collect_held_out_predictions(cfg, args.seed_checkpoints[0], device=args.device)
    names = primary.target_names
    N = len(primary.held)
    cnn_seed_preds = [primary.preds["cnn"]]
    for ckpt in args.seed_checkpoints[1:]:
        hop = collect_held_out_predictions(cfg, ckpt, device=args.device, include_mechanistic=False)
        assert hop.held == primary.held, "seed splits differ"
        cnn_seed_preds.append(hop.preds["cnn"])
    cnn_seed_preds = np.stack(cnn_seed_preds)  # (S, N, F)
    print(f"[c5] radius={primary.radius} N={N} held-out rules; {len(cnn_seed_preds)} CNN seeds")

    rng = np.random.default_rng(0)
    boot_idx = rng.integers(0, N, size=(args.n_boot, N))
    icc, agr = _reliability(cfg)

    methods = {
        "mechanistic": primary.preds["mechanistic"],
        "gbm": primary.preds["gbm"],
        "cnn": primary.preds["cnn"],
    }
    per_method = {}
    for m, pred in methods.items():
        pt = _r2_point(primary.true, pred)
        bt = _r2_boot(primary.true, pred, boot_idx)
        per_method[m] = {
            n: {
                "r2": round(float(pt[j]), 4),
                "ci95": [
                    round(float(np.nanpercentile(bt[:, j], 2.5)), 4),
                    round(float(np.nanpercentile(bt[:, j], 97.5)), 4),
                ],
            }
            for j, n in enumerate(names)
        }
    # CNN seed spread (median-over-seeds per-target R2 and its s.d.).
    seed_r2 = np.stack(
        [_r2_point(primary.true, cnn_seed_preds[s]) for s in range(len(cnn_seed_preds))]
    )
    cnn_seed = {
        n: {
            "mean": round(float(np.nanmean(seed_r2[:, j])), 4),
            "std": round(float(np.nanstd(seed_r2[:, j])), 4),
        }
        for j, n in enumerate(names)
    }

    r2_boot = {m: _r2_boot(primary.true, methods[m], boot_idx) for m in methods}
    r2_pt = {m: _r2_point(primary.true, methods[m]) for m in methods}
    pairs = {}
    for a, b in PAIRS:
        d_boot = r2_boot[a] - r2_boot[b]
        d_pt = r2_pt[a] - r2_pt[b]
        pt = {}
        for j, n in enumerate(names):
            col = d_boot[:, j][np.isfinite(d_boot[:, j])]
            pt[n] = {
                "delta_r2": round(float(d_pt[j]), 4),
                "ci95": [
                    round(float(np.percentile(col, 2.5)), 4),
                    round(float(np.percentile(col, 97.5)), 4),
                ],
                "verdict_by_delta": {str(d): _verdict(float(d_pt[j]), col, d) for d in DELTAS},
            }
        pairs[f"{a}_minus_{b}"] = pt

    summary = {
        "radius": primary.radius,
        "n_held_out": N,
        "n_cnn_seeds": len(cnn_seed_preds),
        "deltas": DELTAS,
        "icc_ceiling": icc,
        "replicate_agreement": agr,
        "per_method_r2": per_method,
        "cnn_seed_spread": cnn_seed,
        "pairs": pairs,
        "mechanistic_note": "split-invariant: no trained parameters; per-rule prediction "
        "does not depend on the held-out split.",
    }
    # Split-uncertainty for the (deterministic-given-data) baseline: pre-registered
    # as leave-one-orbit-out on ECA, repeated leave-rules-out outer splits on radius 2.
    if primary.radius == 1:
        summary["baseline_loo_orbit_r2"] = _baseline_loo_eca(cfg)
    else:
        summary["baseline_repeated_splits"] = _baseline_repeated_splits(cfg, args.repeated_splits)
    save_json(summary, out / "summary.json")

    # LaTeX table body: one row per target, columns mechanistic / 5-stat / CNN(seed mean+-sd) /
    # agreement benchmark / ICC ceiling.
    lines = []
    for n in names:
        me = per_method["mechanistic"][n]
        gb = per_method["gbm"][n]
        cs = cnn_seed[n]
        lines.append(
            f"{n.replace('_', ' ')} & {me['r2']:.3f} [{me['ci95'][0]:.3f},{me['ci95'][1]:.3f}] "
            f"& {gb['r2']:.3f} [{gb['ci95'][0]:.3f},{gb['ci95'][1]:.3f}] "
            f"& {cs['mean']:.3f}$\\pm${cs['std']:.3f} "
            f"& {agr.get(n, float('nan')):.3f} & {icc.get(n, float('nan')):.3f} \\\\"
        )
    (out / "table_body.tex").write_text("\n".join(lines) + "\n")

    print("[c5] per-method R² (mechanistic / 5-stat / CNN seed-mean):")
    for n in names:
        print(
            f"     {n:>16}  mech {per_method['mechanistic'][n]['r2']:.3f}  "
            f"5stat {per_method['gbm'][n]['r2']:.3f}  "
            f"cnn {cnn_seed[n]['mean']:.3f}±{cnn_seed[n]['std']:.3f}  "
            f"| agreement {agr.get(n, float('nan')):.3f}  ICC {icc.get(n, float('nan')):.3f}"
        )
    for pair, pt in pairs.items():
        print(f"[c5] {pair}:")
        for n in names:
            d = pt[n]
            print(
                f"       {n:>16} ΔR²={d['delta_r2']:+.3f} CI{d['ci95']} "
                f"verdicts {d['verdict_by_delta']}"
            )
    if "baseline_loo_orbit_r2" in summary:
        print(
            f"[c5] baseline leave-one-orbit-out R² (88 orbits): {summary['baseline_loo_orbit_r2']}"
        )
    if "baseline_repeated_splits" in summary:
        print(
            f"[c5] baseline repeated-split R² ({args.repeated_splits} splits): "
            f"{summary['baseline_repeated_splits']}"
        )
    print(f"[c5] wrote {out}/summary.json and {out}/table_body.tex")


if __name__ == "__main__":
    main()
