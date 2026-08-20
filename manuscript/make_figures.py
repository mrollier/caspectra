"""Regenerate the manuscript figures from committed results.

Run from the repo root in the ssl-ecas env:
    python manuscript/make_figures.py
Reads cache/s4_landscape.npz (S4), writes manuscript/figures/*.pdf.

History: a second figure (map_benchmark.pdf, "the learned map has no
advantage") was removed in the round-3 revision — it was never included by
main.tex and its title carried the retired rev-7 claim (the registered
verdict is *inconclusive*; RESULTS.md rev-8 C6).
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "manuscript" / "figures"
FIG.mkdir(parents=True, exist_ok=True)
RATE, FILL = 2, 3

# ---- Figure 1: the range-2 damage-signature landscape (S4) ----------------
d = np.load(ROOT / "cache" / "s4_landscape.npz")
t, mask = d["targets"], d["mask"].astype(bool)
anchors = {  # embedded-ECA (rate, fill), from the S4 run
    "204": (0.008, 1.0),
    "184": (0.048, 1.0),
    "30": (0.307, 0.529),
    "90": (0.492, 0.271),
    "54": (0.225, 0.494),
    "110": (0.214, 0.569),
}
fig, ax = plt.subplots(figsize=(5.4, 4.2))

# Iso-damage-fraction contours (referee 4, §3.6). fill = E[N/ext] and
# (w/2rT)*fraction/rate agree up to Jensen, so at fixed damage fraction the two
# plotted coordinates trace a hyperbola. Drawing the family lets the reader see
# how much of the red region's shape is the coordinate choice -- and the honest
# answer is: a lot. The signature rules span only 1.5x in damage fraction
# (IQR 0.084-0.124) against 2.6x for the bulk, so the region lies largely
# BETWEEN two contours rather than cutting across them. In decorrelated
# coordinates (rate vs N/(2rT) = fill*rate, not mechanically tied to extent)
# the same rules do not separate from the bulk: the best axis-aligned box
# containing all 234 of them also contains 732 ordinary rules (F1 = 0.39).
# The red set is a registered THRESHOLD REGION, not a discovered cluster, and
# the caption says so.
W, R, T = 127, 2, 30
K = W / (2 * R * T)
rate_grid = np.linspace(0.02, 0.9, 200)
for frac in (0.02, 0.05, 0.1, 0.2, 0.4):
    ax.plot(
        rate_grid,
        np.clip(K * frac / rate_grid, 0, 1.05),
        color="gray",
        lw=0.6,
        ls=":",
        alpha=0.55,
        zorder=0,
    )
ax.plot([], [], color="gray", lw=0.6, ls=":", label="iso damage-fraction")

ax.scatter(t[~mask, RATE], t[~mask, FILL], s=7, alpha=0.25, c="steelblue", label="ordinary")
# "damage signature", not "complex": the registered criterion is a
# finite-horizon damage signature, deliberately not promoted to a class label
# (manuscript Sec. IV G; rule_labels_PROVENANCE.md).
ax.scatter(
    t[mask, RATE],
    t[mask, FILL],
    s=14,
    alpha=0.7,
    c="crimson",
    label=f"damage signature ({mask.sum()}/{len(mask)} = {mask.mean():.1%})",
)
ax.scatter([], [], marker="*", s=150, c="gold", edgecolor="k", label="embedded ECA")
# 204 and 184 both sit at fill = 1.0 (a single surviving damaged cell has
# extent 1, so fill is 1 by construction -- the sparse-end degeneracy noted in
# Sec. II B); offset their labels so they do not collide.
offsets = {"204": (4, -10), "184": (4, 4)}
for name, (r, f) in anchors.items():
    ax.scatter([r], [f], marker="*", s=150, c="gold", edgecolor="k", zorder=5)
    ax.annotate(
        name,
        (r, f),
        textcoords="offset points",
        xytext=offsets.get(name, (4, 3)),
        fontsize=8,
    )
ax.set_xlim(-0.02, 0.88)
ax.set_ylim(-0.02, 1.08)
ax.set_xlabel("spreading rate  (0 = frozen; light speed = 1.008 here)")
ax.set_ylabel("cone fill  (low = gliders; 1 = solid cone OR single cell)")
ax.set_title("Range-2 damage-signature landscape (stars: embedded ECAs)")
ax.legend(fontsize=7, loc="upper right", framealpha=0.9)
fig.tight_layout()
fig.savefig(FIG / "landscape.pdf")
plt.close(fig)
print("wrote landscape.pdf")
