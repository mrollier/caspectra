#!/usr/bin/env python3
"""Rev-14 re-expression: finite-replicate variability of the rho reference values.

The rho reference values (sqrt(2) simulation-limited, 1 latent; Eq. (2) of the
manuscript) are exact in expectation under the additive-noise idealization, but
the pooled denominator sum_i sigma_e^2(i) is estimated from K replicates per
rule, so the observed rho is a ratio of random quantities. This script
quantifies, by the delta method under a Gaussian working model, the relative
standard deviation the two noise sources contribute to the pooled reference
for an exactly identified rule resimulated at matched budget:

  numerator (finite panel):  e_i ~ (0, 2 sigma_i^2)  => Var(e_i^2) = 8 sigma_i^4
  denominator (finite K):    Var(sigma_hat_i^2) = 2 sigma_i^4 / (K - 1)

  Var(rho)/rho^2 ~= (1/4) [2 + 2/(K-1)] * sum sigma^4 / (sum sigma^2)^2

The numerator share is already carried empirically by the manuscript's
rule-bootstrap CIs; the denominator share is the part the fifth review asked
to be priced. Rules with sigma_e = 0 drop out of both sums (as in Eq. (2)).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]

SPACES = {
    "radius2": REPO / "runs/m4_range2/reliability_heldout/per_rule_sigma_e.npz",
    "eca": REPO / "runs/lever_a_local/reliability_heldout/per_rule_sigma_e.npz",
}


def rel_sd(sigma2: np.ndarray, k: int) -> tuple[float, float, float]:
    """(total, numerator-only, denominator-only) relative SD of rho at sqrt(2)."""
    sigma2 = sigma2[sigma2 > 0]
    shape = float((sigma2**2).sum() / sigma2.sum() ** 2)  # sum s^4 / (sum s^2)^2
    var_num = 2.0 * shape          # Var(N)/E[N]^2 with E[e^2] = 2 s^2
    var_den = (2.0 / (k - 1)) * shape
    tot = 0.5 * float(np.sqrt(var_num + var_den))          # SD(rho)/rho = SD(R)/(2R)
    return tot, 0.5 * float(np.sqrt(var_num)), 0.5 * float(np.sqrt(var_den))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--output", default=str(REPO / "runs/analysis/rho_variability/summary.json")
    )
    args = ap.parse_args()

    out: dict = {"k_replicates": {}, "per_space": {}}
    for space, path in SPACES.items():
        z = np.load(path)
        k = int(z["n_replicates"])
        out["k_replicates"][space] = k
        names = [str(n) for n in z["feature_names"]]
        block = {}
        for j, name in enumerate(names):
            tot, num, den = rel_sd(z["sigma_e"][:, j].astype(float) ** 2, k)
            block[name] = {
                "rel_sd_total": round(tot, 4),
                "rel_sd_numerator_only": round(num, 4),
                "rel_sd_denominator_only": round(den, 4),
                "sd_of_rho_at_sqrt2": round(tot * np.sqrt(2), 4),
                "denominator_sd_of_rho_at_sqrt2": round(den * np.sqrt(2), 4),
            }
        out["per_space"][space] = block

    worst_den = max(
        b[t]["denominator_sd_of_rho_at_sqrt2"]
        for b in out["per_space"].values()
        for t in b
    )
    worst_tot = max(
        b[t]["sd_of_rho_at_sqrt2"] for b in out["per_space"].values() for t in b
    )
    out["worst_case_denominator_sd_of_rho"] = worst_den
    out["worst_case_total_sd_of_rho"] = worst_tot

    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps(out, indent=1, sort_keys=True))
    print(f"\nwrote {dest}")


if __name__ == "__main__":
    main()
