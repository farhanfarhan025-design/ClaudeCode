#!/usr/bin/env python3
"""
quote_log.py — the missing half of the pricing problem.

`margin.py` tells you what a quote SHOULD be priced at. This tells you what
happened to it afterwards.

Right now only won jobs are recorded (memory/open_loops.md OL-012), so the win
rate is unknown. That single gap is why "the market is too competitive" cannot
be tested: if quotes are being discounted and still lost, the discounting is not
buying the work, and the whole diagnosis changes.

Ten closed quotes is enough to know.

Usage
-----
    # log a quote the day it goes out
    python3 quote_log.py add --ref QUT/DCTS/174/2026 --client "Mecca Trading" \
        --cost 46131.04 --price 46000 --rooms 2 --reason TENDER

    # close it when you hear back
    python3 quote_log.py close --ref QUT/DCTS/174/2026 --outcome won
    python3 quote_log.py close --ref QUT/DCTS/174/2026 --outcome lost --lost-to price

    python3 quote_log.py report

Data lives in a CSV outside version control (DECISIONS.md D-001 — the repo holds
instructions, not operational data). Default: AI-Agent-System/logs/quotes.csv
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import sys

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "logs", "quotes.csv")

FIELDS = ["date", "ref", "client", "rooms", "cost", "price", "markup_pct",
          "reason", "outcome", "outcome_date", "lost_to", "notes"]

OUTCOMES = ("open", "won", "lost", "expired", "withdrawn")
LOST_TO = ("price", "spec", "timing", "relationship", "no-decision", "unknown")

FLOOR_PCT = 20.0          # matches margin.py MARKUP_FLOOR until D-004 is ruled
DEFAULT_PCT = 30.0


def load(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def save(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def f(row, key, default=0.0):
    try:
        return float(row.get(key) or default)
    except ValueError:
        return default


def cmd_add(a):
    rows = load(a.path)
    if any(r["ref"] == a.ref for r in rows):
        print(f"quote_log: {a.ref} already logged", file=sys.stderr)
        return 1
    markup = (a.price - a.cost) / a.cost * 100 if a.cost else 0.0
    rows.append({
        "date": a.date or dt.date.today().isoformat(),
        "ref": a.ref, "client": a.client, "rooms": a.rooms,
        "cost": f"{a.cost:.2f}", "price": f"{a.price:.2f}",
        "markup_pct": f"{markup:.1f}", "reason": a.reason or "",
        "outcome": "open", "outcome_date": "", "lost_to": "", "notes": a.notes or "",
    })
    save(a.path, rows)
    flag = "  *** BELOW FLOOR ***" if markup < FLOOR_PCT else ""
    print(f"logged {a.ref}  markup {markup:.1f}%{flag}")
    return 0


def cmd_close(a):
    rows = load(a.path)
    hit = [r for r in rows if r["ref"] == a.ref]
    if not hit:
        print(f"quote_log: {a.ref} not found", file=sys.stderr)
        return 1
    hit[0]["outcome"] = a.outcome
    hit[0]["outcome_date"] = a.date or dt.date.today().isoformat()
    if a.lost_to:
        hit[0]["lost_to"] = a.lost_to
    save(a.path, rows)
    print(f"{a.ref} → {a.outcome}")
    return 0


def cmd_report(a):
    rows = load(a.path)
    if not rows:
        print("No quotes logged yet. Log the next one the day it goes out.")
        return 0

    closed = [r for r in rows if r["outcome"] in ("won", "lost")]
    won = [r for r in closed if r["outcome"] == "won"]
    lost = [r for r in closed if r["outcome"] == "lost"]
    openq = [r for r in rows if r["outcome"] == "open"]

    print("=" * 68)
    print(f"  QUOTE LOG — {len(rows)} quotes, {len(closed)} closed, {len(openq)} open")
    print("=" * 68)

    if closed:
        wr = len(won) / len(closed) * 100
        print(f"  Win rate                        {wr:>8.1f}%  "
              f"({len(won)} of {len(closed)})")
    else:
        print("  Win rate                          n/a — nothing closed yet")

    if won:
        cost = sum(f(r, "cost") for r in won)
        price = sum(f(r, "price") for r in won)
        print(f"  Weighted realised markup (won)  "
              f"{(price - cost) / cost * 100:>8.1f}%")
        print(f"  Profit on won work              {price - cost:>12,.2f}")

    marks = [f(r, "markup_pct") for r in rows]
    if marks:
        print(f"  Markup spread                   "
              f"{min(marks):>8.1f}%  to {max(marks):.1f}%"
              f"   ({max(marks) - min(marks):.0f} points)")
        below = [r for r in rows if f(r, "markup_pct") < FLOOR_PCT]
        print(f"  Below the {FLOOR_PCT:.0f}% floor              "
              f"{len(below):>8}  of {len(rows)}")

    if lost:
        print("\n  WHY QUOTES WERE LOST")
        reasons = {}
        for r in lost:
            reasons[r["lost_to"] or "unknown"] = reasons.get(r["lost_to"] or "unknown", 0) + 1
        for k, v in sorted(reasons.items(), key=lambda x: -x[1]):
            print(f"    {k:<16}{v}")

        on_price = [r for r in lost if r["lost_to"] == "price"]
        cheap_and_lost = [r for r in on_price if f(r, "markup_pct") < DEFAULT_PCT]
        if cheap_and_lost:
            print(f"\n  *** {len(cheap_and_lost)} quote(s) priced below "
                  f"{DEFAULT_PCT:.0f}% AND still lost on price.")
            print("      Discounting is not buying the work. Raising the floor")
            print("      costs less than you think.")

    print("=" * 68)
    print("  Ten closed quotes makes this real. Until then it is a sample,")
    print("  not a finding.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="TNDK quote outcome log")
    ap.add_argument("--path", default=os.path.normpath(DEFAULT_PATH))
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("add", help="log a quote the day it is issued")
    p.add_argument("--ref", required=True)
    p.add_argument("--client", required=True)
    p.add_argument("--cost", type=float, required=True,
                   help="computed cost from margin.py")
    p.add_argument("--price", type=float, required=True, help="price quoted")
    p.add_argument("--rooms", default="")
    p.add_argument("--reason", default="", help="TENDER/REPEAT/VOLUME/STRATEGIC")
    p.add_argument("--date", default="")
    p.add_argument("--notes", default="")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("close", help="record the outcome")
    p.add_argument("--ref", required=True)
    p.add_argument("--outcome", required=True, choices=OUTCOMES)
    p.add_argument("--lost-to", dest="lost_to", choices=LOST_TO, default="")
    p.add_argument("--date", default="")
    p.set_defaults(func=cmd_close)

    p = sub.add_parser("report", help="win rate and margin distribution")
    p.set_defaults(func=cmd_report)

    a = ap.parse_args(argv)
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
