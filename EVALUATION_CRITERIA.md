# EVALUATION_CRITERIA.md — pre-registered success/failure criteria (v2)

Fixed **before** any v2 run (2026-07-01), so that success is not defined after
seeing the results (SELF_CRITICISM: "no pre-registered success criterion").
Changing these thresholds after a run requires saying so explicitly wherever the
run is reported.

## Revision 14 (2026-08-20) — changelog

Added **before any round-7 review-response measurement**, numbers-free. The
fifth review (`manuscript/reviews/review_deepseekv4pro_20aug26.md`, verdict:
major revision) charges that (§3) the manuscript's central matched-regime CNN
numbers rest on the final-epoch protocol that rev 13 itself showed inferior to
validation-based checkpoint selection, and (§2) the ρ reference values are
stated as exact while the denominator is estimated from finitely many
replicates. Rev 14 registers the one run and the one re-expression answering
those charges. Purely additive; **zero changes to criteria 1–9 or to any
rev-2…14 threshold, margin, or verdict rule.** The decision rule below is
frozen before the run.

1. **M13 — validation-selected checkpoint for the matched-regime CNN
   (registered).** The canonical clean-trained direct CNN (five seeds on each
   of ECA and radius two; the estimator behind the manuscript's matched-regime
   tables) is retrained all-else-identical with the final-epoch weight
   selection replaced by the rev-13 M9 inner-fold rule: selection of the epoch
   minimising loss on a fixed fraction of training-rule diagrams
   (`--selection-frac`, the M9 value; selection fold drawn by the fixed
   selection seed; the held-out rule panel is never consulted). Final-epoch
   checkpoints are retained in each run directory so the registered numbers
   stay reproducible. This is a protocol change, not an epoch change: the
   selection fold removes a fixed fraction of training diagrams, exactly as in
   M9, and is disclosed as such. *Switch rule, frozen before training:* if on
   either space any per-target five-seed mean held-out R² under selection
   exceeds the final-epoch five-seed mean by more than 0.02, the selection
   protocol becomes the CNN of record in the matched-regime tables and the
   final-epoch numbers move to a sensitivity note; otherwise the final-epoch
   numbers stand and the selection result is reported as a sensitivity.
   Both protocols are reported either way. *Downstream scope if the switch
   triggers:* every consumer of the canonical checkpoint is rescored
   (ρ column, paired comparisons, stacking, retrieval bottleneck variant,
   identity/table-bit probes) — rescoring and refits only, no further
   training. The frontier's frozen-CNN curves remain the final-epoch artifact
   in either outcome (the frontier carries its own M9 selected-checkpoint
   control), and the manuscript states that scoping.

2. **Finite-replicate variability of the ρ reference values (post-hoc
   confirmatory; rule fixed here, computed from released artifacts).** The
   ρ reference values (√2 simulation-limited, 1 latent) are exact in
   expectation under the additive-noise idealization; the pooled denominator
   is estimated from K replicates per rule and is therefore itself a random
   quantity. The re-expression quantifies the implied spread of the pooled
   reference — by the delta method over the per-rule σ̂ₑ variances, and, if
   computed, by resampling regenerated replicates — and the manuscript's
   wording is downgraded from “exact” to expectation-level exactness wherever
   the claim appears, with the measured spread quoted. Reported whatever the
   magnitude shows: a negligible spread justifies the reference lines as
   drawn; a non-negligible one is disclosed next to every ρ table.

## Revision 13 (2026-08-20) — changelog

Added **before any round-5 review-response measurement**, numbers-free. The
fourth review (`manuscript/reviews/review_opus5_20aug26.md`, verdict: major
revision) accepts the three-benchmark distinction, the retired anti-shortcut
claim and the deployment-versus-diagnostic result, but charges that (§3.1) the
matched-regime verdict is an exchangeability identity presented as an
empirical test, (§3.15/§3.17) the frontier's fairness controls rest on a
training protocol that selects final-epoch weights and on a split that
force-holds every signature-complex rule, (§3.9) the cross-space prevalence
comparison is horizon-confounded, and (§5.3) no retrieval baseline separates
"recognises a training rule" from generalisation. Rev 13 registers the four
measurements answering those charges, plus the reporting rules for the
zero-simulation re-analyses. Purely additive; **zero changes to criteria 1–9
or to any rev-2…12 threshold, margin, or verdict rule.** All four decision
rules below are frozen before the corresponding runs.

1. **M9 — validation-based checkpoint selection for the degradation-trained
   control (registered).** The rev-10 degradation-augmented CNN is retrained
   under seeds 0/1/2, all else identical, with the final-epoch weight
   selection replaced by **selection of the epoch minimising validation loss
   on the training-split validation fold** (fold fixed by the existing split
   seed; held-out rules never consulted). Final-epoch weights are retained in
   each run directory so the rev-10/rev-11 numbers stay reproducible. The
   noise axis is then rescored on **both** the canonical and complement
   80-rule panels at the rev-9 budgets. *Stability rule (unchanged in form
   from rev 11):* the control is declared **seed-stable under selection** iff
   every seed's band-cell median R² lies inside the seed-0 rule-bootstrap CI
   at every noise cell in 3–15%. Reporting rule, binding regardless of
   outcome: the per-seed band range is reported as a range, the seed-stable
   family-level ordering is reported separately from the level, and the
   manuscript's practitioner-guidance caveat about run-to-run variance is
   **rewritten to whatever the selected-checkpoint spread supports** —
   widened, narrowed, or removed. A collapse of the spread is as reportable
   as its persistence.

2. **M10 — stratified-split direct CNN without force-holding (registered).**
   The radius-two CNN is retrained (3 seeds) on a leave-rules-out split that
   **does not** force-hold the 57 signature-complex rules, stratified instead
   so the training and held-out distributions match the sampling universe, and
   evaluated on its own random held-out panel. Purpose: separate the
   held-out-rule question from the covariate-shift question, since under the
   registered split the training set contains no signature-complex rules at
   all. *Decision rule:* the manuscript's family-gap claim (mechanistic over
   the direct estimators) is reported **at the stratified split** as well as
   the enriched one; if the stratified-split gap is smaller than the
   post-stratified gap by more than the registered superiority margin (0.10
   median R²) on any target, the family-gap claim is downgraded to the
   stratified number. Reported regardless of direction, including the
   possibility — visible in the rev-11 decomposition — that the enrichment
   was not a handicap.

3. **M11 — retrieval (nearest-neighbour) baseline (registered).** A
   train-set-lookup estimator: standardise the five statistics on training
   rules, find each held-out diagram's nearest **training** rule, and return
   that rule's cached target vector. A second variant uses the trained CNN's
   64-d bottleneck as the metric space. No training, no simulation.
   *Reporting rule:* per-target and median held-out R² and ρ on both spaces,
   next to the five-statistic and CNN columns. *Interpretation rule, fixed
   here:* a retrieval score close to the CNN's is evidence that the direct
   network's accuracy is substantially rule-recognition rather than
   generalisation to unseen tables; a retrieval score well below it is
   evidence against that reading. Both directions are reported.

4. **M12 — horizon-matched cross-space prevalence (registered).** The
   registered damage-signature criterion is re-evaluated on the 88 ECA orbits
   at the **radius-two horizon** (T as given by the radius-two protocol) so
   that the elementary and radius-two prevalences are compared at equal
   horizon. *Reporting rule:* the manuscript quotes the horizon-matched ECA
   prevalence alongside the existing one, and the cross-space comparison is
   either restated at matched horizon or withdrawn — the confounded form is
   not retained.

5. **Zero-simulation re-analyses (post-hoc confirmatory; rules fixed here,
   computed from already-released artifacts).** Each is a re-expression or
   decomposition of existing measurements, not a new measurement:
   (a) **ρ = RMSE/σ̂_e** reported as a secondary column, with ρ = √2 the
   simulation-limited benchmark and ρ = 1 the latent ceiling;
   (b) **per-panel** replicate-agreement and ICC recomputed inside each
   radius-two panel decomposition, replacing the panel-wide constants;
   (c) the **empirical scatter of cone fill against (w/2rT)·fraction/rate**,
   reported whatever it shows, with the pre-committed reading that R² > 0.95
   would make cone fill a derived coordinate requiring disclosure or removal;
   (d) **reduced-budget frontier ceilings** stated under the actual scoring
   convention (targets at the production budget, estimator simulation at the
   grid budget) and drawn on the frontier figures;
   (e) **survival-band stratified** R²/ρ restricted to rules with survival in
   [0.1, 0.9], plus mode-assignment accuracy, to separate resolution within
   the intermediate band from mode calling.

## Revision 12 (2026-07-07) — changelog

Purely additive; zero changes to criteria 1–9 or to any rev-2…11 threshold,
margin, or verdict rule. Registers one exploratory analysis arising from the
2026-07-07 literature read-through. Unlike rev 11, this entry is written
**after** the analysis ran; the pre-declaration that governs it (expected
strengths, expected failure modes, and the manuscript decision rule) was
frozen in `docs/research_directions_2026-07-07.md` §2 *before* the first
evaluation run, and that file is the reference of record.

1. **M8 — annealed (mean-field) zero-budget family member (exploratory,
   descriptive).** The Derrida–Pomeau annealed damage map applied to the
   *reconstructed* rule table (`caspectra/eval/annealed.py`;
   `scripts/eval_annealed_member.py`; `n_pairs = 0` entry in
   `scripts/benchmark_compute.py`) supplies the zero-simulation point of the
   budget-indexed estimator family. Reporting rule (per the frozen
   pre-declaration): all four targets on both panels, plus the survival-sign
   agreement against its majority base rate, reported regardless of
   direction; results enter the manuscript's accuracy-versus-compute
   subsection tagged [exploratory, rev.~12]. Outcome for the record:
   negative on both axes (median held-out R² −2.15 on the radius-two panel
   vs 0.92 for the 16-pair mechanistic member; survival criterion never
   exceeds the always-survives base rate). No registered quantity is
   affected.

## Revision 11 (2026-07-06) — changelog

Added **before any round-4 review-response measurement**, numbers-free. The
third review (`manuscript/reviews/paper_third_review.md`, verdict: major
revision) accepts the science as "plausible and potentially useful" but
demands (C1) a budget-indexed statement of the central dominance claim, (C2)
an explicit evaluation unit, (C3) decomposition of the enriched radius-two
panel, (C5) a paired equivalence analysis behind "statistically
indistinguishable", (C6/C8) seed and rule-panel stability of the frontier
guidance, and (C7) the deployment status of the stacking result. Rev 11
registers the seven analyses below. No change to criteria 1–9 or any
rev-2…10 threshold or verdict rule; the two M5 trainings are gated (63 px
smoke precedes each full run); all outcomes are reported regardless of
direction, with the manuscript wording downgrades pre-specified here.

1. **M1 — reference-scored direct estimators (post-hoc confirmatory).** Every
   estimator with cached held-out predictions (mechanistic, five-statistic
   ridge and boosted baselines, constrained CNN, and the rev-10 controls) is
   rescored against the existing large-simulation reference targets (the
   rev-8 C2.3 protocol: same rules, much larger `n_pairs`, decorrelated
   seed), alongside the cached-target scores, in one table per panel.
   Reporting rule (fixed here): a fresh-simulation estimator is expected to
   rise from the replicate-agreement benchmark toward ICC; a direct
   estimator rises only to the extent it estimates the latent mean. No
   pass/fail gate; both ceilings are printed next to both scores.
2. **M2 — paired equivalence for the "simulation-limited" claim (post-hoc
   confirmatory).** The K-replicate target matrix is regenerated bit-exactly
   from its registered seed protocol (`reliability.py: base_seed 1000+k`,
   per-rule `SeedSequence([seed, rule, radius])`) on the exact held-out
   panels (radius two primary; ECA where cached predictions exist). A joint
   rule-bootstrap resamples the same rules for both quantities and reports,
   per target, the 95% CI of R²_mechanistic − R²_replicate-agreement.
   *Equivalence margin (fixed here, before measurement):* margin_t =
   max(0.01, 1 − ICC_t), with ICC_t the per-target latent reliability
   already published under rev 8 — the maximal noisy-score headroom any
   estimator has over the replicate benchmark. *Wording rule:*
   "statistically indistinguishable" survives per target iff the 95% CI lies
   within ±margin_t; otherwise the manuscript downgrades to "consistent
   with" and prints the CI.
3. **M3 — enriched-panel decomposition (post-hoc confirmatory).** Held-out
   radius-two results reported separately for the force-held signature
   subpanel and the stratified-random remainder, plus a post-stratified
   pooled estimate: group-weighted SS_res/SS_tot with weights matching each
   group's prevalence in the 800-rule sampling universe (the paper's stated
   rule distribution) rather than its share of the enriched panel.
   Disclosure attached (fixed here): signature membership was computed from
   the same seed-0 target cache later used for evaluation labels, by the
   registered criterion-9 thresholds; the forced rules were never trained
   on.
4. **M4 — per-diagram reconstruction audit (post-hoc confirmatory).** Over
   every held-out diagram (not only the first per rule): table-coverage
   histogram and per-diagram exact-reconstruction rate, reported next to the
   per-rule numbers so the "single diagram" claim is auditable at both
   units. Descriptive; no gate.
5. **M5 — seed replication of the degradation-trained control (gated
   training ×2).** The rev-10 C-i configuration retrained with two new seeds
   (all else identical, 63 px smoke first); each is scored on the clean
   held-out panel (Table III protocol) and the frontier noise axis
   (direct-only evaluation, same cells/budgets as rev 10). *Stability rule
   (fixed here):* the noise-band claim keeps its current wording iff each
   new seed's per-cell median falls inside the seed-0 cell's rule-bootstrap
   95% CI at every noise cell in the recommended band; otherwise the band is
   reported as a per-seed range and Table V is re-worded accordingly.
6. **M6 — deployment-style stack (post-hoc confirmatory).** A ridge
   meta-model over [five statistics + CNN predictions] fit **only on
   training rules**, evaluated once on the untouched held-out panel;
   reported next to the rev-7 cross-fitted diagnostic (which keeps its own
   label). The registered rev-7 adds-value margin (0.02, CI excluding 0) is
   reused for interpretation; neither result overwrites the other.
7. **M7 — independent-panel replication of the frontier noise axis
   (post-hoc confirmatory).** The noise-axis cells re-simulated on the
   complementary half of the held-out panel (the rules the fixed-seed
   frontier subsample excluded), same budgets and estimator set
   (deterministic inverter, both posterior variants, sampled reader, frozen
   CNN, degradation-trained seed-0 CNN). *Verdict rule (fixed here,
   mirroring rev 9/10):* a cell's winner is re-stated only if, on the
   complementary panel, a different estimator's rule-bootstrap CI_low
   exceeds the original winner's CI_high; agreement within CIs is reported
   as replication.

## Revision 10 (2026-07-05) — changelog

Added **before any round-3 fairness-control measurement**, numbers-free. The
internal ARS panel review (`manuscript/reviews/simulated/`, editorial items
R-6 and R-5; independently DA M1/M6 and R3 Q1, echoing the real referee's
concern 7) identified an adaptation-budget asymmetry on the identifiability
frontier: the read-then-simulate family fields two estimators purpose-built
for degradation (Bayesian posterior; degradation-trained reader) while the
direct family is represented only by a clean-trained, architecturally
constrained CNN. Rev 10 registers the two symmetric controls and two
outstanding reporting items. No change to criteria 1–9 or any rev-2…9
threshold or verdict rule; single seed per control (disclosed limitation,
matching the reader's gating); 63 px smoke precedes each full training.

1. **C-i — degradation-augmented direct CNN (gated training).** The canonical
   direct-CNN configuration (`configs/m4_range2.yaml` architecture, epochs,
   batch size, optimizer, split, seed 0) retrained with the *reader's*
   registered input-degradation augmentation applied to training diagrams —
   the same families and ranges fixed for rev-9 F2 (bit-flip probability
   ~ U(0, 0.15) and masking fraction ~ U(0, 0.5), each applied independently
   with probability 1/2), targets unchanged. This gives the direct family
   exactly the adaptation the reader received, nothing more.
2. **C-ii — same-budget unconstrained CNN (gated training).** The expressive
   `resnet18` encoder (the architecture the anti-shortcut constraint was
   designed against), identical data, split, targets, epochs, batch size,
   optimizer and seed as C-i's parent config, clean-trained (no degradation
   augmentation); wall-clock and parameter count disclosed next to the
   constrained CNN's. This tests whether the matched-regime negative result
   is an artifact of the author-imposed first-layer constraint whose
   motivating claim rev-8 retired.
3. **Evaluation and verdict rules (fixed here, before measurement):**
   - *Matched regime:* both controls are scored on the clean-protocol
     held-out panel exactly as Table III (160 rules, production targets,
     rule-bootstrap CIs). The rev-7/8 verdict machinery is reapplied
     unchanged: a control "changes the matched-regime verdict" only if it
     meets the registered simulation-limited test that the current direct
     estimators fail (per-target R² CI reaching the replicate-agreement
     benchmark band). Superiority/equivalence margins unchanged (0.10 / TOST
     δ=0.05).
   - *Frontier:* both controls are evaluated on the existing rev-9 grid
     cells (noise, mask, density axes; same 80-rule panel, same n_pairs=48
     protocol, CNN-family estimators only — the read-family cells are not
     re-simulated). Rev-9 hypothesis (iii) is re-tested with the controls
     added to the direct-amortizer family under its unchanged rule (a
     violation = control's point estimate above the best read-family
     estimator's bootstrap CI_high at a cell with per-bit table recovery
     ≥ 0.95). C-i "extends into the dead zone" at a noise cell only where
     its rule-bootstrap CI excludes the F2-sampled point value from below —
     the same rule shape rev 9 used for F2-vs-F1.
   - *Reporting:* all outcomes are reported regardless of direction. If
     either control overturns the degraded-regime guidance or the
     matched-regime scoping, the manuscript text is rewritten to the
     measured result, not argued around; if the controls confirm the
     guidance, the scoped-claim language ("adaptation-naive amortization")
     is retained with the controls cited as evidence.
4. **Outstanding reporting items completed under existing registrations:**
   - *F1 predictive-interval calibration* (registered in rev 9, not yet
     reported): empirical coverage of the posterior's nominal 1σ predictive
     intervals per grid cell on the noise and mask axes, ε-estimated
     variant, same panel and budgets as the rev-9 grid. Reporting only; no
     pass/fail gate. Nominal coverage for a 1σ interval is ~68%; the
     comparison is stated per cell.
   - *Stacking under the headline base* (post-hoc confirmatory): the rev-7
     stacking protocol rerun with cross-fitted out-of-fold predictions of
     the boosted baseline (Table III's baseline of record) as the base
     regressor, CNN augmentation as before; increment + rule-bootstrap CI
     reported at the registered 0.02 margin. This answers "what is the
     increment under the headline protocol" (DA M2) without replacing the
     registered rev-7 result.

## Revision 9 (2026-07-05) — changelog

Added **before any identifiability-frontier measurement**, numbers-free. The
round-2 manuscript's own Discussion poses the open question: where exact rule
reading collapses (the rev-8 C4 phase diagram: bit-flip noise, heavy masking,
extreme IC densities), do a **Bayesian rule-posterior simulator** (F1) and a
**learned rule-reader→simulator** (F2, the referee's thrice-requested
comparator) restore simulation-limited accuracy? Results are held as a
**round-3 extension of the manuscript** (user decision 2026-07-05,
DECISIONS.md), kept on the `rev9-frontier` branch so the submitted PDF stays
frozen.

1. **New "Identifiability-frontier controls (rev 9)" section** (below) fixing
   F1 (Bayesian posterior over the rule table under an observation-noise
   model), F2 (learned table-bit reader feeding an exact simulator; **gated
   training**), and F3 (the extended degraded-observation grid on which all
   estimators are compared, with per-cell verdict rules).
2. **Pre-registered hypotheses** (stated here so they cannot be reframed post
   hoc): (i) F1 dominates the deterministic inverter in the intermediate-noise
   regime and degrades gracefully; (ii) F2 extends further into the degraded
   regime than F1; (iii) nowhere that per-bit table recovery remains high does
   any *direct* amortizer beat the best read-then-simulate estimator. Each is
   judged by the registered verdict rules, and a refuted hypothesis is reported
   as refuted.
3. **Registration-status labels for the manuscript:** F1 and its evaluation on
   the existing rev-8 axes are *post-hoc confirmatory* (new estimator, existing
   data axes); F2 and the two new axes (state-label noise, unknown radius) are
   *exploratory*. No change to criteria 1–9, rev-2…8 controls, or any existing
   threshold; the rev-8 verdict rules (TOST δ=0.05 primary, superiority 0.10)
   are reused unchanged.

## Revision 8 (2026-07-04) — changelog

Added **before any of the round-2 review-response analyses is measured**, in
response to the **second** referee report (`manuscript/reviews/chaos_second_review.md`,
verdict: major revision — a step up from the first report's reject). The referee
accepts the science and hands us a stronger, honest spine but flags two
integrity-level issues in the *reporting*: (A) the CNN-vs-five-statistic narrative
contradicts our own Tables I/III (the CNN median R² beats the baseline on two
radius-two rows, and the stacking increment is +0.32 on survival), so "dominates /
never beats / skip the network" is false as written; (B) the reliability *ceiling*
is the wrong benchmark for the mechanistic estimator, which is an **independent**
finite Monte-Carlo draw, so its expected agreement with the cached target is
**2·ICC−1**, not ICC. These new controls are **reported controls with
pre-registered decision rules and reporting rules**, not new pass/fail gates on
criteria 1–9. Numbers-free; auditable via git history. The margins are
pre-registered and **not to be edited after a number is seen** — claim corrections
go to `RESULTS.md`/manuscript text only.

1. **New "Round-2 review-response controls (rev 8)" section** (below) fixing
   C1 narrative correction (§1), C2 three distinguished ceilings (§2),
   C3 completion-policy sensitivity (§3), C4 identifiability sweep (§3/§4/§7),
   C5 statistics completeness & repeated outer splits (§6), C6 damage-signature
   landscape + ECA confusion matrix (§9), C7 mosaic-level spatial resampling (§8),
   C8 accuracy–compute Pareto (§11). Section numbers in parentheses are the second
   referee's concerns.
2. **Reporting language fixed, pre-registered:** no *global* CNN-vs-baseline
   ordering is asserted — every such comparison is reported per target with its
   paired CI and TOST verdict; the word "tie"/"equivalent" is reserved for a
   **passing TOST** (otherwise "inconclusive"); "reaches the reliability ceiling"
   is replaced by comparison to the **independent-replicate agreement** benchmark;
   "parameter-free" is retired for the mechanistic estimator unless its completion
   policy is eliminated; "smooth function of the rule" is removed. Every analysis
   is labelled **registered / post-hoc-confirmatory-on-new-data / exploratory**.
3. **No change to criteria 1–9, to rev-2…7 controls, or to any existing
   threshold.** The rev-7 R1–R8 decision rules stand; rev-8 corrects how their
   *outputs* are reported and adds the ceiling correction (C2), the completion
   sensitivity (C3), and the identifiability sweep (C4).

## Revision 7 (2026-07-04) — changelog

Added **before any of the review-response experiments is measured**, in response
to a detailed referee report on the first manuscript submission
(`manuscript/reviews/chaos_review.md`). These are **reported controls with
pre-registered decision rules**, not new pass/fail gates on criteria 1–9; they
harden the negative benchmark into an equivalence-grade result, add the
interpretable positive result (mechanistic rule-inference estimator), and
validate the two descriptive claims (glider landscape, spatial maps) against
independent ground truth. Numbers-free; auditable via git history. The margins
fixed below (δ, the incremental-value margin, K) are pre-registered bars, not
measured outcomes, and are **not to be edited after a number is seen** — claim
corrections go to `RESULTS.md`/manuscript text only.

1. **New "Review-response controls" section** (below) fixing R1 equivalence &
   per-target inference (§2), R2 incremental-value/stacking (§5), R3
   reliability-adjusted ceiling (§3), R4 mechanistic rule-inference estimator
   (§5), R5 rule-recovery probes (§1), R6 independent glider validation (§8),
   R7 nuCA local-perturbation map ground truth (§9), R8 distribution-shift &
   finite-size (§7). Section numbers in parentheses are the referee's concerns.
2. **Scope of claims tightened, pre-registered:** "no advantage of the deep net"
   may be asserted only where the R1 equivalence test (TOST) passes or where the
   baseline is superior; the "structural" language is bounded to the R8-tested
   regime; "glider-supporting prevalence" is replaced by "fraction satisfying the
   pre-registered damage-signature criterion" except on the R6 detector-validated
   subset.
3. **No change to criteria 1–9, to rev-6 controls S1–S3, or to any existing
   threshold.** The rev-6 S1 superiority rule (median ΔR² ≥ 0.10 on ≥ 3 features)
   is retained and *supplemented* by R1's equivalence test — S1 asks "is the net
   better?", R1 asks "are they equivalent, or is the baseline better?".

## Revision 6 (2026-07-04) — changelog

Added **before any baseline-regression fit, any multi-seed retraining, and any
set-dependence measurement** — the manuscript-solidification controls, fixed here
so their outcomes cannot be defined after seeing them (same hygiene as rev 2–5;
auditable via git history):

1. **New "Baseline & robustness controls" section** (below) fixing three
   pre-measurement specs for the manuscript: **S1** the single-diagram feature
   baseline the CNN amortizer is compared against, **S2** the multi-seed
   robustness protocol, **S3** the RNG set-dependence bound.
2. These are **reported controls with pre-registered interpretation rules**, not
   new pass/fail gates on criteria 1–9: they error-bar and contextualize the
   existing criteria; the spatially-resolved-map contribution stands independent
   of S1's outcome.
3. No change to criteria 1–9 or to any existing threshold.

## Revision 5 (2026-07-04) — changelog

Added **before any range-2 (M4) model is trained and before any sampled rule is
held out** — the simulator, sampler, radius-aware targets and the complex
signature ship in the same change set, and the leave-complex-out split is a
deterministic function of the pre-registered signature (auditable via git
history):

1. **Criterion 6 extended to the range-2 rule space** (M4) — same bars,
   evaluated on sampled range-2 rules; the point of M4 is to test amortization
   where the intermediate/complex regime is *populated*, not a two-member club.
2. **New criterion 9 (complex-regime placement)** — the direct test of the
   §6 caveat: hold out a *set* of complex rules and require unbiased placement.
3. The **complex signature** thresholds are fixed here (calibrated on the ECA
   reference and the a-priori embedded-ECA anchors, `caspectra/eval/regimes.py`).
4. No change to criteria 1–8 or to any existing threshold.

## Revision 4 (2026-07-03) — changelog

Added **before any map has been evaluated on a striped-mask diagram beyond the
qualitative period-32 figure of criterion 7's secondary diagnostics, and before
any composed-system invariant has been measured directly** (the harness ships
in the same change set; auditable via git history):

1. **New criterion 8 (stripe resolution + alloy transfer)** — characterizes
   the phenotype maps' spatial resolution and gates their behaviour *below*
   that resolution, with the full measurement spec fixed below.
2. No change to criteria 1–7 or to any existing threshold.

## Revision 3 (2026-07-03) — changelog

Added **before any non-uniform-CA measurement exists** (the `NonUniformCA`
simulator is implemented in the same change set; no map has been evaluated on
composed diagrams at the time of writing — auditable via git history):

1. **New criterion 7 (compositional map transfer)** — gates the per-patch
   phenotype-map payoff of Lever A on non-uniform CA diagrams, with the full
   measurement spec (rule panel, masks, interface exclusion) fixed below.
2. Housekeeping: the label spot-check note under "Reference labels" updated —
   closed by decision on 2026-07-02 (`rule_labels_PROVENANCE.md`).
3. No change to criteria 1–6 or to any threshold.

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

- `rule_labels.csv` (provenance: `rule_labels_PROVENANCE.md`; automated checks
  accepted by decision 2026-07-02, transcribed class lists kept for re-verification).
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
   *(Measured 2026-07-02: PASS in both split variants, median rule-level R²
   0.863 / 0.836 — `RESULTS.md`.)*
7. **Compositional map transfer (rev 3; gates the phenotype-map payoff).**
   The per-patch maps must recover *where* behaviour differs, not merely echo
   the global prediction. Measured on **two-region half/half non-uniform CA
   diagrams** (`caspectra/ca/nuca.py`): left half evolves under rule A, right
   half under rule B, standard protocol otherwise (Bernoulli(1/2) ICs, ring
   127, horizon 127, transient kept).
   - **Model under test:** the frozen `runs/lever_a/checkpoint_final.pt` (no
     retraining, no nuCA data in training) for the primary measurement;
     retrained variants (e.g. a shallower encoder) are additionally reported
     against the same spec.
   - **Primary panel (gated):** the 16 rules {0, 4, 204, 184, 26, 73, 154, 90,
     60, 30, 18, 45, 22, 41, 106, 54} — all orbit representatives in the main
     run's TRAIN split (so criterion 7 isolates *compositional* generalization
     from the rule transfer already gated by criterion 6), stratified across
     damage regimes: dead (0), fixed-point (4, 204), traffic (184), locally
     chaotic (26, 73, 154), additive/ballistic (90, 60), chaotic (30, 18, 45,
     22), borderline (41, 106), complex (54). All 120 unordered pairs, ≥ 8
     ICs per pair with the rule-to-side assignment alternated.
   - **Statistic:** per region, the mean un-standardized `predict_map` output
     over map patches whose receptive field lies entirely inside the region
     (patches within ±16 px of either rule interface are excluded — the
     4-block encoder's receptive-field half-width; the ring has two
     interfaces). Ground truth per region = the pure rule's direct invariant
     vector (`load_or_compute_invariant_targets`, n_pairs = 256, reference
     protocol). Per-feature R² across all (pair, IC, region) region-means,
     then the **median across the 4 features** is gated.
   - **Bars:** success ≥ 0.5; failure < 0.2 (mirrors criterion 6).
   - **Mandatory control (validity, not a gate):** rule_a == rule_b diagrams
     must reproduce the uniform-diagram predictions exactly (same simulator
     output, same map) — if the control fails, the harness is broken and no
     panel number may be reported.
   - **Secondary diagnostics (reported, not gated):** pairs of each main-run
     held-out rule with anchors {0, 204, 30, 54} (rule transfer and
     composition jointly, incl. 110); spreading-rate **ordering accuracy**
     (fraction of pairs with distinct true rates where the predicted
     region ranking matches); striped masks (period 32, qualitative — below
     the interface-exclusion resolution by construction); interface-band
     predictions vs the two flanking regions.

8. **Stripe resolution & alloy transfer (rev 4; characterizes and gates the
   maps below the half/half geometry).** Criterion 7 used half/half masks,
   where even a 7-column map has interface-free columns; no measurement so far
   supports the finer claim that a higher-resolution map buys finer *spatial*
   discrimination. Criterion 8 measures that directly, on striped masks
   (`striped_mask(127, p)` — alternating stripes of `p` cells; the last stripe
   truncates since 127 is not divisible by `p`). Each striped mask is
   **cyclically rolled by a per-IC random offset** (seeded) so stripe phase is
   not accidentally aligned with the fixed patch grid. Applies to **both**
   certified checkpoints (`runs/lever_a_local`, 7×7 map, patch ≈ 18 cells;
   `runs/lever_a_shallow`, 15×15 map, patch ≈ 8.5 cells), each measured and
   gated independently against the same spec.

   **8a — stripe resolution (minimal gate + reported characterization).**
   - *Systems:* periods p ∈ {32, 16, 8, 4, 2}; pairs = all criterion-7
     primary-panel pairs whose cached pure-rule spreading rates differ by
     ≥ 0.25 (n_pairs = 256 reference cache — 78 pairs; derived from public
     cached truth, fixed before any map is rendered). 16 ICs per (pair, p),
     random mask offset per IC; plus 16 half/half ICs per pair for the
     normalizer.
   - *Statistic:* time-averaged per-column spreading-rate reading of the map;
     per-diagram contrast C = mean over columns whose centre cell runs the
     hotter rule (by cached pure-rule rate) − mean over the colder columns,
     **no interface exclusion** (degradation is the measurement). Per pair:
     mean over ICs → C(p) and C(half). Relative contrast R(p) = C(p)/C(half).
     Pairs with measured C(half) < 0.05 are excluded from R(p) aggregation
     (unstable ratios) and reported as excluded. **Resolution limit** =
     smallest p with median-over-pairs R(p) ≥ 0.5.
   - *Gate (deliberately minimal):* at p = 32, the mean-over-pairs R(32) must
     be positive with a 95% bootstrap CI (over pairs, 10 000 resamples)
     excluding 0. A checkpoint failing this cannot claim any spatial
     resolution finer than half/half, and the published "pick 15×15 for
     spatial detail" guidance must be corrected wherever it appears.
     The full R(p) curves and the 7×7-vs-15×15 comparison are **reported
     characterization, not pass/fail** — no bar is set on the resolution
     limit itself.

   **8b — alloy transfer (gated; bars mirror criteria 6/7).** Below the map's
   resolution a fine-striped composed system is effectively a *new* homogeneous
   system — an "alloy" of two rules — and its own invariants are directly
   measurable by the same twin-run protocol run on the composed simulator.
   - *Systems:* all 120 criterion-7 primary-panel pairs × p ∈ {2, 4}
     (240 alloys; both periods are below both checkpoints' patch sizes),
     8 ICs each with random mask offset per IC.
   - *Truth:* `damage_spreading_features` computed **on the composed
     simulator** (n_pairs = 256, width 127, horizon 62, Bernoulli(1/2) —
     identical protocol to the pure-rule reference cache), at mask offset 0
     only (Bernoulli ICs are translation-invariant on the ring, so alloy
     invariants do not depend on the offset).
   - *Statistic:* per (alloy, IC), the global map mean (≡ the global
     prediction, by the GAP∘linear identity) vs the alloy truth; per-feature
     R² over all records; the **median across features is gated**: success
     ≥ 0.5, failure < 0.2. *Degeneracy rule (fixed now):* a feature whose
     alloy-truth std across the 240 alloys is < 0.05 is reported but excluded
     from the gated median.
   - *Mandatory control (abort, not gate):* for r ∈ {0, 30, 54, 204} and both
     periods, the (r, r) "alloy" truth must equal the pure-rule truth exactly
     (same rng path) — otherwise the truth harness is broken and no panel
     number may be reported.
   - *Pre-registered interpretation baseline (reported, NOT gated):* the
     **constituent-mixture baseline** — the mask-area-weighted mean of the two
     pure rules' cached invariant vectors — scored against the same alloy
     truth. If the map beats the mixture, the network reads *emergent* alloy
     behaviour; if not, the maps do texture-mixing below their resolution.
     Both outcomes are reportable findings; neither changes the 8b verdict.

9. **Complex-regime placement in the range-2 space (rev 5; M4; the §6
   repair).** Criterion 6 passed on ECAs but the complex regime there is a
   two-member club ({54, 110}); held out, either is mispredicted, *pulled*
   toward the nearest populated regime (RESULTS.md 2026-07-02: 110's rate read
   0.54 vs true 0.37; 54's 0.18 vs true 0.44). ECAs cannot fix this — ~2
   complex rules in 88. Criterion 9 tests whether **populating** the regime
   (range-2 binary CAs, `caspectra/ca/range_ca.py`) lets the amortizer place
   complex behaviour *without systematic bias*.
   - **Space & protocol:** two-state, radius-2 CAs (2^32 rules), **sampled**
     and de-duplicated by the reflect+complement orbit. Standard protocol
     otherwise: Bernoulli(1/2) ICs, ring width 127, horizon **radius-aware**
     (`width // (2·radius) − 1`, so the light cone cannot wrap; the spreading
     rate is normalized by the cone speed so the four features keep their
     meaning across radii). The panel is a fixed sample: `sample_rules(N, 2,
     seed=0)`; `N` (target 600–1000) is fixed in the training config generated
     by `scripts/analyze_range2_landscape.py` **before** training.
   - **Complex signature (pre-registered, `regimes.COMPLEX_SIGNATURE`):** a
     rule is *complex* iff `damage_survival > 0.85` **and** `0.15 ≤
     spreading_rate ≤ 0.28` **and** `cone_fill < 0.6` **and** `damage_fraction
     < 0.15` (the range-2-protocol calibration: damage persists, spreads
     sub-ballistically, in a sparse localized cone). Calibrated on the
     embedded-ECA anchors so it includes the class-IV cluster {54, 110, 106};
     the additive-adjacent rule 60 also matches (a known, reported contaminant).
     The ECA-protocol sibling (`COMPLEX_SIGNATURE_ECA`) selects exactly
     {54, 106, 110} across the 88 ECA reps — the provenance the method works.
   - **Split:** leave-complex-out — **all** signature-complex sampled rules go
     to the hold-out set (`force_holdout`), plus a stratum-free 20 % random
     hold-out of the rest for the general criterion-6 number. Training never
     sees a complex rule.
   - **Gates (mirror criteria 6/7):** (a) **criterion-6 median R²** on the
     complex hold-out ≥ 0.5 (fail < 0.2); and (b) **no systematic regime pull**
     — the mean *signed* spreading-rate error over the complex hold-out has
     `|mean| ≤ 0.10` (the ECA baseline was strongly signed, ±0.15–0.26). Both
     must hold to pass.
   - **Mandatory control (validity, not a gate):** embedded-ECA continuity —
     the range-2 rules embedding the ECAs reproduce the ECA *diagrams*
     bit-for-bit (`tests/test_range_ca.py`); a break voids the harness.
   - **Reported (not gated):** the complex-regime count/fraction under uniform
     sampling (is it actually populated?); the 4-D invariant landscape vs the
     ECA landscape; curated-anchor placements; per-feature R² and signed bias
     on the complex hold-out vs the general hold-out.
   - **Pre-registered fallback (named now, not post hoc):** if uniform sampling
     yields < 15 complex rules, re-sample with a targeted sampler — Hamming-1
     perturbations of the embedded-complex rule tables and rules with high
     input-entropy variance (Wuensche 1999) — and report both the uniform
     density and the enriched panel. (The measured density is itself a reported
     criterion-9 outcome, above.)

## Baseline & robustness controls (rev 6)

Manuscript-grade controls fixed before measurement. Each carries a
pre-registered interpretation rule; none is a new pass/fail gate on criteria 1–9.

**S1 — single-diagram baseline (does the amortizer beat cheap statistics?).**
The criterion-6/9 claim is that the damage-spreading invariants — *defined* by
twin runs — are non-trivial to recover from a **single** diagram. The null
alternative is that a handful of cheap single-diagram statistics already recover
them (the "the encoder just reads density" objection). Control: fit regressors
from the label-free single-diagram features of `caspectra/eval/baselines.py` —
mean (polarity-folded) density, temporal activity, compression ratio, 2×2 block
entropy, and a **radius-aware** input-entropy variance (Wuensche 1999;
width-(2r+1) neighbourhood codes) — onto the four damage invariants, using the
**identical leave-rules-out split** as the CNN it is compared to (criterion 6 on
ECAs; criterion 9's leave-complex-out on range-2). Regressors: ridge and
gradient-boosted trees (the stronger is the baseline of record). Report
per-feature and median held-out-rule R² for baseline vs CNN on the same truth.
  - *Pre-registered interpretation:* the amortizer is "meaningfully better" iff
    its held-out median R² exceeds the best baseline's by ≥ **0.10** absolute on
    the same split (and, secondarily, beats it on ≥ 3 of the 4 features). If the
    margin is smaller, the manuscript **softens the global-amortization claim**
    and foregrounds the per-patch phenotype map — which the scalar baseline
    cannot produce at all (an architectural fact, not a measured one) — as the
    contribution. Both outcomes are honest and reportable; S1 changes emphasis,
    not the validity of criteria 6–9.

**S2 — multi-seed robustness (error bars on every headline number).** The
certified checkpoints were each a single training run. Retrain the headline
models with **5 seeds** (seeds fixed as {0, 1, 2, 3, 4} before running; each
seed sets both weight init and the IC-stream seed; identical data split and
protocol otherwise): `lever_a_local` (criteria 6/7), `lever_a_shallow`
(criterion 8a), and `m4_range2` (criteria 6/9). Report **mean ± std** of each
gated median R² and of the criterion-9 signed spreading-rate bias.
  - *Pre-registered interpretation:* a gate is robust iff it holds at **mean − 1
    std** (equivalently, at all 5 seeds). A gate that passes only at some seeds
    is reported as **seed-fragile**, not as a pass.

**S3 — RNG set-dependence bound.** `dynamics_feature_matrix` seeds one RNG per
rule by sorted-list position, so a rule's target depends on the set it is
computed in (documented in `targets.py`). Bound it: for ~10 rules spanning the
regimes, recompute the four invariants as members of **3 different rule sets**
(varying size and composition) and report the maximum |Δ| per feature.
  - *Pre-registered interpretation:* if max |Δ| ≤ **0.01** (the documented
    bootstrap precision at n_pairs = 256), the coupling is declared immaterial
    and disclosed as such. If any feature exceeds 0.01, the per-rule RNG is
    re-seeded by **rule identity** (not list position) and the affected caches
    and criteria are recomputed before the manuscript reports them.

## Review-response controls (rev 7)

Fixed before measurement, each with a pre-registered decision rule; none is a new
pass/fail gate on criteria 1–9. All results below are reported **per target**
(the four damage-response statistics: survival, fraction, spreading rate, cone
fill), never only as the 4-target median.

**R1 — Equivalence & per-target inference (§2: "failed superiority ≠
equivalence").** The unit of resampling is the **held-out rule** (rule-level
cluster bootstrap). For each ordered method pair (A, B) and each target, the
paired difference ΔR² = R²_A − R²_B is computed on the *same* held-out rules, and
its interval is estimated by a nested resample: cluster bootstrap over held-out
rules (**10 000 resamples**) within **≥ 10 repeated leave-rules-out outer
splits**, propagating the **K target replicates** of R3 (rules × splits × target
noise). Decisions per target:
  - **Superiority** (retains the rev-6 S1 rule): A is meaningfully better iff the
    median ΔR² ≥ **0.10** *and* the 95% paired CI excludes 0 in A's favour.
  - **Practical equivalence (TOST):** with a pre-registered margin **δ = 0.05**
    absolute R², A and B are practically equivalent on a target iff the **90% CI
    of ΔR² lies entirely within (−δ, +δ)**. δ is chosen a priori as a negligible
    R² gap and is cross-checked against the R3 noise floor (a gap below 1 −
    reliability is meaningless regardless of δ).
  - *Reporting rule:* "the deep net has no advantage" is written as **equivalence
    only where TOST passes**; where B's (baseline's) CI lies entirely above +δ,
    it is written as **baseline superiority** (expected on ECA global); elsewhere
    it is **inconclusive/underpowered**, never "equivalent." Every headline
    number carries its per-target paired CI and TOST verdict.

**R2 — Incremental value / stacking (§5: "does the representation add
information beyond the five statistics?").** Cross-fitted, rule-level: on each
outer fold, fit the baseline (5 features → target) on the training rules and the
CNN separately; on the held-out rules, compute the **incremental R²** of adding
the CNN's prediction to the 5 features (nested-model cross-fit R², equivalently
the variance of the held-out baseline residual explained by the CNN prediction).
Decision per target: the learned representation **adds value** iff incremental
ΔR² > **0.02** with a rule-bootstrap 95% CI excluding 0. The symmetric complement
(does the baseline add value beyond the CNN?) and the oracle-vs-both stack are
reported alongside. This is the rigorous form of the paper's central claim.

**R3 — Reliability-adjusted ceiling (§3: "MC noise does not by itself bound
R²").** Draw **K = 20** independent Monte-Carlo target replicates per rule via
`dynamics_feature_matrix(seed=k)` at the production `n_pairs`. Per target,
decompose the across-rule variance into between-rule (signal) and
between-replicate/within-rule (noise) components; the **reliability** is
ICC(1) = σ²_signal / (σ²_signal + σ²_noise), and the **reliability-adjusted R²
ceiling** is this ICC (classical attenuation bound). Report per target, with the
conditional-on-survival quantities (fraction, rate, fill) and the survival
probability handled separately because their noise is heteroscedastic and
non-Gaussian. This **replaces** the "0.006–0.014 upper-bounds R²" sentence;
observed R² for every method is read against the per-target ceiling.

**R4 — Mechanistic rule-inference estimator (§5: the interpretable reference
method).** `caspectra/eval/rule_inference.py:infer_rule(diagram, radius)`
tabulates observed neighbourhood→next-cell transitions and returns the inferred
table plus its **coverage** (fraction of the 2^(2r+1) entries observed).
Pre-registered handling of unobserved entries: **default to 0**, with coverage
reported and the sensitivity to the default reported (majority-fill as the
alternative). `mechanistic_estimate(diagram)` = infer → build the simulator
(`caspectra/ca/{eca,range_ca}.py`) → `damage_spreading_features` at the
production protocol → the four targets, evaluated on the **same** leave-rules-out
split as every other method. Reported (no pass/fail bar — it is the interpretable
reference): per-target R² vs the R3 ceiling; an **identifiability curve**
(exact-table-match rate and per-entry accuracy vs number of observed rows /
width). Pre-registered expectation (stated so it cannot be reframed post hoc): on
rules whose table is fully covered the estimator should approach the ceiling;
under-covered rules are where it should degrade, and that degradation is a
reported finding.

**R5 — Rule-recovery probes (§1: is the rule actually recoverable from the
representation?).** Extend `caspectra/eval/probes.py` to fit probes from each
source S ∈ {raw-diagram summary statistics, an intermediate encoder feature map,
the 64-d bottleneck, the 5 handcrafted baseline features} predicting (a) rule /
orbit identity and (b) each individual truth-table entry. Identity probes use a
stratified split (identity cannot transfer to unseen rules); truth-table-entry
probes use a **leave-rules-out** split (tests transfer of the *reading*
mechanism). Report balanced accuracy vs the majority baseline for all sources
side by side. Pre-registered reporting rule: this **replaces** the unsupported
"the 2×2 first-layer kernel prevents rule recovery" assertion — if the bottleneck
(or any layer) probe recovers the rule well above chance, the architecture is
**not** described as "anti-shortcut"; the readability of the rule is instead
reported as the mechanism behind the null result.

**R6 — Independent glider validation (§8: the complex label must not be defined
by, and validated on, the same damage signature).** A detector **independent of
the damage signature**: from long-horizon evolution (production ring 127 plus a
ring-255 confirmation so structures are not wrap-limited), estimate and subtract
the dominant temporally-periodic background, then detect **persistent localized
propagating structures** (connected components of the background-subtracted field
that persist ≥ a fixed number of rows and translate at finite, sub-ballistic
velocity), and/or apply a **periodic-localization test** (a single localized seed
on a quiescent background yields a bounded, comoving-eventually-periodic
structure). `caspectra/eval/gliders.py`; a rule is **detector-complex** iff such
a structure is found in ≥ a fixed fraction of trials (threshold fixed in the
module before range-2 application). The detector is first **validated to recover
{54, 110, 106} and reject ordered {0, 4, 204} and chaotic {30, 90, 22}**.
Reported on a held-out range-2 sample: **agreement, false-positive and
false-negative rates** of the damage signature vs the detector. Pre-registered
language rule: landscape prevalence is reported as the "**fraction satisfying the
pre-registered damage-signature criterion**"; only the detector-validated subset
is called "glider-supporting," and both numbers appear side by side with FP/FN.

**R7 — nuCA local-perturbation map ground truth (§9: the map needs an
independently computed local ground truth).** For a mosaic
(`caspectra/ca/nuca.py:NonUniformCA`, `striped_mask`), flip the initial cell at
position x0, evolve twin copies, and measure the four damage statistics on the
**local comoving cone** around x0 → a per-location target vector (averaged over
ICs). This location-resolved target does **not** assume a stripe carries a
uniform rule's phenotype (it measures the composed system in place). Compare
`predict_map` (CNN) and the handcrafted patch-map to this ground truth on
**localization error** (offset of predicted regime boundaries), **spatial
correlation** (per-column predicted vs true invariant), and **calibration**
(predicted vs true value), across ≥ a fixed set of rule pairs, both stripe
orientations, random mosaics, and interface regions analysed explicitly. Window
selection is **fixed from validation data** for the primary comparison; the
per-period best window is reported only as a labelled sensitivity. Verdict rule:
"CNN resolves finer" is asserted only if the CNN map beats the
validation-selected handcrafted map on localization error with a bootstrap 95% CI
excluding 0; ties and losses are reported as such.

**R8 — Distribution shift & finite-size (§7: the conclusion is one regime, not
structural in general).** Train the amortiser and fit the baseline and the R4
oracle on the reference regime, then **evaluate under shift**: IC densities
p ∈ {0.25, 0.75} (extremes 0.1/0.9 as context), widths/horizons {63, 127, 255}
(finite-size scaling; horizon stays radius-aware), perturbation types {1-bit,
multi-bit, 3-cell block}, and a **rule-family holdout** (hold out an entire
additive/other family rather than random rules). Report **degradation curves**
(R² vs shift) for oracle, baseline, and net. Pre-registered interpretation: the
"structural / no-advantage" claim is asserted **only within the tested regime**;
where the R2 incremental value of the net rises above the 0.02 margin (CI
excluding 0) under any shift, that regime is reported as one where representation
learning begins to help — a finding, never suppressed.

## Round-2 review-response controls (rev 8)

Fixed before measurement, each with a pre-registered decision/reporting rule; none
is a new pass/fail gate on criteria 1–9. They correct how the rev-7 outputs are
reported (§1, §2) and add three analyses (§3 completion sensitivity, §3/§4/§7
identifiability sweep, §11 compute). All results are reported **per target**.

**C1 — Narrative correction (§1: the CNN-vs-baseline claim contradicts the
tables).** No *global* ordering of the CNN and the five-statistic baseline is
asserted. For every task and target the two are compared by the R1 paired
cluster-bootstrap and classified **superiority / practical-equivalence (TOST) /
inconclusive** by the rev-7 rule; the manuscript states the per-target verdict, not
a summary "beats/never beats". The **complementarity** of the CNN is reported as
the R2 stacking increment (CNN over five statistics) with its CI, and the symmetric
increment (five statistics over CNN). Pre-registered reporting rule: where the
stacking increment CI excludes 0 above the 0.02 margin on a target, the CNN is
described as **adding information** on that target (expected: survival); the
headline is the mechanistic estimator's dominance over **both** direct estimators,
not any CNN-vs-baseline ordering.

**C2 — Three distinguished ceilings (§2: the reliability ceiling is the wrong
benchmark for an independent-simulation estimator).** From the K=20 replicates of
R3, report per target three quantities, with rule-bootstrap CIs:
  1. **Latent-target reliability** ICC(1) = σ²_signal/(σ²_signal+σ²_noise) — the
     ceiling for a predictor of the *noise-free* target mean.
  2. **Independent-replicate agreement** — the empirical per-target R² of one MC
     replicate predicting another (expectation 2·ICC−1 under equal-variance
     additive noise). This is the correct benchmark for the mechanistic estimator,
     which returns a fresh independent MC simulation.
  3. **Large-simulation reference** — targets recomputed at a much larger `n_pairs`
     (subset of rules) as a near-noise-free θ; the mechanistic estimator is scored
     against this to show it approaches the ICC ceiling as its own MC budget grows.
Decision/reporting rule: the mechanistic estimator's accuracy is judged **against
the independent-replicate agreement benchmark (2)**, not against ICC; the phrase
"reaches the reliability ceiling" is replaced accordingly. Survival is treated as
heteroscedastic/non-Gaussian: its reliability CI is bootstrap-based, not read off a
Gaussian random-effects fit alone.

**C3 — Completion-policy sensitivity (§3: default-zero is an unacknowledged
prior).** For `infer_rule`, report the distribution of observed rule-table
**coverage** and the number of **missing entries** per rule, broken down by rule
space, target stratum (Wolfram/LP class where available), and outcome class
(exact-reconstruction success vs failure). Compare four completions of unobserved
entries — **default-0, default-1, empirical-prior (marginal bit frequency),
posterior-averaged** (enumerate the 2^k completions for small k, sample for large
k) — reporting per-target mechanistic R² under each. A **posterior-averaged**
mechanistic estimate propagates completion uncertainty into a predictive interval;
its calibration (coverage of nominal intervals) is reported. Reporting rule:
"parameter-free" is retired; the estimator is described as **matched-model system
identification with an explicit completion prior**, and the sensitivity of the
headline numbers to the prior is stated.

**C4 — Identifiability sweep (§3/§4/§7: quantify when "read the rule" holds).**
On a fixed rule panel, sweep the observation axes — **diagram width, number of
time-steps, IC density, IC correlation length, partial-observation (masking) rate,
observation (bit-flip) noise, state-label permutation noise, known-vs-unknown
radius** — one/two at a time from the reference protocol. Per sweep cell report:
rule-table **coverage**, **exact-reconstruction rate**, **mechanistic** target R²,
**five-statistic** R², and the **existing (frozen)** CNN R² on the axes that
preserve its fixed input geometry (noise, partial observation, label noise at the
reference width×horizon). Where an axis changes the CNN's input shape (width,
steps), the CNN is **omitted** and this is stated (it was not trained on that
geometry; retraining is out of scope this round). Pre-registered interpretation:
the "read-the-rule" recommendation is asserted **only in the region where
exact-reconstruction is high**; regions of degraded observability where the
mechanistic estimator falls and the frozen CNN degrades more gracefully are
reported as **where a learned estimator could plausibly help** — a finding, never
suppressed. Labelled **exploratory** (new axes, not in the rev-7 registration).

**C5 — Statistics completeness & repeated outer splits (§6).** Report the
**complete per-target table for radius two** (not only ECA): held-out rule count,
each method's R², its rule-bootstrap CI, the CNN seed mean and spread, the paired
ΔR² and CI for each method pair, the superiority/equivalence/inconclusive verdict,
and the C2 replicate-agreement benchmark. Uncertainty beyond a single split is
added for the **non-CNN methods** (deterministic given data): **leave-one-orbit-out**
over the 88 ECA representatives and **≥ 10 repeated leave-rules-out** outer splits
for radius two; the CNN is reported at the fixed pre-registered split with its
five-seed spread and the split-level uncertainty is **stated as a limitation** (no
retraining this round). The TOST margin is reported at **δ ∈ {0.02, 0.05, 0.10}**
(sensitivity), with δ=0.05 remaining primary. Table III (stacking) gains CIs and
the **full stacked-model R²** alongside the increment.

**C6 — Damage-signature landscape + ECA confusion matrix (§9).** The radius-two
landscape is renamed a **"damage-signature landscape"** in title, abstract,
Discussion and figure; the prevalence is reported as "fraction satisfying the
pre-registered finite-horizon damage-signature criterion under the radius-two
sampling distribution", never as validated glider/class-IV prevalence. The ECA
detector validation is reported as a **full confusion matrix**: number of positives
and negatives, sensitivity/recall, specificity, precision, F1, balanced accuracy,
the exact detector settings, and the documented failure mode (rule 54). Raw
agreement alone is not reported as the headline (it is dominated by negatives).

**C7 — Mosaic-level spatial resampling (§8).** In the nuCA map benchmark the unit
of resampling is the **mosaic / composed system**, not the column (adjacent columns
share local dynamics, so a column bootstrap is anti-conservative). The map result
is labelled by its **TOST verdict** under δ=0.05 (expected: inconclusive, given the
reported CI) — the word "tie" is not used unless TOST passes. The report states the
number of mosaics, rule pairs, stripe periods and replicates, the train/val/test
disjointness, the window-selection procedure, and that the local ground truth uses
independent random streams. "training-free" is corrected to "amortization-free at
deployment (a pretrained ridge/GBM)".

**C8 — Accuracy–compute Pareto (§11).** Report, per estimator, wall-clock latency
per diagram (mechanistic = rule inference + MC simulation; CNN = one forward pass),
the number of MC pairs used by the mechanistic simulator, the one-time CNN training
cost, and the **break-even query count**, plus an **accuracy-vs-MC-budget** curve
for the mechanistic estimator. The practical recommendation is stated **with** its
compute cost, not in the abstract.

## Identifiability-frontier controls (rev 9)

Fixed before measurement; none is a new pass/fail gate on criteria 1–9. The
question: **which estimator class wins where, as the observation model degrades
away from the matched (clean, complete, known-radius) regime** in which the
rev-8 mechanistic estimator is simulation-limited-optimal.

**F1 — Bayesian rule-posterior simulator (no training).** From one diagram,
per-entry transition counts (`ones_k` of `total_k`) are already tabulated by
`infer_rule_table` (`caspectra/eval/rule_inference.py`). Under a **bit-flip
observation-noise model** with flip probability ε (each observed *output* cell
is flipped independently; input-side corruption is treated by the same
effective-ε approximation and stated as such), the per-entry likelihood is
Binomial: P(ones_k | bit=1) = Binom(total_k, 1−ε), P(ones_k | bit=0) =
Binom(total_k, ε). With a Bernoulli(p₀) prior per entry (p₀ = the observed
marginal one-frequency, as in the rev-8 completion machinery; sensitivity to
p₀ = 1/2 reported), this yields an independent per-entry posterior P(bit_k=1).
The estimate is the **posterior-predictive damage response**: sample tables
from the per-entry posteriors (reusing `mechanistic_estimate_posterior`'s
sampling), simulate each under the reference protocol with an independent RNG,
and average; the sample spread is the predictive interval. Two ε regimes are
registered: **(a) ε known** (the protocol's true corruption rate is passed in);
**(b) ε estimated** by maximizing the observation self-consistency (the
fraction of transitions agreeing with the per-entry majority) over a fixed ε
grid — the grid and the selection rule are fixed in code before measurement.
Decision rules: F1 "restores identification at a grid cell" **only** where its
per-target R² rule-bootstrap CI excludes the deterministic inverter's point
value from below; the calibration of its nominal 1σ predictive intervals is
reported per cell. Label: **post-hoc confirmatory** on the rev-8 axes.

**F2 — learned rule-reader → simulator (GATED training).** A small CNN
(backbone reused from `caspectra/models/encoder.py`) with a `2^(2r+1)`-unit
sigmoid head is trained on **training-split rules only** (the registered rev-5
leave-rules-out split; held-out rules never seen) to predict the generating
rule's table bits from a diagram, with **noise/masking augmentation** drawn
from the same degradation families as the F3 grid (augmentation ranges fixed
in the training config before training; the grid's *test* corruption levels
are not tuned on). Evaluation on held-out rules: **(a) F2-MAP** — threshold the
predicted bit probabilities at 1/2, simulate the resulting table exactly;
**(b) F2-sampled** — sample tables from the predicted per-bit probabilities and
average the simulated responses (predictive interval reported). Reported per
grid cell: per-bit balanced accuracy, exact-table rate, per-target and median
R². Training discipline: 63 px smoke first; each full 127 px run individually
approved; one seed per rule space initially (seed variance noted as a
limitation, expanded only if the result is borderline). Label: **exploratory**.

**F3 — the extended degraded-observation grid.** Estimators: {deterministic
inverter (rev-8 reference), F1(ε known), F1(ε estimated), F2-MAP, F2-sampled,
frozen direct CNN (rev-8 checkpoint), 5-statistic GBM, stats+CNN stack} ×
axes: **bit-flip noise** (denser grid than rev 8, range 0–20%), **masking**
(0–90%), **IC density** (as rev 8), plus the two axes rev 8 skipped:
**state-label noise** (global 0↔1 polarity flip applied to a random subset of
diagrams — tests reliance on polarity conventions) and **unknown radius** (the
estimator must select r ∈ {1, 2, 3} by a fixed consistency score before
inferring; selection rule fixed in code before measurement). The CNN-family
estimators appear only on axes preserving their input geometry (as rev 8).
Per cell: coverage / per-bit accuracy, exact-reconstruction rate, per-target
and median R² with rule-bootstrap CIs. **Verdict rules per cell region** (the
rev-8 rules, reused): superiority = ΔR² ≥ 0.10 with 95% CI excluding 0; TOST
equivalence at δ=0.05 (sensitivity 0.02/0.10); otherwise inconclusive. The
headline figure reports, per axis, **which estimator class is best** with its
verdict against the runner-up — a "who wins where" map, not a single ordering.
Rule panel and RNG offsets: the rev-8 identifiability panel (80 held-out
range-2 rules, fixed seed) is the primary panel; ECA is the replication panel.

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
