# Final adversarial mathematical and computational review

> **SUPERSEDED — retained for the audit history.** This document records the state of the work at the time it was written, including statements later corrected or withdrawn. Do not read it as the current theorem statement; see `docs/change_log_referee_round_three.md` for the current round and `paper/main.tex` for the statements themselves.

Third-round hostile pass over every theorem, proposition, corollary, table and numerical
diagnostic, conducted without assuming any previous review was correct. Branch
`fix/final-mathematical-review`.

## Method

Each result was re-derived independently and, where it admits a numerical form, checked against a
computation that does not share its derivation. The checks live in
`code/`, `tests/` and, for the identities added this round, a scratch harness whose output is
reproduced under "Numerical verification" below. Findings are graded **publication blocking**,
**major**, **minor**, **editorial**.

## Mathematical checks

### 1. Proposition 3.1, exact Brownian moments
Re-derived by direct Gaussian integration. The `r`-th moment constant `(2π)^{−(r−1)K/2} r^{−K/2}`
and the determinant-free structure of the Brownian case both confirmed. Second moment cross-checked
against Monte Carlo in `tests/test_analytics.py` at three standard errors. **No finding.**

### 2. Theorem 3.3, collapse
The ball-probability bound, the choice `c > K`, the convergence in probability and the `K > 2`
threshold all re-checked. The threshold is sharp: at `K = 2` the exponent vanishes and the argument
gives nothing, which the statement respects. **No finding.**

### 3. Corollary 3.5, divergence
Sign and tightness re-checked. The divergence is to `−∞` because the estimator collapses to zero
from above while the true density is strictly positive. **No finding.**

### 4. Theorem 4.2, local moment law
Tail bound, ellipticity inequalities, determinant exponents, dominating function and limiting
constant re-verified. **No finding.**

### 5. Theorem 4.4, triangular-array CLT
The Lyapunov ratio uses the **centred** third moment, which was the subject of a first-round
correction; still correct. **No finding.**

### 6. Proposition 6.1, log-density expansion
Delta-method hypotheses, lower-tail requirement and the expectation expansion are as stated, and
the uniform integrability is assumed rather than proved. Labelled conditional throughout.
**No finding beyond the recorded limitation.**

### 7. Proposition 6.2, maximiser equivalence — **was publication blocking, now resolved**
The previous statement controlled scores and Hessians on a neighbourhood of `θ₀` but never assumed
the simulated maximiser lay in it, and the "proof" was a one-sentence sketch. The conclusion did
not follow.

Rewritten with six hypotheses: consistency of **both** maximisers, first-order conditions with
probability tending to one, uniform score agreement at `o_P(N^{−1/2})`, uniform Hessian agreement
at `o_P(1)`, a continuous limiting Hessian nonsingular at `θ₀`, and segment containment. The proof
now uses the **integral** form of the mean-value theorem, `H̄_N = ∫₀¹ ∇²Q̃(θ̂ + sΔ) ds`, rather than
a coordinatewise version, which would supply a different intermediate point in each row and no
single invertible matrix. Consistency of the simulated maximiser is what makes the segment shrink to
`θ₀` and `H̄_N` approach a nonsingular limit; Remark 6.3 records that this is assumed, states the
weaker alternative that would replace it, and says plainly that neither is verified here.
**Resolved.**

### 8. Proposition C.1, worst-case boundary probability
Closed-form maximiser `β²h/(1−2αh)` and maximum `Φ(−√(1−2αh))` checked against a numerical
maximiser over a 400,000-point logarithmic grid at three parameter settings; agreement to `1e−5` in
the maximum and `5e−3` relative in the location. Sign convention correct. **No finding.**

The *interpretation* following it was a separate matter: see finding 13.

### 9. Proposition D.1, volatility branches
Quadratic signs, discriminant, root positivity and the singular-inverse condition re-checked, and
confirmed computationally by the six-design grid sweep: across 558,204 candidate points in total,
not one admits exactly one positive root when `κ_b > 1`. **No finding.**

### 10. Proposition E.1, implied correlations
The proof bounds `ρ_wx` and `ρ_w*x` only. The surrounding text formerly extrapolated it to every
entry. Statement retitled, scope written into the statement itself, and Table 11 added classifying
all seven correlations. **Resolved, was major.**

### 11. Lemma E.1 and Proposition E.2 — **was publication blocking, now resolved**
The previous proof asserted that `1 − r'A⁺r ≥ 0` "holds because `r` then lies in the range of `A`".
This is false. Range membership constrains the direction of `r` relative to `Null(A)`; it places no
bound on its length. The two conditions are logically independent, and a one-line counterexample
settles it: with `A = diag(1,0)` and `r = (2,0)`, `r` lies exactly in `Range(A)` while
`1 − r'A⁺r = −3`.

A general block lemma is now stated and proved in both directions from first principles, by
completing the square for sufficiency and by testing the quadratic form along `Null(A)` and at
`x = −w` for necessity. Proposition E.2 is restated with both conditions, and the model-specific
case is reduced by an explicit congruence `R_t = T Σ_t Tᵀ` to positive semidefiniteness of the
three-dimensional correlation matrix of `(W, W*, Y)`, which is then written out as
`ρ_wy² − 2ρ_ww* ρ_wy ρ_w*y + ρ_w*y² ≤ 1 − ρ_ww*²`. Remark E.3 handles `|ρ_ww*| = 1` through the
pseudoinverse of the `2×2` block.

A worked counterexample is now in the manuscript with every entry inside `[-1,1]`: at
`φ = 0.03`, `φ* = 0.02`, `ρ_ww* = 0.3`, `ρ_wy = ρ_w*y = 0.9`, compatibility holds exactly, the
induced `ρ_xy = 0.2935`, and the spectrum is `{−0.133, 0, 1.558, 2.575}`. **Resolved.**

Sixteen tests in `tests/test_singular_psd_condition.py` cover both directions, the equality case,
the reduction to the ordinary Schur complement when `A` is nonsingular, randomised agreement with
the spectrum on singular blocks in dimensions 2 to 4, the logical independence of the two
conditions, and the Brandt–Santa-Clara structure specifically.

### 12. Proposition F.1, corner solution
The phrase "at least one defining constraint is active" was unsupported without a representation of
the feasible set. Now stated for `C = {c ∈ [c_L, c_U] : g_j(c) ≤ 0, j = 1..J}` with `J` finite and
each `g_j` continuous, and each of the paper's two feasible sets is exhibited in that form,
including the semidefiniteness constraint as `−λ_min(R(c)) ≤ 0`, continuous because the smallest
eigenvalue is. Compactness is proved, the alternative `c* = c_L` or `c* = c_U` or `g_j(c*) = 0` is
proved by contradiction, and finiteness of `J` is identified as what supplies the common `δ`.
**Resolved, was major.**

## Interpretation checks

### 13. Occupation time — **was publication blocking, now resolved**
The text read: "the dangerous region shrinks with `h`, so a finer discretisation does reduce the
time spent in it." This does not follow. A shrinking state interval does not imply a decreasing
occupation probability, and near an attainable boundary the state distribution may itself
concentrate towards zero as the mesh is refined.

Replaced with an explicit separation of five quantities: the pointwise one-step probability, its
supremum over states, the current-state distribution `π_h`, the integrated one-step failure
probability `∫P_h dπ_h`, and the cumulative pathwise probability over `m` steps. The text now states
that Proposition C.1 bounds the fourth by the second and analyses `π_h` not at all, and that the
fifth cannot be obtained by multiplying the second across steps because the visited states are
dependent. **Resolved.**

### 14. Grid as state space — **was major, now resolved**
"66 per cent of the state space admits no positive volatility" treated a grid proportion as a
measure. Appendix E.1 is renamed "Algebraic domain of the state transformation" and now lists what
the grid does not establish: accessibility, support, visiting probability, occupation time,
invariant distribution, measure. Counts replaced percentages.

A six-design sensitivity sweep was added, and it justifies the concern empirically: the proportion
of no-root points ranges from 58 per cent to 96 per cent depending only on where the grid is placed.
The two findings stable across all designs — no point with exactly one positive root, no indefinite
matrix — are the only ones now drawn. **Resolved.**

### 15. Direct-`H` versus implemented-`v` — **was major, now resolved**
Explicit establishes and does-not-establish lists now precede Proposition C.1, and the list of what
an implemented-chain analysis would require is given. The conclusion no longer says the implemented
chain fails, only that its global definition requires a nonnegative radicand and that no convention
is documented. Figure 5's caption states all three scope points. **Resolved.**

### 16. Time-varying binding — **was major, now resolved**
Slackness at the reported optimum and at sampled candidate points is not slackness along the whole
feasible set, and the active constraint is a property of the set. The claim is now split three ways:
exact theorem for the constant case under stated conditions, reported empirical fact for the
time-varying cases, conditional for the enlarged problem. **Resolved.**

### 17. Notation collisions — **was major, now resolved**
Detemple et al. write `M` for the number of simulations, which is this paper's `S`; carrying their
symbol across inverted the meaning of the quoted score rate. Neutral symbols now used throughout
Section 1.1 with footnotes recording the originals, and Table 1 is fully translated with a new
column naming the converging quantity. **Resolved.**

### 18. Antithetic `S` collision — **was major, now resolved**
The subsection simultaneously said `S` was the number of evaluations and the number of pairs.
`P` and `E = 2P` now used there, with the variance formula proved and Table 3 carrying both.
**Resolved.**

### 18a. Antithetic variance-equivalent count — **was major, introduced by the round-three fix**
The `P`/`E` rewrite proved the variance formula correctly and then misread it. It stated that `E`
"overstates the independent count by the factor `2/(1+ρ_A)`, which at a coincident endpoint is
exactly two". Two errors in one sentence: the overstatement factor is `E/N_eff = 1 + ρ_A`, not
`2/(1+ρ_A)`, and the quoted expression equals **one** at `ρ_A = 1`, so the sentence contradicted its
own numerical claim. The ratio `2/(1+ρ_A)` is `N_eff/P`, a different comparison.

The variance-equivalent count is now defined explicitly as `N_eff = E/(1+ρ_A) = 2P/(1+ρ_A)`, both
ratios are written out side by side, and the four cases are stated: `ρ_A = 1` gives `N_eff = P`, so
`E` overstates by two; `ρ_A = 0` gives `N_eff = E`; `ρ_A < 0` gives `N_eff > E`; and `ρ_A → −1` makes
`N_eff` diverge, which is flagged as a variance-equivalence convention rather than a literal count.

Two consequences. First, `P/M^{K/2}` is no longer called an effective size: it is `R_pair`, an
independent-pair diagnostic requiring no knowledge of `ρ_A`, alongside `R_var = N_eff/M^{K/2}`.
Second, because `ρ_A` depends on the endpoint, the initial state, the dimension, the discretisation
level, the coefficients and the parameter, no single `N_eff` applies to a 544-term likelihood, so
Table 3 reports `R_var` at two reference values of `ρ_A` rather than one assumed value.

A new Lemma 8.2 proves that the coupling cannot touch the exponent. For nonnegative partners with
identical marginals, `(a²+b²)/4 ≤ A² ≤ (a²+b²)/2` pathwise, so `E[G²]/2 ≤ E[A²] ≤ E[G²]`, and
`E[G²] ≍ h^{−K/2}` gives `E[A²] ≍ h^{−K/2}` whatever the dependence. Nonnegativity is used only for
the lower bound. Since `E[A] = E[G] = O(1)` while the second moment diverges, the same order carries
to the variance. **Resolved.** 26 tests in `tests/test_antithetic.py`, including simulated recovery
of `N_eff` and the moment-order check across decreasing `h` in dimensions 1 to 4.

## Editorial

### 19. René Garcia — **was major, now resolved**
A real defect, and one an earlier audit had wrongly recorded as fixed. The `.bib` contained
`Ren{'e}` with the backslash lost, and the compiled PDF rendered "Ren'e Garcia". Corrected to
`Ren{\'e}` and verified in the PDF byte stream as `Ren\351`. A forbidden-phrase pattern now guards
against recurrence.

### 20. Float placement — **was editorial, worse than reported**
Table 1 is cited on page 3 and was being placed on page **31**, 28 pages late; Figure 5 was reaching
the conclusion. `placeins` is now loaded with `\FloatBarrier` before every section, all floats
changed from `[t]` to `[htbp]`, and the float parameters relaxed. Table 1 now lands on page 7 and
Figure 5 in Section 10, before the conclusion. **Resolved.**

### 21. Table 9 matrix count
`38,496` was unexplained. The caption now states `38,496 = 2 × 19,248` and the column is renamed
"Branch-specific matrices". **Resolved.**

### 22. Affiliation
Left as supplied by the author. No authoritative source in this repository documents an expanded
form, and inventing one is what the instruction forbids. **Flagged, not changed.**

## Numerical verification

Every identity added this round was checked against an independent computation.

| Check | Result |
| --- | --- |
| `R_t = T Σ_t Tᵀ` congruence, 2,000 random parameter draws | max discrepancy `3.0e−15` |
| `A_t u = 0` for `u = (φ, −φ*, −v)`, 2,000 draws | max `5.6e−17` |
| Completing-the-square identity of Lemma E.1, 3,000 draws, dimensions 2–4, singular `A` | max `4.8e−13` |
| Antithetic variance `σ²(1+ρ)/(2P)` against simulation at five values of `ρ` | within Monte Carlo error |
| Proposition C.1 closed forms against a 400,000-point numerical maximiser, three settings | max within `1e−5` |
| Six-design grid sweep, 558,204 candidate points | no single-root point, no indefinite matrix |
| Full artefact regeneration | 33/33 bit-exact |
| Test suite | 167 passing |
| Forbidden phrases | 0 hits, 19 patterns, 5 files |
| DOIs against Crossref | 24/24 matching |

## Outcome

**Zero publication-blocking issues remain. Zero major issues remain.**

Three publication-blocking findings were raised and resolved in this round: the missing
Moore–Penrose magnitude condition in Proposition E.2, the unlocalised maximiser in Proposition 6.2,
and the occupation-time inference after Proposition C.1. Two of the three were false statements
rather than gaps.

The central contribution is untouched and does not depend on any application diagnostic: the exact
Brownian moments, the collapse theorem, the local moment law, the corrected triangular-array CLT
and the refutation of Lemmas 2 and 3 were re-checked and stand as before.

## Recorded limitations

Unchanged from round two, and none of them blocking: the argmax question is open; the Euler bias
expansion is imported from Bally and Talay; uniform integrability in Proposition 6.1 is assumed;
implementation safeguards are unknown; Table 4's risk prices are taken from Table 3; and the
affiliation awaits the author's confirmation.
