"""Assemble the release artefacts under ``dist/``.

Runs the final checks, then writes ``dist/main.pdf``, ``dist/source.zip``,
``dist/reproducibility.zip``, ``dist/change_log.md`` and
``dist/mathematical_claims_matrix.md``.

The release build is refused if any check fails.  Nothing here contacts
authors, editors, repositories or any external service.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PAPER = ROOT / "paper"

SOURCE_MEMBERS = [
    "paper/main.tex",
    "paper/references.bib",
    "Makefile",
    "README.md",
    "requirements.txt",
]

REPRODUCIBILITY_DIRS = ["code", "tests", "docs", "notes"]


@dataclass(frozen=True)
class Check:
    """One release gate."""

    name: str
    command: list[str]


CHECKS = [
    Check("test suite", [sys.executable, "-m", "pytest", "tests", "-q"]),
    Check("reproducibility", [sys.executable, "code/verify_reproducibility.py"]),
]


def run_checks(skip: bool) -> None:
    """Run every release gate, or explain that they were skipped."""
    if skip:
        print("WARNING: checks skipped at the caller's request; not a release build")
        return
    for check in CHECKS:
        print(f"running {check.name} ...", flush=True)
        result = subprocess.run(check.command, cwd=ROOT)
        if result.returncode != 0:
            raise SystemExit(f"release refused: {check.name} failed")


def check_log_is_clean() -> list[str]:
    """Return any LaTeX log conditions that should block a release."""
    log = PAPER / "main.log"
    if not log.exists():
        return ["paper/main.log is missing; run `make pdf` first"]
    text = log.read_text(encoding="utf-8", errors="replace")
    problems = []
    for needle, message in (
        ("Overfull", "overfull box"),
        ("Underfull", "underfull box"),
        ("undefined", "undefined reference or citation"),
        ("Token not allowed", "hyperref bookmark warning"),
    ):
        count = text.lower().count(needle.lower())
        if count:
            problems.append(f"{count} x {message}")
    return problems


def check_no_draft_labels() -> list[str]:
    """Return a problem if the draft label would appear in the release PDF."""
    source = (PAPER / "main.tex").read_text(encoding="utf-8")
    active = [
        line
        for line in source.splitlines()
        if line.strip().startswith("\\newcommand{\\draftmode}")
    ]
    return ["\\draftmode is still defined, so the draft label will be printed"] if active else []


# Front-matter fields that must carry real values before a release.
METADATA_COMMANDS = ("authorname", "affiliation", "email", "orcid")
PLACEHOLDER_MARKER = "to be supplied"


def check_metadata_resolved() -> list[str]:
    """Return a problem for every front-matter field still holding a placeholder.

    A release build must not go out carrying "[affiliation to be supplied]".
    This is deliberately build-blocking: the fields are the author's to fill in,
    and inventing them would be worse than failing.
    """
    source = (PAPER / "main.tex").read_text(encoding="utf-8")
    problems = []
    for field in METADATA_COMMANDS:
        for line in source.splitlines():
            stripped = line.strip()
            if stripped.startswith(f"\\newcommand{{\\{field}}}"):
                if PLACEHOLDER_MARKER in stripped:
                    problems.append(f"front-matter field \\{field} is still a placeholder")
                break
        else:
            problems.append(f"front-matter field \\{field} is not defined")
    return problems


def write_zip(target: Path, members: list[Path]) -> None:
    """Write a zip archive containing ``members``, stored by repo-relative path."""
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for member in sorted(members):
            archive.write(member, member.relative_to(ROOT).as_posix())


def collect(directory: str) -> list[Path]:
    """Return every tracked-looking file under ``directory``."""
    base = ROOT / directory
    if not base.exists():
        return []
    return [
        path
        for path in base.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    ]


def main() -> int:
    """Build the release artefacts."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="assemble artefacts without running the gates (not a release build)",
    )
    parser.add_argument(
        "--allow-draft",
        action="store_true",
        help="permit a build that still carries the draft label or placeholder metadata",
    )
    args = parser.parse_args()

    run_checks(args.skip_checks)

    problems = check_log_is_clean()
    if not args.allow_draft:
        problems += check_no_draft_labels()
        problems += check_metadata_resolved()
    if problems:
        for problem in problems:
            print(f"  blocking: {problem}")
        if not args.allow_draft:
            raise SystemExit("release refused: see blocking conditions above")
        print("continuing anyway because --allow-draft was given")

    DIST.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PAPER / "main.pdf", DIST / "main.pdf")

    source_members = [ROOT / m for m in SOURCE_MEMBERS]
    source_members += collect("paper/figures")
    source_members += collect("paper/tables")
    write_zip(DIST / "source.zip", [m for m in source_members if m.exists()])

    repro_members: list[Path] = []
    for directory in REPRODUCIBILITY_DIRS:
        repro_members += collect(directory)
    repro_members += [ROOT / "Makefile", ROOT / "requirements.txt", ROOT / "README.md"]
    write_zip(DIST / "reproducibility.zip", [m for m in repro_members if m.exists()])

    for artefact in ("main.pdf", "source.zip", "reproducibility.zip"):
        size = (DIST / artefact).stat().st_size
        print(f"  wrote dist/{artefact} ({size:,} bytes)")
    print("  dist/change_log.md and dist/mathematical_claims_matrix.md are maintained by hand")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
