#!/usr/bin/env python3
"""Build a TNDK company letter or certificate from a JSON spec.

    python3 build_company_letter.py --spec letter.json --outdir out/

For the letters a company issues about itself and its people — employment and
salary certificates, experience letters, no-objection certificates, undertakings
and general correspondence on letterhead. One page by default.

These are the documents that get typed from scratch each time, which is how a
company ends up with five different letterheads and a certificate that omits the
QID the bank actually needed. The letterhead, the reference block, the details
table and the signature block are fixed here; only the content changes.

Two things the generator will not do:

  * No tax or VAT wording. DECISIONS.md D-005 — the prohibition covers every
    client-facing document, and the build fails if any appears.
  * No placeholder left unfilled. A field still holding [SQUARE BRACKETS] fails
    the build, because a certificate issued with [DATE OF JOINING] on it is
    worse than one that was never sent.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

CHROME_CANDIDATES = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/opt/pw-browsers/chromium/chrome-linux/chrome",
    "chromium", "chromium-browser", "google-chrome",
]

TAX_WORDS = re.compile(r"\b(tax|taxes|taxable|vat)\b", re.I)
PLACEHOLDER = re.compile(r"\[[A-Z][A-Z /&'\-]{3,}\]")


def esc(v) -> str:
    return html.escape(str(v if v is not None else ""))


CSS = """
@page { size: A4 portrait; margin: 13mm 16mm 15mm; }
* { box-sizing: border-box; }
body { font-family: 'Calibri','Carlito','Liberation Sans',sans-serif; font-size: 10.5pt;
       line-height: 1.5; color: #333; margin: 0;
       -webkit-print-color-adjust: exact; print-color-adjust: exact; }

.letterhead { display: flex; justify-content: space-between; align-items: flex-start;
              gap: 8mm; background: #1F3864; color: #fff; padding: 5.5mm 7mm; }
.letterhead__name { font-size: 12.6pt; font-weight: 700; line-height: 1.15;
                    letter-spacing: .02em; white-space: nowrap; }
.letterhead__sub  { font-size: 8.5pt; margin-top: 1.6mm; opacity: .92; }
.letterhead__addr { font-size: 8pt; margin-top: 1.2mm; opacity: .85; }
.badge { background: #C9A24E; color: #1F3864; text-align: center; padding: 3mm 5mm;
         min-width: 42mm; flex-shrink: 0; }
.badge .small { font-size: 8.5pt; font-weight: 700; letter-spacing: .04em; }
.badge .big   { font-size: 12.5pt; font-weight: 700; letter-spacing: .06em; margin-top: .8mm; }
.gold-stripe { height: 1.6mm; background: #C9A24E; margin: 0 0 5mm; }

.refline { display: flex; justify-content: space-between; font-size: 10pt;
           color: #1F3864; font-weight: 700; margin-bottom: 6mm; }

h1 { font-size: 13pt; font-weight: 700; color: #1F3864; text-align: center;
     letter-spacing: .14em; text-transform: uppercase; margin: 0 0 3mm; }
.rule { width: 44mm; height: .9mm; background: #C9A24E; margin: 0 auto 6mm; }

p { margin: 0 0 3.5mm; text-align: justify; }

.details { width: 100%; border-collapse: collapse; margin: 5mm 0 5mm; }
.details td { border: .25mm solid #BFC7D5; padding: 1.5mm 3mm; font-size: 10pt;
              vertical-align: top; }
.details .k { background: #D6E4F0; font-weight: 700; color: #1F3864; width: 52mm; }

.note { font-size: 9.5pt; color: #555; font-style: italic; margin-top: 4mm; }

.sign { margin-top: 6mm; break-inside: avoid; }
.sign__for { font-weight: 700; color: #1F3864; margin-bottom: 10mm; }
.sign__line { border-top: .3mm solid #1F3864; width: 68mm; padding-top: 2mm; }
.sign__name { font-weight: 700; color: #1F3864; }
.sign__role { font-size: 10pt; color: #555; }
.stamp { font-size: 9pt; color: #6B7280; margin-top: 4mm; }

/* Static, not fixed. A fixed footer sits inside the page content box, so a
   signature block that reaches the foot of the page prints straight through
   it — which is exactly where a signature block ends up. */
.foot { margin-top: 6mm; border-top: .25mm solid #D6E4F0; padding-top: 1.6mm;
        font-size: 7.5pt; color: #6B7280; text-align: center; }
"""


def render(spec: dict) -> str:
    c = spec.get("company", {})
    rows = "".join(
        f'<tr><td class="k">{esc(d["label"])}</td><td>{esc(d["value"])}</td></tr>'
        for d in spec.get("details", [])
    )
    details = f'<table class="details">{rows}</table>' if rows else ""
    body = "".join(f"<p>{esc(p)}</p>" for p in spec.get("body", []))
    closing = "".join(f"<p>{esc(p)}</p>" for p in spec.get("closing", []))
    note = f'<p class="note">{esc(spec["note"])}</p>' if spec.get("note") else ""
    badge = spec.get("badge", ["", ""])

    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>{esc(spec.get('reference',''))}</title><style>{CSS}</style></head><body>

<div class="letterhead">
  <div>
    <div class="letterhead__name">{esc(c.get('name','THE NEW DOHA KITCHEN EQUIPMENT SERVICES W.L.L.'))}</div>
    <div class="letterhead__sub">{esc(c.get('subtitle','Division of Doha Cooling Trading & Solutions W.L.L.'))}</div>
    <div class="letterhead__addr">{esc(c.get('address','P.O. Box 80247, Doha, State of Qatar'))} &nbsp;·&nbsp; {esc(c.get('contact','Tel 7706 0676 · farhan@dctsqatar.com'))}</div>
  </div>
  <div class="badge"><div class="small">{esc(badge[0])}</div><div class="big">{esc(badge[1])}</div></div>
</div>
<div class="gold-stripe"></div>

<div class="refline">
  <span>Ref: {esc(spec.get('reference',''))}</span>
  <span>Date: {esc(spec.get('date',''))}</span>
</div>

<h1>{esc(spec.get('title','To Whom It May Concern'))}</h1>
<div class="rule"></div>

{body}
{details}
{closing}
{note}

<div class="sign">
  <div class="sign__for">For {esc(c.get('name','THE NEW DOHA KITCHEN EQUIPMENT SERVICES W.L.L.'))}</div>
  <div class="sign__line">
    <div class="sign__name">{esc(spec.get('signatory',{}).get('name',''))}</div>
    <div class="sign__role">{esc(spec.get('signatory',{}).get('role',''))}</div>
  </div>
  <div class="stamp">Company Stamp</div>
</div>

<div class="foot">{esc(c.get('address','P.O. Box 80247, Doha, State of Qatar'))}
  &nbsp;·&nbsp; Tel 7706 0676 &nbsp;·&nbsp; farhan@dctsqatar.com</div>
</body></html>"""


def find_chrome():
    for c in CHROME_CANDIDATES:
        if c.startswith("/") and Path(c).exists():
            return c
        if shutil.which(c):
            return shutil.which(c)
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--spec", required=True, type=Path)
    ap.add_argument("--outdir", required=True, type=Path)
    args = ap.parse_args()

    spec = json.loads(args.spec.read_text())
    page = render(spec)
    text = re.sub(r"<[^>]+>", " ", page)

    found = {m.group(0).lower() for m in TAX_WORDS.finditer(text)}
    if found:
        print(f"REFUSING TO BUILD: tax wording present ({', '.join(sorted(found))}) — "
              f"see DECISIONS.md D-005.", file=sys.stderr)
        return 2
    left = PLACEHOLDER.findall(text)
    if left:
        print(f"REFUSING TO BUILD: unfilled placeholder(s) {sorted(set(left))}. "
              f"A certificate issued with a placeholder on it cannot be withdrawn.",
              file=sys.stderr)
        return 2

    outdir = args.outdir.resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    name = re.sub(r"[^A-Za-z0-9]+", "-", spec.get("filename") or spec.get("reference", "letter")).strip("-")
    html_path = outdir / f"{name}.html"
    html_path.write_text(page)
    print(f"HTML → {html_path}")

    chrome = find_chrome()
    if not chrome:
        print("No Chromium — open the HTML and print to PDF at A4.", file=sys.stderr)
        return 0

    pdf = outdir / f"{name}.pdf"
    r = subprocess.run([chrome, "--headless", "--disable-gpu", "--no-sandbox",
                        "--hide-scrollbars", f"--print-to-pdf={pdf}",
                        "--no-pdf-header-footer", html_path.as_uri()],
                       capture_output=True, text=True)
    print(f"PDF  → {pdf}" if r.returncode == 0 else "PDF render failed")

    shot = outdir / "preview.png"
    subprocess.run([chrome, "--headless", "--disable-gpu", "--no-sandbox",
                    "--hide-scrollbars", "--window-size=794,1200",
                    f"--screenshot={shot}", html_path.as_uri()],
                   capture_output=True, text=True)
    if shot.exists():
        print(f"PNG  → {shot}   (look at it before signing)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
