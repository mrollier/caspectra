# DECISIONS.md — executive-decision log

The one-page answer to "who decided what, when, and why" for this project.
Decisions are the **principal investigator's** (Michiel Rollier) unless noted;
each row cites where the full record lives. Measured outcomes live in
`RESULTS.md`; pre-registered rules in `EVALUATION_CRITERIA.md` (revision
changelogs at the top of that file); scientific scope constraints in
`FOUNDATIONS.md`. Newest first.

| date | decision | why | full record |
|---|---|---|---|
| 2026-07-05 | Real authors: M. Rollier + J. M. Baetens (Ghent University, DDAMM); merge `round2-chaos-revision` → `main` conditional on this documentation pass | Submission readiness; auditability for newcomers | this file; `manuscript/main.tex` |
| 2026-07-05 | Next work package = **identifiability frontier** (Bayesian rule-posterior + learned rule-reader→simulator where exact rule reading fails); results held as an **extension of the Chaos manuscript** for round 3, not a separate paper | It is the open question the manuscript's own Discussion poses; the referee requested the learned comparator three times | plan file; rev 9 (forthcoming) |
| 2026-07-04 | **Round-2 review decisions:** (a) full reframe to "rule reconstruction yields simulation-limited prediction" (drop "dominates / never beats / skip the network"); (b) neural claims narrowed to the tested CNN, **no** retraining or model zoo; (c) pre-registration de-emphasized, every analysis labelled registered / post-hoc-confirmatory / exploratory | Second referee showed the narrative contradicted our own tables, and that the ICC ceiling was the wrong benchmark (2·ICC−1 is correct for a fresh-simulation estimator) — both integrity-level | `EVALUATION_CRITERIA.md` rev 8 (commit 75e1d42); `manuscript/reviews/chaos_second_review.md`; `RESULTS.md` rev-8 section |
| 2026-07-04 | **Round-1 review decisions:** (a) full rigorous benchmark, not a rebuttal; (b) three-tier reframe around the mechanistic read-rule→simulate estimator; (c) repository stays private until acceptance; (d) skip unconstrained-CNN retraining, argue from stacking+probes | First referee (reject) demanded a transparent mechanistic baseline — building it produced the paper's positive result | `EVALUATION_CRITERIA.md` rev 7 (commit a809b2a); `manuscript/reviews/chaos_review.md`; `RESULTS.md` rev-7 section |
| 2026-07-04 | M4: extend to the radius-two space (2³²) with criterion 9 (complex-regime placement); Lyapunov/Vispoel invariants deferred | The ECA complex regime has only two members — the §6 placement caveat needed a populated regime to test | `EVALUATION_CRITERIA.md` rev 5; `RESULTS.md` M4 section; notebook 04 §10 |
| 2026-07-03 | Criterion 8 (stripe resolution + alloy transfer) pre-registered before measurement | The "pick 15×15 for spatial detail" guidance was unsupported; the depth-vs-resolution trade needed numbers on both sides | `EVALUATION_CRITERIA.md` rev 4 (commit ead0cf...); `RESULTS.md`; notebook 04 §§8–9 |
| 2026-07-03 | **BatchNorm is mandatory for regression encoders** (GroupNorm only for SSL); the shallow (15×15-map) variant certified alongside the 7×7 one | GroupNorm normalizes over whole-image statistics and destroys `predict_map` locality (rule-0 partner probe isolated the mechanism) | `RESULTS.md` 2026-07-03; `CLAUDE.md`; notebook 04 §7 |
| 2026-07-02 | Label spot-check closed by decision (LP labels transcribed from Li–Packard 1990 accepted) | Verification cost vs. benefit; provenance documented | `rule_labels_PROVENANCE.md` |
| 2026-07-02 | **Full mission reframe** after the commissioned literature review: goal = invariant-based taxonomy of (orbit, IC-measure, protocol) tuples + amortized, spatially-resolved invariant estimation. "SSL discovers the taxonomy" declared ill-posed; texture-BYOL frozen as the negative baseline; lever A (invariant-regression amortizer) primary with pre-registered kill criteria | Undecidability + measure-dependence make "the class of a rule" ill-posed; v1 measurements showed the SSL embedding encodes the rule as well as the class | `FOUNDATIONS.md`; `docs/2026-07-02_deep_research_report.md`; `SELF_CRITICISM.md` |
| 2026-07-01 | Success criterion moved from rule-probe suppression to the geometry/cluster level; larger rule space approved in principle | v1 showed any expressive encoder identifies rules from texture statistics alone (probe 0.967 through the anti-cheat architecture) | `EVALUATION_CRITERIA.md` rev 2; `RESULTS.md` v1 section; notebook 01 §9 |

## Where to read the story

- **New here? Read in this order:** `README.md` → notebook
  `05_reading_the_rule.ipynb` (the paper's result, narrated) → `DECISIONS.md`
  (this file) → `RESULTS.md` (every measured number) → the manuscript
  (`manuscript/main.tex` / `main.pdf`).
- Notebooks 01–03 are **historical (v1)**: the original SSL-taxonomy attempt and
  its honest post-mortem. Notebook 04 is the v2 "learn the physics" arc through
  M4. Notebook 05 covers the two review rounds and the final framing.
- The pre-registration discipline is auditable in git: each
  `EVALUATION_CRITERIA.md` revision is committed numbers-free *before* the
  measurements it governs (rev 2 … rev 8; rev 9 forthcoming for the
  identifiability-frontier work).
