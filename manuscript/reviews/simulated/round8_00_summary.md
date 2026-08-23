# Round-8 simulated re-review — summary

Panel run 2026-08-23 on branch `review-round8-gemini` (state `ccfc4ba`),
verifying the revision that answers `../review_gemini_21aug26.md`
(Accept with Major Revisions; required actions R1–R4).

**Verdict: Minor Revision.** Four of five rubric scores fall in the Accept
band (EIC 86, methodology 84.6, domain 84.5, perspective 83.7); the decision
is held at Minor because the devil's advocate raised two CRITICAL issues,
which the panel rules make disqualifying for Accept.

**Unanimous (5/5): no claim drift.** The presentation-only contract held.
The EIC ran a numeric diff against the merge base, methodology re-ran
`scripts/audit_manuscript_numbers.py` and independently recomputed the ρ
table and the selected-checkpoint bands, and the domain reviewer diffed the
full range: no registered number, verdict, margin, threshold or disclosure
changed.

**Required-action compliance:** R1 fully addressed (all five reviewers),
R3 and R4 fully addressed in substance, R2 partial (density improved, volume
did not — the paper grew from 16 pp to 18 pp).

| File | Reviewer |
|---|---|
| `round8_r0_eic.md` | Editor-in-Chief, verification matrix for R1–R4 |
| `round8_r1_methodology.md` | Statistics, calibration, pre-registration |
| `round8_r2_domain.md` | Cellular automata, damage spreading, diagram conventions |
| `round8_r3_perspective.md` | ML-for-science / simulation-based inference |
| `round8_r4_devils_advocate.md` | Adversarial audit |
| `round8_editorial_decision.md` | Synthesis, consolidated checklist, roadmap |

**Acted on in the same round** (commits `0b3cef9`, `2040c01`, `957fa47`;
details in `../trimmed_material.md`): both CRITICALs, the spreading-rate
ceiling correction (1.008 → 0.992/0.975, verified by direct measurement),
the ρ zero-noise caption, seed-0 provenance and the bimodality note, the
neural-boundary calibrations, the App. E detector protocol, figure
legibility and production defects, and the change record's condensation
framing.

**Carried forward, not done:** the panel's Priority-2 and Priority-3 lists,
the one-page R1–R4 mapping and the point-by-point response letter (the
author elected not to write a response letter this round), and the
user-gated administrative TODOs (ORCIDs, funding, archive DOI).
