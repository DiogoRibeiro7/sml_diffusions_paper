# External review, first round

Seven findings from an independent reader of v1.0.1, all accepted and all fixed. One was
publication-blocking. This is the first review not conducted by the author or by an agent working
for the author, and it found a false statement that five internal rounds had missed.

## 1. Remark E.6 misstated the perfectly correlated case — **publication-blocking**

The remark said that when `|rho_ww*| = 1`, the magnitude condition (76) "degenerates to `0 <= 0` and
carries no information".

That is wrong. With `rho_ww* = sigma` in `{-1, +1}` the right-hand side `1 - rho_ww*^2` is zero, and
because `sigma^2 = 1` the left-hand side is a perfect square:

    rho_wy^2 - 2 sigma rho_wy rho_w*y + rho_w*y^2 = (rho_wy - sigma rho_w*y)^2.

So (76) reads `(rho_wy - sigma rho_w*y)^2 <= 0` and **forces** `rho_w*y = sigma rho_wy`. Far from
carrying no information, it collapses exactly onto the range-compatibility relation of Lemma E.4.

What it does not retain is the separate magnitude restriction. Once compatibility holds the
inequality is satisfied with equality, and the magnitude condition must come from the Moore–Penrose
criterion, where a compatible `d` gives `d' B^+ d = rho_wy^2` and the requirement is
`|rho_wy| <= 1`.

The remark is rewritten to say this. Lemma E.4 and Proposition E.5 were sound and are untouched.
Two tests added: one sweeping `sigma`, `rho_wy` and `rho_w*y` and asserting that (76) holds exactly
when compatibility does, and one confirming the pseudoinverse quadratic form equals `rho_wy^2`.

## 2. Two antithetic overstatements

**"The theory of Section 4 applies directly under the substitution `S -> P`."** Lemma 8.3 preserves
the `h^{-K/2}` second-moment and variance order and nothing else. Replaced with a statement that the
lemma preserves the dimensional consistency scale `P/M^{K/2}`, plus a new remark listing what it does
not give: the exact local variance constant, the third centred-moment constant, the pair-level
Lyapunov condition, and the triangular-array CLT.

**"The second design has half the effective size of the first."** Only `R_pair` halves mechanically.
Replaced with the independent-pair diagnostic, noting that the variance-equivalent size may change by
a different factor because `rho_A` may change with `M`.

The reviewer also supplied a sharper asymptotic observation, now **Proposition 8.4**. Since
`G+, G- >= 0`, we have `E[G+ G-] >= 0`, so

    Cov(G+, G-) >= -E[G]^2,

and dividing by a variance of order `h^{-K/2}` gives `rho_A >= -O(h^{K/2})`, hence
`liminf rho_A >= 0`. Antithetic pairing therefore cannot improve the leading rare-event variance
constant asymptotically, though it can still help at fixed `h` and favourable endpoints — the value
`rho_A = -0.479` reported for `K = 1` is a real finite-sample gain. This strengthens the section
rather than weakening it, and is a better result than what it replaces.

## 3. Appendix F called every optimum a vertex

The sentence "Proposition F.1 proves that the optimum is a vertex of whichever feasible set the
optimiser used" contradicted the three-set distinction established a page earlier. Proposition F.1
Part A proves a **boundary point** of an arbitrary compact scalar set; it is a vertex only when the
set is polyhedral, as `C_pub` is. Corrected, and the following sentence now says "nonnegativity
boundary" rather than "face" outside `C_pub`.

## 4. Appendix H identified the criterion too literally

The text said "the object being maximised is a nearest-neighbour functional of `NS` atoms rather than
a smooth quadratic". The simulated criterion is a smooth log-sum-exp; Proposition H.2 proves only
that after scaling and adding a constant it lies uniformly within `2Nh log S` of a nearest-atom
criterion. Corrected, which matters because the next paragraph insists the proposition does not
compare maximisers.

## 5. Appendix B retained a categorical probability

"A violation probability of `10^-2667` per step is not a phenomenon any simulation will encounter."
Tiny is not impossible, and the figure holds only at the displayed benchmark state. Replaced with
"at the displayed benchmark states ... numerically negligible for any realistically sized
simulation".

## 6. The binary64 underflow threshold was described inaccurately

Table 5's caption said direct evaluation returns zero "below roughly `10^-308`". That is the smallest
**normal** value; binary64 continues through subnormals to about `5e-324`, and whether a particular
routine underflows earlier depends on its algorithm.

Measured rather than assumed: the routine used here returns exactly zero at about `6e-311`, inside
the subnormal range. The caption now gives the representation limit, the normal limit and this
implementation's actual threshold, and states that the flag reports the routine's behaviour rather
than a property of the mathematics. A test asserts the measured threshold lies strictly between the
smallest subnormal and the smallest normal value.

## 7. Theorem 4.7 used an unproved convergence

The proof wrote `q_{M_n}(y|x) -> p(y|x)` and used it to bound the mean term, but the convergence was
never stated or proved. The reviewer's second suggestion is the economical one: the theorem needs only
`q_M = O(1)`, since it centres at `q_M` rather than at `p`.

New **Lemma 4.6** proves exactly that, with an explicit constant:

    sup_{0<h<=1/2} q_M(y|x) <= r_bar (4 v_bar / v_low)^{K/2} + C_K r_bar v_low^{-K/2} mu_bar^K.

The proof substitutes `u = y - z`, bounds the density factor by `r_bar` from (A4) and the Gaussian by
ellipticity from (A2), then splits at `|u| = 2 mu_bar h`; the outer part integrates to a constant free
of `h` and the inner part is `O(h^{K/2})`. A remark records that only boundedness is used, that
convergence also holds by the approximate-identity argument at `r = 1`, and that Corollary 4.9 is
where the first-order expansion is separately assumed. Verified numerically on an
Ornstein–Uhlenbeck process: `q_M` stays near `0.49`–`0.52` across `M` from 4 to 4096 and approaches
`p(y|x) = 0.516`.

This was a proof-completeness issue, not a challenge to the theorem.

## On presentation

The reviewer confirms the PDF renders cleanly, figures are readable, Figure 5 now states the correct
monotonic direction, and the affiliation is consistent. The suggestion that Appendices B–G might move
to an online supplement is recorded as an editorial decision for after external review, not acted on
here.

## Verification

| Check | Result |
| --- | --- |
| Test suite | 229 passing, up from 222 |
| Artefacts | 33/33 bit-exact |
| LaTeX | 0 errors, 0 undefined references, 0 overfull or underfull boxes |
| Pages | 62 |
| Forbidden phrases | 0 hits, 47 patterns |
| Release gate | passes, no bypass flags |

## Assessment

The blocking finding is the one worth recording. Remark E.6 claimed an inequality was vacuous when it
was in fact equivalent to the compatibility condition the same appendix had just spent two pages
establishing. The error was introduced in the same round that corrected the *original* Proposition
E.2 defect, and it survived the round-four and round-five sweeps because both were driven by lists of
suspect phrasings rather than by re-deriving the algebra. A perfect square with a zero right-hand side
is not a phrase pattern.

Seven forbidden-phrase patterns were added for this round's corrections, which guards recurrence but
not recognition. What would have caught it earlier is what caught it now: an independent reader
checking the algebra rather than the prose.

---

# External review, second pass

Four local corrections on the corrected text, all accepted. No broad rewrite; the reviewer's verdict
is that the central results show no structural defect and the manuscript is ready for independent
mathematical review after these.

## 1. Proposition E.2 needed `|rho_ww*| <= 1` as a hypothesis

The proof rests on `Q_t - (phi - rho_ww* phi*)^2 = phi*^2 (1 - rho_ww*^2) >= 0`, which requires
`|rho_ww*| <= 1`. Without it the proposition is false as a standalone algebraic statement, even
though `rho_ww*` is a correlation in the model and Table 11 records that the published
parameterisation imposes the bound entrywise. Added to the hypotheses, with the remark now explaining
that both side conditions are load-bearing and that neither follows from the variance identity.

A test supplies the counterexample: at `phi = 0.03`, `phi* = 0.02` and `rho_ww* = 1.05`, the quadratic
form is still positive so `v_t > 0` and `v_t^2 >= Q_t` both hold, yet an implied correlation reaches
`1.82`.

## 2. Proposition 8.4's gloss was one-sided in the wrong direction

The proposition proves `liminf rho_A >= 0`, hence that pairing cannot give a negative leading-order
correlation. The explanatory paragraph then said "what it cannot do is change the constant multiplying
`h^{-K/2}` in the limit". Too strong: if `rho_A -> c > 0` the constant is multiplied by `1 + c`, and at
a coincident endpoint `rho_A = 1` doubles it relative to `E` independent evaluations.

Corrected to the one-sided statement the proposition actually supports: pairing cannot *reduce* the
leading constant below the independent-evaluation constant, and may leave it unchanged or raise it.
The theorem statement `N_eff <= E(1 + o(1))` was already consistent with the narrower reading.

## 3. The intermediate-radicand mechanism was misidentified

Appendix C argued that the Euler increments of `v_t` are "conditionally Gaussian and unbounded below"
while positive terms are subtracted. That is not the operative mechanism: the radicand contains
`v_t^2`, so a large negative `v_t` makes it large and positive.

Replaced with the correct point. The update is not constrained to preserve the algebraic domain
`v_t^2 >= Q_t + C_t`; a nondegenerate Gaussian update assigns positive probability to neighbourhoods
in which `|v_t|` is small, while the subtracted terms need not be small there. A sentence now states
that turning this into a violation probability would need the joint conditional covariance of the
whole state update, since `Q_t` and `C_t` move with the other components, and that we stop short of
it. The well-posedness criticism is unaffected.

## 4. Two textual errors

Table 7's worst-case probability is the **final** column, not the third, as the Appendix C discussion
claimed. And "no estimate can move this process away from its boundary" overstates what the Feller
ratio gives: it fixes *attainability* of zero, not typical distance from it. Both corrected, the
second with an explicit sentence separating the two readings.

## Verification

230 tests, 33/33 artefacts bit-exact, 62 pages, zero LaTeX errors or overfull boxes, 51
forbidden-phrase patterns with zero hits, release gate passing.

## Not acted on

The reviewer notes unused space on page 34 where Figure 4 separates from Section 9.5, and suggests
Appendices B–G might become supplementary material for a journal with a length limit. Both are
recorded as editorial decisions for after external review rather than changes to make now.
