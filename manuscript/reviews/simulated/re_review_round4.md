# Re-review verification — round-4 revision vs the third review

> **SIMULATED REVIEW MATERIAL.** Inline verification pass, 2026-07-06,
> against branch `round4-revision` (post rev-11 measurements). Every item of
> `manuscript/reviews/paper_third_review.md` checked against file state;
> each verification names its evidence.

## Major concerns

| # | Status | Verification |
|---|---|---|
| C1 | **DONE (adopted + sharpened)** | "can never beat" removed everywhere (grep clean); budget-indexed family framing in abstract/intro/II.C/IV.A/discussion; 1−ICC headroom stated in II.C and intro; M1 measured (mechanistic → ICC vs reference, direct estimators shift ≤0.007); all four line edits adopted in substance. |
| C2 | **DONE** | App. B "Evaluation protocol" box covers the six requested items; M4 per-diagram audit quoted in III(i) (0.990 / 1.0); asymmetry favouring direct estimators disclosed. |
| C3 | **DONE** | "Enriched panel" naming in IV.A + Tables I/III; subpanel + post-stratified rows (M3) in Table I; Q3 cache-provenance disclosed in main text; sampling measure exact (App. B); enrichment shown conservative. |
| C4 | **DONE** | Renamed "approximate Bayesian rule decoder (entrywise pseudo-posterior)" at first use with exact model (output-flips-only, prior, ε grid); App. C pseudocode A1–A4 + worked example; majority-vote/ties-to-0 + t=0 + masking semantics in III(i)/App. C; calibration tied to the approximation (noise-axis overconfidence = its price). |
| C5 | **DONE (claim changed by measurement)** | M2 paired equivalence with registered margins; 6/8 formal; IV.A states per-target results and the two CI-width failures; "statistically indistinguishable" removed (lead ¶ now "as accurate as an independent re-measurement"). |
| C6 | **DONE (partial adopt + justified push-back; adopted part vindicated the concern)** | M5 seed replication ran; registered stability rule FAILED (seed 1 weak); band restated as per-seed range 0.24–0.62 in IV.F(iii)/Table V/intro/abstract/discussion; robustness tax 0.14–0.37; 20% reliability seed-dependent. Push-back on outer-split retraining argued from proportionality in the letter; single-split disclosure already in III "Statistical protocol". |
| C7 | **DONE (claim scoped by measurement)** | Table IV relabelled "cross-fitted complementarity diagnostic"; folds/leakage guards stated; M6 deployment stack measured: survival increment does not deploy (+0.001 n.s.); IV.C states both facts. |
| C8 | **DONE (labeling + noise-axis replication; push-back on other axes)** | Table V "exploratory guidance, bounded to the evaluated protocol" + extrapolation warning; M7 complement-panel replication paragraph in IV.F(iii); crossover restated as 3–7.5% band; "none reliably recommendable" phrasing; per-cell CIs referenced to the released artifact. |

## Minor concerns 1–14

All adopted: m1 target formulas (App. B); m2 Lyapunov proxy (II.B); m3 R²
convention (App. B box); m4 ICC exposition (II.C); m5 sampling measure
(App. B); m6 uncertainty-source labels (Tables I–III captions); m7 same-core
CPU timings + vignette framing (IV.G); m8 radius selection (App. C A4);
m9 IV.H renamed; m10 signature-complex as criterion label (IV.A); m11
rhetorical tightening (abstract, intro, IV.B, Table V, discussion);
m12 prior-work table (App. D) + Sun–Rosin–Martin/Elser/Mordvintsev added
(Crossref-verified); m13 undecidability scoped; m14 env pins + repro entry
points (Data availability; DOI remains user-gated at acceptance).
Citation checks: rollier2024cnn narrowed to task+regime; culikyu1988 scoped;
mcgreivy2024 wording verified against source claims.

## Questions Q1–Q10

Answered in the letter's table, each mapped to a manuscript location or
measurement (Q3 answered against interest: membership from the eval cache).

## Structure

Secondary-analyses separation implemented via explicit lead-in (IV.G) +
IV.H rename; the reviewer's full 8-section renumbering not adopted (current
order already matches it modulo that separation) — documented choice.

## Residual issues (honest list)

1. Learned reader and resnet18 control remain single-seed (disclosed;
   justified in letter — negative-control roles).
2. Outer-split retraining of neural estimators not performed (push-back;
   offer stands if the editor requires it).
3. Frontier masking/density/label/radius axes not replicated on the
   complement panel (push-back: wide-margin verdicts).
4. Page growth 11 → 15; +3 pages are the reviewer-demanded appendices
   (protocol box, pseudocode, prior-work table) and references.
5. M5 exposed genuine ~2× run-to-run variance in the degradation-trained
   control; the paper now carries it honestly, but a referee may ask for
   more seeds or early-stopping protocols (a fair future ask; final-epoch
   checkpointing is the registered protocol).
6. User-gated: ORCIDs, funding, archive DOI (TODOs in main.tex).

## Verdict

Every major concern is addressed by measurement or precise exposition, with
three claims changed by their own registered tests (C5, C6, C7) and both
replication demands met on the axis that carries the headline result. The
central thesis survives in sharper form: identification as a budget-indexed
oracle family; adaptation to the observation model decides the degraded
regime, with its level (not its ordering) sensitive to panel and seed.
Ready for the user's read-through and the round-4 submission decision.
