# Euler-Based Simulated Likelihood for Multidimensional Diffusions

This directory contains a complete mathematical manuscript, reproducible numerical experiments, figures, and generated tables.

## Main files

- `main.tex` - LaTeX manuscript.
- `main.pdf` - compiled manuscript.
- `references.bib` - bibliography.
- `code/generate_results.py` - reproducible calculations and figures.
- `figures/` - vector PDF and PNG figures.
- `tables/` - generated CSV and LaTeX tables.

## Reproduce the numerical results

```bash
python code/generate_results.py
```

The script uses a fixed random seed and no external data.

## Build the manuscript

The document uses `biblatex` with the `biber` backend.

```bash
pdflatex main.tex
biber main
pdflatex main.tex
pdflatex main.tex
```

## Python dependencies

- Python 3.11+
- NumPy
- SciPy
- pandas
- Matplotlib

## Scope

The manuscript establishes an exact Brownian counterexample, derives dimension-dependent moment and central-limit rates for the endpoint estimator, and analyses the mathematical status of the four-dimensional exchange-rate application. It does not claim that the published finite-sample empirical estimates are necessarily incorrect.
