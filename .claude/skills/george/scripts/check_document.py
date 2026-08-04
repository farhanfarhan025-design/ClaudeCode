#!/usr/bin/env python3
"""Pre-delivery verification for TNDK documents.

Reads the text of a finished document and checks it against the house rules that
have hard consequences: the tax prohibition, the payee wording, document
numbering, and the correct signatory. It works on the produced file rather than
the input data on purpose — the failures worth catching are the ones where the
input was right and the document still came out wrong.

    python3 check_document.py --type invoice "Invoice INV-253-2026.pdf"

Exit codes: 0 pass (warnings allowed), 2 one or more FAILs, 1 usage/read error.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import zipfile
from pathlib import Path

DOC_TYPES = ("invoice", "receipt", "delivery-note", "quotation", "lpo", "register")

# Document number series, by type. None = no number expected on the document.
NUMBER_PATTERNS = {
    "invoice": (r"\bINV-\d{3,4}\s*/\s*\d{4}\b", "INV-NNN/YYYY"),
    "receipt": (r"\bRCT-\d{3,4}\s*/\s*\d{4}\b", "RCT-NNN/YYYY"),
    "delivery-note": (r"\bDN-\d{3,4}\s*/\s*\d{4}\b", "DN-NNN/YYYY"),
    "quotation": (r"\bQUT\s*/\s*DCTS\s*/\s*\d{3,4}\s*/\s*\d{4}\b", "QUT/DCTS/NNN/YYYY"),
    "lpo": (r"\bLPO-\d{3,4}\s*/\s*\d{4}\b", "LPO-NNN/YYYY"),
    "register": (None, None),
}

# The exact payee wording. "Equipment and Services", no W.L.L. on this line.
PAYEE_NAME = "The New Doha Kitchen Equipment and Services"
PAYEE_TRIGGER = re.compile(r"cheque\s+should\s+be\s+prepared[^\n]*", re.I)

TAX_WORDS = re.compile(r"\b(tax|taxes|taxable|vat)\b", re.I)
CLIENT_MONEY_DOCS = {"invoice", "receipt", "delivery-note", "register"}

# Money that carries decimals should carry a thousands separator too, so two
# documents never render the same amount differently.
UNSEPARATED_MONEY = re.compile(r"(?<![\d,.])\d{4,}\.\d{2}\b")
AS_OF = re.compile(r"\bas\s+(?:of|at|on)\b", re.I)
BALANCE = re.compile(r"\bbalance\b", re.I)


class Report:
    def __init__(self) -> None:
        self.fails: list[str] = []
        self.warns: list[str] = []
        self.passes: list[str] = []

    def fail(self, msg: str) -> None:
        self.fails.append(msg)

    def warn(self, msg: str) -> None:
        self.warns.append(msg)

    def ok(self, msg: str) -> None:
        self.passes.append(msg)


def extract_text(path: Path) -> str:
    """Best-effort text extraction for pdf / docx / xlsx / plain text."""
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        try:
            out = subprocess.run(
                ["pdftotext", "-layout", str(path), "-"],
                capture_output=True, text=True, check=True,
            )
            return out.stdout
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
        try:
            from pypdf import PdfReader  # type: ignore
        except ImportError:
            raise RuntimeError(
                "cannot read PDF: install poppler-utils (pdftotext) or pypdf"
            )
        return "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)

    if suffix in (".docx", ".xlsx", ".pptx"):
        # Strip tags out of the parts that hold visible text. Avoids a hard
        # dependency on python-docx/openpyxl just to read words back.
        chunks: list[str] = []
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                if not name.endswith(".xml"):
                    continue
                if not any(
                    name.startswith(p)
                    for p in ("word/", "xl/sharedStrings", "xl/worksheets", "ppt/slides/")
                ):
                    continue
                xml = archive.read(name).decode("utf-8", "ignore")
                xml = re.sub(r"</w:p>|</a:p>|<w:br/>", "\n", xml)
                chunks.append(re.sub(r"<[^>]+>", " ", xml))
        return "\n".join(chunks)

    return path.read_text(encoding="utf-8", errors="ignore")


def check(text: str, doc_type: str) -> Report:
    report = Report()
    squashed = re.sub(r"[ \t ]+", " ", text)

    # 1. The tax prohibition — absolute on anything client-facing that carries money.
    hits = {m.group(0).lower() for m in TAX_WORDS.finditer(squashed)}
    if hits:
        listed = ", ".join(sorted(hits))
        if doc_type in CLIENT_MONEY_DOCS:
            report.fail(
                f"tax wording present ({listed}) — invoices, receipts, delivery notes and "
                "registers carry no tax or VAT wording of any kind"
            )
        elif doc_type == "quotation":
            report.warn(
                f"tax wording present ({listed}) — the quotation VAT line contradicts every "
                "invoice TNDK issues and is unresolved; surface it to Farhan before issuing"
            )
    elif doc_type in CLIENT_MONEY_DOCS:
        report.ok("no tax or VAT wording")

    # 2. Payee line, exact wording.
    payee_line = PAYEE_TRIGGER.search(squashed)
    if payee_line:
        line = payee_line.group(0)
        if PAYEE_NAME.lower() not in line.lower():
            report.fail(
                f'payee line wrong — must read "…under the name of: {PAYEE_NAME}"; '
                f"found: {line.strip()!r}"
            )
        elif re.search(r"W\.?\s?L\.?\s?L\.?", line, re.I):
            report.fail("payee line carries W.L.L. — that line drops the W.L.L.")
        else:
            report.ok("payee line wording correct")
    elif doc_type in ("invoice", "receipt"):
        report.warn("no payee line found — invoices and receipts normally carry one")

    # 3. Document number in the right series.
    pattern, shape = NUMBER_PATTERNS[doc_type]
    if pattern:
        found = re.search(pattern, squashed, re.I)
        if found:
            report.ok(f"document number {found.group(0)} matches {shape}")
        else:
            report.fail(
                f"no {shape} document number found — check the numbering log and number it "
                "before this leaves the building"
            )

    # 4. Signatory.
    if doc_type in ("invoice", "receipt", "delivery-note"):
        if re.search(r"\bRonaldo\b", squashed, re.I):
            report.ok("signed Ronaldo / Accountant")
        else:
            report.fail("signature block should be 'Ronaldo / Accountant'")
    elif doc_type == "quotation":
        if re.search(r"\bFarhan\b", squashed, re.I):
            report.ok("signed Farhan / Sales Engineer")
        else:
            report.fail("signature block should be 'Farhan / Sales Engineer'")
    elif doc_type == "lpo":
        if re.search(r"computer\s+generated", squashed, re.I):
            report.ok("computer-generated callout present")
        else:
            report.fail(
                "LPOs carry the 'computer generated document' callout in place of a signature"
            )

    # 5. Receipts record the instrument the money arrived on.
    if doc_type == "receipt":
        cheque = re.search(r"\bcheque\b", squashed, re.I)
        if cheque and not re.search(r"subject\s+to\s+realization", squashed, re.I):
            report.fail(
                'cheque receipt missing "subject to realization of cheque."'
            )
        instrument = re.search(
            r"\b(cheque\s*(no|number|#)|transfer\s*(ref|reference)|payment\s*mode\s*:\s*cash)",
            squashed, re.I,
        )
        if instrument:
            report.ok("payment instrument captured")
        else:
            report.warn(
                "no payment instrument found — a receipt needs a cheque number, a transfer "
                "reference, or 'Payment Mode: Cash'"
            )

    # 6. A balance is a snapshot; it needs its date.
    if BALANCE.search(squashed) and not AS_OF.search(squashed):
        report.warn("a balance appears with no 'as of' date")

    # 7. Money formatting drift.
    unseparated = UNSEPARATED_MONEY.findall(squashed)
    if unseparated:
        report.warn(
            "amounts without thousands separators: "
            + ", ".join(sorted(set(unseparated))[:5])
        )

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument(
        "--type", required=True, choices=DOC_TYPES, dest="doc_type",
        help="what kind of document this is",
    )
    args = parser.parse_args()

    failed = False
    for path in args.files:
        print(f"\n{path.name}  [{args.doc_type}]")
        if not path.exists():
            print("  FAIL  file not found")
            failed = True
            continue
        try:
            text = extract_text(path)
        except Exception as exc:  # noqa: BLE001 — surface any reader problem plainly
            print(f"  FAIL  could not read: {exc}")
            failed = True
            continue
        if not text.strip():
            print("  FAIL  no text extracted — a scanned or image-only file cannot be checked")
            failed = True
            continue

        report = check(text, args.doc_type)
        for msg in report.passes:
            print(f"  ok    {msg}")
        for msg in report.warns:
            print(f"  WARN  {msg}")
        for msg in report.fails:
            print(f"  FAIL  {msg}")
        if report.fails:
            failed = True
        elif not report.warns:
            print("  — clean")

    print()
    if failed:
        print("Not deliverable. Fix the FAILs and run again.")
        return 2
    print("Passed. Check the arithmetic yourself before handing it over.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
