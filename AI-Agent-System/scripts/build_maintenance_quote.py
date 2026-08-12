#!/usr/bin/env python3
"""Build a TNDK maintenance quotation from a JSON spec.

    python3 build_maintenance_quote.py --spec quote.json --outdir out/

Produces `<ref>.pdf`, the HTML behind it, and a PNG of each page.

Why this exists separately from the cold room quotation. That document sells a
new room: thirteen sections covering panel construction, door details, machine
selection, heat load, control panel and a warranty on equipment TNDK supplied.
A maintenance or refurbishment job answers different questions — what is being
removed, what is being re-used, what is genuinely new, and who carries the risk
on plant that was already on site. Forcing that into the new-build format
produces a document that describes equipment nobody is buying.

House rules this enforces rather than leaves to memory:

  * No tax or VAT wording anywhere. DECISIONS.md D-005, ruled 10 Aug 2026 —
    the prohibition that always applied to invoices now covers every
    client-facing document. The build fails if any creeps in.
  * The payee line reads exactly "The New Doha Kitchen Equipment and Services".
  * Quotations are signed Farhan / Sales Engineer.
  * QAR, comma separated, two decimals, with the total repeated in words.
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

PAYEE = "The New Doha Kitchen Equipment and Services"
TAX_WORDS = re.compile(r"\b(tax|taxes|taxable|vat)\b", re.I)

UNITS = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
         "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
         "Seventeen", "Eighteen", "Nineteen"]
TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]


def words(n: int) -> str:
    if n < 20:
        return UNITS[n]
    if n < 100:
        return TENS[n // 10] + (f"-{UNITS[n % 10]}" if n % 10 else "")
    if n < 1000:
        return UNITS[n // 100] + " Hundred" + (f" {words(n % 100)}" if n % 100 else "")
    for divisor, label in ((1_000_000, "Million"), (1000, "Thousand")):
        if n >= divisor:
            return words(n // divisor) + f" {label}" + (f" {words(n % divisor)}" if n % divisor else "")
    return str(n)


def amount_in_words(total: float) -> str:
    riyals = int(total)
    dirhams = int(round((total - riyals) * 100))
    text = f"Qatari Riyals {words(riyals)}"
    if dirhams:
        text += f" and {words(dirhams)} Dirhams"
    return text + " Only."


def money(value: float) -> str:
    return f"{value:,.2f}"


def esc(value) -> str:
    return html.escape(str(value if value is not None else ""))


CSS = """
/* The band sits inside the page margins rather than bleeding to the paper
   edge. Negative margins would bleed it, but anything pulled outside the page
   box is liable to be clipped by the print engine — and a letterhead with the
   company name sheared off is worse than one that stops at the margin. */
@page { size: A4 portrait; margin: 13mm 14mm 15mm; }
* { box-sizing: border-box; }
body { font-family: 'Calibri','Carlito','Liberation Sans',sans-serif; font-size: 9.4pt;
       line-height: 1.45; color: #333; margin: 0;
       -webkit-print-color-adjust: exact; print-color-adjust: exact; }

/* ---- letterhead: matches the TNDK band used on LPOs ---- */
.letterhead { display: flex; justify-content: space-between; align-items: flex-start;
              gap: 8mm; background: #1F3864; color: #fff;
              padding: 5.5mm 7mm; }
.letterhead__name { font-size: 12.6pt; font-weight: 700; line-height: 1.15;
                    letter-spacing: .02em; white-space: nowrap; }
.letterhead__sub  { font-size: 8.5pt; margin-top: 1.6mm; opacity: .92; }
.letterhead__addr { font-size: 8pt; margin-top: 1.2mm; opacity: .85; }
.badge { background: #C9A24E; color: #1F3864; text-align: center; padding: 3mm 5mm;
         min-width: 40mm; flex-shrink: 0; }
.badge .small { font-size: 8.5pt; font-weight: 700; letter-spacing: .04em; }
.badge .big   { font-size: 12.5pt; font-weight: 700; letter-spacing: .06em; margin-top: .8mm; }
.gold-stripe { height: 1.6mm; background: #C9A24E; margin: 0 0 4mm; }

table { width: 100%; border-collapse: collapse; }
.meta td { border: .25mm solid #BFC7D5; padding: 1.6mm 2.2mm; font-size: 8.5pt; vertical-align: top; }
.meta .k { background: #D6E4F0; font-weight: 700; color: #1F3864; width: 24mm; }

.parties { margin: 3mm 0 4mm; }
.parties td { border: .25mm solid #BFC7D5; padding: 2.4mm; width: 50%; vertical-align: top; font-size: 8.5pt; }
.parties .hdr { background: #1F3864; color: #fff; font-weight: 700; font-size: 7.5pt;
                letter-spacing: .1em; padding: 1.4mm 2.4mm; text-transform: uppercase; }

h2 { font-size: 9.8pt; font-weight: 700; color: #fff; background: #1F3864;
     padding: 1.6mm 2.6mm; margin: 3.2mm 0 2mm; letter-spacing: .06em;
     text-transform: uppercase; break-after: avoid; }

p { margin: 0 0 2mm; }
h2.newpage { break-before: page; page-break-before: always; margin-top: 0; }
/* Keep a table with the heading that introduces it. */
.spec, .boq, .total { break-inside: auto; }
.subject { background: #F2F2F2; border-left: 1.2mm solid #C9A24E; padding: 2.4mm 3mm; margin-bottom: 3mm; }
.subject strong { color: #1F3864; }

ol.scope, ul.plain { margin: 0 0 1.5mm; padding-left: 5.5mm; }
ol.scope li, ul.plain li { margin-bottom: 1.8mm; }

.boq th { background: #2F5496; color: #fff; font-size: 8pt; text-align: left;
          padding: 1.9mm 2.2mm; letter-spacing: .04em; text-transform: uppercase; }
.boq td { border-bottom: .25mm solid #D6E4F0; padding: 1.9mm 2.4mm; font-size: 8.8pt; vertical-align: top; }
.boq tr:nth-child(even) td { background: #FAFBFC; }
.boq .num { width: 8mm; text-align: center; color: #6B7280; }
.boq .amt { width: 28mm; text-align: right; white-space: nowrap; }

.total { margin-top: 2.5mm; background: #1F3864; color: #fff; }
.total td { padding: 2.4mm 3mm; font-weight: 700; font-size: 10pt; }
.total .amt { text-align: right; }
.words { font-size: 8.5pt; font-style: italic; color: #1F3864; margin-top: 1.2mm; }

.spec td { border: .25mm solid #BFC7D5; padding: 2mm 2.4mm; font-size: 8.8pt; vertical-align: top; }
.spec .k { background: #D6E4F0; font-weight: 700; color: #1F3864; width: 38mm; }

.payee { background: #D6E4F0; border-left: 1.2mm solid #1F3864; padding: 2mm 3mm;
         font-size: 8.5pt; font-weight: 700; color: #1F3864; margin: 2mm 0 0; }

.sign { margin-top: 5mm; break-inside: avoid; }
.sign__name { font-weight: 700; color: #1F3864; margin-top: 7mm; }
.foot { margin-top: 5mm; border-top: .25mm solid #D6E4F0; padding-top: 1.6mm;
        font-size: 7pt; color: #6B7280; text-align: center; }
"""


def render(spec: dict) -> str:
    company = spec.get("company", {})
    client = spec.get("client", {})

    # Sections named in `page_breaks` start a new sheet. Pagination is a
    # deliberate choice on a quotation — the client reads the price on one page
    # and the exclusions on another, and neither should straddle a fold.
    breaks = set(spec.get("page_breaks", []))

    def section(title: str, body: str) -> str:
        if not body:
            return ""
        cls = ' class="newpage"' if title in breaks else ""
        return f"<h2{cls}>{esc(title)}</h2>{body}"

    scope = "".join(f"<li>{esc(i)}</li>" for i in spec.get("scope", []))
    scope_html = f'<ol class="scope">{scope}</ol>' if scope else ""

    spec_rows = "".join(
        f'<tr><td class="k">{esc(r["label"])}</td><td>{esc(r["value"])}</td></tr>'
        for r in spec.get("specification", [])
    )
    spec_html = f'<table class="spec">{spec_rows}</table>' if spec_rows else ""

    items = spec.get("items", [])
    priced = any(it.get("amount") is not None for it in items)
    rows = "".join(
        f'<tr><td class="num">{i}</td><td>{esc(it["description"])}</td>'
        + (f'<td class="amt">{money(it["amount"]) if it.get("amount") is not None else ""}</td>'
           if priced else "")
        + "</tr>"
        for i, it in enumerate(items, 1)
    )
    total = spec["total"]
    boq_html = (
        f'<table class="boq"><thead><tr><th class="num">#</th><th>Description</th>'
        + ('<th class="amt">Amount (QAR)</th>' if priced else "")
        + "</tr></thead>"
        f"<tbody>{rows}</tbody></table>"
        f'<table class="total"><tr><td>GRAND TOTAL (Lump Sum)</td>'
        f'<td class="amt">QAR {money(total)}</td></tr></table>'
        f'<p class="words">Amount in words: {esc(spec.get("total_words") or amount_in_words(total))}</p>'
    )

    def bullets(key: str) -> str:
        vals = spec.get(key, [])
        return f'<ul class="plain">{"".join(f"<li>{esc(v)}</li>" for v in vals)}</ul>' if vals else ""

    completion = "".join(
        f'<tr><td class="k">{esc(r["label"])}</td><td>{esc(r["value"])}</td></tr>'
        for r in spec.get("completion", [])
    )
    completion_html = f'<table class="spec">{completion}</table>' if completion else ""

    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>{esc(spec.get('reference',''))}</title><style>{CSS}</style></head><body>

<div class="letterhead">
  <div>
    <div class="letterhead__name">{esc(company.get('name','THE NEW DOHA KITCHEN EQUIPMENT SERVICES W.L.L.'))}</div>
    <div class="letterhead__sub">{esc(company.get('subtitle','Division of Doha Cooling Trading & Solutions W.L.L.'))}</div>
    <div class="letterhead__addr">{esc(company.get('address','P.O. Box 80247, Doha, State of Qatar'))} &nbsp;·&nbsp; {esc(company.get('contact','Tel 7706 0676 · farhan@dctsqatar.com'))}</div>
  </div>
  <div class="badge"><div class="small">MAINTENANCE</div><div class="big">QUOTATION</div></div>
</div>
<div class="gold-stripe"></div>

<table class="meta">
  <tr><td class="k">Reference</td><td>{esc(spec.get('reference',''))}</td>
      <td class="k">Date</td><td>{esc(spec.get('date',''))}</td>
      <td class="k">Validity</td><td>{esc(spec.get('validity','15 days from date of issue'))}</td></tr>
</table>

<table class="parties">
  <tr><td class="hdr">To</td><td class="hdr">From</td></tr>
  <tr>
    <td><strong>{esc(client.get('name',''))}</strong>
        {'<br>' + esc(client.get('address','')) if client.get('address') else ''}
        {'<br>Attn: ' + esc(client.get('attn','')) if client.get('attn') else ''}</td>
    <td><strong>The New Doha Kitchen Equipment Services W.L.L.</strong><br>
        P.O. Box 80247, Doha, State of Qatar<br>Tel 7706 0676 · farhan@dctsqatar.com</td>
  </tr>
</table>

<div class="subject"><strong>Subject:</strong> {esc(spec.get('subject',''))}</div>
<p>{esc(spec.get('intro',''))}</p>

{section('Scope of Work', scope_html)}
{section('Materials & Specification', spec_html)}
{section('Pricing / Bill of Quantities', boq_html)}
{section('Payment Terms', bullets('payment_terms')
         + f'<div class="payee">Cheque should be prepared under the name of: {esc(PAYEE)}</div>')}
{section('Work Completion', completion_html)}
{section('Warranty', bullets('warranty'))}
{section('Exclusions', bullets('exclusions'))}

<div class="sign">
  <p>{esc(spec.get('closing','We trust the above meets your requirement and look forward to your valued order. Should you need any clarification, please do not hesitate to contact us.'))}</p>
  <p>Best Regards,</p>
  <div class="sign__name">Farhan</div>
  <div>Sales Engineer</div>
  <div>The New Doha Kitchen Equipment Services W.L.L &amp; Doha Cooling Trading &amp; Solutions W.L.L</div>
  <div>Email: farhan@dctsqatar.com</div>
</div>

<div class="foot">{esc(company.get('address','P.O. Box 80247, Doha, State of Qatar'))}
  &nbsp;·&nbsp; Tel 7706 0676 &nbsp;·&nbsp; farhan@dctsqatar.com</div>
</body></html>"""


def find_chrome() -> str | None:
    for c in CHROME_CANDIDATES:
        if c.startswith("/") and Path(c).exists():
            return c
        found = shutil.which(c)
        if found:
            return found
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--spec", required=True, type=Path)
    ap.add_argument("--outdir", required=True, type=Path)
    args = ap.parse_args()

    spec = json.loads(args.spec.read_text())
    page = render(spec)

    # The tax prohibition is absolute, so it is checked here rather than trusted
    # to whoever wrote the JSON.
    stripped = re.sub(r"<[^>]+>", " ", page)
    found = {m.group(0).lower() for m in TAX_WORDS.finditer(stripped)}
    if found:
        print(f"REFUSING TO BUILD: tax wording present ({', '.join(sorted(found))}). "
              f"See DECISIONS.md D-005 — no tax or VAT wording in any client document.",
              file=sys.stderr)
        return 2
    if PAYEE not in stripped:
        print("REFUSING TO BUILD: payee line missing or altered.", file=sys.stderr)
        return 2

    outdir = args.outdir.resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    name = re.sub(r"[^A-Za-z0-9]+", "-", spec.get("reference", "quotation")).strip("-")
    html_path = outdir / f"{name}.html"
    html_path.write_text(page)
    print(f"HTML → {html_path}")

    chrome = find_chrome()
    if not chrome:
        print("No Chromium found — open the HTML and print to PDF at A4.", file=sys.stderr)
        return 0

    pdf = outdir / f"{name}.pdf"
    result = subprocess.run(
        [chrome, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
         f"--print-to-pdf={pdf}", "--no-pdf-header-footer", html_path.as_uri()],
        capture_output=True, text=True)
    print(f"PDF  → {pdf}" if result.returncode == 0 else "PDF render failed")

    preview = outdir / "preview.png"
    subprocess.run(
        [chrome, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
         "--window-size=794,3200", f"--screenshot={preview}", html_path.as_uri()],
        capture_output=True, text=True)
    if preview.exists():
        print(f"PNG  → {preview}   (look at it before sending)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
