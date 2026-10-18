#!/usr/bin/env python3
"""Build a Tally ERP 9 style columnar register from a JSON spec.

    python3 build_tally_register.py --spec register.json --outdir out/

Tally's printed registers have a look people recognise instantly, and it is
made of a few specific things rather than a general "plain table":

  * monochrome — no colour anywhere, no filled header bands;
  * a plain centred company name and report title, no letterhead;
  * a boxed grid with vertical rules running the full height but **no
    horizontal rule between data rows** — only under the header and above the
    total. This is the single strongest tell, and a table with row lines reads
    as a spreadsheet export instead;
  * narration italic and indented under the particulars;
  * dates as 8-Sep-2025, amounts right-aligned to two decimals;
  * a ruled Grand Total with a double underline beneath the figure.

The arithmetic is recomputed, never trusted: every row against the grand
total, and each group against its own subtotal. A register whose total does
not equal its lines is the specific failure this format exists to prevent.

Page numbering is stamped afterwards, because Chromium ignores CSS paged-media
margin boxes, so `@bottom-right { content: counter(page) }` is silently
dropped.
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

PAGE_H_MM = 297.0
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def esc(v) -> str:
    return html.escape(str(v if v is not None else ""))


def money(v) -> str:
    return f"{float(v):,.2f}"


def tally_date(v: str) -> str:
    """dd-mm-yyyy or yyyy-mm-dd to Tally's 8-Sep-2025."""
    s = str(v).strip()
    m = re.fullmatch(r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})", s)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
    else:
        m = re.fullmatch(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", s)
        if not m:
            return s
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if not 1 <= mo <= 12:
        return s
    return f"{d}-{MONTHS[mo - 1]}-{y}"


CSS = """
@page { size: A4 portrait; margin: 10mm 8mm 16mm; }
* { box-sizing: border-box; }
body { font-family: 'Times New Roman','Liberation Serif',Times,serif;
       font-size: 8.4pt; line-height: 1.26; color: #000; margin: 0;
       -webkit-print-color-adjust: exact; print-color-adjust: exact; }

.hd { text-align: center; }
.hd__co { font-size: 13pt; font-weight: 700; letter-spacing: .02em; }
.hd__co2 { font-size: 10pt; font-weight: 700; margin-top: .6mm; }
.hd__addr { font-size: 8pt; margin-top: .8mm; }
.hd__rule { border-top: .35mm solid #000; margin: 2mm 0 1.8mm; }
.hd__title { font-size: 11.5pt; font-weight: 700; }
.hd__period { font-size: 8.6pt; margin-top: .6mm; }
.hd__sub { font-size: 7.8pt; margin-top: .8mm; }
.hd__bar { display: flex; justify-content: space-between; font-size: 7.4pt;
           margin-bottom: 1.4mm; }

table.reg { width: 100%; border-collapse: collapse; border: .35mm solid #000;
            table-layout: fixed; margin-top: 1.6mm; }
table.reg th { font-weight: 700; font-size: 7.8pt; text-align: left;
               padding: 1.4mm 1.4mm; border-bottom: .35mm solid #000;
               border-left: .2mm solid #000; vertical-align: bottom; }
table.reg th:first-child { border-left: 0; }
/* No rule between data rows — the Tally tell. Verticals only. */
table.reg td { padding: 1.3mm 1.4mm; vertical-align: top;
               border-left: .2mm solid #000; border-top: 0; border-bottom: 0; }
table.reg td:first-child { border-left: 0; }
table.reg tbody tr { break-inside: avoid; }
/* Only the columns that carry unbroken machine references may break mid-token;
   letting every cell do it turns "TNDK" into "TND K". */
td.brk { overflow-wrap: anywhere; }
td.r, th.r { text-align: right; }
td.c, th.c { text-align: center; }
.nowrap { white-space: nowrap; }
.party { font-weight: 700; }
.narr { font-style: italic; font-size: 7.4pt; padding-left: 2.6mm;
        display: block; margin-top: .4mm; }
tr.gap td { height: 1.6mm; padding: 0; }

tr.total td { border-top: .35mm solid #000; font-weight: 700; font-size: 9pt;
              padding: 1.8mm 1.4mm; }
tr.total td.r { text-decoration: none; }
/* Tally rules the grand total figure with two parallel lines. A `double`
   border needs enough width to split and prints as one thick bar at these
   sizes, so the two rules are drawn as nested spans. */
.dbl { border-bottom: .2mm solid #000; display: inline-block; padding-bottom: .7mm; }
.dbl > span { border-bottom: .2mm solid #000; display: inline-block;
              padding-bottom: .7mm; }

table.sub { border-collapse: collapse; border: .35mm solid #000; margin-top: 4mm;
            font-size: 8.2pt; }
table.sub th { font-weight: 700; text-align: left; padding: 1.3mm 3mm;
               border-bottom: .35mm solid #000; border-left: .2mm solid #000; }
table.sub th:first-child { border-left: 0; }
table.sub td { padding: 1.2mm 3mm; border-left: .2mm solid #000; }
table.sub td:first-child { border-left: 0; }
table.sub tr.t td { border-top: .35mm solid #000; font-weight: 700; }

.notes { margin-top: 4.5mm; font-size: 7.8pt; line-height: 1.4; }
.notes__h { font-weight: 700; margin-bottom: 1mm; }
.notes p { margin: 0 0 1.4mm; text-align: justify; }
.sign { margin-top: 9mm; font-size: 8.4pt; }
.sign__line { border-top: .25mm solid #000; width: 88mm; padding-top: 1.4mm; }
.sign__n { font-weight: 700; }
"""

FOOTER_CSS = """
@page { size: A4 portrait; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; font-family: 'Times New Roman','Liberation Serif',Times,serif;
       color: #000; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.pg { height: %(h)smm; position: relative; break-after: page; }
.pg:last-child { break-after: auto; }
.ft { position: absolute; left: 8mm; right: 8mm; bottom: 8mm;
      display: flex; justify-content: space-between; font-size: 7.2pt; }
""" % {"h": PAGE_H_MM}


def verify(spec: dict) -> list[str]:
    problems: list[str] = []
    rows = spec["rows"]
    total = round(sum(float(r["amount"]) for r in rows), 2)
    if "grand_total" in spec and abs(total - float(spec["grand_total"])) > 0.01:
        problems.append(f"{len(rows)} rows sum to {total:,.2f}, stated grand total "
                        f"{float(spec['grand_total']):,.2f}")
    spec["grand_total"] = total

    if "count" in spec and int(spec["count"]) != len(rows):
        problems.append(f"{len(rows)} rows present, stated count {spec['count']}")
    spec["count"] = len(rows)

    for g in spec.get("subtotals", []):
        got = [r for r in rows if r.get(g["key"]) == g["value"]]
        amt = round(sum(float(r["amount"]) for r in got), 2)
        if "amount" in g and abs(amt - float(g["amount"])) > 0.01:
            problems.append(f"{g['value']}: {len(got)} rows sum to {amt:,.2f}, "
                            f"stated {float(g['amount']):,.2f}")
        if "count" in g and int(g["count"]) != len(got):
            problems.append(f"{g['value']}: {len(got)} rows present, stated "
                            f"count {g['count']}")
        g["amount"], g["count"] = amt, len(got)

    covered = round(sum(float(g["amount"]) for g in spec.get("subtotals", [])), 2)
    if spec.get("subtotals") and abs(covered - total) > 0.01:
        problems.append(f"subtotals cover {covered:,.2f} of a {total:,.2f} register — "
                        f"{total - covered:,.2f} sits in no group")
    return problems


def render(spec: dict) -> str:
    cols = spec["columns"]
    cg = "".join(f'<col style="width:{c["w"]}">' if c.get("w") else "<col>"
                 for c in cols)
    th = "".join(f'<th class="{c.get("align","")}">{esc(c["label"])}</th>' for c in cols)

    body = []
    for r in spec["rows"]:
        tds = []
        for c in cols:
            k, a = c["key"], c.get("align", "")
            if k == "date":
                v = f'<span class="nowrap">{esc(tally_date(r["date"]))}</span>'
            elif k == "particulars":
                v = f'<span class="party">{esc(r["party"])}</span>'
                for n in r.get("narration", []):
                    v += f'<span class="narr">{esc(n)}</span>'
            elif k == "amount":
                v = money(r["amount"])
            else:
                v = esc(r.get(k, ""))
            cls = " ".join(x for x in (a, "brk" if c.get("brk") else "") if x)
            tds.append(f'<td class="{cls}">{v}</td>')
        body.append(f"<tr>{''.join(tds)}</tr>")

    span_before = len(cols) - 1
    body.append(f'<tr class="gap"><td colspan="{len(cols)}"></td></tr>')
    body.append(
        f'<tr class="total"><td colspan="{span_before}">{esc(spec["total_label"])}</td>'
        f'<td class="r"><span class="dbl"><span>{money(spec["grand_total"])}</span></span></td></tr>')

    subs = ""
    if spec.get("subtotals"):
        rows = "".join(
            f'<tr><td>{esc(g["value"])} — {esc(g.get("label",""))}</td>'
            f'<td class="c">{g["count"]}</td><td class="r">{money(g["amount"])}</td></tr>'
            for g in spec["subtotals"])
        rows += (f'<tr class="t"><td>Total</td><td class="c">{spec["count"]}</td>'
                 f'<td class="r">{money(spec["grand_total"])}</td></tr>')
        subs = (f'<table class="sub"><thead><tr><th>Company</th>'
                f'<th class="c">Vouchers</th><th class="r">Amount</th></tr></thead>'
                f"<tbody>{rows}</tbody></table>")

    notes = ""
    if spec.get("notes"):
        ps = "".join(f"<p>{esc(n)}</p>" for n in spec["notes"])
        notes = (f'<div class="notes"><div class="notes__h">'
                 f'{esc(spec.get("notes_heading","Notes"))}</div>{ps}</div>')

    sign = ""
    if spec.get("signatory"):
        s = spec["signatory"]
        extra = "".join(f"<div>{esc(x)}</div>" for x in s.get("lines", []))
        sign = (f'<div class="sign"><div class="sign__line">'
                f'<div class="sign__n">{esc(s["name"])}</div>{extra}</div></div>')

    h = spec["heading"]
    co2 = f'<div class="hd__co2">{esc(h["company2"])}</div>' if h.get("company2") else ""
    addr = f'<div class="hd__addr">{esc(h["address"])}</div>' if h.get("address") else ""
    sub = f'<div class="hd__sub">{esc(h["subtitle"])}</div>' if h.get("subtitle") else ""

    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>{esc(spec.get('reference',''))}</title><style>{CSS}</style></head><body>
<div class="hd">
  <div class="hd__co">{esc(h["company"])}</div>{co2}{addr}
  <div class="hd__rule"></div>
  <div class="hd__title">{esc(h["title"])}</div>
  <div class="hd__period">{esc(h["period"])}</div>{sub}
  <div class="hd__rule"></div>
</div>
<div class="hd__bar"><span>{esc(spec.get('bar_left',''))}</span>
  <span>{esc(spec.get('bar_right',''))}</span></div>
<table class="reg">{cg}<thead><tr>{th}</tr></thead><tbody>{''.join(body)}</tbody></table>
{subs}{notes}{sign}
</body></html>"""


def render_footers(spec: dict, pages: int) -> str:
    divs = []
    for n in range(1, pages + 1):
        divs.append(f'<div class="pg"><div class="ft">'
                    f'<span>{esc(spec.get("footer_left",""))}</span>'
                    f'<span>Page {n} of {pages}</span></div></div>')
    return (f'<!doctype html><html><head><meta charset="utf-8">'
            f"<style>{FOOTER_CSS}</style></head><body>{''.join(divs)}</body></html>")


def chrome_pdf(chrome: str, html_path: Path, pdf: Path) -> bool:
    r = subprocess.run([chrome, "--headless", "--disable-gpu", "--no-sandbox",
                        "--hide-scrollbars", f"--print-to-pdf={pdf}",
                        "--no-pdf-header-footer", html_path.as_uri()],
                       capture_output=True, text=True)
    return r.returncode == 0 and pdf.exists()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--spec", required=True, type=Path)
    ap.add_argument("--outdir", required=True, type=Path)
    args = ap.parse_args()

    spec = json.loads(args.spec.read_text())

    problems = verify(spec)
    if problems:
        print("REFUSING TO BUILD — the register does not reconcile:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 2
    print(f"verified: {spec['count']} vouchers, grand total "
          f"{money(spec['grand_total'])}, subtotals reconcile")

    outdir = args.outdir.resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    name = re.sub(r"[^A-Za-z0-9]+", "-",
                  spec.get("filename") or spec["reference"]).strip("-")
    html_path = outdir / f"{name}.html"
    html_path.write_text(render(spec))

    chrome = next((c for c in CHROME
                   if (c.startswith("/") and Path(c).exists()) or shutil.which(c)), None)
    if not chrome:
        print(f"HTML → {html_path}  (no Chromium; print to PDF at A4)", file=sys.stderr)
        return 0
    chrome = chrome if chrome.startswith("/") else shutil.which(chrome)

    body_pdf = outdir / f"{name}.body.pdf"
    if not chrome_pdf(chrome, html_path, body_pdf):
        print("PDF render failed", file=sys.stderr)
        return 1

    # Broken cryptography bindings in this image panic instead of raising
    # ImportError, so pypdf's own fallback never fires. Nothing here is encrypted.
    sys.modules.setdefault("cryptography", None)
    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(str(body_pdf))
    pages = len(reader.pages)
    pdf = outdir / f"{name}.pdf"

    foot_html = outdir / f"{name}.footers.html"
    foot_html.write_text(render_footers(spec, pages))
    foot_pdf = outdir / f"{name}.footers.pdf"
    if chrome_pdf(chrome, foot_html, foot_pdf):
        overlay = PdfReader(str(foot_pdf))
        if len(overlay.pages) != pages:
            print(f"footer overlay has {len(overlay.pages)} pages against {pages}; "
                  f"numbering omitted rather than wrong", file=sys.stderr)
            shutil.copy(body_pdf, pdf)
        else:
            writer = PdfWriter()
            for i, page in enumerate(reader.pages):
                page.merge_page(overlay.pages[i])
                writer.add_page(page)
            with open(pdf, "wb") as fh:
                writer.write(fh)
            print(f"page numbers stamped: {pages} pages")
    else:
        shutil.copy(body_pdf, pdf)

    for tmp in (body_pdf, foot_pdf, foot_html):
        tmp.unlink(missing_ok=True)
    print(f"PDF  → {pdf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
