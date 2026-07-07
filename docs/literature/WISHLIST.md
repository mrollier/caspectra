# Literature wishlist (user-supplied PDFs)

Papers we cannot fetch open-access. Drop the PDFs in this directory, named
`<firstauthor>_<year>_<slug>.pdf`. Nine of the ten items of the 2026-07-07
ranking were uploaded and read the same day — claim-by-claim verification and
synthesis in `readthrough_2026-07-07_NOTES.md` (three manuscript mis-cites
found and staged for fixing on branch `lit-verification`).

Outstanding items, ranked (item 1 pre-dates the read-through; 2–7 were added
by it):

1. **Adamatzky (1994), _Identification of Cellular Automata_** (Taylor & Francis
   monograph) — cited twice as the monograph-length treatment of the inverse problem,
   and now also the sole anchor of the manuscript's "probabilistic move" framing
   (l.661, narrowed from the Y&B co-cite in the read-through); ToC + key chapters
   suffice if the full book is impractical.

Added 2026-07-07 after the read-through (details + rationale in
`docs/research_directions_2026-07-07.md` §3; bibliographic data to verify on
retrieval):

2. **Kauffman 1969**, J. Theor. Biol. 22:437 — *promoted from honourable mention:*
   cited directly at main.tex l.108 but never read (same secondhand-attribution
   risk the read-through just cleaned up elsewhere).
3. **Derrida & Weisbuch 1986**, J. Physique 47:1297 — refined annealed
   overlap-evolution formalism behind the (now-negative) zero-budget member.
4. **Domany & Kinzel 1984**, PRL 53:311 — canonical stochastic-CA/DP model
   anchoring Bagnoli's directed-percolation mapping.
5. **Grassberger 1995**, J. Stat. Phys. 79:13 — damage-spreading transitions and
   DP universality; the critical-regime failure discussion.
6. **Zhao & Billings FCA-OLS line** (Sun 2011 refs [19], [21], [22]) — the actual
   OLS identification papers, for the corrected Appendix-D row.
7. *(optional)* **Bagnoli & Rechtman 1999**, PRE 59:R1307; **Martins et al. 1991**,
   PRL 66:1018.

Unsolicited arrival 2026-07-07 (not yet read; queue for the next read-through):
`cnn-supervised_learning-cellular_automata.pdf` (moved into this directory from
the repo root).

Honourable mentions: Boccara, Nasser & Roger 1991 (PRA 44:866); Schmidt & Lipson
2009 (Science 324:81). Not needed (open access or on disk): Wolfram 1984/2002,
all arXiv/Distill/Complex Systems items.

Already in this directory: the commissioned deep-research report, Li–Packard 1990,
Culik & Yu 1988 (both open-access at complex-systems.com), Israeli & Goldenfeld 2006,
Kari 2005 survey, Wuensche 1999, Mitchell–Hraber–Crutchfield 1993, Hanson & Crutchfield
1997 (rule 54), Vispoel 2024 (`vispoel_2024_damage_spreading.pdf`), Vispoel 2026
(`vispoel-hidden_structure.pdf`), Rollier et al. 2025 taxonomy (`rollier-taxonomy.pdf`),
and — received + read 2026-07-07 (notes in `readthrough_2026-07-07_NOTES.md`):
Vispoel 2022 (`vispoel-progress-2022.pdf`), Richards 1990 (`richards-extracting-1990.pdf`),
Yang & Billings 2000 (`yang-extracting-2000.pdf`), Bagnoli 1992 (`bagnoli-damage-1992.pdf`),
Derrida & Pomeau 1986 (`derrida-random-1986.pdf`), Gilman 1987 (`gilman-classes-1987.pdf`),
Sun 2011 (`sun-fast-2011.pdf`), Langton 1990 (`langton-computation-1990.pdf`),
Baetens & De Baets 2010 (`baetens-phenomenological-2010.pdf`).

## Analysis wishlist (tracked, not scheduled)

Added 2026-07-07 after assessing Vispoel, Daly & Baetens 2026
(`vispoel-hidden_structure.pdf`; notes in `vispoel_2026_hidden_structure_NOTES.md`):

1. **Annealed / Derrida–Pomeau mean-field damage estimate as a ~zero-budget oracle-family
   member.** ~~Open question: how much of the damage-response statistics does the annealed
   tier capture?~~ **EXECUTED 2026-07-07 — answer: essentially none (honest negative).**
   Implemented as `caspectra/eval/annealed.py` + `scripts/eval_annealed_member.py` on
   branch `annealed-oracle` (rev-12 changelog in `EVALUATION_CRITERIA.md`); pre-declaration
   and full execution record in `docs/research_directions_2026-07-07.md` §2 and §4.
   Median held-out R² −2.15 on the r=2 panel (16-pair MC member: 0.92) and the survival
   criterion ĝ′(0) > 1 never beats the always-survives base rate. Reported in the
   manuscript's accuracy-vs-compute subsection as the family's negative zero-budget anchor.
2. **(s, β) mean-field parameters as genotype-side covariates for the radius-two panel.**
   Both are instant to compute for the 800 sampled r=2 rules (Eqs. 23–24 of Vispoel 2026).
   Diagnostics, not features (genotype side): does amortizer error correlate with β; does
   the criterion-9 complex-regime placement sit near their binary-space II↔III boundary
   (their triple-point localization is for k ≥ 3 totalistic spaces, not r=2 binary)?
   **Partial (2026-07-07):** s̄ (= s, table-side µ-sensitivity) now computed for every
   panel rule as a byproduct of item 1 (`per_rule.csv` columns `slope`, `s_bar`); β and
   the boundary comparison still open.
