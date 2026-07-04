"""Regenerate the manuscript figures from committed results.

Run from the repo root in the ssl-ecas env:
    python manuscript/make_figures.py
Reads cache/s4_landscape.npz (S4) and runs/*/map_vs_baseline/summary.json
(the map control), writes manuscript/figures/*.pdf.
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "manuscript" / "figures"
FIG.mkdir(parents=True, exist_ok=True)
RATE, FILL = 2, 3

# ---- Figure 1: the range-2 complexity landscape (S4) ----------------------
d = np.load(ROOT / "cache" / "s4_landscape.npz")
t, mask = d["targets"], d["mask"].astype(bool)
anchors = {  # embedded-ECA (rate, fill), from the S4 run
    "204": (0.008, 1.0), "184": (0.048, 1.0), "30": (0.307, 0.529),
    "90": (0.492, 0.271), "54": (0.225, 0.494), "110": (0.214, 0.569),
}
fig, ax = plt.subplots(figsize=(5.4, 4.2))
ax.scatter(t[~mask, RATE], t[~mask, FILL], s=7, alpha=0.25, c="steelblue", label="ordinary")
ax.scatter(t[mask, RATE], t[mask, FILL], s=14, alpha=0.7, c="crimson",
           label=f"complex ({mask.sum()}/{len(mask)} = {mask.mean():.1%})")
for name, (r, f) in anchors.items():
    ax.scatter([r], [f], marker="*", s=150, c="gold", edgecolor="k", zorder=5)
    ax.annotate(name, (r, f), textcoords="offset points", xytext=(4, 3), fontsize=8)
ax.set_xlabel("spreading rate  (0 = frozen, 1 = light speed)")
ax.set_ylabel("cone fill  (low = gliders, high = solid)")
ax.set_title("Range-2 behaviour landscape (stars: embedded ECAs)")
ax.legend(fontsize=8, loc="upper right")
fig.tight_layout()
fig.savefig(FIG / "landscape.pdf")
plt.close(fig)
print("wrote landscape.pdf")

# ---- Figure 2: map benchmark, CNN vs hand-crafted (map control) -----------
fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.6), sharey=True)
for ax, (run, title) in zip(axes, [("lever_a_local", "7x7 map"), ("lever_a_shallow", "15x15 map")]):
    s = json.loads((ROOT / "runs" / run / "map_vs_baseline" / "summary.json").read_text())
    periods = sorted(int(p) for p in s["methods"]["cnn"]["relative_contrast_median"])

    def curve(mth):
        m = s["methods"][mth]["relative_contrast_median"]
        return [m.get(str(p), np.nan) for p in periods]

    best_w = min(s["window_widths"],
                 key=lambda w: s["methods"][f"hc{w}"]["resolution_limit_px"] or 1e9)
    ax.plot(periods, curve("cnn"), "o-", lw=2.4, c="crimson", label="CNN map")
    ax.plot(periods, curve(f"hc{best_w}"), "s--", lw=1.8, c="steelblue",
            label=f"hand-crafted ({best_w}px window)")
    ax.axhline(0.5, ls=":", c="grey", lw=0.9)
    ax.set_xscale("log", base=2)
    ax.set_xticks(periods)
    ax.set_xticklabels([str(p) for p in periods])
    ax.set_xlabel("stripe period (cells)")
    ax.set_title(title)
    ax.legend(fontsize=8)
axes[0].set_ylabel("relative contrast R(p)")
fig.suptitle("Spatial resolution: the learned map has no advantage", y=1.02)
fig.tight_layout()
fig.savefig(FIG / "map_benchmark.pdf", bbox_inches="tight")
plt.close(fig)
print("wrote map_benchmark.pdf")
