#!/usr/bin/env python3
"""Build a TNDK priced Bill of Quantities quotation on letterhead.

    python3 build_boq_quotation.py --spec boq.json --outdir out/

For tender and budgetary submissions: a multi-section priced bill with unit
rates, quantities, section subtotals and a grand total, running over as many
pages as it needs, on the house letterhead.

Arithmetic is recomputed here, not trusted. Every line amount is checked
against rate x quantity, every section total against its lines, and the grand
total against the sections named in `grand_total_sections`. A mismatch fails
the build and prints what disagreed. The register in Drive reported a book of
18,250 against a real 758,100 because a total covered only the first three
rows, and that is exactly the failure a priced BOQ is prone to.

No tax or VAT wording, per DECISIONS.md D-005 — the build fails if any appears.
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

CHROME = ["/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
          "/opt/pw-browsers/chromium/chrome-linux/chrome",
          "chromium", "chromium-browser", "google-chrome"]

TAX_WORDS = re.compile(r"\b(tax|taxes|taxable|vat)\b", re.I)


def esc(v) -> str:
    return html.escape(str(v if v is not None else ""))


def money(v) -> str:
    return f"{v:,.0f}" if float(v) == int(v) else f"{v:,.2f}"


def qty(v) -> str:
    return f"{v:,.0f}" if float(v) == int(v) else f"{v:,.2f}"


CSS = """
@page { size: A4 portrait; margin: 12mm 11mm 14mm; }
* { box-sizing: border-box; }
body { font-family: 'Calibri','Carlito','Liberation Sans',sans-serif; font-size: 8.4pt;
       line-height: 1.32; color: #333; margin: 0;
       -webkit-print-color-adjust: exact; print-color-adjust: exact; }

.letterhead { display: flex; justify-content: space-between; align-items: flex-start;
              gap: 6mm; background: #1F3864; color: #fff; padding: 5mm 6mm; }
.letterhead__name { font-size: 12pt; font-weight: 700; line-height: 1.15; white-space: nowrap; }
.letterhead__sub  { font-size: 8pt; margin-top: 1.4mm; opacity: .92; }
.letterhead__addr { font-size: 7.5pt; margin-top: 1mm; opacity: .85; }
.badge { background: #C9A24E; color: #1F3864; text-align: center; padding: 2.6mm 4mm;
         min-width: 38mm; flex-shrink: 0; }
.badge .small { font-size: 8pt; font-weight: 700; letter-spacing: .04em; }
.badge .big   { font-size: 11.5pt; font-weight: 700; letter-spacing: .05em; margin-top: .6mm; }
.gold-stripe { height: 1.4mm; background: #C9A24E; margin: 0 0 3.5mm; }

h1 { font-size: 11pt; font-weight: 700; color: #1F3864; margin: 0 0 1.5mm; }
.project { font-size: 9pt; color: #333; margin: 0 0 3mm; }
.meta { width: 100%; border-collapse: collapse; margin-bottom: 3mm; }
.meta td { border: .25mm solid #BFC7D5; padding: 1.3mm 2mm; font-size: 8pt; vertical-align: top; }
.meta .k { background: #D6E4F0; font-weight: 700; color: #1F3864; width: 24mm; white-space: nowrap; }

.banner { background: #FFF2CC; border-left: 1.2mm solid #C9A24E; padding: 2.2mm 3mm;
          font-size: 8.4pt; font-weight: 700; color: #7A5A00; margin-bottom: 4mm; }

table.boq { width: 100%; border-collapse: collapse; }
table.boq thead th { background: #2F5496; color: #fff; font-size: 7.8pt; text-align: left;
                     padding: 1.8mm 1.6mm; text-transform: uppercase; letter-spacing: .03em;
                     border: .25mm solid #2F5496; }
table.boq td { border: .25mm solid #D6E4F0; padding: 1.5mm 1.6mm; vertical-align: top; }
.c-item { width: 11mm; text-align: center; color: #1F3864; font-weight: 700; }
.c-unit { width: 13mm; text-align: center; }
.c-qty  { width: 15mm; text-align: right; }
.c-rate { width: 22mm; text-align: right; }
.c-amt  { width: 26mm; text-align: right; white-space: nowrap; font-weight: 700; color: #1F3864; }

tr.sec td { background: #1F3864; color: #fff; font-weight: 700; font-size: 8.6pt;
            padding: 2mm 2.2mm; letter-spacing: .03em; border-color: #1F3864; }
tr.sub td { background: #D6E4F0; font-weight: 700; color: #1F3864; font-size: 8.6pt; }
tr.opt td { background: #F2F2F2; }
tr.total td { background: #1F3864; color: #fff; font-weight: 700; font-size: 10pt;
              padding: 2.6mm 2.2mm; border-color: #1F3864; }
tr.total .c-amt { color: #C9A24E; }
tr.optiontotal td { background: #C9A24E; color: #1F3864; font-weight: 700; font-size: 9.4pt; }
tr.optiontotal .c-amt { color: #1F3864; }

h2 { font-size: 9.4pt; font-weight: 700; color: #fff; background: #1F3864;
     padding: 1.6mm 2.4mm; margin: 6mm 0 2.5mm; letter-spacing: .05em;
     text-transform: uppercase; break-after: avoid; }
ol.notes { margin: 0; padding-left: 5.5mm; }
ol.notes li { margin-bottom: 2mm; font-size: 8.6pt; text-align: justify; }

.sign { margin-top: 9mm; break-inside: avoid; }
.sign__for { font-weight: 700; color: #1F3864; margin-bottom: 13mm; font-size: 9pt; }
.sign__line { border-top: .3mm solid #1F3864; width: 66mm; padding-top: 1.6mm; }
.sign__name { font-weight: 700; color: #1F3864; font-size: 9.4pt; }
.sign__role { font-size: 8.6pt; color: #555; }
.foot { margin-top: 6mm; border-top: .25mm solid #D6E4F0; padding-top: 1.4mm;
        font-size: 7pt; color: #6B7280; text-align: center; }
"""


def verify(spec: dict) -> list[str]:
    """Recompute every amount, subtotal and the grand total."""
    problems, totals = [], {}
    for sec in spec["sections"]:
        running = 0.0
        for it in sec["items"]:
            expected = round(float(it["rate"]) * float(it["qty"]), 2)
            if "amount" in it and abs(expected - float(it["amount"])) > 0.01:
                problems.append(
                    f"{sec['key']}{it['no']}: {it['rate']} x {it['qty']} = {expected:,.2f}, "
                    f"stated {float(it['amount']):,.2f}")
            it["amount"] = expected
            running += expected
        running = round(running, 2)
        if "total" in sec and abs(running - float(sec["total"])) > 0.01:
            problems.append(f"Section {sec['key']} total: lines sum to {running:,.2f}, "
                            f"stated {float(sec['total']):,.2f}")
        sec["total"] = running
        totals[sec["key"]] = running

    wanted = spec.get("grand_total_sections", [])
    grand = round(sum(totals[k] for k in wanted), 2)
    if "grand_total" in spec and abs(grand - float(spec["grand_total"])) > 0.01:
        problems.append(f"Grand total: sections {'+'.join(wanted)} sum to {grand:,.2f}, "
                        f"stated {float(spec['grand_total']):,.2f}")
    spec["grand_total"] = grand
    return problems


def render(spec: dict) -> str:
    c = spec.get("company", {})
    badge = spec.get("badge", ["", ""])

    rows = []
    for sec in spec["sections"]:
        opt = " opt" if sec.get("option") else ""
        rows.append(f'<tr class="sec"><td colspan="6">{esc(sec["key"])}. {esc(sec["title"])}</td></tr>')
        for it in sec["items"]:
            rows.append(
                f'<tr class="{opt.strip()}"><td class="c-item">{esc(sec["key"])}.{esc(it["no"])}</td>'
                f'<td>{esc(it["description"])}</td>'
                f'<td class="c-unit">{esc(it["unit"])}</td>'
                f'<td class="c-qty">{qty(it["qty"])}</td>'
                f'<td class="c-rate">{money(it["rate"])}</td>'
                f'<td class="c-amt">{money(it["amount"])}</td></tr>')
        label = f'Total Section {sec["key"]}' + (" (Option)" if sec.get("option") else "")
        rows.append(f'<tr class="sub"><td colspan="5">{esc(label)}</td>'
                    f'<td class="c-amt">{money(sec["total"])}</td></tr>')

    included = ", ".join(spec.get("grand_total_sections", []))
    excluded = [s["key"] for s in spec["sections"] if s.get("option")]
    excl = f" — excluding Option {', '.join(excluded)}" if excluded else ""
    rows.append(f'<tr class="total"><td colspan="5">GRAND TOTAL — BUDGETARY '
                f'(Sections {esc(included)}{esc(excl)})</td>'
                f'<td class="c-amt">QAR {money(spec["grand_total"])}</td></tr>')
    for sec in spec["sections"]:
        if sec.get("option"):
            rows.append(f'<tr class="optiontotal"><td colspan="5">OPTION — Section '
                        f'{esc(sec["key"])} {esc(sec["title"])}, if required</td>'
                        f'<td class="c-amt">QAR {money(sec["total"])}</td></tr>')

    meta = "".join(
        f'<tr><td class="k">{esc(a)}</td><td>{esc(b)}</td>'
        f'<td class="k">{esc(c2)}</td><td>{esc(d)}</td></tr>'
        for a, b, c2, d in spec.get("meta_rows", []))

    notes = "".join(f"<li>{esc(n)}</li>" for n in spec.get("notes", []))

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

<h1>{esc(spec.get('doc_title',''))}</h1>
<div class="project">{esc(spec.get('project',''))}</div>
<table class="meta">{meta}</table>
<div class="banner">{esc(spec.get('banner',''))}</div>

<table class="boq">
  <thead><tr>
    <th class="c-item">Item</th><th>Description</th><th class="c-unit">Unit</th>
    <th class="c-qty">Qty</th><th class="c-rate">Unit Rate (QAR)</th>
    <th class="c-amt">Amount (QAR)</th>
  </tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>

<h2>Notes, Qualifications &amp; Conditions</h2>
<ol class="notes">{notes}</ol>

<div class="sign">
  <div class="sign__for">For {esc(c.get('name','THE NEW DOHA KITCHEN EQUIPMENT SERVICES W.L.L.'))}</div>
  <div class="sign__line">
    <div class="sign__name">{esc(spec.get('signatory',{}).get('name',''))}</div>
    <div class="sign__role">{esc(spec.get('signatory',{}).get('role',''))}</div>
  </div>
</div>

<div class="foot">{esc(c.get('address','P.O. Box 80247, Doha, State of Qatar'))}
  &nbsp;·&nbsp; Tel 7706 0676 &nbsp;·&nbsp; farhan@dctsqatar.com</div>
</body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--spec", required=True, type=Path)
    ap.add_argument("--outdir", required=True, type=Path)
    args = ap.parse_args()

    spec = json.loads(args.spec.read_text())

    problems = verify(spec)
    if problems:
        print("REFUSING TO BUILD — arithmetic does not reconcile:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 2
    print("arithmetic verified: every line, every section total, grand total")

    page = render(spec)
    text = re.sub(r"<[^>]+>", " ", page)
    found = {m.group(0).lower() for m in TAX_WORDS.finditer(text)}
    if found:
        print(f"REFUSING TO BUILD: tax wording present ({', '.join(sorted(found))}) — "
              f"see DECISIONS.md D-005.", file=sys.stderr)
        return 2

    outdir = args.outdir.resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    name = re.sub(r"[^A-Za-z0-9]+", "-", spec.get("filename") or spec["reference"]).strip("-")
    html_path = outdir / f"{name}.html"
    html_path.write_text(page)

    chrome = next((c for c in CHROME if (c.startswith("/") and Path(c).exists()) or shutil.which(c)), None)
    if not chrome:
        print(f"HTML → {html_path}  (no Chromium; print to PDF at A4)", file=sys.stderr)
        return 0
    chrome = chrome if chrome.startswith("/") else shutil.which(chrome)

    pdf = outdir / f"{name}.pdf"
    r = subprocess.run([chrome, "--headless", "--disable-gpu", "--no-sandbox",
                        "--hide-scrollbars", f"--print-to-pdf={pdf}",
                        "--no-pdf-header-footer", html_path.as_uri()],
                       capture_output=True, text=True)
    print(f"PDF  → {pdf}" if r.returncode == 0 else "PDF render failed")
    print(f"GRAND TOTAL QAR {money(spec['grand_total'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
