# Adversarial mathematical review

A line-by-line verification pass over every theorem, proposition, corollary and displayed
asymptotic claim, conducted as a hostile referee would: assuming each result is wrong until the
proof and an independent check say otherwise. The manuscript was not edited during the first
pass; the issues found are listed with resolution notes below, and each fix was applied
afterwards and re-verified.

Constants were checked symbolically or by high-precision numerical integration, not by agreement
with the paper's own simulations. Numerical agreement alone was never accepted as verification of
a theorem.

## Verification table

| Result | Claim | Assumptions | Depends on | Dim. | Limit order | Proof complete | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Prop. 3.1 | Exact $\mathbb E[G_h^r]$ for Brownian motion | none beyond the model | Gaussian identity | all $K$ | finite $M$, no limit | yes | **verified** against quadrature for $K\in\{1,2,4,5\}$, $M\in\{4,32,256\}$, $r\in\{1,2,2.5,3\}$, two separations |
| Cor. 3.2 | $\operatorname{Var}(\hat q)\sim\tau_K^2/(Sh^{K/2})$ | Prop. 3.1 | Prop. 3.1 | all $K$ | $h\downarrow0$ | yes | **verified**; also checked against direct simulation |
| Thm. 3.3 | Collapse in probability along $M=S$, $K>2$ | BSC Assumptions 1–2 | Gaussian tail bound only | $K>2$ | joint | yes | **verified**; independent of every CLT in the paper |
| Rem. 3.6 | Incompatibility is unconditional for $K\ge4$; $K=3$ admits compatible sequences | — | Cor. 3.5 | $K\ge4$ vs $K\le3$ | joint | yes | **verified**; witness $S=M^{7/4}$ at $K=3$ checked |
| Thm. 3.7 | Brownian density CLT at $\sqrt{Sh^{K/2}}$ | $Sh^{K/2}\to\infty$ | Prop. 3.1 | all $K$ | joint, triangular array | yes | **verified** after fix (i) below |
| Ass. 4.1 | Global regularity (A1)–(A5) | — | — | all $K$ | — | n/a | **verified**: no condition now presupposes its conclusion |
| Thm. 4.2 | $h^{(r-1)K/2}\mathbb E[G_h^r]\to c_{r,K}\,p\,|V|^{-(r-1)/2}$ | Ass. 4.1, $r>1$ | dominated convergence | all $K$ | $h\downarrow0$ | yes | **verified** after fix (ii); constant checked against the Brownian case symbolically |
| Cor. 4.3 | $\tau^2=(4\pi)^{-K/2}p|V|^{-1/2}$ | Thm. 4.2 at $r=2$ | Thm. 4.2 | all $K$ | $h\downarrow0$ | yes | **verified**: $(2\pi)^{-K/2}2^{-K/2}=(4\pi)^{-K/2}$ |
| Thm. 4.4 | Generic density CLT | Ass. 4.1, $R_n\to\infty$ | Thm. 4.2 at $r=2,3$ | all $K$ | joint | yes | **verified** after fix (i) |
| Cor. 4.5 | CLT centred at $p$; $M^2\ll S\ll M^4$ at $K=4$ | + Euler bias expansion | Thm. 4.4, Bally–Talay | all $K$ | joint | yes | **verified**; $\sqrt S/M^{1+K/4}\to0\iff S/M^{2+K/2}\to0$ checked; regime nonempty via $S=M^3$ |
| Prop. 5.1 | $M\asymp S^{2/(K+4)}$, MSE $\asymp S^{-4/(K+4)}$ | bias expansion, Cor. 4.3 | no CLT | all $K$ | $h\downarrow0$ | yes | **verified**; exponents checked for $K\in\{1,2,4,8\}$ |
| Prop. 6.1 | Log-density expansion and $-\tau^2/(2p^2R)$ bias | + uniform integrability, lower-tail control | Thm. 4.4 | all $K$ | joint | **conditional** | **verified as conditional**; the third statement is assumed, and the text says so |
| Prop. 6.2 | Abstract equivalence to exact MLE | (i)–(iv) as listed | none | — | — | yes, but vacuous for the simulated estimator | **verified as an abstract implication**; labelled as such, conditions not verified for the estimator |
| Prop. B.2 | $\sup_xP_h(x)\to\Phi(-1)$ at $H\sim\beta^2h$ | $\alpha>0$, $\beta\ne0$ | substitution | — | $h\downarrow0$ | yes | **verified** numerically at three step sizes and three parameter sets |
| Prop. D.1 | Branch structure; $\kappa_b>1$ gives zero or two positive roots | $\zeta_t>0$ | sign analysis | — | — | yes | **verified**; all four cases exercised by tests |
| Prop. E.1 | Entrywise validity is automatic above the volatility floor | variance identity | algebra | $K=4$ | — | yes | **verified**: $Q_t-(\phi_t-\rho\phi_t^*)^2=\phi_t^{*2}(1-\rho^2)\ge0$ |
| Prop. E.2 | $\rho_{xy}$ over-determined at the floor | $Q_t>0$ | rank argument | $K=4$ | — | yes | **verified** numerically: indefinite matrices with all entries inside $[-1,1]$ |
| Prop. F.1 | Corner solution over the complete feasible set | $\mathcal C$ compact, slope $\ne0$ | convexity of the PSD cone | — | — | yes | **verified** against a brute-force optimiser, including a case where a range restriction binds first |
| Prop. H.1 | CRN reduction is an exact KDE identity | location model | algebra | all $K$ | — | yes | **verified** to $10^{-11}$ against direct Euler simulation |
| Prop. H.2 | Nearest-atom sandwich bound | location model | factorisation | all $K$ | — | yes | **verified** after fix (iii) below |

## Issues found and resolved

### (iii) Sign error in the sandwich bound of Proposition H.2 — **publication-blocking, fixed**

This was the only substantive mathematical error found, and it was introduced by this revision
rather than inherited.

The proposition stated

$$ 0 \le 2h\log\hat{\mathcal L} + D_N + NhK\log(2\pi h) \le 2Nh\log S, $$

but the factored term lies in $[1/S,1]$, so its logarithm lies in $[-\log S,0]$ and the correct
statement is

$$ -2Nh\log S \le 2h\log\hat{\mathcal L} + D_N + NhK\log(2\pi h) \le 0 . $$

A direct numerical evaluation at $K=3$, $N=12$, $S=7$, $M=9$ gave values near $-4.7$, outside the
stated interval $[0,5.19]$ and inside the corrected one. The conclusion drawn from the bound is
unaffected, because only the magnitude of the slack, $2Nh\log S$, is used. Fixed in the manuscript
and in `notes/argmax_counterexample.md`, and locked in by
`test_nearest_atom_sandwich_bound`, which checks the sign as stated.

### (i) Centred versus raw third moment — **gap, fixed**

Both central limit theorems previously asserted that the third absolute *centred* moment inherits
the $O(h^{-K})$ order of the raw third moment, with the words "the same order holds". That is a
step, not an observation. It is now proved: the summand is a Gaussian density value and therefore
nonnegative, so $|a-b|^3\le4(a^3+b^3)$ applies, and $\mathbb E G_h=q_M$ is bounded. Nonnegativity
is what makes the argument elementary and is stated explicitly.

### (ii) Assumption phrased in terms of its own conclusion — **gap, fixed**

Assumption 4.1(iv) previously required the tail contribution to be "dominated by an integrable
Gaussian envelope after multiplication by the appropriate power of $h$". That is the thing the
proof needs to establish, not a hypothesis, and "the appropriate power" is undefined. Replaced by
explicit conditions (A1)–(A5), with the tail bound derived in the proof and the dominating
function exhibited.

### (iv) Iterated versus joint limits in the statements — **presentation, fixed**

Several statements wrote $M\to\infty$, $S\to\infty$ without indexing, leaving it ambiguous whether
a joint or an iterated limit was meant — the very confusion the paper criticises. All limit
statements now index a single sequence $(M_n,S_n)$ with $h_n=1/M_n$.

### (v) Density-estimator failure conflated with argmax failure — **fixed under prompt 2**

Recorded here for completeness: the manuscript previously described the Brownian construction as a
counterexample to Theorem 1 of Brandt and Santa-Clara. It is a counterexample to their Lemma 2.

### (vi) Effective-size arithmetic — **fixed under prompt 7**

$R(2M,2S)=R/2$, not $R/4$.

## Adversarial tests applied

Each of the following was tested against every result in the table.

1. **Constants.** Every factor of $2\pi$, $4\pi$, determinant power and power of $h$ was
   re-derived independently. The cancellation $h^{(r-1)K/2}\cdot h^{-rK/2}\cdot h^{K/2}=h^0$ in
   the tail bound and the local term was checked separately in both places.
2. **Centred versus raw moments.** See (i).
3. **Pointwise versus uniform.** Theorem 4.2 and both CLTs are pointwise in $(x,y)$. No result
   claims uniformity, and the log-likelihood discussion says explicitly that summing over $N$
   observations requires uniform control that is not supplied.
4. **Iterated versus joint.** See (iv). Theorem 3.3 is the point of the paper here and is
   unambiguously joint.
5. **Convergence in probability versus $L^2$.** Theorem 3.3 gives convergence in probability while
   the mean is exactly correct at every $M$; the accompanying remark states that the sequence is
   not uniformly integrable, so the two modes genuinely diverge. This was the one place where a
   careless reading could conflate them, and it is addressed in the text.
6. **Exact versus approximate densities.** The Brownian benchmark has $q_M=p$ exactly; the general
   results centre at $q_M$ and only Corollary 4.5 centres at $p$, at the cost of an imported bias
   expansion. Checked that no result silently substitutes one for the other.
7. **Fixed-$M$ versus triangular array.** Remark 4.6 states why a fixed-$M$ CLT cannot be reused.
   No proof in the manuscript invokes one.
8. **Finite-sample diagnostics versus asymptotics.** Section 8 opens by saying nothing in it is an
   asymptotic theorem. No diagnostic is phrased as a limit statement.
9. **Density failure versus argmax failure.** See (v). Section 7.6 and Appendix H set out the gap.
10. **Sign conditions in the quadratic analysis.** All four branch cases were enumerated and
    tested, including the repeated-root boundary and the case $\eta_t\ge0$ where no positive root
    exists.

## Unresolved and disclosed

These are stated in the manuscript as open, not hidden.

1. **The argmax question.** No counterexample to consistency of the simulated-likelihood
   maximiser was obtained. The nearest-neighbour limit of Appendix H would settle it but requires
   a uniform-in-$\theta$ law for exchangeable rather than independent atoms.
2. **The Euler bias expansion** $q_M-p=b(x,y)h+o(h)$ is imported from Bally and Talay, not proved
   here. Corollary 4.5 and Proposition 5.1 depend on it.
3. **Uniform integrability in Proposition 6.1.** Assumed. Given that the estimator's own
   distribution is not uniformly integrable in the collapse regime, this assumption deserves more
   scepticism than it usually receives, and the text says so.
4. **Parameter-level rate conditions** in equation (28) are labelled a design implication, not a
   theorem, because derivatives of the simulated paths can impose stronger requirements.
5. **`StramerYan2007a` was not read in full** (paywalled). Nothing in the manuscript depends on
   its detailed contents; see `docs/bibliography_audit.md`.

## Conclusion

Zero publication-blocking errors remain. One was found during this pass, in Proposition H.2, and
is fixed and regression-tested. The full build and reproducibility suite were re-run after the
fixes: 132 tests pass, 25 of 25 artefacts reproduce exactly, and the LaTeX log is free of errors,
undefined references, undefined citations and overfull boxes.
