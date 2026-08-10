# Change log, the verification round

Baseline `7cb7a31`, the state released as v1.8.0. This round closed the last open condition in the
estimator-level result, and then spent its remaining effort on the machinery that checks the
manuscript rather than on the manuscript itself. That was not the plan; it was forced by what the
machinery found once it was pointed at prose.

## 1. The empirical tail, closed in every dimension

**Was.** `prop:uniform_lln_all` held outright only where the envelope is square integrable, which
needs `K sigma^2 > 4`. Below that the release recorded an obstruction and argued it was structural:
truncating the criterion reintroduces a threshold growing like a power of `S`, so the observation
count would have to satisfy `N >> S^c`, contradicting the published `N / S^{1/4} -> 0`. The stated
conclusion was that any repair "needs a route that doesn't go through the envelope at all".

**It did.** The obstruction is real for truncation on the *criterion* and disappears for truncation
on the *centre*. Split the observations by where `theta_0` sits relative to the cloud rather than by
how large the criterion is. The far region then needs only a *first* moment of the envelope, which
exists throughout `K sigma^2 > 2`; and because the far region bounds a single random variable rather
than a supremum over `theta`, Markov applies with no interchange of supremum and expectation — the
error an earlier round had made and quarantined. The near region has a square-integrable envelope by
the covering bound. The Gaussian tail of the centre means the splitting radius need only grow like
`sqrt(log log S)`.

**Now.** The condition is polylogarithmic, `N >> (log S)^p` with

    p = 1 + 4/K + 16/(K (K sigma^2 - 2)),

which is `4` at `K = 4`. `cor:argmax_consistent` is therefore unconditional in every dimension
`K > 2`, the application's four included. For `K >= 5` the envelope route still gives the smaller
exponent `1 + 4/K`; only the exponent differs.

**Caveat, recorded in `rem:window`.** A polylogarithm eventually loses to any power, so the two rate
conditions are compatible and admissible sequences exist. But the window opens near `S = 1e29` at
`K = 4` and `S = 1e14` at `K = 6`. This is the third statement in that appendix true in the limit and
unreachable in practice, and the remark names the pattern rather than leaving it implicit.

## 2. Five macros a shell heredoc had eaten

**Was.** Five occurrences of `\neval` in the antithetic section were a literal newline followed by
`eval`, from a shell heredoc that collapsed the backslash. This shipped in a release.

**Why nothing caught it.** LaTeX reads `$ eval$` as math-mode italic. The build had zero errors, zero
warnings and zero undefined references, and the typeset page read "The *eval* density evaluations" in
five sentences. Every check in this repository reads either the LaTeX log or the generated numbers,
and this defect touches neither.

**Now.** Repaired, and gated: `check_forbidden_phrases.scan_mangled_macros` fails on a stray control
character and on any macro eaten by its own escape. `test_escape_mangled_macros_are_detected` builds
its fixtures from `chr(92)` and `chr(10)`, because writing them as escape sequences is the hazard
under test and would collapse the intact case and the damaged one into one string.

## 3. Every prose number now has a generator

**Was.** The number gate read tabular environments only. A prose scan was added with 28 existing
numbers frozen in a baseline as technical debt.

**Now.** The baseline is empty. Paying it down was worth more than the bookkeeping suggested, because
deriving each value in order to generate it turned up four defects:

| Quantity | Printed | Correct |
| --- | --- | --- |
| Antithetic correlation, `K = 4`, `r = 0.5` | `+0.063` | `+0.064` (exactly `0.06360`) |
| Antithetic correlation, `K = 4`, `r = 1.5` | `-0.012` | `-0.013` (exactly `-0.01259`) |
| Critical limit median | `0.89` | correct, but no generator existed |
| Critical limit `P(L < 1/2)` | `0.28` | correct, but no generator existed |

All four had passed the gate by landing within rounding distance of unrelated quantities in the
exchange-rate tables.

**What that says about the gate.** Matching *something* in the pool is weak evidence. Detection was
also being reported under a flattering error model. Measured paired, over identical draws:

| decimals | arbitrary wrong value | near-miss of a real value |
| --- | --- | --- |
| 2 | 82% | 63% |
| 3 | 97% | 86% |
| 4 | 99.6% | 98% |

Near-misses are what real errors are — a stale value from a scratch run, a transposed digit — and
they land where the pool is densest. Both columns are now measured and asserted by
`test_number_gate_detection_rate`.

Note the trade in the other direction. Generating more numbers strengthens the gate where it matters,
since each quoted value gains a named source; but it enlarges the pool everything else is checked
against, and near-miss detection at two decimals fell from 68 to 63 per cent as the pool grew from
817 values to 931. Only coverage is worth having: a number with a generator behind it is verified, a
number that merely matches the pool is unrefuted.

The blanket percentage variant is genuinely gone. A previous commit said it had been removed and it
had not — the line was still there and the comment claiming otherwise pointed at a name that never
existed. Measured, it cost five points of two-decimal detection and no manuscript number depends on
it.

## 4. Five passages that outlived the result they described

Closing item 1 left five pieces of summarising prose describing the corollary as it stood before.
Two contradicted the paper outright.

| Where | Said | Problem |
| --- | --- | --- |
| The argmax-counterexample discussion | "subject to one unverified condition" | contradicts the exponent paragraph, which states no unverified condition in any `K > 2` |
| The four conclusions about the published paper | "subject to one unverified empirical-tail condition" | same contradiction, in a summary a reader reaches early |
| Status of the appendix ingredients | "the limit of `D_N` is open, and with it the argmax question" | consistency does not go through that limit; only the `sqrt N` question does |
| Closing of the same paragraph | "the manuscript claims only what Section 7 establishes" | true when the appendix had nothing positive to claim; incomplete once it proves consistency |
| Statement of `cor:argmax_consistent` | "for `K >= 5` ... is unconditional" | attaches unconditionality to `K >= 5`, implying the application's `K = 4` is conditional |

The abstract and the proved/conditional inventory were already correct, which is why nothing caught
it: no gate reads for agreement between two sentences in different sections, and none is proposed
here, because no cheap one exists. The honest statement is that this manuscript's weak point is
cross-section consistency of connective prose, and it is checked by reading.

## What remains open

The `sqrt N` statement, unchanged, with its three named ingredients: the rate for `E X_N - G` at
`N^{-1}`; a functional central limit theorem for a criterion that is neither differentiable nor
square integrable; and the sandwich slack, which needs `M >> N S^{2/K} log S`. The paper states this
as open in `rem:rate_numerics` and in the claim inventory.
