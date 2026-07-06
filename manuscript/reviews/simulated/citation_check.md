# Citation Check Report — `main.tex` + `refs.bib`

> **SIMULATED REVIEW MATERIAL.** Generated 2026-07-05 by the ARS
> `academic-paper` citation-check mode (run inline). Advisory only.
> Manuscript state: branch `rev9-frontier`, HEAD d4c6efb.

## Method
Newline-safe extraction of every `\cite{...}` key from `main.tex` (13 distinct
keys, 15 citation instances) cross-checked against the 13 `refs.bib` entries
and the compiled `main.bbl` (13 `\bibitem`s). Metadata spot-verified against
the Crossref API (three group self-citations + the five classic entries
lacking DOI fields) and the arXiv API.

## Results

### Structural integrity — PASS
| Check | Result |
|---|---|
| Cited keys missing from refs.bib | **0** |
| Bib entries never cited | **0** (initial line-based grep falsely flagged `vispoel2024damage`/`vispoel2022progress`; the `\cite` spans a line break at main.tex:93–94) |
| Duplicate bib keys | 0 |
| Compiled bibliography count | 13 = bib count ✓ |
| Undefined citations in main.log | none |

### In-text attribution — PASS
All 15 citation instances checked in context; each supports the sentence it is
attached to (e.g. `culikyu1988` → undecidability, main.tex:86; `gilman1987` →
IC-measure dependence, main.tex:88 and 651; `geirhos2020shortcut` → shortcut
learning, main.tex:84; `wuensche1999` → input-entropy variance statistic,
main.tex:227; `kleinberg2002`+`mitchell1993` → no-ground-truth-scheme claim,
main.tex:663).

### Errors found

**E1 (should fix): `rollier2024cnn` year is wrong.**
The bib entry says `year = {2024}`, but Crossref records the Springer chapter
(doi 10.1007/978-3-031-81097-8_3, *Emergence, Complexity and Computation*) as
published **2025**, pages **49–70** (pages also missing from the entry). The
2024 date belongs to the arXiv preprint (2409.02740, title and authors
verified). Fix: `year = {2025}`, add `pages = {49--70}`; keep the arXiv note.
The citation *key* may stay as-is.

**E2 (should fix): the bib header's DOI promise is not kept.**
`refs.bib` line 1 states "All entries carry stable identifiers (DOI) where one
exists", but only 3/13 entries have DOI fields. DOIs verified to exist via
Crossref for five more:
- `langton1990` → 10.1016/0167-2789(90)90064-V
- `israeli2006` → 10.1103/PhysRevE.73.026203
- `geirhos2020shortcut` → 10.1038/s42256-020-00257-z
- `gilman1987` → 10.1017/S0143385700003837
- `wuensche1999` → 10.1002/(SICI)1099-0526(199901/02)4:3<47::AID-CPLX9>3.0.CO;2-V

No DOIs exist for the *Complex Systems* entries (`culikyu1988`,
`lipackard1990`, `mitchell1993`), `kleinberg2002` (NeurIPS 15), or the
`wolfram2002` book — those are consistent with the header claim.

### Notes (no action required)
- The two Vispoel self-citations' metadata match Crossref exactly (volume,
  article number, year).
- `kleinberg2002` dated 2002 for NIPS 15 follows the standard convention
  (proceedings printed 2003); acceptable.
- The `apsrev4-2` style suppresses article titles in the rendered reference
  list ("Control: production of article title (-1) disabled" in main.bbl);
  journal-standard behaviour, not an error.

## Verdict
Citation apparatus is structurally clean; two metadata fixes recommended
(E1 year/pages, E2 five missing DOIs) before round-3 submission.
