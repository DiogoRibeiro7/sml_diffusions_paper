# Change log, the curvature identity

Baseline `1f1e35f`. The step the previous round reported as the substantive obstacle is closed, and
a defect in that round's measurement of the maximiser is corrected.

## The obstacle, and why it was not one

The previous round left this open: does `grad^2 G_S(theta_0)` converge to the Hessian of `G`? Without
it the exact score moment cannot be turned into a statement about the estimator, since the
displacement is score divided by curvature.

The difficulty as posed was real. Differentiating the criterion pathwise gives `grad^2 psi = 2 S^{2/K} I`
wherever the nearest atom is locally fixed, but `psi` is a *minimum* of parabolas, so it has concave
kinks on the surfaces where the nearest atom switches, contributing a negative singular measure.
Taking expectations leaves `grad^2 G_S` as the difference between `2 S^{2/K} I` and an expected
singular part that must cancel it to relative precision `S^{-2/K}`. Bounding the pieces separately
gives nothing.

**That is an artefact of the route.** `theta` enters `G_S` only through a noncentrality parameter.
The atoms of cloud `n` are centred at `DeltaY_n`, so conditionally the law of `rho_S(theta)` depends
on `theta` only through `m = ||theta - DeltaY_n||`; and `||theta - DeltaY_n||^2` is noncentral
chi-squared with noncentrality `||theta - theta_0||^2`. Writing that as a Poisson mixture, with
`a_j = E[g_S(sqrt(chi^2_{K+2j}))]` and `u = ||theta - theta_0||^2 / 2`,

    G_S = exp(-u) sum_j u^j a_j / j!,

so differentiating `G_S` is differentiating a Poisson mixture in its parameter. Hence

    grad G_S(theta_0) = 0,    grad^2 G_S(theta_0) = (a_1 - a_0) I,

exactly, for every `S`: the curvature is a difference of two ordinary criterion values, each `O(1)`,
with no singular measure and no cancellation of divergent terms.

Convergence `a_j^{(S)} -> a_j` is then the interchange proposition with the weighting `chi^2_K`
replaced by `chi^2_{K+2j}`. Only two features of the weighting are used there, and neither changes:
the tail is Gaussian, and the dominating function is integrable, which requires
`E exp(chi^2_{K+2j} / (K sigma^2)) < infinity`, that is `K sigma^2 > 2` — independent of `j`. So

    grad^2 G_S(theta_0) -> V I,   V = 2 G(theta_0) / (K sigma^2 - 2),

the Hessian of `G`. Verified against an independent finite-difference curvature, agreeing to four
decimals at `K = 4` from `S = 10^2` to `10^10`.

## What this buys

The prediction `sqrt(N) ||theta~ - theta_0|| ~ 2 S^{1/K} sqrt(a_0) / (a_1 - a_0)` is now a *number*
at finite `S`, using the actual curvature rather than its limit. That matters because the limit is
exactly what the reachable range is short of: the curvature reaches only 0.40, 0.54, 0.67 and 0.87
of `V` at `S = 10^2, 10^3, 10^4, 10^6`. The asymptotic form of the prediction is therefore
untestable at any simulable `S`, while the finite-`S` form is testable.

Measured against simulation it holds: discrepancies of `-0.16`, `+1.60` and `+1.58` standard errors
at `S = 16, 81, 256`, with no systematic sign. That is evidence the linearisation does what it
should where it can be checked. It is not proof, and the manuscript says so.

## A defect in the previous round's measurement

The maximiser table committed in `1f1e35f` iterated the fixed point from the origin — which in this
model **is** `theta_0`. The estimator is the global minimiser and `theta_0` is unknown in practice,
so that returned the local minimum in the truth's own basin.

A diagnostic found random restarts beating that solution in **28 of 30** replications, with the
understatement growing in `S`: 2.6, 3.3 and 14.1 per cent at `S = 16, 81, 256`. The bias flattered
the estimator and grew precisely where the criterion roughens, so it would have suppressed the trend
at issue. At `S = 256` the measured error rises from 3.79 to 4.31 once the search starts elsewhere.

The generator now searches from eight random starts and keeps the best. With a finite restart budget
that is still an upper bound on the criterion, hence a lower bound on the estimator's error, and the
manuscript states it as such. `Remark A.9` records the pitfall, because it is the kind of error that
produces a plausible table rather than an obviously broken one.

## Where the question now stands

Proved: the score at the truth, exactly, at order `S^{1/K}`; the curvature at the truth, exactly, and
its convergence to a positive limit.

Not proved: the linearisation joining them. That needs a modulus-of-continuity bound for the
empirical process near `theta_0`, for which the entropy estimates behind the uniform law are the
natural input, plus control of the remainder beyond the quadratic term in the Poisson expansion —
whose coefficients are the explicit finite differences of the `a_j`.

If completed, the consequence is definite: consistent but not root-`N` consistent, so
`sqrt(N)(theta~ - theta^)` diverges. That contradicts the *conclusion* of Lemma 5, not merely its
proof, and would leave Theorem 1's conclusion true in this model, Theorem 2's false, and both proofs
invalid.

## Machinery

- `code/generate_results.py`: `central_chi_coefficient` computes `a_j`; the maximiser generator
  searches globally and now reports the curvature and the finite-`S` prediction alongside the
  measurement.
- `tests/test_analytics.py`: the curvature identity is checked against an independent
  finite-difference route sharing no code beyond the conditional criterion; the convergence to `V`
  is checked against the closed form; the prediction is rebuilt from its two ingredients rather than
  copied; and the agreement with simulation is asserted at two standard errors. The test also
  asserts the search uses restarts, so the old bias cannot return silently.

## Verification

Both documents build with zero errors, zero overfull and underfull boxes and no undefined references
or citations: 62 and 26 pages. All generated artefacts reproduce bit-for-bit. No forbidden phrase
appears in any searched file.
