# Overlap audit: Detemple, Garcia and Rindisbacher

Primary-source comparison between the manuscript and

> Detemple, J., Garcia, R. and Rindisbacher, M. (2006). Asymptotic properties of Monte Carlo
> estimators of diffusion processes. *Journal of Econometrics* 134(1), 1–68.

**Source consulted.** The full text was read in the CIRANO working-paper version 2003s-11
(67 pages, April 2003), which is the openly available version of the same paper; the published
version is paywalled. Page references below are to the working paper. The decisive passage is
Section 5.2 on simulation-based inference, pages 31–32.

**Verdict: the overlap is substantially larger than the manuscript previously acknowledged.**
Four claims that the manuscript treated as its own framing are stated explicitly by Detemple et
al., and one of them — that the Brandt and Santa-Clara rate condition is insufficient — is stated
by them about Brandt and Santa-Clara by name. Section 1.1 has been rewritten accordingly.

## Notation

Detemple et al. use `L` for sample size, `M` for the number of Monte Carlo simulations and `N`
for the number of discretisation points. The manuscript uses `N`, `S` and `M` respectively. The
translation is

| Detemple et al. | Manuscript |
| --- | --- |
| `L` (sample size) | `N` |
| `M` (simulations) | `S` |
| `N` (discretisation points) | `M` |
| `d` (state dimension) | `K` |

All comparisons below are stated in the manuscript's notation unless quoting.

## Overlapping claims

### 1. Kernel interpretation of the simulated transition density

**Manuscript.** "The central observation of this paper is that the final Gaussian density is a
kernel with bandwidth `h^{1/2}`."

**Detemple et al.**, p. 32, verbatim:

> "Since Monte Carlo integration of the true transition density kernel is based on a Gaussian
> kernel approximation with bandwith determined by the number of discretization points N, the
> resulting score function depends on the time discretization parameter N not just through the
> simulated discretized trajectories but also through its functional form. As described by
> Milshtein, Schoenmakers and Spokoiny (2001), this estimator of the transition density can be
> interpreted as a kernel estimator based on simulated i.i.d. data."

**Overlap: identical**, and Detemple et al. themselves attribute it to Milstein, Schoenmakers and
Spokoiny, published as *Bernoulli* 10(2), 281–312 (2004). The kernel interpretation therefore
predates both.

**Correction applied.** The manuscript no longer describes the kernel interpretation as its
"central observation". It is attributed to Milstein, Schoenmakers and Spokoiny and to Detemple et
al., and both are now cited.

### 2. Dimension-dependent convergence rate

**Manuscript.** Proposition 5.1: optimal `M ≍ S^{2/(K+4)}` with pointwise MSE `≍ S^{-4/(K+4)}`.

**Detemple et al.**, p. 32, verbatim:

> "It is well known that such an estimator will converge at a rate slower than `M^{-1/2}`. The
> rate for the score will be `M^{-2/(d+4)}`, and therefore will depend on the dimension of the
> diffusion."

and footnote 28, p. 30:

> "Alternative kernel-based estimation methods for conditional expectations converge at a slower
> rate (`L^{-2/(d+4)}`) which depends on the dimension of the diffusion."

**Overlap: same rate family, different object.** The exponent `2/(d+4)` is exactly the one in the
manuscript's Proposition 5.1. Detemple et al. state it for the *score*; the manuscript derives it
for the *pointwise transition-density MSE*, with explicit constants. This is a sharpening, not a
discovery.

**Correction applied.** The manuscript no longer presents the dimension-dependent rate as new. It
now says the exponent is already in Detemple et al. and that the contribution is the exact
constants and the finite-`M` moments behind it.

### 3. Optimal allocation between simulation size and discretisation level

**Manuscript.** Proposition 5.1 balances `O(M^{-2})` bias against `O(M^{K/2}/S)` variance.

**Detemple et al.**, p. 32: optimality for simulated maximum likelihood estimators requires

> `sqrt(L)/M_L^{2/(d+4)} → ε1` and `M_L^{2/(d+4)}/N_L → ε2`.

**Overlap: prior work.** An explicit optimal design linking sample size, simulation size and
discretisation level is given there and not here.

**Correction applied.** Listed as prior work in Section 1.1.

### 4. Insufficiency of the Brandt and Santa-Clara rate condition

This is the most consequential overlap.

**Manuscript** previously implied that identifying the inadequacy of the published rate condition
was part of its contribution.

**Detemple et al.**, p. 32, verbatim:

> "Corresponding optimal designs for the simulated maximum likelihood estimator of Pedersen
> (1995a,b) and Brandt and Santa Clara (2002) depend in addition on the dimension of the
> diffusion. **These authors assume that ε2 = 0. This assumption, unfortunately, is not
> sufficient.** To avoid an exploding second-order bias it must be the case that `sqrt(L)/sqrt(M_L)`
> does not diverge faster than `sqrt(M_L)/N_L` vanishes. It follows that the rate of divergence of
> `M_L` cannot be chosen independently from `L`."

and, two paragraphs later:

> "For estimators with a fixed number of discretization points and a fixed number of Monte Carlo
> simulations the second-order bias always explodes when the sample size becomes large. The
> corresponding asymptotic confidence intervals will then cover the true values with probability
> zero."

**Overlap: Detemple et al. state the insufficiency first, and about Brandt and Santa-Clara by
name.** They reach it through second-order bias in the estimating function; the manuscript reaches
a different and sharper conclusion, that the transition-density statements are false along an
explicit sequence. But the general claim that the condition is inadequate is theirs.

**Correction applied.** Section 1.1 attributes the insufficiency of the condition to Detemple et
al. and restricts the manuscript's claim to the specific counterexample.

### 5. Joint limits in data size, discretisation and simulation

**Detemple et al.** work throughout with joint limits in `L`, `M` and `N`.

**Overlap: prior work.** The manuscript's contribution here is not that joint limits are needed
but that a specific joint sequence produces convergence to the wrong value.

## Claims with no counterpart in Detemple et al.

Each of these was searched for in the full text and is absent.

| Manuscript claim | Status |
| --- | --- |
| Exact finite-`M` moments of every order for the Brownian endpoint summand (Prop. 3.1) | **not present**; Detemple et al. work asymptotically throughout |
| Exact local moment constant `c_{r,K} = (2π)^{-(r-1)K/2} r^{-K/2}` (Thm. 4.2) | **not present** |
| Collapse in probability along `M = S` (Thm. 3.3) | **not present**; their negative results concern exploding second-order bias and inefficiency, not convergence of the density estimator to a wrong value |
| Direct refutation of the joint convergence in Lemma 2 (§7.1) | **not present** |
| Direct refutation of the joint CLT in Lemma 3 (Cor. 3.5) | **not present** |
| The exact four-dimensional incompatibility `S/M² → 0` versus `S/M² → ∞` | **not present** in this explicit form; their statement is the weaker "not sufficient" |
| The identification of `S/M^{K/2}` as the effective simulation size, with constants | **conceptually related** to the kernel interpretation but not stated |
| The entire analysis of the exchange-rate application (App. B–G) | **not present** |

## Required corrections, all applied

1. Remove "the central observation of this paper is that the final Gaussian density is a kernel".
2. Attribute the kernel interpretation to Milstein, Schoenmakers and Spokoiny, and to Detemple et
   al.
3. Attribute the dimension-dependent rate exponent `2/(d+4)` to Detemple et al.
4. Attribute the optimal-allocation idea to Detemple et al.
5. Attribute the insufficiency of the Brandt and Santa-Clara condition to Detemple et al.
6. Rewrite Table 1 so that Detemple et al. are not reduced to a bias-correction contribution.
7. Reframe the contribution as sharpening: exact finite-discretisation moments, exact local
   constants, and an explicit admissible sequence along which the simulated density converges to
   the wrong value.

## Bibliographic verification

| Field | Value | Source |
| --- | --- | --- |
| Authors | Jérôme Detemple, René Garcia, Marcel Rindisbacher | title page of CIRANO 2003s-11 |
| Title | Asymptotic properties of Monte Carlo estimators of diffusion processes | publisher record |
| Journal | Journal of Econometrics | publisher record |
| Volume, issue, pages, year | 134(1), 1–68, September 2006 | publisher record, RePEc |
| DOI | `10.1016/j.jeconom.2005.06.019` | see caveat below |

**DOI caveat.** The ScienceDirect landing page returns HTTP 403 to automated fetches, so the DOI
could not be resolved directly against the publisher. It is recorded here as unverified-by-
resolution, although volume, issue, page range and year are confirmed from two independent
sources. `René Garcia` is rendered with the correct accent in the bibliography as
`Garcia, Ren{\'e}`.

Added to the bibliography as a result of this audit:

> Milstein, G. N., Schoenmakers, J. G. M. and Spokoiny, V. (2004). Transition density estimation
> for stochastic differential equations via forward-reverse representations. *Bernoulli* 10(2),
> 281–312. DOI `10.3150/bj/1082380220`.
