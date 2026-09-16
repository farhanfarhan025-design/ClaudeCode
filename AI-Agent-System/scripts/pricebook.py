#!/usr/bin/env python3
"""
TNDK vendor price book — capture, verify and compare vendor rates over time.

Why this exists
---------------
`memory/open_loops.md` OL-009: nobody knows when a rate was last checked against
a live vendor quote. PROCURE's lane says "flag when a real vendor price diverges
from the estimating rate" and "compare quotes on landed cost, not headline price"
— neither is possible without a kept record. This is that record.

What it does NOT do
-------------------
It does not price a job (that is `margin.py`), it does not touch the estimating
rate card, and it never invents a figure. A price that is not on a vendor
document is not in here.

Usage
-----
    python3 scripts/pricebook.py --verify              # arithmetic check, every quote
    python3 scripts/pricebook.py --compare             # cross-vendor unit prices
    python3 scripts/pricebook.py --item copper-coil-half-50ft
    python3 scripts/pricebook.py --basket pricebook/quotes/<file>.json
    python3 scripts/pricebook.py --list
    python3 scripts/pricebook.py --compare --json      # machine-readable

Data: pricebook/items.json (canonical parts) + pricebook/quotes/*.json (as quoted).
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

TOL = 0.005  # half a dirham-cent: figures are 2dp, so anything larger is a real error


# --- loading ---------------------------------------------------------------

def load_items():
    with open(ITEMS_FILE) as f:
        return json.load(f)["items"]


def load_quotes(paths=None):
    if paths is None:
        paths = sorted(
            os.path.join(QUOTES_DIR, n)
            for n in os.listdir(QUOTES_DIR)
            if n.endswith(".json")
        )
    quotes = []
    for p in paths:
        with open(p) as f:
            q = json.load(f)
        q["_path"] = os.path.relpath(p, ROOT)
        quotes.append(q)
    return quotes


def money(x):
    """QAR house format: comma-separated, 2 decimals (RULES C8)."""
    return "{:,.2f}".format(x)


# --- verification ----------------------------------------------------------

def verify(quotes):
    """Every line must multiply out, and a stated total must match the lines.

    A quote with no stated total is reported, not failed — the handwritten sheet
    genuinely carries no total, and computing one does not make it the vendor's.
    """
    ok = True
    for q in quotes:
        print("\n{}  [{}]".format(q["vendor"]["short"], q["quote_id"]))
        computed = 0.0
        for line in q["lines"]:
            expect = round(line["qty"] * line["unit_price"], 2)
            if abs(expect - line["line_total"]) > TOL:
                ok = False
                print("  FAIL line {}: {} x {} = {}, document says {}".format(
                    line["sl"], line["qty"], money(line["unit_price"]),
                    money(expect), money(line["line_total"])))
            computed += line["line_total"]
        computed = round(computed, 2)
        stated = q.get("stated_total")
        if stated is None:
            print("  lines OK · computed total QAR {} · NO TOTAL ON DOCUMENT "
                  "— confirm with vendor before use (RULES A3)".format(money(computed)))
        elif abs(computed - stated) > TOL:
            ok = False
            print("  FAIL total: lines sum to {}, document states {}".format(
                money(computed), money(stated)))
        else:
            print("  lines OK · total OK · QAR {} verified against the document".format(
                money(computed)))
    return ok


# --- comparison ------------------------------------------------------------

def index_by_item(quotes):
    """item key -> list of {vendor, date, unit_price, unit, qty, description, note}."""
    idx = defaultdict(list)
    for q in quotes:
        for line in q["lines"]:
            idx[line["item"]].append({
                "vendor": q["vendor"]["short"],
                "vendor_name": q["vendor"]["name"],
                "date": q["document"]["date"],
                "ref": q["document"].get("ref"),
                "unit_price": line["unit_price"],
                "unit": line["unit"],
                "qty": line["qty"],
                "description": line["description"],
                "note": line.get("note"),
                "quote_id": q["quote_id"],
            })
    return idx


def compare_rows(items, idx, vendors):
    """One row per item, with each vendor's best (lowest) unit price for it."""
    rows = []
    for key, offers in idx.items():
        meta = items.get(key, {})
        by_vendor = {}
        for o in offers:
            cur = by_vendor.get(o["vendor"])
            if cur is None or o["unit_price"] < cur["unit_price"]:
                by_vendor[o["vendor"]] = o
        prices = [o["unit_price"] for o in by_vendor.values()]
        row = {
            "item": key,
            "description": meta.get("description", key),
            "by_vendor": by_vendor,
            "quoted_by": len(by_vendor),
            "best": min(prices),
            "worst": max(prices),
            "compare_note": meta.get("compare_note"),
        }
        row["spread_pct"] = (
            (row["worst"] - row["best"]) / row["best"] * 100.0 if row["best"] else 0.0
        )
        row["best_vendor"] = min(by_vendor.items(), key=lambda kv: kv[1]["unit_price"])[0]
        rows.append(row)
    rows.sort(key=lambda r: (-r["quoted_by"], -r["spread_pct"]))
    return rows


def print_compare(items, quotes):
    idx = index_by_item(quotes)
    vendors = []
    for q in quotes:
        if q["vendor"]["short"] not in vendors:
            vendors.append(q["vendor"]["short"])
    rows = compare_rows(items, idx, vendors)

    wdesc = 46
    head = "{:<{w}}".format("ITEM", w=wdesc)
    for v in vendors:
        head += "{:>13}".format(v)
    head += "{:>10}{:>10}  {}".format("BEST", "SPREAD", "CHEAPEST")
    print(head)
    print("-" * len(head))

    contested = [r for r in rows if r["quoted_by"] > 1]
    single = [r for r in rows if r["quoted_by"] == 1]

    for r in contested:
        line = "{:<{w}}".format(_clip(r["description"], wdesc - 2), w=wdesc)
        for v in vendors:
            o = r["by_vendor"].get(v)
            line += "{:>13}".format(money(o["unit_price"]) if o else "—")
        line += "{:>10}{:>9.0f}%  {}".format(
            money(r["best"]), r["spread_pct"], r["best_vendor"])
        print(line + ("  ⚠" if r["compare_note"] else ""))

    if single:
        print("\nQuoted by one vendor only — no comparison possible yet:")
        for r in single:
            v, o = next(iter(r["by_vendor"].items()))
            print("  {:<{w}} {:>12}  {}".format(
                _clip(r["description"], wdesc - 2), money(o["unit_price"]), v, w=wdesc))

    notes = [r for r in contested if r["compare_note"]]
    if notes:
        print("\n⚠ NOT LIKE FOR LIKE — read before acting on the spread:")
        for r in notes:
            print("  · {}\n      {}".format(r["description"], r["compare_note"]))


def _clip(s, n):
    return s if len(s) <= n else s[: n - 1] + "…"


# --- one item over time ----------------------------------------------------

def print_item(items, quotes, key):
    idx = index_by_item(quotes)
    if key not in idx:
        print("No quoted price on record for '{}'.".format(key))
        near = [k for k in items if key.split("-")[0] in k]
        if near:
            print("Did you mean: {}".format(", ".join(near)))
        return 1
    meta = items.get(key, {})
    print("\n{}".format(meta.get("description", key)))
    if meta.get("brand") or meta.get("model"):
        print("  {} {}".format(meta.get("brand", ""), meta.get("model", "")).strip())
    print()
    print("  {:<12} {:<12} {:>12}  {}".format("DATE", "VENDOR", "UNIT PRICE", "AS QUOTED"))
    for o in sorted(idx[key], key=lambda o: (o["date"], o["vendor"])):
        print("  {:<12} {:<12} {:>12}  {}".format(
            o["date"], o["vendor"], money(o["unit_price"]), _clip(o["description"], 52)))
        if o["note"]:
            print("  {:<26} └ {}".format("", o["note"]))
    if meta.get("compare_note"):
        print("\n  ⚠ {}".format(meta["compare_note"]))
    return 0


# --- basket ----------------------------------------------------------------

def print_basket(items, quotes, basket_path):
    """Price one quotation's requirement at every vendor, and at best-of.

    Quantities come from the basket document. A vendor who never quoted an item
    shows as a gap, not a zero — a missing price is a question, not a saving.
    """
    basket = load_quotes([basket_path])[0]
    idx = index_by_item(quotes)
    vendors = []
    for q in quotes:
        if q["vendor"]["short"] not in vendors:
            vendors.append(q["vendor"]["short"])

    totals = {v: 0.0 for v in vendors}
    gaps = {v: [] for v in vendors}
    best_total = 0.0

    print("\nBasket: {}  ({} lines)".format(basket["quote_id"], len(basket["lines"])))
    print("Quantities from that document. Prices from every quote on record.\n")
    wdesc = 46
    head = "{:<{w}}{:>5}".format("ITEM", "QTY", w=wdesc)
    for v in vendors:
        head += "{:>14}".format(v)
    head += "{:>14}".format("BEST-OF")
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
                row += "{:>14}".format("—")
                gaps[v].append(meta.get("description", key))
                continue
            price = min(o["unit_price"] for o in offers)
            ext = round(price * qty, 2)
            totals[v] += ext
            cheapest = ext if cheapest is None else min(cheapest, ext)
            row += "{:>14}".format(money(ext))
        if cheapest is not None:
            best_total += cheapest
            row += "{:>14}".format(money(cheapest))
        print(row)

    print("-" * len(head))
    foot = "{:<{w}}{:>5}".format("TOTAL (priced lines only)", "", w=wdesc)
    for v in vendors:
        foot += "{:>14}".format(money(round(totals[v], 2)))
    foot += "{:>14}".format(money(round(best_total, 2)))
    print(foot)

    for v in vendors:
        if gaps[v]:
            print("\n{} did not quote {} of these lines — its total above is NOT comparable:"
                  .format(v, len(gaps[v])))
            for g in gaps[v]:
                print("    · {}".format(g))

    print("\nThese are vendor costs. They are not a price to anyone. A client-facing\n"
          "figure goes through margin.py and then through Farhan (RULES B).")


# --- main ------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="TNDK vendor price book")
    ap.add_argument("--verify", action="store_true", help="check every quote's arithmetic")
    ap.add_argument("--compare", action="store_true", help="cross-vendor unit price table")
    ap.add_argument("--item", help="price history for one canonical item key")
    ap.add_argument("--basket", help="price one quote's quantities across all vendors")
    ap.add_argument("--list", action="store_true", help="list quotes on record")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    items = load_items()
    quotes = load_quotes()

    if args.json:
        idx = index_by_item(quotes)
        out = {
            "generated_from": [q["quote_id"] for q in quotes],
            "items": {
                k: [
                    {kk: vv for kk, vv in o.items() if kk != "description"}
                    for o in v
                ]
                for k, v in idx.items()
            },
        }
        json.dump(out, sys.stdout, indent=2, sort_keys=True)
        print()
        return 0

    if args.list or not (args.verify or args.compare or args.item or args.basket):
        print("\nQuotes on record ({}):\n".format(len(quotes)))
        for q in quotes:
            t = q.get("stated_total")
            print("  {}  {:<12} {:<28} {:>12}  {} lines".format(
                q["document"]["date"], q["vendor"]["short"],
                q["document"].get("ref") or "(no ref)",
                money(t) if t is not None else "no total",
                len(q["lines"])))
            print("      {}".format(q["_path"]))
        if not (args.verify or args.compare or args.item or args.basket):
            print("\nTry --compare, --verify, --item <key>, or --basket <file>.")
            return 0

    if args.verify:
        print("\n=== ARITHMETIC VERIFICATION ===")
        if not verify(quotes):
            print("\nAt least one quote does not add up. Do not use it until resolved.")
            return 2

    if args.compare:
        print("\n=== UNIT PRICE COMPARISON (QAR) ===\n")
        print_compare(items, quotes)

    if args.item:
        return print_item(items, quotes, args.item)

    if args.basket:
        print_basket(items, quotes, args.basket)

    return 0


if __name__ == "__main__":
    sys.exit(main())
