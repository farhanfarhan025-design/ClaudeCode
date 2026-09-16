#!/usr/bin/env python3
"""
TNDK price book — capture, verify and compare quoted rates over time.

Why this exists
---------------
`memory/open_loops.md` OL-009: nobody knows when a rate was last checked against
a live vendor quote. PROCURE's lane says "compare quotes on landed cost, not
headline price" and "flag when a real vendor price diverges from the estimating
rate" — neither is possible without a kept record. This is that record.

It holds two directions of document:

  inbound   vendor quotations to us — what we PAY
  outbound  our own quotations to a client — what we CHARGE

Keeping both in one place is the point: `--margin` sets one against the other and
checks the result against the floor, which is the gap `analysis/FINDINGS.md`
describes as invisible at the moment of quoting.

What it does NOT do
-------------------
It does not price a job (that is `margin.py`), it does not change the estimating
rate card, and it never invents a figure. A price that is not on a document is
not in here.

Usage
-----
    python3 scripts/pricebook.py --verify        # arithmetic, every document
    python3 scripts/pricebook.py --compare       # cross-vendor unit prices
    python3 scripts/pricebook.py --item sight-glass-sgi12s
    python3 scripts/pricebook.py --basket  pricebook/quotes/<inbound>.json
    python3 scripts/pricebook.py --margin  pricebook/quotes/<outbound>.json
    python3 scripts/pricebook.py --rates         # vendor prices vs margin.py
    python3 scripts/pricebook.py --list

Exit codes for --verify
    0  every document adds up
    1  the only failures are ones the quote file documents in `known_discrepancy`
    2  a document does not add up and nobody has written down why — do not use it
"""

import argparse
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ITEMS_FILE = os.path.join(ROOT, "pricebook", "items.json")
QUOTES_DIR = os.path.join(ROOT, "pricebook", "quotes")

TOL = 0.005  # figures are 2dp; anything larger is a real error, not rounding

# RULES.md B states a 22% margin floor. scripts/margin.py enforces 20%, which is
# what DECISIONS D-004 / OL-004 record as *proposed and unconfirmed*. Both are
# shown, because a price that clears one and not the other is exactly the case
# Farhan has not yet ruled on.
FLOOR_RULES_MD = 0.22
FLOOR_MARGIN_PY = 0.20
try:
    sys.path.insert(0, HERE)
    from margin import MARKUP_FLOOR as FLOOR_MARGIN_PY, RATES as MARGIN_RATES
except Exception:                                    # pragma: no cover
    MARGIN_RATES = {}


# --- loading ---------------------------------------------------------------

def load_items():
    with open(ITEMS_FILE) as f:
        return json.load(f)["items"]


def load_quotes(paths=None, direction=None):
    if paths is None:
        paths = sorted(
            os.path.join(QUOTES_DIR, n)
            for n in os.listdir(QUOTES_DIR) if n.endswith(".json")
        )
    quotes = []
    for p in paths:
        with open(p) as f:
            q = json.load(f)
        q["_path"] = os.path.relpath(p, ROOT)
        q.setdefault("direction", "inbound")
        if direction and q["direction"] != direction:
            continue
        quotes.append(q)
    return quotes


def money(x):
    """QAR house format: comma-separated, 2 decimals (RULES C8)."""
    return "{:,.2f}".format(x)


def _clip(s, n):
    return s if len(s) <= n else s[: n - 1] + "…"


def lines_sum(q):
    return round(sum(l["line_total"] for l in q["lines"]), 2)


# --- verification ----------------------------------------------------------

def verify(quotes):
    """Every line must multiply out, and a stated total must match lines minus discount.

    A documented `known_discrepancy` is reported loudly and counted separately —
    it is acknowledged, never waived. A quote with an undocumented mismatch must
    not be used at all.
    """
    clean, documented, broken = [], [], []

    for q in quotes:
        tag = "OUTBOUND" if q["direction"] == "outbound" else q["vendor"]["short"]
        print("\n{}  [{}]".format(tag, q["quote_id"]))
        failed = False

        for line in q["lines"]:
            expect = round(line["qty"] * line["unit_price"], 2)
            if abs(expect - line["line_total"]) > TOL:
                failed = True
                print("  LINE {} does not multiply out: {} x {} = {}, document says {}".format(
                    line["sl"], line["qty"], money(line["unit_price"]),
                    money(expect), money(line["line_total"])))

        computed = lines_sum(q)
        discount = q.get("discount", 0.0) or 0.0
        net = round(computed - discount, 2)
        stated = q.get("stated_total")
        detail = "lines {}{}".format(
            money(computed), " less discount {}".format(money(discount)) if discount else "")

        if stated is None:
            print("  lines OK · {} · NO TOTAL ON DOCUMENT — confirm with the vendor "
                  "before use (RULES A3)".format(detail))
        elif abs(net - stated) > TOL:
            failed = True
            kd = q.get("known_discrepancy")
            if kd:
                print("  ⚠ DOCUMENTED DISCREPANCY — {} but the document states {} "
                      "(out by {})".format(detail, money(stated),
                                           money(abs(net - stated))))
                print("    {}".format(kd.get("note", "")))
                documented.append(q["quote_id"])
                continue
            print("  UNDOCUMENTED MISMATCH: {} but the document states {}".format(
                detail, money(stated)))
        else:
            print("  lines OK · total OK · QAR {} verified against the document{}".format(
                money(stated), " (after discount)" if discount else ""))

        (broken if failed else clean).append(q["quote_id"])

    print("\n{} clean · {} documented discrepancy · {} unexplained".format(
        len(clean), len(documented), len(broken)))
    if broken:
        return 2
    if documented:
        return 1
    return 0


# --- indexing --------------------------------------------------------------

def index_by_item(quotes):
    """item key -> every quoted line for it, across documents."""
    idx = defaultdict(list)
    for q in quotes:
        for line in q["lines"]:
            size = line.get("unit_size")
            idx[line["item"]].append({
                "vendor": q["vendor"]["short"],
                "direction": q["direction"],
                "date": q["document"]["date"],
                "ref": q["document"].get("ref"),
                "unit_price": line["unit_price"],
                "unit": line["unit"],
                "qty": line["qty"],
                "description": line["description"],
                "note": line.get("note"),
                "unit_size": size,
                "unit_size_uom": line.get("unit_size_uom"),
                "per_uom": round(line["unit_price"] / size, 2) if size else None,
                "quote_id": q["quote_id"],
            })
    return idx


def best_inbound(idx, key):
    """Cheapest inbound unit price on record for an item, or None."""
    offers = [o for o in idx.get(key, []) if o["direction"] == "inbound"]
    return min(offers, key=lambda o: o["unit_price"]) if offers else None


# --- comparison ------------------------------------------------------------

def print_compare(items, quotes):
    idx = index_by_item(quotes)
    vendors = []
    for q in quotes:
        if q["vendor"]["short"] not in vendors:
            vendors.append(q["vendor"]["short"])

    rows = []
    for key, offers in idx.items():
        by_vendor = {}
        for o in offers:
            cur = by_vendor.get(o["vendor"])
            if cur is None or o["unit_price"] < cur["unit_price"]:
                by_vendor[o["vendor"]] = o
        prices = [o["unit_price"] for o in by_vendor.values()]
        meta = items.get(key, {})
        best = min(prices)
        rows.append({
            "item": key,
            "description": meta.get("description", key),
            "by_vendor": by_vendor,
            "quoted_by": len(by_vendor),
            "best": best,
            "best_vendor": min(by_vendor.items(), key=lambda kv: kv[1]["unit_price"])[0],
            "spread_pct": (max(prices) - best) / best * 100.0 if best else 0.0,
            "compare_note": meta.get("compare_note"),
        })
    rows.sort(key=lambda r: (-r["quoted_by"], -r["spread_pct"]))

    wdesc = 44
    head = "{:<{w}}".format("ITEM", w=wdesc)
    for v in vendors:
        head += "{:>12}".format(v)
    head += "{:>10}{:>9}  {}".format("BEST", "SPREAD", "CHEAPEST")
    print(head)
    print("-" * len(head))

    contested = [r for r in rows if r["quoted_by"] > 1]
    single = [r for r in rows if r["quoted_by"] == 1]

    for r in contested:
        line = "{:<{w}}".format(_clip(r["description"], wdesc - 2), w=wdesc)
        for v in vendors:
            o = r["by_vendor"].get(v)
            line += "{:>12}".format(money(o["unit_price"]) if o else "—")
        line += "{:>10}{:>8.0f}%  {}".format(
            money(r["best"]), r["spread_pct"], r["best_vendor"])
        print(line + ("  ⚠" if r["compare_note"] else ""))

    if single:
        print("\nOne source only — no comparison possible yet:")
        for r in single:
            v, o = next(iter(r["by_vendor"].items()))
            print("  {:<{w}} {:>11}  {}".format(
                _clip(r["description"], wdesc - 2), money(o["unit_price"]), v, w=wdesc))

    notes = [r for r in contested if r["compare_note"]]
    if notes:
        print("\n⚠ NOT LIKE FOR LIKE — read before acting on the spread:")
        for r in notes:
            print("  · {}\n      {}".format(r["description"], r["compare_note"]))


# --- one item over time ----------------------------------------------------

def print_item(items, quotes, key):
    idx = index_by_item(quotes)
    if key not in idx:
        print("No price on record for '{}'.".format(key))
        stem = key.split("-")[0]
        near = [k for k in items if stem in k]
        if near:
            print("Did you mean: {}".format(", ".join(near)))
        return 1

    meta = items.get(key, {})
    print("\n{}".format(meta.get("description", key)))
    if meta.get("brand") or meta.get("model"):
        print("  {} {}".format(meta.get("brand", ""), meta.get("model", "")).strip())
    if meta.get("rate_card"):
        rate = MARGIN_RATES.get(meta["rate_card"])
        print("  estimating rate: margin.py RATES['{}'] = {}".format(
            meta["rate_card"], money(rate) if rate else "?"))
    print()
    print("  {:<12} {:<12} {:>11} {:>11}  {}".format(
        "DATE", "SOURCE", "UNIT PRICE", "PER UOM", "AS QUOTED"))
    for o in sorted(idx[key], key=lambda o: (o["date"], o["vendor"])):
        per = "{} /{}".format(money(o["per_uom"]), o["unit_size_uom"]) if o["per_uom"] else "—"
        mark = "*" if o["direction"] == "outbound" else " "
        print("  {:<12} {:<12}{}{:>10} {:>11}  {}".format(
            o["date"], o["vendor"], mark, money(o["unit_price"]), per,
            _clip(o["description"], 46)))
        if o["note"]:
            print("  {:<26} └ {}".format("", o["note"]))
    if any(o["direction"] == "outbound" for o in idx[key]):
        print("\n  * our own selling price, not a cost")
    if meta.get("compare_note"):
        print("\n  ⚠ {}".format(meta["compare_note"]))
    return 0


# --- basket ----------------------------------------------------------------

def print_basket(items, quotes, basket_path):
    """Price one document's quantities against every vendor on record."""
    basket = load_quotes([basket_path])[0]
    inbound = [q for q in quotes if q["direction"] == "inbound"]
    idx = index_by_item(inbound)
    vendors = []
    for q in inbound:
        if q["vendor"]["short"] not in vendors:
            vendors.append(q["vendor"]["short"])

    totals = {v: 0.0 for v in vendors}
    gaps = {v: [] for v in vendors}
    best_total = 0.0

    print("\nBasket: {}  ({} lines)".format(basket["quote_id"], len(basket["lines"])))
    print("Quantities from that document. Prices from every inbound quote on record.\n")
    wdesc = 44
    head = "{:<{w}}{:>5}".format("ITEM", "QTY", w=wdesc)
    for v in vendors:
        head += "{:>13}".format(v)
    head += "{:>13}".format("BEST-OF")
    print(head)
    print("-" * len(head))

    for line in basket["lines"]:
        key, qty = line["item"], line["qty"]
        meta = items.get(key, {})
        row = "{:<{w}}{:>5}".format(_clip(meta.get("description", key), wdesc - 2), qty, w=wdesc)
        cheapest = None
        for v in vendors:
            offers = [o for o in idx.get(key, []) if o["vendor"] == v]
            if not offers:
                row += "{:>13}".format("—")
                gaps[v].append(meta.get("description", key))
                continue
            ext = round(min(o["unit_price"] for o in offers) * qty, 2)
            totals[v] += ext
            cheapest = ext if cheapest is None else min(cheapest, ext)
            row += "{:>13}".format(money(ext))
        if cheapest is not None:
            best_total += cheapest
            row += "{:>13}".format(money(cheapest))
        print(row)

    print("-" * len(head))
    foot = "{:<{w}}{:>5}".format("TOTAL (priced lines only)", "", w=wdesc)
    for v in vendors:
        foot += "{:>13}".format(money(round(totals[v], 2)))
    foot += "{:>13}".format(money(round(best_total, 2)))
    print(foot)

    for v in vendors:
        if gaps[v]:
            print("\n{} did not quote {} of these lines — its total above is NOT comparable:"
                  .format(v, len(gaps[v])))
            for g in gaps[v]:
                print("    · {}".format(g))

    print("\nThese are vendor costs. They are not a price to anyone. A client-facing\n"
          "figure goes through margin.py and then through Farhan (RULES B).")


# --- margin on one of our own quotations -----------------------------------

def print_margin(items, quotes, quote_path):
    """Set an outbound quotation against the best inbound cost on record."""
    sell = load_quotes([quote_path])[0]
    if sell["direction"] != "outbound":
        print("{} is an inbound (vendor) document. --margin takes one of OUR "
              "quotations.".format(sell["quote_id"]))
        return 1

    idx = index_by_item([q for q in quotes if q["direction"] == "inbound"])

    print("\n=== MARGIN CHECK: {} ===".format(sell["document"]["ref"]))
    print("Client: {} · dated {} · {}".format(
        sell.get("client", {}).get("name", "?"), sell["document"]["date"],
        sell["terms"].get("scope", "")))
    print("\nCost = cheapest inbound price on record for each line. Where no vendor "
          "\nprice is on record the line is shown UNCOSTED and excluded from the maths.\n")

    wdesc = 42
    print("{:<{w}}{:>4}{:>11}{:>11}{:>11}{:>9}".format(
        "LINE", "QTY", "COST/EA", "SELL/EA", "PROFIT", "MARKUP", w=wdesc))
    print("-" * (wdesc + 46))

    cost_total = sell_total = 0.0
    uncosted = []
    thin = []

    for line in sell["lines"]:
        key, qty = line["item"], line["qty"]
        meta = items.get(key, {})
        desc = _clip(meta.get("description", key), wdesc - 2)
        b = best_inbound(idx, key)
        if b is None:
            uncosted.append((desc, line["line_total"]))
            print("{:<{w}}{:>4}{:>11}{:>11}{:>11}{:>9}".format(
                desc, qty, "—", money(line["unit_price"]), "—", "—", w=wdesc))
            continue
        c, s = b["unit_price"], line["unit_price"]
        cost_total += c * qty
        sell_total += s * qty
        mk = (s - c) / c * 100.0 if c else 0.0
        if mk < FLOOR_MARGIN_PY * 100:
            thin.append((desc, mk, b["vendor"]))
        print("{:<{w}}{:>4}{:>11}{:>11}{:>11}{:>8.0f}%".format(
            desc, qty, money(c), money(s), money((s - c) * qty), mk, w=wdesc))

    cost_total, sell_total = round(cost_total, 2), round(sell_total, 2)
    profit = round(sell_total - cost_total, 2)
    markup = profit / cost_total if cost_total else 0.0
    margin = profit / sell_total if sell_total else 0.0

    print("-" * (wdesc + 46))
    print("{:<{w}}{:>15}{:>11}{:>11}".format(
        "COSTED LINES", money(cost_total), money(sell_total), money(profit), w=wdesc))
    print("\n  Quotation grand total      QAR {}".format(money(sell["stated_total"])))
    print("  Material cost (best-of)    QAR {}".format(money(cost_total)))
    print("  Gross profit               QAR {}".format(money(profit)))
    print("  Markup on cost             {:.1f}%".format(markup * 100))
    print("  Margin on price            {:.1f}%".format(margin * 100))

    if uncosted:
        print("\n  {} line(s) have no vendor price on record and are excluded above:"
              .format(len(uncosted)))
        for d, v in uncosted:
            print("    · {}  (sold at {})".format(d, money(v)))

    print("\n  Floor check")
    for label, floor in (("RULES.md B (22%)", FLOOR_RULES_MD),
                         ("margin.py / D-004 proposed (20%)", FLOOR_MARGIN_PY)):
        verdict = "CLEARS" if markup >= floor else "BELOW FLOOR"
        print("    {:<34} {}".format(label, verdict))
    if markup < max(FLOOR_RULES_MD, FLOOR_MARGIN_PY):
        print("\n  ESCALATE (RULES B / RULES E): quoting below the floor needs Farhan's\n"
              "  written override with a reason, logged. This has not been logged.")

    if thin:
        print("\n  Lines below the floor individually:")
        for d, mk, v in sorted(thin, key=lambda t: t[1]):
            print("    {:>6.0f}%  {}  (cheapest: {})".format(mk, d, v))

    print("\n  Cost excludes handling, collection and any labour. Supply-only scope,\n"
          "  so no installation cost is carried — but nor is any installation revenue.")
    return 0


# --- rate card check -------------------------------------------------------

def print_rates(items, quotes):
    """Every item tied to a margin.py rate, against the real quoted price."""
    idx = index_by_item([q for q in quotes if q["direction"] == "inbound"])
    tied = [(k, v) for k, v in items.items() if v.get("rate_card")]
    if not tied:
        print("No items are tied to a margin.py rate yet.")
        return 0

    print("\n=== ESTIMATING RATE vs REAL VENDOR PRICE ===")
    print("PROCURE escalates a divergence over 10% (agents/procure/IDENTITY.md).\n")
    print("{:<40}{:>12}{:>12}{:>10}  {}".format(
        "ITEM", "RATE CARD", "QUOTED", "DIVERGE", "SOURCE"))
    print("-" * 92)
    worst = []
    for key, meta in sorted(tied):
        b = best_inbound(idx, key)
        rate = MARGIN_RATES.get(meta["rate_card"])
        if b is None or rate is None:
            continue
        div = (b["unit_price"] - rate) / rate * 100.0
        print("{:<40}{:>12}{:>12}{:>9.0f}%  {} {}".format(
            _clip(meta["description"], 38), money(rate), money(b["unit_price"]),
            div, b["vendor"], b["date"]))
        if meta.get("rate_card_note"):
            print("      ↳ {}".format(meta["rate_card_note"]))
        if abs(div) > 10:
            worst.append((meta["description"], rate, b["unit_price"], div, meta["rate_card"]))

    if worst:
        print("\n⚠ Over PROCURE's 10% escalation threshold:")
        for d, r, p, div, rc in worst:
            direction = "ABOVE" if div > 0 else "below"
            print("  · {}\n      RATES['{}'] = {} · real {} · {:.0f}% {} the rate"
                  .format(d, rc, money(r), money(p), abs(div), direction))
        print("\n  A rate that is BELOW the real price understates cost, so every price\n"
              "  built on it is thinner than it looks. Only PROCURE may propose a rate\n"
              "  change, and only with a real vendor quote as evidence — which is what\n"
              "  these are. The change itself is Farhan's.")
    return 0


# --- main ------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="TNDK price book")
    ap.add_argument("--verify", action="store_true", help="check every document's arithmetic")
    ap.add_argument("--compare", action="store_true", help="cross-vendor unit price table")
    ap.add_argument("--item", help="price history for one canonical item key")
    ap.add_argument("--basket", help="price one document's quantities across all vendors")
    ap.add_argument("--margin", help="set one of OUR quotations against vendor cost")
    ap.add_argument("--rates", action="store_true", help="vendor prices vs margin.py rate card")
    ap.add_argument("--list", action="store_true", help="list documents on record")
    ap.add_argument("--json", action="store_true", help="machine-readable price index")
    args = ap.parse_args()

    items = load_items()
    quotes = load_quotes()
    inbound = [q for q in quotes if q["direction"] == "inbound"]

    if args.json:
        out = {
            "generated_from": [q["quote_id"] for q in quotes],
            "items": {k: v for k, v in index_by_item(quotes).items()},
        }
        try:
            json.dump(out, sys.stdout, indent=2, sort_keys=True)
            print()
        except BrokenPipeError:
            pass
        return 0

    any_action = any([args.verify, args.compare, args.item, args.basket,
                      args.margin, args.rates])

    if args.list or not any_action:
        print("\nDocuments on record ({}):\n".format(len(quotes)))
        for q in sorted(quotes, key=lambda q: q["document"]["date"]):
            tag = "SELL" if q["direction"] == "outbound" else q["vendor"]["short"]
            t = q.get("stated_total")
            flag = "  ⚠ discrepancy" if q.get("known_discrepancy") else ""
            print("  {}  {:<11} {:<26} {:>11}  {} lines{}".format(
                q["document"]["date"], tag,
                _clip(q["document"].get("ref") or "(no ref)", 26),
                money(t) if t is not None else "no total", len(q["lines"]), flag))
            print("      {}".format(q["_path"]))
        if not any_action:
            print("\nTry --compare, --verify, --rates, --item <key>, --basket <file>, "
                  "--margin <our quote>.")
            return 0

    rc = 0
    if args.verify:
        print("\n=== ARITHMETIC VERIFICATION ===")
        rc = verify(quotes)

    if args.compare:
        print("\n=== UNIT PRICE COMPARISON — INBOUND VENDOR QUOTES (QAR) ===\n")
        print_compare(items, inbound)

    if args.rates:
        print_rates(items, quotes)

    if args.item:
        return print_item(items, quotes, args.item)

    if args.basket:
        print_basket(items, quotes, args.basket)

    if args.margin:
        return print_margin(items, quotes, args.margin)

    return rc


if __name__ == "__main__":
    sys.exit(main())
