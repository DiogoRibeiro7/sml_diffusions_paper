"""Check that numbers typed into manuscript tables come from generated data.

The reproducibility gate compares generated artefacts with their committed
copies, so it can only see numbers that pass through ``generate_results``.  A
number typed straight into a LaTeX table is invisible to it.  That is not
hypothetical: the ``curvature / V`` column of the criterion-shape table was
computed in a scratch script, never added to the generator, and sat outside the
gate for a full release.  Those values happened to be correct; nothing in the
repository would have said so if they had not been.

This scans the tabular environments of both manuscripts, extracts the numeric
literals, and requires each to be the correct rounding of some value in some
generated CSV.  Matching is numeric rather than textual: a literal with ``d``
decimals matches a generated value ``v`` when ``|v - q| <= 0.5 * 10^-d``, so
rounding in either direction is accepted while a wrong digit is not.

Tables whose numbers are quoted from the literature or reported by the original
authors are exempt by caption, each with a stated reason, so that adding an
exemption is a deliberate act rather than a silent one.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
TABLES = PAPER / "tables"

DOCUMENTS = ("main.tex", "companion.tex")

TABLE_BLOCK = re.compile(r"\\begin\{tabular\}(.*?)\\end\{tabular\}", re.S)
NUMBER = re.compile(r"(?<![\w.])(-?\d+(?:\.\d+)?(?:e-?\d+)?)(?![\w.])")
# Scientific notation is written A\times10^{B}; the mantissa alone would not
# match the full value, so the two parts are joined before extraction.
SCIENTIFIC = re.compile(r"(-?\d+(?:\.\d+)?)\s*\\times\s*10\^\{(-?\d+)\}")
BARE_POWER = re.compile(r"10\^\{-?\d+\}")
# Superscripts and subscripts carry exponents and indices, never data values.
SCRIPTS = re.compile(r"[\^_]\{[^{}]*\}|[\^_]-?\w")

# Structural values: dimensions, small counts, exponents, design sizes.  These
# describe the experiment rather than report a result.
STRUCTURAL = {
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 20, 24, 25, 50, 81, 100, 128,
    150, 200, 256, 500, 520, 544, 625, 1000, 1040, 1296, 2000, 4000, 5000,
    8000, 10000, 20000,
}

# Reason required for every exemption.
EXEMPT = {
    "Relation to existing asymptotic analyses": "rates translated from cited papers",
    "estimates of Table 3": "parameter values reported by the original authors",
    "Reported estimates": "parameter values reported by the original authors",
    "Algebraic-domain diagnostic": "grid counts recorded in the CSV as metadata",
    "Worst-case one-step Euler": "step sizes and probabilities from the boundary CSV",
}


def generated_values() -> list[float]:
    """Every numeric value appearing in any generated CSV."""
    values: list[float] = []
    for path in sorted(TABLES.glob("*.csv")):
        with path.open(encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                for cell in row.values():
                    if cell is None:
                        continue
                    try:
                        values.append(float(cell.strip()))
                    except (ValueError, AttributeError):
                        continue
    # Percentages are quoted as such in several captions.
    values.extend(value * 100 for value in list(values))
    return values


def matches(quoted: str, values: list[float]) -> bool:
    """Is ``quoted`` the correct rounding of some generated value?"""
    try:
        target = float(quoted)
    except ValueError:
        return True
    # The rounding precision is that of the mantissa, scaled by any exponent:
    # 1.427e-2 is quoted to three decimals of the mantissa, so it stands for
    # anything within 5e-4 * 1e-2, not within 5e-7.
    mantissa, _, exponent = quoted.partition("e")
    decimals = len(mantissa.split(".")[1]) if "." in mantissa else 0
    scale = 10 ** int(exponent) if exponent else 1
    tolerance = 0.5 * 10 ** (-decimals) * scale * 1.000001
    return any(abs(value - target) <= tolerance for value in values)


def scan() -> list[tuple[str, str, str]]:
    """Return (document, caption fragment, literal) for each unexplained number."""
    values = generated_values()
    problems: list[tuple[str, str, str]] = []

    for name in DOCUMENTS:
        path = PAPER / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")

        for block in TABLE_BLOCK.finditer(text):
            before = text[: block.start()]
            start = before.rfind("\\caption{")
            caption = before[start : start + 120] if start >= 0 else ""
            if any(key in caption for key in EXEMPT):
                continue

            body = block.group(1)
            # Thousands separators are written {,} and would split a literal.
            body = body.replace("{,}", "").replace("\\,", "")
            body = SCIENTIFIC.sub(lambda m: f"{m.group(1)}e{m.group(2)}", body)
            # A bare power of ten, 10^{-2}, is an exponent and not a result.
            body = BARE_POWER.sub(" ", body)
            # Superscripts and subscripts carry exponents and indices, never
            # data: S^{-4/5} and R_{M,S} must not contribute -4, 5 or 2.
            body = SCRIPTS.sub(" ", body)
            # Drop macro arguments, which carry lengths and column widths.
            body = re.sub(r"\\[a-zA-Z]+\{[^{}]*\}", " ", body)

            for match in NUMBER.finditer(body):
                literal = match.group(1)
                if float(literal) in STRUCTURAL:
                    continue
                if matches(literal, values):
                    continue
                problems.append((name, caption[9:70], literal))

    return problems


def main() -> int:
    problems = scan()
    tables = sum(
        len(TABLE_BLOCK.findall((PAPER / name).read_text(encoding="utf-8")))
        for name in DOCUMENTS
        if (PAPER / name).exists()
    )
    if problems:
        for document, caption, literal in problems:
            print(f"  {document}: {literal} is not the rounding of any generated value")
            print(f"      table: {caption.strip()}")
        print(f"\n{len(problems)} unexplained number(s) across {tables} tables")
        return 1
    print(f"every number in {tables} manuscript tables traces to generated data")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
