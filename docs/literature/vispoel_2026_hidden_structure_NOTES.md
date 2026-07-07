# Vispoel, Daly & Baetens (2026) — "Unveiling hidden structures" — 3W scan and project impact

**Produced 2026-07-07 with the ARS deep-research `three-way-scan` mode** (WHY/HOW/WHAT per
source + cross-source synthesis), comparing the new paper against this repo's Chaos
manuscript and the project frame in `FOUNDATIONS.md`. Source PDF:
`docs/literature/vispoel-hidden_structure.pdf`. Page anchors below refer to the journal
pagination (Physica D 496 (2026) 135306, pp. 1–12; received 27 May 2026, accepted 19 June
2026, online 1 July 2026; DOI `10.1016/j.physd.2026.135306`).

**Provenance note:** all quotes were checked against text extracted from the PDF (pypdf).
The exact nearest-centroid prediction scores for the mean-field (s, β) plane are printed
*inside* the Fig. 12 panels and are not recoverable from the text layer; the prose
characterizes them only as "significantly higher" (p. 11) and "exceptionally high"
(pp. 11) — no numbers are asserted here beyond what the text states. Re-verify against the
figures before quoting scores anywhere citable.

---

## 1. Vispoel, Daly & Baetens 2026 (Physica D) — the new paper

**WHY.** CA rule spaces have "no inherent geometric or topological structure" (p. 1); the
classic parameterizations (Langton's λ, μ-sensitivity) were only ever assessed
*qualitatively*, and behaviour prediction from the rule table is undecidable in general.
The paper asks: "to what extent can the Wolfram class of a CA be predicted from its rule
table alone, without any simulation of its dynamics, and which parameterization of the
rule space best supports this?" (p. 2).

**HOW.** Frame rule-space structure as a supervised multiclass problem: compute a
two-parameter representation (p₁, p₂) per rule, fit a nearest-centroid classifier
(deliberately hyperparameter-free, "not an artefact of overfitting", p. 9) against manual
Wolfram labels, and read the test score as a measure of how well the parameter pair
clusters the classes. Three parameter tiers at increasing compute cost (§4.2, pp. 9–10):
rule-table (λ, μ — constant cost), **mean-field (s, β — ≈500 iterations of the mean-field
map, "independent of the lattice size or number of time steps", p. 10)**, and
phenomenological (H̄, Ī — "roughly 20 million local updates per rule", p. 10). Three rule
spaces: ECA (256), r=2 k=2 totalistic (64), r=1 k=3 totalistic (2187), each **manually
Wolfram-classified in full** from multiple random ICs over 500 time steps (p. 9), under a
modified convention: "We will classify constant inhomogeneous behavior as Class I" (p. 3).
The new parameters come from mean-field theory: each rule table maps to a density map
f: ρ(t)→ρ(t+1) (Eq. 15) — a logistic-map analogue — from which they take the average slope
s = f(1) − f(0) (degree of (inverse-)linearity, Eq. 23) and the non-linearity β, the
maximum bulge of the curve above the chord (Eq. 24).

**WHAT.** (i) λ + μ are quantitatively poor: "even here only 39% of the rules are assigned
to the correct Wolfram class" (best space, p. 9), because "λ and μ are correlated and
provide largely the same information" (p. 10) — μ is "a very poor choice for the 'mystery
parameter'" of Li–Packard–Langton. (ii) Phenomenological (H̄, Ī) parameters work well for
totalistic spaces but reach "a prediction score of just 54%" on ECA (p. 10), depressed by
identity-rule variants whose high entropy "is due to the randomness that is present in the
initial configuration, not the randomness introduced by applying the local update rule"
(p. 11). (iii) The mean-field pair (s, β) yields scores "exceptionally high considering the
mean-field parameters are derived from the rule table while the Wolfram classes they
predict are based on the space-time patterns" (p. 11). (iv) Class IV appears as a
second-order phase-transition region between Classes II and III for binary CA, and "near
the triple point of Class I, II and III" for the k=3 space — proposed as the closest thing
to "a universal rule space structure" (p. 11). (v) Data (the manual classifications)
"available on request" (p. 11); future work: unsupervised ML on rule-table properties.

## 2. This repo's Chaos manuscript (Rollier & Baetens, round-4 state)

**WHY.** Learned models increasingly read dynamical properties off a single observation;
because a clean spacetime diagram contains the rule table in its local neighbourhoods, the
fair baseline for any such amortized estimator is the transparent route: *read the rule,
re-run the defining experiment* (`manuscript/main.tex`, Introduction).

**HOW.** Pre-registered benchmark over 88 ECA orbits + 800 sampled radius-two rules;
targets are finite-horizon damage-response statistics of the protocol tuple; the
mechanistic estimator (tabulate transitions → simulate) is compared against two direct
learned estimators under matched observation models, then pushed across an
identifiability frontier (masking, IC density, noise).

**WHAT.** Diagram→rule is essentially solved under matched assumptions (100% ECA, 97.5%
radius-two held-out); reconstruct-and-simulate attains the independent-replicate benchmark
by construction, yielding a **budget-indexed family** of estimators rather than a point;
direct estimators can win only on cost or on robustness beyond the frontier.

## 3. FOUNDATIONS.md — the project frame

**WHY.** "The behaviour class of rule R" is not well-defined (undecidability,
measure-dependence); the defensible object is the protocol tuple. **HOW.** Pre-registered
criteria at the geometry/cluster level; invariant-based taxonomy + amortized invariant
estimation; texture-SSL frozen as negative baseline. **WHAT.** Class-IV metrics scored on
`wolfram_class` with reference {54, 110} and dual-reported borderline flags {40, 41, 42,
106}; λ/edge-of-chaos explicitly listed as *contested*.

---

## 4. Cross-source synthesis

**Common WHY.** All three reject "the class of a rule" as a primitive and treat
behaviour prediction as an *operationalized, protocol-dependent* measurement — Vispoel
2026 is explicit that Wolfram's classification is observational, IC-measure-biased, and
undecidable in every formalization (§2.2, p. 3), matching FOUNDATIONS §1 and the
manuscript's protocol-tuple framing.

**Divergent HOW.** The arrows point in opposite directions. Vispoel 2026 predicts
*class from the genotype* (rule table → parameters → class, no simulation); the manuscript
predicts *phenotype statistics from an observation* (diagram → rule → simulate, or diagram
→ direct estimator). Vispoel's supervision comes from manual visual classification; the
repo's from simulator-defined damage statistics precisely to avoid scheme-dependent labels.
Vispoel handles the identity-rule confound by restricting to legal (left-right-symmetric)
rules (Fig. 11, p. 11); this repo folds the full reflection+complementation orbit instead —
a strictly stronger symmetry treatment that keeps all 88 orbits in play.

**Strongest WHAT.** The compute-tier result. Vispoel §4.2 independently arrives at the
manuscript's round-4 organizing idea — prediction accuracy must be indexed by simulation
budget — with a genuinely intermediate tier (mean-field, lattice-independent, ~500 map
iterations) between "free" and "full simulation". **Composition argument:** the manuscript
shows diagram→rule is solved under matched assumptions; Vispoel 2026 shows rule→class is
cheap and accurate given the rule. Composed: once the rule is read off a clean diagram,
class-level behaviour prediction costs essentially nothing. This sharpens two standing
claims: (a) "when the observation encodes the generator, identification is the baseline to
beat" now extends beyond damage statistics to class prediction; (b) the genotype-cheat
path (FOUNDATIONS §2; v1's 0.967 rule probe) is short and now *quantified* — an encoder
that latches onto the rule gets the class nearly for free through two scalar functionals
of the table, so MI(cluster; orbit | class) ≈ 0 remains the right gate.

**Unresolved gap.** (i) Their manual ECA classification vs this repo's labels: does their
Class IV equal {54, 110}, and where do the borderline rules 40/41/42/106 land — especially
under their constant-inhomogeneous→Class I convention, which moves rules like the identity
family relative to both the Wolfram and Li–Packard columns? Unanswerable until the data
arrives (requested; see DECISIONS 2026-07-07). (ii) Their triple-point localization of
Class IV (k≥3) has not been checked against the M4 radius-two complex-regime placement
(criterion 9) — note their k≥3 claim is for *totalistic* spaces, whereas M4's space is
r=2 non-totalistic binary, where their binary result (Class IV on the II↔III boundary)
is the relevant one. (iii) Whether a mean-field/annealed estimate of *damage-response*
statistics (Derrida–Pomeau) can join the oracle family as a ~zero-budget member is an open
wishlist item (`docs/literature/WISHLIST.md`).

## 5. Consequences adopted in this repo (2026-07-07)

1. **FOUNDATIONS.md**: (s, β) added to Established; λ bullet strengthened with the 39%
   quantitative result; reading-list item 11; Unknown-section annotation re: their full
   manual ECA table.
2. **Manuscript**: light-touch citation (`vispoel2026structure`) in the budget-indexed
   paragraph, on branch `vispoel2026-cite` (user gates merge).
3. **Labels**: data requested from the authors; on receipt, a `vispoel2026_class` column
   in `rule_labels.csv` for *additional* dual-reported class-IV robustness. **No
   pre-registered threshold, reference set, or borderline flag changes.**
4. **Wishlist**: annealed damage-spreading oracle member; (s, β) as genotype-side
   covariates for the radius-two panel.

**Caution for citation:** cite their *results*, not their undecidability framing — the
abstract's "predict the behavior of a CA based on its rule table, which is an undecidable
problem" (p. 1) is looser than the manuscript's careful statement that the obstruction
applies to the asymptotic formalization, not to finite protocols. Their own §2.2 is more
careful and consistent with ours.
