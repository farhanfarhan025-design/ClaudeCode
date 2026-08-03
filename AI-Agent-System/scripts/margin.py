#!/usr/bin/env python3
"""
TNDK cost build-up and margin calculator.

Reproduces Farhan's documented pricing methodology exactly, then makes the two
things visible that the current process hides:

  1. the realised margin on a proposed price, and
  2. whether that price clears the floor.

Rates and formulas come from tndk-coldroom-quotation/references/pricing-guide.md.
Verified against the Mr. Suresh worked example (April 2026): direct cost 43,448.

Usage
-----
    python3 margin.py --config job.json
    python3 margin.py --config job.json --price 59000
    python3 margin.py --config job.json --json          # machine-readable

Config format: see scripts/examples/suresh.json
"""

import argparse
import json
import math
import sys

# --- Rate card -------------------------------------------------------------
# Internal estimating prices, not client-facing. Update here, nowhere else.
RATES = {
    "panel_sqm": 115.0,        # 100mm PUF sandwich panel, food-grade GI both faces
    "door": 1800.0,            # 90x190 hinged, safety release
    "angle_piece": 55.0,       # 40x40x2mm L-profile, 6m length
    "floor_pair": 350.0,       # chequered sheet + plywood, covers ~2.88 sqm
    "floor_pair_coverage": 2.88,
    "unit_chiller": 8800.0,    # condensing unit + evaporator, +2 to +8C
    "unit_freezer": 6400.0,    # condensing unit + evaporator, freezer duty
    "control_panel": 1200.0,   # per room, IP55, digital controller
    "pipe_system": 2500.0,     # per system
    "wiring_system": 1800.0,   # per system
    "lights_per_2_rooms": 500.0,
}

LABOUR_PCT = 0.15          # of direct cost
TRANSPORT_DEFAULT = 1500.0  # lump sum within Doha

# Floor is expressed as MARKUP ON COST, matching the pricing guide's convention.
#
# 20% is the pricing guide's own lowest documented tier (competitive / tender /
# repeat client). Below it, nothing in Farhan's methodology justifies the price —
# so it takes an owner override. Between 20% and 30% the price is legitimate but
# must carry a reason code, so that "competitive" is a decision rather than a drift.
MARKUP_FLOOR = 0.20
MARKUP_DEFAULT_NEW_CLIENT = 0.30
MARKUP_COMPETITIVE = 0.20

REASON_CODES = {
    "TENDER": "Competitive tender / bid",
    "REPEAT": "Repeat client, relationship value",
    "VOLUME": "Volume or multi-room award",
    "STRATEGIC": "Reference site or strategic entry",
    "CORRECTION": "Correcting an earlier quoted figure",
}


def room_cost(room):
    """Cost build-up for one room. Returns (lines, subtotal)."""
    L, W, H = room["length"], room["width"], room["height"]
    qty = room.get("qty", 1)
    has_floor = room.get("floor", False)
    kind = room["type"].lower()

    wall = 2 * (L * H) + 2 * (W * H)
    ceiling = L * W
    floor = L * W if has_floor else 0.0
    panel_sqm = wall + ceiling + floor

    # Angle requirement: perimeter runs top and bottom, plus vertical corners.
    angle_pieces = math.ceil((4 * (L + W) + 4 * H) / 6)

    lines = [
        {"item": f"{room['name']} — panels",
         "detail": f"{panel_sqm:.2f} sqm @ {RATES['panel_sqm']:.0f}"
                   f"  (wall {wall:.2f} + ceiling {ceiling:.2f}"
                   + (f" + floor {floor:.2f}" if has_floor else "") + ")",
         "amount": panel_sqm * RATES["panel_sqm"]},
        {"item": f"{room['name']} — angles",
         "detail": f"{angle_pieces} pcs @ {RATES['angle_piece']:.0f}",
         "amount": angle_pieces * RATES["angle_piece"]},
    ]

    doors = room.get("doors", 1)
    if doors:
        lines.append({"item": f"{room['name']} — door",
                      "detail": f"{doors} @ {RATES['door']:.0f}",
                      "amount": doors * RATES["door"]})

    if has_floor:
        pairs = math.ceil(floor / RATES["floor_pair_coverage"])
        lines.append({"item": f"{room['name']} — floor (chequered + ply)",
                      "detail": f"{pairs} pairs @ {RATES['floor_pair']:.0f}",
                      "amount": pairs * RATES["floor_pair"]})

    unit_rate = RATES["unit_freezer"] if "freez" in kind else RATES["unit_chiller"]
    lines.append({"item": f"{room['name']} — condensing unit + evaporator",
                  "detail": f"{kind} duty, 1 set @ {unit_rate:.0f}",
                  "amount": unit_rate})

    if qty > 1:
        for ln in lines:
            ln["amount"] *= qty
            ln["detail"] += f"  x{qty} rooms"

    return lines, sum(ln["amount"] for ln in lines), panel_sqm * qty


def build(config):
    rooms = config["rooms"]
    n_rooms = sum(r.get("qty", 1) for r in rooms)

    lines = []
    total_panel = 0.0
    for r in rooms:
        rl, _, panel = room_cost(r)
        lines.extend(rl)
        total_panel += panel

    # Common / shared items
    common = [
        {"item": "Common — control panels",
         "detail": f"{n_rooms} @ {RATES['control_panel']:.0f}",
         "amount": n_rooms * RATES["control_panel"]},
        {"item": "Common — pipe & accessories",
         "detail": f"{n_rooms} systems @ {RATES['pipe_system']:.0f}",
         "amount": n_rooms * RATES["pipe_system"]},
        {"item": "Common — wiring",
         "detail": f"{n_rooms} systems @ {RATES['wiring_system']:.0f}",
         "amount": n_rooms * RATES["wiring_system"]},
        {"item": "Common — LED vapour-proof lights",
         "detail": f"lump sum for {n_rooms} rooms",
         "amount": RATES["lights_per_2_rooms"] * max(1, round(n_rooms / 2))},
    ]
    lines.extend(common)

    for extra in config.get("extras", []):
        lines.append({"item": f"Extra — {extra['item']}",
                      "detail": extra.get("detail", ""),
                      "amount": float(extra["amount"])})

    direct = sum(ln["amount"] for ln in lines)
    labour = direct * config.get("labour_pct", LABOUR_PCT)
    transport = config.get("transport", TRANSPORT_DEFAULT)
    cost = direct + labour + transport

    return {
        "lines": lines,
        "direct": direct,
        "labour": labour,
        "labour_pct": config.get("labour_pct", LABOUR_PCT),
        "transport": transport,
        "cost": cost,
        "total_panel_sqm": total_panel,
        "n_rooms": n_rooms,
    }


def price_at(cost, markup):
    return cost * (1 + markup)


def analyse_price(cost, price):
    """Both conventions, because they differ and the difference is commercially real."""
    profit = price - cost
    markup_on_cost = profit / cost if cost else 0.0
    margin_on_price = profit / price if price else 0.0
    return {"price": price, "profit": profit,
            "markup_on_cost": markup_on_cost,
            "margin_on_price": margin_on_price}


def money(x):
    return f"{x:>12,.2f}"


def report(config, b, proposed=None):
    out = []
    A = out.append
    A("=" * 74)
    A(f"  COST BUILD-UP — {config.get('job', 'untitled job')}")
    A(f"  Client: {config.get('client', '—')}"
      f"   ·   {b['n_rooms']} room(s)   ·   {b['total_panel_sqm']:.2f} sqm panel")
    A("=" * 74)
    for ln in b["lines"]:
        A(f"  {ln['item']:<44}{money(ln['amount'])}")
        if ln["detail"]:
            A(f"      {ln['detail']}")
    A("-" * 74)
    A(f"  {'DIRECT COST':<44}{money(b['direct'])}")
    labour_label = "Labour & installation ({:.0f}%)".format(b["labour_pct"] * 100)
    A(f"  {labour_label:<44}{money(b['labour'])}")
    A(f"  {'Transport & handling':<44}{money(b['transport'])}")
    A(f"  {'TOTAL COST':<44}{money(b['cost'])}")
    A("=" * 74)
    A("  PRICE LADDER")
    for label, mk in [("FLOOR / competitive / tender / repeat (20%)", MARKUP_FLOOR),
                      ("Standard (25%)", 0.25),
                      ("Default, new client (30%)", MARKUP_DEFAULT_NEW_CLIENT),
                      ("Premium / urgent / difficult access (35%)", 0.35)]:
        p = price_at(b["cost"], mk)
        a = analyse_price(b["cost"], p)
        A(f"  {label:<44}{money(p)}   ({a['margin_on_price']*100:>5.1f}% of price)")
    A("=" * 74)

    if proposed is not None:
        a = analyse_price(b["cost"], proposed)
        A("  PROPOSED PRICE CHECK")
        A(f"  {'Proposed price':<44}{money(proposed)}")
        A(f"  {'Total cost':<44}{money(b['cost'])}")
        A(f"  {'Gross profit':<44}{money(a['profit'])}")
        A("")
        A(f"  {'Markup on cost (pricing-guide convention)':<44}"
          f"{a['markup_on_cost']*100:>11.1f}%")
        A(f"  {'True gross margin (share of price)':<44}"
          f"{a['margin_on_price']*100:>11.1f}%")
        A("")
        if a["markup_on_cost"] < MARKUP_FLOOR:
            shortfall = price_at(b["cost"], MARKUP_FLOOR) - proposed
            A(f"  *** BELOW FLOOR ***  {a['markup_on_cost']*100:.1f}% markup"
              f" vs {MARKUP_FLOOR*100:.0f}% floor")
            A(f"  This is below every tier in the pricing guide, including")
            A(f"  competitive tender. Nothing in the documented methodology")
            A(f"  produces this price.")
            A(f"  To reach the floor, price must rise {shortfall:,.2f}"
              f" to {price_at(b['cost'], MARKUP_FLOOR):,.2f}")
            A("  → OWNER OVERRIDE REQUIRED. Log it in logs/overrides/.")
        elif a["markup_on_cost"] < MARKUP_DEFAULT_NEW_CLIENT:
            gap = price_at(b["cost"], MARKUP_DEFAULT_NEW_CLIENT) - proposed
            A(f"  Clears the {MARKUP_FLOOR*100:.0f}% floor, below the"
              f" {MARKUP_DEFAULT_NEW_CLIENT*100:.0f}% default.")
            A(f"  Legitimate, but needs a reason code:")
            A("    " + " · ".join(REASON_CODES))
            A(f"  Gap to the default tier: {gap:,.2f}")
        else:
            A(f"  Clears the {MARKUP_DEFAULT_NEW_CLIENT*100:.0f}% default."
              f" No override, no reason code needed.")
        A("=" * 74)
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="TNDK cost build-up and margin check")
    ap.add_argument("--config", required=True)
    ap.add_argument("--price", type=float, default=None,
                    help="proposed client price to check against the floor")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    with open(args.config) as f:
        config = json.load(f)

    b = build(config)

    if args.json:
        payload = {"job": config.get("job"), "client": config.get("client"),
                   "cost": round(b["cost"], 2), "direct": round(b["direct"], 2),
                   "labour": round(b["labour"], 2), "transport": b["transport"],
                   "total_panel_sqm": round(b["total_panel_sqm"], 2),
                   "ladder": {f"{int(m*100)}%": round(price_at(b["cost"], m), 2)
                              for m in [0.20, 0.25, 0.30, 0.35]}}
        if args.price is not None:
            a = analyse_price(b["cost"], args.price)
            payload["proposed"] = {
                "price": args.price,
                "profit": round(a["profit"], 2),
                "markup_on_cost": round(a["markup_on_cost"], 4),
                "margin_on_price": round(a["margin_on_price"], 4),
                "below_floor": a["markup_on_cost"] < MARKUP_FLOOR,
            }
        print(json.dumps(payload, indent=2))
    else:
        print(report(config, b, args.price))

    if args.price is not None:
        a = analyse_price(b["cost"], args.price)
        if a["markup_on_cost"] < MARKUP_FLOOR:
            sys.exit(2)   # non-zero so a wrapper can gate on it
    return 0


if __name__ == "__main__":
    main()
