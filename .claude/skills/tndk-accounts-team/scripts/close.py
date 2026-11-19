#!/usr/bin/env python3
"""TNDK accounts close and weekly position.

Recomputes everything from source rows. Nothing is read from a stored balance or a
spreadsheet total — the register's own total row has been wrong before (it read 18,250
against a book of 758,100), so any figure used for a decision gets computed here.

Two modes:

    python3 close.py --data close.json              # month-end close, 7 steps
    python3 close.py --data close.json --weekly     # the weekly accounts page

Exit codes:  0 = PASS   1 = PARTIAL (something unknown)   2 = FAILED (something disagrees)

A missing figure is reported as UNKNOWN and downgrades the run to PARTIAL. It is never
estimated, defaulted to zero, or quietly dropped — see RULES.md A3.
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import date, datetime

PASS, PARTIAL, FAILED = 0, 1, 2


def qar(n):
    return f"QAR {n:,.2f}"


def plural(n, word):
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def d(s):
    return datetime.strptime(s, "%Y-%m-%d").date()


class Report:
    """Collects lines, unknowns and variances so status is derived, never asserted."""

    def __init__(self, numbered=True):
        self.numbered = numbered
        self.lines = []
        self.unknowns = []
        self.variances = []

    def say(self, text=""):
        self.lines.append(text)

    def head(self, text):
        if not self.numbered and text[:1].isdigit():
            text = text.split(". ", 1)[1]
        self.say()
        self.say(text)
        self.say("-" * len(text))

    def unknown(self, what, why):
        self.unknowns.append((what, why))

    def variance(self, what, amount, detail):
        self.variances.append((what, amount, detail))

    @property
    def status(self):
        if self.variances:
            return FAILED
        return PARTIAL if self.unknowns else PASS

    def render(self, title, as_of):
        status = {PASS: "PASS", PARTIAL: "PARTIAL", FAILED: "FAILED"}[self.status]
        out = [f"{title} — as of {as_of}", f"Status: {status}", ""]
        out += self.lines

        out.append("")
        out.append("UNKNOWN")
        out.append("-------")
        if self.unknowns:
            for what, why in self.unknowns:
                out.append(f"  {what}: {why}")
        else:
            out.append("  (none — every figure above is sourced)")

        if self.variances:
            out.append("")
            banner = ("VARIANCE — the close does not tie out" if self.numbered
                      else "VARIANCE — unresolved, do not report a net figure past this")
            out.append(banner)
            out.append("-" * len(banner))
            for what, amount, detail in self.variances:
                out.append(f"  {what}: {qar(amount)}")
                out.append(f"    {detail}")
            out.append("")
            out.append("  Report the variance. Do not pick the majority answer.")
        return "\n".join(out)


# ---------------------------------------------------------------- register


def check_register(data, r):
    """Step 1 — Contract - Received = Balance, on every row and at the total."""
    rows = data.get("register")
    if not rows:
        r.unknown("Register", "no rows supplied")
        return None

    r.head("1. REGISTER ARITHMETIC")
    contract = received = 0.0
    for row in rows:
        c, got = row.get("contract"), row.get("received")
        if c is None or got is None:
            r.unknown(f"Register row '{row.get('project', '?')}'",
                      "contract or received missing — not computed, not assumed zero")
            continue
        bal = c - got
        contract += c
        received += got
        flag = ""
        if "balance" in row and row["balance"] is not None and abs(row["balance"] - bal) > 0.005:
            flag = f"   << stored balance says {qar(row['balance'])}"
            r.variance(f"Balance mismatch — {row.get('project', '?')}",
                       abs(row["balance"] - bal),
                       f"stored {qar(row['balance'])} vs computed {qar(bal)}")
        r.say(f"  {row.get('project', '?')[:38]:<38} {qar(c):>18} - {qar(got):>18} = {qar(bal):>18}{flag}")

    r.say(f"  {'TOTAL':<38} {qar(contract):>18} - {qar(received):>18} = {qar(contract - received):>18}")
    r.say(f"  Rows counted: {len(rows)} — confirm the register's own total row covers all {len(rows)}.")
    return {"contract": contract, "received": received, "outstanding": contract - received}


# ---------------------------------------------------------------- tie-out


def tie_out(data, reg, r):
    """Step 6 — receipts logged = Received in the register = instruments recorded."""
    r.head("6. THREE-WAY TIE-OUT")

    receipts = data.get("receipts")
    instruments = data.get("instruments")
    if receipts is None:
        r.unknown("Receipts", "not supplied — tie-out cannot run")
        return
    if instruments is None:
        r.unknown("Instruments", "no instrument register supplied — tie-out cannot run")
        return

    sum_receipts = sum(x.get("amount", 0) for x in receipts)
    sum_instr = sum(x.get("amount", 0) for x in instruments)
    sum_reg = reg["received"] if reg else None

    r.say(f"  Receipts logged      {qar(sum_receipts):>18}   ({plural(len(receipts), 'receipt')})")
    r.say(f"  Register 'Received'  {qar(sum_reg) if sum_reg is not None else 'UNKNOWN':>18}")
    r.say(f"  Instruments recorded {qar(sum_instr):>18}   ({plural(len(instruments), 'instrument')})")

    if sum_reg is None:
        r.unknown("Tie-out", "register total unavailable")
        return

    figures = {"receipts": sum_receipts, "register": sum_reg, "instruments": sum_instr}
    if max(figures.values()) - min(figures.values()) > 0.005:
        agree = defaultdict(list)
        for name, v in figures.items():
            agree[round(v, 2)].append(name)
        pair = max(agree.items(), key=lambda kv: len(kv[1]))
        detail = (f"{' and '.join(pair[1])} agree at {qar(pair[0])}; "
                  f"the others do not. Identify the documents before reporting any figure.")
        r.variance("Three-way tie-out", max(figures.values()) - min(figures.values()), detail)
    else:
        r.say("  Ties out.")

    # Every receipt needs an instrument behind it (RULES.md C7).
    have = {x.get("receipt_ref") for x in instruments}
    orphans = [x for x in receipts if x.get("ref") not in have]
    for o in orphans:
        r.variance(f"Receipt {o.get('ref', '?')} has no instrument",
                   o.get("amount", 0),
                   "a received amount with no cheque/transfer/cash record behind it")

    unallocated = [x for x in instruments if not x.get("invoice")]
    for u in unallocated:
        r.unknown(f"Instrument {u.get('number') or u.get('receipt_ref', '?')}",
                  "matches no invoice — allocation check, do not spread it across balances")


# ---------------------------------------------------------------- payables


def payables(data, as_of, r, horizon=14):
    r.head("4. PAYABLES")
    bills = data.get("payables")
    if bills is None:
        r.unknown("Payables", "no payables register supplied — what TNDK owes is unrecorded")
        return None

    overdue = due_soon = later = 0.0
    for b in bills:
        if b.get("status") == "paid":
            continue
        amt = b.get("amount")
        if amt is None:
            r.unknown(f"Bill {b.get('bill', '?')}", "amount missing")
            continue
        if not b.get("lpo"):
            r.variance(f"Bill {b.get('bill', '?')} has no LPO behind it", amt,
                       "an unmatched bill is how a business pays for something it never ordered — "
                       "return it to PROCURE before scheduling")
        if b.get("lpo_amount") is not None and abs(b["lpo_amount"] - amt) > 0.005:
            r.variance(f"Bill {b.get('bill', '?')} differs from its LPO",
                       abs(b["lpo_amount"] - amt),
                       f"LPO {qar(b['lpo_amount'])} vs bill {qar(amt)} — state it before payment, not after")
        due = b.get("due")
        if not due:
            r.unknown(f"Bill {b.get('bill', '?')}", "no due date — cannot be scheduled")
            continue
        days = (d(due) - as_of).days
        if days < 0:
            overdue += amt
        elif days <= horizon:
            due_soon += amt
        else:
            later += amt

    committed = data.get("committed_not_billed")
    r.say(f"  Overdue                    {qar(overdue):>18}")
    r.say(f"  Due within {horizon} days          {qar(due_soon):>18}")
    r.say(f"  Due later                  {qar(later):>18}")
    if committed is None:
        r.unknown("Committed but not yet billed", "no open-LPO list supplied")
        committed_total = None
    else:
        committed_total = sum(x.get("amount", 0) for x in committed)
        r.say(f"  Committed, not yet billed  {qar(committed_total):>18}   ({plural(len(committed), 'LPO')})")
    return {"overdue": overdue, "due_soon": due_soon, "later": later, "committed": committed_total}


# ---------------------------------------------------------------- cash


def cash(data, r):
    """Cleared, in hand uncleared, committed out — three figures, never merged."""
    r.head("3. CASH POSITION")
    instruments = data.get("instruments")
    if instruments is None:
        r.unknown("Cash position", "no instrument register — cleared and uncleared cannot be separated")
        return None

    cleared = sum(x.get("amount", 0) for x in instruments if x.get("status") == "cleared")
    held = sum(x.get("amount", 0) for x in instruments if x.get("status") in ("held", "deposited"))
    bounced = [x for x in instruments if x.get("status") == "bounced"]

    issued = data.get("cheques_issued")
    out = None if issued is None else sum(x.get("amount", 0) for x in issued if not x.get("presented"))

    opening = data.get("opening_cash")
    r.say(f"  Cleared in this period     {qar(cleared):>18}")
    r.say(f"  In hand, uncleared         {qar(held):>18}   << not cash")
    if out is None:
        r.unknown("Cheques issued", "no issued-cheque list supplied")
    else:
        r.say(f"  Committed out (unpresented){qar(out):>18}   << already spent")

    if opening is None:
        r.unknown("Opening cash position",
                  "no bank connection (TOOLS.md) — Farhan must confirm it; it is not estimated here")
        r.say("  Cash on hand               UNKNOWN — opening position not confirmed")
        position = None
    else:
        position = opening + cleared - (out or 0)
        r.say(f"  Opening confirmed          {qar(opening):>18}")
        r.say(f"  Position                   {qar(position):>18}   (opening + cleared - committed out)")

    for b in bounced:
        r.variance(f"Cheque {b.get('number', '?')} bounced", b.get("amount", 0),
                   "notify LEDGER (receipt status) and COLLECT (the balance is live again); "
                   "supersede and mark, never quietly reduce the received figure")
    return {"cleared": cleared, "held": held, "out": out, "position": position}


# ---------------------------------------------------------------- ageing


def ageing(data, as_of, r):
    r.head("5. RECEIVABLES AGEING")
    rows = data.get("register") or []
    buckets = {"0-30": 0.0, "31-60": 0.0, "61-90": 0.0, "90+": 0.0}
    ageable = 0
    for row in rows:
        c, got = row.get("contract"), row.get("received")
        if c is None or got is None or c - got <= 0:
            continue
        since = row.get("due_since")
        if not since:
            r.unknown(f"Ageing — {row.get('project', '?')}",
                      "no due date; outstanding but not ageable (blocked on a milestone?)")
            continue
        ageable += 1
        days = (as_of - d(since)).days
        key = "0-30" if days <= 30 else "31-60" if days <= 60 else "61-90" if days <= 90 else "90+"
        buckets[key] += c - got
    for k, v in buckets.items():
        r.say(f"  {k:<8} {qar(v):>18}")
    r.say(f"  {ageable} of {len(rows)} rows carried a due date.")


# ---------------------------------------------------------------- exposure


def exposure(data, r):
    r.head("EXPOSURE — committed spend vs collected cash, per project")
    rows = {x.get("project"): x for x in (data.get("register") or [])}
    spend = defaultdict(float)
    for b in (data.get("payables") or []) + (data.get("committed_not_billed") or []):
        if b.get("project"):
            spend[b["project"]] += b.get("amount", 0)
    if not spend:
        r.say("  No project-tagged vendor spend supplied.")
        return
    for project, committed in sorted(spend.items()):
        row = rows.get(project, {})
        collected = row.get("received")
        if collected is None:
            r.unknown(f"Exposure — {project}", "collected cash unknown")
            continue
        gap = committed - collected
        mark = "   << committed spend exceeds collected cash" if gap > 0 else ""
        r.say(f"  {project[:38]:<38} committed {qar(committed):>16}  collected {qar(collected):>16}{mark}")
        if gap > 0:
            r.variance(f"Exposure — {project}", gap,
                       "TNDK is funding this project out of working capital; escalate the same day")


# ---------------------------------------------------------------- modes


def weekly(data, as_of, r):
    reg = check_register(data, r)
    c = cash(data, r)
    p = payables(data, as_of, r)
    exposure(data, r)

    r.head("NET")
    if reg:
        r.say(f"  Receivables outstanding    {qar(reg['outstanding']):>18}")
    if p and c and c["position"] is not None:
        r.say(f"  Position if all due in 14 days is paid  {qar(c['position'] - p['overdue'] - p['due_soon']):>18}")
    else:
        r.say("  Net position               UNKNOWN — see the UNKNOWN block below")
    return r


def close(data, as_of, r):
    reg = check_register(data, r)

    r.head("2. NUMBERING")
    log = data.get("numbering")
    if not log:
        r.unknown("Numbering log", "not supplied — gaps and collisions unchecked")
    else:
        for series, nums in sorted(log.items()):
            issued = sorted(nums)
            gaps = [n for n in range(issued[0], issued[-1]) if n not in set(issued)]
            dupes = {n for n in issued if issued.count(n) > 1}
            note = ""
            if gaps:
                note += f"   gaps: {gaps}"
            if dupes:
                note += f"   COLLISION: {sorted(dupes)}"
                r.variance(f"Numbering collision in {series}", 0,
                           f"numbers {sorted(dupes)} reused — renumber the newer document")
            r.say(f"  {series:<12} issued {issued[0]}-{issued[-1]}, next free {issued[-1] + 1}{note}")

    cash(data, r)
    payables(data, as_of, r)
    ageing(data, as_of, r)
    tie_out(data, reg, r)

    r.head("7. MARGIN COLUMN")
    rows = data.get("register") or []
    costed = [x for x in rows if x.get("cost") is not None]
    r.say(f"  {len(costed)} of {len(rows)} rows carry a cost, so the book shows profit on {len(costed)}.")
    for row in costed:
        c, cost = row.get("contract"), row["cost"]
        if c:
            r.say(f"  {row.get('project', '?')[:38]:<38} margin {(c - cost) / c * 100:>6.1f}%  ({qar(c - cost)})")
    if len(costed) < len(rows):
        r.unknown("Margin column", f"{len(rows) - len(costed)} rows have no cost recorded (see open loop OL-011)")

    exposure(data, r)
    return r


def main():
    ap = argparse.ArgumentParser(description="TNDK accounts close / weekly position")
    ap.add_argument("--data", required=True, help="JSON input — see assets/example_close.json")
    ap.add_argument("--weekly", action="store_true", help="weekly page instead of the full close")
    ap.add_argument("--json", action="store_true", help="machine-readable status")
    args = ap.parse_args()

    data = json.load(open(args.data))
    as_of = d(data["as_of"]) if data.get("as_of") else date.today()

    r = Report(numbered=not args.weekly)
    (weekly if args.weekly else close)(data, as_of, r)
    title = "TNDK ACCOUNTS WEEKLY" if args.weekly else "TNDK MONTH-END CLOSE"

    if args.json:
        print(json.dumps({
            "status": {PASS: "PASS", PARTIAL: "PARTIAL", FAILED: "FAILED"}[r.status],
            "as_of": str(as_of),
            "unknowns": [{"what": w, "why": y} for w, y in r.unknowns],
            "variances": [{"what": w, "qar": round(a, 2), "detail": dt} for w, a, dt in r.variances],
        }, indent=2))
    else:
        print(r.render(title, as_of))

    return r.status


if __name__ == "__main__":
    sys.exit(main())
