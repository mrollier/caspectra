#!/usr/bin/env python3
"""M11 -- retrieval (nearest-training-rule) baseline (EVALUATION_CRITERIA rev 13).

The fourth referee report (§5.3) points out that a paper framed around shortcut
learning has no baseline separating *"the network recognises which training rule
this diagram resembles"* from *"the network generalises to unseen tables"*. This
script supplies it: no training, no simulation, just a lookup.

For every held-out diagram, find the nearest **training** rule in a feature
space, and return that training rule's *cached target vector* as the prediction.
Predictions are averaged within rule before scoring, exactly as for the direct
estimators (Appendix B evaluation protocol, item 2). Two metric spaces:

* ``stats5``   -- the five label-free single-diagram statistics, standardised on
  training rules (the same features the boosted baseline of record consumes).
* ``bottleneck`` -- the trained CNN's 64-d bottleneck, i.e. retrieval *in the
  network's own representation*. If the CNN's accuracy were mostly rule
  recognition, retrieval in its embedding should approach its regression score.

Interpretation rule, fixed in rev 13 before measurement: a retrieval score close
to the CNN's is evidence that the direct network's accuracy is substantially
rule recognition; a retrieval score well below it is evidence against that
reading. Both directions are reported.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.preprocessing import StandardScaler

from caspectra.config import ExperimentConfig
from caspectra.data.targets import TARGET_NAMES, load_or_compute_invariant_targets
from caspectra.eval.baselines import compute_baseline_features
from caspectra.factory import build_dataloader, build_dataset, build_model
from caspectra.utils import ensure_dir, save_json, select_device, set_seed


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="M11 retrieval baseline (rev 13).")
    p.add_argument("--config", required=True)
    p.add_argument("--checkpoint", required=True, help="CNN checkpoint (its stored split is used).")
    p.add_argument("--device", default="mps")
    p.add_argument("--n-boot", type=int, default=10000)
    p.add_argument("--sigma-e", default=None, help="per_rule_sigma_e.npz for the rho column.")
    p.add_argument("--output-dir", default=None, help="Default <train.output_dir>/retrieval.")
    return p.parse_args()


def _rule_means(values: np.ndarray, reps: np.ndarray, rules: list[int]) -> np.ndarray:
    return np.stack([values[reps == r].mean(axis=0) for r in rules])


def _r2(true: np.ndarray, pred: np.ndarray) -> np.ndarray:
    res = np.sum((true - pred) ** 2, axis=0)
    tot = np.sum((true - true.mean(axis=0)) ** 2, axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        return 1.0 - res / tot


def _r2_boot(true: np.ndarray, pred: np.ndarray, boot: np.ndarray) -> np.ndarray:
    t, p = true[boot], pred[boot]
    res = np.sum((t - p) ** 2, axis=1)
    tot = np.sum((t - t.mean(axis=1, keepdims=True)) ** 2, axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        return 1.0 - res / tot


def _retrieve(space_tr: np.ndarray, space_ho: np.ndarray, y_tr_rule: np.ndarray) -> np.ndarray:
    """Nearest training rule per held-out diagram -> that rule's cached target."""
    # (n_ho, n_train_rules) squared Euclidean distances, chunked to bound memory.
    out = np.empty((space_ho.shape[0], y_tr_rule.shape[1]))
    step = 2048
    for i in range(0, space_ho.shape[0], step):
        chunk = space_ho[i : i + step]
        d = ((chunk[:, None, :] - space_tr[None, :, :]) ** 2).sum(-1)
        out[i : i + step] = y_tr_rule[d.argmin(axis=1)]
    return out


def main() -> None:
    args = parse_args()
    import torch

    cfg = ExperimentConfig.from_yaml(args.config)
    out_dir = ensure_dir(args.output_dir or f"{cfg.train.output_dir}/retrieval")
    set_seed(cfg.seed)
    radius = cfg.data.radius

    ds = build_dataset(cfg.data, training=False)
    reps = np.asarray(ds.equiv_reps)
    images = ds.images
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

    state = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    held = [int(r) for r in state["holdout_rules"] if int(r) in set(rules)]
    train_rules = [r for r in rules if r not in set(held)]
    tr_mask, ho_mask = np.isin(reps, train_rules), np.isin(reps, held)
    reps_ho = reps[ho_mask]
    print(f"[m11] radius={radius} {len(train_rules)} train rules, {len(held)} held out")

    y_tr_rule = np.stack([true_by_rule[r] for r in train_rules])
    true_ho = np.stack([true_by_rule[r] for r in held])

    spaces: dict[str, tuple[np.ndarray, np.ndarray]] = {}

    feats = compute_baseline_features(images, radius=radius)
    feats = StandardScaler().fit(feats[tr_mask]).transform(feats)
    spaces["stats5"] = (_rule_means(feats[tr_mask], reps[tr_mask], train_rules), feats[ho_mask])

    model = build_model(cfg.model)
    model.load_state_dict(state["model_state"])
    device = select_device(prefer=args.device)
    model = model.to(device).eval()
    loader = build_dataloader(
        ds, batch_size=cfg.eval.batch_size, shuffle=False, num_workers=cfg.train.num_workers
    )
    with torch.no_grad():
        emb = np.concatenate(
            [model.extract_embedding(img.to(device)).cpu().numpy() for img, _ in loader]
        )
    emb = StandardScaler().fit(emb[tr_mask]).transform(emb)
    spaces["bottleneck"] = (_rule_means(emb[tr_mask], reps[tr_mask], train_rules), emb[ho_mask])

    sigma_e = None
    if args.sigma_e and Path(args.sigma_e).exists():
        z = np.load(args.sigma_e)
        lookup = {int(r): z["sigma_e"][i] for i, r in enumerate(z["rules"])}
        if all(r in lookup for r in held):
            sigma_e = np.stack([lookup[r] for r in held])

    rng = np.random.default_rng(0)
    boot = rng.integers(0, len(held), size=(args.n_boot, len(held)))
    results: dict[str, dict] = {}
    for name, (space_tr, space_ho_diag) in spaces.items():
        pred_diag = _retrieve(space_tr, space_ho_diag, y_tr_rule)
        pred = _rule_means(pred_diag, reps_ho, held)
        r2 = _r2(true_ho, pred)
        draws = _r2_boot(true_ho, pred, boot)
        lo, hi = np.percentile(draws, [2.5, 97.5], axis=0)
        row = {
            t: {
                "r2": round(float(r2[j]), 4),
                "r2_ci95": [round(float(lo[j]), 4), round(float(hi[j]), 4)],
            }
            for j, t in enumerate(TARGET_NAMES)
        }
        if sigma_e is not None:
            rho = np.sqrt(np.mean(((true_ho - pred) / sigma_e) ** 2, axis=0))
            for j, t in enumerate(TARGET_NAMES):
                row[t]["rho"] = round(float(rho[j]), 3)
        row["median_r2"] = round(float(np.median(r2)), 4)
        results[name] = row
        print(
            f"[m11] {name:11s} median R2 {row['median_r2']:.4f}  "
            + "  ".join(f"{t.split('_')[-1]}={row[t]['r2']:.3f}" for t in TARGET_NAMES)
        )

    summary = {
        "radius": radius,
        "n_train_rules": len(train_rules),
        "n_held": len(held),
        "checkpoint": args.checkpoint,
        "per_rule_sigma_e": bool(sigma_e is not None),
        "retrieval": results,
    }
    save_json(summary, Path(out_dir) / "summary.json")
    print(f"[m11] wrote {Path(out_dir) / 'summary.json'}")
    print(json.dumps({k: v["median_r2"] for k, v in results.items()}, indent=1))


if __name__ == "__main__":
    main()
