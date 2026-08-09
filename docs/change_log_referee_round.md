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

## Second pass, after the referee round

A self-directed pass over the same material, looking for the error classes the
referee had just demonstrated I make. It found four more, all mine.

**An orphaned paragraph.** The rewrite that demoted the uniform law left a "three
things stand between prop:uniform_lln and that conclusion" paragraph stranded
outside the remark that had closed above it, duplicating the replacement text and
citing the uniform law as proved. Removed and its substance folded in, now as
four things: the empirical-tail condition is prior to the other three.

**Three stale claims** that consistency is settled, surviving the demotion,
including one inside the remark on why the sandwich cannot deliver the rate.

**The contribution list** still asserted `S/M^3 -> infinity` as a necessary
condition and called a density-derivative second moment a "score" moment. That is
the same conflation the referee caught in Section 6, one section earlier, and
neither of us had noticed it there.

**Hand-typed table numbers.** The criterion-shape table's curvature column and
three columns of the design table were computed in scratch scripts and typed into
LaTeX. Every value was correct, and the generators now reproduce them, but they
sat outside the reproducibility gate.

### A gate for the blind spot

The reproducibility check compares generated artefacts with committed copies, so
it only sees numbers that pass through the generator. A number typed into a table
is invisible to it. That is the same blind spot that let an RNG-mismatched score
table through earlier.

`code/check_table_numbers.py` now extracts every numeral from every tabular
environment in both manuscripts and requires each to be the correct rounding of
some value in some generated CSV, matching numerically with a tolerance set by
the quoted precision. It is wired into `make check` and the release gate.

Making it honest took five iterations, and each was the guard being wrong rather
than the manuscript: thousands separators split `10{,}000` into `000`; scientific
notation compared a mantissa against a full value; the tolerance ignored the
exponent, holding `1.427e-2` to `5e-7` instead of `5e-6`; bare `10^{-2}` powers
were read as data; and symbolic superscripts such as `S^{-4/5}` contributed `-4`.

It reports every number in 18 tables as traceable. That result was verified not to
be vacuous by planting a wrong digit in a generated value, confirming the guard
fails, and restoring it. A gate that passes because it inspects nothing is worse
than no gate, and this repository now has four whose failure mode is silence.

## Third pass: closing the two open threads

Both threads left open after the referee round are now addressed, one completely
and one only above four dimensions.

### The step-size quantifier: closed

`lem:sigma_uniform`. The interchange, and with it the coefficients of the
curvature identity, converge uniformly over `sigma^2` in a compact `[sigma_0^2, 1]`
whenever `K sigma_0^2 > 2`. Only two features of `sigma^2` enter those proofs:
the Gaussian tail constants of the distant-centre estimate, and the integrability
of the dominating function, `E exp(m^2/(K sigma^2)) = (1 - 2/(K sigma^2))^{-K/2}`.
Both are continuous on a compact interval bounded away from `2/K`, hence bounded
there. Since `sigma_n^2 = 1 - h_n -> 1` and `2/K < 1` for `K > 2`, a fixed
`sigma_0^2` in `(2/K, 1)` contains the tail of any admissible sequence.

### The empirical tail: closed for `K >= 5`, open at `K = 4`

`lem:covering` bounds the envelope. Covering the parameter set by balls of radius
`r/2` and applying a union bound over the grid gives

    P(sup_theta rho_S > r | DeltaY) <= (1 + 2D/r)^K exp(-S f_min omega_K (r/2)^K),

whence `E[Psi_S^2 | DeltaY] <= C ((1 + log S)/f_min)^{4/K}`. Averaging over the
centre needs `E[f_min^{-4/K}] < infinity`, and since
`f_min >= c exp(-(||DeltaY - theta*|| + D)^2 / (2 sigma^2))` that holds exactly
when `2/(K sigma^2) < 1/2`, that is when `K sigma^2 > 4`.

In that range the envelope is square integrable, the bracketing maximal
inequality applies to the whole class with no truncation, and
`prop:uniform_lln_high` gives the uniform law unconditionally under
`N >> (log S)^{1 + 4/K}`. The consistency corollary is therefore unconditional
for `K >= 5`.

**It is not unconditional at `K = 4`.** Since `sigma^2 = 1 - h < 1`, the quantity
`K sigma^2` is strictly below 4 there. The envelope has infinite second moment,
truncation reintroduces a threshold growing like a power of `S`, and the
resulting rate condition is `N >> S^c` for some positive `c` — which conflicts
with the published `N / S^{1/4} -> 0`. The obvious repair does not merely fail;
it fails in the direction that would make the result useless for the dimension
the application uses. That is why the empirical-tail hypothesis is retained
rather than replaced.

### The covering measurement, and two errors in making it

The extra logarithm matters, so it was measured: at `K = 4` the covering radius
divided by `S^{-1/K}` rises monotonically by `1.084` across two decades, against
`1.136` for a full logarithmic correction, while the radius divided by
`((log S)/S)^{1/K}` is flat to within five per cent.

Two mistakes were made getting there. The first measurement used 60,000 probes,
so at the largest `S` the probe spacing approached the covering radius itself and
the supremum was under-resolved, biasing the result against the very trend being
measured; the probe count is now 400,000 and the resolution ratio is recorded in
the table. The second used three replications and produced a non-monotone column;
it is now eight.

And the numbers first written into the manuscript came from a scratch run rather
than the pipeline, differing in the third digit. That is the same error the
table-number gate was built to catch — but these numbers appear in prose rather
than in a tabular environment, and the gate reads only tables. The limitation is
worth stating: the gate narrows the blind spot, it does not remove it.
