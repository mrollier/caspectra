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
for name, (r, f) in anchors.items():
    ax.scatter([r], [f], marker="*", s=150, c="gold", edgecolor="k", zorder=5)
    ax.annotate(name, (r, f), textcoords="offset points", xytext=(4, 3), fontsize=8)
ax.set_xlabel("spreading rate  (0 = frozen, 1 = light speed)")
ax.set_ylabel("cone fill  (low = gliders, high = solid)")
ax.set_title("Range-2 damage-signature landscape (stars: embedded ECAs)")
ax.legend(fontsize=8, loc="upper right")
fig.tight_layout()
fig.savefig(FIG / "landscape.pdf")
plt.close(fig)
print("wrote landscape.pdf")
