"""Fail the build if a corrected overstatement reappears anywhere.

Each entry below is a phrase that was removed during a review round because it
claimed more than the mathematics supports.  The risk this script addresses is
regression: a later edit reintroducing wording that an earlier round retracted,
in a different section, where nobody is looking for it.

Run directly, or through ``make check``; ``code/make_release.py`` blocks a
release on any hit.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Files that carry claims.  Audit documents are excluded because they quote the
# retracted wording on purpose, in order to record what was withdrawn.
SEARCHED = (
    "paper/main.tex",
    "README.md",
    "dist/literature_novelty_matrix.md",
    "dist/application_feasibility_matrix.md",
    "dist/mathematical_claims_matrix.md",
)


@dataclass(frozen=True)
class Forbidden:
    """One retracted phrase, with the reason it may not return."""

    pattern: str
    reason: str


FORBIDDEN = (
    Forbidden(
        r"every individual correlation",
        "Proposition E.1 bounds only the two implied correlations, not all of them",
    ),
    Forbidden(
        r"all correlations are automatically",
        "same overstatement of Proposition E.1",
    ),
    Forbidden(
        r"the entrywise restriction adds nothing",
        "the entrywise restriction is operative on the five free correlations",
    ),
    Forbidden(
        r"the variance identity forces every correlation",
        "the identity constrains the implied correlations only",
    ),
    Forbidden(
        r"logistic restriction is redundant",
        "it is redundant only on the two implied entries",
    ),
    Forbidden(
        r"reachable state space",
        "the grid is an algebraic-domain diagnostic; reachability is not proved",
    ),
    Forbidden(
        r"states the diffusion must traverse",
        "no accessibility or support theorem is available",
    ),
    Forbidden(
        r"fraction of the state space",
        "grid-point counts are not a measure of the state space",
    ),
    Forbidden(
        r"66\s*(%|per cent) of (the )?(swept |reachable )?states",
        "a grid proportion is not a model property; it ranges 58-96% across grids",
    ),
    Forbidden(
        r"probability of an invalid state",
        "the grid supplies no probability",
    ),
    Forbidden(
        r"finer discretisation (does )?reduce[sd]? the time spent",
        "a shrinking region does not imply lower occupation probability",
    ),
    Forbidden(
        r"dangerous region shrinks with \$?h\$?, so",
        "same inference from geometry to occupation time",
    ),
    Forbidden(
        r"perfectly negatively (dependent|correlated)",
        "at a coincident endpoint antithetic partners are identical, correlation +1",
    ),
    Forbidden(
        r"numerically hazardous",
        "no crossing frequency is established for the implemented chain",
    ),
    Forbidden(
        r"the implementation crosses the boundary",
        "not established; the exact result concerns the directly discretised state",
    ),
    Forbidden(
        r"Ren'e Garcia",
        "the accent is mangled; the bib needs Ren{\\'e}",
    ),
    Forbidden(
        r"holds because \$?r_t\$? then lies in the range",
        "range membership does not imply the Moore-Penrose magnitude bound",
    ),
    Forbidden(
        r"\\eqref\{eq:induced_rho_xy\} (alone )?is sufficient",
        "compatibility is necessary but not sufficient; see Proposition E.2(ii)",
    ),
    Forbidden(
        r"deterministic implication about any pair of maximisers",
        "Proposition 6.2's hypotheses are probabilistic",
    ),
    Forbidden(
        r"overstates the independent count by (the factor )?\$?2/\(1\+\\rho_A\)",
        "E overstates the effective count by 1 + rho_A; 2/(1+rho_A) is N_eff/P",
    ),
    Forbidden(
        r"2/\(1\+\\rho_A\)\$?,? (which )?(at a coincident endpoint )?is exactly two",
        "at rho_A = 1 the expression 2/(1+rho_A) equals one, not two",
    ),
    Forbidden(
        # Only the asserting form: the manuscript legitimately denies this.
        r"is the (exact )?effective (simulation )?size of the antithetic",
        "P/M^{K/2} is an independent-pair diagnostic, not an exact variance equivalence",
    ),
)


def scan() -> list[tuple[str, int, str, str]]:
    """Return every (file, line number, matched text, reason) hit."""
    hits: list[tuple[str, int, str, str]] = []
    for relative in SEARCHED:
        path = ROOT / relative
        if not path.exists():
            continue
        for number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            for entry in FORBIDDEN:
                match = re.search(entry.pattern, line, flags=re.IGNORECASE)
                if match:
                    hits.append((relative, number, match.group(0), entry.reason))
    return hits


def main() -> int:
    """Report any reappearance of a retracted phrase."""
    hits = scan()
    for relative, number, text, reason in hits:
        print(f"  {relative}:{number}: {text!r}")
        print(f"      {reason}")
    if hits:
        print(f"\n{len(hits)} forbidden phrase(s) found")
        return 1
    print(f"no forbidden phrases in {len(SEARCHED)} files, {len(FORBIDDEN)} patterns")
    return 0


if __name__ == "__main__":
    sys.exit(main())
