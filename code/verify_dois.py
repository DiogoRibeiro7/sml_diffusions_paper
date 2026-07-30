"""Verify every DOI in references.bib against the Crossref registry.

Compares the title Crossref holds for each DOI with the title in the .bib.
This exists because a DOI inferred from a volume number, rather than looked
up, silently pointed at a different article in the same volume for one entry.
Requires network access, so it is not part of `make check`; run it before a
release or whenever a reference is added.

    python code/verify_dois.py
"""

import json
import pathlib
import re
import time
import urllib.error
import urllib.request

BIB = pathlib.Path("paper/references.bib")
UA = {"User-Agent": "bib-audit/1.0 (mailto:dfr@esmad.ipp.pt)"}


def normalise(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (text or "").lower())


def crossref_title(doi: str) -> str:
    request = urllib.request.Request(f"https://api.crossref.org/works/{doi}", headers=UA)
    with urllib.request.urlopen(request, timeout=25) as response:
        message = json.load(response)["message"]
    return (message.get("title") or [""])[0]


def main() -> None:
    text = BIB.read_text(encoding="utf-8")
    entries = re.findall(r"@\w+\{([^,]+),(.*?)\n\}", text, re.S)
    mismatches = 0
    for key, body in entries:
        doi_match = re.search(r"doi\s*=\s*\{([^}]*)\}", body)
        title_match = re.search(r"title\s*=\s*\{(.*)\}\s*,", body)
        mine = re.sub(r"[{}\\]", "", title_match.group(1)) if title_match else ""
        if not doi_match:
            print(f"{'no DOI':14s} {key}")
            continue
        doi = doi_match.group(1)
        try:
            got = crossref_title(doi)
        except urllib.error.HTTPError as error:
            print(f"{'HTTP ' + str(error.code):14s} {key:28s} {doi}")
            mismatches += 1
            continue
        except Exception as error:  # noqa: BLE001
            print(f"{type(error).__name__:14s} {key:28s} {doi}")
            continue
        a, b = normalise(mine), normalise(got)
        ok = a[:40] in b or b[:40] in a
        print(f"{'MATCH' if ok else '*** MISMATCH':14s} {key:28s} {doi}")
        if not ok:
            mismatches += 1
            print(f"{'':14s} bib      : {mine[:88]}")
            print(f"{'':14s} crossref : {got[:88]}")
        time.sleep(0.25)
    print()
    print(f"{mismatches} problem(s)")


if __name__ == "__main__":
    main()
