# Response to the referee (second round)

We thank the referee for a second exceptionally careful report. Its two central
technical points — that our narrative contradicted our own tables, and that the
reliability ceiling we cited is not the correct benchmark for an
independent-simulation estimator — were both correct, and both are now fixed at
the root rather than papered over. The manuscript has been rewritten around the
spine the referee identified as the defensible one: *a single space–time diagram
identifies the local rule under the matched observation model, and
reconstruct-and-simulate is then simulation-limited-optimal*. The title is now
"Rule reconstruction from a single space–time diagram yields simulation-limited
prediction of the finite-horizon damage response of cellular automata." All new
decision and reporting rules were committed numbers-free before measurement
(repository revision 8); "C1–C8" below name them.

---

## 1. The central narrative is internally inconsistent

**Agreed, and retired (C1).** "Never beats," "three tiers, one ordering,"
"dominates deep networks," and "compute the cheap features and skip the network"
are gone from the title, abstract, headings, captions and Discussion. The
CNN-vs-five-statistic comparison is now reported per target with paired CIs and
the registered verdict labels, and the honest summary is the referee's: **no
stable ordering** — the CNN is ahead on survival (Δ = +0.08, CI [+0.00, +0.20],
below the superiority margin), the baseline is superior on cone fill
(Δ = −0.21), fraction and rate are inconclusive at δ = 0.05. The stacking result
is promoted, not minimized: the CNN adds large, significant survival information
(+0.32, raising the stacked model from 0.56 to 0.88), and the manuscript now
names the statistics+CNN hybrid as the natural practical choice for
survival-like targets where rule reconstruction is unavailable (Secs. IV.B–C,
Discussion). The recommendation is stated conditionally on the observation
model, never as "skip the network."

## 2. The reliability ceiling is not the correct ceiling

**Agreed — this was our most consequential error, and fixing it made the result
stronger (C2).** The manuscript now distinguishes three quantities, each with
rule-bootstrap CIs (Sec. II.C): (1) latent-target reliability ICC; (2)
**empirical independent-replicate agreement** (the referee's 2·ICC−1; we verify
the algebraic prediction empirically — they match to four decimals); (3) a
**large-simulation reference** at 16× the Monte-Carlo budget. The mechanistic
estimator is judged against (2), the benchmark appropriate to a
fresh-simulation estimator, and sits *at* it on every target in both spaces
(e.g. ECA survival 0.985 vs 0.987 [0.978, 0.992]; radius-two cone fill 0.985 vs
0.959 [0.900, 0.987]). Scored against the near-noise-free reference (3), the
same predictions rise to the ICC ceiling (ECA survival 0.9943 vs ICC 0.9936;
radius-two 0.9877 vs 0.987) — the referee's diagnosis was exactly right: the
apparent shortfall was the comparison target's noise. "Reaches the reliability
ceiling" has been replaced throughout; survival's heteroscedasticity is noted
and all reliability intervals are bootstrap-based rather than Gaussian.

## 3. The mechanistic estimator's privileged assumptions and completion prior

**Agreed; both are now explicit (C3).** The estimator is introduced as
**matched-model system identification**, with the full assumption list
(deterministic, synchronous, binary, fully observed, noiseless, spatially
uniform, known radius) stated in the Methods and flagged in the abstract's first
claims. "Parameter-free" is retired. The default-zero completion is exposed as a
prior and tested: coverage is reported per rule space (ECA 18/18 fully covered;
radius-two 156/160, the four exceptions missing one entry each), the
default-0/default-1/empirical-prior completions move the radius-two median R²
by <0.001, and a **posterior-averaged variant** (exact enumeration of the 2^k
completions for small k, sampling otherwise) propagates table uncertainty into
predictive intervals — available precisely where reconstruction fails.

**Identifiability curve → phase diagram: done (C4).** This was the referee's
most valuable suggestion and is now a headline figure (Fig. 2). On the
radius-two held-out rules we sweep observation length, bit-flip noise, random
masking, and IC density, reporting coverage, exact-reconstruction rate, and the
median R² of the mechanistic inverter, the five statistics, and the frozen CNN
(on axes preserving its input geometry). The result quantifies the referee's
intuition: reconstruction is exact from as few as 4 observed rows when clean,
but collapses at ~2–5% observation noise and ~40% masking, where the frozen CNN
degrades more gracefully and *overtakes* the inverter — the regime where direct
amortization has a rationale, now delineated rather than asserted away. We did
not sweep IC correlation length, label noise or unknown radius this round;
the figure is labelled exploratory and those axes are named as extensions.

## 4. The paper does not "prove" why the CNN fails

**Agreed; language corrected.** "Prove(s) the mechanism" is gone; the probes are
presented as establishing **accessibility, not causal use** (Sec. IV.D states
this explicitly), and "any statistic that is a smooth function of the rule" has
been deleted — the argument now rests only on the fact the referee endorsed:
once the exact rule is known, the finite-horizon target can be directly
simulated. The rule-scrubbing, rule-provision, and learned rule-reader→simulator
interventions are named in the Discussion as the tests that would establish
causality; we have not run them and do not claim their conclusions.

## 5. The probe results need definition

**Provided (Sec. IV.D).** The two probe tasks are now specified separately:
*identity probes* (88/800 classes; stratified split over diagrams, so train and
test diagrams are disjoint but rule classes are shared — within-rule decoding
across new diagrams; majority baseline ≈ 0.011/0.001) and *truth-table-bit
probes* (leave-rules-out GroupKFold, so test rules are never seen — out-of-rule
transfer; chance 0.5; bits evaluated separately and averaged). Both are linear
(logistic) probes on the bottleneck vs the five statistics, with the
deterministic tabulation result reported alongside as the raw-diagram
reference. The manuscript no longer speaks of classifying "unseen identities."

## 6. The statistical analysis is incomplete

**Completed (C5).** Table III now gives the full radius-two per-target results:
held-out count, each method's R² with rule-bootstrap 95% CIs, the CNN's
mean ± s.d. over all five seeds (no more single "reference seed"), with paired
ΔR², CIs and verdicts in Sec. IV.B and the replicate-agreement and ICC columns
alongside. Split uncertainty beyond the registered split is quantified for the
deterministic methods — **leave-one-orbit-out over all 88 ECA orbits** and **20
repeated radius-two outer splits** (survival 0.76 with 5th–95th range
0.56–0.84; fill 0.68, 0.55–0.75) — and the mechanistic estimator is
split-invariant by construction (no trained parameters). We state explicitly
that CNN retraining across splits was not performed and that its seed spread
does not capture split variance. TOST margins are reported at δ ∈ {0.02, 0.05,
0.10} (verdict changes listed in the appendix; no superiority verdict moves).
"Tie"/"equivalent" now appear only where TOST passes; the spatial-map result is
relabelled **inconclusive** (see §8).

## 7. One constrained CNN does not represent deep networks

**Claims narrowed (the referee's option 1).** Every neural claim is scoped to
"this architecture under this training budget" (Sec. III, Discussion), the full
architecture (layer table, 31,524 parameters, receptive field, optimizer,
schedule, augmentations, training cost) is in the supplement, and the
Discussion names the missing comparators — above all a learned rule-table
predictor feeding a simulator — as open questions rather than settled ones. We
did not run a model suite; with the narrowed claims none of our conclusions
require one. The identifiability diagram additionally identifies the regimes
where such learned system identifiers would be the interesting competitors.

## 8. The spatial-map conclusion is too strong

**Corrected (C7).** The result is now labelled by the registered framework:
**inconclusive** (Δ = +0.047, 95% CI [−0.002, +0.102], 90% CI [+0.005, +0.092]
— neither superiority nor equivalence), described as "a small, statistically
unresolved edge for the learned map." "Training-free" is corrected to "no
additional training at deployment." The protocol details the referee asked for
are in the supplement: 16-rule panel, pairs with rate gap ≥ 0.25, 8 ICs per
pair, half/half mosaics, validation/test split of pairs (window selected once
on validation, per-pair best window reported only as a labelled oracle
sensitivity), independent random streams for the local ground truth, and —
importantly — the **unit of resampling is the composed system** (per-pair
mean-over-IC Spearman values are bootstrapped; columns never enter the
inference as independent observations). Extending the mechanistic contribution
to a local system-identification map is named as future work; we agree it is
the on-thesis extension.

## 9. The landscape should be a damage-signature landscape

**Renamed and validated with confusion matrices (C6).** Title, abstract,
Discussion and the figure caption now say **damage-signature landscape**, and
the prevalence is stated as "7.8% (Wilson CI [6.9, 8.8]%) satisfying the
registered finite-horizon damage-signature criterion under the stated sampling
distribution." The ECA validation is now a full confusion matrix against the
literature class-IV ground truth: the signature has sensitivity 1.0,
specificity 0.988, precision 2/3 (its one false positive being the documented
borderline rule 106), balanced accuracy 0.994 — raw agreement is no longer the
headline. The same reporting shows the *independent detector* is the weak
instrument (sensitivity 0.5 — it misses rule 54's light-speed ether — precision
0.17), which is exactly why we do not promote the radius-two band to a glider
region: there the detector agrees with the signature at balanced accuracy 0.39
(precision 0.05). The curated long-horizon radius-two validation the referee
sketches is the right way to earn a complexity claim; we have not done it and
make no such claim.

## 10. Pre-registration is unauditable during review

**De-emphasized and labelled, with one candid limitation.** The paper no longer
leans on "pre-registered" as its warrant: the word is used sparingly, and
Appendix A now **labels every analysis** as registered / post-hoc confirmatory /
exploratory, including the honest placement of this revision's own additions
(the replicate-agreement correction and reference simulation: post-hoc
confirmatory; the identifiability diagram and Pareto curve: exploratory). The
one deviation from the original registration (the target-stream RNG fix)
remains disclosed with its measured effect. On review-time access: we have kept
the repository private during review to protect anonymity, and we acknowledge
plainly that this limits auditability; the complete timestamped history
(criteria revisions, code, cached predictions and targets) is released with the
article, and we are glad to provide the editor an anonymized archive on
request.

## 11. Report the compute trade-off

**Done (C8; Sec. IV.F).** Per-diagram latency: mechanistic 283 ms at the
production 256-pair budget (single CPU core, embarrassingly parallel) vs 2.2 ms
for a CNN forward pass and 1.4 ms for the five statistics; one-time costs
≈22 min training per CNN seed vs 15 s for the boosted baseline; break-even
≈4,700 queries. The accuracy-vs-budget curve is the informative part: at a
16-pair budget (17 ms) the mechanistic median R² is 0.924 — above both direct
estimators at any cost — so under the matched observation model the estimator
is simultaneously the most accurate at every budget we measured. The practical
recommendation now carries this price tag explicitly.

## 12. Missing methodological detail

**Supplement added (Appendix B).** It contains every item on the referee's
list: diagrams per rule per split and stream independence (no shared random
numbers across methods); the full CNN layer table with parameter count and
receptive field; optimizer, schedule, batch size, augmentations, and the
absence of early stopping; ridge/GBM settings and the baseline-of-record rule;
the exact split protocol including the force-held complex panel; the exact
target formulas including perturbation-cell selection and the
no-surviving-damage convention; the panel-overlap disclosure (the 800-rule
estimator panel is a subset of the 3,000-rule landscape sample); the detector
definition and thresholds; and the composed-system construction.

---

## Editorial points

1. **Slash notation**: removed; every paired value names its rule space.
2. **Table I caption**: rewritten; it states the aggregation rule, points to
   the per-target tables, and makes no ordering claim about the CNN and the
   baseline.
3. **Reference-seed CNN**: all tables report mean ± s.d. over the five seeds.
4. **Stacking table**: now carries 95% CIs and the full stacked-model R²
   (base → stacked) alongside each increment.
5. **"Deterministic given the protocol"**: corrected to "reproducible under a
   fixed seed but Monte-Carlo limited."
6. **"Smooth function of the rule"**: deleted (no smoothness claim is needed
   or made).
7. **Companion sensitivity analysis**: the free-floating reference is removed;
   protocol dependence is shown directly in Fig. 2(d) and the released code
   contains the full protocol sweep.
8. **Assumptions visible early**: the observation model (fully observed,
   noiseless, deterministic, binary, known radius) appears in the abstract and
   in Methods before any result.
9. **Vispoel citations**: completed with volume, pages and DOIs
   (Chaos, Solitons & Fractals **184**, 114989, 2024,
   doi:10.1016/j.chaos.2024.114989; Physica D **432**, 133074, 2022,
   doi:10.1016/j.physd.2021.133074).
10. **Figure 1**: caption rewritten — sample size and Wilson CI stated, panel
    overlap disclosed, embedded anchor rules identified, and an explicit
    statement that the red band is not an independently validated glider
    region.
11. **Verdict language**: "no evidence of superiority," "practical
    equivalence," and "inconclusive" are used strictly per the registered
    definitions everywhere (including the spatial map, which is inconclusive).

---

## Summary of what is new in this revision

C2 corrected reliability benchmarks (ICC vs replicate agreement vs
large-simulation reference, with CIs); C3 coverage/completion sensitivity and a
posterior-averaged uncertainty-aware mechanistic variant; C4 the
identifiability phase diagram (new Fig. 2); C5 complete per-target tables for
both spaces with seed spreads, repeated-split/leave-one-orbit-out uncertainty,
and TOST margin sensitivity; C6 confusion-matrix validation and the
damage-signature reframing of the landscape; C7 the corrected (inconclusive)
spatial-map verdict with full protocol disclosure; C8 the accuracy–compute
Pareto analysis. The manuscript was rewritten around rule identifiability and
simulation-limited prediction, with every neural claim scoped to the tested
architecture and every analysis labelled by its registration status.

---

# Round-3 supplement (prepared in advance; folded into the concern structure)

Everything below was produced after the round-2 revision was frozen, on a
separate branch so the submitted PDF is untouched; each block is filed under
the round-2 concern it continues. Decision rules were committed numbers-free
before each measurement (repository revisions 9 and 10; the full
registration-history extract is Appendix L1 of this letter).

## Cross-reference: concern → response → manuscript location

| Concern | Round-2 response | Round-3 continuation | Manuscript |
|---|---|---|---|
| 1 narrative consistency | §1 (retired, C1) | — | §IV.A–B, Table I |
| 2 reliability ceiling | §2 (C2) | — | §II.C |
| 3 assumptions + identifiability | §3 (C3, C4) | frontier estimators + the two axes deferred at round 2 (→ §3-bis) | §IV.D–E, Figs. 2–3 |
| 4 mechanism not proven | §4 | — | §IV.D |
| 5 probe definitions | §5 | — | §IV.D |
| 6 statistics incomplete | §6 (C5) | — | Tables II–III |
| 7 one constrained CNN | §7 | learned rule-reader + two fairness controls (→ §7-bis) | §III(iii), §IV.E |
| 8 spatial map | §8 (C7) | — | §IV.G |
| 9 landscape naming | §9 (C6) | — | §IV.G, Fig. 4 |
| 10 registration auditability | §10 | corrected access rationale + attached history (→ §10-bis) | App. A |
| 11 compute | §11 (C8) | — | §IV.F |
| 12 methods detail | §12 | — | App. B |

## §3-bis. The identifiability frontier, completed (continues concern 3)

Round 2 deferred two axes ("we did not sweep … label noise or unknown radius
this round"). Both are now measured, together with the estimators the phase
diagram called for, pre-registered numbers-free as revision 9 with three
hypotheses whose verdicts are reported as earned (one split, one refuted in
half — manuscript Appendix A enumerates them):

- **Bayesian rule-posterior (no training)**: restores identification across
  the intermediate band — masking tolerance extended from ~25% to 50% of
  cells, IC-density extremes rescued, exact polarity invariance — and is best
  of all methods up to ~3% bit-flip noise. Self-estimated noise rate matches
  the supplied-rate variant throughout.
- **Label-polarity axis**: the read-then-simulate family is exactly
  invariant; the frozen CNN and the stack degrade.
- **Unknown-radius axis**: smallest-consistent selection costs ~0.12 median
  R² on clean diagrams and degrades under noise — the known-radius
  assumption now carries a measured price.
- The registered calibration of the posterior's 1σ predictive intervals is
  reported per cell (manuscript §IV.E), completing the one reporting item
  that was outstanding from the rev-9 registration.

## §7-bis. The learned rule-reader and two fairness controls (continues concern 7)

The referee three times asked what a *learned* rule-reader would do where
exact inversion fails. We benchmarked it (registered as exploratory, gated
single-seed training): its MAP table fails everywhere (per-bit accuracy 0.73
never yields an exact table, and one mostly-right table is a badly wrong
dynamical system), while *sampling* its per-bit posterior is the only
estimator that does not collapse beyond 5% noise (median R² ≈ 0 out to 20%,
all others −1 to −5.6). It moves the frontier without restoring
identification; under masking it adds nothing.

Because the reader is degradation-trained while the direct CNN of the
submitted manuscript is clean-trained and architecturally constrained, we
also ran the two symmetric controls this comparison owes the reader of the
degraded-regime guidance (pre-registered as revision 10 before measurement):
**(C-i)** the same direct CNN retrained with the reader's registered
degradation augmentation, and **(C-ii)** an unconstrained same-budget
`resnet18` CNN — the architecture the anti-shortcut constraint was designed
against, whose motivating claim round 2 retired.

The controls changed one conclusion and confirmed the other, and we report
both plainly. **Changed:** the noise "dead zone" was an adaptation artifact,
not an estimator-family boundary — the degradation-trained direct CNN holds
median R² 0.51–0.62 across 3–15% noise, where no previously tested estimator
exceeded 0.17; our earlier statement that learned system identification is
the only class retaining signal there is withdrawn and replaced by the
measured one (what decides the noise band is training for the corruption,
at a ~0.14 clean-diagram cost). **Confirmed:** at every grid cell where the
rule is recoverable (per-bit ≥ 0.95), the best read-then-simulate estimator
remains unbeaten with both controls included — zero violations of the
registered hypothesis — and the unconstrained 11.2M-parameter network is no
better on clean diagrams than the 31k constrained one (0.55 vs 0.65) while
degrading faster under noise, so the matched-regime negative result is not
an artifact of the constraint. The Bayesian posterior still owns the
intermediate masking and density band against both controls. Manuscript:
Sec. IV E(iii), Table V, Discussion; measured record: RESULTS.md rev-10
section with artifacts under `runs/m4_range2_degaug/`,
`runs/m4_range2_resnet/`, and `runs/m4_range2/frontier_grid_controls/`.

## §10-bis. Registration auditability, corrected (continues concern 10)

Two updates. First, our round-2 rationale for the private repository
("to protect anonymity") was wrong and we withdraw it: the byline is signed
and the manuscript cites our own group, so anonymity was never the
constraint. The repository is private because it is the submission history
of an unpublished article; that is a choice, and it does limit auditability
during review. Second, instead of offering an archive "on request", we now
attach the registration evidence directly: Appendix L1 reproduces the
complete commit history of the criteria file (revision, timestamp, subject),
so the numbers-free-before-measurement ordering for every load-bearing
revision is checkable from this letter alone, and the full timestamped
repository is released with the article.

One honest caveat belongs in this list: for criterion 7 (the nuCA
validation, a by-product) the registration and the measurement were
committed together, so for that one criterion the ordering is attested
rather than git-auditable. Every criterion the paper's claims rest on
(revisions 7–10) has the committed numbers-free ordering shown in
Appendix L1.

## Correction disclosed (found by internal audit, fixed at the source)

An internal pre-submission audit found that one manuscript number and six
cells of the internal measured record still carried values from the
discarded wrong-checkpoint frontier run that RESULTS.md itself documents
(the run was re-measured with the canonical checkpoint before any rev-9
number was reported, but the in-session reproduction check covered the
shared columns, not those six cells). The manuscript value "frozen CNN to
−1.1" is corrected to the canonical −0.93; no bolded comparison, verdict, or
conclusion changes. A programmatic audit
(`scripts/audit_manuscript_numbers.py`) now re-derives every §IV.E prose and
table number from the released artifact and fails on mismatch; it runs clean
on the revised manuscript.

## Appendix L1 — registration-history extract (EVALUATION_CRITERIA.md)

Complete `git log --follow` of the criteria file (newest first). Each
revision commit is numbers-free; measurements follow in separate commits.

| Commit | Timestamp | Subject |
|---|---|---|
| c16cc2b | 2026-07-05 20:26 | Pre-register round-3 fairness controls + reporting completions (rev 10) |
| 8f5cb56 | 2026-07-05 01:43 | Pre-register identifiability-frontier controls (rev 9) |
| 75e1d42 | 2026-07-04 20:40 | Pre-register round-2 review-response controls (rev 8) |
| a809b2a | 2026-07-04 14:27 | Pre-registration rev 7: review-response controls (numbers-free) |
| 516866b | 2026-07-04 01:21 | Pre-register rev 6: baseline & robustness controls (S1–S3), numbers-free |
| e2dd185 | 2026-07-04 00:15 | Pre-register M4 (criterion 9) + range-2 harness, no measured numbers |
| ead0fcf | 2026-07-03 18:58 | Pre-register criterion 8: stripe resolution (8a) + alloy transfer (8b) |
| c2b99cb | 2026-07-03 01:52 | nuCA validation: criterion 7 pre-registered, measured, and passed (registration and measurement in one commit — the caveat disclosed in §10-bis) |
| a7789b4 | 2026-07-02 11:21 | (pre-criteria bootstrap) |

First measurement commits following each load-bearing revision: rev 8 →
fa994da (2026-07-05 00:52); rev 9 → 111e3df (2026-07-05 10:00) and 0f8e691
(2026-07-05 14:04); rev 10 → the control-training commits recorded in the
repository history accompanying this revision.

---

# Response to the third review (round 4)

We thank the reviewer for an unusually precise report. Its centre of gravity
— specification and statistical rigour — matched an uncomfortable fact: much
of what the report asked for already existed in our code and released
artifacts but had never been surfaced in the manuscript. The revision
therefore has two kinds of content: exposition that closes that gap
(evaluation-protocol box, decoder pseudocode, honest renaming of the
"Bayesian posterior"), and **seven new pre-registered analyses**
(EVALUATION_CRITERIA.md revision 11, committed numbers-free before any
measurement; git-auditable) that answer the report's empirical questions,
including both of its replication demands. Three of the reviewer's concerns
produced results that *changed the manuscript's claims* (C5's equivalence
test replaced "statistically indistinguishable"; C6's seed replication
failed its registered stability rule and downgraded the noise-band level to
a per-seed range; C7's deployment test showed
the survival complementarity does not deploy) — we consider all three
improvements. Where we push back (parts of C6 and C8) we say so explicitly
and give the reason.

## C1 — "no direct method can beat reading the rule" is too strong

**Adopted, and the fix sharpened the thesis.** The reviewer is right: at a
fixed finite Monte-Carlo budget, a perfect latent-mean predictor could
exceed a fresh simulation on the noisy score. The revision replaces the
universal claim with the precise one, in the abstract, Introduction,
Sec. II.C, Sec. IV.A and the Discussion: identification yields a
**budget-indexed family** of estimators; at matched budget it attains the
independent-replicate benchmark by construction, with budget it climbs to
the latent ceiling, and the entire headroom available to any direct
estimator over the matched-budget member is exactly 1 − ICC (measured:
≤ 0.013–0.026 on the noisiest targets) — which identification also claims by
simulating more. "Can never beat it" became "can win only on cost, with
simulation budget now explicitly part of the cost, or on robustness."

We also measured the reviewer's scenario rather than argue it away
(**M1**, registered; answers Q8): every estimator was rescored against the
near-noise-free reference targets next to the cached ones. The mechanistic
estimator rises to the ICC ceiling (0.991 → 0.995); the CNN moves by
−0.0003, the boosted baseline by +0.007. The tested direct estimators are
not latent-mean predictors being unfairly scored against noise — their
shortfall is estimator error. All four of the reviewer's line-edit proposals
were adopted in substance (Sec. II.C item 2 verbatim in spirit).

## C2 — prediction unit and R² computation under-specified

**Adopted.** Appendix B now opens with an "Evaluation protocol (the unit
behind every number)" box answering the six requested items: a test instance
is a (rule, diagram) pair; direct estimators predict per diagram and are
averaged within rule before scoring; the mechanistic decoder uses the
rule's *first* diagram only (an asymmetry that *favours* the direct
estimators, now stated); every R² is the unfitted 1 − SS_res/SS_tot at the
rule level with the held-out panel mean in the denominator; bootstrap
resamples rules; the four-target median is defined. The registered
**M4** audit makes the "single diagram" claim auditable at both units: over
all 10,240 radius-two held-out diagrams the per-diagram exact-reconstruction
rate is 0.990 (median coverage 1.0); on all 4,608 ECA diagrams it is 1.000.
Answers Q1/Q2.

## C3 — the radius-two panel is enriched, not representative

**Adopted.** The panel is now called what it is — an *enriched evaluation
panel* (all 57 signature-complex rules force-held; 35.6% of the panel vs
7.1% of the sampling universe) — in Sec. IV.A, Table I and Table III. The
registered **M3** decomposition reports the forced and stratified-random
subpanels separately plus a post-stratified estimate at the universe
prevalence, now rows of Table I. The result is that our original enrichment
was *conservative*: representative reweighting raises the mechanistic median
(0.991 → 0.994) and lowers the CNN's (0.859 → 0.830), *widening* the gap.
To Q3 we answer plainly, in the paper: signature membership was computed by
the registered criterion-9 thresholds **from the same seed-0 target cache
later used for evaluation labels**; the forced rules were never trained on,
and the random-subpanel numbers are unaffected by the criterion entirely.
The sampling measure (Q4) is now stated exactly: uniform over raw encodings,
folded to orbit representatives and deduplicated — orbit-size-biased, the
natural random-rule measure — and all prevalences are under it.

## C4 — degraded reconstruction methods under-specified

**Adopted, including the honest rename.** The reviewer guessed our
implementation exactly. The method is now introduced as an *approximate
Bayesian rule decoder* whose model is an **entrywise pseudo-posterior**:
output-cell flips only, independent per-entry Binomial likelihood, Bernoulli
prior at the observed marginal, ε supplied or matched to a fixed ten-point
self-consistency grid. Input-side corruption is explicitly *not* modelled
and the text says so. New Appendix C gives pseudocode for tabulation (with
the majority-vote conflict policy, ties to 0, and the t=0/masking
semantics — a transition is dropped if its output cell or any input cell is
masked), the pseudo-posterior, ε estimation, and radius selection, plus a
worked example with a corrupted transition. Answers Q5/Q6.

One connection we owe to this concern: the rev-10 calibration measurement
turns out to be the *empirical price* of the pseudo-likelihood. Coverage
holds at or above nominal across the masking band (masking removes
transitions cleanly, so the independence approximation stays benign) and
degrades along the noise axis (input-side flips are exactly what the
likelihood ignores). The manuscript now states this. **Partial push-back:**
we did not add further sensitivity analyses over alternative likelihoods —
the calibration measurement already quantifies the approximation's
consequences per axis, per cell, against the targets the estimator is
scored on; a better-specified decoder is future work the Discussion now
names, not a claim this paper makes.

## C5 — "statistically indistinguishable" is not established

**Adopted; the analysis was run and the wording changed by its result.**
The registered **M2** paired analysis (rev. 11; answers Q7) regenerates the
K = 20 replicate matrix bit-exactly from its registered seeds on the exact
held-out panels and rule-bootstraps the *same* resamples through
R²_mechanistic and R²_replicate, both against the same cached targets, with
a pre-registered margin max(0.01, 1 − ICC_t). Six of eight target–panel
comparisons are formally equivalent (radius-two survival: diff +0.0007,
CI [−0.008, +0.009], margin ±0.013). Two fail — for instructive reasons the
paper now prints: ECA survival's CI (±0.015) exceeds its ±0.010 margin
because 18 rules bound the resolution (point difference +0.0003), and
radius-two cone fill (+0.006, CI [−0.009, +0.022], margin ±0.020) overshoots
only on the side where the mechanistic estimator *beats* the replicate.
"Statistically indistinguishable" was removed and replaced by the per-target
statement; the lead paragraph now says "as accurate as an independent
re-measurement". Sec. II.C additionally states that the agreement benchmark
is *measured* as the mean pairwise R² over replicates (the 2·ICC−1 identity
is a cross-check only), that ICC(1) is used descriptively, and that all
intervals are rule bootstraps — the heteroscedasticity treatment the
reviewer asked about, which was in the code all along.

## C6 — split and training uncertainty of the neural comparisons

**Partially adopted; push-back on the remainder, with reasons — and the
adopted part vindicated the concern.** Adopted:
(i) the load-bearing single-seed result — the degradation-trained CNN that
owns the noise band — was retrained under two additional seeds against a
registered stability rule (M5: the band claim keeps its wording only if
every new seed's cell medians fall inside the seed-0 cells' 95% CIs). **The
rule failed:** seed 2 reproduces seed 0 (band 0.49–0.56, inside every CI),
but seed 1 trains to a much weaker model (0.24–0.33) despite identical loss
convergence — late-epoch validation medians swing by ~±0.2 under
augmentation, implicating final-epoch selection variance. The manuscript
now reports the band as a per-seed range (0.24–0.62; two of three seeds
0.49–0.62), restates the robustness tax as 0.14–0.37, and re-words Table V's
20% row, where reliability itself proved seed-dependent (two seeds clear
zero at 0.31/0.43; seed 0 does not). What is seed-stable — and is now the
stated claim — is the family-level ordering: every seed's point median
exceeds every read-then-simulate estimator at every cell from 5% to 20%
noise. The reviewer's single-seed concern was correct, and pricing it
improved the paper.
(ii) Single-seed and single-split
qualifiers now appear at the claims themselves (Sec. IV.F(iii), Table V,
Table I/III captions state which uncertainty source each interval covers).

Push-back: we did not retrain the full estimator zoo across repeated outer
rule splits. Proportionality is the reason. The paper's central claim rests
on the mechanistic estimator — no training stochasticity, split uncertainty
already quantified by leave-one-orbit-out over all 88 ECA orbits and 20
repeated radius-two outer splits (Appendix B) — and on gaps of 0.13–0.16
median R² against direct estimators whose five-seed spread is ±0.014. The
close neural comparisons, where split/seed variance could plausibly change a
verdict, are already labelled "no stable ordering" and inconclusive, and the
manuscript states explicitly that the CNN was not retrained across splits.
Retraining every network over multiple splits would sharpen error bars on
comparisons whose verdicts we already refuse to over-read. If the editor
regards this as essential we will run it, but we believe the registered
disclosure is the honest, proportionate treatment. (Q10 is answered for the
frontier by M5 + M7 below.)

## C7 — the stacking result is a diagnostic, not a deployable stack

**Adopted — and the reviewer's distinction turned out to be empirically
real.** Table IV is now titled a *cross-fitted complementarity diagnostic,
computed within the held-out panel*, with folds, grouping, and in-fold
standardization stated (rows are rules; the CNN predictions use no held-out
labels). The registered **M6** deployment-style stack (ridge over
[statistics + CNN predictions], fit on training rules only, applied once to
the untouched panel; answers Q9) reaches an overall median of 0.88 but
realizes essentially none of the survival increment: +0.001 over the CNN
alone (n.s.), against the diagnostic's +0.32. Fraction (+0.02) and rate
(+0.03) do transfer. The manuscript now says both: the network *carries*
survival information the statistics miss, and a practitioner cannot yet buy
it with a linear meta-model. We kept the complementarity claim scoped to
exactly that.

## C8 — Table V over-generalizes from an exploratory 80-rule panel

**Adopted in labeling and — for the axis that carries the paper's headline
reversal — in replication; push-back on replicating the full grid.**
Table V is now titled *exploratory guidance, bounded to the evaluated
protocol* with the extrapolation warning the reviewer proposed ("no tested
estimator" phrasing included). The registered **M7** replication re-simulated
the entire noise axis on the complementary 80 held-out rules at identical
budgets. The family structure replicates (read family early; the
degradation-trained network strongest or tied from 3%, point-strongest from
7.5%; nothing reliable at 20%), and no cell winner is re-stated under the
registered rule. The replication also *improved* the guidance: cell levels
shift with the panel (degradation-trained band 0.35–0.71 vs 0.51–0.62), and
the pseudo-posterior's collapse point moves (it holds to 7.5% on the
complement vs 3% canonically), so the posterior-to-network crossover is now
stated as a panel-dependent band, ~3–7.5%, in Sec. IV.F and Table V.
Push-back: we did not replicate the masking/density/label/radius axes —
their verdicts are separated by margins of 0.3–1.5 median R² (vs the noise
axis's close races), and the winner-flip risk the reviewer worries about is
correspondingly remote; the cost is another ~4 axes × 80 rules of
simulation for verdicts nobody contests.

## Minor concerns (all fourteen adopted)

1. Exact target formulas, flip-centred coordinates, single-cell extent, and
   why conditional denominators are positive: Appendix B "Targets".
2. "Finite-horizon proxy for the sign of the damage-based maximal Lyapunov
   exponent" — reworded as proposed (Sec. II.B).
3. R² convention: protocol box, item (3).
4. ICC under heteroscedasticity: Sec. II.C (descriptive use; empirical
   pairwise agreement is the measured benchmark; bootstrap intervals).
5. Sampling measure stated exactly (Appendix B "Data"; orbit-size-biased).
6. Every interval/± now names its uncertainty source (captions, Tables I–III).
7. Compute vignette: same-core CPU timings for both methods added (the CNN
   is 1.0 ms on the same core that gives the mechanistic estimator 283 ms;
   the GPU number is retained as deployment context); framed explicitly as
   a vignette, not a hardware-neutral study.
8. Radius-selection procedure: candidates, criterion, margin, tie-break —
   Appendix C, A4.
9. Sec. IV.H renamed "Descriptive by-products, with independent ground-truth
   evaluation".
10. "Signature-complex" defined as a criterion label at first use.
11. Rhetorical absolutes tightened ("almost always possible", "textbook
    instance", "nothing direct beats", "unambiguous", "none reliable").
    A subsequent global condensation pass additionally shortened the
    manuscript from 15 to 14 pages (~700 words): duplicated expositions
    (the budget-indexed-family argument, the coverage numbers, the frontier
    guidance, the hypothesis verdicts) are now stated once with pointers,
    and figure/table captions no longer repeat the adjacent text. No
    registered number, verdict, margin, or disclosure changed; every
    substantive cut is logged in `manuscript/trimmed_material.md` in the
    released repository.
12. Structured prior-work table added (new Appendix D), with three
    literature additions found in a fresh search (Sun–Rosin–Martin 2011;
    Elser 2021; Mordvintsev et al. 2020). We found no prior work measuring
    the benchmark consequence of identifiability for perturbation-defined
    behaviour targets, including in 2024–2026 preprints on learned CA rule
    inference; the claim is now scoped by the table rather than by a
    narrative paragraph.
13. Undecidability sentence scoped to the formalization (Sec. I).
14. Data availability: environment pins, reproduction entry points
    (audit script + figure script), and commit-hash language added; the
    archival DOI is minted at acceptance.

Citation checks requested: [rollier2024cnn] wording narrowed to the actual
task ("elementary-rule label from a single clean diagram, 99.9% test
accuracy"); [culikyu1988] scoped (minor 13); [mcgreivy2024] kept — its claim
in our text ("comparisons ... documented to be frequently absent or weak")
matches the source's findings.

## Answers to the ten questions

| Q | Answer (and where it now lives) |
|---|---|
| Q1 | One evaluation observation = one (rule, diagram) pair; direct estimators average predictions over the rule's 64/256 diagrams, the mechanistic decoder uses the first diagram; coverage is per rule in the main text and per diagram in the M4 audit. (App. B protocol box) |
| Q2 | R² after within-rule averaging, over rules, unfitted, panel-mean denominator; bootstrap resamples rules. (App. B) |
| Q3 | The 57 were selected by the registered criterion-9 thresholds applied to the seed-0 target cache — the same cache that supplies evaluation labels; disclosed in Sec. IV.A; forced rules never trained on; random-subpanel results independent of the criterion. |
| Q4 | Uniform over raw encodings → fold → dedup: orbit-size-biased measure; prevalences under it. (App. B) |
| Q5 | Majority vote, ties to 0, inconsistency flag; flips i.i.d. over all cells incl. t=0; masking drops transitions touching any masked input/output cell. (App. C) |
| Q6 | Entrywise pseudo-likelihood on output flips only, now named as such; prior = observed marginal; ε grid fixed (10 points); 8 posterior samples simulated and averaged. (Sec. IV.F(i), App. C) |
| Q7 | Yes — M2 paired equivalence with pre-registered margins; 6/8 equivalent, wording changed accordingly. (Sec. IV.A) |
| Q8 | Yes — M1: direct estimators rescored against the 4096-pair reference move by ≤0.007; they are not being under-credited by label noise. (Sec. IV.A) |
| Q9 | Folds are rule-level; meta-model fit strictly in-fold; 0.88 was the within-panel diagnostic value. The deployable stack (M6) also reaches 0.88 overall but +0.001 on survival — the diagnostic does not deploy, now stated. (Sec. IV.C) |
| Q10 | M7: full noise axis replicated on the complementary 80 rules (structure replicates; crossover restated as a band); M5: the degradation-trained control retrained under two more seeds against a registered stability rule. (Sec. IV.F(iii)) |

## Registration note

Revision 11 of EVALUATION_CRITERIA.md — defining M1–M7, the equivalence
margins, the M5 stability rule, and the M7 winner-re-statement rule — was
committed numbers-free before any of the measurements above, in the same
git-auditable pattern as revisions 2–10. The manuscript's Appendix A lists
all seven under post-hoc confirmatory (review-response) with their decision
rules.
