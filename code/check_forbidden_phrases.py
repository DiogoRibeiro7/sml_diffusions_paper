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
    "paper/companion.tex",
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
    Forbidden(
        r"boundary is never approached",
        "unattainable is not unapproachable; claims hold at the displayed states only",
    ),
    Forbidden(
        r"five free correlations",
        "four entries of R_t are free; rho_zz* is primitive but enters C_t, not R_t",
    ),
    Forbidden(
        r"\\Cref\{prop:min_incomplete\} (shows|proves) that the boundary is[^.]*attained exactly",
        "exact binding is proved only for the constant case under its conditions",
    ),
    Forbidden(
        r"no bound in the useful direction",
        "a union bound always exists; it is merely trivial at these probabilities",
    ),
    Forbidden(
        r"model[- ]feasible (state|reference state)",
        "use algebraically feasible: the grid establishes no dynamic accessibility",
    ),
    Forbidden(
        r"the calibrated model (can )?reach",
        "algebraic feasibility is not dynamic accessibility",
    ),
    Forbidden(
        r"rises (very slightly )?tow(a|)rds \$?\\Phi\(-1\)",
        "the worst case DECREASES to Phi(-1) from above as h is refined",
    ),
    Forbidden(
        r"without lowering (its|the) peak",
        "refinement does lower the peak, towards the positive limit Phi(-1)",
    ),
    Forbidden(
        r"halves the effective endpoint size",
        "only R_pair = P/M^2 halves mechanically; R_var depends on rho_A",
    ),
    Forbidden(
        r"maximiser is (thus )?governed by a nearest",
        "Proposition H.2 is a uniform comparison, not a statement about maximisers",
    ),
    Forbidden(
        # Asserting form only: the manuscript records the withdrawal in words
        # that necessarily quote the retracted claim.
        r"therefore negligible relative to \$?D_N",
        "the relative order of the slack against D_N is unproved",
    ),
    Forbidden(
        r"no admissible sequence exists",
        "admissible sequences abound; none is also density-consistent in K >= 4",
    ),
    Forbidden(
        r"Three entries of \$R_t\$ are free",
        "four entries of R_t are free, including rho_ww*",
    ),
    Forbidden(
        r"binding constraints imply nonregular inference",
        "nonregularity is possible, not demonstrated; the interior argument is incomplete",
    ),
    Forbidden(
        r"interest-rate states are far from the boundary",
        "unattainable is not unapproachable; claims hold at displayed states only",
    ),
    Forbidden(
        r"All but the last of these underflow",
        "several rows do not underflow; Table 5 records it state by state",
    ),
    Forbidden(
        r"cannot be excluded by strengthening the hypotheses",
        "it is excluded by a rate condition; only regularity assumptions cannot fix it",
    ),
    Forbidden(
        r"specifications are unproblematic",
        "a finite grid does not establish global validity",
    ),
    Forbidden(
        r"degenerates to \$?0\\le0\$? and carries no information",
        "at |rho_ww*|=1 the condition forces compatibility; it is not vacuous",
    ),
    Forbidden(
        r"applies directly under the substitution \$?S\\mapsto P",
        "the lemma preserves the scale only; it does not carry the CLT across",
    ),
    Forbidden(
        r"half the effective size of the first",
        "only the independent-pair diagnostic halves; R_var may not",
    ),
    Forbidden(
        r"optimum is a vertex of whichever feasible set",
        "boundary point in general; vertex only for the polyhedral C_pub",
    ),
    Forbidden(
        r"object being maximised is a nearest-neighbour functional",
        "the simulated criterion is a smooth log-sum-exp, only approximated by one",
    ),
    Forbidden(
        r"not a phenomenon any simulation will encounter",
        "negligible at the displayed states, not impossible",
    ),
    Forbidden(
        r"returns exactly zero, which happens below roughly \$?10\^\{-308\}",
        "binary64 reaches 5e-324 via subnormals; this routine underflows near 6e-311",
    ),
    Forbidden(
        r"cannot do is change the constant multiplying",
        "pairing cannot REDUCE the leading constant; it may raise it when rho_A > 0",
    ),
    Forbidden(
        r"conditionally Gaussian and unbounded below",
        "the radicand holds v^2, so large negative v helps; the issue is support near zero",
    ),
    Forbidden(
        r"no estimate can move this process away from its boundary",
        "the Feller ratio fixes attainability, not typical distance from zero",
    ),
    Forbidden(
        r"its third column is strictly decreasing",
        "the worst-case probability is the final column of that table",
    ),
    Forbidden(
        r"either no positive root or exactly two positive roots",
        "inconsistent unless multiplicity is counted; state the three cases",
    ),
    Forbidden(
        r"inverse map is globally single valued",
        "single valued on states with zeta_t > 0, the proposition's hypothesis",
    ),
    Forbidden(
        r"in any of the three specifications",
        "the sweep covers models A, B and C across two currency systems",
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


# ---------------------------------------------------------------------------
# Macros destroyed by shell escape interpretation.
#
# Editing the manuscripts through a shell heredoc has repeatedly replaced a
# backslash escape with the character it denotes: `\neval` became a literal
# newline followed by `eval`, `\beta` a backspace followed by `eta`.  LaTeX
# accepts the wreckage without complaint -- it reads `$ eval$` as math-mode
# italic -- so the build stays clean, no reference goes undefined, and the
# damage reaches the typeset page.  Five occurrences in one paragraph survived
# a release that way.  Nothing else in the repository looks for this, because
# every other check reads either the log or the numbers.
# ---------------------------------------------------------------------------

TEX_FILES = ("paper/main.tex", "paper/companion.tex")

# The escapes a shell or Python string literal would interpret, mapped to the
# character that replaces them.  A macro whose name begins with one of these
# letters is at risk; `\a` is omitted only because no macro here starts with it.
ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "b": "\x08", "f": "\x0c", "v": "\x0b"}

MACRO_DEFINITION = re.compile(
    r"\\(?:newcommand\*?|DeclareMathOperator\*?|def)\s*\{?\\([a-zA-Z]+)"
)


def mangled_in_text(text: str) -> list[tuple[int, str]]:
    """Return every (line number, description) where an escape ate a macro."""
    hits: list[tuple[int, str]] = []

    # Any control character other than a newline is damage on its own.
    for index, character in enumerate(text):
        if character in set(ESCAPES.values()) - {"\n"}:
            line = text.count("\n", 0, index) + 1
            letter = next(k for k, v in ESCAPES.items() if v == character)
            hits.append((line, f"control character for the escape \\{letter}"))

    # A newline standing in for a macro that begins with one.
    for macro in sorted(set(MACRO_DEFINITION.findall(text))):
        replacement = ESCAPES.get(macro[0])
        if replacement is None:
            continue
        for match in re.finditer(
            re.escape(replacement) + re.escape(macro[1:]) + r"(?![a-zA-Z])", text
        ):
            line = text.count("\n", 0, match.start()) + 1
            hits.append((line, f"macro {macro} eaten by its own escape"))
    return hits


def scan_mangled_macros() -> list[tuple[str, int, str]]:
    """Return every (file, line number, description) where a macro was eaten."""
    hits: list[tuple[str, int, str]] = []
    for relative in TEX_FILES:
        path = ROOT / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        hits.extend(
            (relative, line, description)
            for line, description in mangled_in_text(text)
        )
    return hits


def main() -> int:
    """Report any reappearance of a retracted phrase, or any eaten macro."""
    hits = scan()
    for relative, number, text, reason in hits:
        print(f"  {relative}:{number}: {text!r}")
        print(f"      {reason}")
    mangled = scan_mangled_macros()
    for relative, number, description in mangled:
        print(f"  {relative}:{number}: {description}")
        print("      a shell escape replaced the backslash; LaTeX will not complain")
    if hits or mangled:
        print(
            f"\n{len(hits)} forbidden phrase(s) and {len(mangled)} mangled macro(s) found"
        )
        return 1
    print(f"no forbidden phrases in {len(SEARCHED)} files, {len(FORBIDDEN)} patterns")
    print(f"no escape-mangled macros in {len(TEX_FILES)} manuscripts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
