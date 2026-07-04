#!/usr/bin/env python3
"""R5 (EVALUATION_CRITERIA.md rev 7): how recoverable is the rule?

The referee's first concern: the "anti-shortcut" 2x2 architecture is asserted,
not shown, to block rule recovery. We measure recoverability directly and replace
the assertion with evidence. Three representation sources are compared:

* **raw diagram** — recovered *exactly* by the mechanistic inverter
  (:func:`caspectra.eval.rule_inference.infer_rule`; 100% on ECA, ~97.5% on
  range-2). We report that definitive number rather than a learned proxy.
* **five handcrafted statistics** — do texture features carry the rule?
* **CNN 64-d bottleneck** — does the "anti-shortcut" representation still encode
  the rule?

For the two learned/handcrafted sources we fit probes for (a) rule/orbit identity
(stratified split — identity cannot transfer) and (b) each individual truth-table
entry under a **leave-rules-out** split (does the source let you read rule *bits*
of unseen rules?). Balanced accuracy against the majority baseline. High accuracy
supports the paper's mechanism: the rule pervades every representation, so the
deep model's shortfall is a failure to *exploit* readable structure, not a lack
of it.

Usage::

    python scripts/probe_rule_recovery.py --config configs/lever_a_local.yaml \
        --checkpoint runs/lever_a_local_seed0/checkpoint_final.pt
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import GroupKFold, train_test_split
from sklearn.preprocessing import StandardScaler

from caspectra.config import ExperimentConfig
from caspectra.eval.baselines import compute_baseline_features
from caspectra.factory import build_dataset
from caspectra.utils import ensure_dir, save_json, set_seed


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="R5 rule-recovery probes (rev 7).")
    p.add_argument("--config", required=True)
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--device", default="mps")
    p.add_argument("--per-rule", type=int, default=32, help="Diagrams per rule for probing.")
    p.add_argument("--output-dir", default=None, help="Default <train.output_dir>/rule_probe.")
    return p.parse_args()


def _cnn_bottleneck(cfg, checkpoint, device_pref, subset_idx):
    import torch

    from caspectra.factory import build_model
    from caspectra.utils import select_device

    state = torch.load(checkpoint, map_location="cpu", weights_only=False)
    model = build_model(cfg.model)
    model.load_state_dict(state["model_state"])
    device = select_device(prefer=device_pref)
    model = model.to(device).eval()
    ds = build_dataset(cfg.data, training=False)
    embs = []
    with torch.no_grad():
        for i in range(0, len(subset_idx), 256):
            batch = subset_idx[i : i + 256]
            imgs = torch.from_numpy(ds.images[batch]).to(torch.float32).unsqueeze(1).to(device)
            embs.append(model.encoder(imgs).cpu().numpy())
    return np.concatenate(embs)


def _identity_ba(feats, labels, seed=0):
    """Balanced accuracy of a multinomial rule-identity probe (stratified split)."""
    tr, te = train_test_split(
        np.arange(len(labels)), test_size=0.3, stratify=labels, random_state=seed
    )
    scaler = StandardScaler().fit(feats[tr])
    clf = LogisticRegression(max_iter=2000, C=1.0)
    clf.fit(scaler.transform(feats[tr]), labels[tr])
    pred = clf.predict(scaler.transform(feats[te]))
    return float(balanced_accuracy_score(labels[te], pred))


def _bits_ba_leave_rules_out(feats, groups, rule_bits, n_bits, n_splits=5):
    """Mean per-bit balanced accuracy of reading truth-table entries on unseen rules."""
    gkf = GroupKFold(n_splits=n_splits)
    per_bit = np.full(n_bits, np.nan)
    for b in range(n_bits):
        y = rule_bits[:, b]
        if len(np.unique(y)) < 2:
            continue  # a bit that is constant across the panel is not probeable
        scores = []
        for tr, te in gkf.split(feats, y, groups):
            if len(np.unique(y[tr])) < 2:
                continue
            scaler = StandardScaler().fit(feats[tr])
            clf = LogisticRegression(max_iter=2000, C=1.0)
            clf.fit(scaler.transform(feats[tr]), y[tr])
            pred = clf.predict(scaler.transform(feats[te]))
            scores.append(balanced_accuracy_score(y[te], pred))
        if scores:
            per_bit[b] = float(np.mean(scores))
    return float(np.nanmean(per_bit)), per_bit


def _mechanistic_exact_rate(cfg):
    path = Path(f"{cfg.train.output_dir}/mechanistic_eval/summary.json")
    if path.exists():
        return json.loads(path.read_text()).get("exact_inference_rate")
    return None


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    out = ensure_dir(args.output_dir or f"{cfg.train.output_dir}/rule_probe")
    set_seed(cfg.seed)
    radius = cfg.data.radius
    n_bits = 1 << (2 * radius + 1)

    dataset = build_dataset(cfg.data, training=False)
    reps = np.asarray(dataset.equiv_reps)
    rules = sorted({int(r) for r in reps})

    # Subsample diagrams per rule to keep probe fitting cheap and balanced.
    rng = np.random.default_rng(0)
    idx = np.concatenate(
        [
            rng.choice(
                np.flatnonzero(reps == r), min(args.per_rule, int((reps == r).sum())), replace=False
            )
            for r in rules
        ]
    )
    idx.sort()
    labels = reps[idx]
    rule_bits = np.array([[(int(r) >> b) & 1 for b in range(n_bits)] for r in labels], dtype=int)

    feats_hand = StandardScaler().fit_transform(
        compute_baseline_features(dataset.images[idx], radius=radius)
    )
    feats_cnn = _cnn_bottleneck(cfg, args.checkpoint, args.device, idx)

    summary = {
        "radius": radius,
        "n_diagrams": len(idx),
        "n_rules": len(rules),
        "raw_diagram_exact_inference_rate": _mechanistic_exact_rate(cfg),
        "sources": {},
    }
    for name, feats in (("handcrafted5", feats_hand), ("cnn_bottleneck", feats_cnn)):
        ident = _identity_ba(feats, labels)
        bits_mean, per_bit = _bits_ba_leave_rules_out(feats, labels, rule_bits, n_bits)
        summary["sources"][name] = {
            "rule_identity_balanced_acc": round(ident, 4),
            "truth_table_bit_balanced_acc_leave_rules_out": round(bits_mean, 4),
        }
        print(
            f"[r5] {name:>14}: identity BA {ident:.3f}   "
            f"truth-table-bit BA (leave-rules-out) {bits_mean:.3f}"
        )
    summary["identity_majority_baseline"] = round(1.0 / len(rules), 4)
    print(
        f"[r5] raw-diagram exact rule inference (R4): "
        f"{summary['raw_diagram_exact_inference_rate']}"
    )
    save_json(summary, out / "summary.json")
    print(f"[r5] wrote {out}/summary.json")


if __name__ == "__main__":
    main()
