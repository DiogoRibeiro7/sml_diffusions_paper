# Adversarial review, round two

Second hostile pass, conducted after the round-two corrections and without relying on the earlier
review reports. The manuscript was not modified during the review pass; the issues below were
recorded first and then fixed, with resolutions noted.

Severity: **publication blocking** / **major** / **minor** / **editorial**.

## The ten questions

### 1. Does Detemple et al. already contain any result still claimed as new?

**No, after correction.** The round-two audit (`docs/detemple_overlap_audit.md`) read the full
CIRANO working-paper text and found four claims that the manuscript had been treating as its own
framing. All four are now explicitly disclaimed in §1.1, which states verbatim that the paper
claims *none* of the following as new: the kernel interpretation, the dimension dependence
including the exponent `2/(d+4)`, the bias–variance trade-off and optimal allocation, the
inadequacy of the Brandt and Santa-Clara condition, the need for joint limits, or the case for
bridge proposals.

What remains claimed — exact finite-`M` moments, the exact local constant `c_{r,K}`, the collapse
sequence, the refutation of Lemmas 2 and 3, the four-dimensional incompatibility, and the
application analysis — was searched for in the full text and is absent.

**Residual risk, disclosed.** Detemple et al. attribute the kernel reading to Milstein,
Schoenmakers and Spokoiny. That paper was not read in full; only its abstract and publisher record
were consulted. If it contains exact finite-discretisation moments for the multidimensional
Gaussian endpoint kernel, claim (a) in §1.1 would need narrowing further. Its abstract describes a
forward–reverse estimator that is root-`N` consistent in any dimension, which is a different
construction, so this is judged unlikely but not excluded.

### 2. Are Lemmas 2 and 3 identified correctly as directly refuted?

**Yes.** Corollary 3.5 proves that `√S_n(q̂ − p) → −∞` in probability along `M_n = S_n = n`, so the
sequence is not tight and has no weak limit. Remark 3.7 states the four-level hierarchy in one
place: Lemmas 2 and 3 false; proofs of Theorems 1 and 2 fail; conclusions of the
parameter-estimator theorems not disproved. §7.3 gives both the ill-posedness objection and the
falsity objection separately, and notes the second does not depend on identifying the intended
limiting variance.

One point of care: the refutation of Lemma 3 is a corollary of Theorem 3.3, so it inherits the
requirement `K > 2`. Since the application has `K = 4`, this is not a limitation in context, but
the corollary states `K > 2` explicitly rather than leaving it implicit.

### 3. Does every numerical state in Appendix E satisfy the complete variance identity?

**Yes, and this was the round-one failure.** Every row of Table 10 now reports `Q`, `C`, the implied
`ε²` and `v`, so feasibility is visible. The two rows with negative eigenvalues carry
`ε² = −0.003` and are labelled infeasible in bold. No claim rests on them.

The systematic search sweeps rates to 100× their long-run means and `ε² ∈ {0, 0.005, 0.02, 0.10}`,
always taking `v` from the identity, and finds a worst minimum eigenvalue of `+0.0128`. Verified
independently in `test_no_feasible_psd_violation_in_the_searched_range`.

**Limitation, disclosed in the appendix.** `C` is read from Table 3, which is the constant-risk-price
specification. For models B and C, `C_t` is state dependent and in model C depends on `v_t` itself,
so feasibility cannot be evaluated without the observed state series. Appendix E says this and
makes no claim about B and C. A referee could reasonably ask for the analysis to be completed with
the data; it cannot be completed without them.

### 4. Does Proposition F.1 rely on unproved convexity?

**No, after correction.** It previously argued that the feasible set is an interval because the
correlation matrix depends affinely on the free parameter and the PSD cone is convex. Affine
dependence was never established. The proposition now assumes only nonemptiness and compactness,
and the proof uses strict monotonicity of an affine function on a compact set, plus a boundary
argument. The finite-union-of-intervals case is handled explicitly.

### 5. Is antithetic sampling described correctly?

**Yes, after correction, and the correction reversed the sign.** The manuscript had said the
antithetic contributions are perfectly negatively dependent. New Proposition 8.1 proves that at a
coincident endpoint they are *identical*: the summand depends on the preterminal draw only through
`‖y − Z‖²`, which is invariant under reflection about `x` when `y = x`. So the correlation is `+1`
and the pair is worth one draw, not two. Away from the endpoint it is neither `−1` nor reliably
negative: `+0.063` at `K = 4, ‖y − x‖ = 0.5`, `−0.479` at `K = 1, ‖y − x‖ = 0.5`.

`S` is now defined once as the number of independent draws, equivalently antithetic pairs, and the
diagnostics use that convention. The dimensional exponent is stated to be unaffected; only the
variance constant changes.

### 6. Is the volatility quadratic interpreted only as an inverse-map problem?

**Yes.** Appendix D opens by stating that the analysis is not a claim about what the estimator
computes, and that the implementation takes `v` as primitive and uses the identity in the easy
direction. The abstract, introduction, §8.1 summary and conclusion were each rewritten to the
inverse-map formulation. A sweep for "solves a quadratic at every Euler step", "the implemented
diffusion has two volatility branches" and "the specification has no unique volatility" returns
nothing.

### 7. Is Proposition C.1 correct for the declared sign convention on `β`?

**Yes, after correction, and it is now exact rather than asymptotic.** The proposition declares
`β > 0`, matching the reported estimates, and states the `|β|` convention for `β < 0`. The exact
maximiser is `β²h/(1 − 2αh)` and the exact supremum is `Φ(−√(1 − 2αh))`, replacing the previous
compactness argument. Verified against a grid search and against direct simulation at three step
sizes and three parameter sets; agreement to eight decimal places against the grid.

The proposition now also separates worst-case from average-path risk explicitly, and says that the
dangerous region shrinks with `h` so the overall risk depends on the invariant law.

### 8. Are all rate descriptions consistent with their equations?

**Yes, after correction.** Two errors were fixed. "No amount of additional simulation repairs that"
became a statement that divergence of `S` alone is insufficient and that a fast enough rate does
repair the estimator. The bias condition, previously described loosely as an upper bound on `S`
relative to `√M`, is now given as `S/M^{2+K/2} → 0`, equivalently `√S/M^{1+K/4} → 0`, with the
`K = 4` case `S ≪ M⁴` and the pair `M² ≪ S ≪ M⁴` stated together.

### 9. Are strictly positive Euler negativity probabilities described quantitatively?

**Yes, after correction.** "Numerically nil" is gone. Table 6 reports `z`-scores of 111 to 203 at
the long-run means, base-ten log probabilities from `−2667` to `−8986`, and whether double-precision
evaluation underflows. The text says the probabilities are strictly positive because Gaussian
increments have full support, and separates that structural point from the magnitude.

### 10. Does Appendix H distinguish proof, heuristic, conjecture and simulation?

**Yes, after correction.** Four levels are now labelled: Propositions H.1 and H.2 as an exact
identity and a proved bound; the nearest-neighbour limit as a conjecture, explicitly not asserted
and used nowhere; and the numerical observations as observations, confined to
`notes/argmax_counterexample.md` rather than reported as a finding. "The two objectives have no
reason to share a maximiser" was replaced by a statement about what the bound does and does not
imply. "The simulated maximiser is consistent" became "appears to approach `θ₀`".

## Issues found in this pass

| # | Severity | Location | Problem | Resolution |
| --- | --- | --- | --- | --- |
| 1 | **publication blocking** | App. E, round-one text | The volatility floor was `√Q`, ignoring `C ≥ 0`; the reported negative eigenvalues came from states with `ε² = −C < 0` | Rebuilt on the complete identity; counterexample withdrawn; Prop. E.2 made conditional with a null-space proof; three dependent sentences rewritten |
| 2 | **publication blocking** | §1.1, round-one text | Four claims already in Detemple et al. were presented as this paper's framing, including the inadequacy of the BSC condition, which they state naming BSC | §1.1 rewritten with an explicit disclaimer; audit document with verbatim quotations and page numbers |
| 3 | **major** | §7.2, round-one text | Only Lemma 2 was said to be directly refuted; Lemma 3's joint CLT is equally refuted by the same sequence | New Corollary 3.5 with proof; Remark 3.7 states the hierarchy |
| 4 | **major** | §8.2, round-one text | Antithetic contributions described as perfectly negatively dependent | Proposition 8.1: at `y = x` they are identical; correlation `+1` |
| 5 | **major** | Prop. F.1, round-one proof | Convexity of the feasible set assumed via unproved affine dependence | Restated using compactness only |
| 6 | **major** | Prop. C.1, round-one text | `β ≠ 0` allowed but `β` used unsigned in the standard deviation; only an asymptotic result | `β > 0` declared; exact maximiser and maximum proved |
| 7 | **minor** | App. B, round-one text | Strictly positive Gaussian tail probabilities called "nil" | Quantified in Table 6 |
| 8 | **minor** | §1.1, round-one text | "No amount of additional simulation repairs that" | Corrected |
| 9 | **minor** | Rem. 4.10, round-one text | Bias condition described at the wrong power | Restated as `S/M^{2+K/2} → 0` |
| 10 | **minor** | App. H, round-one text | Conjecture and simulation presented alongside proved results without labels | Four levels labelled; numerics moved to notes |
| 11 | **editorial** | Conclusion; App. F | "drives it onto its degenerate boundary exactly" stated unconditionally | Made conditional on Prop. F.1 case (i) |
| 12 | **editorial** | App. F | Interiority of `ρ_zz*` claimed "in every specification" | Restricted to the time-varying specifications where Table 4 reports it |

All twelve are resolved. Items 1 and 2 changed what the paper claims; 3 to 6 changed theorem
statements or proofs; 7 to 12 changed wording.

## Open problems and limitations

Stated in the manuscript, not only here.

1. **The argmax question.** No counterexample to consistency of the simulated-likelihood maximiser.
   The nearest-neighbour limit that would settle it is a conjecture requiring uniform-in-`θ`
   asymptotics for exchangeable atoms.
2. **Models B and C feasibility.** `C_t` is state dependent there and, in model C, depends on `v_t`,
   so Appendix E's feasibility analysis covers only the constant-risk-price specification. The
   observed state series would be required.
3. **The Euler bias expansion** is imported from Bally and Talay, not proved here.
4. **Uniform integrability** in Proposition 6.1 is assumed.
5. **Implementation safeguards** are unknown and labelled so.
6. **One reference not read in full**: Stramer and Yan (2007a), paywalled, with no open version
   located. Milstein, Schoenmakers and Spokoiny (2004) has since been read in full; see question 1.
   The residual risk from Stramer and Yan is structurally smaller: the estimator they analyse is
   the modified Brownian bridge sampler, not the unconditioned endpoint estimator, and the
   manuscript states that distinction. Their bibliographic record is confirmed against Crossref.
7. ~~One DOI unresolved.~~ **Resolved, and it was wrong.** The recorded Detemple DOI had been
   guessed and belonged to a different article in the same volume. Every DOI in the bibliography is
   now verified by title against the Crossref registry; 24 of 24 match and the four entries without
   a DOI are books or journals that register none.
8. ~~Author metadata unresolved.~~ **Resolved.** Affiliation, email and ORCID were supplied by
   the author and the release gate now passes.

## Conclusion

Zero publication-blocking mathematical errors remain. Two were found in this pass, both in
material added or framed during the first round, and both are fixed with regression tests. Every
feasible-state calculation is reproducible through `make verify` and the pytest suite. All
unresolved questions are disclosed above and in the manuscript.
