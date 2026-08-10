#!/usr/bin/env python3
"""
deal_check.py — RAIS's arithmetic for a job-take decision.

Answers the questions a verdict needs numbers for:

  * What is the realised margin, honestly costed?
  * How much of Farhan's own cash does this job consume, and for how long?
  * What does he earn on the cash he puts at risk?
  * What does this contract do to client concentration?
  * Which of the STOP gates in verdict-engine.md trip?

This is arithmetic, not judgement. It tells RAIS what is true; RAIS still decides.

Usage
-----
    python3 deal_check.py --config examples/sample_job.json
    python3 deal_check.py --config job.json --json          # machine-readable
    python3 deal_check.py --value 46000 --direct 30000 \
                          --schedule 60@0,40@45 --duration 30

Exit codes
----------
    0  no STOP gate tripped
    1  bad input
    2  at least one STOP gate tripped
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict

# Defaults. Every one of these is overridable per job in the config.
# The margin floor is a PROPOSAL pending Farhan's ruling — DECISIONS.md D-004.
DEFAULT_MARGIN_FLOOR_PCT = 22.0
DEFAULT_NEW_CLIENT_FLOOR_PCT = 30.0
DEFAULT_OVERHEAD_PCT = 0.0
CONCENTRATION_WARN_PCT = 25.0
CONCENTRATION_STOP_PCT = 50.0

STOP, WARN, OK = "STOP", "WARN", "OK"


def qar(x: float) -> str:
    return f"QAR {x:,.2f}"


def pct(x: float) -> str:
    return f"{x:,.1f}%"


# --------------------------------------------------------------------------
# Input
# --------------------------------------------------------------------------

@dataclass
class Milestone:
    pct: float
    trigger: str = ""
    expected_day: int = 0


@dataclass
class Job:
    job: str = "unnamed job"
    client: str = "unnamed client"

    contract_value: float = 0.0

    direct_cost: float = 0.0          # materials, panels, units, doors
    labour_cost: float = 0.0
    transport_cost: float = 0.0
    other_cost: float = 0.0
    overhead_pct: float = DEFAULT_OVERHEAD_PCT   # % of direct cost

    duration_days: int = 30
    material_order_day: int = 0       # day materials are committed
    vendor_payment_days: int = 30     # days after order that the vendor is paid

    payment_schedule: list = field(default_factory=list)
    retention_pct: float = 0.0
    retention_release_day: int | None = None

    # Context — optional, but each one unlocks a gate
    current_book: float | None = None
    client_existing_book: float = 0.0
    cash_in_hand: float | None = None

    new_client: bool = False
    penalty_clause: bool = False
    verbal_award: bool = False
    unverified_rates: bool = False

    margin_floor_pct: float = DEFAULT_MARGIN_FLOOR_PCT
    new_client_floor_pct: float = DEFAULT_NEW_CLIENT_FLOOR_PCT

    @classmethod
    def from_dict(cls, d: dict) -> "Job":
        known = {f for f in cls.__dataclass_fields__}
        unknown = set(d) - known
        if unknown:
            raise ValueError(f"unknown config key(s): {', '.join(sorted(unknown))}")
        d = dict(d)
        d["payment_schedule"] = [
            Milestone(**m) if isinstance(m, dict) else m
            for m in d.get("payment_schedule", [])
        ]
        return cls(**d)


# --------------------------------------------------------------------------
# Arithmetic
# --------------------------------------------------------------------------

def cost_buildup(j: Job) -> dict:
    overhead = j.direct_cost * j.overhead_pct / 100.0
    total = j.direct_cost + j.labour_cost + j.transport_cost + j.other_cost + overhead
    profit = j.contract_value - total
    return {
        "direct": j.direct_cost,
        "labour": j.labour_cost,
        "transport": j.transport_cost,
        "other": j.other_cost,
        "overhead": overhead,
        "total_cost": total,
        "profit": profit,
        # Margin on price (what the client pays) and markup on cost (what the
        # pricing guide calls markup). Both are reported — they are not the same
        # number and confusing them is how 30% becomes 14.6%.
        "margin_on_price_pct": (profit / j.contract_value * 100.0) if j.contract_value else 0.0,
        "markup_on_cost_pct": (profit / total * 100.0) if total else 0.0,
    }


def cash_events(j: Job, costs: dict) -> list[tuple[int, float, str]]:
    """(day, amount, label). Positive = cash in."""
    ev: list[tuple[int, float, str]] = []

    retained = j.contract_value * j.retention_pct / 100.0
    billable = j.contract_value - retained

    for m in j.payment_schedule:
        ev.append((m.expected_day, billable * m.pct / 100.0,
                   f"receipt {m.pct:g}% {m.trigger}".strip()))

    if retained > 0:
        day = j.retention_release_day
        # No stated release date is itself a finding; model it as far out so the
        # exposure is visible rather than assumed away.
        ev.append((day if day is not None else j.duration_days + 365,
                   retained, "retention release"))

    ev.append((j.material_order_day + j.vendor_payment_days,
               -(j.direct_cost + costs["other"]), "vendor payment"))
    if j.labour_cost:
        ev.append((j.duration_days, -j.labour_cost, "labour"))
    if j.transport_cost:
        ev.append((j.duration_days, -j.transport_cost, "transport"))
    if costs["overhead"]:
        ev.append((j.duration_days, -costs["overhead"], "overhead"))

    ev.sort(key=lambda e: (e[0], e[1]))
    return ev


def cash_profile(events: list[tuple[int, float, str]]) -> dict:
    running = 0.0
    peak_exposure = 0.0       # worst cumulative deficit, as a positive number
    peak_day = 0
    ledger = []
    negative_days: set[int] = set()
    prev_day = None

    for day, amt, label in events:
        if prev_day is not None and running < 0:
            negative_days.update(range(prev_day, day))
        running += amt
        if running < -peak_exposure:
            peak_exposure, peak_day = -running, day
        ledger.append({"day": day, "amount": amt, "label": label, "running": running})
        prev_day = day

    first_in = next((d for d, a, _ in events if a > 0), None)
    first_out = next((d for d, a, _ in events if a < 0), None)

    return {
        "ledger": ledger,
        "peak_exposure": peak_exposure,
        "peak_day": peak_day,
        "days_cash_out": len(negative_days),
        "first_inflow_day": first_in,
        "first_outflow_day": first_out,
        "closing": running,
    }


def returns(costs: dict, cash: dict) -> dict:
    exposure = cash["peak_exposure"]
    days = max(cash["days_cash_out"], 1)
    rowc = (costs["profit"] / exposure * 100.0) if exposure > 0 else None
    return {
        "return_on_working_capital_pct": rowc,
        "annualised_pct": (rowc * 365.0 / days) if rowc is not None else None,
        "days_cash_out": cash["days_cash_out"],
    }


def concentration(j: Job) -> dict | None:
    if j.current_book is None:
        return None
    book_after = j.current_book + j.contract_value
    client_after = j.client_existing_book + j.contract_value
    return {
        "book_after": book_after,
        "client_after": client_after,
        "client_share_pct": (client_after / book_after * 100.0) if book_after else 0.0,
    }


# --------------------------------------------------------------------------
# Gates — verdict-engine.md step 3
# --------------------------------------------------------------------------

def gates(j: Job, costs: dict, cash: dict, conc: dict | None) -> list[dict]:
    g: list[dict] = []

    def add(level, name, detail):
        g.append({"level": level, "gate": name, "detail": detail})

    floor = j.new_client_floor_pct if j.new_client else j.margin_floor_pct
    label = "new-client floor" if j.new_client else "margin floor"
    m = costs["markup_on_cost_pct"]
    if m < j.margin_floor_pct:
        add(STOP, "margin floor",
            f"markup on cost {pct(m)} is below the {pct(j.margin_floor_pct)} floor")
    elif m < floor:
        add(WARN, label,
            f"markup on cost {pct(m)} is below the {pct(floor)} expected for a new client")
    else:
        add(OK, label, f"markup on cost {pct(m)}")

    fi, fo = cash["first_inflow_day"], cash["first_outflow_day"]
    if fo is not None and (fi is None or fi > fo):
        add(STOP, "cash-out-first",
            "money leaves before any client money arrives — restructure the schedule")
    else:
        add(OK, "cash-out-first", "client money arrives before or with the first outflow")

    advance = sum(m.pct for m in j.payment_schedule if m.expected_day <= 0)
    if advance <= 0 and j.direct_cost > 0:
        add(STOP, "no advance",
            f"no advance, with {qar(j.direct_cost)} of material to commit")
    elif advance < 15:
        add(WARN, "thin advance", f"advance is only {pct(advance)} of contract")
    else:
        add(OK, "advance", f"{pct(advance)} advance")

    if j.cash_in_hand is not None:
        if cash["peak_exposure"] > j.cash_in_hand:
            add(STOP, "exposure vs cash",
                f"peak exposure {qar(cash['peak_exposure'])} exceeds "
                f"cash in hand {qar(j.cash_in_hand)}")
        else:
            add(OK, "exposure vs cash",
                f"peak exposure {qar(cash['peak_exposure'])} within "
                f"cash in hand {qar(j.cash_in_hand)}")

    if j.retention_pct > 0 and j.retention_release_day is None:
        add(WARN, "retention",
            f"{pct(j.retention_pct)} retention with no stated release date — "
            "get the date in writing before signing")

    if j.verbal_award:
        add(STOP, "verbal award",
            "no written award — do not commit material until it is in writing")

    if j.penalty_clause:
        add(WARN, "penalty clause",
            "penalty/LD clause present — confirm it is capped and priced in")

    if j.unverified_rates:
        add(WARN, "unverified rates",
            "costed off an unverified rate card — get dated vendor quotes first")

    if conc:
        s = conc["client_share_pct"]
        if s >= CONCENTRATION_STOP_PCT:
            add(STOP, "concentration",
                f"this client becomes {pct(s)} of the book")
        elif s >= CONCENTRATION_WARN_PCT:
            add(WARN, "concentration",
                f"this client becomes {pct(s)} of the book")
        else:
            add(OK, "concentration", f"client share after award {pct(s)}")

    return g


def suggest(costs: dict, g: list[dict], ret: dict) -> str:
    """Mechanical starting point only. RAIS forms the actual verdict."""
    if any(x["level"] == STOP for x in g):
        return "DON'T DO IT — or restructure until the STOP gates clear"
    if any(x["level"] == WARN for x in g):
        return "DO IT, BUT — clear the warnings below first"
    r = ret["annualised_pct"]
    if costs["markup_on_cost_pct"] >= 30 and (r is None or r >= 50):
        return "DO IT"
    return "DO IT — nothing trips, margin is adequate"


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------

def report(j: Job, costs, cash, ret, conc, g) -> str:
    L = []
    w = L.append
    w("=" * 68)
    w(f"DEAL CHECK — {j.job}  ({j.client})")
    w("=" * 68)
    w("")
    w("COST BUILD-UP")
    w(f"  Direct (materials)          {costs['direct']:>14,.2f}")
    w(f"  Labour                      {costs['labour']:>14,.2f}")
    w(f"  Transport                   {costs['transport']:>14,.2f}")
    w(f"  Other                       {costs['other']:>14,.2f}")
    w(f"  {f'Overhead ({j.overhead_pct:g}% of direct)':<26}{costs['overhead']:>14,.2f}")
    w(f"  {'-' * 42}")
    w(f"  Total cost                  {costs['total_cost']:>14,.2f}")
    w(f"  Contract value              {j.contract_value:>14,.2f}")
    w(f"  Profit                      {costs['profit']:>14,.2f}")
    w("")
    w(f"  Markup on cost              {costs['markup_on_cost_pct']:>13,.1f}%   "
      f"(floor {j.margin_floor_pct:g}%)")
    w(f"  Margin on price             {costs['margin_on_price_pct']:>13,.1f}%")
    w("")
    w("CASH TIMELINE")
    for e in cash["ledger"]:
        w(f"  day {e['day']:>4}  {e['amount']:>13,.2f}  {e['label']:<26} "
          f"running {e['running']:>13,.2f}")
    w("")
    w(f"  Peak cash exposure          {cash['peak_exposure']:>14,.2f}  "
      f"(day {cash['peak_day']})")
    w(f"  Days with his cash out      {cash['days_cash_out']:>14}")
    if ret["return_on_working_capital_pct"] is not None:
        w(f"  Return on capital at risk   {ret['return_on_working_capital_pct']:>13,.1f}%"
          f"   ({ret['annualised_pct']:,.0f}% annualised)")
    else:
        w("  Return on capital at risk        n/a — no cash exposure")
    if conc:
        w("")
        w("CONCENTRATION")
        w(f"  Book after award            {conc['book_after']:>14,.2f}")
        w(f"  This client                 {conc['client_after']:>14,.2f}  "
          f"= {conc['client_share_pct']:,.1f}% of book")
    w("")
    w("GATES")
    for x in g:
        mark = {STOP: "STOP", WARN: "WARN", OK: " ok "}[x["level"]]
        w(f"  [{mark}] {x['gate']:<22} {x['detail']}")
    w("")
    w(f"SUGGESTED STARTING POINT: {suggest(costs, g, ret)}")
    w("")
    w("  Arithmetic only. RAIS weighs capacity, relationship, strategy and")
    w("  what the alternative use of the slot is worth before giving a verdict.")
    w("=" * 68)
    return "\n".join(L)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def parse_schedule(s: str) -> list[Milestone]:
    """'60@0,40@45' or '60@0:advance,40@45:delivery'"""
    out = []
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        head, _, trigger = part.partition(":")
        p, _, day = head.partition("@")
        out.append(Milestone(pct=float(p), trigger=trigger, expected_day=int(day or 0)))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="RAIS deal check")
    ap.add_argument("--config", help="JSON job file")
    ap.add_argument("--value", type=float, help="contract value")
    ap.add_argument("--direct", type=float, help="direct/material cost")
    ap.add_argument("--labour", type=float, default=0.0)
    ap.add_argument("--transport", type=float, default=0.0)
    ap.add_argument("--overhead-pct", type=float)
    ap.add_argument("--schedule", help="e.g. 60@0,40@45")
    ap.add_argument("--duration", type=int, help="duration in days")
    ap.add_argument("--floor", type=float, help="margin floor %% (markup on cost)")
    ap.add_argument("--cash-in-hand", type=float)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    a = ap.parse_args(argv)

    try:
        if a.config:
            with open(a.config) as f:
                j = Job.from_dict(json.load(f))
        else:
            if a.value is None or a.direct is None:
                ap.error("give --config, or at least --value and --direct")
            j = Job(contract_value=a.value, direct_cost=a.direct)

        if a.value is not None:
            j.contract_value = a.value
        if a.direct is not None:
            j.direct_cost = a.direct
        if a.labour:
            j.labour_cost = a.labour
        if a.transport:
            j.transport_cost = a.transport
        if a.overhead_pct is not None:
            j.overhead_pct = a.overhead_pct
        if a.schedule:
            j.payment_schedule = parse_schedule(a.schedule)
        if a.duration is not None:
            j.duration_days = a.duration
        if a.floor is not None:
            j.margin_floor_pct = a.floor
        if a.cash_in_hand is not None:
            j.cash_in_hand = a.cash_in_hand

        if j.contract_value <= 0:
            raise ValueError("contract_value must be positive")
        total_pct = sum(m.pct for m in j.payment_schedule)
        if j.payment_schedule and abs(total_pct - 100.0) > 0.01:
            raise ValueError(f"payment schedule sums to {total_pct:g}%, not 100%")
        if not j.payment_schedule:
            raise ValueError("no payment schedule — that is itself the finding; "
                             "ask for the terms before pricing")
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as e:
        print(f"deal_check: {e}", file=sys.stderr)
        return 1

    costs = cost_buildup(j)
    cash = cash_profile(cash_events(j, costs))
    ret = returns(costs, cash)
    conc = concentration(j)
    g = gates(j, costs, cash, conc)

    if a.json:
        print(json.dumps({
            "job": asdict(j) | {"payment_schedule":
                                [asdict(m) for m in j.payment_schedule]},
            "costs": costs, "cash": cash, "returns": ret,
            "concentration": conc, "gates": g,
            "suggested": suggest(costs, g, ret),
        }, indent=2, default=str))
    else:
        print(report(j, costs, cash, ret, conc, g))

    return 2 if any(x["level"] == STOP for x in g) else 0


if __name__ == "__main__":
    sys.exit(main())
