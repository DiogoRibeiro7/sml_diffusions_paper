# Dimensional Asymptotics of Euler-Based Simulated Likelihood for Multidimensional Diffusions

Two mathematical manuscripts, the code that generates every number in them, and the machinery that
keeps the two in agreement.

## What the paper argues

A widely used method for likelihood inference in discretely observed diffusions — the endpoint or
Pedersen estimator — approximates each transition density by simulating an Euler scheme to one step
before the observed endpoint and averaging the final Gaussian density.

That final Gaussian is the model's own one-step law, of covariance `hV`. Its bandwidth is therefore
`√h`, not `h`, which makes the construction a shrinking-bandwidth kernel estimator whose effective
simulation size is

```text
S / M^(K/2)
```

rather than `S`, where `K` is the state dimension, `M` the number of Euler substeps and `S` the
number of simulations. The paper derives the exact finite-`M` moments, the general local moment law
with its constants, the corrected density-level normalisation, and the mean squared error, minimised
at `M ≍ S^(2/(K+4))`.

It then gives a counterexample to the joint transition-density statements of Brandt and Santa-Clara
(2002), *Journal of Financial Economics* 63, 161–210. Along `M = S → ∞`, a sequence satisfying their
own rate condition and their own regularity assumptions, the simulated density converges in
probability to zero for every `K > 2` while the true density is strictly positive. This refutes the
consistency asserted in their Lemma 2 and, since `√S` times the centred density then diverges, the
central-limit statement of their Lemma 3. The proofs of their parameter-estimator theorems
consequently fail, and in the four dimensions the application uses, their rate condition is
incompatible with mean-square consistency of the simulated density.

The threshold is sharp. Collapse holds throughout the subcritical region, under `R_{M,S} → 0` alone,
and the density-level central limit theorem throughout its complement, so no designs are left
unsettled between them — the collapse rate is `O(R (log 1/R)^(K/2))`. The scaling that produces the
threshold does not depend on the paper's one imported hypothesis: under Aronson-type two-sided
Gaussian bounds on the Euler density, which are checkable from `μ` and `V`, the moment law holds with
its constant bracketed, so the exponent of `h` — and hence the effective size — follows from
primitive conditions. Assumption (A5) does exactly one thing, which is to replace that bracket by
the single value `p(y|x)`.

**What the paper does not claim.** It does not prove that the resulting argmax estimator is
inconsistent, and in the most tractable case it proves the opposite. In a Gaussian location model
the simulated maximiser is **consistent** along `M = S = n` with `K > 2` — precisely the sequence on
which the density collapses to zero. Collapse of the density and consistency of the maximiser hold
simultaneously, in the same model on the same designs, so the counterexample provably does not
transfer and no argument through pointwise density behaviour alone can make it. What remains open is
the rate. The consistency argument itself is conditional: it rests on a uniform law whose proof was
found incomplete under external review, and which now carries an unverified empirical-tail
hypothesis. Separately, whether `√N(θ̃ - θ̂)` diverges would refute the *conclusion* of Lemma 5
rather than its proof, and half of that is proved. The criterion's score at the truth has the exact second
moment `4 S^(2/K) G_S(θ₀) / N`, so it grows like `S^(1/K)` and cannot converge to the exact score —
the discrepancy is present, exactly, in the score. What is not proved is that it survives division
by the curvature, and Appendix A measures the obstacle: the finite-`S` criterion is about a third
less curved than its limit at `S = 10⁴` and does not approach it until `S ≈ 10¹⁰`, so the two
dependences on `S` nearly cancel across every simulation size anyone can run. The prediction is
therefore neither confirmed nor refuted by simulation, and is reported as a prediction. What the
simulation does establish is a level rather than a trend: solving the stationarity condition exactly,
the simulated maximiser carries roughly twice the error of the exact MLE at every size tested, so
the loss is real at practical simulation sizes even though its growth in `S` is not resolvable. The
paper does not claim the published empirical estimates are wrong.

## The companion note

The exchange-rate application of Brandt and Santa-Clara (2002) raises a separate set of questions,
about that specification rather than about the estimator, and they are answered in a companion note:
*Mathematical Status of the Exchange-Rate Application in Brandt and Santa-Clara (2002)*, built from
`paper/companion.tex`. It covers the square-root boundaries and the Feller ratios, the reality of
the incompleteness state under the implemented parameterisation, the invertibility of the
volatility map, the validity of the Brownian correlation matrix, the minimum-incompleteness
identification rule, and the constrained-inference question.

Its results are algebraic propositions and numerical diagnostics, not limit theorems, and several
are negative — establishing that no problem arises where one might have been suspected. Each claim
is labelled as a proved proposition, a numerical diagnostic, a statement reported by the original
authors, or an implementation detail the published description does not settle. Nothing in the
theory paper depends on the companion; the dependence runs one way.

## Quick start

```bash
pip install -r requirements.txt
make            # regenerate figures and tables, then build the PDF
make check      # tests, reproducibility, forbidden-phrase gate
```

`make` builds both documents: `paper/main.pdf`, the theory paper, and `paper/companion.pdf`,
the application note. Python 3.11+, NumPy, SciPy, pandas and Matplotlib; LaTeX with `latexmk`
and `biber`.

## Layout

```text
paper/                    the two manuscripts and everything they include
  main.tex                theory paper, LaTeX source
  main.pdf                theory paper, compiled
  companion.tex           application companion, LaTeX source
  companion.pdf           application companion, compiled
  references.bib          bibliography, 42 entries, its 39 DOIs Crossref-verified
  figures/                5 figures, vector PDF and PNG (generated)
  tables/                 16 LaTeX tables and 19 CSV files (generated)
code/
  generate_results.py         every figure and table
  check_correlation_matrix.py correlation-matrix and grid-domain diagnostics
  argmax_counterexample.py    the argmax investigation
  verify_reproducibility.py   regeneration check behind `make verify`
  verify_dois.py              every bibliography DOI against Crossref
  check_forbidden_phrases.py  guards against retracted wording returning
  make_release.py             gated release artefacts into dist/
tests/
  test_analytics.py             every analytical formula, checked independently
  test_singular_psd_condition.py the singular-block PSD lemma of the companion
  test_antithetic.py            the pair-average variance and the h-exponent
  test_feasible_sets.py         the two parts of the feasibility proposition
docs/                     audit trail; see below
notes/                    the argmax investigation and its go/no-go conclusion
reference/                literature under review; local only, never committed
dist/                     release artefacts; gitignored
```

Everything under `paper/figures` and `paper/tables` is generated. Edit `code/generate_results.py`,
not those files.

## How the numbers are kept honest

Every numerical statement in the manuscript is produced by code in `code/`, and four independent
gates keep the manuscript and the code from drifting apart.

| Gate | Command | What it enforces |
| --- | --- | --- |
| Tests | `make test` | 270 tests. Every closed form is checked against an independent computation: numerical integration, direct Monte Carlo, or brute force. Tolerances are stated at each assertion. |
| Reproducibility | `make verify` | 45 artefacts regenerated into a scratch directory and compared with the committed copies. CSV field-wise at `1e-9`; PDF and PNG by SHA-256. Figure output carries no embedded timestamp, so the comparison is exact. |
| Wording | `make phrases` | 54 patterns for claims retracted in an earlier review round. Guards against an overstatement removed from one section reappearing in another later. |
| Release | `python code/make_release.py` | All of the above, plus a clean LaTeX log, resolved front-matter metadata, no draft label, deposit metadata that parses, and every release document present. |

`make check` runs the first three. The release gate refuses to build if any fails; `--allow-draft`
bypasses only the metadata and draft-label checks, for intermediate artefacts.

## The audit trail

The manuscript has been through five internal review rounds and one external one, each of which found real errors. The record is
kept because a paper arguing that published claims need checking should show its own being checked.

| Document | Contents |
| --- | --- |
| `docs/external_review_round_one.md` | external review, three passes: one blocking finding and fourteen corrections |
| `docs/final_local_revision_review.md` | the fifth round, twelve local corrections |
| `docs/targeted_final_review.md` | the fourth round, nine targeted issues |
| `docs/final_revision_issue_matrix.md` | the seventeen third-round issues, with resolutions |
| `docs/final_adversarial_review.md` | hostile pass over every theorem, proposition and table |
| `docs/final_claim_dependency_audit.md` | every claim, its category, its support, and its referent |
| `docs/adversarial_mathematical_review.md`, `docs/adversarial_review_round2.md` | earlier rounds |
| `docs/detemple_overlap_audit.md` | overlap with Detemple, Garcia and Rindisbacher, with quotations |
| `docs/bibliography_audit.md`, `docs/bibliography_audit_round2.md` | references against primary sources |
| `docs/grid_diagnostic_methodology.md` | what the candidate-state grid does and does not establish |
| `docs/application_claims_dependency_matrix.md` | what each application claim rests on |
| `docs/repository_audit.md` | build and reproducibility baseline |

Three publication-blocking errors were found and fixed in the third round alone, two of them false
statements rather than gaps: a missing Moore–Penrose magnitude condition in Proposition E.2, an
unlocalised maximiser in Proposition 6.2, and an invalid inference from a shrinking region to
reduced occupation time. Two of the fourth round's findings were errors *introduced by* the third
round's fixes — a misread variance ratio and a miscounted correlation — which is the argument for the
wording gate above: each round's corrections are themselves new claims and need checking on the same
terms as the original text. The fifth round found a correct closed-form result whose every verbal
gloss stated the limit in the wrong direction, with the disproving numbers printed in the paper's own
table three lines below the caption asserting it; four earlier rounds had checked the formula and
read the prose as agreeing with it. The first **external** review then found a blocking error none of
the five had: a remark calling an inequality vacuous when it was in fact equivalent to the
compatibility condition the same appendix had just established. Every internal round had checked
phrasings; an independent reader checked the algebra. Claims withdrawn across the rounds are recorded
in the change logs rather than quietly deleted.

Every claim in both documents is labelled as one of: proved theorem, proved algebraic proposition,
conditional statement, numerical diagnostic, statement reported by the original authors, unknown
implementation detail, or literature-based claim. `docs/final_claim_dependency_audit.md` is the
index.

## Building by hand

Both documents use `biblatex` with the `biber` backend and compile from inside `paper/` so the
relative `figures/` and `tables/` paths resolve. They share a preamble and a bibliography but
neither inputs the other, so they build independently and in either order. `make pdf` drives
`latexmk` for both, which orders the passes correctly. To run the cycle yourself, let each pass
finish, and repeat it with `companion` in place of `main`:

```bash
cd paper
pdflatex -interaction=nonstopmode main.tex
biber main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

All `make` targets: `all`, `figures`, `pdf` (alias `paper`), `theory`, `companion`, `test`,
`verify`, `phrases`, `check`, `clean`.

## Archiving

The repository is linked to Zenodo, which archives it automatically on every GitHub release.
`.zenodo.json` is read by that integration and supplies the deposit metadata: description, creators,
keywords, licence, and the related identifiers that register this work as **reviewing**
`10.1016/S0304-405X(01)00093-9` and citing the four asymptotic analyses it is positioned against.

What Zenodo archives is a snapshot of the repository at the tagged commit, not the contents of
`dist/`, which is gitignored. That snapshot is self-contained: it carries both `.tex` sources and
both compiled PDFs, the generated figures and tables, all of `code/` and `tests/`, and the audit
documents in `docs/`. Anyone with the tarball can rebuild both documents and reproduce every
artefact. The bundles under `dist/` remain useful for sending the paper to a person rather than to an
archive, and `code/make_release.py` still produces them.

To publish a new version, tag a release. Zenodo mints a fresh version DOI and updates the concept
DOI, which always resolves to the newest version. Later revisions should go out as new releases of
the same repository rather than as separate deposits, so the concept DOI keeps resolving correctly.

The article under review is not in the repository and never has been: `reference/` is gitignored and
appears in no commit on any branch, so nothing third-party is archived.

## Licence

Everything here, manuscript and code alike, is released under the
[Creative Commons Attribution 4.0 International Licence](https://creativecommons.org/licenses/by/4.0/);
`LICENSE` carries the full text. Share and adapt for any purpose, including commercially, with
appropriate credit.

The article under review is not part of this repository and carries its own copyright. The local
`reference/` directory is gitignored and is never committed or distributed.

## Citation

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21719868.svg)](https://doi.org/10.5281/zenodo.21719868)

Cite the **concept DOI**, which represents every version and always resolves to the most recent one:

> Ribeiro, D. (2026). *Dimensional Asymptotics of Euler-Based Simulated Likelihood for
> Multidimensional Diffusions*. Zenodo. <https://doi.org/10.5281/zenodo.21719868>

```bibtex
@misc{Ribeiro2026DimensionalAsymptotics,
  author    = {Ribeiro, Diogo},
  title     = {Dimensional Asymptotics of {Euler}-Based Simulated Likelihood
               for Multidimensional Diffusions},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.21719868},
  url       = {https://doi.org/10.5281/zenodo.21719868}
}
```

| DOI | Refers to | Status |
| --- | --- | --- |
| [`10.5281/zenodo.21719868`](https://doi.org/10.5281/zenodo.21719868) | all versions; resolves to the latest | **cite this** |
| [`10.5281/zenodo.21848464`](https://doi.org/10.5281/zenodo.21848464) | v1.5.0 | superseded: uniform law labelled proved; its proof is incomplete |
| [`10.5281/zenodo.21834941`](https://doi.org/10.5281/zenodo.21834941) | v1.4.0 | superseded: introduces the uniform law whose proof is incomplete |
| [`10.5281/zenodo.21830098`](https://doi.org/10.5281/zenodo.21830098) | v1.3.0 | superseded: wrongly reports a rate condition `N ≫ S^(2/K)` for the uniform step |
| [`10.5281/zenodo.21823961`](https://doi.org/10.5281/zenodo.21823961) | v1.2.0 | superseded: weaker collapse theorem, scaling law resting on (A5) |
| [`10.5281/zenodo.21763715`](https://doi.org/10.5281/zenodo.21763715) | v1.1.0 | superseded: the single-document form, nothing known to be wrong |
| [`10.5281/zenodo.21760062`](https://doi.org/10.5281/zenodo.21760062) | v1.0.3 | superseded: critical case without the limit law |
| [`10.5281/zenodo.21729471`](https://doi.org/10.5281/zenodo.21729471) | v1.0.2 | superseded: Proposition E.2 omits `\|ρ_ww*\| ≤ 1` |
| [`10.5281/zenodo.21728285`](https://doi.org/10.5281/zenodo.21728285) | v1.0.1 | superseded: Remark E.6 wrongly calls a condition vacuous |
| [`10.5281/zenodo.21719869`](https://doi.org/10.5281/zenodo.21719869) | v1.0.0 | superseded: Proposition C.1 limit stated in the wrong direction |

Zenodo issues a version DOI only when a release is published, and the identifier is not predictable,
so the row for the newest release appears in the first commit after it, not in the release itself.
The concept DOI is the one to cite and never changes. Pin a version DOI only when you need that
exact archived snapshot, for instance when quoting a page or theorem number that a later revision
could move.

What the Zenodo record holds is the repository as a single zip, since that is what the GitHub
integration deposits; both PDFs are inside it under `paper/`. For a direct download of either paper,
use the [release assets](https://github.com/DiogoRibeiro7/sml_diffusions_paper/releases/latest) —
GitHub release assets are not ingested by Zenodo, so the two are separate routes to the same files.

**Every superseded version carries a mathematical error the next one corrects**, and the table names
each. Zenodo records are immutable, so they stay resolvable; listing them with their defects is
deliberate, so that a reader who meets one can learn its status here rather than rediscover the
problem. The corrections came from review — five internal rounds and one external — and the record of
what each found is in `docs/`.

`CITATION.cff` carries the same metadata in Citation File Format, which GitHub renders as a "Cite
this repository" control and which `cffconvert` turns into BibTeX, RIS and other formats. It also
records Brandt and Santa-Clara (2002) as the article under review. A test asserts that the title,
author ORCID, affiliation, licence and DOI agree across `CITATION.cff`, `.zenodo.json` and
`paper/main.tex`, so they cannot drift apart. Both documents are deposited in the same record, so
one concept DOI covers the pair.
