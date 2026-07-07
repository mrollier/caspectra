# Research directions from the 2026-07-07 read-through

Derived from `docs/literature/readthrough_2026-07-07_NOTES.md` §3 (seven numbered
links/ideas) and the analysis wishlist in `docs/literature/WISHLIST.md`. Ranked by
manuscript leverage per unit cost, with risk noted. Directions never touch registered
criteria, thresholds, or verdicts (`EVALUATION_CRITERIA.md` rev. 2); anything that
reaches the manuscript is explicitly post-hoc.

---

## 1. Ranked directions

### D1 — Annealed Derrida–Pomeau zero-budget oracle member  **(chosen, executed)**

**What.** Compute the four damage-response targets analytically from a rule table —
no twin simulation — via the per-table annealed damage map
ĝ(y) = Σ_{S≠0} y^|S| (1−y)^(n−|S|) d_S (Derrida & Pomeau 1986 Eqs. 9/15 applied to a
specific table), with d_S the exact Bernoulli(1/2) disagreement probability for flip-mask
S and n = 2r+1. Slope ĝ′(0) = (2r+1)·s̄ (s̄ = mean Boolean derivative = Vispoel's s);
the identity chain ĝ′(0) > 1 ⇔ Bagnoli mean-field λ = log((2r+1)μ) > 0 ⇔ Derrida–Pomeau
instability ties three literatures to one criterion. Estimators: Galton–Watson
finite-horizon extinction → `damage_survival`; fixed point y* → `cone_fill`;
branching-random-walk front speeds → `spreading_rate`; y* × cone coverage →
`damage_fraction`. Two variants: `annealed_true` (ground-truth table; diagnostic
ceiling) and `annealed` (table reconstructed from ONE diagram — the actual pipeline
member).

**Why it wins.** Fully spec'd (notes §3.1); ~zero compute; the manuscript already
reserves the slot (main.tex ~l.154–155 names a "lattice-independent mean-field
iteration" tier; the accuracy-vs-budget discussion ~l.836–846 lacks a zero-budget
anchor); either outcome is manuscript-worthy — success adds the missing anchor, failure
shows Monte-Carlo twins are genuinely necessary, which supports the budget argument.

**Risk.** Mean-field ignores spatial correlation and defect annihilation — see the
pre-declaration in §2 below.

### D2 — Output-only noise axis in the identifiability frontier  *(runner-up; tracked, not scheduled)*

Sun et al. 2011 achieve exact rule recovery at 40–45% flip noise because their flips
corrupt *outputs only* (inputs stay exact — entrywise likelihood exactly right), while
our diagram-level noise mis-bins inputs and collapses tabulation at ~5% (notes idea 4).
Adding a Sun-style output-only degradation axis to `scripts/build_frontier_grid.py`
would let the manuscript *show* the regime split instead of arguing it. Moderate cost
(frontier grid re-run), strong rebuttal value if a referee cites Sun's tolerance
against ours.

### D3 — Genotype-side covariates for the r=2 panel  *(partially free via D1)*

Wishlist item 2. s̄ (Vispoel's s, table-side µ-sensitivity) now comes free as
ĝ′(0)/(2r+1) from D1's code; correlating amortizer error with s̄ is a one-liner once D1
lands. Vispoel's β and the II↔III triple-point comparison stay deferred (their
localization is for k ≥ 3 totalistic spaces). λ stays **out** of the covariate set —
Langton's own caveat (p.15: poor discrimination at small K, N) plus polarity/orbit
inconsistency (notes idea 2).

### D4 — Rebuttal receipts  *(done; no analysis needed)*

Already documented in the notes: exercise-dependence prior art (Y&B's Rule-184
(111)-elimination anecdote, idea 3), the noise-model taxonomy (idea 4), and the
model-selection genealogy Richards MI−2^m/N → BIC → our ε self-consistency (idea 7).
Kept as referee-response material; Appendix D's novelty claim (we *measure* the
consequence) is unaffected.

### D5 — Gilman-§5 finite-observation stability formalization  *(future work)*

Gilman's per-class change-propagation probabilities and finite-observation frequency
test (1987) are the measure-theoretic ancestors of criterion-5-style stability gates
(notes idea 6). A formal bridge would be a separate methods paper, not a revision of
this one.

**Standing warning (notes idea 5).** Bagnoli's noiseless marginal group (λ ≥ 0 for some
class-2 rules whose damage never spreads, because replica counting ignores defect
annihilation) means MLE-sign and damage-survival can disagree. The manuscript's
"proxy" hedge stays as is; D1's results must be read with the same caution.

---

## 2. D1 pre-declared expectations  (written 2026-07-07, BEFORE any evaluation run)

Recorded before the first panel evaluation so that hindsight cannot quietly move the
goalposts. Evaluation: R² per target (`r2_per_feature`) against the same
n_pairs = 256 Monte-Carlo reference all other estimators use, on both panels
(88 ECA equivalence-class representatives, r = 1; 800 sampled rules, r = 2).

**Expected strengths.**
- `damage_survival` and `spreading_rate` for clearly spreading / chaotic rules: the
  branching approximation is exact at low defect density and short times, and the
  Bernoulli(1/2) IC matches the protocol measure at t = 0.
- The r = 2 panel should behave *better* than ECA: larger neighbourhoods are closer to
  the mean-field regime (Derrida–Pomeau's approximation improves with K; their K = 3
  fixed point already matched quenched simulation).

**Expected failures (pre-declared, to be reported not hidden).**
1. **Marginal / conserved rules** (Bagnoli's λ ≈ 0 group: identity- and traffic-like,
   e.g. 204, 184): mean-field has no notion of frozen or ballistically confined damage.
   Known concrete miss: a frozen single defect gives MC `cone_fill` = 1 while the
   marginal-guarded mean-field gives 0.
2. **Near-critical rules**: Derrida–Pomeau's own marginal K = 2 case underestimates
   damage (0 vs 0.113) — quenched spatial correlations matter exactly at criticality;
   directed-percolation lore (Grassberger 1995) says mean-field exponents are wrong
   there too.
3. **`cone_fill` for glider/complex rules**: sparse cones violate the well-mixed-density
   assumption; expect systematic overestimation.
4. **Invariant-measure drift**: d_S is computed under Bernoulli(1/2), but after a few
   steps the twin diagrams live on the rule's own invariant measure. Rules whose
   invariant density is far from 1/2 should show bias at the horizon (127-step targets).
5. **Reconstruction gap**: the `annealed` variant inherits tabulation's
   exercise-dependence — low-coverage rules (ordered diagrams) get completion-policy
   tables; expect `annealed` ≤ `annealed_true` with the gap concentrated on low-coverage
   rules.

**Pre-committed decision rule for manuscript integration.**
(a) If the member is a useful zero-budget anchor — median R² materially above a
predict-panel-mean baseline and a meaningful fraction of the 16-pair Monte-Carlo
member — integrate it as the zero-budget point of the budget-indexed family.
(b) If it fails broadly, integrate one–two honest sentences: the mean-field tier does
not transfer to protocol-tuple damage-response statistics; Monte-Carlo twins remain
necessary (this *supports* the manuscript's budget argument).
(c) Mixed outcomes: per-target reporting, all four targets always shown, no
cherry-picking. In every case the addition is presented as post-hoc.

---

## 3. Literature worth adding to `docs/literature/`  (for re-reading)

Ordered by usefulness; bibliographic details to be verified on retrieval. Mirrored in
`WISHLIST.md`.

| # | Reference | Why |
|---|-----------|-----|
| 1 | **Adamatzky 1994**, *Identification of Cellular Automata* (Taylor & Francis) | Still #1: completes the citation audit; sole anchor of the manuscript's "probabilistic move" cite (l.661) |
| 2 | **Derrida & Weisbuch 1986**, J. Physique 47:1297 | Overlap-evolution formalism — the refined annealed distance-map lineage directly behind D1 |
| 3 | **Kauffman 1969**, J. Theor. Biol. 22:437 | The quenched original the annealed treatment approximates; cited directly at main.tex l.108 but **never read** — the same secondhand-attribution risk the read-through cleaned up elsewhere |
| 4 | **Domany & Kinzel 1984**, PRL 53:311 | Canonical stochastic-CA / directed-percolation model anchoring Bagnoli's DP mapping |
| 5 | **Grassberger 1995**, J. Stat. Phys. 79:13 | Damage-spreading transitions and DP universality — the pre-declared critical-regime failure discussion for D1 |
| 6 | **Zhao & Billings FCA-OLS line** (Sun 2011 refs [19], [21], [22]) | The actual OLS identification papers, now that the Y&B Appendix-D row was corrected |
| 7 | *(optional)* **Bagnoli & Rechtman 1999**, PRE 59:R1307 | Synchronization ↔ MLE connection; sharpens the survival-proxy caveat |
| 8 | *(optional)* **Martins et al. 1991**, PRL 66:1018 | Damage-spreading phases in spin systems; framing only |

---

## 4. Execution record (D1) — run 2026-07-07, after freezing §2

Code: `caspectra/eval/annealed.py` + `tests/test_annealed.py` (15 tests, all analytic
anchors pass; rule 90's rate matches the MC target to 5 decimals, so the negative
result below is physics, not implementation). Runs:
`runs/analysis/annealed_member/{default,m4_range2}/` (127px, targets = cached
256-pair reference; `annealed` latency ≈ 2–3 ms/diagram, dominated by table
reconstruction — the analytic part is microseconds).

**Outcome: decision-rule branch (b) — broad failure, reported as such.**

| Panel | annealed median R² (per-target) | mech@16 median R² | survival-sign agreement | majority base rate |
|---|---|---|---|---|
| 88 ECA (r=1) | **−2.10** (surv 0.06, frac −2.30, rate −2.37, fill −1.89) | 0.987 | 0.795 | 0.841 |
| 800 r=2 | **−2.27** (surv −0.09, frac −4.12, rate −4.76, fill −0.41) | 0.873 | 0.980 | 0.980 |

Both halves of the negative result matter:

1. **Quantitative failure (pre-declared, mechanisms confirmed).** On the both-alive
   subset the biases are systematic: spreading rate +0.44 mean bias (BRW front speeds
   ignore quenched correlations — rule 30's left front: mean-field 0.72 vs true ≈0.24);
   cone_fill −0.38 on ECA (additive rules: the difference pattern IS the deterministic
   Sierpinski gasket, density 0.27, which no mixing argument can produce); frozen/
   marginal rules maximally anti-predicted (MC fill 1 vs mean-field 0). Expectation
   §2.1–3 confirmed.
2. **Qualitative failure (NOT pre-declared — stronger than expected).** The survival
   criterion ĝ′(0) > 1 (≡ Bagnoli mean-field λ > 0 ≡ Vispoel-s instability) does not
   beat the majority-class base rate on either panel: on r=2 it predicts "survives"
   for all 800 rules (TN = 0, FP = 16); on ECA it scores *below* always-survive
   (balanced accuracy ≈ 0.68; GW predicts survival 0.95 for rules whose damage
   actually dies by annihilation — Bagnoli's own replica-counting caveat operating
   at full strength). The §2 expectation that r=2 would behave *better* was wrong:
   the sampled-r=2 panel is survival-saturated, so the criterion has nothing to add.

Consequence for the manuscript (branch `annealed-oracle`): the budget-indexed family
gets its zero-budget anchor as a **negative** point — the analytic tier promised at
the cost-hierarchy level does not transfer to protocol-tuple damage-response
statistics, so the family's accuracy floor starts at the smallest Monte-Carlo member;
this *supports* the budget argument rather than undercutting it. Nuance kept: this
does not contradict Vispoel 2026's mean-field class prediction (k ≥ 3 totalistic,
asymptotic classes, different measure) — it shows their tier does not transfer to
*this* protocol tuple and *these* observables, which is the manuscript's
protocol-dependence thesis in action.
