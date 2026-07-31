# Dimensional Asymptotics of Euler-Based Simulated Likelihood for Multidimensional Diffusions

A mathematical manuscript, the code that generates every number in it, and the machinery that keeps
the two in agreement.

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

**What the paper does not claim.** It does not prove that the resulting argmax estimator is
inconsistent — Section 7.6 and Appendix H set out exactly what such a proof would require and why
the density counterexample does not transfer. It does not claim the published empirical estimates
are wrong. Application-specific findings are labelled as diagnostics, not theorems.

## Quick start

```bash
pip install -r requirements.txt
make            # regenerate figures and tables, then build the PDF
make check      # tests, reproducibility, forbidden-phrase gate
```

The manuscript builds to `paper/main.pdf` (55 pages). Python 3.11+, NumPy, SciPy, pandas and
Matplotlib; LaTeX with `latexmk` and `biber`.

## Layout

```text
paper/                    the manuscript and everything it includes
  main.tex                LaTeX source
  main.pdf                compiled manuscript
  references.bib          bibliography, 27 entries, its 24 DOIs Crossref-verified
  figures/                5 figures, vector PDF and PNG (generated)
  tables/                 10 LaTeX tables and 13 CSV files (generated)
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
  test_singular_psd_condition.py the block PSD lemma of Appendix E
  test_antithetic.py            the pair-average variance and the h-exponent
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
| Tests | `make test` | 193 tests. Every closed form is checked against an independent computation: numerical integration, direct Monte Carlo, or brute force. Tolerances are stated at each assertion. |
| Reproducibility | `make verify` | 33 artefacts regenerated into a scratch directory and compared with the committed copies. CSV field-wise at `1e-9`; PDF and PNG by SHA-256. Figure output carries no embedded timestamp, so the comparison is exact. |
| Wording | `make phrases` | 22 patterns for claims retracted in an earlier review round. Guards against an overstatement removed from one section reappearing in another later. |
| Release | `python code/make_release.py` | All of the above, plus a clean LaTeX log, resolved front-matter metadata, no draft label, deposit metadata that parses, and every release document present. |

`make check` runs the first three. The release gate refuses to build if any fails; `--allow-draft`
bypasses only the metadata and draft-label checks, for intermediate artefacts.

## The audit trail

The manuscript has been through three review rounds, each of which found real errors. The record is
kept because a paper arguing that published claims need checking should show its own being checked.

| Document | Contents |
| --- | --- |
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
reduced occupation time. Claims withdrawn across the rounds are recorded in the change logs rather
than quietly deleted.

Every claim in the manuscript is labelled as one of: proved theorem, proved algebraic proposition,
conditional statement, numerical diagnostic, statement reported by the original authors, unknown
implementation detail, or literature-based claim. `docs/final_claim_dependency_audit.md` is the
index.

## Building by hand

The document uses `biblatex` with the `biber` backend and compiles from inside `paper/` so the
relative `figures/` and `tables/` paths resolve. `make pdf` drives `latexmk`, which orders the passes
correctly. To run the cycle yourself, let each pass finish:

```bash
cd paper
pdflatex -interaction=nonstopmode main.tex
biber main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

All `make` targets: `all`, `figures`, `pdf` (alias `paper`), `test`, `verify`, `phrases`, `check`,
`clean`.

## Archiving

The record is deposited on Zenodo. `.zenodo.json` holds the deposit metadata, including the related
identifiers that register this work as **reviewing** `10.1016/S0304-405X(01)00093-9` and citing the
four asymptotic analyses it is positioned against. The repository is private, so the deposit is made
manually; the GitHub–Zenodo integration requires a public repository, and `.zenodo.json` therefore
serves as the source for the deposit form rather than being read automatically.

Three files make up the deposit, all produced by `code/make_release.py`:

| File | Contents |
| --- | --- |
| `dist/main.pdf` | the manuscript |
| `dist/source.zip` | LaTeX and Python sources, figures, tables, tests, documents |
| `dist/reproducibility.zip` | the code and manifest needed to regenerate every artefact |

Zenodo mints a concept DOI that always resolves to the newest version, alongside a DOI per version.
Later revisions should be published as new versions of the same record rather than as separate
deposits, so the concept DOI keeps resolving correctly.

## Licence

Everything here, manuscript and code alike, is released under the
[Creative Commons Attribution 4.0 International Licence](https://creativecommons.org/licenses/by/4.0/);
`LICENSE` carries the full text. Share and adapt for any purpose, including commercially, with
appropriate credit.

The article under review is not part of this repository and carries its own copyright. The local
`reference/` directory is gitignored and is never committed or distributed.

## Citation

`CITATION.cff` carries the metadata in Citation File Format, which GitHub renders as a "Cite this
repository" control and which `cffconvert` turns into BibTeX, RIS and other formats. It also records
Brandt and Santa-Clara (2002) as the article under review.

Once the Zenodo record exists, add its DOI to `CITATION.cff` as an `identifiers` entry and to this
section. A test asserts that the title, author ORCID, affiliation and licence agree across
`CITATION.cff`, `.zenodo.json` and `paper/main.tex`, so those four cannot drift apart.
