# ARS Full Review — Consolidated Summary (2026-07-05)

> **SIMULATED REVIEW MATERIAL** — internal pre-round-3 stress test of
> `manuscript/main.tex` @ `rev9-frontier` (d4c6efb) plus a whole-project
> audit, run with the academic-research-skills plugin (v3.15.0):
> `academic-paper-reviewer` full mode (5-reviewer panel, sprint contract) +
> `academic-paper` citation-check and rebuttal-audit modes + a project
> integrity audit. Real referee reports live one directory up.

## Verdict

**MAJOR REVISION (near the minor boundary)** — contract condition F1 fired on
the Devil's Advocate's verified CRITICAL; 3×Major / 2×Minor recommendations;
mean rubric 78.5/100. No conclusion-invalidating flaw found; the measurements
themselves survived a 46-number artifact audit (44 exact) and a deliberate
attempt to break them.

## Read in this order

1. [`editorial_decision.md`](editorial_decision.md) — decision, consensus/disagreement analysis, prioritized roadmap (R-1…R-7, S-1…S-8)
2. [`r4_devils_advocate.md`](r4_devils_advocate.md) — the CRITICAL (abstract contradicts §IV.E) + the steelmanned counter-argument
3. [`r1_methodology.md`](r1_methodology.md) — the artifact audit; the −1.1 vs −0.93 provenance finding
4. [`r2_domain.md`](r2_domain.md) — the missing inverse-CA prior art (Richards 1990, Adamatzky 1994, Billings & Yang 2000) and damage-spreading lineage
5. [`r3_perspective.md`](r3_perspective.md) — SINDy/SBI/weak-baselines positioning; boundary conditions of the general lesson
6. [`r0_eic.md`](r0_eic.md) — venue fit, abstract/lead-paragraph compliance, production matter
7. [`citation_check.md`](citation_check.md) — clean structure; 2 metadata fixes (rollier2024cnn year 2025; 5 missing DOIs)
8. [`rebuttal_audit.md`](rebuttal_audit.md) — 12/12 round-2 concerns covered; risks: archive access + anonymity rationale
9. [`project_audit.md`](project_audit.md) — 208 tests pass, lint clean, prereg ordering git-verified; stale figure labels; criterion-7 caveat
10. [`phase0_field_analysis.md`](phase0_field_analysis.md) — panel configuration + orchestration disclosure

## The five things to fix first

1. **Abstract** — its degraded-regime clause is the old rev-8 claim, contradicted by the paper's own §IV.E frontier results (DA C1; verified against main.tex:55–59 vs 494–538). Also ~370 words vs the 250 limit, and the *Chaos* lead paragraph is missing (EIC).
2. **One wrong number with a provenance trail** — "frozen CNN to −1.1" (main.tex:526) vs −0.93 in the canonical artifact; RESULTS.md's F2 cnn/stack column (6 cells) carries values from the documented discarded wrong-checkpoint run (R1).
3. **Literature repositioning** — all five reviewers, three literatures: inverse-CA prior art (the core operation has direct ancestors), the damage-spreading lineage (incl. Baetens & De Baets, *Chaos* 2010), and the ML-for-dynamics/SBI audience of the closing lesson.
4. **Registration bookkeeping** — Appendix A omits every rev-9 item §IV.E labels as registered; the three frontier hypotheses are never enumerated; reduced MC budgets (48/64 vs 256 pairs) and the single-seed reader are undisclosed.
5. **Two cheap fairness controls** — degradation-augmented CNN and same-budget unconstrained CNN (~22 min/seed) — or scope the degraded-regime guidance to adaptation-naive amortizers (DA + R3, independently; echoes the real referee's concern 7).

## What the panel praised (unanimously)

The ICC vs 2·ICC−1 replicate-agreement distinction (algebraically verified,
empirically self-validating, "exportable to any Monte-Carlo-target
benchmark"), the registration discipline (git-verified numbers-free ordering
for revs 7–9), the identifiability frontier as "the paper's most transferable
artifact", and honestly-reported inconclusive/refuted verdicts throughout.
