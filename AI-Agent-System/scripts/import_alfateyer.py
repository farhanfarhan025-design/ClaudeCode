#!/usr/bin/env python3
"""
One-off importer: Alfateyer's discounted spare parts stock list (Aug 2026) ->
pricebook/quotes/.

The sheet is 396 lines of stock, most of it AC and tooling we do not buy. Only
the lines that genuinely match something already in the price book are mapped
to a canonical item key; the rest are kept verbatim with item: null so they can
still be looked up with `pricebook.py --find`, but never silently enter a
comparison they do not belong in.

Usage:  python3 scripts/import_alfateyer.py <path to .xlsx>
"""

import json
import os
import sys

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "pricebook", "quotes",
                   "2026-08-01-alfateyer-discounted-spares-stock-list.json")

# SL number -> (canonical key, optional per-line note, unit_size, uom)
MAP = {
    5:   ("vibration-eliminator-seven-eighths", "Brand not stated on the sheet; ours is Harbax.", None, None),
    30:  ("ball-valve-half-hongsen", None, None, None),
    80:  ("capillary-assembly-with-nut", None, 1.5, "m"),
    81:  ("capillary-assembly-with-nut", None, 1.0, "m"),
    139: ("copper-coil-seven-eighths-50ft",
          "ECONOMY grade, Heidelberg Vietnam, 15 m roll. A 50 ft roll is 15.24 m, so the lengths "
          "are within 1.6% — but the grade is not stated on the Arctic lines and 'economy' may "
          "not be the same wall thickness. Only 4 rolls in stock.", None, None),
    149: ("expansion-valve-element-tes5-067b3342", None, None, None),
    152: ("expansion-valve-te2-r134a",
          "Same Danfoss code 068Z3348. The sheet calls it TEN-2, Airtronics calls it TE2.", None, None),
    227: ("orifice-te2-no04", None, None, None),
    228: ("orifice-te2-no05", None, None, None),
    230: ("orifice-te5-no01", None, None, None),
    265: ("sight-glass-half-hongsen", "Brazing connection.", None, None),
    266: ("sight-glass-half-hongsen", "Flaring connection.", None, None),
    273: ("solenoid-valve-evr6-half", "Without coil — see solenoid-coil-be230as.", None, None),
    281: ("solenoid-coil-be230as", None, None, None),
}


def main():
    wb = openpyxl.load_workbook(sys.argv[1], data_only=True)
    ws = wb["Sheet2"]

    lines, mapped = [], 0
    for row in ws.iter_rows(min_row=2, values_only=True):
        sl, name, qty, price = (row + (None,) * 4)[:4]
        if sl is None or price is None:
            continue
        sl = int(sl)
        key, note, size, uom = MAP.get(sl, (None, None, None, None))
        if key:
            mapped += 1
        line = {
            "sl": sl,
            "item": key,
            "description": " ".join(str(name).split()),
            "qty": int(qty) if qty is not None else None,
            "unit": "EACH",
            "unit_price": round(float(price), 4),
            "line_total": None,
        }
        if note:
            line["note"] = note
        if size:
            line["unit_size"], line["unit_size_uom"] = size, uom
        lines.append(line)

    doc = {
        "quote_id": "2026-08-01-alfateyer-discounted-spares-stock-list",
        "direction": "inbound",
        "kind": "stock price list",
        "vendor": {
            "name": "Alfateyer",
            "short": "ALFATEYER",
            "note": "Named by Farhan, 12 Oct 2026. The spreadsheet itself carries no letterhead, "
                    "no contact and no company name."
        },
        "document": {
            "ref": "SPARE PARTS - DISCOUNTED PRICE AUG 2026",
            "revision": None,
            "date": "2026-08-01",
            "date_confidence": "low — only 'AUG 2026' appears, in the filename. Treated as 1 Aug "
                               "for ordering; the real issue date is unknown.",
            "subject": "Discounted spare parts stock list",
            "source_file": "SPARE_PARTS_-_DISCOUNTED_PRICE_AUG_2026.xlsx",
            "source_type": "vendor spreadsheet"
        },
        "terms": {
            "currency": "QAR",
            "currency_confidence": "medium — the column is headed only 'Price', with no currency "
                                   "anywhere on the sheet. QAR assumed because the supplier is in "
                                   "Qatar. Confirm before any of it is used in a costing (RULES A3).",
            "payment": "not stated",
            "validity_days": None,
            "valid_until": None,
            "validity_note": "No validity on the sheet. Dated Aug 2026, so roughly two months old.",
            "delivery": "not stated",
            "stock_note": "The Quantity column is stock on hand, not a quoted quantity. Several "
                          "of the interesting lines are thin — 4 rolls of 7/8\" copper, 1 roll of "
                          "3/4\". A discounted clearance list is only a price while the stock lasts."
        },
        "stated_total": None,
        "stated_total_note": "A stock list, not a priced offer. There is no total and none is computed.",
        "price_basis": "unit",
        "price_basis_note": "Figures carry four and five decimal places (7.119999, 1.4375), which "
                            "is what a percentage discount applied to a base price looks like. "
                            "These are already-discounted unit prices.",
        "lines": lines,
        "provenance": {
            "captured_by": "PROCURE (inventory keeper)",
            "captured_on": "2026-10-12",
            "confidence": "medium",
            "basis": "Read straight from the supplier's spreadsheet. Prices are as given. Only %d "
                     "of %d lines are mapped to a canonical item; the rest are recorded verbatim "
                     "with item: null and are searchable but excluded from every comparison."
                     % (mapped, len(lines))
        }
    }

    with open(OUT, "w") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("%s — %d lines, %d mapped" % (os.path.relpath(OUT, ROOT), len(lines), mapped))


if __name__ == "__main__":
    main()
