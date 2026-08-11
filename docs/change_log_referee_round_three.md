# Change log, third referee round

Baseline `f93754f`, the state deposited as v1.9.0. The report described the revision as a narrow one:
the density-level core passes, the centre-truncation strategy is accepted, and the previous round's
repairs are credited as genuine. It then listed seven required changes, of which three are real proof
gaps. All seven are made below. The referee was right on each.

## 1. The covering number and the net construction

**Was.** "Cover `Θ` by balls of radius `r/2` centred at the points of a grid of spacing `r/2`; at
most `(1+2D/r)^K` are needed."

Two faults. A grid of spacing `r/2` does not give Euclidean covering radius `r/2`: the farthest point
of a cube of side `r/2` sits at distance `(r/4)√K` from its centre, which exceeds `r/2` once `K > 4`.
And the count is wrong — a set of diameter `D` lies in a ball of radius `D`, and the volumetric bound
at scale `r/2` is `(1+4D/r)^K`.

**Now.** A maximal `r/2`-separated subset, which is an `r/2`-net by maximality, with the count from
the standard packing argument: the balls `B(θ_i, r/4)` are disjoint and lie in a ball of radius
`D + r/4`, giving `(1+4D/r)^K`. Constant-level throughout; no exponent moves.

## 2. The ULLN rate was stated too sharply — the main new finding

**Was.** `prop:uniform_lln_all` concluded under `N/(log S)^p → ∞`, with the proof choosing `η` small
"for `η` small enough" *after* the rate condition was fixed.

**Why it fails.** The distant-centre bound carries `e^{-(α-η)R²}`, so the exponent the argument needs
is `2·4/{K²σ²(α-η)}`, which decreases to `16/{K(Kσ²-2)}` as `η ↓ 0` but strictly exceeds it at every
fixed `η`. The hypothesis `N/(log S)^p → ∞` does not imply `N/(log S)^{p+δ} → ∞`: the referee's
counterexample `N = (log S)^p log log S` satisfies the first and fails the second at every `δ > 0`.
The same applies to the `exp{C√(log log S)} = (log S)^{o(1)}` factor from expanding `(R_S + D)²` —
smaller than every fixed power of `log S`, but not dominated by a ratio that may itself diverge as
slowly as `log log log S`.

**Now.** The theorem is stated under `N/(log S)^{p+ε} → ∞` for some `ε > 0`, with the quantifiers in
the order `ε` first, then `η`. `rem:epsilon_loss` records both losses and why neither is recoverable
by the argument given. The qualitative content is untouched: the requirement stays polylogarithmic
and the comparison with a polynomial condition such as `N/S^{1/4} → 0` is unaffected.

The window arithmetic in `rem:window` used the limiting exponent `p = 4`. Rather than recompute it at
an arbitrary `ε`, the remark now says what those figures are: the crossing computed at `p` is the
*earliest* size at which the window can open, so `S ≈ 10²⁹` at `K = 4` is a lower bound and the
conclusion drawn from it is only strengthened.

## 3. `lem:sigma_uniform` used the small-ball bound in the wrong direction

**Was.** The proof wrote `G(u²;K,λ) ≤ C_K u^K` and then used `(1-G)^{S-1} ≤ e^{-(S-1)G}` to reach
`e^{-cSu^K}`.

**Why it fails.** Extracting decay from `e^{-(S-1)G}` needs a **lower** bound `G ≥ c u^K`. The upper
bound controls the other factor. Both are needed and only one was supplied.

**Now.** A two-sided small-ball estimate `c_L u^K ≤ G(u²;K,λ) ≤ C_L u^K` on `0 < u < u_0`,
`0 ≤ λ ≤ L`, with the integral split at `u_0`. Below it the upper bound controls `G` and the lower
bound the decay, and `w = Su^K` gives `O(1)`. Above it, `q = sup_{λ≤L}{1 - G(u_0²;K,λ)} < 1` factors
out and the remainder is bounded by the noncentral mean, so that piece vanishes geometrically.

## 4. The noncentrality is not confined to a compact set

**Was.** "Since `Θ` is bounded and `σ² ≥ σ_0² > 0`, the noncentrality ranges over a compact set."

**Why it fails.** `λ = ‖θ - c‖²/σ²` and the centre `c = ΔY_n` is Gaussian, hence unbounded. There is
no deterministic compact set containing all such `λ`.

**Now.** The argument is made conditionally on `c` and then integrated: uniform over `{λ ≤ L}` for
each `L`, with the complement dominated by the Gaussian envelope already built for
`prop:nn_interchange`, whose integrability is exactly the standing condition and which depends on
neither `S` nor `σ²` in the interval. Equicontinuity on the bounded part with a uniformly small tail
is equicontinuity of the integrated quantity, which is what the net argument consumes.

## 5. A second triangular-σ quantifier, beyond `lem:sigma_uniform`

`lem:sigma_uniform` gives uniformity for `prop:nn_interchange` and the curvature coefficients.
`cor:argmax_consistent` also applies `prop:uniform_lln_all`, itself a fixed-`σ²` statement, along
`σ_n² = 1 - 1/n`. Pointwise validity at every fixed `σ` does not license substituting a triangular
sequence, and the quantifier appeared nowhere.

`cor:uniform_lln_sigma` now supplies it: the conclusion holds uniformly over `σ² ∈ [σ_0², 1]` under
the worst-case exponent on that interval, which since `p(σ²)` is decreasing is `p(σ_0²)`. Every
constant in the proof is continuous on the compact interval and bounded there, so the proof carries
over with each replaced by its worst value.

**The cost is nothing**, because `ε` absorbs it. `p` is continuous at `σ² = 1`, so given `ε > 0` one
picks `σ_0² < 1` with `p(σ_0²) ≤ p(1) + ε/2`; the requirement remains `N ≫ (log n)^{p(1)+ε}`, exactly
as stated, and `σ_n² = 1 - 1/n` enters `[σ_0², 1]` for all large `n`.

`rem:sigma_uniformity` had claimed `lem:sigma_uniform` settled the whole question. It now says both
quantifiers are needed and that an earlier version supplied only the first — an omission invisible
because the two sit in different subsections.

## 6. The practical design rule quietly upgraded a diagnostic

The rule said that for parameter estimation "it *is*" the score-level version `S/M^{(K+2)/2}`. Given
that `rem:score_scale` carefully declines to assert necessity, the practical section was reinstating
as a theorem what the theory section had demoted. It now says the score-numerator calculation
suggests *monitoring* that quantity **in addition** to the proved density-level `S/M^{K/2}`, and says
in the same breath which of the two is proved.

## 7. `J^{-1}` where `J` need not be square

`θ ∈ Θ ⊂ R^L` while `μ: Θ → R^K`, so `J = ∂μ/∂θ` is `K × L` and `J^{-1}` is undefined unless
`L = K`. The assumption and the proposition now require `‖J‖` bounded above and the smallest singular
value bounded below, which needs `L ≤ K` and furnishes a bounded left inverse
`J⁺ = (JᵀJ)⁻¹Jᵀ`; for `L = K` this is the old condition. Does not affect the location model, where
`L = K` and `J = -I`.

## 8. Superseded audit documents are now bannered

Twenty historical documents in `docs/` carry a banner naming them superseded and pointing at the
current round and at `paper/main.tex`. The three logs describing the current state are not bannered.
The concern is real: these files are reachable by search, and several state theorems that were later
withdrawn.

## Status after this round

The referee's own table listed `prop:uniform_lln_all` as needing a rate correction,
`lem:sigma_uniform` as not passing, and `cor:argmax_consistent` as not established under its stated
assumptions. All three are addressed here, and the referee's assessment was that no new conceptual
idea was needed — only technical bookkeeping and one corrected equicontinuity proof. That is what
this round is.

## What remains open

The `√N` statement, unchanged.
