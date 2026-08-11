# Grid diagnostic methodology

> **SUPERSEDED — retained for the audit history.** This document records the state of the work at the time it was written, including statements later corrected or withdrawn. Do not read it as the current theorem statement; see `docs/change_log_referee_round_three.md` for the current round and `paper/main.tex` for the statements themselves.

What the candidate-state grid in Appendix E computes, exactly, and what it does not compute. This
document exists because an earlier version of the analysis described the grid as a sweep over the
"reachable state space" and quoted a percentage of it, which claims more than a grid can support.

## What is computed

For each candidate combination of

- domestic interest rate `r`,
- foreign interest rate `r*`,
- log exchange rate `e`,
- incompleteness level `eps^2`,

the diagnostic solves the inverse variance identity for volatility and records how many **positive**
solutions exist: none, exactly one, or two. Under model C the identity is the implicit quadratic of
Appendix D,

    (1 - kappa_b) v^2 - 2 eta_t v - (Q_t + zeta^a_t + eps^2) = 0,

so the answer is a property of that quadratic's coefficients at the candidate point. Where a
positive root exists, the four-dimensional Brownian correlation matrix is assembled at it and its
minimum eigenvalue is recorded. One matrix is built per positive root, so a two-root point
contributes two branch-specific matrices.

This is an algebraic question about a map evaluated at a point.

## What is not computed

The grid establishes nothing about any of the following, and no statement in the manuscript may rest
on it as though it did:

- dynamic accessibility of a candidate point by the diffusion;
- the support of the process;
- the probability of visiting any point or region;
- occupation times;
- the invariant distribution;
- the Lebesgue or any other measure of a subset of the state domain;
- empirical frequency in the observed sample.

Consequently a count of grid points is reported as a count of grid points. It is never converted to
a percentage of a state space, and never read as a probability.

Establishing reachability would require a support theorem, an accessibility argument, analysis of
the transition or invariant densities, or direct simulation under a fully specified and well-posed
process. The last is obstructed by the very failure the diagnostic exhibits.

## Grid designs

Six designs, all in `GRID_DESIGNS` in `code/check_correlation_matrix.py`. Rate multipliers apply to
the long-run means `theta` and `theta_star`; endpoints are included in every `linspace` and
`logspace`.

| Design | Rate values | Spacing | Rate range | `e` values | `e` range | `eps^2` levels |
| --- | ---: | --- | --- | ---: | --- | ---: |
| baseline | 26 | linear | 0.05 to 5 | 21 | [-2, 2] | 4 |
| denser | 41 | linear | 0.05 to 5 | 33 | [-2, 2] | 4 |
| wider fx | 26 | linear | 0.05 to 5 | 21 | [-4, 4] | 4 |
| narrower fx | 26 | linear | 0.05 to 5 | 21 | [-0.5, 0.5] | 4 |
| log rates | 26 | logarithmic | 0.05 to 5 | 21 | [-2, 2] | 4 |
| more eps | 26 | linear | 0.05 to 5 | 21 | [-2, 2] | 6 |

The `eps^2` levels are `{0, 0.002, 0.01, 0.05}` for the first five designs and
`{0, 0.001, 0.005, 0.01, 0.02, 0.05}` for the last.

## Tolerances

Stated once in code, as module constants, so that the manuscript caption cannot drift from what is
computed.

| Constant | Value | Meaning |
| --- | --- | --- |
| `POSITIVE_ROOT_TOLERANCE` | `1e-12` | a root counts as positive when it exceeds this |
| `REPEATED_ROOT_TOLERANCE` | `1e-9` | two roots count as repeated when they differ by less |
| `NEGATIVE_EIGENVALUE_TOLERANCE` | `-1e-10` | an eigenvalue counts as negative below this |

## Results

Produced by `code/generate_results.py` into `paper/tables/grid_sensitivity.csv` and `.tex`, and
reproduced bit-for-bit by `make verify`.

| Design | Points | No root | One | Two | Matrices | Worst `λ_min` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 56,784 | 37,536 | 0 | 19,248 | 38,496 | +0.4455 |
| denser | 221,892 | 148,021 | 0 | 73,871 | 147,742 | +0.4380 |
| wider fx | 56,784 | 32,804 | 0 | 23,980 | 47,960 | +0.4455 |
| narrower fx | 56,784 | 54,542 | 0 | 2,242 | 4,484 | +0.4059 |
| log rates | 56,784 | 37,065 | 0 | 19,719 | 39,438 | +0.4460 |
| more eps | 85,176 | 56,416 | 0 | 28,760 | 57,520 | +0.4455 |

## Interpretation

The counts are properties of each grid, not of the specification. The proportion of no-root points
ranges from 58 per cent to 96 per cent across these six designs, which is precisely why no single
percentage may be quoted as a model property; it is a function of where the grid was placed.

Two findings are stable across every design and are the only ones the manuscript draws:

1. **No candidate point, on any grid, admits exactly one positive root.** This confirms
   Proposition D.1(ii) computationally: when `kappa_b > 1` the quadratic opens downward and positive
   roots arrive in pairs.
2. **No candidate point, on any grid, yields an indefinite correlation matrix.** Where the inverse
   map is defined, the resulting matrix is comfortably valid.

Together these support the statement that the U.S.–U.K. model-C inverse mapping fails to be globally
defined and is never single-valued where it is defined. They do not support any statement about how
often the diffusion visits the region where it fails.
