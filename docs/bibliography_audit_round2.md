# Bibliography audit, round two

Follows `docs/bibliography_audit.md`. Only entries touched or re-checked in this round are
recorded here; entries verified in round one and unchanged since are not repeated.

## Detemple, Garcia and Rindisbacher

| Field | Value | Verified against |
| --- | --- | --- |
| Authors | Jerome Detemple, René Garcia, Marcel Rindisbacher | title page of CIRANO working paper 2003s-11 |
| Title | Asymptotic properties of Monte Carlo estimators of diffusion processes | publisher record and RePEc |
| Journal, volume, issue, pages, year | Journal of Econometrics, 134(1), 1–68, September 2006 | RePEc listing and Elsevier author page, two independent sources |
| DOI | `10.1016/j.jeconom.2005.06.028` | Crossref registry, title and authors matched |

**Accent.** Rendered `Garcia, Ren{\'e}` in the `.bib`, which typesets as "René Garcia". Confirmed
in the compiled bibliography.

**DOI corrected.** The first round recorded `10.1016/j.jeconom.2005.06.019`, inferred from the
volume rather than verified, and flagged it as unresolved. It was wrong. That DOI belongs to
Escanciano and Velasco, "Generalized spectral tests for the martingale difference hypothesis",
*Journal of Econometrics* 134(1), 151-185 - the same volume, a different paper. The correct DOI is
`10.1016/j.jeconom.2005.06.028`, obtained from Crossref, which returns the exact title, all three
authors, volume 134, issue 1 and pages 1-68.

Because one guessed DOI turned out to be wrong, every DOI in the bibliography was then checked
individually against Crossref by comparing the registered title with the title in the `.bib`. The
script is `doicheck` in the scratch directory; the result is 24 of 24 matching, no mismatches. Four
entries carry no DOI: Hall and Heyde (1980), a 1980 monograph for which Crossref registers only
chapter-level identifiers; Pedersen (1995a) and Miasojedow et al. (2016), whose journals appear not
to register them; and formerly Stramer and Yan (2007b), whose DOI was located in the course of this
check and added.

**Full text.** Read in the openly available CIRANO working-paper version 2003s-11 (67 pages,
April 2003). All quotations in `docs/detemple_overlap_audit.md` are from that version with page
numbers given; the published version is paywalled and was not consulted. The working paper and the
published article carry the same title and abstract.

## Milstein, Schoenmakers and Spokoiny — added

| Field | Value | Verified against |
| --- | --- | --- |
| Authors | Grigori N. Milstein, John G. M. Schoenmakers, Vladimir Spokoiny | Project Euclid record |
| Title | Transition density estimation for stochastic differential equations via forward-reverse representations | Project Euclid record |
| Journal, volume, issue, pages, year | Bernoulli, 10(2), 281–312, 2004 | Project Euclid record |
| DOI | `10.3150/bj/1082380220` | Project Euclid |

Added because Detemple et al. attribute the kernel interpretation of the simulated transition
density to it, so it is the primary source for a claim the manuscript previously left
unattributed. Note the spelling: Detemple et al. cite it as "Milshtein ... (2001)", referring to
the working-paper version; the published surname is Milstein and the year is 2004.

## Stramer and Yan, both 2007 papers

**2007b, DOI found and added.** `10.1198/106186007x237306`, located through a Crossref
bibliographic query and verified by title, volume 16 and pages 672–691. The first round searched
without success and left the entry without one.

**2007a, record confirmed and full text read.** *Methodology and Computing in Applied
Probability* 9(4), 483-496, DOI `10.1007/s11009-006-9006-2`, all confirmed against Crossref. The
published article was supplied by the author after automated retrieval failed; Springer redirects
to an authorisation endpoint and Semantic Scholar reports the abstract as elided. Every reference
in the bibliography has now been read in full.

Its contents bear on the novelty claims and are treated in Section 1.1. In summary: Theorem 1
concerns the modified Brownian bridge sampler, proves its importance-weight variance is bounded
uniformly in `M`, gives the optimal allocation `N ~ M^2`, and holds "regardless of the dimension
d". About the endpoint sampler it records three qualitative observations, all of which are now
disclaimed as prior work in Section 1.1: that its importance-weight variance may be unbounded;
that "a limiting quantity for G_M does not exist and, therefore, even a huge number N can give
poor approximations"; and that numerically its error "increases as M increases" at fixed `N`. It
also states the kernel connection for the endpoint estimator specifically, with the evaluation
points taken at time `Delta - h`.

The two papers remain clearly distinguished by key, title, journal, DOI and their descriptions in
Section 1.1.

## Re-verified without change

`Pedersen1995a`, `Pedersen1995b`, `BallyTalay1996a`, `BallyTalay1996b`, `Nicolau2002`,
`MiasojedowEtAl2016`, `Lindstrom2012`. The Pedersen 1995b DOI corrected in round one
(`10.3150/bj/1193667818`) resolves to the Project Euclid record. The Lindström page range
corrected in round one (615–623) matches the Springer record. `Lindstr{\"o}m` and
`Miasojedow, B{\l}a{\.z}ej` typeset correctly.

## Build state

27 entries, all cited, no citation without an entry, no biber warnings.

## Front matter

PDF metadata is now set through `hyperset` from the same commands that typeset the title block,
so the document properties cannot drift from the visible front matter: `pdftitle`, `pdfauthor`,
`pdfsubject` and `pdfkeywords`.

`code/make_release.py` gained a build-blocking check. A release build fails if any of
`\authorname`, `\affiliation`, `\email` or `\orcid` still contains the marker "to be supplied", or
if any of them is undefined.

All four are now supplied by the author and the gate passes:

| Field | Value |
| --- | --- |
| `\authorname` | Diogo Ribeiro |
| `\affiliation` | ESMAD – IPP |
| `\email` | `dfr@esmad.ipp.pt`, linked as `mailto:` |
| `\orcid` | 0009-0001-2022-7072, linked to `https://orcid.org/0009-0001-2022-7072` |

The ORCID iD passes the ISO 7064 MOD 11-2 checksum used for ORCID identifiers, which is a
structural check only and not confirmation that the record belongs to the named author. The
affiliation is recorded exactly as supplied, without expanding the acronym.
