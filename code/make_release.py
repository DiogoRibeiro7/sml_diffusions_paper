"""Assemble the release artefacts under ``dist/``.

Runs the final checks, then writes ``dist/main.pdf``, ``dist/companion.pdf``,
``dist/source.zip``, ``dist/reproducibility.zip``, ``dist/change_log.md`` and
``dist/mathematical_claims_matrix.md``.

The deposit is two documents: the theory paper (``main``) and the application
companion (``companion``).  Every source-level gate below runs over both, so a
placeholder or a retracted phrase in either one blocks the release.

The release build is refused if any check fails.  Nothing here contacts
authors, editors, repositories or any external service.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PAPER = ROOT / "paper"

# The two deposited documents, by base name.  Everything that checks a source
# file or a build log iterates over this.
DOCUMENTS = ("main", "companion")

SOURCE_MEMBERS = [
    "paper/main.tex",
    "paper/companion.tex",
    "paper/references.bib",
    "Makefile",
    "README.md",
    "requirements.txt",
    "LICENSE",
    "CITATION.cff",
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
    """Return any LaTeX log conditions that should block a release, for both documents."""
    problems = []
    for document in DOCUMENTS:
        log = PAPER / f"{document}.log"
        if not log.exists():
            problems.append(f"paper/{document}.log is missing; run `make pdf` first")
            continue
        text = log.read_text(encoding="utf-8", errors="replace")
        for needle, message in (
            ("Overfull", "overfull box"),
            ("Underfull", "underfull box"),
            ("undefined", "undefined reference or citation"),
            ("Token not allowed", "hyperref bookmark warning"),
        ):
            count = text.lower().count(needle.lower())
            if count:
                problems.append(f"{document}: {count} x {message}")
    return problems


def check_no_draft_labels() -> list[str]:
    """Return a problem if the draft label would appear in either release PDF."""
    problems = []
    for document in DOCUMENTS:
        source = (PAPER / f"{document}.tex").read_text(encoding="utf-8")
        if any(
            line.strip().startswith("\\newcommand{\\draftmode}")
            for line in source.splitlines()
        ):
            problems.append(
                f"{document}: \\draftmode is still defined, so the draft label will be printed"
            )
    return problems


# Front-matter fields that must carry real values before a release.
METADATA_COMMANDS = ("authorname", "affiliation", "email", "orcid")
PLACEHOLDER_MARKER = "to be supplied"


def check_forbidden_phrases() -> list[str]:
    """Return a problem for each retracted phrase that has reappeared.

    A release must not reintroduce wording that an earlier review round removed
    as an overstatement.  The patterns live in ``code/check_forbidden_phrases``.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import check_forbidden_phrases as checker

    return [
        f"forbidden phrase {text!r} at {relative}:{number} ({reason})"
        for relative, number, text, reason in checker.scan()
    ]


def check_deposit_metadata() -> list[str]:
    """Return a problem for every archiving file that is missing or unusable.

    Depositing a record openly without a licence leaves it all-rights-reserved by
    default, which contradicts the deposit; and Zenodo requires a licence selection.
    ``CITATION.cff`` and ``.zenodo.json`` are parsed rather than merely counted, so a
    malformed file blocks the release instead of surfacing at the deposit form.
    """
    problems: list[str] = []

    if not (ROOT / "LICENSE").exists():
        problems.append("LICENSE is absent; a deposit needs an explicit licence")

    citation = ROOT / "CITATION.cff"
    if not citation.exists():
        problems.append("CITATION.cff is absent")
    else:
        try:
            import yaml

            loaded = yaml.safe_load(citation.read_text(encoding="utf-8"))
        except ImportError:
            loaded = None
        except Exception as error:  # noqa: BLE001 - report any parse failure verbatim
            problems.append(f"CITATION.cff does not parse: {error}")
            loaded = None
        if isinstance(loaded, dict):
            for field in ("cff-version", "title", "authors", "license"):
                if field not in loaded:
                    problems.append(f"CITATION.cff lacks the {field!r} field")

    zenodo = ROOT / ".zenodo.json"
    if not zenodo.exists():
        problems.append(".zenodo.json is absent")
    else:
        try:
            metadata = json.loads(zenodo.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            problems.append(f".zenodo.json does not parse: {error}")
        else:
            for field in ("title", "upload_type", "creators", "license"):
                if field not in metadata:
                    problems.append(f".zenodo.json lacks the {field!r} field")

    return problems


def check_metadata_resolved() -> list[str]:
    """Return a problem for every front-matter field still holding a placeholder.

    A release build must not go out carrying "[affiliation to be supplied]".
    This is deliberately build-blocking: the fields are the author's to fill in,
    and inventing them would be worse than failing.
    """
    problems = []
    for document in DOCUMENTS:
        source = (PAPER / f"{document}.tex").read_text(encoding="utf-8")
        for field in METADATA_COMMANDS:
            for line in source.splitlines():
                stripped = line.strip()
                if stripped.startswith(f"\\newcommand{{\\{field}}}"):
                    if PLACEHOLDER_MARKER in stripped:
                        problems.append(
                            f"{document}: front-matter field \\{field} is still a placeholder"
                        )
                    break
            else:
                problems.append(f"{document}: front-matter field \\{field} is not defined")
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
    problems += check_deposit_metadata()
    problems += check_forbidden_phrases()
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
    for document in DOCUMENTS:
        shutil.copy2(PAPER / f"{document}.pdf", DIST / f"{document}.pdf")

    source_members = [ROOT / m for m in SOURCE_MEMBERS]
    source_members += collect("paper/figures")
    source_members += collect("paper/tables")
    write_zip(DIST / "source.zip", [m for m in source_members if m.exists()])

    repro_members: list[Path] = []
    for directory in REPRODUCIBILITY_DIRS:
        repro_members += collect(directory)
    repro_members += [
        ROOT / "Makefile",
        ROOT / "requirements.txt",
        ROOT / "README.md",
        ROOT / "LICENSE",
        ROOT / "CITATION.cff",
    ]
    write_zip(DIST / "reproducibility.zip", [m for m in repro_members if m.exists()])

    for artefact in ("main.pdf", "companion.pdf", "source.zip", "reproducibility.zip"):
        size = (DIST / artefact).stat().st_size
        print(f"  wrote dist/{artefact} ({size:,} bytes)")
    hand_written = (
        "change_log.md",
        "change_log_round2.md",
        "change_log_final.md",
        "change_log_split.md",
        "mathematical_claims_matrix.md",
        "literature_novelty_matrix.md",
        "application_feasibility_matrix.md",
        "application_diagnostic_matrix.md",
        "final_claim_dependency_audit.md",
        "final_adversarial_review.md",
        "targeted_final_review.md",
        "final_local_revision_review.md",
        "external_review_round_one.md",
    )
    missing = [name for name in hand_written if not (DIST / name).exists()]
    for name in hand_written:
        if name not in missing:
            print(f"  present dist/{name}")
    if missing:
        print("  MISSING hand-written release documents: " + ", ".join(missing))
        raise SystemExit("release refused: missing release documents")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
