# Bibliography audit

Every entry in `paper/references.bib` was checked against primary bibliographic sources:
publisher pages, DOI records and journal tables of contents. Secondary summaries were not used
as the basis for any correction.

The build is free of biber warnings, every cited key resolves, and every entry is cited at least
once.

## Entries changed

### Pedersen (1995b) — DOI corrected

The prompt flagged this DOI as suspect, and it was wrong.

| | |
| --- | --- |
| Old | `10.2307/3318487` |
| New | `10.3150/bj/1193667818` |
| Source | Project Euclid record for *Bernoulli* 1(3), 257–279 |

`10.2307/…` is a JSTOR stable identifier. The publisher DOI issued by Project Euclid is the
canonical one and is now used. Volume, issue, pages and year were confirmed correct.

### Bally and Talay — the wrong pair was cited for density results

The manuscript cited `BallyTalay1995` and `BallyTalay1996` for Euler *density* expansions and
for Gaussian upper bounds on Euler densities. The 1995 entry is a different paper.

| Key | Reference | Content |
| --- | --- | --- |
| `BallyTalay1995` (**removed**) | *Mathematics and Computers in Simulation* 38(1–3), 35–41 | error analysis via Malliavin calculus; a different paper from the two cited, and no longer referenced, so the entry was dropped rather than left uncited |
| `BallyTalay1996a` (**added**) | *Probability Theory and Related Fields* 104(1), 43–60, DOI `10.1007/BF01303802` | Part I, convergence rate of the **distribution function** |
| `BallyTalay1996b` (**renamed** from `BallyTalay1996`) | *Monte Carlo Methods and Applications* 2(2), 93–128 | Part II, convergence rate of the **density** |

Citations in the manuscript now point to Parts I and II, which are the results actually used.
The Gaussian upper bound on Euler densities is attributed specifically to Part II.

### Stramer and Yan — two distinct 2007 papers were conflated

This is the most consequential correction, because it bears on the novelty claim. Stramer and
Yan published two papers in 2007 and only one of them is a numerical comparison.

| Key | Reference | Content |
| --- | --- | --- |
| `StramerYan2007a` (**added**) | *Methodology and Computing in Applied Probability* 9(4), 483–496, DOI `10.1007/s11009-006-9006-2` | **asymptotics**: trade-off between Euler discretisation error and Monte Carlo error, efficient allocation of computing effort, for the modified Brownian bridge importance sampler |
| `StramerYan2007b` (**renamed** from `StramerYan2007`) | *Journal of Computational and Graphical Statistics* 16(3), 672–691 | numerical comparison of simulated likelihood with a closed-form approximation |

The manuscript previously cited only the numerical paper and used it to support the claim that
prior work on the endpoint estimator was "qualitative and largely numerical". That
characterisation was wrong, because the asymptotic paper exists. Section 1.1 now attributes the
bias–variance trade-off and the optimal-allocation idea to prior work and restricts the novelty
claim accordingly.

Note the estimator studied differs: `StramerYan2007a` analyses the modified Brownian bridge
sampler, whereas this manuscript analyses the unconditioned endpoint sampler. The manuscript
states that distinction explicitly rather than implying the results are comparable.

### Detemple, Garcia and Rindisbacher — added

| | |
| --- | --- |
| Reference | *Journal of Econometrics* 134(1), 1–68 (2006), DOI `10.1016/j.jeconom.2005.06.019` |
| Title | Asymptotic Properties of Monte Carlo Estimators of Diffusion Processes |
| Source | Elsevier record and RePEc listing |

Required by the revision brief and genuinely relevant: it derives limit distributions for Euler-based
Monte Carlo estimators of diffusions, including expected approximation errors and bias-corrected
estimators. Now cited in Section 1.1 as prior work establishing that a joint analysis of
discretisation and simulation error is possible.

### Lindström (2012) — page range corrected

| | |
| --- | --- |
| Old | 615–622 |
| New | 615–623 |
| Source | Springer record for *Statistics and Computing* 22(2), DOI `10.1007/s11222-011-9255-y` |

## Entries verified without change

| Entry | Checked against |
| --- | --- |
| Aït-Sahalia (2002) | *Econometrica* 70(1), 223–262, DOI `10.1111/1468-0262.00274` |
| Beskos, Papaspiliopoulos, Roberts and Fearnhead (2006) | *JRSS-B* 68(3), 333–382 |
| Beskos, Papaspiliopoulos and Roberts (2009) | *Annals of Statistics* 37(1), 223–245 |
| Brandt and Santa-Clara (2002) | *Journal of Financial Economics* 63(2), 161–210 |
| Cox, Ingersoll and Ross (1985) | *Econometrica* 53(2), 385–407 |
| Delyon and Hu (2006) | *Stochastic Processes and their Applications* 116(11), 1660–1675 |
| Durham and Gallant (2002) | *JBES* 20(3), 297–316 |
| Elerian, Chib and Shephard (2001) | *Econometrica* 69(4), 959–993 |
| Hall and Heyde (1980) | Academic Press monograph |
| Karatzas and Shreve (1991) | Springer, 2nd edition |
| Kloeden and Platen (1992) | Springer |
| Lee (1995) | *Econometric Theory* 11(3), 437–483 |
| Miasojedow, Niemiro, Palczewski and Rejchel (2016) | *Probability and Mathematical Statistics* 36(2), 295–310 |
| Nicolau (2002) | *The Econometrics Journal* 5(1), 91–103 |
| Pedersen (1995a) | *Scandinavian Journal of Statistics* 22(1), 55–71 |
| Schauer, van der Meulen and van Zanten (2017) | *Bernoulli* 23(4A), 2917–2950 |
| Self and Liang (1987) | *JASA* 82(398), 605–610 |
| Sung and Geyer (2007) | *Annals of Statistics* 35(3), 990–1011 |
| van der Meulen and Schauer (2017) | *Electronic Journal of Statistics* 11(1), 2358–2396 |

Author accents were checked: `A{\"i}t-Sahalia`, `Lindstr{\"o}m`, `Miasojedow, B{\l}a{\.z}ej`,
`Garcia, Ren{\'e}`, `Nicolau, Jo{\~a}o`. Journal titles are given in full throughout, and no
entry carries a raw URL where a DOI is available. There are no duplicate entries.

## Limitation

The full text of `StramerYan2007a` is behind a publisher paywall and was not consulted; the
description of its contents in `docs/` and in the manuscript is based on its abstract and
publisher record. The manuscript is written so that nothing depends on the detail of that paper's
results: it states that the estimator analysed there is a different one, and does not assert what
that paper does or does not find about dimension dependence.
