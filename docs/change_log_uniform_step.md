# Change log, the uniform-in-theta step and a correction

> **SUPERSEDED — retained for the audit history.** This document records the state of the work at the time it was written, including statements later corrected or withdrawn. Do not read it as the current theorem statement; see `docs/change_log_referee_round_three.md` for the current round and `paper/main.tex` for the statements themselves.

Baseline `d0d6112` (v1.3.0). The last open step in the argmax question is closed, the argmax
question itself is settled in one direction, and a claim published in v1.3.0 is corrected.

## The correction, first

v1.3.0 said, in Remark A.5, that the uniform-in-`theta` statement
"plausibly requires `N >> S^{2/K}`", and observed that the published rate conditions constrain `N`
from above rather than below, so the requirement pointed "the awkward direction".

**That was wrong, and the error was mine.** The reasoning ran: each summand
`psi_n(theta) = S^{2/K} min_s ||theta - b_{n,s}||^2` is 1-Lipschitz in `theta` up to a factor
`2 S^{2/K} rho`, so its Lipschitz constant is of order `S^{1/K}` and diverges; chaining over the
index set then costs `S^{1/K}`, giving `N >> S^{2/K}`.

The Lipschitz constant does diverge, and the criterion really is rough at scale `S^{-1/K}`. The
error was in what that implies. The chaining bound was taken over the **metric diameter of the index
set**, which is of order `S^{1/K}`, where it should be taken over the **envelope of the function
class**. After truncation the envelope is bounded, the diverging Lipschitz constant enters the
entropy only through its logarithm, and the maximal inequality costs `sqrt(log S)` rather than
`S^{1/K}`.

Nothing in v1.3.0 depended on the claim -- it was a description of an open step, not a hypothesis of
any theorem -- so no result there is invalidated. But the description was misleading in a way that
mattered: it suggested a tension with the published conditions where there is none.

**How it was caught.** Not by rereading the argument. The two routes make different predictions for
how the uniform deviation grows with `S`, a power against a logarithm, and the ratio of uniform to
pointwise deviation isolates exactly that, cancelling the `1/sqrt(N)` and the scale of the summand.
Across two decades the observed ratio grows by `1.35`, against `1.41` predicted by the logarithm and
`2.51` by the power. The numbers are in `paper/tables/uniform_scaling.csv` and the comparison is in
Table 7.

## The uniform law

Proposition A.4 proves that if `N / log S -> infinity` then
`sup_theta |X_N(theta) - G(theta)| -> 0` in probability, for `theta` ranging over any compact set.
The proof has three parts:

- *Uniform integrability over the compact.* The proof of the interchange proposition already bounds
  the conditional upper tail of `psi` by a Weibull tail with scale `f_n(theta)^{-2/K}` and no
  dependence on `S`. Over a compact set of `theta` that scale is at most
  `2 pi sigma^2 exp{(||DeltaY_n - theta*|| + D)^2 / (K sigma^2)}`, integrable for a small enough
  slack exactly because `K sigma^2 > 2` is strict. So the tail expectation is small uniformly in
  both `S` and `theta`.
- *Entropy of the truncated class.* The truncated class has constant envelope `tau`; the
  Lipschitz-in-parameter structure gives bracketing numbers `(C D S^{2/K}/eta)^K`, so
  `log N_[](eta) <= 2 log S + K log(C D / eta)`. The entropy integral is `tau (sqrt(log S) + sqrt K)`
  and the maximal inequality gives `tau sqrt(log S / N)`.
- *Choice of truncation.* Take `tau_N -> infinity` slowly enough that `tau_N sqrt(log S / N) -> 0`,
  possible precisely when `N / log S -> infinity`.

Passing from `E X_N` to `G` uses monotonicity: `E X_N` depends on `theta` only through
`r = ||theta - theta_0||` and is nondecreasing in it, because a noncentral chi-squared distribution
function is nonincreasing in its noncentrality; monotone pointwise convergence to a continuous limit
on a compact interval is uniform.

`N / log S -> infinity` is weak, and compatible with the published conditions: `N = S^{1/5}` meets
both it and `N / S^{1/4} -> 0`, with the margin widening in `S`.

## The consequence: consistency along the collapsing sequence

Corollary A.6. If `N / log S -> infinity` and `M / (S^{2/K} log S) -> infinity`, the simulated
maximum likelihood estimator in the location model converges in probability to the true parameter.
Along `M = S = n` with `K > 2` the second condition is automatic, so consistency needs only
`N / log n -> infinity`.

That is the same sequence along which the collapse corollary makes the simulated transition density
converge in probability to zero at every fixed pair of points. **The density collapses and the
maximiser is consistent, simultaneously, in the same model on the same designs.**

This does not weaken the critique; it sharpens it. The paper has said throughout that refuting the
density statements of Lemmas 2 and 3 does not show the estimator inconsistent, and has been careful
to call that a gap rather than a hedge. It is now a theorem in the most tractable case: the density
counterexample provably does not transfer, and no argument proceeding through pointwise density
behaviour alone can make it transfer.

## What is still open, and it is narrower

The `sqrt(N)` statement, which would refute the *conclusion* of Lemma 5 rather than its proof, needs
three things the paper does not supply, now named individually:

1. A rate for `E X_N - G`. The interchange gives convergence but not speed, and the quadrature shows
   it is slow. The curvature comparison needs `E X_N - G = o(N^{-1})` uniformly near `theta_0`.
2. A functional central limit theorem for `sqrt(N)(X_N - E X_N)` near the minimiser, where the
   summands are not differentiable in `theta` and, when `K sigma^2 <= 4`, not square integrable
   either. This is the substantive one.
3. The sandwich slack negligible against the *variation* rather than the level, which means
   `M >> N S^{2/K} log S`.

## Machinery

- `code/generate_results.py`: `make_uniform_scaling_table`, producing `uniform_scaling.{csv,tex}`.
- `tests/test_analytics.py`: five new tests. The scaling table is checked to follow the logarithm
  rather than the power, and the test first asserts the two predictions are far enough apart to
  discriminate; the ratio is checked to exceed one; the compatibility of `N >> log S` with
  `N << S^{1/4}` is checked asymptotically, with the margin required to widen; the corollary's two
  conditions are checked to hold together on the collapsing diagonal; and the monotonicity the
  Polya argument needs is checked against the quadrature.

Two of those tests failed when first written, both from my own over-tight thresholds rather than
from the mathematics: `S^{1/8} > log S` only past `S = 10^12`, and `K = 3` collapses too slowly for a
fixed bound to serve every dimension. Both are now stated asymptotically, which is what the claims
actually are.

## Verification

Both documents build with zero errors, zero overfull and underfull boxes and no undefined references
or citations: 58 and 26 pages. 264 tests pass. All generated artefacts reproduce bit-for-bit. No
forbidden phrase appears in any searched file. All bibliography DOIs resolve against Crossref.
