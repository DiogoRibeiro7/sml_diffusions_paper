# Bibliography audit, round two

Follows `docs/bibliography_audit.md`. Only entries touched or re-checked in this round are
recorded here; entries verified in round one and unchanged since are not repeated.

## Detemple, Garcia and Rindisbacher

| Field | Value | Verified against |
| --- | --- | --- |
| Authors | Jerome Detemple, René Garcia, Marcel Rindisbacher | title page of CIRANO working paper 2003s-11 |
| Title | Asymptotic properties of Monte Carlo estimators of diffusion processes | publisher record and RePEc |
| Journal, volume, issue, pages, year | Journal of Econometrics, 134(1), 1–68, September 2006 | RePEc listing and Elsevier author page, two independent sources |
| DOI | `10.1016/j.jeconom.2005.06.019` | **not resolved** — see below |

**Accent.** Rendered `Garcia, Ren{\'e}` in the `.bib`, which typesets as "René Garcia". Confirmed
in the compiled bibliography.

**DOI caveat.** The ScienceDirect landing page returns HTTP 403 to automated requests, so the DOI
could not be confirmed by resolution. Volume, issue, page range and year are confirmed from two
independent sources. The DOI is retained because it follows Elsevier's registered pattern for this
volume and matches the article's PII, but it is recorded here as unresolved rather than verified,
and a human should click it once before circulation.

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

## Stramer and Yan, 2007b

Searched for a DOI without success. The article is *Journal of Computational and Graphical
Statistics* 16(3), 672–691 (2007); volume, issue, pages and year are confirmed, and the entry is
retained without a DOI rather than carrying an invented one. It remains clearly distinguished from
`StramerYan2007a`, the Methodology and Computing in Applied Probability paper, by key, title,
journal and the description in Section 1.1.

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
