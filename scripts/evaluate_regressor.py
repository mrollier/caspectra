#!/usr/bin/env python3
"""Evaluate a Lever A checkpoint against criterion 6 (EVALUATION_CRITERIA.md rev 2).

Reports, for the held-out rules of the leave-rules-out split stored in the
checkpoint:

1. **Criterion 6 (the gate):** per-feature R² across held-out rules, computed on
   rule-level mean predictions (the amortized estimate of the rule's invariant)
   — success: median across features ≥ 0.5; failure: < 0.2. Rule 110 (the
   unseen complex rule) reported separately. Diagram-level R² and a
   per-Wolfram-class breakdown are given as context, with borderline rules
   (40/41/42/106) flagged.
2. **Amortized vs direct taxonomy:** the agglomerative k=14 protocol from
   ``scripts/protocol_sensitivity.py`` run on orbit-averaged *predicted*
   invariants vs the *direct* targets — per-class recall + {54, 110}
   co-membership side by side.
3. **Embedding diagnostics:** participation ratio + rule(orbit) probe (reported
   as a diagnostic, not pass/fail).
4. **Per-patch phenotype maps:** ``predict_map`` rendered for a few diagrams —
   the qualitative preview of the nuCA payoff.
"""

from __future__ import annotations

import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402
from sklearn.cluster import AgglomerativeClustering  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

from caspectra.config import ExperimentConfig  # noqa: E402
from caspectra.data.targets import TARGET_NAMES, load_or_compute_invariant_targets  # noqa: E402
from caspectra.eval.embed import extract_embeddings  # noqa: E402
from caspectra.eval.labels import load_rule_labels  # noqa: E402
from caspectra.eval.probes import run_probes  # noqa: E402
from caspectra.eval.salience import participation_ratio, per_class_cluster_recall  # noqa: E402
from caspectra.factory import build_dataloader, build_dataset, build_model  # noqa: E402
from caspectra.train.regression_trainer import r2_per_feature  # noqa: E402
from caspectra.utils import ensure_dir, save_json, select_device, set_seed  # noqa: E402

K_CLUSTERS = 14  # same granularity as scripts/protocol_sensitivity.py
MAP_RULES = [110, 30, 0, 204]  # complex / chaotic / null / identity demo panel


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a Lever A checkpoint.")
    parser.add_argument("--config", required=True, help="Path to a YAML ExperimentConfig.")
    parser.add_argument("--checkpoint", default=None, help="Override eval.checkpoint.")
    parser.add_argument("--device", default="mps", help="Preferred device (mps/cpu/cuda).")
    parser.add_argument("--output-dir", default=None, help="Override eval.output_dir.")
    return parser.parse_args()


@torch.no_grad()
def predict_all(model, loader, device, scaler_mean, scaler_std) -> np.ndarray:
    """Unstandardized per-diagram predictions ``(N, n_targets)``."""
    model.eval()
    preds = []
    for image, _metadata in loader:
        preds.append(model(image.to(device)).cpu().numpy())
    return np.concatenate(preds) * scaler_std + scaler_mean


def rule_means(values: np.ndarray, reps: np.ndarray, rules: list[int]) -> np.ndarray:
    return np.stack([values[reps == r].mean(axis=0) for r in rules])


def taxonomy_recall(features: np.ndarray, wolfram: np.ndarray, rules: np.ndarray) -> dict:
    """The k=14 agglomerative protocol: per-class recall + {54,110} co-membership.

    k is clamped below the rule count so smoke-scale runs (few rules) still work;
    at the full 88 rules this is exactly the ``protocol_sensitivity.py`` protocol.
    """
    k = min(K_CLUSTERS, len(rules) - 1)
    lab = AgglomerativeClustering(n_clusters=k).fit_predict(
        StandardScaler().fit_transform(features)
    )
    recall = per_class_cluster_recall(lab, wolfram)
    i54 = int(np.where(rules == 54)[0][0])
    i110 = int(np.where(rules == 110)[0][0])
    cluster54 = [int(r) for r in rules[lab == lab[i54]]]
    return {
        "per_class_recall": {int(k): round(v, 4) for k, v in recall.items()},
        "rule54_110_together": bool(lab[i54] == lab[i110]),
        "rule54_cluster": cluster54,
    }


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    checkpoint_path = args.checkpoint or cfg.eval.checkpoint
    output_dir = ensure_dir(args.output_dir or cfg.eval.output_dir)
    set_seed(cfg.seed)
    device = select_device(prefer=args.device)
    print(f"[eval-a] device={device} checkpoint={checkpoint_path}")

    state = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    scaler_mean, scaler_std = state["scaler_mean"], state["scaler_std"]
    holdout_rules = [int(r) for r in state["holdout_rules"]]
    train_rules = [int(r) for r in state["train_rules"]]
    target_names = state.get("target_names", TARGET_NAMES)

    model = build_model(cfg.model)
    model.load_state_dict(state["model_state"])
    model = model.to(device)

    dataset = build_dataset(cfg.data, training=False)  # raw diagrams, cache hit
    loader = build_dataloader(
        dataset, batch_size=cfg.eval.batch_size, shuffle=False, num_workers=cfg.train.num_workers
    )
    reps = dataset.equiv_reps
    all_rules = sorted({int(r) for r in reps})
    labels = load_rule_labels(cfg.eval.rule_labels_csv)
    wolfram_by_rule = (
        {r: int(labels.wolfram.get(r, -1)) for r in all_rules}
        if labels
        else dict.fromkeys(all_rules, -1)
    )
    borderline = labels.borderline if labels else set()

    predictions = predict_all(model, loader, device, scaler_mean, scaler_std)
    targets = load_or_compute_invariant_targets(
        all_rules,
        width=cfg.data.grid_size,
        ic_density=cfg.targets.ic_density,
        n_pairs=cfg.targets.n_pairs,
        seed=cfg.targets.seed,
        cache_dir=cfg.data.cache_dir,
        radius=cfg.data.radius,
    )
    target_by_rule = {r: targets[i] for i, r in enumerate(all_rules)}

    # --- 1. Criterion 6 -----------------------------------------------------
    held = [r for r in holdout_rules if r in set(all_rules)]
    pred_rule = rule_means(predictions, reps, held)  # amortized estimate per rule
    true_rule = np.stack([target_by_rule[r] for r in held])
    r2_rule = r2_per_feature(pred_rule, true_rule)
    hmask = np.isin(reps, held)
    r2_diag = r2_per_feature(
        predictions[hmask], np.stack([target_by_rule[int(r)] for r in reps[hmask]])
    )
    median_rule_r2 = float(np.nanmedian(r2_rule))
    verdict = (
        "PASS" if median_rule_r2 >= 0.5 else ("FAIL" if median_rule_r2 < 0.2 else "INCONCLUSIVE")
    )
    print(f"[eval-a] criterion 6 — {len(held)} held-out rules (rule-level R², the gate):")
    for n, rr, dr in zip(target_names, r2_rule, r2_diag):
        print(f"    {n:>18}: rule-level R²={rr:.3f}  (diagram-level {dr:.3f})")
    print(
        f"[eval-a] criterion 6 median across features = {median_rule_r2:.3f} "
        f"-> {verdict} (success >= 0.5, failure < 0.2)"
    )

    per_rule_report = {}
    for i, r in enumerate(held):
        flag = " [borderline]" if r in borderline else ""
        per_rule_report[r] = {
            "wolfram": wolfram_by_rule.get(r, -1),
            "predicted": [round(float(v), 4) for v in pred_rule[i]],
            "true": [round(float(v), 4) for v in true_rule[i]],
        }
        if r == 110:
            pairs = ", ".join(
                f"{n}: {p:.3f} (true {t:.3f})"
                for n, p, t in zip(target_names, pred_rule[i], true_rule[i])
            )
            print(f"[eval-a] rule 110 (unseen complex rule){flag}: {pairs}")

    # Per-Wolfram-class diagram-level R² on held-out rules (context).
    r2_by_class = {}
    held_wolf = np.array([wolfram_by_rule.get(int(r), -1) for r in reps[hmask]])
    held_targets = np.stack([target_by_rule[int(r)] for r in reps[hmask]])
    for c in sorted(set(held_wolf.tolist()) - {-1}):
        m = held_wolf == c
        vals = r2_per_feature(predictions[hmask][m], held_targets[m])
        r2_by_class[int(c)] = [None if np.isnan(v) else round(float(v), 3) for v in vals]
    print(f"[eval-a] diagram-level R² per Wolfram class (held-out): {r2_by_class}")

    # --- 2. Amortized vs direct taxonomy ------------------------------------
    rules_arr = np.array(all_rules)
    wolf_arr = np.array([wolfram_by_rule[r] for r in all_rules])
    amortized = taxonomy_recall(rule_means(predictions, reps, all_rules), wolf_arr, rules_arr)
    direct = taxonomy_recall(targets, wolf_arr, rules_arr)
    print(f"[eval-a] taxonomy (k={K_CLUSTERS}) on amortized invariants: {amortized}")
    print(f"[eval-a] taxonomy (k={K_CLUSTERS}) on direct invariants:    {direct}")

    # --- 3. Embedding diagnostics --------------------------------------------
    embeddings, _rules, equiv_reps = extract_embeddings(model, loader, device)
    pr = participation_ratio(embeddings)
    probe_report = run_probes(embeddings, equiv_reps, labels, seed=cfg.seed)
    print(f"[eval-a] participation ratio = {pr:.1f} / {embeddings.shape[1]} dims")
    print("[eval-a] diagnostic probes (not pass/fail):")
    print(probe_report.summary())

    # --- 4. Per-patch phenotype maps -----------------------------------------
    rate_idx = target_names.index("spreading_rate")
    demo_rules = [r for r in MAP_RULES if r in set(all_rules)]
    if demo_rules and hasattr(model.encoder, "feature_map"):
        fig, axes = plt.subplots(2, len(demo_rules), figsize=(3.2 * len(demo_rules), 6))
        for col, r in enumerate(demo_rules):
            idx = int(np.flatnonzero(reps == r)[0])
            image = torch.from_numpy(dataset.images[idx]).float().unsqueeze(0).unsqueeze(0)
            with torch.no_grad():
                pmap = model.predict_map(image.to(device)).cpu().numpy()[0]
            pmap = pmap * scaler_std[:, None, None] + scaler_mean[:, None, None]
            axes[0, col].imshow(dataset.images[idx], cmap="binary", interpolation="nearest")
            axes[0, col].set_title(f"rule {r} (w{wolfram_by_rule.get(r, '?')})", fontsize=9)
            im = axes[1, col].imshow(pmap[rate_idx], cmap="viridis")
            fig.colorbar(im, ax=axes[1, col], fraction=0.046)
            for ax in (axes[0, col], axes[1, col]):
                ax.set_xticks([]), ax.set_yticks([])
        axes[1, 0].set_ylabel("predicted spreading rate", fontsize=8)
        fig.suptitle("Per-patch phenotype maps (qualitative nuCA-payoff preview)")
        fig.tight_layout()
        fig.savefig(output_dir / "phenotype_maps.png", dpi=120)
        plt.close(fig)

    save_json(
        {
            "criterion6_rule_level_r2": {
                n: None if np.isnan(v) else round(float(v), 4)
                for n, v in zip(target_names, r2_rule)
            },
            "criterion6_median_r2": round(median_rule_r2, 4),
            "criterion6_verdict": verdict,
            "diagram_level_r2": {
                n: None if np.isnan(v) else round(float(v), 4)
                for n, v in zip(target_names, r2_diag)
            },
            "r2_by_wolfram_class": r2_by_class,
            "held_out_rules": held,
            "train_rules": train_rules,
            "per_held_out_rule": per_rule_report,
            "taxonomy_amortized": amortized,
            "taxonomy_direct": direct,
            "participation_ratio": round(float(pr), 3),
            "rule_probe_acc_diagnostic": probe_report.rule.accuracy,
        },
        output_dir / "summary.json",
    )
    print(f"[eval-a] artifacts in {output_dir.resolve()}")


if __name__ == "__main__":
    main()
