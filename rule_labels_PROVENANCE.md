# Provenance of `rule_labels.csv`

**Status: awaiting user spot-check** (generated 2026-07-01; metrics computed from it
should be treated as provisional until this line is removed).

## `lp_class` — Li–Packard (authoritative)

Transcribed from **W. Li & N. Packard, "The Structure of the Elementary Cellular
Automata Rule Space", *Complex Systems* 4 (1990) 281–297, Table 2 (p. 288)**
([open-access PDF](https://www.complex-systems.com/pdf/04-3-3.pdf)). Coding:

| code | LP class | orbits | rules (of 256) |
|---|---|---|---|
| 1 | null | 8 | 24 |
| 2 | fixed point | 32 | 97 |
| 3 | periodic | 31 | 89 |
| 4 | locally chaotic | 3 | 10 |
| 5 | chaotic | 14 | 36 |

Li & Packard list their own orbit representatives (e.g. 137 for {110,124,137,193});
each was mapped to this repo's canonical minimum-of-orbit representative via
`caspectra.ca.eca.equivalence_class`. Automated checks, all passing
(script: session scratchpad `build_labels.py`):

1. the 88 listed rules map **one-to-one** onto the repo's 88 representatives, no
   class clashes within an orbit;
2. expanding orbits to all 256 rules reproduces the published class sizes
   **24 / 97 / 89 / 10 / 36** exactly;
3. LP *null* coincides exactly with the Wolfram-class-1 rows already in the CSV.

### Corrections to the previous best-effort table (not just filled blanks)

| rule | old | new (Li–Packard) | why |
|---|---|---|---|
| 2, 10, 170, 184 | periodic | **fixed point** | LP count horizontally *translating* configurations as fixed point |
| 54, 110 | locally chaotic | **chaotic** | LP explicitly classify the Class-IV rules as global chaotic (p. 287: "only Rule-54 and Rule-137 (or Rule-110) have the typical Class-IV behaviors. In this paper they are classified as global chaotic rules.") |

56 previously blank orbits were filled.

**Consequence for evaluation:** under LP, *complex/class-IV is not a class* — 54 and
110 are just "chaotic". Any class-IV recall metric must therefore be scored against
the **`wolfram_class` column** (4 = complex), never against `lp_class`. Likewise the
locally-chaotic LP class (26, 73, 154) sits inside Wolfram class 2 — the two schemes
genuinely disagree on the boundary rules, which is part of why this project exists.

## `wolfram_class` — best-effort (unchanged)

The Wolfram column is carried over unchanged from the previous CSV (all 88 filled;
flagged "best-effort" in `notebooks/02_cluster_exploration.ipynb`). Spot-checks
against the standard listing pass (30/45/60/90/105/150 → 3; 54/110 → 4;
0/8/… → 1; 204/232/178 → 2; 26/73/154 → 2). Wolfram's scheme has no single
authoritative per-rule table and borderline rules vary between listings; treat
class 4 = {54, 110} as the load-bearing part, which is uncontroversial.

## `borderline` — scheme-instability flags (added 2026-07-02)

Neither classification column is ground truth: formalized Wolfram-style class
membership is **undecidable** (Culik & Yu 1988; Sutner), and the observed class
depends on the initial-condition measure and observation protocol (Gilman 1987)
— see `FOUNDATIONS.md` and the literature report in `docs/literature/`. The
`borderline` column flags rules with documented instability; per
`EVALUATION_CRITERIA.md` rev 2, class-IV metrics are reported both with and
without them:

| rule | listed as | why flagged |
|---|---|---|
| 40 | Wolfram 1 / LP null | published chaotic dynamics on invariant subsets (Ohi) |
| 42 | Wolfram 2 / LP fixed point | published chaotic global attractor, positive topological entropy (Chen, Hsu et al.) |
| 41 | Wolfram 2 / LP periodic | ballistic, chaotic-looking damage cone in our measurements (spreading rate 0.62 — squarely in the chaotic range; `RESULTS.md` 2026-07-01) |
| 106 | Wolfram 3 / LP chaotic | intermediate damage signature (rate 0.43) adjacent to {54, 110}; the one contaminant of the class-IV cluster; some schemes treat it as edge/complex |

The Li–Packard 54/110 disagreement (complex folded into chaotic) is documented
above and is handled by scoring class IV on the Wolfram column, not by a flag.
