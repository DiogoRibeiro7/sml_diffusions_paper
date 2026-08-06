# Change log, the split into two documents

Baseline `c8540d1`. No mathematical content was added, removed or altered in this round. The single
manuscript was divided into two, on the recommendation of all three referee reports, and the
supporting machinery was generalised to build and gate both.

## What moved

The manuscript was 75 pages, of which roughly a third analysed the four-dimensional exchange-rate
specification of Brandt and Santa-Clara (2002) rather than the estimator. That material is now a
separate document.

**Theory paper**, `paper/main.tex`, 50 pages. Sections 1–7 unchanged. Section 8 is the
finite-sample scaling diagnostics for the implemented design, promoted from the former subsection
8.2 and given a short framing paragraph of its own. Sections 9–11 (numerics, remedies, conclusion)
are unchanged except that the numerics section lost its final subsection. Appendix A is the argmax
question, Appendix B reproducibility.

**Companion note**, `paper/companion.tex`, 26 pages, titled *Mathematical Status of the
Exchange-Rate Application in Brandt and Santa-Clara (2002)*. It takes the former Section 8.1
summary of findings, the former Section 9.5 boundary figure, and the former Appendices B–G, which
become its Sections 3–8: square-root coefficients and the generic assumptions, the reality of the
simulated incompleteness state, invertibility of the volatility map, feasibility of the Brownian
correlation matrix, the minimum-incompleteness selection rule, and constrained inference. It has its
own title, abstract, keywords and a scope section stating the relation to the theory paper.

## Why the boundary falls where it does

The two documents answer different questions. The theory paper asks what the endpoint estimator does
as `M` and `S` grow, and its answers are limit theorems that hold whatever specification the
estimator is applied to. The companion asks what can be established about one published
specification, and its answers are algebraic propositions and numerical diagnostics; several are
negative, establishing that no problem arises where one might have been suspected. Mixing the two
made the negative results read as hedges on the positive ones, which they are not.

One diagnostic stayed with the theory paper. The implemented design is the concrete point at which
the effective size `R_{M,S}` can be evaluated, and the arithmetic of refining `M` and `S` together
is the clearest practical statement of what the dimensional law implies, so it belongs to the
argument about the estimator rather than to the assessment of the model.

## Edits made to preserve accuracy

Splitting a document silently breaks every claim that spans the cut. The following were repaired:

- Eleven dangling cross-references in the theory paper, and two in the companion, each converted to
  a textual reference rather than deleted, so no claim lost its support.
- The theory paper's abstract, contribution list, claim taxonomy and roadmap, which each enumerated
  the application findings.
- Two long recapitulations in the theory paper — the sixth item of the overview and the
  application paragraph of the conclusion — compressed to a summary and a pointer. Both had
  restated the companion's findings in full.
- The claim taxonomy now records that the companion uses two further categories the theory paper
  does not need: statements reported by the original authors, and implementation details their
  published description does not settle.
- The companion's scope section states the relation explicitly: the dependence runs one way, the
  companion cites the theory paper by result number, and nothing in the theory paper depends on it.

## Machinery

- `Makefile`: `pdf` now depends on the new `theory` and `companion` targets; `clean` covers both.
- `code/make_release.py`: `DOCUMENTS` drives the log-cleanliness, draft-label and placeholder-metadata
  gates over both sources and both logs, and `dist/companion.pdf` joins the artefacts.
- `code/check_forbidden_phrases.py`: `paper/companion.tex` added to the searched set, so the
  54 retracted-wording patterns are enforced on both documents.
- `tests/test_analytics.py`: the CIR negativity table check reads `companion.tex`, where that table
  now lives.
- `README.md`, `.zenodo.json`, `CITATION.cff`: describe two documents in one deposit record.

## Verification

Both documents build with zero errors, zero overfull and underfull boxes and no undefined references
or citations: 50 and 26 pages. 250 tests pass. 33 of 33 generated artefacts reproduce bit-for-bit.
No forbidden phrase appears in any of the six searched files. Neither document contains an
unreferenced figure or table.
