# Literature wishlist (user-supplied PDFs)

Papers we could not fetch open-access (2026-07-02). Drop the PDFs in this directory,
named `<firstauthor>_<year>_<slug>.pdf`. Ranked by usefulness to the project:

1. **Vispoel, Daly & Baetens (2024), _Damage spreading and the Lyapunov spectrum of
   cellular automata and Boolean networks_** — **top priority.** Defines the extended
   perturbation-invariant family (Lyapunov spectrum conventions) that Lever A's target
   set should grow into, and the conventions our `eval/dynamics.py` features should be
   checked against. *(Received: `vispoel_2024_damage_spreading.pdf`.)*
2. **Vispoel, Daly & Baetens (2022), _Progress, gaps and obstacles in the classification
   of cellular automata_** — the modern critical overview cited throughout
   FOUNDATIONS.md; useful as the canonical reference when writing up.
3. **Gilman (1987), _Classes of linear automata_** (Ergodic Theory Dynam. Systems 7) —
   the measure-dependence source; only needed if we formalize the protocol-tuple claims
   further.

Already in this directory: the commissioned deep-research report, Li–Packard 1990,
Culik & Yu 1988 (both open-access at complex-systems.com), Israeli & Goldenfeld 2006,
Kari 2005 survey, Wuensche 1999, Mitchell–Hraber–Crutchfield 1993, Hanson & Crutchfield
1997 (rule 54).

## Analysis wishlist (tracked, not scheduled)

Added 2026-07-07 after assessing Vispoel, Daly & Baetens 2026
(`vispoel-hidden_structure.pdf`; notes in `vispoel_2026_hidden_structure_NOTES.md`):

1. **Annealed / Derrida–Pomeau mean-field damage estimate as a ~zero-budget oracle-family
   member.** Compute the annealed damage-spreading approximation from the *reconstructed*
   rule table (no twin simulation) and place it on the manuscript's accuracy-vs-budget
   curve below the smallest Monte-Carlo member. `derridapomeau1986` is already in
   `manuscript/refs.bib`; Vispoel 2026 legitimizes the mean-field tier (lattice-independent,
   ~500 map iterations) for class prediction — the open question is how much of the
   *damage-response* statistics the annealed tier captures.
2. **(s, β) mean-field parameters as genotype-side covariates for the radius-two panel.**
   Both are instant to compute for the 800 sampled r=2 rules (Eqs. 23–24 of Vispoel 2026).
   Diagnostics, not features (genotype side): does amortizer error correlate with β; does
   the criterion-9 complex-regime placement sit near their binary-space II↔III boundary
   (their triple-point localization is for k ≥ 3 totalistic spaces, not r=2 binary)?
