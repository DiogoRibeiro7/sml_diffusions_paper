# Change log, the external referee round

Baseline `96c9d2e` (v1.5.0). An external referee report on the new estimator-level material. One
finding breaks a theorem previously labelled proved; the rest are overclaims, a quantifier
imprecision, and three small proof repairs. Every finding was checked before being accepted, and
every one held.

## The serious finding: `prop:uniform_lln` was not proved

The proof established uniform integrability of the individual indexed variables,

    lim_{tau} sup_S sup_theta E[psi_theta 1{psi_theta > tau}] = 0,

and then wrote that the empirical tail is small "by Markov's inequality since its mean is the
second". That step is wrong. Markov at a fixed `theta` controls `P_N (psi_theta - tau)_+` for that
`theta`; the supremum may select a different `theta` for every sample, and

    E[ sup_theta P_N (psi_theta - tau)_+ ]  >=  sup_theta E[ P_N (psi_theta - tau)_+ ],

so the quantity the uniform-integrability statement controls is the *smaller* one. Interchanging
the supremum with the expectation is exactly the work a uniform law has to do, and it was assumed
rather than done.

**Why the obvious repair does not work.** Take the envelope `Psi_S = sup_theta psi_theta`, so that
`sup_theta (psi_theta - tau)_+ = (Psi_S - tau)_+` and Markov applies to a single variable. But
`Psi_S` is not uniformly integrable in `S`: it is `S^{2/K}` times the squared covering radius of the
atom cloud over the parameter set, and a covering radius carries a logarithmic factor that a
nearest-neighbour distance does not, so `Psi_S` grows like `(log S)^{2/K}` even at a well-placed
centre, with distant centres contributing a further `S^{2/K} ||DeltaY_n||^2`.

**Action.** The proposition now carries the empirical-tail condition as an explicit unverified
hypothesis, and is labelled conditional. `cor:argmax_consistent` inherits that label, since its
proof invokes the uniform law directly. `Remark A.6` states the gap, why the envelope route fails,
and what a working argument would need: a covering estimate for the nearest-neighbour geometry
combined with the distant-centre truncation already used in the interchange proposition, with the
truncation level allowed to grow like `log S`. Strengthening the moment assumptions instead was
considered and rejected: at `K = 4` that would move the boundary `K sigma^2 > 2` the appendix exists
to study.

The theorem may well be true. The numerics and the structure both support it. It is not proved.

## Overclaims corrected

**The proxy criterion is not the simulated score.** `prop:score_at_truth` and `prop:curvature`
concern `X_N`, the scaled nearest-atom proxy, not the simulated log likelihood. The nearest-atom
sandwich relates the two through their *values*, uniformly in `theta`, and a uniform bound on values
does not bound derivatives. Both propositions are retitled, the surrounding prose says "nearest-atom
proxy criterion" throughout, and the claim that this is the object Brandt and Santa-Clara's Lemma 4
concerns is removed: their Lemma 4 is a log-likelihood approximation, not a nearest-neighbour score.

**`cor:score_contradiction` assumed its denominator away.** `prop:score_moment` is a second moment
for the derivative of a density summand. The log-likelihood score is `grad qhat / qhat`, and the
corollary carried the numerator's variance across the ratio without controlling the lower tail of
the denominator or its dependence on the numerator. That is the move from `L^2` behaviour to
convergence in probability that this paper elsewhere insists on scrutinising — and the collapse
theorem is itself an example of an estimator with mean `p` at every `n` that converges in
probability to zero, so its second moment is a poor guide to its lower tail. The corollary is now
labelled conditional, and `Remark 6.x` records why the denominator is not a formality here.
`S h^{(K+2)/2} -> infinity` is stated as a mean-square stability condition suggested by the
calculation, not as a proved necessary condition.

**The abstract claimed a dichotomy that the paper's own results refute.** It said collapse holds
throughout the subcritical region "and the central limit theorem throughout its complement". But
`prop:critical_limit` exhibits `R_{M,S}` of constant order with a nondegenerate non-Gaussian limit,
so the boundary is a third regime. Corrected to: collapse for `R -> 0`, density CLT for
`R -> infinity`, with `R ≍ 1` a separate case.

**The claim taxonomy contradicted itself.** Section 1.2 said all proved results concern the
transition density and none concerns the maximiser, while the preceding "Proved" list included the
argmax consistency corollary. With that corollary demoted the sentence is again accurate, and both
it and the uniform law now appear under "Conditional".

## Proof repairs

- **Poisson-series differentiation.** The claim that termwise differentiation is legitimate
  "whenever the `a_j` grow at most geometrically" is now backed by a bound. Since the nearest atom
  is no farther than the first, `g_S(m) <= S^{2/K}(m^2 + K sigma^2)`, so integrating against
  `chi^2_{K+2j}` gives `a_j <= S^{2/K}(K + 2j + K sigma^2)`: linear in `j`, so the series and all
  its derivatives converge absolutely.
- **Quantifier in the `a_j` transfer.** The convergence is stated and used for every *fixed* `j`.
  No uniformity in `j` is claimed, and none is needed, since only `j = 0, 1` enter the curvature.
- **Critical-limit continuous mapping.** Vague convergence controls compactly supported test
  functions, and `e^{-t}` is not compactly supported, so the functional is not vaguely continuous as
  asserted. Repaired by truncating at `R`, applying the continuous mapping theorem to the truncated
  functional, and bounding both remainders in mean by `e^{-R}`.

## What the referee confirmed

Worth recording, since the previous round flagged these as the least-scrutinised material:
`prop:curvature` passes, including the absence of a stray factor of two; the `a_j -> a_j` transfer
passes for each fixed `j`; and `prop:nn_interchange` appears sound. The density-level results — the
exact Brownian moments, the subcritical collapse, the triangular-array CLT, the general local moment
law, the variance and CLT scaling, and the MSE balance — were all assessed as sound, as was the
substance of the critique of Lemmas 2 and 3.

So the damage is confined to the estimator-level appendix and one corollary in Section 6, which is
where the previous round predicted the risk was concentrated.

## Verification

Both documents build with zero errors, zero overfull and underfull boxes and no undefined references
or citations: 63 and 26 pages. All generated artefacts reproduce bit-for-bit. No forbidden phrase
appears in any searched file.
