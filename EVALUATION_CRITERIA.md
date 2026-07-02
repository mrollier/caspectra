# EVALUATION_CRITERIA.md — pre-registered success/failure criteria (v2)

Fixed **before** any v2 run (2026-07-01), so that success is not defined after
seeing the results (SELF_CRITICISM: "no pre-registered success criterion").
Changing these thresholds after a run requires saying so explicitly wherever the
run is reported.

## Revision 2 (2026-07-02) — changelog

Revised after the foundations literature review (`FOUNDATIONS.md`,
`docs/literature/2026-07-02_deep_research_report.md`), **before any v2 training
run**, so no run outcome motivated these changes:

1. The classified object is now explicit: the **protocol tuple** *(orbit,
   Bernoulli(1/2) IC measure, ring 127, horizon 127)* — not "the rule"
   (undecidability, measure-dependence; FOUNDATIONS.md §1).
2. Criterion 1: Wolfram agreement demoted from ground truth to **reference
   touchstone**; class-IV reference set fixed at **{54, 110}**; borderline rules
   **40, 41, 42, 106** flagged in `rule_labels.csv`, and class-IV recall is
   reported **both with and without rule 106 in the chaotic pool**.
3. Criterion 3 reinterpreted: the physics baseline is now also the **auxiliary
   training target** (Lever A), so the comparison becomes "match the direct
   invariant out-of-sample and add spatial resolution", not "beat it".
4. **New criterion 5 (protocol stability)** and **new criterion 6 (amortization
   transfer)** added; both pre-registered before being measured on any learned
   model.
5. Lever change: temporal-window positives dropped as a standalone lever
   (instance discrimination — same shortcut incentives as v1); levers are now
   A = invariant-regression amortizer (primary), B = predictive SSL
   (FOUNDATIONS.md §4, incl. kill criteria).

## Why the criterion moved (decision record)

v1 (`runs/default/`) showed that **rule identifiability is not the right pass/fail
bar**: every ECA rule produces a statistically distinctive texture, so any
expressive encoder identifies rules from mesoscopic statistics alone — no
rule-table ("T-tetromino") reading required — and instance-discrimination SSL
actively rewards per-diagram (hence per-rule) distinctiveness. The v1 rule probe
hit 0.967 *through* an anti-cheat architecture; the supervised paper only reached
rule ≈ 61% because label pressure pushed the other way. Demanding "rule probe well
below 100%" of an unsupervised embedding is therefore likely unachievable and,
more importantly, mis-aimed: v1's real failure was that **behavioural structure was
present but not salient** — density dominated the geometry (PC1 ≈ density), and
clustering followed it.

**Success is therefore defined at the geometry/cluster level** (what the
unsupervised pipeline makes salient), not at the embedding-decodability level.
The rule probe stays prominently reported as a diagnostic.

## The classified object (rev 2)

Every criterion below is a statement about the **protocol tuple**

> *(rule orbit under reflection/complement, Bernoulli(1/2) IC measure, ring of
> 127 cells with periodic boundaries, horizon of 127 rows from t = 0)*

— not about "the rule" in the abstract. The literature (Gilman; Culik–Yu; see
FOUNDATIONS.md §1) shows the observed class can change with the IC measure,
lattice, and horizon; criterion 5 measures that sensitivity instead of assuming
it away.

## Reference labels

- `rule_labels.csv` (provenance: `rule_labels_PROVENANCE.md`; user spot-check pending).
- **Class-IV metrics use the `wolfram_class` column (4 = {54, 110})** — under
  Li–Packard, complex rules are folded into "chaotic", so LP cannot score class IV.
- Wolfram/LP agreement is a **reference touchstone, not ground truth** (rev 2):
  formalized class membership is undecidable and borderline rules are unstable
  across published schemes. The `borderline` column flags **40, 41, 42, 106**
  (published chaotic substructure for 40/42; intermediate damage signatures for
  41/106 — see provenance file).
- Genotype = the **orbit** (equivalence-class representative), as in v1.

## Primary criteria (pass/fail, per run)

1. **Behavioural salience of clusters.** Per-Wolfram-class cluster recall — the
   fraction of a class's diagrams that land in clusters where that class is the
   majority. Success: recall ≥ 0.5 for **each** of the four Wolfram classes,
   including class IV. Failure: class-IV recall < 0.2 after the M3 levers.
   **Criteria 1 and 2 are one joint criterion**: rule-pure clusters are trivially
   class-pure, so a one-cluster-per-rule solution scores recall 1.0 while
   failing criterion 2 (measured on v1: recall ≈ 1.0 everywhere with excess
   genotype fraction 0.81). Neither number means anything alone.
   *(Rev 2)* Class-IV recall is reported **twice**: with rule 106 counted as
   chaotic (published labelling) and with 106 excluded from the chaotic pool
   (our damage-space borderline). Borderline rules (40, 41, 42, 106) are
   flagged in all per-class tables; a pass/fail that flips depending on
   borderline placement is reported as **ambiguous**, not as a pass.
2. **No excess genotype information in clusters.**
   `MI(cluster; orbit | wolfram_class) / H(orbit | wolfram_class)` — the fraction
   of within-class rule information the clustering resolves. Success ≤ 0.25;
   failure ≥ 0.5. (v1: clusters ≈ orbits, so this is ≈ 1 by construction; measure
   to confirm.)
3. **Beat the physics baseline where it counts.** Class-IV recall of the
   SSL-embedding clustering ≥ that of clustering on the damage-spreading /
   dynamics features alone (`caspectra/eval/dynamics.py`, M2.3). If the cheap
   physics baseline wins, the honest headline is "texture SSL does not detect
   computation beyond label-free dynamical statistics" — reportable, not tunable
   away.
   *(Rev 2 — measured outcome + reinterpretation.)* This gate was measured on
   2026-07-01: the physics baseline won, 1.00 vs 0.00 (`RESULTS.md`). The
   dynamics features consequently become the **auxiliary training target** of
   Lever A, so for learned models this criterion now reads: the amortized
   estimate must *match the direct invariant out-of-sample* (criterion 6) and
   *add what the scalar invariant cannot* (spatial resolution / per-patch maps)
   — not "beat" its own supervision signal.
4. **Stability.** The macro-structure must survive clustering hyperparameters:
   ARI ≥ 0.6 between cluster assignments across the `min_cluster_size` sweep and
   across 3 UMAP seeds. A class-IV island that appears at one seed only does not
   count.
5. **Protocol stability (rev 2).** Any claimed taxonomy must be stable across
   the observation protocol: over IC densities p ∈ {0.25, 0.5, 0.75} (width
   127), each dynamics feature keeps Spearman ρ ≥ 0.8 against the p = 0.5
   reference, and cluster assignments (agglomerative, k = 14, standardized
   features) keep ARI ≥ 0.6 against the reference. Rules that flip cluster
   membership across protocols are listed explicitly wherever the taxonomy is
   reported (density-dependent behaviour, e.g. rule 184, is a *finding* about
   the protocol tuple, never hidden). Measured by
   `scripts/protocol_sensitivity.py`; extreme densities (0.1, 0.9) and other
   widths are reported as context, not gated.
   *Measurement spec + first outcome (2026-07-02, documented — not a threshold
   change):* the gate must be measured with **n_pairs ≥ 128** and read against
   a same-protocol **seed control** — at n_pairs = 32 the sampling floor alone
   is ARI ≈ 0.4, which would conflate noise with protocol dependence. First
   measurement (n_pairs = 128, seed control ARI = 0.70): the feature-ρ half
   **passes** (ρ ≥ 0.90 at gated densities); the ARI half **fails** (0.33 at
   p = 0.25, 0.37 at p = 0.75) — the *fine hard partition* is genuinely
   IC-measure-dependent, while width barely matters (w = 255: ARI 0.78, no
   class flips), class-level flips at gated densities are single rules (106,
   168), and the {54, 110} co-membership holds across the whole gated range
   (`RESULTS.md`). Consequence: v2 taxonomy claims must be made at the level of
   protocol-robust structures (invariant feature space, coarse/class-level
   groups, specific co-memberships), never as a fine partition of rule space.
6. **Amortization transfer (rev 2; gates Lever A).** A learned encoder must
   predict the dynamics feature vector from a **single diagram** with
   leave-rules-out validation: success = median held-out-rule R² ≥ 0.5 per
   feature; failure = R² < 0.2. This is pre-registered now, before any Lever-A
   model exists. Passing it is what earns the learning component its place;
   the payoff claim (per-patch phenotype maps for nuCA) is only credible if
   this holds.

## Reported diagnostics (not gated)

- Rule(orbit)-identity probe accuracy/balanced accuracy + the LP/Wolfram probe
  **gap** (kept for continuity with the supervised paper; no longer pass/fail).
- Collapse: `embedding_std`, plus **effective rank / participation ratio** of the
  embedding covariance (v1: std ≈ 0.018 vs ≈ 0.125 isotropic — heavy anisotropy).
- **Invert-invariance check:** R²(embedding → raw density) vs R²(embedding →
  folded density `min(d, 1−d)`). If raw density is decodable well beyond folded,
  the invert augmentation did not produce the intended invariance (training bug
  signal, since only the 88 min-representatives are simulated).
- Hand-crafted feature baseline comparison (`eval/baselines.py`), per class.

## Explicit failure conditions

- Any run where the collapse diagnostics fire (embedding_std → 0 or effective
  rank ≈ 1) is void regardless of other numbers.
- *(Rev 2 — kill criteria, FOUNDATIONS.md §4.)* If Lever A (invariant-regression
  amortizer) fails criterion 6 **and** Lever B (predictive SSL) separates
  {54, 110} (106 reported both ways) no better than the direct damage features,
  the learning component concludes as a negative result — "SSL adds nothing over
  direct invariants on ECAs" — and effort moves to the larger rule space (M4).
  No further texture-SSL (instance-discrimination) tuning runs on 88 ECAs under
  any outcome: that question was answered on 2026-07-01 (`RESULTS.md`).
