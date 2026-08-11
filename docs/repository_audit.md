# Repository audit

> **SUPERSEDED — retained for the audit history.** This document records the state of the work at the time it was written, including statements later corrected or withdrawn. Do not read it as the current theorem statement; see `docs/change_log_referee_round_three.md` for the current round and `paper/main.tex` for the statements themselves.

Baseline established before any mathematical revision. No theorem, proof, conclusion, numerical
result, title, or abstract was altered in producing this report.

## Repository structure

```text
paper/
  main.tex                  LaTeX entry point, single file, no \input or \include
  main.pdf                  compiled manuscript (tracked)
  references.bib            biblatex database, 24 entries
  figures/                  5 figures, each as PDF and PNG (generated)
  tables/                   5 tables, each as CSV and LaTeX (generated)
code/
  generate_results.py       all figures and tables
  verify_reproducibility.py regeneration check used by `make verify`
docs/
  repository_audit.md       this file
reference/                  literature under review; untracked and gitignored
Makefile
README.md
requirements.txt
```

There is one LaTeX entry point and no duplicated or obsolete manuscript file. `main.tex` is
self-contained: it defines its own theorem environments and macros in the preamble and pulls in
no local `.sty` or section file.

## Commands

| Purpose | Command |
| --- | --- |
| Everything | `make` |
| Figures and tables | `make figures` |
| PDF only | `make pdf` (alias `make paper`) |
| Reproducibility check | `make verify` |
| Remove LaTeX auxiliaries | `make clean` |

The manuscript is compiled from inside `paper/` so that the relative `figures/` and `tables/`
paths resolve. `latexmk` drives the `pdflatex`/`biber`/rerun cycle.

## Toolchain used for this audit

| Component | Version |
| --- | --- |
| Python | 3.13.5 |
| NumPy | 2.3.5 |
| SciPy | 1.15.3 |
| pandas | 2.3.3 |
| Matplotlib | 3.10.8 |
| pdfTeX | MiKTeX-pdfTeX 4.21 (MiKTeX 25.4) |
| Biber | 2.21 |
| latexmk | 4.87 |

Declared in `requirements.txt`: `numpy>=1.26`, `scipy>=1.11`, `pandas>=2.1`, `matplotlib>=3.8`.
All imports in `code/` are covered by that list or by the standard library. The `save_figure`
helper relies on Matplotlib's `metadata` argument to `savefig`, which requires Matplotlib 3.3 or
later; the declared floor of 3.8 is therefore sufficient.

## Build state

Compiled from a clean state (`make clean && make`).

| Check | Result |
| --- | --- |
| Page count | 27 |
| Undefined references | 0 |
| Undefined citations | 0 |
| Multiply-defined labels | 0 |
| Overfull boxes | 0 |
| Underfull boxes | 0 |
| `hyperref` bookmark warnings | 0 |
| Biber warnings | 0 |
| Missing figure files | 0 |

Three build defects were found and fixed while establishing the baseline. They are recorded here
because each of them was silently tolerated by the previous build procedure.

1. **`aliascnt` declarations were malformed.** The theorem environments were declared as
   `\newtheorem{proposition}{Proposition}` after `\newaliascnt{proposition}{theorem}`, which
   raised `Command \c@proposition already defined` on every run. Under `nonstopmode` pdfTeX
   recovered and still produced a complete PDF, so the error was invisible unless the log was
   read for errors rather than for warnings. Fixed by passing the alias as the shared counter:
   `\newtheorem{proposition}[proposition]{Proposition}`.
2. **The explicit four-pass build was fragile.** A pass that stopped early left a truncated
   `main.aux`, and the next pass then failed inside `\@newl@bel` with a misleading
   `Missing \begin{document}`. Replaced by `latexmk`, which sequences the passes and Biber and
   decides how many reruns are needed.
3. **Two overfull boxes and ten `hyperref` bookmark warnings.** The bookmark warnings came from
   inline math in two subsection titles, now wrapped in `\texorpdfstring`. The overfull boxes
   came from an unbreakable math atom in one sentence and a long hyphenated compound in another.

## Reproducibility

`make verify` regenerates every figure and table into a scratch directory and compares against
the committed copies: CSV field by field with a relative tolerance of `1e-9`, LaTeX tables as
text, and PDF and PNG by SHA-256.

**All 20 artefacts reproduce exactly.**

Reaching that required one change. Matplotlib stamps a `CreationDate` into PDF output and a
`Software` tag into PNG output, so before this audit every rebuild produced byte-different
figures with identical content, and any hash-based check was meaningless. `save_figure` now
passes `metadata={"CreationDate": None}` and `metadata={"Software": None}`.

The fixed seed does control the numerics. `SEED = 20260726` is consumed by a single
`numpy.random.default_rng` instance threaded through the one stochastic routine
(`make_subcritical_distribution_results`); every other artefact is a closed-form evaluation. An
independent re-run of the Monte Carlo table under a different seed and a different summation
order reproduced all reported four-significant-figure values, so the committed table is not
seed-fragile at the precision at which it is quoted.

### Committed artefact digests

SHA-256, first 16 hex characters.

| Artefact | Digest |
| --- | --- |
| `figures/brownian_joint_path_rmse.pdf` | aedbc68ae058ea40 |
| `figures/brownian_joint_path_rmse.png` | 515b47d3b0a69ffd |
| `figures/brownian_second_moment_scaling.pdf` | d4bf50a9b01e5d82 |
| `figures/brownian_second_moment_scaling.png` | 5082effb68a05420 |
| `figures/brownian_subcritical_distribution.pdf` | f65f4ca6c26facb6 |
| `figures/brownian_subcritical_distribution.png` | 6f88da13e6920abe |
| `figures/epsilon_squared_euler_negative_probability.pdf` | f79af0436048e001 |
| `figures/epsilon_squared_euler_negative_probability.png` | 526787a14c2d5df3 |
| `figures/ou_second_moment_scaling.pdf` | 974a92d3dbbd8260 |
| `figures/ou_second_moment_scaling.png` | 61313e3c1fda27b1 |
| `tables/brownian_subcritical_path.csv` | fc643229320352f0 |
| `tables/brownian_subcritical_path.tex` | f0824f764a3738a4 |
| `tables/feller_conditions.csv` | f00c27129818f78c |
| `tables/feller_conditions.tex` | b518edf3ef451713 |
| `tables/implemented_design.csv` | 5aecd19dea1fd13e |
| `tables/implemented_design.tex` | 64733212a6e1d946 |
| `tables/implicit_volatility_coefficients.csv` | 66425d682790fc36 |
| `tables/implicit_volatility_coefficients.tex` | 14c543c509480637 |
| `tables/rate_conditions.csv` | 1eca27d15df676fc |
| `tables/rate_conditions.tex` | e150680f78acc7ce |

## Stale or unused files

| Item | Status |
| --- | --- |
| `.benchmarks/` | Empty `pytest-benchmark` directory, no test suite present. Removed and gitignored. |
| `.mypy_cache/` | Tool cache. Gitignored. |
| `paper/main.bbl-SAVE-ERROR` | `latexmk` failure artefact from a broken build. Removed; the pattern is gitignored. |
| `tables/*.tex` | Generated but not `\input` by the manuscript, which reproduces these tables inline. Retained deliberately as machine-readable companions to the CSV files; noted so the duplication is not mistaken for drift. |

`main.tex` cites 24 of 24 bibliography entries; there are no uncited entries and no citations
without an entry.

## Known limitations of this baseline

- The LaTeX tables under `paper/tables/` duplicate values that are also typeset by hand in
  `main.tex`. Nothing enforces that the two agree. A test asserting agreement is deferred to the
  numerical test-suite task.
- `make verify` checks that committed artefacts match a regeneration on *this* toolchain. It is
  not a cross-platform reproducibility guarantee; a different BLAS could change the Monte Carlo
  table in its final digits, which is why the CSV comparison carries a tolerance rather than
  demanding byte equality.
