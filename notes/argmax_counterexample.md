# Investigation: is there a direct counterexample to argmax consistency?

**Decision: no-go.** No complete proof was obtained that the endpoint simulated-likelihood
maximiser fails. The manuscript therefore retains the narrower claim — that Lemma 2 of Brandt and
Santa-Clara is directly refuted and that the proofs of Theorems 1 and 2 consequently fail — and
does not assert that the argmax estimator is inconsistent.

Two by-products of the investigation *are* rigorous and are worth keeping: an exact reduction of
the simulated criterion under common random numbers, and a uniform sandwich bound that identifies
which objective governs the maximiser. Both are recorded in Appendix E of the manuscript. A third
result, the limiting shape of that objective, is derived heuristically and verified numerically
but not proved; it is reported here only.

## 1. Setup

Take the location family

$$ dY_t = \theta\,dt + dW_t, \qquad Y_t \in \mathbb{R}^K, $$

observed at unit intervals $t = 0, 1, \dots, N$. This is the most favourable possible setting for
the published theory:

- the Euler scheme is **exact** at every $M$, so there is no discretisation bias at all and
  Lemma 1 of Brandt and Santa-Clara holds with zero error;
- the drift and diffusion coefficients are $C^\infty$ with bounded derivatives of all orders and
  $\Sigma\Sigma^{\mathsf T} = I_K$, so Assumptions 1 and 2 hold exactly;
- the exact transition density is Gaussian and the exact MLE is available in closed form,
  $\hat\theta_N = \frac1N\sum_n \Delta Y_n$, the mean increment.

Any failure here is attributable to the endpoint Monte Carlo construction alone.

## 2. The common-random-number reduction (proved)

Common random numbers across $\theta$ are not optional: the published implementation requires
them so that the objective is smooth in $\theta$ and can be handed to a gradient-based optimiser.
Fix the standard normal innovations $\xi_{n,s}$ once, independently of $\theta$.

Because the Euler recursion is exact and linear, the preterminal state after $M-1$ steps is

$$ Z_{n,s}(\theta) = Y_n + \theta(1-h) + \sqrt{1-h}\,\xi_{n,s}, $$

and the endpoint summand is

$$
G_{n,s}(\theta)
= \phi\!\left(Y_{n+1};\, Z_{n,s}(\theta) + \theta h,\, hI\right)
= \phi\!\left(u_n(\theta) - \sqrt{1-h}\,\xi_{n,s};\, 0,\, hI\right),
$$

where $u_n(\theta) = \Delta Y_n - \theta$ is the centred increment. The drift enters *only*
through $u_n(\theta)$.

**Lemma A.** Under common random numbers, the simulated transition density for observation $n$ is
exactly a Gaussian kernel density estimate with bandwidth $\sqrt h$,

$$ \hat q_{M,S}(Y_{n+1}\mid Y_n;\theta) = \frac1S\sum_{s=1}^S \phi_h\!\left(u_n(\theta) - a_{n,s}\right), \qquad a_{n,s} = \sqrt{1-h}\,\xi_{n,s}, $$

built from a sample that does not depend on $\theta$ and evaluated at the $\theta$-dependent point
$u_n(\theta)$.

This is an identity, not an approximation. It makes the whole picture concrete: the simulated log
likelihood is a sum of logs of fixed random KDEs, and $\theta$ only slides the evaluation point.
The collapse theorem of the manuscript is, in this language, the elementary statement that a KDE
with $S$ atoms and bandwidth $\sqrt h$ is useless when $S h^{K/2} \to 0$.

## 3. Which objective governs the maximiser (proved)

Write $b_{n,s} = \Delta Y_n - \sqrt{1-h}\,\xi_{n,s}$ for the atoms translated into $\theta$-space,
so $u_n(\theta) - a_{n,s} = b_{n,s} - \theta$, and let

$$ D_N(\theta) = \sum_{n} \min_{s\le S}\ \lVert \theta - b_{n,s}\rVert^2 . $$

**Lemma B.** For every $\theta$,

$$ 0 \;\le\; 2h\log\hat{\mathcal L}_{N,M,S}(\theta) + D_N(\theta) + Nh\,K\log(2\pi h) \;\le\; 2Nh\log S . $$

*Proof.* For each $n$ factor the minimising atom out of the sum:

$$ \frac1S\sum_s e^{-\lVert\theta-b_{n,s}\rVert^2/(2h)} = e^{-\min_s\lVert\theta-b_{n,s}\rVert^2/(2h)}\cdot\frac1S\sum_s e^{-(\lVert\theta-b_{n,s}\rVert^2-\min_s\lVert\theta-b_{n,s}\rVert^2)/(2h)} . $$

Every exponent in the second factor is non-positive and at least one equals zero, so that factor
lies in $[1/S, 1]$. Take logarithms, multiply by $2h$, and sum over $n$. $\square$

The bound is **uniform in $\theta$** and the slack is $2Nh\log S$, whereas the objective itself is
of order $D_N$. Along the collapse path $M = S = n$ the slack per observation is
$2(\log n)/n \to 0$. Hence the maximiser of the simulated likelihood is governed by the
**nearest-atom objective** $D_N$, not by anything resembling the exact log likelihood.

This is already a substantive statement. The exact log likelihood in this model is
$-\frac12\sum_n\lVert\theta - \Delta Y_n\rVert^2$, a smooth quadratic whose minimiser is the
sample mean. The simulated criterion is instead a nearest-neighbour objective over $NS$ atoms.
The two have no reason to share a maximiser, and this is the precise sense in which the endpoint
construction changes the estimation problem rather than approximating it.

## 4. The limiting shape (heuristic, verified numerically, not proved)

Conditionally on the data innovation $\eta_n = \Delta Y_n - \theta_0$, the atoms
$b_{n,s} = \theta_0 + \eta_n - \sqrt{1-h}\,\xi_{n,s}$ are iid Gaussian with mean
$\theta_0 + \eta_n$. Standard nearest-neighbour asymptotics give, for $S$ iid draws from a density
$f$ in $\mathbb{R}^K$,

$$ \mathbb{E}\left[\min_{s\le S}\lVert v - W_s\rVert^2\right] \;\asymp\; c_K\,\bigl(S f(v)\bigr)^{-2/K} . $$

Applying this conditionally with $f = \phi_{I}$ centred at $\eta$, then averaging over
$\eta \sim N(0, I)$, and writing $v = \theta - \theta_0$:

$$ \frac{1}{N}D_N(\theta) \;\approx\; c_K S^{-2/K}\,(2\pi)\;\mathbb{E}_\eta\!\left[e^{\lVert v-\eta\rVert^2/K}\right] . $$

The Gaussian moment generating function of a noncentral chi-square gives, for $t < 1/2$,
$\mathbb{E}[e^{t\lVert v-\eta\rVert^2}] = (1-2t)^{-K/2}e^{t\lVert v\rVert^2/(1-2t)}$. At $t = 1/K$
this is finite **if and only if $K > 2$**, and equals

$$ \ell(v) \;\propto\; \exp\!\left(\frac{\lVert v\rVert^2}{K-2}\right). $$

The closed form was checked against Monte Carlo for $K \in \{3,4,6\}$ and
$\lVert v\rVert \in \{0, 0.5, 1\}$; agreement to three digits (`code/argmax_counterexample.py`,
`limiting_shape`).

Two consequences, if the heuristic is correct:

1. $\ell$ is strictly increasing in $\lVert v\rVert$ and uniquely minimised at $v = 0$, so the
   simulated argmax is **consistent** for $\theta_0$. There is no counterexample to consistency
   in this model.
2. $\ell$ is not the exact log-likelihood shape. The simulated estimator is a different
   M-estimator, converging at a rate governed by $S^{2/K}$ rather than at the parametric rate.
   So $\sqrt N(\hat\theta_{N,M,S} - \hat\theta_N)$ should **not** vanish, which is what Lemma 5
   and Theorem 1 of Brandt and Santa-Clara require.

The recurrence of the threshold $K > 2$ — the same condition as the density collapse theorem — is
notable. Below it the relevant expectation diverges and the argument says nothing.

## 5. Numerical evidence

`python code/argmax_counterexample.py`, seed 20260728, $K = 4$, $\theta_0 = 0$, eight restarts per
fit. Restart objective spreads were small relative to the objective value, so the reported
maximisers are not local-optimisation artefacts.

**Fixed simulation design $M = S = 32$, $N$ growing.**

| $N$ | $\lVert\hat\theta_N-\theta_0\rVert$ | $\lVert\hat\theta_{N,M,S}-\theta_0\rVert$ | gap | $\sqrt N\,\cdot$ gap | restart spread |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 200 | 0.1777 | 0.2685 | 0.1010 | 1.428 | 0.0000 |
| 400 | 0.1070 | 0.1543 | 0.2109 | 4.218 | 0.0000 |
| 800 | 0.1119 | 0.1657 | 0.1078 | 3.050 | 0.0000 |
| 1600 | 0.0524 | 0.0966 | 0.0637 | 2.548 | 0.0000 |
| 3200 | 0.0162 | 0.0391 | 0.0395 | 2.233 | 0.0000 |

**Collapse path $M = S$, $N$ growing.**

| $N$ | $M=S$ | $S/M^{2}$ | $\lVert\hat\theta_N-\theta_0\rVert$ | $\lVert\hat\theta_{N,M,S}-\theta_0\rVert$ | $\sqrt N\,\cdot$ gap | restart spread |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 200 | 8 | 0.125 | 0.1220 | 0.0934 | 1.642 | 0.0000 |
| 400 | 16 | 0.0625 | 0.1436 | 0.2010 | 1.417 | 0.0000 |
| 800 | 32 | 0.0312 | 0.0751 | 0.0660 | 2.202 | 0.0000 |
| 1600 | 64 | 0.0156 | 0.0256 | 0.0710 | 3.138 | 0.0000 |

The restart spread is identically zero to four decimals in every design: all eight restarts
reached the same objective value. At these sizes the criterion is effectively unimodal, so the
reported maximisers are genuine and not artefacts of derivative-free local search.

The pattern matches section 4. The simulated estimator's own error falls from 0.2685 to 0.0391 as
$N$ grows sixteenfold, so it is consistent; but it stays roughly $2.4$ times the exact MLE error
throughout and falls more slowly. The scaled gap
$\sqrt N\lVert\hat\theta_{N,M,S} - \hat\theta_N\rVert$ fluctuates between $1.4$ and $4.2$ with no
downward trend, whereas Lemma 5 and Theorem 2 of Brandt and Santa-Clara together require it to
vanish.

This is **evidence, not proof**, and it is weak evidence in one specific respect. A single seed
per design makes the scaled gap noisy — the non-monotonicity in the tables is sampling
variability, not structure — so the correct reading is "does not visibly converge to zero", not
"diverges". No uniformity in $\theta$ has been established, the dimension is fixed at $K = 4$, and
the designs reachable by simulation are nowhere near the regime $N^4 \ll S \ll M^2$ in which the
published theorem actually operates.

## 6. Approaches tried and why each fails

| Approach | Why it fails |
| --- | --- |
| Transfer the density collapse directly to the argmax | The collapse in the manuscript's Theorem 3.3 fixes $x = y = 0$. An argmax argument needs simultaneous control over $N$ observed pairs and over a neighbourhood of $\theta_0$; the collapse regions for different observations need not align, and nothing forces them to sit near $\theta_0$. |
| Argue from non-uniform integrability | The criterion is a sum of logs. Failure of uniform integrability of the density estimator says nothing about the location of the maximiser of its logarithm, which is unbounded below and therefore repelled from collapse regions rather than attracted to them. |
| Take $S$ fixed and $N \to \infty$ | Gives a clean limit criterion and a clean non-equivalence result, but $S$ fixed violates the hypotheses of the theorems under discussion, which require $S \to \infty$. Not a counterexample to anything claimed. |
| Prove the nearest-neighbour limit rigorously | Requires a uniform-in-$\theta$ nearest-neighbour law for a triangular array whose atoms are exchangeable rather than independent (they share $\eta_n$), with $S$ growing. Standard results (e.g. Evans-type nearest-neighbour asymptotics) are pointwise and assume iid sampling from a fixed density. Bridging that gap is the main obstacle, and it was not closed. |
| Show the criterion is asymptotically flat | It is not. Lemma B shows the criterion has curvature of order $1/h$ in the nearest-atom metric. The problem is that the curvature is in the wrong geometry, not that it vanishes. |
| Find multimodality that traps the optimiser | Restart experiments found the criterion to be effectively unimodal at the sizes tested; restart optima agreed to within a small fraction of the objective. Multimodality may appear at larger $S$, but no controlled statement was obtained. |

## 7. What a complete counterexample would require

Any of the following would suffice, and none is currently available:

1. A rigorous uniform-in-$\theta$ limit for $N^{-1}S^{2/K}D_N(\theta)$ along an admissible
   $(M_n, S_n)$, with an argmax-continuity argument. This is the most promising route: sections 2
   and 3 are already proved, and only section 4 is missing.
2. A parametric family and admissible sequence for which the limit criterion is maximised away
   from $\theta_0$. The symmetry of the location model works against this; a model in which the
   atom density is asymmetric in $\theta$ would be a better candidate.
3. A demonstration that $\sqrt N(\hat\theta_{N,M,S} - \hat\theta_N) \not\to 0$ in probability
   along a sequence satisfying both $\sqrt S/M \to 0$ and $N/S^{1/4} \to 0$. Note the difficulty:
   those two conditions together force $N^4 \ll S \ll M^2$, so the designs in which the published
   theorem operates are extraordinarily simulation-rich, and the numerical study above does not
   reach them.

Point 3 deserves emphasis. The published conditions are so demanding that a counterexample must
be constructed in a regime that cannot be simulated. This is a reason the question is hard, and
also a reason it may be of limited practical interest compared with the density-level result,
which bites at implementable designs.
