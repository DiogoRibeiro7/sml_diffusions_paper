# Change log, the three open problems

Baseline `4bd5eca`. Three problems the manuscript had recorded as open are addressed. Two are
closed. The third is advanced by one of its two named steps, and the remaining step is given a
sharper description than "standard in kind if delicate in execution".

## 1. The logarithmic gap in Theorem 3.3 — closed

**Was.** The theorem assumed `S h^{K/2} (log(1/h))^{K/2} -> 0`, strictly stronger than the
effective-size condition `R_{M,S} -> 0`. Designs in between — the manuscript's own example is
`S = h^{-K/2} / log(1/h)` with `K > 2` — satisfied neither the collapse hypothesis nor the
divergence hypothesis of the central limit theorem, and their behaviour was unsettled. The remark
recording the gap conjectured that the logarithm was an artefact of the proof strategy.

**It was.** The old proof bounded every surviving summand by the largest one and multiplied by `S`.
That forces the exclusion radius to satisfy `r^2 ≍ h log(1/h)` so the largest surviving summand
vanishes, and the extra logarithm then propagates into the ball-probability bound: one factor of
`log(1/h)` per dimension, paid entirely for the crudeness of the step.

**Now.** The theorem holds under `R_{M,S} -> 0` alone. The proof rests on an exact rewriting,

    qhat = (2 pi)^{-K/2} T / lam,   lam = S h^{K/2},   T = sum_s exp(-||y - Z_s||^2 / (2h)),

which makes the effective size the only parameter in sight. Draws are split at radius `sqrt(h) R`.
The near draws are handled by a union bound, `P(some draw within) <= C_K lam R^K`. The far draws are
bounded by their **expectation** rather than by `S` times a pointwise maximum, giving
`E T_far <= lam 2^{K/2} P(chi_K > R)`, and Markov's inequality then yields a bound
`P(chi_K > R) / (eps pi^{K/2})` that **does not involve lam**. That decoupling is the whole point:
`R` may now grow as slowly as needed to keep `lam R^K` small, and such a choice exists whenever
`lam -> 0`. Taking `R = lam^{-1/(2K)}` suffices.

Optimising over `R` instead gives a rate: `P(qhat > eps) <= C lam (log(1/lam))^{K/2}`. The logarithm
has not left the problem, it has moved from the hypothesis to the conclusion, where it costs nothing.

**Consequence.** The threshold at `R_{M,S}` is now sharp. The same quantity that must diverge for the
density-level central limit theorem must vanish for collapse, with no designs left between them.

**Checked.** `paper/tables/collapse_bound.csv` compares the bound with the exact exceedance
probability at seven designs; it holds at all seven and is tight to a factor of about four. The
comparison needs no simulation of the full estimator: each summand depends on its draw only through
the distance to the target, so the count inside a ball is binomial and the squared radius inside it
is a truncated chi-squared. Designs with `S = 10^7` are therefore evaluated exactly. Separately, a
run along the manuscript's own gap example, `lam = 1/log(1/h)` at `K = 4` and `S` up to `5.4 x 10^14`,
shows the median falling to `0.15` of the true density while the mean stays at `1.00`, which is
unbiasedness — collapse inside the region the old theorem could not reach.

## 2. Assumption (A5) and the Aronson replacement — closed, in the form that matters

**Was.** (A5) requires the Euler preterminal density at time `1-h` to converge uniformly on a ball to
the diffusion density at time `1`. It is not primitive: it bundles a discretisation limit with
continuity of `t -> p_t` in the uniform topology, and the manuscript conceded that appealing to
Bally–Talay to justify it while citing (A1)–(A2) as the primitive conditions would be mildly
circular.

**Now.** Proposition 4.7 (Section 4.1) proves that under an Aronson-type two-sided Gaussian bound on the Euler
density — primitive in `mu` and `V`, and available from Lemaire and Menozzi (2010) — the moment law
holds with its constant bracketed:

    c_- phi_{a_-}(y-x) kappa  <=  liminf h^{(r-1)K/2} E[G_h^r]
                              <=  limsup  <=  c_+ phi_{a_+}(y-x) kappa.

Both ends are strictly positive and finite, so `E[G_h^r] ≍ h^{-(r-1)K/2}` exactly. The **exponent**,
and with it the effective size `R_{M,S}`, the variance scale, and the four-dimensional
incompatibility between the published rate condition and mean-square consistency, follow without
(A5) at all. (A5) does exactly one thing: it replaces the bracket by the single value `p(y|x)`.

This matters for the standing of the critique. The paper's thesis is a scaling law, and the scaling
law is now shown to rest on conditions a reader can check from the coefficients.

**A second, smaller reduction.** Even for the constant, (A5) is stronger than the proof consumes. The
local argument integrates `r_h` against a kernel of bandwidth `sqrt(h/r)` centred at `y`, so what is
used is convergence along the rescaled neighbourhood only, `r_h(y - sqrt(h) u) -> p(y|x)` for almost
every `u`. Uniform convergence on a fixed ball implies this and is strictly stronger.

**A correction found by testing.** The first version of the test built the Gaussian bounds at a single
value of `h` and failed: the bracket did not contain the truth. It should not have. The assumption
must hold uniformly over `h in (0, 1/2]`, so the constants must cover the whole range of preterminal
variances — `[1/2, 1)` in the Brownian case — which forces `a_- <= 1/2` and `a_+ >= 1`. The bracket is
therefore wide, and the proposition now says so explicitly: it claims containment and two-sided
positivity, not tightness.

## 3. The argmax question (Proposition A.3, Remark A.4) — one of two steps closed

**Was.** The nearest-neighbour limit `(nn_limit)` was a conjecture. Establishing it would show the
simulated argmax is consistent but with the wrong curvature, so that `sqrt(N)(theta~ - theta^)` has a
nondegenerate limit, refuting the *conclusion* of Lemma 5 rather than only its proof. Two
requirements were named: uniform integrability in the interchange, described as "a genuine obstacle
rather than a formality", and a uniform-in-`theta` upgrade, described as "standard in kind".

**Now, the interchange is proved.** The obstacle was that the limit is dominated by centres far from
`theta`, exactly where the conditional asymptotics need the largest `S`. The fix is to split the
centres at a radius `r_S = sqrt(2 a log S)` with `2/K < a < sigma^2`, which `K sigma^2 > 2` makes
possible:

- *Distant centres.* Use only `rho <= ||theta - b_1||`, so the contribution is at most
  `S^{2/K} E[(m^2 + K sigma^2) 1{m > r_S}]`, which is `O(S^{2/K - a})` up to subpolynomial factors and
  vanishes because `a > 2/K`.
- *Nearby centres.* A lower bound on the ball probability valid for radii up to
  `T = min(sigma^2/2m, sigma)` gives a dominating function `e^{2/K} Gamma(1+2/K) (omega_K f)^{-2/K}`,
  valid for every `S` and every centre, whose integral converges precisely when `K sigma^2 > 2`. The
  remainder is `O(S^{2/K} m^2 e^{-S beta})` with `S beta -> infinity` uniformly on the region because
  `a < sigma^2`.

Dominated convergence then gives the limit, and uniform integrability comes from the same dominating
function. Keeping `sigma^2 = 1-h` rather than passing to the limit sharpens the constant, and the
condition reads `K(1-h) > 2` — the finite-`h` form of the same integrability boundary `K > 2` that
governs the collapse theorem.

**Checked to five significant figures.** Direct simulation cannot settle this; the manuscript reports
89 per cent of the limit at `S = 5,000`. But the quantity is two one-dimensional integrals, not an
intrinsically stochastic object, because the conditional distance law is a noncentral chi-squared in
closed form. Quadrature reaches `S = 10^18`, where the ratio to the conjectured limit is `1.0000` at
`K = 3`, `4` and `6` and at two values of `||theta - theta_0||`, always approached from below.

**What remains, described properly.** The uniform-in-`theta` step is not a formality either, and the
manuscript now says why. The map `theta -> min_s ||theta - b_s||` is 1-Lipschitz, so an individual
summand of the criterion has Lipschitz constant of order `S^{2/K} rho ≍ S^{1/K}`, which **diverges**.
The limit function is smooth with bounded derivative, so the divergence must cancel in the average
over `n`; but that cancellation is a law of large numbers for terms whose oscillation grows like
`S^{1/K}`, and it therefore plausibly requires `N >> S^{2/K}` rather than holding for every admissible
pair. The sharp condition is not determined here. This is worth stating because the published rate
conditions constrain `N` from **above**, not below, so the direction of the requirement is exactly
the awkward one.

The paper claims no more than the interchange proposition states. The argmax consequence remains
conditional and is labelled as such.

## Machinery

- `code/generate_results.py`: two new deterministic generators, `make_nn_convergence_table` and
  `make_collapse_bound_table`, producing `nn_convergence.{csv,tex}` and `collapse_bound.{csv,tex}`.
  The first is pure quadrature; the second uses the exact binomial-and-truncated-chi-squared
  reduction rather than simulating `10^7` draws.
- `tests/test_analytics.py`: eight new tests. The bound is checked to dominate the exact exceedance
  probability and to be neither vacuous nor wildly loose; the rate is checked to scale like
  `lam (log(1/lam))^{K/2}`; the nearest-neighbour limit is checked for monotone convergence and
  recomputed from its definition rather than from the generator; the conditional nearest-neighbour
  law is checked against direct simulation at one centre; and the Aronson bracket is checked to
  contain the truth and to widen as the Gaussian bounds loosen.
- `paper/references.bib`: Lemaire and Menozzi (2010), DOI verified against Crossref.

## Verification

Both documents build with zero errors, zero overfull and underfull boxes and no undefined references
or citations: 55 and 26 pages. 259 tests pass. All generated artefacts reproduce bit-for-bit. No
forbidden phrase appears in any searched file. All bibliography DOIs resolve against Crossref.
