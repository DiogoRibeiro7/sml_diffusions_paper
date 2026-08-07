# Change log, the score at the truth

Baseline `d21ed04` (v1.4.0). The `sqrt(N)` question is advanced but **not** settled. What is new is
an exact result about the score, and a quantitative explanation of why the step from the score to
the estimator resists both proof and simulation.

## What is proved

The scaled nearest-atom criterion is differentiable wherever each cloud has a unique nearest atom,
which holds almost surely, and

    grad psi_n(theta) = 2 S^{2/K} (theta - b_{n,s*}),   s* = argmin_s ||theta - b_{n,s}||.

The joint law of the configuration is invariant under rotations about `theta_0`, so the score there
is centred, and independence across `n` gives, **exactly and for every N and S**,

    E ||grad X_N(theta_0)||^2 = 4 S^{2/K} G_S(theta_0) / N.

Since `G_S(theta_0) -> G(theta_0) > 0`, the root mean square score at the truth is asymptotically
`2 sqrt(G(theta_0)) S^{1/K} / sqrt(N)`, which **diverges in S** at every fixed `N`.

Checked against direct simulation at `K = 6`, where the committed table agrees to 0.2, 1.1 and 0.8
per cent at `S = 10^2, 10^3, 10^4`.

The check is not run at the application's `K = 4`, and the reason is itself worth recording. The
sampling variance of an estimate of `E||grad psi||^2` is governed by `E[rho^4]`, finite only when
`K sigma^2 > 4`. At `K = 4` that fails exactly, so the estimate has infinite variance and agreement
is noisy at any number of draws: a first version of the table sat at 5 per cent off at `S = 10^4`
and would have made the test flaky. `K = 6` puts the check inside the integrable region. The same
boundary is why the functional central limit theorem is delicate at `K = 4`.

This is the score route that `rem:score_route` recommended as "the first thing to try", rather than
the nearest-neighbour route, and it is the object Lemma 4 of Brandt and Santa-Clara concerns.

## What it implies, and why that is a prediction rather than a result

The exact criterion in this model has gradient of order `N^{-1/2}` at `theta_0` and curvature `2`,
so it implies a displacement of order `N^{-1/2}`. The simulated criterion has gradient of order
`S^{1/K} N^{-1/2}` against a limiting curvature `V = 2 G(theta_0)/(K sigma^2 - 2)` free of `S`. The
`M`-estimator linearisation therefore predicts

    sqrt(N) ||theta~ - theta_0||  ~  S^{1/K},

so the estimator would be consistent but not root-`N` consistent, and the *conclusion* of Lemma 5
would fail rather than merely its proof.

**That is recorded as a prediction and not claimed.** The step from score to estimator divides by
the curvature of `G_S` near `theta_0`, not by its limit, and the difference is not a technicality.

## The obstacle, measured

The finite-`S` criterion approaches its limit slowly in level and far more slowly in shape. At
`K = 4` the scale-free shape ratio `G_S(theta_0 + 1.5e)/G_S(theta_0)` runs

| S | shape ratio | fraction of limit |
|---|---|---|
| 10^2 | 1.650 | 0.536 |
| 10^3 | 1.866 | 0.606 |
| 10^4 | 2.092 | 0.679 |
| 10^6 | 2.512 | 0.816 |
| 10^10 | 2.971 | 0.965 |
| limit | 3.080 | 1 |

So the criterion is roughly a third less curved than its limit at `S = 10^4`, and still short at
`S = 10^6`. Since the score grows like `S^{1/K}` and the displacement divides by this curvature, the
two dependences on `S` very nearly cancel over the whole reachable range.

The maximiser itself is computable exactly, because `grad X_N(theta) = 0` reads
`theta = N^{-1} sum_n b_{n,s*(n,theta)}`, a fixed point of "average the nearest atoms". At
`N = 8,000`, `K = 4` and 24 replications the ratio
`sqrt(N)||theta~ - theta_0|| / sqrt(N)||theta^_N - theta_0||` is 2.05, 2.13 and 2.05 at
`S = 16, 81, 256`.

Two readings, and they must be separated.

**Solid.** The simulated maximiser carries roughly twice the error of the exact MLE at every
simulation size shown. That loss is real at sizes anyone would use, and it is not small.

**Not solid.** The growth of that ratio in `S`, which is the quantity the prediction is about. The
standard errors are 8-9 per cent of the level, so a growth factor carries about 14 per cent error.
Two runs of this experiment differing only in the random stream returned growth factors of 1.00 and
1.54 against a prediction of 2.00. An intermediate draft of this note quoted the 1.54 as though it
were a measurement; it was one draw. Twenty-four replications do not resolve the trend, and the
count that would is not worth its cost, because the criterion-shape table already supplies the
reason the growth is suppressed here with no simulation at all.

## Where this leaves the question

Established: the discrepancy between the simulated and exact criteria is present **in the score**,
exactly, and at order `S^{1/K}`.

Not established: that it survives division by the curvature. A proof would need `grad^2 G_S`
controlled near `theta_0` uniformly in `S`. The numbers above identify that as the substantive
difficulty rather than a technical one, which is a sharper statement of the obstacle than the
previous "functional central limit theorem" formulation.

## Machinery

- `code/generate_results.py`: `make_score_moment_table` and `make_criterion_shape_table`.
- `tests/test_analytics.py`: four new tests. The exact moment is recomputed from its definition
  rather than copied from the generator and checked against simulation; the score is checked to grow
  like `S^{1/K}` once the slowly-converging factor is divided out; and the shape table is checked to
  stay below 90 per cent of its limit at every reachable `S`, which is the claim that licenses
  reporting the rate as open.

## Verification

Both documents build with zero errors, zero overfull and underfull boxes and no undefined references
or citations: 60 and 26 pages. 268 tests pass. All generated artefacts reproduce bit-for-bit. No
forbidden phrase appears in any searched file. All bibliography DOIs resolve against Crossref.
