#!/usr/bin/env python3
"""C3 (EVALUATION_CRITERIA.md rev 8): rule-table coverage & completion sensitivity.

The second referee (concern 3) noted that the mechanistic estimator's default-zero
fill of *unobserved* rule-table entries is an unacknowledged prior, and that the
few failed reconstructions may be systematically concentrated. This script exposes
the assumption and tests it. For the held-out rules it reports:

* the **coverage distribution** and **missing-entry counts**, broken down by
  outcome class (fully-covered vs under-covered) and by target stratum (Wolfram
  class where available);
* per-target held-out R^2 under the **default-0 / default-1 / empirical-MAP**
  completions (identical on fully-covered rules, so only the under-covered subset
  is re-simulated — the comparison is cheap on top of one base run);
* the **posterior-averaged** estimate that marginalises over unobserved entries
  under an empirical Bernoulli prior, and the empirical **calibration** of its
  predictive interval on the under-covered rules (rev-8 C3).

Usage::

    python scripts/validate_completion_policies.py --config configs/m4_range2.yaml \
        --checkpoint runs/m4_range2_seed0/checkpoint_final.pt
"""

from __future__ import annotations

import argparse

import numpy as np

from caspectra.config import ExperimentConfig
from caspectra.data.splits import leave_rules_out_split
from caspectra.data.targets import TARGET_NAMES, load_or_compute_invariant_targets
from caspectra.eval.dynamics import damage_spreading_features
from caspectra.eval.labels import load_rule_labels
from caspectra.eval.rule_inference import (
    complete_table,
    infer_rule_table,
    mechanistic_estimate_posterior,
    table_to_rule,
)
from caspectra.train.regression_trainer import r2_per_feature
from caspectra.utils import ensure_dir, save_json, set_seed

POLICIES = ["zero", "one", "empirical"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="C3 coverage & completion-policy sensitivity (rev 8).")
    p.add_argument("--config", required=True)
    p.add_argument("--checkpoint", default=None, help="Use this CNN's stored held-out split.")
    p.add_argument("--n-pairs", type=int, default=None)
    p.add_argument("--output-dir", default=None)
    return p.parse_args()


def _holdout(cfg, rules, checkpoint):
    if checkpoint:
        import torch

        state = torch.load(checkpoint, map_location="cpu", weights_only=False)
        return [int(r) for r in state["holdout_rules"]]
    labels = load_rule_labels(cfg.eval.rule_labels_csv)
    strata = (
        np.array([int(labels.wolfram.get(int(r), -1)) for r in rules])
        if labels and labels.has_wolfram
        else np.zeros(len(rules))
    )
    _, held = leave_rules_out_split(
        rules,
        strata,
        holdout_fraction=cfg.train.holdout_fraction,
        seed=cfg.train.holdout_seed,
        force_holdout=cfg.train.force_holdout_rules,
        force_train=cfg.train.force_train_rules,
    )
    return held


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    out = ensure_dir(args.output_dir or f"{cfg.train.output_dir}/completion_policies")
    set_seed(cfg.seed)
    radius = cfg.data.radius
    width = cfg.data.grid_size
    n_pairs = args.n_pairs if args.n_pairs is not None else cfg.targets.n_pairs

    from caspectra.factory import build_dataset

    dataset = build_dataset(cfg.data, training=False)
    reps = np.asarray(dataset.equiv_reps)
    images = dataset.images
    rules = sorted({int(r) for r in reps})

    targets = load_or_compute_invariant_targets(
        rules,
        width=width,
        ic_density=cfg.targets.ic_density,
        n_pairs=cfg.targets.n_pairs,
        seed=cfg.targets.seed,
        cache_dir=cfg.data.cache_dir,
        radius=radius,
    )
    true_by_rule = {r: targets[i] for i, r in enumerate(rules)}
    labels = load_rule_labels(cfg.eval.rule_labels_csv)

    held = [r for r in _holdout(cfg, rules, args.checkpoint) if r in set(rules)]
    tsize = 1 << (2 * radius + 1)
    print(f"[c3] radius={radius} n_pairs={n_pairs} {len(held)} held-out rules; table size {tsize}")

    def _rng(rule: int, tag: int) -> np.random.Generator:
        return np.random.default_rng(
            np.random.SeedSequence([int(cfg.targets.seed) + 104729, int(rule), int(radius), tag])
        )

    def _sim(rule_number: int, gen) -> np.ndarray:
        if radius == 1:
            return damage_spreading_features(
                rule_number,
                width=width,
                n_pairs=n_pairs,
                ic_density=cfg.targets.ic_density,
                rng=gen,
            )
        from caspectra.ca.range_ca import RangeCA

        return damage_spreading_features(
            simulator=RangeCA(rule_number, radius),
            width=width,
            n_pairs=n_pairs,
            ic_density=cfg.targets.ic_density,
            rng=gen,
        )

    coverages, n_missing, exact = [], [], []
    strata = []
    preds = {pol: [] for pol in POLICIES}
    under_idx = []  # positions (in held order) of under-covered rules
    post_records = []  # (rule, k, within1sigma per target)

    for pos, r in enumerate(held):
        diagram = images[np.flatnonzero(reps == r)[0]]
        table, observed, _ = infer_rule_table(diagram, radius)
        cov = float(observed.mean())
        k = int((~observed).sum())
        coverages.append(cov)
        n_missing.append(k)
        exact.append(table_to_rule(complete_table(table, observed, "zero")) == int(r) and k == 0)
        strata.append(int(labels.wolfram.get(int(r), -1)) if labels and labels.has_wolfram else -1)

        if k == 0:
            feats = _sim(table_to_rule(table), _rng(r, 0))
            for pol in POLICIES:
                preds[pol].append(feats)  # identical when fully covered
        else:
            under_idx.append(pos)
            for pol in POLICIES:
                rule_pol = table_to_rule(complete_table(table, observed, pol))
                preds[pol].append(_sim(rule_pol, _rng(r, hash(pol) & 0xFFFF)))
            # posterior estimate + calibration
            mean, std, _, _, kk = mechanistic_estimate_posterior(
                diagram,
                radius,
                width=width,
                n_pairs=n_pairs,
                ic_density=cfg.targets.ic_density,
                rng=_rng(r, 7),
            )
            truth = true_by_rule[r]
            within = np.abs(truth - mean) <= np.maximum(std, 1e-9)
            post_records.append({"rule": int(r), "k": kk, "within1sigma": within.tolist()})

    true_rule = np.stack([true_by_rule[r] for r in held])
    per_policy_r2 = {
        pol: {
            n: round(float(v), 4)
            for n, v in zip(TARGET_NAMES, r2_per_feature(np.stack(preds[pol]), true_rule))
        }
        for pol in POLICIES
    }

    coverages = np.array(coverages)
    n_missing = np.array(n_missing)
    n_under = int((coverages < 1.0).sum())
    summary = {
        "radius": radius,
        "n_pairs": n_pairs,
        "n_held_out": len(held),
        "table_size": tsize,
        "coverage": {
            "min": round(float(coverages.min()), 4),
            "median": round(float(np.median(coverages)), 4),
            "mean": round(float(coverages.mean()), 4),
            "n_fully_covered": int((coverages >= 1.0).sum()),
            "n_under_covered": n_under,
            "frac_under_covered": round(float(n_under / len(held)), 4),
        },
        "missing_entries": {
            "max": int(n_missing.max()),
            "mean_among_under_covered": round(
                float(n_missing[coverages < 1.0].mean()) if n_under else 0.0, 4
            ),
        },
        "per_policy_median_r2": {
            pol: round(float(np.nanmedian(list(v.values()))), 4) for pol, v in per_policy_r2.items()
        },
        "per_policy_r2": per_policy_r2,
        "under_covered_rules": [int(held[i]) for i in under_idx],
    }
    if post_records:
        within = np.array([rec["within1sigma"] for rec in post_records])  # (n_under, 4)
        summary["posterior_calibration_1sigma"] = {
            n: round(float(within[:, j].mean()), 4) for j, n in enumerate(TARGET_NAMES)
        }
        summary["posterior_n_rules"] = len(post_records)
    # per-policy R2 on the under-covered subset (where the policy actually matters)
    if under_idx:
        tu = true_rule[under_idx]
        summary["per_policy_r2_under_covered"] = {
            pol: {
                n: round(float(v), 4)
                for n, v in zip(TARGET_NAMES, r2_per_feature(np.stack(preds[pol])[under_idx], tu))
            }
            for pol in POLICIES
        }

    save_json(summary, out / "summary.json")
    cov = summary["coverage"]
    print(
        f"[c3] coverage min {cov['min']:.3f} median {cov['median']:.3f}; "
        f"under-covered {cov['n_under_covered']}/{len(held)} "
        f"(mean missing {summary['missing_entries']['mean_among_under_covered']:.2f})"
    )
    for pol in POLICIES:
        print(
            f"[c3] completion={pol:>9}: "
            f"median R² {summary['per_policy_median_r2'][pol]:.4f}  {per_policy_r2[pol]}"
        )
    if "posterior_calibration_1sigma" in summary:
        print(
            "[c3] posterior 1σ calibration (under-covered): "
            f"{summary['posterior_calibration_1sigma']}"
        )
    print(f"[c3] wrote {out}/summary.json")


if __name__ == "__main__":
    main()
