"""Collect per-rule held-out predictions for every method on one shared split.

The paired-inference (R1) and stacking (R2) analyses both need, for the *same*
held-out rules and the *same* cached truth, the four-vector prediction of each
method: the mechanistic rule-inference estimator, the ridge and gradient-boosted
single-diagram baselines, and the CNN amortiser. Centralising the collection here
guarantees the three analyses score identical rules against identical targets
(the referee's fairness requirement) and avoids duplicating the fit/forward code.
"""

from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

from caspectra.data.targets import TARGET_NAMES, load_or_compute_invariant_targets
from caspectra.eval.baselines import FEATURE_NAMES, compute_baseline_features
from caspectra.eval.rule_inference import mechanistic_estimate
from caspectra.factory import build_dataset

__all__ = ["HeldOutPredictions", "collect_held_out_predictions"]


@dataclass
class HeldOutPredictions:
    """Per-rule held-out predictions, aligned row-for-row with ``held``."""

    held: list[int]
    radius: int
    target_names: list[str]
    true: np.ndarray  # (N, 4)
    preds: dict[str, np.ndarray]  # method -> (N, 4)
    features: np.ndarray  # (N, 5) rule-averaged single-diagram baseline features
    feature_names: list[str]  # names of the 5 baseline features
    coverage: np.ndarray  # (N,) mechanistic table coverage
    complex_mask: np.ndarray  # (N,) held-out rule is a signature-complex rule


def _rule_means(values: np.ndarray, reps: np.ndarray, rules: list[int]) -> np.ndarray:
    return np.stack([values[reps == r].mean(axis=0) for r in rules])


def _baseline_pred(name, feats_tr, y_tr, feats_ho):
    if name == "ridge":
        model = Ridge(alpha=1.0)
        model.fit(feats_tr, y_tr)
        return model.predict(feats_ho)
    preds = np.empty((feats_ho.shape[0], y_tr.shape[1]))
    for j in range(y_tr.shape[1]):
        gb = GradientBoostingRegressor(random_state=0)
        gb.fit(feats_tr, y_tr[:, j])
        preds[:, j] = gb.predict(feats_ho)
    return preds


def _cnn_pred(cfg, checkpoint, device_pref):
    import torch

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


def collect_held_out_predictions(
    cfg,
    checkpoint: str,
    *,
    device: str = "mps",
    include_mechanistic: bool = True,
    mechanistic_n_pairs: int | None = None,
    use_cache: bool = True,
) -> HeldOutPredictions:
    """Fit/evaluate every method on the checkpoint's stored held-out split.

    The result is cached next to the checkpoint (the mechanistic simulation is
    the expensive part and is reused verbatim by the R1/R2/R5 analyses), keyed on
    the checkpoint path and the mechanistic ``n_pairs``.
    """
    n_pairs_key = mechanistic_n_pairs or cfg.targets.n_pairs
    cache_path = Path(checkpoint).with_name(
        f"held_out_preds_np{n_pairs_key}_{'mech' if include_mechanistic else 'nomech'}.pkl"
    )
    if use_cache and cache_path.exists():
        with cache_path.open("rb") as fh:
            return pickle.load(fh)

    radius = cfg.data.radius
    dataset = build_dataset(cfg.data, training=False)
    reps = np.asarray(dataset.equiv_reps)
    images = dataset.images
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

    cnn_pred_diag, holdout_rules = _cnn_pred(cfg, checkpoint, device)
    held = [r for r in holdout_rules if r in set(rules)]
    train_rules = [r for r in rules if r not in set(holdout_rules)]

    # Single-diagram baseline features (standardised on train rules only).
    feats = compute_baseline_features(images, radius=radius)
    scaler = StandardScaler().fit(feats[np.isin(reps, train_rules)])
    feats = scaler.transform(feats)
    y = np.stack([true_by_rule[int(r)] for r in reps])
    tr_mask, ho_mask = np.isin(reps, train_rules), np.isin(reps, held)
    reps_ho = reps[ho_mask]

    preds: dict[str, np.ndarray] = {}
    for name in ("ridge", "gbm"):
        pred_diag = _baseline_pred(name, feats[tr_mask], y[tr_mask], feats[ho_mask])
        preds[name] = _rule_means(pred_diag, reps_ho, held)
    preds["cnn"] = _rule_means(cnn_pred_diag[ho_mask], reps_ho, held)

    # Rule-averaged raw baseline features (standardised on train rules) for R2.
    held_features = _rule_means(feats[ho_mask], reps_ho, held)

    coverage = np.zeros(len(held))
    if include_mechanistic:
        n_pairs = mechanistic_n_pairs or cfg.targets.n_pairs
        mech = np.empty((len(held), len(TARGET_NAMES)))
        for i, r in enumerate(held):
            diagram = images[np.flatnonzero(reps == r)[0]]
            rng = np.random.default_rng(
                np.random.SeedSequence([int(cfg.targets.seed) + 104729, int(r), int(radius)])
            )
            feats_m, _, cov = mechanistic_estimate(
                diagram,
                radius,
                width=cfg.data.grid_size,
                n_pairs=n_pairs,
                ic_density=cfg.targets.ic_density,
                rng=rng,
            )
            mech[i] = feats_m
            coverage[i] = cov
        preds["mechanistic"] = mech

    complex_set = {int(r) for r in cfg.train.force_holdout_rules} if radius > 1 else set()
    complex_mask = np.array([r in complex_set for r in held], dtype=bool)

    result = HeldOutPredictions(
        held=[int(r) for r in held],
        radius=radius,
        target_names=list(TARGET_NAMES),
        true=np.stack([true_by_rule[r] for r in held]),
        preds=preds,
        features=held_features,
        feature_names=list(FEATURE_NAMES),
        coverage=coverage,
        complex_mask=complex_mask,
    )
    if use_cache:
        with cache_path.open("wb") as fh:
            pickle.dump(result, fh)
    return result
