# Application claims: dependency matrix

Every application-specific claim in the manuscript, with the result or calculation it rests on and
whether that support survives the corrected feasibility analysis of Appendix E. Produced after the
second review round, in which the volatility floor was recomputed under the complete variance
identity `v² = Q + C + ε²`.

**Rule applied throughout:** no application claim may rely on a state that violates the complete
variance identity. Every claim below was re-checked against that rule, and the two that failed it
were removed.

## Status key

| Status | Meaning |
| --- | --- |
| **proved** | algebraic result with a complete proof; holds wherever its hypotheses hold |
| **conditional** | proved, but its hypotheses are not known to be satisfied by the calibrated model |
| **diagnostic** | a numerical calculation at reconstructed states, reproducible, not a theorem |
| **removed** | withdrawn in this round |

## Matrix

| # | Claim | Location | Support | Feasible state? | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Ratios corresponding to the published rate conditions are not small at `N=544, M=10, S=5000` | §8.2 | arithmetic on reported design | n/a | **diagnostic** |
| 2 | `R(M,S)=50`; `R(2M,2S)=R/2`, `R(2M,S)=R/4`, `R(2M,4S)=R` | §8.2, eq. (37) | arithmetic | n/a | **proved** |
| 3 | Antithetic pairs are not independent draws; at a coincident endpoint the pair is worth one draw | Prop. 8.1 | exact identity `G⁻ = G` at `y = x` | n/a | **proved** |
| 4 | Interest-rate Feller ratios are 6.4 to 48.5, so the origin is unattainable | App. B, Tab. 5 | reported estimates | yes | **diagnostic** |
| 5 | Interest-rate Euler negativity probabilities are strictly positive but of order `10^-2667` or smaller at the long-run means | App. B, Tab. 6 | closed-form Gaussian tail | yes | **diagnostic** |
| 6 | The incompleteness Feller ratio is exactly `1/2` for every admissible `(α, β)` | App. B | algebraic identity `2κϑ/σ² = 2β²/4β²` | n/a | **proved** |
| 7 | `sup_x P_h(x) = Φ(−√(1−2αh))` at `x = β²h/(1−2αh)` | Prop. C.1 | exact optimisation | n/a | **proved** |
| 8 | Refining the step does not reduce the worst-case per-step violation probability | App. C | corollary of #7 | n/a | **proved** |
| 9 | Worst-case risk is not average-path risk; the dangerous region shrinks with `h` | App. C | stated as a qualification | n/a | **proved** (as a negative statement) |
| 10 | The estimator simulates `(r, r*, e, v)` and recovers `ε` by a square root | App. C | BSC eq. (31), Appendix B | n/a | **diagnostic** (reading of the published equations) |
| 11 | A negative radicand makes the next substep's coefficients complex | App. C | structure of eq. (28) | n/a | **proved** |
| 12 | At least one sample date has `ε² = 0`, so one simulated transition starts on the boundary | App. C, App. F | Prop. F.1 case (i) | yes | **conditional** on the active constraint being a nonnegativity one; interiority checked in App. E |
| 13 | Reported minima of `0.0000` are rounded corroboration, not proof of exact binding | App. F | stated explicitly | n/a | **proved** (as a caveat) |
| 14 | Truncation, reflection, absorption and exact transition define different chains | App. C | stated | n/a | **proved** |
| 15 | Given `v`, the identity reconstructs `ε²` uniquely | App. D | subtraction | yes | **proved** |
| 16 | Given `ε²`, recovering positive `v` requires solving a quadratic | App. D | eq. (44) | n/a | **proved** |
| 17 | Local invertibility fails on `v = η/(1−κ_b)` | App. D | implicit function theorem | n/a | **proved** |
| 18 | At `κ_b > 1` there are zero or two positive roots, never one | Prop. D.1(ii) | sign analysis | n/a | **proved** |
| 19 | `κ_b ≈ 1.9982` for U.S.–U.K. model C; `≈ 0.0702` for U.S.–Germany | Tab. 9 | arithmetic on Table 4 | n/a | **diagnostic** |
| 20 | The U.S.–U.K. inverse map is not globally single-valued without a branch-selection condition | App. D | #18 and #19 | n/a | **conditional**, and about the inverse map, not the implementation |
| 21 | The implemented estimator solves a quadratic for `v` at each Euler step | — | — | — | **removed**; the implementation takes `v` as primitive |
| 22 | Entrywise correlation validity is automatic above `v² ≥ Q` | Prop. E.1 | `Q − (φ − ρφ*)² = φ*²(1 − ρ²) ≥ 0` | yes | **proved** |
| 23 | `C = 0.003 > 0` in both systems under constant risk prices | App. E | sum of the two quantities in Table 3 Panel B | yes | **diagnostic** |
| 24 | The feasible minimum volatility is `√(Q + C)`, not `√Q` | App. E, eq. (49) | complete variance identity | yes | **proved** |
| 25 | If `C = ε² = 0` then `ρ_xy` is over-determined and any other value makes `R` indefinite | Prop. E.2 | null-space argument; Moore–Penrose compatibility | n/a | **conditional**; the hypothesis is not satisfied at the reported estimates |
| 26 | The calibrated model reaches an indefinite correlation matrix | — | — | **no** | **removed**; the supporting states had `ε² = −C < 0` |
| 27 | Every model-feasible state examined is positive definite, `λ_min` from 0.68 to +0.0128 | App. E, Tab. 10 | reconstructed states under the full identity | yes | **diagnostic** |
| 28 | No model-feasible violation was found in a sweep to 100× long-run rates | App. E | `search_for_infeasible_psd_violation` | yes | **diagnostic** |
| 29 | Perturbation by reported standard errors produces no violation in 5,000 draws per system | App. E | Monte Carlo | yes | **diagnostic** |
| 30 | The specification supplies no parameterisation guaranteeing PSD globally | App. E | absence of such a statement in BSC | n/a | **proved** (a statement about what the paper contains) |
| 31 | Whether the implementation imposed safeguards is unknown | App. E | explicit | n/a | **disclosed as unknown** |
| 32 | The minimum-incompleteness criterion is affine in the free parameter | App. F | `ε²` is the residual | n/a | **proved** |
| 33 | An affine objective on a compact feasible set attains its minimum on the boundary | Prop. F.1 | compactness; no convexity assumed | n/a | **proved** |
| 34 | Published and mathematically complete feasible sets differ | App. F, eqs. (57)–(58) | definition | n/a | **proved** |
| 35 | The active constraint at the published estimates is a nonnegativity one | App. F | interiority of `ρ_zz*` and PSD slack from App. E | yes | **conditional**, on reconstructed states; the observed series is unavailable |
| 36 | Dispersion of `v²` rather than its level drives estimated excess volatility | App. F | corollary of the corner rule | n/a | **proved**, and acknowledged by BSC p.193 |
| 37 | Binding constraints imply nonregular inference | App. G | Self and Liang; BSC report the constraint binds | n/a | **diagnostic** |
| 38 | The final estimator is a hybrid not covered by the unconstrained SML theorem | §8.1, App. G | #32–#37 | n/a | **proved** (a statement about coverage) |

## Claims removed in this round

**#26, the PSD counterexample.** The manuscript previously reported minimum eigenvalues of
`−0.0009` and `−0.0027` at states described as the volatility floor, and used them to argue that
entrywise validity and joint validity come apart within the calibrated model. Those states set
`v² = Q`, which the complete identity permits only when `C = ε² = 0`; since `C = 0.003`, they imply
`ε² = −0.003 < 0`. They are retained in Table 10 explicitly labelled infeasible, purely to mark the
distinction, and every dependent sentence in the abstract, introduction, §8 and the conclusion has
been rewritten.

**#21, the per-step quadratic.** Removed under the volatility-map harmonisation; the implemented
estimator takes `v` as primitive.

## Downstream text checked

Abstract, §1 contribution list, §1.1, §1.2, §8.1 summary, §8.2, conclusion, and Appendices C, D, E,
F and G were each searched for sentences depending on #21 or #26. Three were found and rewritten:
the introduction's summary of the correlation finding, the §8.1 summary item on correlation
validity, and the conclusion's sentence on the Brownian correlation matrix. Two further sentences
stating that the identification rule drives the incompleteness state onto its boundary
"exactly" were made conditional on Proposition F.1's case (i).
