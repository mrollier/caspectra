#!/usr/bin/env python3
"""The decisive map control: CNN phenotype map vs a patch-wise hand-crafted map.

S1 showed the deep amortizer does not beat cheap single-diagram features at
predicting the *global* damage invariants. The only thing a scalar baseline
cannot produce is a *spatially-resolved* map — so the paper's contribution stands
or falls on whether the CNN's learned per-patch representation resolves behaviour
*more finely* than applying the same hand-crafted features to comparable local
windows.

This measures exactly that, with a maximally fair, matched design:

* Same striped two-rule diagrams (criterion-8a panel, periods, random phase).
* Same contrast metric (`stripe_contrast(column_profile(...)[RATE], mask, hot)`)
  applied identically to the CNN map and to a hand-crafted per-column map built
  at the **same column resolution** as the CNN map.
* The hand-crafted map: a gradient-boosted `spreading_rate` regressor trained on
  the full uniform training diagrams (exactly mirroring how the CNN is trained
  globally and applied locally), evaluated on a window around each map column.
  We sweep the window width and report the baseline's **best** resolution — the
  strongest baseline — so a CNN win is decisive.

Reported per checkpoint: relative contrast R(p) = C(p)/C(half) vs stripe period
for the CNN and each hand-crafted window, and the resolution limit (finest period
with median R(p) >= 0.5) of each. If the CNN's limit is finer than the best
hand-crafted window's, the learned map genuinely resolves behaviour the sliding
hand-crafted features cannot.

Usage::

    python scripts/validate_map_vs_baseline.py --config configs/lever_a_local.yaml
"""

from __future__ import annotations

import argparse
from itertools import combinations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402
from sklearn.ensemble import GradientBoostingRegressor  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

from caspectra.ca.nuca import NonUniformCA, half_mask, striped_mask  # noqa: E402
from caspectra.config import ExperimentConfig  # noqa: E402
from caspectra.data.splits import leave_rules_out_split  # noqa: E402
from caspectra.data.targets import TARGET_NAMES, load_or_compute_invariant_targets  # noqa: E402
from caspectra.eval.baselines import compute_baseline_features  # noqa: E402
from caspectra.eval.labels import load_rule_labels  # noqa: E402
from caspectra.eval.nuca_metrics import column_profile, stripe_contrast  # noqa: E402
from caspectra.factory import build_dataset, build_model  # noqa: E402
from caspectra.utils import ensure_dir, save_json, select_device, set_seed  # noqa: E402

PRIMARY_PANEL = [0, 4, 204, 184, 26, 73, 154, 90, 60, 30, 18, 45, 22, 41, 106, 54]
PERIODS = [32, 16, 8, 4]
RATE_GAP_MIN = 0.25
MIN_HALF_CONTRAST = 0.05
RATE = TARGET_NAMES.index("spreading_rate")
WINDOW_WIDTHS = [8, 12, 16, 24, 32]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="CNN map vs patch-wise hand-crafted map.")
    p.add_argument("--config", required=True)
    p.add_argument("--checkpoint", default=None)
    p.add_argument("--device", default="mps")
    p.add_argument("--output-dir", default=None)
    p.add_argument("--n-ic", type=int, default=16)
    p.add_argument("--panel", type=int, nargs="*", default=None, help="Smoke: override the panel.")
    p.add_argument("--periods", type=int, nargs="*", default=None, help="Smoke: override periods.")
    return p.parse_args()


@torch.no_grad()
def cnn_maps(model, diagrams, device, mean, std, batch=64):
    model.eval()
    out = []
    for s in range(0, len(diagrams), batch):
        b = torch.from_numpy(np.stack(diagrams[s : s + batch])).to(torch.float32).unsqueeze(1)
        out.append(model.predict_map(b.to(device)).cpu().numpy())
    maps = np.concatenate(out)
    return maps * std[None, :, None, None] + mean[None, :, None, None]


def fit_rate_gbm(cfg):
    """GBM predicting spreading_rate from single-diagram features, on the CNN's
    training rules (full uniform diagrams) — the hand-crafted analogue of the CNN."""
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
    gbm = GradientBoostingRegressor(random_state=0)
    gbm.fit(scaler.transform(feats[tr]), y[tr])
    return gbm, scaler


def handcrafted_profile(diagram, m, w, gbm, scaler, radius):
    """A length-m per-column spreading-rate profile from windows of width w."""
    width = diagram.shape[1]
    centers = ((np.arange(m) + 0.5) * width / m).astype(int)
    windows = np.stack(
        [np.take(diagram, range(c - w // 2, c - w // 2 + w), axis=1, mode="wrap") for c in centers]
    )
    feats = scaler.transform(compute_baseline_features(windows, radius=radius))
    return gbm.predict(feats)


def relative_contrast(per_pair_half, per_pair_p, min_half):
    halves = np.array(per_pair_half)
    usable = halves >= min_half
    if not usable.any():
        return None, 0
    return np.array(per_pair_p)[usable] / halves[usable], int(usable.sum())


def resolution_limit(rel_by_period):
    passing = [p for p in sorted(rel_by_period) if np.median(rel_by_period[p]) >= 0.5]
    return min(passing) if passing else None


def main() -> None:
    args = parse_args()
    cfg = ExperimentConfig.from_yaml(args.config)
    ckpt = args.checkpoint or cfg.eval.checkpoint
    out = ensure_dir(args.output_dir or f"{cfg.train.output_dir}/map_vs_baseline")
    set_seed(cfg.seed)
    device = select_device(prefer=args.device)
    width = cfg.data.grid_size
    radius = cfg.data.radius
    panel = args.panel if args.panel is not None else PRIMARY_PANEL
    periods = sorted(args.periods if args.periods is not None else PERIODS, reverse=True)
    print(f"[map] device={device} checkpoint={ckpt}")

    state = torch.load(ckpt, map_location="cpu", weights_only=False)
    mean, std = state["scaler_mean"], state["scaler_std"]
    model = build_model(cfg.model)
    model.load_state_dict(state["model_state"])
    model = model.to(device)

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
        (a, b)
        for a, b in combinations(panel, 2)
        if abs(rate_by_rule[a] - rate_by_rule[b]) >= RATE_GAP_MIN
    ]
    print(
        f"[map] {len(pairs)} pairs (rate gap >= {RATE_GAP_MIN}), periods {periods}, {args.n_ic} ICs"
    )

    gbm, scaler = fit_rate_gbm(cfg)
    m = cnn_maps(
        model,
        [
            NonUniformCA(0, 0, half_mask(width)).random_diagram(
                width, width, np.random.default_rng(0)
            )
        ],
        device,
        mean,
        std,
    ).shape[-1]
    print(f"[map] CNN map width = {m} columns; hand-crafted windows {WINDOW_WIDTHS}px")

    rng = np.random.default_rng(48)
    methods = ["cnn"] + [f"hc{w}" for w in WINDOW_WIDTHS]
    # per method: {period: [rel per usable pair]}, plus half contrasts per pair
    contrast = {mth: {"half": [], **{p: [] for p in periods}} for mth in methods}

    for a, b in pairs:
        hot = 0 if rate_by_rule[a] > rate_by_rule[b] else 1
        for label, base_mask in [("half", half_mask(width))] + [
            (p, striped_mask(width, p)) for p in periods
        ]:
            masks = [np.roll(base_mask, int(rng.integers(width))) for _ in range(args.n_ic)]
            diagrams = [
                NonUniformCA(a, b, mk).random_diagram(
                    width, width, np.random.default_rng([4, a, b, i])
                )
                for i, mk in enumerate(masks)
            ]
            cmaps = cnn_maps(model, diagrams, device, mean, std)
            cnn_c = np.mean(
                [stripe_contrast(column_profile(pm)[RATE], mk, hot) for pm, mk in zip(cmaps, masks)]
            )
            contrast["cnn"][label].append(cnn_c)
            for w in WINDOW_WIDTHS:
                hc_c = np.mean(
                    [
                        stripe_contrast(handcrafted_profile(d, m, w, gbm, scaler, radius), mk, hot)
                        for d, mk in zip(diagrams, masks)
                    ]
                )
                contrast[f"hc{w}"][label].append(hc_c)

    summary = {
        "checkpoint": str(ckpt),
        "map_width": int(m),
        "n_pairs": len(pairs),
        "window_widths": WINDOW_WIDTHS,
        "methods": {},
    }
    rel_curves = {}
    for mth in methods:
        rel = {}
        for p in periods:
            r, n_used = relative_contrast(
                contrast[mth]["half"], contrast[mth][p], MIN_HALF_CONTRAST
            )
            if r is not None:
                rel[p] = r
        med = {p: round(float(np.median(r)), 4) for p, r in rel.items()}
        limit = resolution_limit(rel)
        rel_curves[mth] = rel
        summary["methods"][mth] = {"relative_contrast_median": med, "resolution_limit_px": limit}
        print(f"[map] {mth:>6}: median R(p) {med}  -> resolution limit {limit} px")

    best_hc_limit = min(
        (summary["methods"][f"hc{w}"]["resolution_limit_px"] or 10**9) for w in WINDOW_WIDTHS
    )
    cnn_limit = summary["methods"]["cnn"]["resolution_limit_px"] or 10**9
    summary["best_handcrafted_limit_px"] = None if best_hc_limit >= 10**9 else best_hc_limit
    summary["cnn_limit_px"] = None if cnn_limit >= 10**9 else cnn_limit
    summary["cnn_resolves_finer"] = bool(cnn_limit < best_hc_limit)
    verdict = (
        "CNN RESOLVES FINER"
        if cnn_limit < best_hc_limit
        else ("TIE" if cnn_limit == best_hc_limit else "HAND-CRAFTED RESOLVES FINER")
    )
    summary["verdict"] = verdict
    print(
        f"[map] CNN limit {summary['cnn_limit_px']}px vs best hand-crafted "
        f"{summary['best_handcrafted_limit_px']}px  ->  {verdict}"
    )

    fig, ax = plt.subplots(figsize=(7, 4.5))
    xs = sorted(periods)
    for mth in methods:
        med = [float(np.median(rel_curves[mth][p])) if p in rel_curves[mth] else np.nan for p in xs]
        style = (
            dict(marker="o", lw=2.2, color="crimson") if mth == "cnn" else dict(marker=".", lw=1)
        )
        ax.plot(xs, med, label=mth, **style)
    ax.axhline(0.5, ls="--", c="grey", lw=0.8)
    ax.set_xscale("log", base=2)
    ax.set_xticks(xs), ax.set_xticklabels([str(p) for p in xs])
    ax.set_xlabel("stripe period (cells)"), ax.set_ylabel("relative contrast R(p)")
    ax.set_title(f"CNN map vs patch-wise hand-crafted map ({verdict})")
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(out / "map_vs_baseline.png", dpi=150)
    plt.close(fig)

    save_json(summary, out / "summary.json")
    print(f"[map] wrote {out}/summary.json")


if __name__ == "__main__":
    main()
