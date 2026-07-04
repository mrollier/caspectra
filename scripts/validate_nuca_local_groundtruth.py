#!/usr/bin/env python3
"""R7 (EVALUATION_CRITERIA.md rev 7): maps vs an independent local ground truth.

The referee's concern 9: the spatial-map benchmark used a stripe-contrast proxy
with an oracle-selected window, and never defined the local ground truth through
local perturbations. This script fixes all three. On half/half composed diagrams
it builds the location-resolved damage ground truth by *local perturbation in the
composed system* (:func:`caspectra.eval.nuca_metrics.local_damage_profile`), then
scores each phenotype map by the Spearman spatial correlation between its
per-column spreading-rate profile and that ground truth. The hand-crafted map's
window is **selected on a validation split of rule pairs** (primary), with the
per-pair best window reported only as an oracle sensitivity. Verdict: the CNN map
"resolves finer" only if it beats the validation-selected hand-crafted map with a
pair-bootstrap CI excluding 0.

Usage::

    python scripts/validate_nuca_local_groundtruth.py --config configs/lever_a_shallow.yaml \
        --checkpoint runs/lever_a_shallow_seed0/checkpoint_final.pt
"""

from __future__ import annotations

import argparse
from itertools import combinations

import numpy as np
import torch
from scipy.stats import spearmanr
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler

from caspectra.ca.nuca import NonUniformCA, half_mask
from caspectra.config import ExperimentConfig
from caspectra.data.splits import leave_rules_out_split
from caspectra.data.targets import TARGET_NAMES, load_or_compute_invariant_targets
from caspectra.eval.baselines import compute_baseline_features
from caspectra.eval.labels import load_rule_labels
from caspectra.eval.nuca_metrics import column_profile, local_damage_profile
from caspectra.factory import build_dataset, build_model
from caspectra.utils import ensure_dir, save_json, select_device, set_seed

PRIMARY_PANEL = [0, 4, 204, 184, 26, 73, 154, 90, 60, 30, 18, 45, 22, 41, 106, 54]
WINDOW_WIDTHS = [8, 12, 16, 24, 32]
RATE = TARGET_NAMES.index("spreading_rate")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="R7 maps vs independent local ground truth (rev 7).")
    p.add_argument("--config", required=True)
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--device", default="mps")
    p.add_argument("--n-ic", type=int, default=8)
    p.add_argument("--local-horizon", type=int, default=24)
    p.add_argument("--panel", type=int, nargs="*", default=None)
    p.add_argument("--output-dir", default=None)
    return p.parse_args()


@torch.no_grad()
def _cnn_rate_profile(model, diagram, device, mean, std):
    b = torch.from_numpy(diagram).to(torch.float32).unsqueeze(0).unsqueeze(0).to(device)
    pmap = model.predict_map(b).cpu().numpy()[0]
    pmap = pmap * std[:, None, None] + mean[:, None, None]
    return column_profile(pmap)[RATE]


def _fit_rate_gbm(cfg):
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
    rate_by_rule = {r: targets[i][RATE] for i, r in enumerate(rules)}
    labels = load_rule_labels(cfg.eval.rule_labels_csv)
    strata = (
        np.array([int(labels.wolfram.get(int(r), -1)) for r in rules])
        if labels and labels.has_wolfram
        else np.zeros(len(rules))
    )
    train_rules, _ = leave_rules_out_split(
        rules,
        strata,
        holdout_fraction=cfg.train.holdout_fraction,
        seed=cfg.train.holdout_seed,
        force_holdout=cfg.train.force_holdout_rules,
        force_train=cfg.train.force_train_rules,
    )
    tr = np.isin(reps, train_rules)
    feats = compute_baseline_features(ds.images, radius=cfg.data.radius)
    scaler = StandardScaler().fit(feats[tr])
    y = np.array([rate_by_rule[int(r)] for r in reps])
    gbm = GradientBoostingRegressor(random_state=0).fit(scaler.transform(feats[tr]), y[tr])
    return gbm, scaler


def _handcrafted_rate_profile(diagram, m, w, gbm, scaler, radius):
    width = diagram.shape[1]
    centers = ((np.arange(m) + 0.5) * width / m).astype(int)
    windows = np.stack(
        [np.take(diagram, range(c - w // 2, c - w // 2 + w), axis=1, mode="wrap") for c in centers]
    )
    return gbm.predict(scaler.transform(compute_baseline_features(windows, radius=radius)))


def _spearman(a, b):
    if np.std(a) < 1e-9 or np.std(b) < 1e-9:
        return np.nan
    return float(spearmanr(a, b).statistic)


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    out = ensure_dir(args.output_dir or f"{cfg.train.output_dir}/nuca_local_gt")
    set_seed(cfg.seed)
    device = select_device(prefer=args.device)
    width, radius = cfg.data.grid_size, cfg.data.radius
    panel = args.panel if args.panel is not None else PRIMARY_PANEL

    state = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    mean, std = state["scaler_mean"], state["scaler_std"]
    model = build_model(cfg.model)
    model.load_state_dict(state["model_state"])
    model = model.to(device).eval()
    gbm, scaler = _fit_rate_gbm(cfg)

    # Map column resolution.
    probe = NonUniformCA(0, 0, half_mask(width)).random_diagram(
        width, width, np.random.default_rng(0)
    )
    m = _cnn_rate_profile(model, probe, device, mean, std).shape[0]
    centers = ((np.arange(m) + 0.5) * width / m).astype(int)
    print(f"[r7] map columns m={m}; local horizon {args.local_horizon}; windows {WINDOW_WIDTHS}")

    # Rule pairs with a real rate gap (a spatial signal to localise).
    targets = load_or_compute_invariant_targets(
        panel,
        width=width,
        ic_density=cfg.targets.ic_density,
        n_pairs=cfg.targets.n_pairs,
        seed=cfg.targets.seed,
        cache_dir=cfg.data.cache_dir,
        radius=radius,
    )
    rate_by_rule = {r: float(targets[i][RATE]) for i, r in enumerate(panel)}
    pairs = [
        (a, b) for a, b in combinations(panel, 2) if abs(rate_by_rule[a] - rate_by_rule[b]) >= 0.25
    ]

    methods = ["cnn"] + [f"hc{w}" for w in WINDOW_WIDTHS]
    corr = {mth: [] for mth in methods}  # one mean-over-ICs Spearman per pair
    rng = np.random.default_rng(7)
    for a, b in pairs:
        mask = half_mask(width)
        gt = local_damage_profile(
            NonUniformCA(a, b, mask),
            centers,
            n_steps=args.local_horizon,
            n_pairs=64,
            ic_density=cfg.targets.ic_density,
            rng=np.random.default_rng([9, a, b]),
        )
        per_method_ic = {mth: [] for mth in methods}
        for i in range(args.n_ic):
            diagram = NonUniformCA(a, b, mask).random_diagram(
                width, width, np.random.default_rng([4, a, b, i])
            )
            per_method_ic["cnn"].append(
                _spearman(_cnn_rate_profile(model, diagram, device, mean, std), gt)
            )
            for w in WINDOW_WIDTHS:
                prof = _handcrafted_rate_profile(diagram, m, w, gbm, scaler, radius)
                per_method_ic[f"hc{w}"].append(_spearman(prof, gt))
        for mth in methods:
            corr[mth].append(float(np.nanmean(per_method_ic[mth])))

    corr = {mth: np.array(v) for mth, v in corr.items()}
    n_pairs = len(pairs)
    # Validation-selected window: best mean corr on a validation half of the pairs.
    val = np.arange(0, n_pairs, 2)
    test = np.arange(1, n_pairs, 2)
    best_w = max(WINDOW_WIDTHS, key=lambda w: np.nanmean(corr[f"hc{w}"][val]))
    hc_sel = corr[f"hc{best_w}"]
    hc_oracle = np.nanmax(np.stack([corr[f"hc{w}"] for w in WINDOW_WIDTHS]), axis=0)

    # Bootstrap CI on CNN - validation-selected-handcrafted (test pairs). The unit
    # of resampling is the composed system (rule pair), NOT the column: the
    # resampled observations are per-pair mean-over-IC Spearman values, so
    # spatially correlated columns inside one mosaic never inflate the effective
    # sample size (rev-8 C7).
    rng = np.random.default_rng(0)
    d = corr["cnn"][test] - hc_sel[test]
    d = d[np.isfinite(d)]
    boot = (
        np.array([np.mean(d[rng.integers(0, len(d), len(d))]) for _ in range(10000)])
        if len(d)
        else np.array([np.nan])
    )
    ci = [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]
    ci90 = [float(np.percentile(boot, 5.0)), float(np.percentile(boot, 95.0))]
    # Pre-registered language rule (rev-8 C7): "equivalent" only if TOST passes
    # (90% CI within +-delta); a CI straddling 0 but exceeding delta is inconclusive.
    delta = 0.05
    if -delta < ci90[0] and ci90[1] < delta:
        verdict = "equivalent"
    elif np.nanmean(d) > 0 and ci[0] > 0:
        verdict = "cnn_superior"
    elif np.nanmean(d) < 0 and ci[1] < 0:
        verdict = "handcrafted_superior"
    else:
        verdict = "inconclusive"

    summary = {
        "checkpoint": str(args.checkpoint),
        "map_columns": int(m),
        "n_pairs": n_pairs,
        "n_validation_pairs": int(len(val)),
        "n_test_pairs": int(len(test)),
        "n_ic_replicates_per_pair": int(args.n_ic),
        "panel_rules": [int(r) for r in panel],
        "mosaic_type": "half/half composed system (single interface)",
        "gt_random_stream": "independent SeedSequence([9, a, b]) per pair; observed "
        "diagrams use SeedSequence([4, a, b, ic]); streams never shared",
        "window_selection": "one global window chosen on the validation half of the "
        "pairs (even indices); test = odd indices; per-pair oracle reported only as "
        "a labelled sensitivity",
        "resampling_unit": "composed system (rule pair)",
        "local_horizon": args.local_horizon,
        "validation_selected_window": int(best_w),
        "mean_spearman_to_local_gt": {
            "cnn": round(float(np.nanmean(corr["cnn"])), 4),
            "handcrafted_val_selected": round(float(np.nanmean(hc_sel)), 4),
            "handcrafted_oracle_perpair": round(float(np.nanmean(hc_oracle)), 4),
            **{f"hc{w}": round(float(np.nanmean(corr[f"hc{w}"])), 4) for w in WINDOW_WIDTHS},
        },
        "cnn_minus_val_selected_handcrafted_test": round(float(np.nanmean(d)), 4),
        "ci95": [round(ci[0], 4), round(ci[1], 4)],
        "ci90": [round(ci90[0], 4), round(ci90[1], 4)],
        "tost_delta": delta,
        "verdict": verdict,
        "cnn_resolves_finer": bool(np.nanmean(d) > 0 and ci[0] > 0),
    }
    save_json(summary, out / "summary.json")
    sp = summary["mean_spearman_to_local_gt"]
    print(
        f"[r7] mean Spearman to local GT: CNN {sp['cnn']:.3f}  "
        f"handcrafted(val-sel w={best_w}) {sp['handcrafted_val_selected']:.3f}  "
        f"handcrafted(oracle) {sp['handcrafted_oracle_perpair']:.3f}"
    )
    print(
        f"[r7] CNN - val-selected handcrafted (test) "
        f"{summary['cnn_minus_val_selected_handcrafted_test']:+.3f} "
        f"CI95[{ci[0]:+.3f},{ci[1]:+.3f}] CI90[{ci90[0]:+.3f},{ci90[1]:+.3f}]  "
        f"verdict={verdict}  cnn_resolves_finer={summary['cnn_resolves_finer']}"
    )
    print(f"[r7] wrote {out}/summary.json")


if __name__ == "__main__":
    main()
