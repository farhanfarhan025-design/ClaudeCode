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
         "amount": panel_sqm * RATES["panel_sqm"], "class": "envelope"},
        {"item": f"{room['name']} — angles",
         "detail": f"{angle_pieces} pcs @ {RATES['angle_piece']:.0f}",
         "amount": angle_pieces * RATES["angle_piece"], "class": "envelope"},
    ]

    doors = room.get("doors", 1)
    if doors:
        lines.append({"item": f"{room['name']} — door",
                      "detail": f"{doors} @ {RATES['door']:.0f}",
                      "amount": doors * RATES["door"], "class": "envelope"})

    if has_floor:
        pairs = math.ceil(floor / RATES["floor_pair_coverage"])
        lines.append({"item": f"{room['name']} — floor (chequered + ply)",
                      "detail": f"{pairs} pairs @ {RATES['floor_pair']:.0f}",
                      "amount": pairs * RATES["floor_pair"], "class": "envelope"})

    unit_rate = RATES["unit_freezer"] if "freez" in kind else RATES["unit_chiller"]
    lines.append({"item": f"{room['name']} — condensing unit + evaporator",
                  "detail": f"{kind} duty, 1 set @ {unit_rate:.0f}",
                  "amount": unit_rate, "class": "equipment"})

    for ln in lines:
        ln["room"] = room["name"]

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
    groups = []          # per room-entry: name, qty, panel sqm, own cost
    for r in rooms:
        rl, sub, panel = room_cost(r)
        lines.extend(rl)
        total_panel += panel
        groups.append({"name": r["name"], "qty": r.get("qty", 1),
                       "panel_sqm": panel, "own_cost": sub})

    # Common / shared items
    common = [
        {"item": "Common — control panels",
         "detail": f"{n_rooms} @ {RATES['control_panel']:.0f}",
         "amount": n_rooms * RATES["control_panel"], "class": "equipment"},
        {"item": "Common — pipe & accessories",
         "detail": f"{n_rooms} systems @ {RATES['pipe_system']:.0f}",
         "amount": n_rooms * RATES["pipe_system"], "class": "equipment"},
        {"item": "Common — wiring",
         "detail": f"{n_rooms} systems @ {RATES['wiring_system']:.0f}",
         "amount": n_rooms * RATES["wiring_system"], "class": "equipment"},
        {"item": "Common — LED vapour-proof lights",
         "detail": f"lump sum for {n_rooms} rooms",
         "amount": RATES["lights_per_2_rooms"] * max(1, round(n_rooms / 2)),
         "class": "equipment"},
    ]
    lines.extend(common)

    for extra in config.get("extras", []):
        lines.append({"item": f"Extra — {extra['item']}",
                      "detail": extra.get("detail", ""),
                      "amount": float(extra["amount"]), "class": "extra"})

    direct = sum(ln["amount"] for ln in lines)
    labour = direct * config.get("labour_pct", LABOUR_PCT)
    transport = config.get("transport", TRANSPORT_DEFAULT)
    cost = direct + labour + transport

    # --- Cost drivers -----------------------------------------------------
    # Envelope scales with room size. Equipment scales with room COUNT. When
    # equipment dominates, room area is a misleading proxy for price — which is
    # exactly how 174/2026 was quoted at -0.3%. See analysis/BACKTEST-2026-08-06.md.
    drivers = {"envelope": 0.0, "equipment": 0.0, "extra": 0.0}
    for ln in lines:
        drivers[ln.get("class", "extra")] += ln["amount"]

    # --- Per-room cost ----------------------------------------------------
    # Common items allocated per room-unit; extras, labour and transport
    # allocated pro-rata. The point is a like-for-like against price per room.
    common_total = sum(ln["amount"] for ln in lines if ln["item"].startswith("Common"))
    extras_total = drivers["extra"]
    per_unit_common = common_total / n_rooms if n_rooms else 0.0

    base = [g["own_cost"] + g["qty"] * per_unit_common for g in groups]
    base_sum = sum(base) or 1.0
    load = (cost / direct) if direct else 1.0

    per_room = []
    for g, b in zip(groups, base):
        share = b + extras_total * (b / base_sum)
        per_room.append({
            "name": g["name"], "qty": g["qty"],
            "panel_sqm": g["panel_sqm"],
            "equipment_set": g["qty"] * per_unit_common,
            "cost": share * load,
        })

    return {
        "lines": lines,
        "direct": direct,
        "labour": labour,
        "labour_pct": config.get("labour_pct", LABOUR_PCT),
        "transport": transport,
        "cost": cost,
        "total_panel_sqm": total_panel,
        "n_rooms": n_rooms,
        "drivers": drivers,
        "per_room": per_room,
        "per_unit_common": per_unit_common * load,
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

    d = b["drivers"]
    env_pct = d["envelope"] / b["direct"] * 100 if b["direct"] else 0
    eqp_pct = d["equipment"] / b["direct"] * 100 if b["direct"] else 0
    A("  COST DRIVERS")
    A(f"  {'Envelope — panel, angles, doors, floor':<44}{money(d['envelope'])}"
      f"   ({env_pct:>5.1f}%)")
    A(f"  {'Equipment & systems — scales with ROOM COUNT':<44}"
      f"{money(d['equipment'])}   ({eqp_pct:>5.1f}%)")
    if d["extra"]:
        A(f"  {'Extras':<44}{money(d['extra'])}")
    if eqp_pct >= env_pct:
        A("")
        A("  *** EQUIPMENT-DRIVEN JOB ***")
        A(f"  Equipment is the larger half of direct cost. Each room adds")
        A(f"  ~{b['per_unit_common']:,.2f} of systems regardless of its size,")
        A(f"  on top of its own condensing unit and evaporator.")
        A("  Pricing this off room area will underprice it.")
    A("=" * 74)

    if b["n_rooms"] > 1 or len(b["per_room"]) > 1:
        A("  COST PER ROOM")
        for r in b["per_room"]:
            label = r["name"] + (f" x{r['qty']}" if r["qty"] > 1 else "")
            A(f"  {label:<28}{r['panel_sqm']:>8.2f} sqm{money(r['cost'])}")
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

        # Area-weighted test: split the proposed price the way the job LOOKS
        # (by panel area) and compare with what each room actually costs.
        # This is the Mecca failure made visible.
        if len(b["per_room"]) > 1 and b["total_panel_sqm"]:
            A("  IF PRICED BY ROOM SIZE (area-weighted)")
            worst = None
            for r in b["per_room"]:
                alloc = proposed * (r["panel_sqm"] / b["total_panel_sqm"])
                gap = alloc - r["cost"]
                flag = "  <-- UNDER COST" if gap < 0 else ""
                A(f"  {r['name']:<20}{money(alloc)} vs cost{money(r['cost'])}"
                  f"{flag}")
                if worst is None or gap < worst[1]:
                    worst = (r["name"], gap)
            if worst and worst[1] < 0:
                A("")
                A(f"  '{worst[0]}' is {abs(worst[1]):,.2f} under its own cost when the")
                A("  price is split by area. Equipment does not scale with size —")
                A("  price the equipment count, not the square metres.")
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
