# Change log, second referee round

Baseline `71cf5f5`, the state deposited as v1.8.0. The report recommended major revision, confirmed
that the density-level core passes, and identified one blocking error together with four smaller
problems. All are addressed below. The referee was right on every point.

## 1. `lem:covering` was false — blocking

**Was.** The lemma bounded the probability that a ball `B(θ, r/2)` around a point of `Θ` contains an
atom from below by `f_min · ω_K · (r/2)^K`, with `f_min` the infimum of the atom density **over `Θ`**.

**Why it fails.** The ball protrudes beyond `Θ`, and its mass is governed by the density on the
protrusion, which for a Gaussian cloud is smaller than at the centre. The referee's counterexample:
`K = 4`, `σ² = 1`, `Θ = {0}` with the cloud also at the origin gives a claimed lower bound of
`f(0) ω₄ 2⁻⁴ = 0.0078125` against a true mass of `P(χ²₄ ≤ ¼) = 0.0071910`. The purported lower bound
exceeds the probability it bounds, so `eq:covering_tail` fails outright at `S = 1`.

Checked further, the failure is not an edge case. Of 42 configurations swept over `K ∈ {3,4,6}`,
`σ² ∈ {0.5,1}`, offsets `{0, 0.8, 2}` and radii `{0.3, 0.6, 1.0}`, the original bound fails in **all
42** and the repaired bound in none. The reason is structural: a Gaussian density is largest at its
centre, so `f_min × volume` always overstates a ball's mass.

**Now.** The infimum is taken over the closed `r/2`-neighbourhood of `Θ`, which is what the union
bound actually needs. The lemma is stated in that generality; a separate corollary supplies the
Gaussian case, where

    f_{min,r} = f_min exp{ -(ρ_max r + r²/4) / (2σ²) }.

The correction could have cost an exponent. It does not, because the splitting radius may be chosen
to depend on the geometry: with `r₀ = (1 + ρ_max)⁻¹` the correction obeys

    f_{min,r} ≥ κ f_min   for all r ≤ r₀,   κ = e^{-5/(8σ²)},

an absolute constant, independent of `ρ_max`, of `S` and of the observation. Since `κ` enters the
moment bound only through `f_min` at the power it already carried, it moves the constant and nothing
else. **The exponent `p` of `prop:uniform_lln_all` is unchanged**, and so `cor:argmax_consistent`
stands.

**The second, smaller error in the same proof.** The covering count was bounded by
`A_{K,D} S u^{-K/2}` after substituting `u = S^{2/K} r²`. No constant `A` works: as `u` grows the
left side tends to one while `S u^{-K/2}` tends to zero, and the measured ratio diverges
(16 → 10¹⁰ over `u ∈ [10⁻⁴, 10⁸]`). The additive form `C_{K,D}(1 + S u^{-K/2})` the referee proposes
is correct and is now used.

**A consequence the referee did not raise.** The Gaussian corollary carries a regime condition —
the covering scale must sit below `r₀` — and that condition fails for centres far enough out. The
distant-centre region of `prop:uniform_lln_all` is therefore cut again at `L_S` with
`(L_S + D)² = 2σ²(log S − (K+1) log log S)`. Below it the covering moments apply; above it only the
deterministic bound `ρ_S ≤ ρ_max + ‖b₁ − c‖` does, and that outer piece contributes

    S^{2/K − σ²} exp{ C √(log S) },

which vanishes exactly when `2/K < σ²`, i.e. `Kσ² > 2` — the standing hypothesis, arrived at
independently for the second time in the same proof. The cross term `exp(C√log S)` is **not**
polylogarithmic; a first draft of this repair claimed it was, and the numerical check caught it.
Convergence is slow: at `K = 3`, `σ² = 0.7` the bound still increases until `S ≈ 10³⁰⁰`.

## 2. `cor:score_contradiction` claimed a necessity its proof withheld

The corollary said hypothesis `it:me_score` **requires** `S h^{(K+2)/2} → ∞`. Its own proof granted
two steps unproved, one being precisely the passage from `∇q̂` to `∇q̂/q̂`; and the neighbouring
`rem:score_denominator` said in terms that this is "not a proved necessary condition". The paper
contradicted itself across two adjacent environments.

It is now `rem:score_scale`: `S h^{(K+2)/2}` is recorded as the mean-square scale the **numerator**
calculation suggests, with the incompatibility stated conditionally — *if* it were necessary, the
gap would be wider by a factor `M` than the density-level one — and explicitly not asserted.

The scope paragraph also claimed the result was "proved outright" for constant-coefficient families.
As the referee notes, constant coefficients discharge the identification of the parameter derivative
with the `y`-derivative and **nothing else**; the denominator is untouched by them. Corrected.

## 3. `lem:sigma_uniform` was underproved

The proof concluded that "the pointwise nearest-neighbour limit is uniform on the interval by the
same continuity". That does not follow: continuous functions can converge pointwise to a continuous
limit on a compact interval without converging uniformly.

The repair supplies equicontinuity, via an exact scaling identity. Writing `d = θ − c`, the law of
`‖d − σξ‖²` is `σ²` times a noncentral `χ²_K` with noncentrality `λ = ‖d‖²/σ²`, so

    S^{2/K} E[min_s ‖θ − b_s‖²] = σ² Λ_S(‖d‖²/σ²),

which puts the whole `σ²`-dependence in a prefactor and a noncentrality. Then `|∂_λ G| ≤ ½G` from
the standard noncentral identity, plus `G ≲ u^K` near the origin, gives `|Λ_S'| ≤ C` uniformly in
`S`. Equi-Lipschitz plus pointwise convergence gives uniform convergence by a finite-net argument.

Checked before being written: the slope is flat in `S` across `K ∈ {3,4,6}` and offsets `{0, 1, 1.5}`,
and at offset zero the identity makes `g_S(σ²) = σ² g_S(1)` exactly linear, which is visible in the
numbers to five decimals.

## 4. The numerical table measured the proxy, not the estimator

`tab:simulated_maximiser` was named for the simulated maximiser, but `_criterion_value` minimises the
nearest-atom criterion `X_N` over a cloud drawn at `σ² = 1` — not the Gaussian log-sum-exp simulated
likelihood at finite `M`. Renamed throughout to `tab:proxy_minimiser`, with the function, the CSV,
the test and the caption following; the caption now says which object is minimised and that the two
are linked by a sandwich rather than being the same thing.

`rem:search_bias` also contained a genuine logical error: it concluded that a finite restart budget
gives "an upper bound on the criterion, hence a lower bound on the estimator's error". The second
half does not follow — ordering criterion values does not order parameter errors, and a suboptimal
local minimum may lie nearer `θ₀` than the global one. Removed, in the remark and in the docstring
that carried the same claim. What the restarts do buy is the removal of a bias of *known* direction,
namely starting the search at the answer; the residual effect of a finite budget is of unknown sign.

## 5. Claim-status contradictions

| Where | Said | Now |
| --- | --- | --- |
| §1.2 boundary paragraph | "none of them concerns the maximiser of the simulated log likelihood" | names `cor:argmax_consistent` as the exception, scoped to the location model |
| `rem:ullnn_gap` | "We have not carried it out." | records that `prop:uniform_lln_all` carries it out, by a different route than the one sketched |
| `cor:argmax_consistent` proof | "By `prop:uniform_lln`, sup |A_N − G| → 0" | cites `prop:uniform_lln_all`; the entropy proposition supplies only the bracketing estimate |
| README | CLT "throughout its complement" | supercritical region only; `R ≍ 1` is a third regime |
| README | stationarity solved "exactly" | iterated to convergence from eight random starts, best kept |
| README | "the simulated maximiser carries roughly twice the error" | the nearest-atom proxy minimiser, over a unit-variance cloud |

The mis-citation in the third row is the one that mattered: `prop:uniform_lln` is the entropy
proposition and does not deliver a uniform law, so the consistency proof was, as written, citing a
result that does not support its step.

## What this round did not change

The density-level core, which the referee rechecked and passed: exact Brownian moments, subcritical
collapse, the critical regime, the triangular-array scaling, the general local moment law, and the
MSE balance. `prop:curvature` and the `a_j^{(S)}` transfer also pass and are untouched.

## What remains open

The `√N` statement, unchanged.
