#!/usr/bin/env python3
"""Build a neutral two-party contract from a JSON spec.

    python3 build_contract.py --spec contract.json --outdir out/

This is deliberately *not* a letterhead document. A contract between two
companies belongs to both of them: it carries no company header band, no house
colours and no sender's footer, because a contract that looks like one party's
stationery reads as that party's terms imposed on the other. The styling here
is the neutral register of a legal instrument — serif face, numbered clauses,
ruled headings, grey tables — and the only identity on the page is the two
parties named in the recitals and the seals at the end.

Page numbering is stamped after rendering. Chromium does not implement CSS
paged-media margin boxes, so `@bottom-center { content: counter(page) }` is
silently ignored; the footer is rendered as its own N-page overlay and merged.
An unnumbered contract is a contract from which a page can be removed without
trace, so this is not cosmetic.

No tax or VAT wording is policed here, unlike the client-facing generators:
clause 3.5 of a Qatar contract has to be able to say what happens *if* a tax is
introduced, and forbidding the word would forbid the clause.
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


def esc(v) -> str:
    return html.escape(str(v if v is not None else ""))


def rich(v) -> str:
    """Escape, then allow **bold** and *italic* — the emphasis a contract uses
    to pin a defined term — and turn a run of underscores into a ruled blank
    for a date or a seal the other Party fills in by hand. No raw HTML: the
    spec is data, and a contract is the last document that should be able to
    smuggle markup into its own text."""
    out = esc(v)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", out)
    out = re.sub(r"_{3,}", '<span class="fill"></span>', out)
    return out


CSS = """
@page { size: A4 portrait; margin: 20mm 18mm 24mm; }
* { box-sizing: border-box; }
body { font-family: Georgia,'Liberation Serif','Times New Roman',serif;
       font-size: 10pt; line-height: 1.5; color: #111; margin: 0;
       -webkit-print-color-adjust: exact; print-color-adjust: exact; }

p { margin: 0 0 3mm; text-align: justify; }

/* ---- Cover ---------------------------------------------------------- */
.cover { height: 253mm; display: flex; flex-direction: column;
         justify-content: center; text-align: center; padding: 0 10mm; }
.cover__rule { border-top: .6mm solid #111; border-bottom: .2mm solid #111;
               height: 1.6mm; margin: 0 auto 10mm; width: 60mm; }
.cover__kicker { font-size: 9pt; letter-spacing: .32em; text-transform: uppercase;
                 color: #555; margin-bottom: 5mm; }
.cover__title { font-size: 26pt; font-weight: 700; letter-spacing: .14em;
                text-transform: uppercase; margin: 0 0 7mm; }
.cover__works { font-size: 12pt; line-height: 1.5; margin: 0 auto 10mm;
                max-width: 140mm; text-align: center; }
.cover__meta { font-size: 10pt; margin-bottom: 11mm; }
.cover__meta div { margin-bottom: 1.6mm; }
.cover__between { font-size: 9pt; letter-spacing: .3em; text-transform: uppercase;
                  color: #555; margin: 5mm 0 3mm; }
.cover__party { font-size: 13pt; font-weight: 700; line-height: 1.35; }
.cover__party span { display: block; font-size: 9pt; font-weight: 400;
                     letter-spacing: .16em; text-transform: uppercase;
                     color: #555; margin-top: 1.2mm; }
.cover__foot { margin-top: 13mm; font-size: 9pt; color: #444; font-style: italic;
               line-height: 1.6; }

/* ---- Headings ------------------------------------------------------- */
h2 { font-size: 10.5pt; font-weight: 700; letter-spacing: .09em;
     text-transform: uppercase; margin: 7mm 0 2.5mm; padding-bottom: 1.2mm;
     border-bottom: .35mm solid #111; break-after: avoid; }
h2 .n { margin-right: 3mm; }
h3 { font-size: 11pt; font-weight: 700; letter-spacing: .12em;
     text-transform: uppercase; text-align: center; margin: 0 0 4mm;
     padding-bottom: 2mm; border-bottom: .35mm solid #111; break-after: avoid; }

/* ---- Lists ---------------------------------------------------------- */
ol, ul { margin: 0 0 3mm; padding-left: 7mm; }
ol.lower-alpha { list-style: lower-alpha; }
li { margin-bottom: 1.8mm; text-align: justify; }
li::marker { color: #111; }

/* ---- Tables --------------------------------------------------------- */
table { width: 100%; border-collapse: collapse; margin: 0 0 4mm;
        font-size: 9.5pt; }
th { background: #E8E8E8; color: #111; font-weight: 700; text-align: left;
     padding: 1.8mm 2.2mm; border: .25mm solid #777;
     font-size: 8.6pt; letter-spacing: .05em; text-transform: uppercase; }
td { border: .25mm solid #999; padding: 1.8mm 2.2mm; vertical-align: top; }
td.num { text-align: right; white-space: nowrap; }
td.ctr { text-align: center; }
tr.sum td { background: #F2F2F2; font-weight: 700; }
tr.tot td { background: #DCDCDC; font-weight: 700; font-size: 10pt; }
table.kv td.k { background: #F2F2F2; font-weight: 700; width: 46mm; }

/* ---- Parties -------------------------------------------------------- */
table.parties { table-layout: fixed; }
table.parties th { text-align: center; }
table.parties td { padding: 3mm 3.4mm; font-size: 9.5pt; line-height: 1.45; }
.pname { font-weight: 700; font-size: 10.5pt; display: block; margin-bottom: 1.6mm; }
.palias { display: block; margin-top: 2.6mm; }

/* ---- Note box ------------------------------------------------------- */
.note { border: .25mm solid #999; border-left: 1.2mm solid #111; background: #F7F7F7;
        padding: 2.6mm 3.4mm; margin: 0 0 4mm; font-size: 9.5pt; }
.note p:last-child { margin-bottom: 0; }

/* ---- Execution ------------------------------------------------------ */
.exec { margin-top: 5mm; }
table.exec__t { table-layout: fixed; }
table.exec__t td { padding: 0; vertical-align: top; }
.sigbox { padding: 3.4mm; min-height: 62mm; }
.sigbox__h { font-weight: 700; font-size: 8.6pt; letter-spacing: .07em;
             text-transform: uppercase; border-bottom: .25mm solid #111;
             padding-bottom: 1.6mm; margin-bottom: 3mm; }
.sigbox__art { height: 36mm; position: relative; }
.sigbox__art img { max-height: 36mm; max-width: 72mm; position: absolute;
                   left: 0; bottom: 0; }
.sigbox__line { border-top: .25mm solid #111; margin-bottom: 2.2mm; }
.sigbox__name { font-weight: 700; font-size: 10pt; }
.sigbox__d { font-size: 9.5pt; line-height: 1.5; }
.fill { display: inline-block; border-bottom: .2mm solid #555; min-width: 40mm;
        height: 3.4mm; }
.initials { margin-top: 4mm; font-size: 8.5pt; color: #444; font-style: italic; }

.pagebreak { break-before: page; }
.keep { break-inside: avoid; }
"""

FOOTER_CSS = """
@page { size: A4 portrait; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; font-family: Georgia,'Liberation Serif','Times New Roman',serif;
       color: #333; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.pg { height: %(h)smm; position: relative; break-after: page; }
.pg:last-child { break-after: auto; }
.ft { position: absolute; left: 18mm; right: 18mm; bottom: 12mm;
      border-top: .2mm solid #BBB; padding-top: 1.6mm;
      display: flex; justify-content: space-between; font-size: 7.6pt; }
.ft .i { color: #666; }
""" % {"h": PAGE_H_MM}


# --------------------------------------------------------------------------
# Block renderers
# --------------------------------------------------------------------------

def r_para(b, spec):
    return f"<p>{rich(b['text'])}</p>"


def r_heading(b, spec):
    return f"<h3>{rich(b['text'])}</h3>"


def r_clause(b, spec):
    head = (f'<h2><span class="n">{esc(b["no"])}.</span>{rich(b["title"])}</h2>'
            if b.get("no") else f'<h2>{rich(b["title"])}</h2>')
    body = ""
    if b.get("lead"):
        body += f"<p>{rich(b['lead'])}</p>"
    if b.get("items"):
        lis = "".join(f"<li>{rich(i)}</li>" for i in b["items"])
        cls = ' class="lower-alpha"' if b.get("alpha") else ""
        body += f"<ol{cls}>{lis}</ol>"
    if b.get("tail"):
        body += f"<p>{rich(b['tail'])}</p>"
    return head + body


def r_list(b, spec):
    lis = "".join(f"<li>{rich(i)}</li>" for i in b["items"])
    cls = ' class="lower-alpha"' if b.get("alpha") else ""
    # `start` matters: where a clause opens with a lead sentence, that sentence
    # is sub-clause 1 and the list continues from 2. Restarting at 1 silently
    # renumbers every sub-clause and breaks the cross-references that point at
    # them — clause 14.3 cites clause 4.4 by number.
    start = f' start="{int(b["start"])}"' if b.get("start") else ""
    lead = f"<p>{rich(b['lead'])}</p>" if b.get("lead") else ""
    return f"{lead}<ol{cls}{start}>{lis}</ol>"


def _cells(row, aligns, tag="td"):
    out = []
    for i, c in enumerate(row):
        a = aligns[i] if i < len(aligns) else ""
        cls = f' class="{a}"' if a and tag == "td" else ""
        out.append(f"<{tag}{cls}>{rich(c)}</{tag}>")
    return "".join(out)


def r_table(b, spec):
    aligns = b.get("align", [])
    widths = b.get("widths", [])
    cols = "".join(f'<col style="width:{w}">' for w in widths) if widths else ""
    head = f"<thead><tr>{_cells(b['head'], [], 'th')}</tr></thead>" if b.get("head") else ""
    rows = "".join(f"<tr>{_cells(r, aligns)}</tr>" for r in b.get("rows", []))
    for r in b.get("sum_rows", []):
        rows += f'<tr class="sum">{_cells(r, aligns)}</tr>'
    for r in b.get("total_rows", []):
        rows += f'<tr class="tot">{_cells(r, aligns)}</tr>'
    cls = "kv" if b.get("kv") else ""
    if b.get("kv"):
        rows = "".join(f'<tr><td class="k">{rich(k)}</td><td>{rich(v)}</td></tr>'
                       for k, v in b["rows"])
    lead = f"<p>{rich(b['lead'])}</p>" if b.get("lead") else ""
    return (f'{lead}<table class="{cls}">{cols}{head}<tbody>{rows}</tbody></table>')


def r_note(b, spec):
    inner = "".join(f"<p>{rich(p)}</p>" for p in b["items"]) if b.get("items") \
        else f"<p>{rich(b['text'])}</p>"
    return f'<div class="note">{inner}</div>'


def r_pagebreak(b, spec):
    return '<div class="pagebreak"></div>'


def r_parties(b, spec):
    cells = []
    for p in spec["parties"]:
        lines = "".join(f"<div>{rich(l)}</div>" for l in p["lines"])
        cells.append(f'<td><span class="pname">{rich(p["name"])}</span>{lines}'
                     f'<span class="palias">{rich(p["alias"])}</span></td>')
    heads = "".join(f"<th>{rich(p['role'])}</th>" for p in spec["parties"])
    return (f'<table class="parties"><thead><tr>{heads}</tr></thead>'
            f'<tbody><tr>{"".join(cells)}</tr></tbody></table>')


def r_execution(b, spec):
    e = spec["execution"]
    boxes = []
    for s in e["signatories"]:
        art = ""
        if s.get("image"):
            art = f'<img src="{esc(s["image"])}" alt="">'
        details = "".join(f"<div>{rich(d)}</div>" for d in s["details"])
        boxes.append(
            f'<td><div class="sigbox"><div class="sigbox__h">{rich(s["heading"])}</div>'
            f'<div class="sigbox__art">{art}</div>'
            f'<div class="sigbox__line"></div>'
            f'<div class="sigbox__name">{rich(s["name"])}</div>'
            f'<div class="sigbox__d">{details}</div></div></td>')
    return (f'<div class="exec keep"><p>{rich(e["attestation"])}</p>'
            f'<table class="exec__t"><tbody><tr>{"".join(boxes)}</tr></tbody></table>'
            f'<p class="initials">{rich(e["note"])}</p></div>')


def r_cover(b, spec):
    c = spec["cover"]
    meta = "".join(f"<div>{rich(m)}</div>" for m in c["meta"])
    parties = ""
    for i, p in enumerate(spec["parties"]):
        if i:
            parties += '<div class="cover__between">and</div>'
        parties += (f'<div class="cover__party">{rich(p["name"])}'
                    f'<span>{rich(p["role"])}</span></div>')
    return (f'<div class="cover"><div class="cover__kicker">{rich(c["kicker"])}</div>'
            f'<div class="cover__title">{rich(c["title"])}</div>'
            f'<div class="cover__rule"></div>'
            f'<div class="cover__works">{rich(c["works"])}</div>'
            f'<div class="cover__meta">{meta}</div>'
            f'<div class="cover__between">between</div>{parties}'
            f'<div class="cover__foot">{rich(c["foot"])}</div></div>'
            f'<div class="pagebreak"></div>')


RENDERERS = {
    "cover": r_cover, "para": r_para, "heading": r_heading, "clause": r_clause,
    "list": r_list, "table": r_table, "note": r_note, "pagebreak": r_pagebreak,
    "parties": r_parties, "execution": r_execution,
}


def verify(spec: dict) -> list[str]:
    """Check the arithmetic the contract states about itself.

    A priced contract that does not add up is unenforceable in the part that
    matters, and the sub-total/discount/price chain is exactly where a late
    edit goes wrong.
    """
    problems: list[str] = []
    money = spec.get("check_money")
    if money:
        lines = [float(x) for x in money["lines"]]
        sub = round(sum(lines), 2)
        if abs(sub - float(money["subtotal"])) > 0.01:
            problems.append(f"line items sum to {sub:,.2f}, sub-total states "
                            f"{float(money['subtotal']):,.2f}")
        price = round(float(money["subtotal"]) - float(money.get("discount", 0)), 2)
        if abs(price - float(money["price"])) > 0.01:
            problems.append(f"sub-total less discount is {price:,.2f}, contract price "
                            f"states {float(money['price']):,.2f}")
    stages = spec.get("check_stages")
    if stages:
        pct = round(sum(float(s[0]) for s in stages), 4)
        amt = round(sum(float(s[1]) for s in stages), 2)
        if abs(pct - 100.0) > 0.01:
            problems.append(f"payment stages sum to {pct}%, not 100%")
        if money and abs(amt - float(money["price"])) > 0.01:
            problems.append(f"payment stages sum to {amt:,.2f}, contract price "
                            f"{float(money['price']):,.2f}")
    return problems


def render(spec: dict) -> str:
    body = "".join(RENDERERS[b["type"]](b, spec) for b in spec["blocks"])
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<title>{esc(spec.get("reference",""))}</title>'
            f"<style>{CSS}</style></head><body>{body}</body></html>")


def render_footers(spec: dict, pages: int, skip_first: bool) -> str:
    ref = esc(spec.get("reference", ""))
    left = esc(spec.get("footer_left", ref))
    divs = []
    for n in range(1, pages + 1):
        inner = ""
        if not (skip_first and n == 1):
            inner = (f'<div class="ft"><span>{left}</span>'
                     f'<span class="i">{esc(spec.get("footer_initials",""))}</span>'
                     f'<span>Page {n} of {pages}</span></div>')
        divs.append(f'<div class="pg">{inner}</div>')
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
        print("REFUSING TO BUILD — the contract does not reconcile:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 2
    print("money verified: line items, sub-total, discount, price, payment stages")

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

    # The broken cryptography bindings in this image panic on import rather
    # than raising ImportError, so pypdf's own fallback never fires. Blocking
    # the module makes that fallback work; nothing here is encrypted.
    sys.modules.setdefault("cryptography", None)
    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(str(body_pdf))
    pages = len(reader.pages)

    foot_html = outdir / f"{name}.footers.html"
    foot_html.write_text(render_footers(spec, pages, spec.get("cover_has_no_footer", True)))
    foot_pdf = outdir / f"{name}.footers.pdf"
    pdf = outdir / f"{name}.pdf"

    if chrome_pdf(chrome, foot_html, foot_pdf):
        overlay = PdfReader(str(foot_pdf))
        if len(overlay.pages) != pages:
            print(f"footer overlay has {len(overlay.pages)} pages against {pages} "
                  f"in the contract — numbering would be wrong, so it is omitted",
                  file=sys.stderr)
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
