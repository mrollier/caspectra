# Re-review verification checklist — round-3 revision vs the ARS roadmap

> **SIMULATED REVIEW MATERIAL.** ARS `academic-paper-reviewer` **re-review**
> (verification) mode, run inline 2026-07-05 against the revision on branch
> `round3-revision` (post rev-10 measurements). Each item from
> `editorial_decision.md` is checked against the actual file state; every
> verification names its evidence.

## Required revisions

| # | Status | Verification |
|---|---|---|
| R-1 | **DONE** | Abstract 250 words (strict counter); degraded-regime clause now states the *measured* attribution (posterior → masking/density/≤3% noise; noise band → corruption-trained direct network; matched regime → read family, zero violations). *Chaos* lead paragraph present after `\maketitle`. Discussion "almost surely" → measured rates; the reader "only estimator that retains signal" sentence replaced by the rev-10-aware text. |
| R-2 | **DONE** | main.tex quotes −0.93; RESULTS.md F2 cnn/stack cells re-derived with an explicit correction note; `scripts/audit_manuscript_numbers.py` re-derives 25 rev-9 + 12 rev-10 quoted values + 3 text guards from the released artifacts — 40/40 pass. The audit already caught one real prose error during this revision (0.55→0.51 band edge), demonstrating it works. |
| R-3 | **DONE** | 16 Crossref-verified entries added (29 total). Introduction stipulates identification as prior art ("We claim no novelty for the inverter"), names Richards/Adamatzky/Yang–Billings, and repositions the contribution as the benchmark consequence. Damage-spreading lineage cited at first use (Kauffman, Derrida–Pomeau, Bagnoli, Baetens & De Baets); survival named as the finite-horizon Lyapunov sign. Discussion paragraph connects SINDy/Schmidt–Lipson/Cranmer/McGreivy. By-products: Shalizi (maps ×2), Zenil (zlib), Boccara (census), Wolfram 1984, Li–Packard landscape analogue; rule-106 claim now sourced. |
| R-4 | **DONE** | Appendix A taxonomy covers rev-9 *and* rev-10 labels; the three hypotheses enumerated verbatim with earned verdicts; n_pairs 64/48-vs-256 and the single-seed reader disclosed in both captions and at first mention; the registered posterior-interval calibration is **measured and reported** (§IV.E: ≥ nominal across the masking band, 0.13 at 20% noise), with the recomputation reproducing all 17 released medians bit-exactly. |
| R-5 | **DONE** | §IV.C defines the base (cross-fitted OOF ridge, refit within the held-out panel), reconciles 0.56/0.14 vs Table III, and reports the headline-base increment: survival +0.08 CI[+0.02,+0.18] (post-hoc confirmatory, rev. 10). |
| R-6 | **DONE (ran the controls; guidance rewritten to the measured result)** | Both controls trained under numbers-free rev-10 registration (commit c16cc2b precedes all measurements). Outcome honestly reported in both directions: the noise dead zone **overturned** (degaug CNN 0.51–0.62 across 3–15% noise; the rev-9 estimator-class claim withdrawn in manuscript and letter), the matched regime **confirmed** (hypothesis-(iii) re-test zero violations; 354× unconstrained control changes no verdict). Abstract, Intro, §III(iii), §IV.E(iii), Table V, Discussion, letter §7-bis, RESULTS.md rev-10 all consistent. |
| R-7 | **DONE** | greps: no "2/88" (→3/88 ×2); survival CI printed [+0.002,+0.201]; stacking CI upper 1.01 with caption note; the 80-rule panel explicitly a fixed-seed subsample of the 160, cross-referenced in §IV.D. |

## Suggested revisions

| # | Status | Note |
|---|---|---|
| S-1 | DONE | Corollary stated in the Introduction ("attains the benchmark by construction… only on cost or robustness"). |
| S-2 | DONE | Discussion boundary-conditions paragraph maps all five axes, measured vs conjectured; stochastic case excluded explicitly. |
| S-3 | DONE | `sec:frontier` subsection with (i)/(ii)/(iii)/verdict paragraphs + practitioner Table (tab:guidance). Prune kept light — the paper grew 9→11 pages, all growth reviewer-demanded (positioning, controls, production matter). |
| S-4 | DONE | make_figures.py labels fixed, landscape.pdf regenerated, orphaned map_benchmark.pdf + code removed with a history note. |
| S-5 | MOSTLY | Acknowledgments/Author declarations/Data availability added; scikit-learn pinned (1.9.0). **User-gated remainder: ORCIDs, funding text, archive DOI.** External timestamping of the registration history remains a process suggestion. |
| S-6 | DONE | rollier2024cnn → 2025, pages 49–70, booktitle corrected; 5 missing DOIs added. |
| S-7 | DONE | Letter: per-concern round-3 supplement (§3-bis/§7-bis/§10-bis), anonymity rationale withdrawn, registration history attached as Appendix L1 (criterion-7 caveat disclosed), R→A→C cross-reference table, R-2 correction disclosed plainly. |
| S-8 | NOT DONE (superseded) | The denoise-then-invert baseline for the 3–7% band lost its motivation: the rev-10 degaug CNN now owns 3–15% noise at R² ≈ 0.5–0.6, far above what a denoiser+inverter could plausibly reach there (the inverter needs ≲1 flipped transition). Remains a legitimate optional robustness check. |

## Residual issues (for the authors, honest list)

1. **Single seed per control** (registered and disclosed; matches the
   reader's gating). If the referee asks, seed replication of C-i is the
   cheapest high-value addition (~30 min/seed).
2. **Page growth** 9→11 pages; all additions trace to panel/referee demands,
   but a copy-editing pass could recover ~half a page.
3. Optional lineage completions not added: Sun–Rosin–Martin 2011, Wulff &
   Hertz 1992, Hanson–Crutchfield, Martínez et al. on rule 54 (R2's
   "complete the lineage" suggestions — the load-bearing ancestors are in).
4. Transient float-placement warnings remain in the LaTeX log
   (`floatfix` on); all 3 figures + 5 tables verified present in the PDF.
5. ORCIDs / funding / archive DOI TODOs (user-only information).

## Verdict

Every Required item R-1…R-7 verified DONE with evidence; S-1…S-7 done or
user-gated; S-8 superseded by a stronger measured result. The revision also
*strengthened* the paper beyond the roadmap: the rev-10 controls turned the
panel's fairness objection into a new, publishable finding (adaptation to
the observation model, not estimator family, decides the degraded regime)
while leaving the paper's central claim intact and better defended. Under
the panel's contract this state would clear F1 (the D3 contradiction is
resolved and re-verified against artifacts) — **recommendation: the revision
is ready for the user's read-through and the round-3 submission decision.**
