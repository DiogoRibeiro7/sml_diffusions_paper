# Final claim dependency audit

Every substantive claim in the abstract, introduction, Section 8, conclusion and Appendices C to G,
with what it rests on and what it refers to. Compiled after the third revision round on branch
`fix/final-mathematical-review`.

## Logical categories

| Code | Meaning |
| --- | --- |
| **T** | proved theorem in this paper |
| **A** | proved algebraic proposition in this paper |
| **C** | conditional statement: proved under hypotheses this paper does not verify |
| **G** | numerical grid or finite-sample diagnostic |
| **R** | statement reported by Brandt and Santa-Clara, not independently verified here |
| **U** | unknown implementation detail, recorded as unknown |
| **L** | literature-based claim, attributed |

## Referents

Application claims are ambiguous unless the object is named, so each row records one of:
generic endpoint estimator (**gen**); direct `H`-state Euler scheme (**dirH**); transformed
`v`-state implementation (**impV**); inverse volatility map (**inv**); published optimisation
constraints (**Cpub**); mathematically complete model constraints (**Cmath**).

## Core theoretical claims

| Claim | Cat. | Support | Assumptions | Referent | Revised | Supported |
| --- | --- | --- | --- | --- | --- | --- |
| Effective simulation size is `S/M^{K/2}`, not `S` | T | Def. 2.1, Thm 4.2, Cor. 4.3 | (A1)–(A5) | gen | no | yes |
| Exact finite-`M` Brownian moments of every order | T | Prop. 3.1 | none beyond the Brownian setting | gen | no | yes |
| Collapse in probability along `M = S` for `K > 2` | T | Thm 3.3 | BSC Assumptions 1–2 and their rate condition | gen | no | yes |
| `√S(q̂ − p) → −∞` | T | Cor. 3.5 | as above | gen | no | yes |
| Local moment constant `c_{r,K} = (2π)^{−(r−1)K/2} r^{−K/2}` | T | Thm 4.2 | uniform ellipticity | gen | no | yes |
| Triangular-array CLT under `S/M^{K/2} → ∞` | T | Thm 4.4 | Lyapunov condition verified | gen | no | yes |
| MSE-optimal `M ≍ S^{2/(K+4)}` | T | §5 | first-order Euler density bias | gen | no | yes |
| Lemmas 2 and 3 of BSC are false | T | Thm 3.3, Cor. 3.5 | their own assumptions | gen | no | yes |
| In `K = 4` no admissible sequence exists | T | Cor. 3.4, Rem. 3.6 | — | gen | no | yes |
| Log-density expansion | C | Prop. 6.1 | uniform integrability, lower-tail control, both assumed | gen | no | conditional, labelled |
| Exact and simulated maximisers agree at `√N` | C | Prop. 6.2 | six hypotheses incl. consistency of the simulated maximiser | gen | **yes** | conditional, labelled |
| The argmax estimator is inconsistent | — | **not claimed** | — | gen | — | explicitly disclaimed, §7.6 |

## Application claims

| Claim | Cat. | Support | Referent | Revised | Supported |
| --- | --- | --- | --- | --- | --- |
| The implemented ratios are not small | G | Table 3, `N=544`, `M=10`, `P=5,000` | impV | yes, `P`/`E` split | yes |
| Antithetic pairs are identical at a coincident endpoint | A | Prop. 8.1 | gen | yes, `P`/`E` | yes |
| `N_eff = E/(1+ρ_A)` | A | Def. 8.2, from Prop. 8.1 | gen | **new** | yes |
| `E` overstates the effective count by `1+ρ_A` | A | eq. (two ratios) | gen | **corrected** | yes |
| `E` overstates it by `2/(1+ρ_A)` | — | **withdrawn as false** | — | **yes** | that ratio is `N_eff/P`, and equals 1 at `ρ_A=1` |
| `P/M^{K/2}` is the effective size of the antithetic design | — | **withdrawn** | — | **yes** | now `R_pair`, an independent-pair diagnostic |
| `R_var ≥ R_pair` always | A | `ρ_A ≤ 1` | gen | new | yes |
| A single `N_eff` applies to the whole likelihood | — | **not claimed** | gen | new | disclaimed: `ρ_A` varies by transition |
| Antithetic pairing preserves the `h^{−K/2}` exponent | A | Lemma 8.2 | gen | **new** | yes |
| Interest-rate Feller ratios are comfortable | G | Table 6 | dirH | no | yes |
| The incompleteness Feller ratio is exactly 1/2 | A | App. C | dirH | no | yes |
| Direct Euler on `H` is not positivity preserving | A | Prop. C.1 | **dirH** | yes, scope list added | yes |
| Worst-case one-step probability `Φ(−√(1−2αh))` | A | Prop. C.1 | **dirH** | no | yes |
| Refinement does not lower the worst case | A | Prop. C.1 | dirH | no | yes |
| Refinement reduces time spent in the region | — | **withdrawn** | — | **yes** | no longer claimed |
| Crossing frequency for the implemented chain | — | **not claimed** | impV | yes | explicitly disclaimed |
| No intermediate-violation convention is documented | U | published paper is silent | impV | no | yes, as unknown |
| The inverse map is not globally single-valued | A + G | Prop. D.1, grid | **inv** | yes, wording | yes |
| No candidate point admits exactly one positive root | G | six grid designs | inv | yes | yes, as a grid fact |
| 37,536 of 56,784 points admit no positive root | G | baseline grid | inv | **yes**, was "66% of the state space" | yes, as a count |
| The proportion is a model property | — | **withdrawn** | — | **yes** | no longer claimed; ranges 58–96% across designs |
| The diffusion visits the failure region | — | **not claimed** | inv | yes | explicitly disclaimed |
| Two implied correlations are automatically bounded | A | Prop. E.1 | Cmath | yes, scope | yes |
| All correlations are automatically bounded | — | **withdrawn** | — | **yes** | no longer claimed |
| Entrywise bounds are insufficient for PSD | A | Lemma E.1, Prop. E.2 | Cmath | no | yes |
| Degenerate PSD needs compatibility **and** magnitude | A | Lemma E.1, Prop. E.2 | Cmath | **new** | yes |
| Compatibility alone suffices | — | **withdrawn as false** | — | **yes** | refuted by explicit counterexample |
| No feasible state has an indefinite matrix | G | Table 12, sweep, 5,000 perturbations | Cmath | no | yes, within the search |
| The calibrated model reaches an invalid matrix | — | **withdrawn** in round 2 | — | no | no longer claimed |
| The minimum-incompleteness optimum is a vertex | A | Prop. F.1 | Cpub or Cmath | yes, representation | yes |
| `min_t eps² = 0` exactly, constant case | A | Prop. F.1(iii) | **Cpub** | yes | yes, under stated conditions |
| `min_t eps² = 0`, time-varying cases | **R** | BSC report it | Cpub | **yes**, was inferred | yes, as reported |
| The active constraint in `Cmath` is nonnegativity | — | **withdrawn** | — | **yes** | cannot be determined |
| Implementation safeguards | U | not described | impV | no | yes, as unknown |
| The empirical estimates are wrong | — | **not claimed** | — | — | explicitly disclaimed |

## Mandatory checks

| Check | Status |
| --- | --- |
| Proposition E.2 contains both range and magnitude conditions | pass |
| Only `ρ_wx` and `ρ_w*x` described as automatically bounded | pass |
| Grid points not called reachable | pass, gated |
| Grid percentages not interpreted probabilistically | pass, gated |
| Proposition 6.2 localises both maximisers | pass |
| Proposition F.1 has explicit continuous constraints | pass |
| Time-varying binding attributed to the published paper | pass |
| Direct-`H` results not applied to the implemented chain | pass, gated |
| Shrinking region not said to imply lower occupation | pass, gated |
| `P` and `E` used for pairs and evaluations | pass |
| `N_eff = E/(1+ρ_A)` appears correctly | pass |
| `E/N_eff` distinguished from `N_eff/P` | pass, gated |
| At `ρ_A = 1`, `E` said to overstate by two | pass |
| `P/M^{K/2}` called a diagnostic, not an exact effective size | pass, gated |
| The `h^{−K/2}` exponent proved to survive pairing | pass, Lemma 8.2 |
| Milstein covariance and bandwidth wording correct | pass |
| No unsupported novelty claim | pass |
| Conclusion does not reintroduce removed overstatements | pass, gated |

Nineteen forbidden-phrase patterns are enforced by `code/check_forbidden_phrases.py`, run by
`make check` and blocking in `code/make_release.py`.
