#!/usr/bin/env python3
"""S1 (EVALUATION_CRITERIA.md rev 6): single-diagram baseline vs the CNN amortizer.

The criterion-6/9 claim is that the damage-spreading invariants — *defined* by
twin runs — are non-trivial to recover from a **single** diagram. The obvious
null alternative is that a handful of cheap single-diagram statistics already
recover them (the "the encoder just reads density" objection). This control fits
ridge + gradient-boosted-tree regressors from the label-free single-diagram
features (:mod:`caspectra.eval.baselines`) onto the four invariants, using the
**identical leave-rules-out split** as the CNN it is compared to, and reports
per-feature + median held-out-rule R² for the baseline and (if a checkpoint is
given) the CNN, with the pre-registered "meaningfully better" margin
(CNN median − best baseline median ≥ 0.10).

The split is reconstructed from the config exactly as ``scripts/train_regressor``
builds it; with ``--checkpoint`` the stored split is used verbatim instead, so
the baseline and the CNN are scored on the same held-out rules and truth.

Usage::

    python scripts/validate_baseline_regression.py --config configs/lever_a_local.yaml \
        --checkpoint runs/lever_a_local_seed0/checkpoint_final.pt
"""

from __future__ import annotations

import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.ensemble import GradientBoostingRegressor  # noqa: E402
from sklearn.linear_model import Ridge  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

from caspectra.config import ExperimentConfig  # noqa: E402
from caspectra.data.splits import leave_rules_out_split  # noqa: E402
from caspectra.data.targets import TARGET_NAMES, load_or_compute_invariant_targets  # noqa: E402
from caspectra.eval.baselines import compute_baseline_features  # noqa: E402
from caspectra.eval.labels import load_rule_labels  # noqa: E402
from caspectra.factory import build_dataset  # noqa: E402
from caspectra.train.regression_trainer import r2_per_feature  # noqa: E402
from caspectra.utils import ensure_dir, save_json, set_seed  # noqa: E402

MARGIN = 0.10  # pre-registered "meaningfully better" bar (rev 6 S1)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="S1 single-diagram baseline vs CNN (rev 6).")
    p.add_argument("--config", required=True, help="Path to the YAML ExperimentConfig.")
    p.add_argument("--checkpoint", default=None, help="CNN checkpoint (uses its stored split).")
    p.add_argument("--device", default="mps", help="Device for the CNN pass (if --checkpoint).")
    p.add_argument("--output-dir", default=None, help="Default: <train.output_dir>/baseline_eval.")
    return p.parse_args()


def _config_split(cfg, rules):
    """Reproduce scripts/train_regressor.py's leave-rules-out split from config."""
    labels = load_rule_labels(cfg.eval.rule_labels_csv)
    if labels and labels.has_wolfram:
        strata = np.array([int(labels.wolfram.get(int(r), -1)) for r in rules])
    else:
        strata = np.zeros(len(rules))
    return leave_rules_out_split(
        rules,
        strata,
        holdout_fraction=cfg.train.holdout_fraction,
        seed=cfg.train.holdout_seed,
        force_holdout=cfg.train.force_holdout_rules,
        force_train=cfg.train.force_train_rules,
    )


def _rule_means(values, reps, rules):
    return np.stack([values[reps == r].mean(axis=0) for r in rules])


def _fit_predict(name, feats_tr, y_tr, feats_ho):
    """Return per-diagram held-out predictions for a named regressor."""
    if name == "ridge":
        model = Ridge(alpha=1.0)
        model.fit(feats_tr, y_tr)
        return model.predict(feats_ho)
    # Gradient boosting is single-output: one model per target.
    preds = np.empty((feats_ho.shape[0], y_tr.shape[1]))
    for j in range(y_tr.shape[1]):
        gb = GradientBoostingRegressor(random_state=0)
        gb.fit(feats_tr, y_tr[:, j])
        preds[:, j] = gb.predict(feats_ho)
    return preds


def _median_r2(pred_diag, reps_ho, held, true_by_rule):
    pred_rule = _rule_means(pred_diag, reps_ho, held)
    true_rule = np.stack([true_by_rule[r] for r in held])
    per = r2_per_feature(pred_rule, true_rule)
    return per, float(np.nanmedian(per))


def _cnn_predictions(cfg, checkpoint, device_pref, images_shape):
    import torch  # local import: only needed with --checkpoint

    from caspectra.factory import build_dataloader, build_model
    from caspectra.utils import select_device

    state = torch.load(checkpoint, map_location="cpu", weights_only=False)
    model = build_model(cfg.model)
    model.load_state_dict(state["model_state"])
    device = select_device(prefer=device_pref)
    model = model.to(device).eval()
    ds = build_dataset(cfg.data, training=False)
    loader = build_dataloader(
        ds, batch_size=cfg.eval.batch_size, shuffle=False, num_workers=cfg.train.num_workers
    )
    with torch.no_grad():
        preds = np.concatenate([model(img.to(device)).cpu().numpy() for img, _ in loader])
    preds = preds * state["scaler_std"] + state["scaler_mean"]
    return preds, [int(r) for r in state["holdout_rules"]]


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    out = ensure_dir(args.output_dir or f"{cfg.train.output_dir}/baseline_eval")
    set_seed(cfg.seed)
    radius = cfg.data.radius

    dataset = build_dataset(cfg.data, training=False)
    reps = np.asarray(dataset.equiv_reps)
    rules = sorted({int(r) for r in reps})

    targets = load_or_compute_invariant_targets(
        rules,
        width=cfg.data.grid_size,
        ic_density=cfg.targets.ic_density,
        n_pairs=cfg.targets.n_pairs,
        seed=cfg.targets.seed,
        cache_dir=cfg.data.cache_dir,
        radius=radius,
    )
    true_by_rule = {r: targets[i] for i, r in enumerate(rules)}

    # Split: from the checkpoint (verbatim) if given, else reconstruct from config.
    if args.checkpoint:
        cnn_pred, holdout_rules = _cnn_predictions(
            cfg, args.checkpoint, args.device, dataset.images
        )
        train_rules = [r for r in rules if r not in set(holdout_rules)]
    else:
        cnn_pred = None
        train_rules, holdout_rules = _config_split(cfg, rules)
    held = [r for r in holdout_rules if r in set(rules)]
    print(f"[s1] radius={radius}  {len(train_rules)} train / {len(held)} held-out rules")

    # Single-diagram features and per-diagram targets.
    feats = compute_baseline_features(dataset.images, radius=radius)
    scaler = StandardScaler().fit(feats[np.isin(reps, train_rules)])
    feats = scaler.transform(feats)
    y = np.stack([true_by_rule[int(r)] for r in reps])
    tr_mask, ho_mask = np.isin(reps, train_rules), np.isin(reps, held)
    reps_ho = reps[ho_mask]

    # Complex subset (criterion-9 style) when the config forces a complex hold-out.
    complex_set = {int(r) for r in cfg.train.force_holdout_rules} if radius > 1 else set()
    held_complex = [r for r in held if r in complex_set]

    summary = {"radius": radius, "n_held_out": len(held), "features": ["baseline"], "baselines": {}}
    baseline_medians = {}
    for name in ("ridge", "gbm"):
        reg = "ridge" if name == "ridge" else "gbm"
        pred_diag = _fit_predict(reg, feats[tr_mask], y[tr_mask], feats[ho_mask])
        per, med = _median_r2(pred_diag, reps_ho, held, true_by_rule)
        entry = {
            "per_feature_r2": {n: round(float(v), 4) for n, v in zip(TARGET_NAMES, per)},
            "median_r2": round(med, 4),
        }
        if held_complex:
            _, med_cx = _median_r2(pred_diag, reps_ho, held_complex, true_by_rule)
            entry["complex_median_r2"] = round(med_cx, 4)
        summary["baselines"][name] = entry
        baseline_medians[name] = med
        tag = f", complex {entry.get('complex_median_r2')}" if held_complex else ""
        print(f"[s1] baseline {name:>5}: median R² {med:.4f}{tag}")
        print(f"       per-feature {entry['per_feature_r2']}")

    best_baseline = max(baseline_medians.values())
    summary["best_baseline_median_r2"] = round(best_baseline, 4)

    if cnn_pred is not None:
        per_cnn, med_cnn = _median_r2(cnn_pred[ho_mask], reps_ho, held, true_by_rule)
        summary["cnn"] = {
            "per_feature_r2": {n: round(float(v), 4) for n, v in zip(TARGET_NAMES, per_cnn)},
            "median_r2": round(med_cnn, 4),
        }
        if held_complex:
            _, med_cnn_cx = _median_r2(cnn_pred[ho_mask], reps_ho, held_complex, true_by_rule)
            summary["cnn"]["complex_median_r2"] = round(med_cnn_cx, 4)
        margin = med_cnn - best_baseline
        n_feat_beat = int(
            sum(
                c > b
                for c, b in zip(
                    per_cnn,
                    [summary["baselines"]["ridge"]["per_feature_r2"][n] for n in TARGET_NAMES],
                )
            )
        )
        summary["cnn_minus_best_baseline_median"] = round(margin, 4)
        summary["cnn_beats_baseline_on_n_features"] = n_feat_beat
        summary["meaningfully_better"] = bool(margin >= MARGIN and n_feat_beat >= 3)
        print(
            f"[s1] CNN median R² {med_cnn:.4f}  vs best baseline {best_baseline:.4f}  "
            f"margin {margin:+.4f} (bar +{MARGIN}); beats baseline on {n_feat_beat}/4 features "
            f"-> meaningfully_better={summary['meaningfully_better']}"
        )

    save_json(summary, out / "summary.json")

    # Bar chart: median R² by method (+ complex where applicable).
    labels_ = ["ridge", "gbm"] + (["CNN"] if cnn_pred is not None else [])
    med_vals = [baseline_medians["ridge"], baseline_medians["gbm"]] + (
        [summary["cnn"]["median_r2"]] if cnn_pred is not None else []
    )
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    ax.bar(labels_, med_vals, color=["#9ecae1", "#6baed6", "#08519c"][: len(labels_)])
    ax.axhline(0.5, ls="--", c="k", lw=0.8, alpha=0.6)
    ax.set_ylabel("median held-out-rule R²")
    ax.set_title(f"S1: single-diagram baseline vs amortizer (radius {radius})")
    ax.set_ylim(min(0, min(med_vals) - 0.05), 1.0)
    fig.tight_layout()
    fig.savefig(out / "baseline_vs_cnn.png", dpi=150)
    plt.close(fig)
    print(f"[s1] wrote {out}/summary.json")


if __name__ == "__main__":
    main()
