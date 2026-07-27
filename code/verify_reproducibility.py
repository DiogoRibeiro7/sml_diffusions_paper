"""Check that committed figures and tables can be regenerated exactly.

The generator writes into a scratch directory and every artefact is compared
with the committed copy under ``paper/``.  Text artefacts (CSV, LaTeX) are
compared field by field with an explicit numerical tolerance; binary artefacts
(PDF, PNG) are compared by SHA-256, which is only meaningful because
``generate_results.save_figure`` suppresses the embedded creation timestamps
that would otherwise differ on every run.

Exit status is 0 when every artefact matches and 1 otherwise.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import generate_results

ROOT = Path(__file__).resolve().parents[1]
COMMITTED = ROOT / "paper"

# Relative tolerance for numerical fields in regenerated CSV tables.  Monte
# Carlo columns are produced from a fixed seed and should agree to the last
# bit, but summation order can differ across BLAS builds, so a small tolerance
# is allowed rather than demanding byte equality.
RELATIVE_TOLERANCE = 1e-9


@dataclass(frozen=True)
class Comparison:
    """Outcome of comparing one regenerated artefact with its committed copy."""

    path: str
    status: str
    detail: str = ""

    @property
    def ok(self) -> bool:
        return self.status == "match"


def sha256(path: Path) -> str:
    """Return the SHA-256 hex digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 16), b""):
            digest.update(block)
    return digest.hexdigest()


def _as_float(value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        return None


def compare_csv(committed: Path, regenerated: Path) -> Comparison:
    """Compare two CSV tables field by field, numerically where possible."""
    name = committed.relative_to(COMMITTED).as_posix()
    with committed.open(newline="", encoding="utf-8") as a, regenerated.open(
        newline="", encoding="utf-8"
    ) as b:
        rows_a = list(csv.reader(a))
        rows_b = list(csv.reader(b))

    if len(rows_a) != len(rows_b):
        return Comparison(name, "shape", f"{len(rows_a)} rows committed, {len(rows_b)} regenerated")

    for index, (row_a, row_b) in enumerate(zip(rows_a, rows_b)):
        if len(row_a) != len(row_b):
            return Comparison(name, "shape", f"row {index} width differs")
        for column, (left, right) in enumerate(zip(row_a, row_b)):
            if left == right:
                continue
            x, y = _as_float(left), _as_float(right)
            if x is None or y is None:
                return Comparison(name, "text", f"row {index} column {column}: {left!r} vs {right!r}")
            scale = max(abs(x), abs(y), 1.0)
            if abs(x - y) / scale > RELATIVE_TOLERANCE:
                return Comparison(
                    name, "numeric", f"row {index} column {column}: {x!r} vs {y!r}"
                )
    return Comparison(name, "match")


def compare_bytes(committed: Path, regenerated: Path) -> Comparison:
    """Compare two artefacts by digest."""
    name = committed.relative_to(COMMITTED).as_posix()
    left, right = sha256(committed), sha256(regenerated)
    if left == right:
        return Comparison(name, "match")
    return Comparison(name, "digest", f"{left[:12]} vs {right[:12]}")


def compare_text(committed: Path, regenerated: Path) -> Comparison:
    """Compare two text artefacts exactly, ignoring line-ending differences."""
    name = committed.relative_to(COMMITTED).as_posix()
    left = committed.read_text(encoding="utf-8").replace("\r\n", "\n")
    right = regenerated.read_text(encoding="utf-8").replace("\r\n", "\n")
    if left == right:
        return Comparison(name, "match")
    return Comparison(name, "text", "content differs")


def verify(keep: Path | None = None) -> list[Comparison]:
    """Regenerate every artefact into a scratch directory and compare."""
    scratch = Path(tempfile.mkdtemp(prefix="sml-verify-"))
    try:
        generate_results.main(scratch)
        results: list[Comparison] = []
        for subdir in ("figures", "tables"):
            committed_dir = COMMITTED / subdir
            for committed_file in sorted(committed_dir.iterdir()):
                if not committed_file.is_file():
                    continue
                regenerated_file = scratch / subdir / committed_file.name
                if not regenerated_file.exists():
                    results.append(
                        Comparison(
                            committed_file.relative_to(COMMITTED).as_posix(),
                            "missing",
                            "not produced by the generator",
                        )
                    )
                    continue
                suffix = committed_file.suffix.lower()
                if suffix == ".csv":
                    results.append(compare_csv(committed_file, regenerated_file))
                elif suffix in {".pdf", ".png"}:
                    results.append(compare_bytes(committed_file, regenerated_file))
                else:
                    results.append(compare_text(committed_file, regenerated_file))
        if keep is not None:
            if keep.exists():
                shutil.rmtree(keep)
            shutil.copytree(scratch, keep)
        return results
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--keep",
        type=Path,
        default=None,
        help="copy the regenerated artefacts to this directory for inspection",
    )
    args = parser.parse_args()

    results = verify(args.keep)
    failures = [result for result in results if not result.ok]

    for result in results:
        mark = "ok  " if result.ok else "FAIL"
        suffix = f"  ({result.status}: {result.detail})" if not result.ok else ""
        print(f"{mark} {result.path}{suffix}")

    print()
    print(f"{len(results) - len(failures)}/{len(results)} artefacts reproduce exactly")
    if failures:
        print(f"{len(failures)} artefact(s) did not reproduce", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
