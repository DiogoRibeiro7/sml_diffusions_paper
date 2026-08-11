# Targeted final review

> **SUPERSEDED — retained for the audit history.** This document records the state of the work at the time it was written, including statements later corrected or withdrawn. Do not read it as the current theorem statement; see `docs/change_log_referee_round_three.md` for the current round and `paper/main.tex` for the statements themselves.

Fourth round, restricted by design to the nine issues listed below. The core results were not
reopened: no error was found in them, and none was looked for beyond confirming they still compile,
still reproduce and are still stated as before.

## 1. Antithetic arithmetic

**Was: a false statement.** The round-three `P`/`E` rewrite proved
`Var(A_i) = σ²(1+ρ_A)/2` correctly and then misread it, claiming `E` "overstates the independent
count by the factor `2/(1+ρ_A)`, which at a coincident endpoint is exactly two". Both halves wrong:
the overstatement factor is `E/N_eff = 1+ρ_A`, and `2/(1+ρ_A)` evaluates to **one** at `ρ_A = 1`, so
the sentence contradicted its own numerical claim.

Now: `N_eff = E/(1+ρ_A) = 2P/(1+ρ_A)` is a numbered definition; both ratios appear side by side; the
four cases are stated, including `ρ_A → −1` as a convention rather than a literal count.
`P/M^{K/2}` is `R_pair`, an independent-pair diagnostic, reported beside `R_var = N_eff/M^{K/2}`,
with `R_var ≥ R_pair` always because `ρ_A ≤ 1`. Table 3 gives `R_var` at two reference values rather
than one assumed value, and the caption notes that no separate `N_eff` column is needed there because
`N_eff(1) = P` and `N_eff(0) = E`.

New Lemma 8.2 proves the exponent survives: `(a²+b²)/4 ≤ A² ≤ (a²+b²)/2` pathwise for nonnegative
partners, hence `E[G²]/2 ≤ E[A²] ≤ E[G²]` for any dependence, hence `E[A²] ≍ h^{−K/2}`.
Nonnegativity is used only for the lower bound; `E[A] = O(1)` carries the order to the variance.
**Resolved.** 26 tests.

## 2. Proposition F.1 and the three feasible sets

**Was: a finite-`J` representation applied to an infinite constraint family.** The round-three fix
gave the proposition an explicit representation with finitely many continuous constraints, which is
correct for the observed-date sets, but the enlarged model requirement — positive semidefiniteness at
*every* state of a continuous domain — is indexed by a continuum and has no such representation.

Now three sets are distinguished: `C_pub` (affine, a polyhedron), `C_obs` (adds `N` continuous
constraints, still finite), and `C_glob` (an infinite family). The proposition is split. **Part A**
locates the minimiser using compactness alone and no representation, so it covers all three.
**Part B** identifies the active constraint and requires the finite representation. The proof now
says explicitly why: a minimum of finitely many positive numbers is positive, whereas an infimum over
infinitely many constraints may be zero, so the common `δ` in the contradiction argument is not
available for `C_glob`.

"Linear programme" is now used only for `C_pub`, where every constraint is affine; the enlarged
problems are called affine-objective constrained optimisation problems. The corner formula
`c* = min_t A_t` is stated with all four conditions, and with the observation that a global
constraint may cut the interval first. **Resolved.** 12 tests, including one exhibiting an infinite
family whose members are each slack at a point while their infimum is zero.

## 3. Algebraic versus dynamic language

Eight further replacements: "reference states the calibrated model can reach" → "reference points
satisfying the reported algebraic restrictions"; "the degenerate configuration is not reachable" →
"algebraically infeasible ... because it requires `C_t = 0` while `C = 0.003 > 0`"; "model-feasible
state" → "algebraically feasible point" throughout; "a state the calibrated model does not reach" →
"a point the reported estimates render algebraically infeasible". Section 8.1(iv) now gives the exact
baseline count, 37,536 of 56,784, rather than "most candidate grid points".

A new remark in Appendix E states the distinction once and for all: algebraic feasibility is not
dynamic accessibility, and establishing the latter would need a support theorem, an accessibility
argument, or transition-density analysis. Two forbidden-phrase patterns now guard it.
**Resolved.**

## 4. CIR boundary language

**Was: unattainable conflated with unapproachable.** "The boundary is never approached" is a
pathwise claim that the Feller condition does not support: the condition makes the exact origin
unattainable from a positive start, but says nothing about how close the process comes.

Now: the Feller ratio gives unattainability; the displayed benchmark states give negligible one-step
probabilities; and the text says plainly that without the observed rate path no sample-wide maximum
is established. The introduction, Section 8.1(i), Section 9.5 and the conclusion all use this
formulation.

**Table 5 caption matched to its columns.** The caption referred to an "underflow" column that did
not exist. The column now exists, populated from `cir_negativity` in `code/generate_results.py`, and
the caption defines the `z`-score, the base-ten log tail, the underflow criterion (direct IEEE-754
binary64 evaluation returning exactly zero, below about `1e−308`) and the fact that underflow is a
property of double precision rather than of the mathematics. **Resolved.** Four tests, including the
stable log-CDF against the Gaussian asymptotic `φ(z)/z`, and a test that the hand-typed manuscript
values still match the generated CSV, which closes a standing drift risk.

## 5. Exact binding

A status table now fixes the hierarchy in one place: proved conditionally for the constant
specification; reported by the original authors for the two time-varying ones; corroborative only for
the rounded `0.0000`; unresolved for `C_obs` and `C_glob`. Appendices B and C were rewritten to match,
and Appendix C now states three things that do *not* follow from an observed-date binding constraint:
that every simulation starts on the boundary, that any intermediate simulated state reaches it, or
that the original code ever evaluated coefficients at an exact floating-point zero. **Resolved.**

## 6. Correlation count

**Was: a miscount introduced in round three.** Table 11 listed `ρ_zz*` among the correlations of the
reduced `4×4` matrix. It is not an entry of that matrix: it enters the currency-risk quadratic form
`C_t` and reaches `R_t` only through `v_t`.

Now: five primitive correlation parameters, of which four are entries of `R_t`; two implied
state-dependent entries; six off-diagonal entries in total, which is what a symmetric `4×4` matrix
has. Table 11 gains columns for "in `R_t`" and "in `C_t`" so the distinction is visible per row. The
magnitude condition of Proposition E.3 is described as a joint restriction on `ρ_ww*`, `ρ_wy` and
`ρ_w*y`, with the compatibility relation determining `ρ_xy`. **Resolved.** A structural test asserts
the 4 + 2 = 6 decomposition and that `ρ_zz*` is outside it.

## 7. Path risk

**Was: too strong a negative.** The text said no bound was available "in the useful direction". A
union bound is always available and needs no independence.

Now stated: `P(∪F_j) ≤ Σ P(F_j) ≤ m sup_x P_h(x)`, followed by why it is useless here. With
`sup_x P_h ≈ 0.1587` the bound reaches one at `m = 7`; at `m = 10, 20, 520` it gives `1.59`, `3.17`
and `82.5`, all clipping to 1. Product formulas such as `1 − (1−p)^m` remain rejected, since
successive Euler states are dependent. **Resolved.**

## 8. Conclusion and front matter

Checked for reappearance of every corrected overstatement. The conclusion now uses the algebraic
formulation for the grid, the split status for binding, the unattainable-not-unapproachable
formulation for the interest rates, and the corrected correlation inventory. The abstract makes no
application-level claim. The central mathematical contribution is stated exactly as before.

## Verification

| Check | Result |
| --- | --- |
| Test suite | 209 passing, up from 193 |
| Artefacts | 33/33 bit-exact |
| LaTeX | 0 errors, 0 undefined references, 0 multiply-defined labels, 0 overfull or underfull boxes |
| Pages | 57 |
| Forbidden phrases | 0 hits, 28 patterns across 5 files |
| DOIs | 24/24 Crossref-verified |
| Release gate | passes, no bypass flags |

## Outcome

**No publication-blocking issue remains. No major issue remains.**

Two of the seven issues in this round were errors introduced by the round-three fixes rather than
survivals from earlier: the antithetic ratio and the correlation miscount. That is worth recording,
because it is the argument for the forbidden-phrase gate: each round's corrections are themselves a
source of new claims, and they need checking on the same terms as the original text.

The Brownian counterexample, the exact moments, the local moment law and the corrected
triangular-array CLT are unchanged, and none of them depends on any application diagnostic.

## Recorded limitations

Unchanged: the argmax question is open; the Euler bias expansion is imported from Bally and Talay;
uniform integrability in Proposition 6.1 is assumed; implementation safeguards are unknown; Table 4's
risk prices are taken from Table 3; the observed state path is unavailable, so no sample-wide
boundary diagnostic is computed for the interest rates; and the active constraint in `C_obs` and
`C_glob` cannot be identified.
