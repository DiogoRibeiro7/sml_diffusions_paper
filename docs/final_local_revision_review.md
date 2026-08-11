# Final local revision review

> **SUPERSEDED — retained for the audit history.** This document records the state of the work at the time it was written, including statements later corrected or withdrawn. Do not read it as the current theorem statement; see `docs/change_log_referee_round_three.md` for the current round and `paper/main.tex` for the statements themselves.

Fifth round, twelve targeted issues. The core Brownian moment, counterexample, local moment and
density-CLT results were not reopened; no error was found in them and none was sought beyond
confirming they still compile, still reproduce, and are still stated as before.

One finding was a **false mathematical statement**, and it had survived four previous rounds.

## 1. Proposition C.1 monotonicity — **was a false statement**

The proposition itself was correct:

    sup_{x>0} P_h(x) = Phi(-sqrt(1 - 2 alpha h)).

Every verbal gloss on it was backwards. The manuscript said the peak "rises very slightly towards
Phi(-1) from below", that refinement "translates the curve to the left without lowering it", and that
the maximum is "essentially invariant to h".

As `h` decreases, `1 - 2*alpha*h` increases to 1, so `sqrt(...)` increases to 1, so `-sqrt(...)`
decreases to `-1`, and since `Phi` is increasing the maximum **decreases** to `Phi(-1)`. Refinement
lowers the worst case; it simply does not drive it to zero. The direction is now proved rather than
asserted:

    d/dh [-sqrt(1 - 2 a h)] = a / sqrt(1 - 2 a h) > 0,

so `f(h) = Phi(-sqrt(1 - 2 a h))` is strictly increasing in `h`, and the limit is approached from
above.

Table 7 contained the disproof all along: 0.1602 at `h = 0.02`, 0.1588 at `h = 1/520`, 0.1587 at
`h = 1/1040`. Strictly decreasing, exactly as the corrected statement requires. The table caption
had described these as "essentially invariant".

Corrected in the proposition, its proof, the discussion after it, Section 8.1(i), Section 9.5, the
Figure 5 caption and the Table 7 caption. **The substantive conclusion is unchanged**: the dangerous
state still moves toward zero at order `h`, the worst case is still bounded away from zero, and mesh
refinement alone still does not eliminate the local positivity problem. **Resolved.** Three
regression tests, including one asserting strict monotonicity across four values of `alpha` and one
checking the analytic derivative against a numerical one.

## 2. Antithetic refinement claims

"Doubling `M` and the simulation count halves the effective endpoint size" attributed to `R_pair` a
status it does not have. Now: in four dimensions doubling `P` and `M` halves the independent-pair
scaling diagnostic `P/M^2`, and the corresponding change in `R_var` cannot be determined without the
pair correlation at each transition, since `rho_A` may itself vary with `M`.

Two scenarios in the tests make the point concrete. If `rho_A` falls from 1 to 0 as `M` doubles,
`R_pair` halves while `R_var` is **unchanged**. If `rho_A` rises from `-0.5` to 1, `R_pair` still
halves while `R_var` falls to an **eighth**, from 200 to 25. The only invariant is `R_var >= R_pair`,
from `rho_A <= 1`.

A remark now states what Lemma 8.3 does and does not give: it fixes the moment order `h^{-K/2}`
within a factor of two, and supplies neither the exact local variance constant, nor the Lyapunov
constant, nor a pair-level CLT, nor a likelihood-level antithetic theorem. A test exhibits two
couplings with the same marginals and the same exponent but different constants. **Resolved.**

## 3. Proposition H.2

Retitled from "The maximiser is governed by a nearest-atom objective" to "Uniform comparison with a
nearest-atom objective", which is what is proved. The claim that the slack is "negligible relative to
`D_N`" is withdrawn: what is proved is that after division by `N` the slack is `2h log S`, which
vanishes along `M = S = n` as `2(log n)/n`. Whether that is sharp enough to control the maximiser
depends on the order and local geometry of `D_N`, both unresolved.

Five things the bound does not establish are now listed explicitly: convergence of maximisers,
equality of finite-sample maximisers, equivalence of local curvature, the order of `D_N`, or a
contradiction to Lemma 5. The nearest-neighbour limit remains labelled a conjecture, and the appendix
summary now reads: H.1 an exact identity, H.2 an exact uniform bound, the limit of `D_N` open, the
argmax question unresolved. **Resolved.**

## 4. "No admissible sequence exists"

Inaccurate: many sequences satisfy the published condition `sqrt(S)/M -> 0`, including `S = M`, which
is precisely the sequence Theorem 3.3 uses. The correct statement is that no sequence satisfies both
that condition and `S/M^2 -> infinity`. Corrected in contribution (e), in the Corollary 3.4
discussion and in Remark 3.6, and a terminology note now distinguishes **admissible** (satisfies the
published assumptions) from **density-consistent** (`S/M^{K/2} -> infinity`). The `M = S`
counterexample is still described as admissible under the published condition, which is what gives it
its force. **Resolved.**

## 5. Appendix E opening inventory

The opening said three entries of `R_t` are free, omitting `rho_ww*`. A symmetric `4x4` correlation
matrix has six off-diagonal entries: four free (`rho_ww*`, `rho_wy`, `rho_w*y`, `rho_xy`) and two
implied (`rho_wx,t`, `rho_w*x,t`). The fifth primitive parameter `rho_zz*` enters `C_t`, not `R_t`.
The opening now states all of this and points at Table 11. **Resolved.** A structural test enumerates
the six entries and confirms the 4 + 2 split with `rho_zz*` outside it.

## 6. Exact binding in the conclusion

The conclusion still said Proposition F.1 places the incompleteness state on its boundary at one
sample date, without distinguishing specifications. It now defers to Table 13: exact under the corner
formula for the constant case, reported by the original authors for the time-varying ones. **Resolved.**

## 7. Optimisation terminology

"Vertex" and "linear programme" are correct for `C_pub`, whose constraints are affine and whose
feasible set is a polyhedron. They are wrong for `C_obs` and `C_glob`, which carry non-affine
semidefiniteness constraints and need not be polyhedral or connected. Both terms are now restricted
to `C_pub`; elsewhere the text says "boundary point" and "affine-objective constrained optimisation
problem". Proposition F.1 Part A says boundary point; only Part B uses active-constraint language.
**Resolved.**

## 8. Section G title

"Binding constraints imply nonregular inference" asserts more than is shown. A finite-sample optimum
on an active boundary does not determine the asymptotic distribution: a constraint can bind in every
sample drawn and still be slack in the limit. Retitled "Binding constraints are not covered by
interior asymptotics", and the body now says the interior justification is incomplete and a separate
constrained analysis is required, rather than that the distribution is nonstandard or the standard
errors invalid. The list of unresolved issues is unchanged. **Resolved.**

## 9. Proposition E.2 positivity

The implied correlations divide by `v_t`, and the hypothesis `v_t^2 >= Q_t` permits `v_t = Q_t = 0`.
`v_t > 0` is now assumed explicitly, with a remark noting that the empirical application satisfies it
everywhere and that the assumption is stated because the formulas require it, not because the data
threaten it. **Resolved.** Five tests, including one asserting that `v_t = 0` raises rather than
silently dividing.

## 10. Interest-rate language and the underflow prose

"The interest-rate states are far from the boundary" is a pathwise claim the Feller condition does
not support; unattainable is not unapproachable. All such claims are now scoped to the displayed
benchmark states, with an explicit statement that the observed rate path is not reconstructed and no
sample-wide bound is claimed.

The prose said "all but the last of these underflow", but Table 5 marks four rows `no`, not one. Now:
"Many of these tails underflow in binary64 arithmetic; Table 5 records the result state by state." A
test checks every flag against direct IEEE-754 evaluation. **Resolved.**

## 11. Regularity versus rate assumptions

"The counterexample cannot be excluded by strengthening the hypotheses" is too broad, since the
correct joint rate condition does exclude it. Now: it cannot be excluded by strengthening smoothness,
boundedness or ellipticity **alone**, because Brownian motion already satisfies those in their
strongest form; it is excluded by requiring `S/M^{K/2}` to diverge, a restriction on the design rather
than the model. **Resolved.**

## 12. Finite-grid conclusions

"Three of the four specifications are unproblematic" presents a finite grid as a global proof. Now:
"no algebraic branch or positive-semidefinite problem was found on the examined grids", with the
computational findings reported in full and an explicit "this does not prove global validity outside
the examined grids". **Resolved.**

## Verification

| Check | Result |
| --- | --- |
| Test suite | 222 passing, up from 210 |
| Artefacts | 33/33 bit-exact |
| LaTeX | 0 errors, 0 undefined references, 0 multiply-defined labels, 0 overfull or underfull boxes |
| Pages | 59 |
| Forbidden phrases | 0 hits, 40 patterns across 5 files |
| DOIs | 24/24 Crossref-verified |
| Release gate | passes, no bypass flags |

## Outcome

**No publication-blocking issue remains. No major issue remains.**

The finding worth dwelling on is the first. A correct closed-form result had every verbal
interpretation reversed, and the numbers disproving the gloss were printed in the paper's own table
three lines below the caption asserting it. Four previous review rounds, including two adversarial
passes, did not catch it, because each checked the formula and read the prose as agreeing with it.
The lesson is narrow and practical: a limit's *direction* deserves the same explicit check as its
value, and the regression test now added encodes exactly that.

The central theorem sequence is unchanged: the exact Brownian moments, the collapse theorem, the
local moment law and the corrected triangular-array CLT stand as before, and none depends on any
application diagnostic.

## Recorded limitations

Unchanged: the argmax question is open; the Euler bias expansion is imported from Bally and Talay;
uniform integrability in Proposition 6.1 is assumed; implementation safeguards are unknown; Table 4's
risk prices are taken from Table 3; the observed state path is unavailable, so no sample-wide boundary
diagnostic is computed; the active constraint in `C_obs` and `C_glob` cannot be identified; and the
limit of `D_N` in Appendix H is unresolved.
