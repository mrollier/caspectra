# Rebuttal Audit — `response_to_referees.md` vs the round-2 referee report

> **SIMULATED REVIEW MATERIAL.** Generated 2026-07-05 by the ARS
> `academic-paper` rebuttal-audit mode (run inline). Advisory QA only — no new
> response text is generated. Manuscript state: branch `rev9-frontier`, HEAD
> d4c6efb. "Verified" below means checked against `main.tex` / `refs.bib` in
> this audit; "claimed" means asserted in the response but not independently
> re-checked here (deep number tracing is in `project_audit.md`).

## Coverage matrix — 12 numbered concerns

| # | Referee concern | Response | Coverage | Verification |
|---|---|---|---|---|
| 1 | Narrative contradicts own tables ("never beats", "three tiers") | C1: framing retired, per-target verdicts, stacking promoted | **Full** | Verified: zero hits for "never beats"/"three tiers"/"skip the network" in main.tex; §IV.B heading is now "No stable ordering…" |
| 2 | ICC is the wrong ceiling for a fresh-simulation estimator | C2: three benchmarks distinguished (ICC / 2·ICC−1 replicate agreement / 16× reference), estimator judged against the right one | **Full** | Verified: §II.C "Three reliability benchmarks, distinguished"; ECA survival row 0.985 vs 0.987 (replicate) vs 0.994 (ICC) present at main.tex:310 |
| 3 | Privileged assumptions + default-zero completion prior; identifiability curve | C3+C4: matched-model framing, assumption list, coverage stats, completion-policy sensitivity, posterior-averaged variant; phase diagram as headline figure | **Full** on assumptions/completions; **substantial** on the sweep (see gap G1) | Verified: "matched-model" present; "parameter-free" absent; Fig. 2 exists. Axes: 4 of 9 requested swept in round 2, +2 (label noise, unknown radius) in the rev-9 addendum |
| 4 | "Prove the mechanism" over-claims; causal tests missing | Language corrected; interventions named as future work — one (learned rule-reader→simulator) since **run** in the rev-9 addendum | **Substantial** | Verified: zero occurrences of "prove" in main.tex; "smooth function" deleted |
| 5 | Probe results under-specified | Both probe tasks fully specified (classes, splits, baselines, evaluation unit) | **Full** | Claimed; §IV.D exists and response's description is consistent with it |
| 6 | Statistics incomplete (per-target tables, split/seed uncertainty, TOST misuse) | C5: full per-target tables with CIs and 5-seed spreads; LOO-88 + 20 repeated outer splits for deterministic methods; TOST at δ∈{0.02,0.05,0.10}; "tie" only where TOST passes | **Substantial** (gap G2: CNN split variance not measured — disclosed) | Verified: main.tex:729–746 matches the response's split numbers exactly (survival 0.76, 0.56–0.84; fill 0.68, 0.55–0.75); margin-sensitivity paragraph present |
| 7 | One constrained CNN ≠ "deep networks" | Referee's option 1 taken: claims narrowed to this architecture; full architecture disclosure in supplement; no model suite | **Full** (per the referee's own either/or) | Verified: narrowed language in abstract ("a deliberately constrained convolutional amortiser") |
| 8 | Spatial-map "tie" is not equivalence | C7: relabelled **inconclusive** with both CIs shown; "training-free" explicitly disclaimed; composed system = unit of resampling | **Full** | Verified: main.tex:565–578 — CIs match the response verbatim; "(we do not call this training-free)" |
| 9 | "Complexity map" → damage-signature landscape; confusion matrices | C6: renamed throughout; full ECA confusion matrix; detector shown to be the weak instrument; no complexity claim | **Full** | Verified: main.tex:582–594 — sensitivity 1.0, precision 2/3, specificity 0.99, balanced accuracy 0.99; Wilson CI [6.9, 8.8]% |
| 10 | Pre-registration unauditable during review | De-emphasized; every analysis labelled registered / post-hoc confirmatory / exploratory; repo stays private; anonymized archive offered to the editor "on request" | **Partial** (see risk R1/R2) | Verified: Appendix A labelling exists (main.tex:686) |
| 11 | Report the compute trade-off | C8: latency, budgets, break-even ≈4,700 queries, accuracy-vs-budget curve | **Full** | Verified: main.tex:547–551 |
| 12 | Missing methodological detail | Appendix B supplement with every listed item | **Full** | Spot-verified: baseline-of-record rule, split sensitivity, per-seed cost present in the Methods supplement |

**Editorial points 1–11:** all addressed in the response; spot-verified: #9
Vispoel citations now carry volume/pages/DOIs matching Crossref exactly
(cross-checked in `citation_check.md`); #11 verdict-language discipline
observed at main.tex:251, 360–363, 573–576. Not individually re-checked: #2
(Table I caption), #3, #4, #10 — their claims are consistent with the sections
read.

## Gaps (real, but disclosed)

- **G1 — identifiability sweep still misses 3 of the 9 requested axes**
  (diagram width, IC correlation length, weakly nonuniform rules). Disclosed
  and labelled as extensions; low risk, but the referee enumerated them
  explicitly, so expect the question again.
- **G2 — CNN split variance is not quantified** (repeated splits cover only
  the deterministic/baseline methods; no CNN retraining across splits).
  Disclosed candidly, and the narrowed claims reduce the exposure, but this is
  the most likely residual statistical objection.
- **G3 — causal interventions** (rule-scrubbing, rule-provision) remain unrun;
  named as future work. The rev-9 addendum's learned rule-reader→simulator
  covers the third intervention and the controlled-degradation test, which
  materially strengthens the reply to concern 4/7.

## Risk flags

- **R1 (highest) — concern 10 is answered on labelling but declined on the
  substantive request.** The referee asked for a review-time, immutable,
  anonymized preregistration archive. The response offers one only "on
  request" to the editor. Recommendation: attach the anonymized timestamped
  archive proactively with the round-3 submission rather than making the
  referee ask twice for the same thing.
- **R2 — the anonymity rationale is internally inconsistent.** The stated
  reason for keeping the repository private is "to protect anonymity", but the
  manuscript is signed (Rollier & Baetens, Ghent), includes a first-author
  self-citation (`rollier2024cnn`), and cites two more group papers. If review
  is single-anonymous, the repo cannot deanonymize anyone the byline hasn't
  already. Either give the real reason (e.g. releasing on acceptance) or drop
  the rationale — a careful referee will notice the mismatch.
- **R3 — the round-3 addendum must be folded in, not appended.** The current
  "Addendum held for round 3" is clearly marked as outside the round-2
  response — good — but at round-3 submission its content (F1/F2 frontier
  results) should be integrated into the per-concern replies (esp. concerns 3,
  4, 7) instead of remaining a trailing section.
- **R4 — no over-claim detected in the response.** Every spot-checked response
  claim matched the manuscript, including the honest relabellings
  ("inconclusive", "we do not call this training-free") and the refuted half
  of frontier hypothesis (ii). Tone is concessive where the referee was right,
  which is the correct posture for this referee.

## Verdict

Point-by-point coverage: 12/12 concerns and 11/11 editorial points receive a
substantive reply; 9 full / 2 substantial / 1 partial. The single partial
(concern 10, review-time auditability) is the highest-risk item for round 3
and is fixable by proactively supplying the anonymized archive (R1) and
repairing the anonymity rationale (R2).
