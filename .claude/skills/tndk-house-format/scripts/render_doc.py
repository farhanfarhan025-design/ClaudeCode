#!/usr/bin/env python3
"""TNDK house-format document renderer.

One layout, every accounts document. JSON in, branded A4 PDF out — LPO, invoice,
receipt, delivery note, delivery return, and anything else that is a header, a party
block, a line table and a money block.

    python3 render_doc.py job.json --outdir out/

The geometry is not invented here. It is measured from the approved LPO-194/2026 and
recorded in references/format-spec.md: navy #1F3864, gold #C9A24E, panel #EEF2F8,
grid #C9CDD6, Arial 9.5pt body, A4 with a 27pt content margin and a full-bleed header.

Three checks run before a PDF is written, because a document that looks right and is
wrong is worse than no document:

  * the word "tax"/"VAT" anywhere on the page raises — TNDK invoices never carry one
  * line totals must sum to the sub-total, and sub-total - discount to the grand total
  * the amount in words must match the grand total

Each raises rather than warns. A wrong total on an issued document costs more than a
failed run.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

# --------------------------------------------------------------------- brand

NAVY = "#1F3864"
GOLD = "#C9A24E"
PANEL = "#EEF2F8"
GRID = "#C9CDD6"
INK = "#222222"
INK_SOFT = "#333333"

# Column widths as measured off the approved LPO, in % of the 540.8pt content width.
COLS = {
    "sn": 4.59,
    "description": 50.89,
    "unit": 6.93,
    "qty": 6.93,
    "rate": 17.48,
    "amount": 13.18,
}

DEFAULT_COMPANY = {
    "name": "THE NEW DOHA KITCHEN COMPANY",
    "address": "P.O. Box 80247, Doha, Qatar | info@dkeqatar.com",
    "footer": "The New Doha Kitchen Company  |  P.O. Box 80247, Doha, Qatar | info@dkeqatar.com",
}

# --------------------------------------------------------- document contracts
#
# Each type differs in four ways only: what the badge says, what the party block is
# called, what the meta strip is labelled, and how it is signed. Everything else is
# shared — which is the whole point of a house format.

TYPES = {
    "lpo": {
        "badge": ["LOCAL PURCHASE", "ORDER"],
        "party": "VENDOR INFORMATION",
        "meta": ["PO NUMBER", "DATE", "REF QUOTE"],
        "counterparty": "VENDOR",
        "money": True,
        "sign": "computer",
        "callout": "This Purchase Order is system-generated and is valid without a physical signature.",
    },
    "invoice": {
        "badge": ["INVOICE"],
        "party": "BILL TO",
        "meta": ["INVOICE NO", "DATE", "REF"],
        "counterparty": "CLIENT",
        "money": True,
        "sign": "accountant",
        "payee": True,
    },
    "receipt": {
        "badge": ["RECEIPT"],
        "party": "RECEIVED FROM",
        "meta": ["RECEIPT NO", "DATE", "AGAINST INVOICE"],
        "counterparty": "CLIENT",
        "money": True,
        "sign": "accountant",
        "instrument": True,
    },
    "delivery_note": {
        "badge": ["DELIVERY", "NOTE"],
        "party": "DELIVER TO",
        "meta": ["DN NUMBER", "DATE", "REF LPO"],
        "counterparty": "CLIENT",
        "money": False,
        "sign": "two-party",
        "sign_labels": ("Delivered by (TNDK)", "Received by (Client)"),
    },
    "delivery_return": {
        "badge": ["DELIVERY", "RETURN"],
        "party": "RETURNED FROM",
        "meta": ["RETURN NO", "DATE", "AGAINST DN"],
        "counterparty": "CLIENT",
        "money": False,
        "sign": "two-party",
        "sign_labels": ("Returned by", "Received back by (TNDK)"),
        "reason_column": True,
    },
}

# --------------------------------------------------------------------- helpers

ONES = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
        "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen",
        "Eighteen", "Nineteen"]
TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]


def words(n):
    n = int(n)
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + (" " + ONES[n % 10] if n % 10 else "")
    for div, name in ((1_000_000_000, "Billion"), (1_000_000, "Million"), (1000, "Thousand"), (100, "Hundred")):
        if n >= div:
            rest = n % div
            return words(n // div) + f" {name}" + (" " + words(rest) if rest else "")
    return ""


def amount_in_words(total, currency="QAR"):
    """'Nine Thousand Five Hundred Qatari Riyals Only (QAR 9,500.00)'"""
    unit = {"QAR": ("Qatari Riyals", "Halalas")}.get(currency, (currency, "Cents"))
    riyals = int(round(total * 100)) // 100
    sub = int(round(total * 100)) % 100
    text = words(riyals) or "Zero"
    out = f"{text} {unit[0]}"
    if sub:
        out += f" and {words(sub)} {unit[1]}"
    return f"{out} Only ({currency} {total:,.2f})"


def money(n):
    """Negatives in parentheses, accounting style — a standing convention."""
    return f"({abs(n):,.2f})" if n < 0 else f"{n:,.2f}"


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if s is not None else "")


class DocumentError(Exception):
    """Raised when a document would go out wrong. Never downgraded to a warning."""


# --------------------------------------------------------------------- checks


def check_arithmetic(doc, lines, subtotal, discount, grand, adjustments=0):
    computed = sum(l.get("amount", 0) for l in lines)
    if abs(computed - subtotal) > 0.005:
        raise DocumentError(
            f"Line totals sum to {money(computed)} but the sub-total says {money(subtotal)}. "
            f"Difference {money(abs(computed - subtotal))}. Fix the source, not the total.")
    expected_grand = subtotal - discount + adjustments
    if abs(expected_grand - grand) > 0.005:
        adj = f" plus adjustments {money(adjustments)}" if adjustments else ""
        raise DocumentError(
            f"Sub-total {money(subtotal)} less discount {money(discount)}{adj} is "
            f"{money(expected_grand)}, but the grand total says {money(grand)}.")
    stated = doc.get("amount_in_words")
    if stated:
        expected = amount_in_words(grand, doc.get("currency", "QAR"))
        if re.sub(r"\s+", " ", stated.strip().lower()) != expected.lower():
            raise DocumentError(
                f"Amount in words does not match the grand total.\n  given:    {stated}\n"
                f"  computed: {expected}\nOne of them is wrong — check which before issuing.")


def check_no_tax(html):
    """RULES.md A1. The generator throws on violation; that is deliberate — keep it."""
    text = re.sub(r"<[^>]+>", " ", html)
    hit = re.search(r"\b(tax|taxes|taxable|vat)\b", text, re.I)
    if hit:
        line = text[max(0, hit.start() - 60):hit.end() + 60].strip()
        raise DocumentError(
            f'The word "{hit.group(0)}" appears on this document: "…{line}…"\n'
            "TNDK documents never carry a tax or VAT line. Remove it, or if this is a "
            "genuine change of policy, that is Farhan's ruling to make and record first.")


# ----------------------------------------------------------------------- HTML


def build_html(doc):
    kind = doc.get("type", "").lower()
    if kind not in TYPES:
        raise DocumentError(f"Unknown document type '{kind}'. Known: {', '.join(sorted(TYPES))}")
    spec = TYPES[kind]
    company = {**DEFAULT_COMPANY, **doc.get("company", {})}
    currency = doc.get("currency", "QAR")
    show_money = spec["money"] and doc.get("show_prices", True)

    lines = []
    for raw in doc.get("lines", []):
        line = dict(raw)
        if show_money and "amount" not in line:
            line["amount"] = round(line.get("qty", 0) * line.get("rate", 0), 2)
        lines.append(line)

    subtotal = doc.get("subtotal", round(sum(l.get("amount", 0) for l in lines), 2))
    discount = doc.get("discount", 0) or 0
    adjustments = round(sum(a.get("amount", 0) for a in doc.get("adjustments", [])), 2)
    grand = doc.get("grand_total", round(subtotal - discount + adjustments, 2))
    if show_money:
        check_arithmetic(doc, lines, subtotal, discount, grand, adjustments)

    # ---- header, meta strip
    labels = spec["badge"]
    badge = "<br/>".join(f'<span class="b{i if len(labels) > 1 else 1}">{esc(t)}</span>'
                         for i, t in enumerate(labels))
    meta_labels = doc.get("meta_labels", spec["meta"])
    meta_values = [doc.get("number", ""), doc.get("date", ""), doc.get("ref", "")]
    meta = " &nbsp;&nbsp;&nbsp; ".join(
        f'<b>{esc(l)}:</b>&nbsp;{esc(v)}' for l, v in zip(meta_labels, meta_values) if v)

    party_name = doc.get("party", {}).get("name", "")
    counterparty = doc.get("counterparty_label", spec["counterparty"])

    # ---- party block
    rows = []
    for field in doc.get("party", {}).get("fields", []):
        if isinstance(field, dict):
            rows.append(f'<div><b>{esc(field.get("label"))}:</b> {esc(field.get("value"))}</div>')
        else:
            rows.append(f"<div>{esc(field)}</div>")
    party_rows = "\n".join(rows)

    # ---- line table
    reason = spec.get("reason_column") or doc.get("reason_column")
    head = [("S/N", COLS["sn"], "c"), ("DESCRIPTION", COLS["description"], "c")]
    if reason:
        head.append(("REASON", 14.0, "l"))
    head += [("UNIT", COLS["unit"], "c"), ("QTY", COLS["qty"], "c")]
    if show_money:
        head += [(f"UNIT PRICE<br/>({currency})", COLS["rate"], "r"),
                 (f"TOTAL<br/>({currency})", COLS["amount"], "r")]

    total_w = sum(h[1] for h in head)
    ths = "".join(f'<th style="width:{w / total_w * 100:.2f}%" class="{a}">{t}</th>'
                  for t, w, a in head)

    trs = []
    for i, line in enumerate(lines, 1):
        cells = [f'<td class="c sn">{i}</td>',
                 f'<td class="l desc">{esc(line.get("description"))}</td>']
        if reason:
            cells.append(f'<td class="l">{esc(line.get("reason", ""))}</td>')
        cells += [f'<td class="c">{esc(line.get("unit", "Nos"))}</td>',
                  f'<td class="c">{esc(line.get("qty", ""))}</td>']
        if show_money:
            cells += [f'<td class="r">{money(line.get("rate", 0))}</td>',
                      f'<td class="r">{money(line.get("amount", 0))}</td>']
        trs.append("<tr>" + "".join(cells) + "</tr>")

    # ---- money block
    money_block = ""
    if show_money:
        rows_html = [f'<tr><td class="fill"></td><td class="mlabel">Sub-Total:</td>'
                     f'<td class="mval">{money(subtotal)}</td></tr>']
        if discount:
            rows_html.append(f'<tr><td class="fill"></td><td class="mlabel">Discount:</td>'
                             f'<td class="mval">({money(discount)})</td></tr>')
        for extra in doc.get("adjustments", []):
            rows_html.append(f'<tr><td class="fill"></td>'
                             f'<td class="mlabel">{esc(extra["label"])}:</td>'
                             f'<td class="mval">{money(extra["amount"])}</td></tr>')
        label = doc.get("grand_total_label", "GRAND TOTAL")
        rows_html.append(f'<tr class="grand"><td class="fill"></td>'
                         f'<td class="mlabel">{esc(label)}:</td>'
                         f'<td class="mval">{money(grand)}</td></tr>')
        money_block = f'<table class="money">{"".join(rows_html)}</table>'

        aiw = doc.get("amount_in_words") or amount_in_words(grand, currency)
        money_block += f'<div class="words"><b>Amount in Words:</b>&nbsp; {esc(aiw)}</div>'

    # ---- receipt instrument block (RULES.md C7)
    instrument = ""
    if spec.get("instrument"):
        inst = doc.get("instrument")
        if not inst:
            raise DocumentError(
                "A receipt needs its payment instrument — cheque no. + bank + date + drawer, "
                "transfer ref + bank + date, or Payment Mode: Cash. A receipt without one is "
                "a received amount nobody can trace (RULES.md C7).")
        bits = [f'<div><b>{esc(k.replace("_", " ").title())}:</b> {esc(v)}</div>'
                for k, v in inst.items() if k != "type"]
        note = ('<div class="realis"><i>Subject to realization of cheque.</i></div>'
                if inst.get("type", "").lower() == "cheque" else "")
        instrument = (f'<div class="sect">PAYMENT INSTRUMENT</div>'
                      f'<div class="party">{"".join(bits)}{note}</div>')

    # ---- notes
    notes = ""
    if doc.get("notes"):
        items = "".join(f"<div>{i}. {esc(n)}</div>" for i, n in enumerate(doc["notes"], 1))
        notes = f'<div class="notes"><b><i>Notes:</i></b><div class="nlist">{items}</div></div>'

    # ---- payee line (invoices), exact wording — a standing correction
    payee = ""
    if spec.get("payee") and doc.get("show_payee", True):
        payee = ('<div class="payee">Cheque should be prepared under the name of: '
                 '<b>The New Doha Kitchen Equipment and Services</b></div>')

    # ---- signature
    if spec["sign"] == "computer":
        callout = spec.get("callout", "")
        sign = (f'<div class="callout"><div class="cg">*** COMPUTER GENERATED DOCUMENT ***</div>'
                f'<div class="cgs">{esc(callout)}</div></div>')
    elif spec["sign"] == "accountant":
        sign = ('<div class="sigwrap"><div class="sig">'
                '<div class="sigline"></div><div class="signame">Ronaldo / Accountant</div>'
                '<div class="sigco">For The New Doha Kitchen Company</div></div></div>')
    else:
        left, right = spec.get("sign_labels", ("Delivered by", "Received by"))
        sign = (f'<table class="sig2"><tr>'
                f'<td><div class="sigline"></div><div class="signame">{esc(left)}</div>'
                f'<div class="sigco">Name / Signature / Date</div></td><td class="gap"></td>'
                f'<td><div class="sigline"></div><div class="signame">{esc(right)}</div>'
                f'<div class="sigco">Name / Signature / Date</div></td></tr></table>')

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{esc(doc.get('number', ''))}</title>
<style>
  @page {{ size: A4; margin: 0; }}
  * {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  body {{ font-family: Arial, "Liberation Sans", Helvetica, sans-serif;
          font-size: 9.5pt; color: {INK}; margin: 0; }}
  .band {{ background: {NAVY}; color: #FFFFFF; padding: 13pt 27pt 11pt 27pt; }}
  .band .co {{ font-size: 17pt; font-weight: bold; }}
  .band .ad {{ font-size: 9pt; }}
  .badge {{ background: {GOLD}; color: {NAVY}; text-align: center; width: 123pt;
            padding: 8pt 0; font-weight: bold; line-height: 1.25; }}
  .badge .b0 {{ font-size: 10pt; }}
  .badge .b1 {{ font-size: 14pt; }}
  .rule {{ background: {GOLD}; height: 4pt; font-size: 1pt; }}
  .meta {{ background: {PANEL}; padding: 6pt 27pt; font-size: 9.5pt; }}
  .wrap {{ padding: 0 27pt; }}
  .sect {{ background: {NAVY}; color: #FFFFFF; font-weight: bold; font-size: 10.5pt;
           padding: 5pt 12pt; margin-top: 12pt; }}
  .party {{ padding: 6pt 12pt 2pt 12pt; line-height: 1.45; }}
  table.items {{ width: 100%; border-collapse: collapse; margin-top: 16pt; }}
  table.items th {{ background: {NAVY}; color: #FFFFFF; font-size: 9.5pt; padding: 6pt 5pt;
                    border: 0.6pt solid {GRID}; }}
  table.items td {{ border: 0.6pt solid {GRID}; padding: 5pt; font-size: 9.5pt;
                    vertical-align: top; }}
  table.items td.desc {{ font-weight: bold; }}
  .l {{ text-align: left; }} .c {{ text-align: center; }} .r {{ text-align: right; }}
  table.money {{ width: 100%; border-collapse: collapse; margin-top: 6pt; }}
  table.money td {{ padding: 3pt 5pt; font-weight: bold; }}
  table.money td.fill {{ width: 69.3%; }}
  table.money td.mlabel {{ text-align: right; width: 17.6%; white-space: nowrap; }}
  table.money td.mval {{ text-align: right; width: 13.2%; }}
  table.money tr.grand td {{ font-size: 11pt; color: {NAVY}; padding: 5pt 5pt; }}
  table.money tr.grand td.fill {{ background: {PANEL}; }}
  table.money tr.grand td.mval {{ background: {PANEL}; }}
  .words {{ background: {PANEL}; padding: 6pt 12pt; margin-top: 8pt; }}
  .payee {{ padding: 8pt 12pt 0 12pt; }}
  .notes {{ margin-top: 10pt; font-size: 8.5pt; font-style: italic; color: {INK_SOFT}; }}
  .notes b {{ color: {NAVY}; }}
  .notes .nlist {{ padding-left: 8pt; }}
  .realis {{ font-size: 8.5pt; color: {INK_SOFT}; padding-top: 3pt; }}
  .callout {{ background: {PANEL}; border: 0.8pt solid {GOLD}; text-align: center;
              padding: 9pt; margin-top: 14pt; }}
  .callout .cg {{ color: {NAVY}; font-weight: bold; font-size: 10.5pt; }}
  .callout .cgs {{ font-size: 9pt; color: {INK_SOFT}; }}
  .sigwrap {{ margin-top: 30pt; text-align: right; }}
  .sig {{ display: inline-block; width: 210pt; text-align: center; }}
  table.sig2 {{ width: 100%; margin-top: 34pt; }}
  table.sig2 td {{ width: 44%; text-align: center; }}
  table.sig2 td.gap {{ width: 12%; }}
  .sigline {{ border-top: 0.8pt solid {INK}; height: 1pt; font-size: 1pt; }}
  .signame {{ font-weight: bold; padding-top: 3pt; }}
  .sigco {{ font-size: 8.5pt; color: {INK_SOFT}; }}
  .footwrap {{ position: fixed; bottom: 0; left: 0; right: 0; }}
  .foot {{ background: {NAVY}; color: #FFFFFF; text-align: center; padding: 7pt 27pt;
           font-size: 8.5pt; }}
  .tail {{ height: 46pt; }}   /* keeps content clear of the fixed footer */
  .foot .f2 {{ font-style: italic; }}
</style></head><body>

<table width="100%" cellpadding="0" cellspacing="0" class="band"><tr>
  <td><div class="co">{esc(company['name'])}</div>
      <div class="ad">{esc(company['address'])}</div></td>
  <td width="42%" align="right"><div class="badge">{badge}</div></td>
</tr></table>
<div class="rule"></div>
<div class="meta">{meta}<br/><b>{esc(counterparty)}:</b>&nbsp; {esc(party_name)}</div>

<div class="wrap">
  <div class="sect">{esc(doc.get('party', {}).get('title', spec['party']))}</div>
  <div class="party">{party_rows}</div>

  <table class="items"><tr>{ths}</tr>{''.join(trs)}</table>
  {money_block}
  {instrument}
  {payee}
  {notes}
  {sign}
</div>

<div class="tail"></div>
<div class="footwrap"><div class="rule"></div>
  <div class="foot"><b>{esc(company['footer'])}</b>
    <div class="f2">This is a computer-generated document and does not require a physical signature.</div>
  </div>
</div>
</body></html>"""

    check_no_tax(html)
    return html


# ----------------------------------------------------------------------- main


def find_chromium():
    """Chrome's print-to-pdf gives the closest match to the approved document."""
    for env in ("CHROME_BIN", "CHROMIUM_BIN"):
        if os.environ.get(env) and os.path.exists(os.environ[env]):
            return os.environ[env]
    for name in ("chromium", "chromium-browser", "google-chrome", "chrome"):
        found = shutil.which(name)
        if found:
            return found
    root = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
    if os.path.isdir(root):
        for dirpath, _, files in os.walk(root):
            for candidate in ("chrome", "headless_shell"):
                if candidate in files:
                    return os.path.join(dirpath, candidate)
    return None


def to_pdf(html_path, outdir):
    """Chromium first, LibreOffice second. Both are checked so the same JSON renders
    the same document wherever it runs — a house format that only works on one machine
    is not a house format."""
    out = os.path.join(outdir, os.path.splitext(os.path.basename(html_path))[0] + ".pdf")

    chrome = find_chromium()
    if chrome:
        subprocess.run(
            [chrome, "--headless", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
             f"--print-to-pdf={out}", "file://" + os.path.abspath(html_path)],
            capture_output=True, timeout=180)
        if os.path.exists(out):
            return out

    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice:
        subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", outdir,
                        html_path], capture_output=True, timeout=240)
        if os.path.exists(out):
            return out

    raise DocumentError(
        "No HTML-to-PDF backend worked. Install Chromium (preferred) or LibreOffice, or set "
        "CHROME_BIN. The HTML itself is valid — render it in any browser's print-to-PDF as a "
        "fallback, A4 with margins off.")


def main():
    ap = argparse.ArgumentParser(description="Render a TNDK document in the house format")
    ap.add_argument("data", help="JSON document definition — see assets/")
    ap.add_argument("--outdir", default=".", help="where the PDF lands")
    ap.add_argument("--keep-html", action="store_true", help="keep the intermediate HTML")
    args = ap.parse_args()

    doc = json.load(open(args.data))
    try:
        html = build_html(doc)
    except DocumentError as e:
        print(f"REFUSED — {e}", file=sys.stderr)
        return 2

    os.makedirs(args.outdir, exist_ok=True)
    name = (doc.get("filename")
            or f"{doc.get('type', 'document')}_{doc.get('number', '')}".replace("/", "-"))
    tmp = tempfile.mkdtemp()
    html_path = os.path.join(args.outdir if args.keep_html else tmp, name + ".html")
    with open(html_path, "w") as fh:
        fh.write(html)

    pdf = to_pdf(html_path, args.outdir)
    print(f"{doc.get('type')} {doc.get('number', '')} -> {pdf}")
    print("Verify before it goes anywhere: totals reconcile, numbering log updated, "
          "no 'tax' (checked), signature correct for the document type.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
