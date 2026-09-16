#!/usr/bin/env python3
"""
Render the price book as a printable A4 report.

Everything in the output is read from pricebook/ at run time — the report is a
view, never a second copy of the data. Regenerate it whenever a quote is added;
never edit the PDF and never treat it as the record.

Branding follows RULES C3 (A4 portrait, dark blue #1F3864, gold #C9A24E), but
the document is marked INTERNAL throughout: it carries vendor costs and must
never be mistaken for something a client can see.

Usage
-----
    python3 scripts/pricebook_report.py                    # -> out/pricebook.html
    python3 scripts/pricebook_report.py --out out/pb.html
"""

import argparse
import datetime
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from pricebook import (                                    # noqa: E402
    load_items, load_quotes, index_by_item, best_inbound, money,
    FLOOR_RULES_MD, FLOOR_MARGIN_PY, MARGIN_RATES,
)

BLUE = "#1F3864"
GOLD = "#C9A24E"

CSS = """
@page { size: A4 portrait; margin: 14mm 12mm 16mm 12mm; }
* { box-sizing: border-box; }
body { font-family: Calibri, Carlito, "DejaVu Sans", sans-serif; font-size: 8.6pt;
       color: #1a1a1a; margin: 0; }
h1 { font-size: 17pt; color: %(blue)s; margin: 0 0 2mm 0; letter-spacing: -0.2pt; }
h2 { font-size: 11pt; color: %(blue)s; margin: 7mm 0 2mm 0; padding-bottom: 1.2mm;
     border-bottom: 1.6pt solid %(gold)s; }
h2.first { margin-top: 4mm; }
h3 { font-size: 9pt; color: %(blue)s; margin: 4mm 0 1.5mm 0; }
p  { margin: 0 0 2mm 0; line-height: 1.42; }
.small { font-size: 7.6pt; color: #555; }

.letterhead { border-bottom: 2.4pt solid %(blue)s; padding-bottom: 3mm; margin-bottom: 4mm; }
.letterhead .co { font-size: 12.5pt; font-weight: bold; color: %(blue)s;
                  letter-spacing: 0.3pt; }
.letterhead .addr { font-size: 7.4pt; color: #555; margin-top: 0.8mm; }
.stamp { float: right; font-size: 7.4pt; font-weight: bold; color: #9b2c2c;
         border: 1pt solid #9b2c2c; padding: 1mm 2.5mm; letter-spacing: 0.6pt; }
.sub { color: #444; font-size: 9pt; margin-bottom: 4mm; }

table { width: 100%%; border-collapse: collapse; margin: 1.5mm 0 3mm 0; }
th { background: %(blue)s; color: #fff; font-size: 7.4pt; font-weight: bold;
     text-align: left; padding: 1.4mm 1.8mm; letter-spacing: 0.2pt; }
td { padding: 1.25mm 1.8mm; border-bottom: 0.4pt solid #dcdcdc; vertical-align: top; }
tr:nth-child(even) td { background: #f6f7f9; }
.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.mid { text-align: center; }
tfoot td { font-weight: bold; border-top: 1.2pt solid %(blue)s;
           border-bottom: 1.2pt solid %(blue)s; background: #eef1f6 !important; }

.best { color: #14663d; font-weight: bold; }
.dear { color: #8a8a8a; }
.warn { color: #9b2c2c; font-weight: bold; }
.flag { color: %(gold)s; font-weight: bold; }

.box { border-left: 2.6pt solid %(gold)s; background: #fbf8f1; padding: 2.5mm 3mm;
       margin: 2mm 0 3mm 0; }
.box.red { border-left-color: #9b2c2c; background: #fdf3f3; }
.box .lead { font-weight: bold; color: %(blue)s; }

.kpi { width: 100%%; margin: 2mm 0 3mm 0; }
.kpi td { border: none; padding: 2mm 2.5mm; background: #f2f4f8 !important;
          border-left: 2.4pt solid %(blue)s; width: 25%%; }
.kpi .lbl { font-size: 6.9pt; text-transform: uppercase; letter-spacing: 0.5pt; color: #555; }
.kpi .val { font-size: 13pt; font-weight: bold; color: %(blue)s; line-height: 1.2; }
.kpi .val.bad { color: #9b2c2c; }

.note { font-size: 7.2pt; color: #666; line-height: 1.38; }
.avoid { page-break-inside: avoid; }
.newpage { page-break-before: always; }
footer { position: fixed; bottom: -9mm; left: 0; right: 0; font-size: 6.8pt;
         color: #888; border-top: 0.4pt solid #ccc; padding-top: 1mm; }
""" % {"blue": BLUE, "gold": GOLD}


CSS_LANDSCAPE = CSS.replace("size: A4 portrait", "size: A4 landscape").replace(
    "font-size: 8.6pt", "font-size: 8.2pt")


def build_price_list(items, quotes):
    """The unit price comparison on its own — a landscape sheet to carry."""
    today = datetime.date.today().isoformat()
    inbound = [q for q in quotes if q["direction"] == "inbound"]
    idx_in = index_by_item(inbound)
    idx_all = index_by_item(quotes)

    vendors = []
    for q in inbound:
        if q["vendor"]["short"] not in vendors:
            vendors.append(q["vendor"]["short"])

    rows = []
    for key, offers in idx_in.items():
        by_vendor = {}
        for o in offers:
            cur = by_vendor.get(o["vendor"])
            if cur is None or o["unit_price"] < cur["unit_price"]:
                by_vendor[o["vendor"]] = o
        prices = [o["unit_price"] for o in by_vendor.values()]
        sell = [o for o in idx_all.get(key, []) if o["direction"] == "outbound"]
        rows.append({
            "key": key, "meta": items.get(key, {}), "by_vendor": by_vendor,
            "n": len(by_vendor), "best": min(prices),
            "spread": (max(prices) - min(prices)) / min(prices) * 100.0 if min(prices) else 0.0,
            "sell": sell[0]["unit_price"] if sell else None,
        })

    multi = sorted([r for r in rows if r["n"] > 1], key=lambda r: -r["spread"])
    single = sorted([r for r in rows if r["n"] == 1], key=lambda r: -r["best"])

    o = ['<!DOCTYPE html><html><head><meta charset="utf-8">',
         "<title>TNDK Unit Price Comparison</title><style>%s</style></head><body>" % CSS_LANDSCAPE]
    o.append("""
    <div class="letterhead">
      <div class="stamp">INTERNAL — NOT FOR CLIENTS</div>
      <div class="co">THE NEW DOHA KITCHEN EQUIPMENT SERVICES W.L.L.</div>
      <div class="addr">P.O. Box 80247, Doha, State of Qatar &nbsp;|&nbsp; Tel: 7706 0676
        &nbsp;|&nbsp; farhan@dctsqatar.com</div>
    </div>
    <h1>Unit Price Comparison</h1>
    <div class="sub">Every item we hold a quoted price for, in QAR. %d items from %d
      documents · %s</div>
    """ % (len(rows), len(quotes), today))

    def table(rs, show_spread):
        t = ["<table><tr><th>Item</th><th>Model / part</th>"]
        for v in vendors:
            t.append('<th class="num">%s</th>' % esc(v))
        t.append('<th class="num">Best</th>')
        if show_spread:
            t.append('<th class="num">Spread</th>')
        t.append('<th class="num">We sell</th><th class="num">Markup</th>'
                 '<th class="mid">Note</th></tr>')
        for r in rs:
            t.append("<tr><td><b>%s</b></td>" % esc(r["meta"].get("description", r["key"])))
            t.append('<td class="note">%s</td>' % esc(r["meta"].get("model", "—")))
            for v in vendors:
                x = r["by_vendor"].get(v)
                if x is None:
                    t.append('<td class="num dear">—</td>')
                else:
                    cls = ("num best" if abs(x["unit_price"] - r["best"]) < 0.005
                           and r["n"] > 1 else "num")
                    t.append('<td class="%s">%s</td>' % (cls, money(x["unit_price"])))
            t.append('<td class="num"><b>%s</b></td>' % money(r["best"]))
            if show_spread:
                t.append('<td class="num">%.0f%%</td>' % r["spread"])
            if r["sell"] is None:
                t.append('<td class="num dear">—</td><td class="num dear">—</td>')
            else:
                mk = (r["sell"] - r["best"]) / r["best"] * 100.0 if r["best"] else 0.0
                cls = "num warn" if mk < FLOOR_MARGIN_PY * 100 else "num"
                t.append('<td class="num">%s</td><td class="%s">%.0f%%</td>' % (
                    money(r["sell"]), cls, mk))
            t.append('<td class="mid flag">%s</td></tr>' % (
                "◆" if r["meta"].get("compare_note") else ""))
        t.append("</table>")
        return "".join(t)

    o.append("<h2 class='first'>Two or more sources — %d items</h2>" % len(multi))
    o.append('<p class="small">Sorted by spread, widest first. <b class="best">Green</b> is '
             'the cheapest source. <span class="warn">Red markup</span> is below the 20%% '
             'floor. <span class="flag">◆</span> means the sources are not strictly like for '
             "like — check the note before acting on the gap.</p>")
    o.append(table(multi, True))

    o.append('<h2 class="newpage">One source only — %d items</h2>' % len(single))
    o.append('<p class="small">No comparison is possible on these. A second quote on the '
             "plant items in particular is where the money is.</p>")
    o.append(table(single, False))

    flagged = [r for r in multi if r["meta"].get("compare_note")]
    if flagged:
        o.append("<h2>◆ Why these are not directly comparable</h2><table>")
        o.append("<tr><th>Item</th><th>Note</th></tr>")
        for r in flagged:
            o.append(row([(esc(r["meta"].get("description", r["key"])),),
                          (esc(r["meta"]["compare_note"]),)]))
        o.append("</table>")

    o.append('<p class="note">Generated %s from pricebook/ · the record is the JSON, not '
             "this PDF · vendor costs — not a client document.</p>" % today)
    o.append("</body></html>")
    return "\n".join(o)


def esc(s):
    return html.escape(str(s))


def row(cells, cls=""):
    return "<tr{}>{}</tr>".format(
        ' class="%s"' % cls if cls else "",
        "".join("<td{}>{}</td>".format(
            ' class="%s"' % c[1] if len(c) > 1 and c[1] else "", c[0]) for c in cells))


def build(items, quotes):
    today = datetime.date.today().isoformat()
    inbound = [q for q in quotes if q["direction"] == "inbound"]
    outbound = [q for q in quotes if q["direction"] == "outbound"]
    idx_all = index_by_item(quotes)
    idx_in = index_by_item(inbound)

    vendors = []
    for q in inbound:
        if q["vendor"]["short"] not in vendors:
            vendors.append(q["vendor"]["short"])

    out = ['<!DOCTYPE html><html><head><meta charset="utf-8">',
           "<title>TNDK Price Book</title><style>%s</style></head><body>" % CSS]

    # --- letterhead ---
    out.append("""
    <div class="letterhead">
      <div class="stamp">INTERNAL — NOT FOR CLIENTS</div>
      <div class="co">THE NEW DOHA KITCHEN EQUIPMENT SERVICES W.L.L.</div>
      <div class="addr">P.O. Box 80247, Doha, State of Qatar &nbsp;|&nbsp; Tel: 7706 0676
        &nbsp;|&nbsp; farhan@dctsqatar.com</div>
    </div>
    <h1>Price Book — Vendor Rate Comparison</h1>
    <div class="sub">Every quotation on record, line by line, with what we pay set against
      what we charge. Prepared by PROCURE · %s · %d documents · %d priced items</div>
    <p class="note">This report is generated from <b>pricebook/</b> and is a view of that
      record, not a second copy of it. Figures are as printed on the source documents;
      anything computed is marked. Vendor costs appear throughout — this document does not
      go to a client (RULES A2, B).</p>
    """ % (today, len(quotes), len(idx_all)))

    # --- 1. documents on record ---
    out.append('<h2 class="first">1 &nbsp; Documents on record</h2><table>')
    out.append("<tr><th>Date</th><th>Direction</th><th>Party</th><th>Reference</th>"
               '<th class="mid">Lines</th><th class="num">Stated total</th>'
               "<th>Verification</th></tr>")
    for q in sorted(quotes, key=lambda q: q["document"]["date"]):
        outb = q["direction"] == "outbound"
        stated = q.get("stated_total")
        if q.get("known_discrepancy"):
            kd = q["known_discrepancy"]
            verdict = '<span class="warn">Lines sum to %s — out by %s</span>' % (
                money(kd["lines_sum_to"]), money(kd["difference"]))
        elif stated is None:
            verdict = '<span class="flag">No total on the document</span>'
        else:
            verdict = "Verified against the document"
            if q.get("discount"):
                verdict += " (after %s discount)" % money(q["discount"])
        out.append(row([
            (q["document"]["date"],),
            ("<b>OUTBOUND</b>" if outb else "inbound",),
            (esc(q["vendor"]["name"] if not outb else
                 "→ " + q.get("client", {}).get("name", "client")),),
            (esc(q["document"].get("ref") or "— none —"),),
            (len(q["lines"]), "mid"),
            (money(stated) if stated is not None else "—", "num"),
            (verdict,),
        ]))
    out.append("</table>")

    # --- 2. margin check ---
    for sell in outbound:
        cost = sellv = 0.0
        uncosted = []
        for line in sell["lines"]:
            b = best_inbound(idx_in, line["item"])
            if b is None:
                uncosted.append(line)
                continue
            cost += b["unit_price"] * line["qty"]
            sellv += line["unit_price"] * line["qty"]
        cost, sellv = round(cost, 2), round(sellv, 2)
        profit = round(sellv - cost, 2)
        markup = profit / cost if cost else 0.0
        margin = profit / sellv if sellv else 0.0
        below = markup < max(FLOOR_RULES_MD, FLOOR_MARGIN_PY)

        out.append('<h2>2 &nbsp; Margin check — %s</h2>' % esc(sell["document"]["ref"]))
        out.append('<p class="small">%s · dated %s · cost is the cheapest inbound price on '
                   "record for each line.</p>" % (
                       esc(sell.get("client", {}).get("name", "")), sell["document"]["date"]))
        out.append('<table class="kpi"><tr>')
        for lbl, val, bad in (("Quoted", money(sell["stated_total"]), False),
                              ("Material cost", money(cost), False),
                              ("Gross profit", money(profit), False),
                              ("Markup on cost", "%.1f%%" % (markup * 100), below)):
            out.append('<td><div class="lbl">%s</div><div class="val%s">%s</div></td>'
                       % (lbl, " bad" if bad else "", val))
        out.append("</tr></table>")

        if below:
            out.append('<div class="box red"><span class="lead">Below the margin floor.</span> '
                       "%.1f%% markup against a %d%% floor in RULES.md B and %d%% in "
                       "margin.py. RULES.md B requires an owner override with a written "
                       "reason, logged — none is logged. Clearing 22%% at this cost needs "
                       "<b>QAR %s</b>, an uplift of %s.</div>" % (
                           markup * 100, FLOOR_RULES_MD * 100, FLOOR_MARGIN_PY * 100,
                           money(round(cost * 1.22, 2)),
                           money(round(cost * 1.22 - sell["stated_total"], 2))))

        out.append("<table><tr><th>Item</th><th class='mid'>Qty</th>"
                   "<th class='num'>Cost each</th><th class='num'>Sell each</th>"
                   "<th class='num'>Profit</th><th class='num'>Markup</th>"
                   "<th>Cheapest source</th></tr>")
        for line in sell["lines"]:
            meta = items.get(line["item"], {})
            b = best_inbound(idx_in, line["item"])
            if b is None:
                out.append(row([(esc(meta.get("description", line["item"])),),
                                (line["qty"], "mid"), ('<span class="flag">no price</span>', "num"),
                                (money(line["unit_price"]), "num"), ("—", "num"), ("—", "num"),
                                ('<span class="flag">not on record</span>',)]))
                continue
            c, s = b["unit_price"], line["unit_price"]
            mk = (s - c) / c * 100.0 if c else 0.0
            cls = "warn" if mk < FLOOR_MARGIN_PY * 100 else ""
            out.append(row([
                (esc(meta.get("description", line["item"])),), (line["qty"], "mid"),
                (money(c), "num"), (money(s), "num"),
                (money(round((s - c) * line["qty"], 2)), "num"),
                ('<span class="%s">%.0f%%</span>' % (cls, mk), "num"),
                (esc(b["vendor"]) + " " + b["date"],),
            ]))
        out.append("<tfoot>" + row([
            ("Costed lines",), ("", "mid"), (money(cost), "num"), (money(sellv), "num"),
            (money(profit), "num"), ("%.1f%%" % (markup * 100), "num"),
            ("margin on price %.1f%%" % (margin * 100),)]) + "</tfoot></table>")
        if uncosted:
            out.append('<p class="note">%d line(s) excluded from the arithmetic above — no '
                       "vendor price on record: %s</p>" % (
                           len(uncosted), ", ".join(
                               esc(items.get(l["item"], {}).get("description", l["item"]))
                               for l in uncosted)))

    # --- 3. rate card ---
    tied = [(k, v) for k, v in sorted(items.items()) if v.get("rate_card")]
    if tied:
        out.append('<h2 class="newpage">3 &nbsp; Estimating rate card vs real vendor prices</h2>')
        out.append('<p class="small">PROCURE escalates any divergence over 10% '
                   "(agents/procure/IDENTITY.md). Rates live in scripts/margin.py.</p>")
        out.append("<table><tr><th>Item</th><th>Rate in margin.py</th>"
                   "<th class='num'>Card</th><th class='num'>Real</th>"
                   "<th class='num'>Divergence</th><th>Source</th></tr>")
        notes = []
        for key, meta in tied:
            b = best_inbound(idx_in, key)
            rate = MARGIN_RATES.get(meta["rate_card"])
            if b is None or rate is None:
                continue
            div = (b["unit_price"] - rate) / rate * 100.0
            cls = "warn" if abs(div) > 10 else "best"
            out.append(row([
                (esc(meta["description"]),), ("<code>%s</code>" % esc(meta["rate_card"]),),
                (money(rate), "num"), (money(b["unit_price"]), "num"),
                ('<span class="%s">%+.0f%%</span>' % (cls, div), "num"),
                (esc(b["vendor"]) + " " + b["date"],)]))
            if meta.get("rate_card_note"):
                notes.append((meta["description"], meta["rate_card_note"]))
        out.append("</table>")
        for d, n in notes:
            out.append('<div class="box"><span class="lead">%s</span><br>'
                       '<span class="note">%s</span></div>' % (esc(d), esc(n)))

    # --- 4. the price list ---
    out.append('<h2 class="newpage">4 &nbsp; Unit price list — every item, every source</h2>')
    out.append('<p class="small">Inbound vendor prices in QAR. <b class="best">Green</b> is the '
               "cheapest source on record. A blank means that vendor has not quoted the item. "
               '<span class="flag">◆</span> marks an item where the sources are not strictly '
               "like for like — see section 5 before acting on the spread.</p>")

    rows = []
    for key, offers in idx_in.items():
        by_vendor = {}
        for o in offers:
            cur = by_vendor.get(o["vendor"])
            if cur is None or o["unit_price"] < cur["unit_price"]:
                by_vendor[o["vendor"]] = o
        prices = [o["unit_price"] for o in by_vendor.values()]
        meta = items.get(key, {})
        sell = [o for o in idx_all.get(key, []) if o["direction"] == "outbound"]
        rows.append({
            "key": key, "meta": meta, "by_vendor": by_vendor,
            "n": len(by_vendor), "best": min(prices),
            "spread": (max(prices) - min(prices)) / min(prices) * 100.0 if min(prices) else 0.0,
            "sell": sell[0]["unit_price"] if sell else None,
        })
    rows.sort(key=lambda r: (-r["n"], -r["spread"]))

    out.append("<table><tr><th>Item</th>")
    for v in vendors:
        out.append('<th class="num">%s</th>' % esc(v))
    out.append('<th class="num">Best</th><th class="num">Spread</th>'
               '<th class="num">We sell</th></tr>')
    for r in rows:
        cells = ['<b>%s</b>%s' % (esc(r["meta"].get("description", r["key"])),
                                 ' <span class="flag">◆</span>' if r["meta"].get("compare_note") else "")]
        line = "<tr><td>%s" % cells[0]
        if r["meta"].get("model"):
            line += '<br><span class="note">%s</span>' % esc(r["meta"]["model"])
        line += "</td>"
        for v in vendors:
            o = r["by_vendor"].get(v)
            if o is None:
                line += '<td class="num dear">—</td>'
            else:
                cls = "num best" if abs(o["unit_price"] - r["best"]) < 0.005 and r["n"] > 1 else "num"
                line += '<td class="%s">%s</td>' % (cls, money(o["unit_price"]))
        line += '<td class="num"><b>%s</b></td>' % money(r["best"])
        line += '<td class="num">%s</td>' % ("%.0f%%" % r["spread"] if r["n"] > 1 else "—")
        line += '<td class="num">%s</td>' % (money(r["sell"]) if r["sell"] else "—")
        out.append(line + "</tr>")
    out.append("</table>")

    # --- 5. not like for like ---
    flagged = [r for r in rows if r["meta"].get("compare_note")]
    if flagged:
        out.append("<h2>5 &nbsp; Not like for like — read before acting on a spread</h2>")
        out.append("<table><tr><th>Item</th><th>Why the prices are not directly comparable</th></tr>")
        for r in flagged:
            out.append(row([(esc(r["meta"].get("description", r["key"])),),
                            (esc(r["meta"]["compare_note"]),)]))
        out.append("</table>")

    # --- 6. terms ---
    out.append('<h2 class="newpage">6 &nbsp; Terms and validity on record</h2>')
    out.append("<table><tr><th>Document</th><th>Payment</th><th>Validity</th>"
               "<th>Delivery</th><th>Expires</th></tr>")
    for q in sorted(quotes, key=lambda q: q["document"]["date"]):
        t = q["terms"]
        exp = t.get("valid_until", "—")
        expired = exp != "—" and exp < today
        out.append(row([
            (esc(q["document"].get("ref") or q["vendor"]["short"]),),
            (esc(t.get("payment", "—")),),
            (esc("%s days" % t["validity_days"] if t.get("validity_days") else "—"),),
            (esc(t.get("delivery", "—")),),
            ('<span class="%s">%s</span>' % ("warn" if expired else "", exp)
             + (" (expired)" if expired else ""),),
        ]))
    out.append("</table>")

    out.append('<p class="note">Generated %s from pricebook/ · verify with '
               "<code>python3 scripts/pricebook.py --verify</code> · the record is the JSON, "
               "not this PDF.</p>" % today)
    out.append("</body></html>")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Render the price book as an A4 report")
    ap.add_argument("--out", default=os.path.join(ROOT, "out", "pricebook.html"))
    ap.add_argument("--price-list", action="store_true",
                    help="just the unit price comparison, landscape")
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    maker = build_price_list if args.price_list else build
    with open(args.out, "w") as f:
        f.write(maker(load_items(), load_quotes()))
    print(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
