#!/usr/bin/env python3
"""
TNDK pipeline and quote-conversion calculator.

The business currently records won jobs and nothing else. Quotation numbering has
reached QUT/DCTS/066/2026; eight awards are recorded anywhere in the system. So the
win rate is unknown, and with it the answer to the question that decides whether the
margin floor costs anything: DOES QUOTING LOW ACTUALLY WIN THE WORK?

This script computes what the register cannot:

  1. conversion rate, by count and by value,
  2. win rate broken down by the margin tier the job was quoted at,
  3. weighted open pipeline, with age decay,
  4. every quotation that is past validity or has gone quiet, and
  5. what each open quotation would do to client concentration if won.

Two deliberate refusals, both learned from analysis/FINDINGS.md:

  - It will not print a win-rate percentage computed from fewer than
    MIN_DECIDED_FOR_RATE decided quotes. A percentage derived from n=2 looks
    exactly like one derived from n=200. (lessons.md L-002)
  - It will not silently use an assumed win probability. When the observed rate is
    too thin to use, it says so in a banner, every run.

Usage
-----
    python3 pipeline.py --data pipeline.json
    python3 pipeline.py --data pipeline.json --awards examples/awards.json
    python3 pipeline.py --data pipeline.json --json          # machine-readable
    python3 pipeline.py --data pipeline.json --as-of 2026-08-03

Exit code 2 = one or more quotations require action (past validity, or quiet).
Data format: see scripts/examples/pipeline.json
"""

import argparse
import json
import sys
from datetime import date, datetime

# --- Policy constants ------------------------------------------------------
# Validity is Farhan's documented standard (memory/preferences.md, "Commercial").
VALIDITY_DAYS = 15

# A quotation with no client contact for three weeks is not "still open", it is
# unrecorded. This threshold drives the manager's standing weekly quiet list.
QUIET_DAYS = 21

# Below this many decided quotes, a win rate is a coincidence, not a rate.
MIN_DECIDED_FOR_RATE = 20
# Below this many decided quotes in a single tier, no per-tier rate is printed.
MIN_DECIDED_PER_TIER = 5

# Used only when the observed rate is too thin. ALWAYS reported as an assumption.
ASSUMED_WIN_RATE = 0.30

# Age decay on open quotations. A quote inside its validity carries full weight;
# past that, the probability it converts falls whatever the client says.
AGE_WEIGHTS = [(VALIDITY_DAYS, 1.00), (30, 0.60), (60, 0.30), (10**6, 0.10)]

OPEN_STATUSES = {"open"}
DECIDED_STATUSES = {"won", "lost"}
CLOSED_NO_DECISION = {"expired", "withdrawn"}
ALL_STATUSES = OPEN_STATUSES | DECIDED_STATUSES | CLOSED_NO_DECISION

REQUIRED_FIELDS = ("ref", "client", "value", "date_sent", "status")


def parse_date(s):
    return datetime.strptime(s, "%Y-%m-%d").date()


def days_between(a, b):
    return (b - a).days


def age_weight(days_open):
    for limit, w in AGE_WEIGHTS:
        if days_open <= limit:
            return w
    return AGE_WEIGHTS[-1][1]


def validate(quotes):
    """Fail loudly rather than report a plausible-looking pipeline."""
    seen = set()
    for i, q in enumerate(quotes, start=1):
        for f in REQUIRED_FIELDS:
            if f not in q:
                raise ValueError(f"quote #{i}: missing required field '{f}'")
        if q["status"] not in ALL_STATUSES:
            raise ValueError(f"{q['ref']}: unknown status '{q['status']}' "
                             f"(expected one of {sorted(ALL_STATUSES)})")
        if q["ref"] in seen:
            raise ValueError(f"{q['ref']}: duplicate quotation reference — "
                             f"a reused number is a RULES.md A7 violation")
        seen.add(q["ref"])
        if q["status"] in DECIDED_STATUSES and not q.get("decided_date"):
            raise ValueError(f"{q['ref']}: status '{q['status']}' with no decided_date")
        if q["status"] == "lost" and not q.get("loss_reason"):
            raise ValueError(f"{q['ref']}: lost with no loss_reason — "
                             f"the reason is the entire point of this register")


def analyse(data, as_of):
    quotes = data["quotes"]
    validate(quotes)

    open_rows, decided, expired = [], [], []

    for q in quotes:
        sent = parse_date(q["date_sent"])
        value = float(q["value"])

        if q["status"] in OPEN_STATUSES:
            days_open = days_between(sent, as_of)
            last = parse_date(q["last_contact"]) if q.get("last_contact") else sent
            days_quiet = days_between(last, as_of)
            w = age_weight(days_open)
            flags = []
            if days_open > VALIDITY_DAYS:
                flags.append("PAST VALIDITY")
            if days_quiet >= QUIET_DAYS:
                flags.append("QUIET")
            open_rows.append({
                "ref": q["ref"], "client": q["client"], "value": value,
                "tier": q.get("tier"), "days_open": days_open, "days_quiet": days_quiet,
                "weight": w, "weighted": value * w, "flags": flags,
                "next_action": q.get("next_action"),
                "next_action_date": q.get("next_action_date"),
            })
        elif q["status"] in DECIDED_STATUSES:
            dec = parse_date(q["decided_date"])
            decided.append({
                "ref": q["ref"], "client": q["client"], "value": value,
                "tier": q.get("tier"), "won": q["status"] == "won",
                "days_to_decide": days_between(sent, dec),
                "loss_reason": q.get("loss_reason"),
                # Reconstructed = recovered from the award register, which only ever
                # recorded wins. Counted, but never allowed into a rate.
                "reconstructed": bool(q.get("reconstructed")) or q.get("tier") == "unrecorded",
            })
        else:
            expired.append({"ref": q["ref"], "client": q["client"], "value": value,
                            "status": q["status"]})

    won = [d for d in decided if d["won"]]
    lost = [d for d in decided if not d["won"]]

    # Only quotes that were tracked from issue to decision can produce a rate.
    tracked = [d for d in decided if not d["reconstructed"]]
    reconstructed = [d for d in decided if d["reconstructed"]]
    tracked_won = [d for d in tracked if d["won"]]

    n_decided = len(decided)
    n_tracked = len(tracked)
    rate_known = n_tracked >= MIN_DECIDED_FOR_RATE
    win_rate = (len(tracked_won) / n_tracked) if n_tracked else None
    value_rate = (sum(d["value"] for d in tracked_won) /
                  sum(d["value"] for d in tracked)) if n_tracked else None

    base_rate = win_rate if rate_known else ASSUMED_WIN_RATE

    # Per-tier win rate — the G1 answer. Suppressed until each tier has enough rows.
    tiers = {}
    for d in decided:
        t = d["tier"] or "unrecorded"
        tiers.setdefault(t, {"n": 0, "won": 0, "value": 0.0, "won_value": 0.0})
        tiers[t]["n"] += 1
        tiers[t]["value"] += d["value"]
        if d["won"]:
            tiers[t]["won"] += 1
            tiers[t]["won_value"] += d["value"]
    for t, v in tiers.items():
        # "unrecorded" is the historic backlog, reconstructed from the award register —
        # which only ever recorded jobs that were WON. Its win rate is therefore ~100%
        # by construction. Printing it as a rate would be the most misleading number in
        # the file, so it never gets one.
        v["survivorship"] = (t == "unrecorded")
        v["rate"] = None if v["survivorship"] or v["n"] < MIN_DECIDED_PER_TIER \
            else v["won"] / v["n"]

    unweighted = sum(r["value"] for r in open_rows)
    # Age weight scales the base conversion probability; it does not replace it.
    weighted = sum(r["weighted"] * base_rate for r in open_rows)
    for r in open_rows:
        r["expected"] = r["weighted"] * base_rate

    assert abs(weighted - sum(r["expected"] for r in open_rows)) < 0.01
    assert weighted <= unweighted + 0.01, "weighted pipeline cannot exceed unweighted"
    assert len(open_rows) + len(decided) + len(expired) == len(quotes)

    avg_decide = (sum(d["days_to_decide"] for d in tracked) / n_tracked) if n_tracked else None
    avg_win_decide = (sum(d["days_to_decide"] for d in tracked_won) /
                      len(tracked_won)) if tracked_won else None

    losses = {}
    for d in lost:
        losses[d["loss_reason"]] = losses.get(d["loss_reason"], 0) + 1

    action = [r for r in open_rows if r["flags"]]

    return {
        "open": sorted(open_rows, key=lambda r: -r["value"]),
        "decided": decided, "won": won, "lost": lost, "expired": expired,
        "n_quotes": len(quotes), "n_decided": n_decided,
        "n_tracked": n_tracked, "n_reconstructed": len(reconstructed),
        "win_rate": win_rate, "value_win_rate": value_rate, "rate_known": rate_known,
        "base_rate": base_rate, "base_rate_assumed": not rate_known,
        "tiers": tiers, "unweighted": unweighted, "weighted": weighted,
        "avg_decide": avg_decide, "avg_win_decide": avg_win_decide,
        "loss_reasons": losses, "action": action,
    }


def concentration_if_won(awards, open_rows):
    """G4 check: does this opportunity move concentration down, or up?

    Reads the awards file rather than carrying its own copy of the book —
    DECISIONS.md D-001, one source of truth.
    """
    book = {}
    for a in awards:
        book[a["client"]] = book.get(a["client"], 0.0) + float(a["contract"])
    total = sum(book.values())

    def top2(b):
        ranked = sorted(b.values(), reverse=True)
        t = sum(ranked[:2])
        s = sum(b.values())
        return (t / s * 100) if s else 0.0

    current = top2(book)
    rows = []
    for r in open_rows:
        hypothetical = dict(book)
        hypothetical[r["client"]] = hypothetical.get(r["client"], 0.0) + r["value"]
        after = top2(hypothetical)
        rows.append({"ref": r["ref"], "client": r["client"], "value": r["value"],
                     "after": after, "delta": after - current})
    return {"current": current, "book_total": total,
            "rows": sorted(rows, key=lambda x: x["delta"])}


def money(x):
    return f"{x:>12,.2f}"


def report(data, a, as_of, conc=None):
    out = []
    A = out.append
    A("=" * 78)
    A(f"  PIPELINE & CONVERSION — as of {as_of.strftime('%d %B %Y')}")
    A(f"  {a['n_quotes']} quotations tracked   ·   {len(a['open'])} open   ·   "
      f"{a['n_decided']} decided   ·   {len(a['expired'])} closed with no decision")
    A("=" * 78)

    if data.get("_note"):
        A("  SOURCE NOTE")
        for line in _wrap(data["_note"], 74):
            A(f"    {line}")
        A("-" * 78)

    # --- Open pipeline -----------------------------------------------------
    A("  OPEN QUOTATIONS")
    if not a["open"]:
        A("    none")
    for r in a["open"]:
        flag = ("  ← " + " · ".join(r["flags"])) if r["flags"] else ""
        A(f"  {r['ref']:<22}{r['client'][:22]:<24}{money(r['value'])}{flag}")
        A(f"      {r['days_open']:>3}d open · {r['days_quiet']:>3}d since contact · "
          f"age weight {r['weight']:.2f} · expected {r['expected']:,.2f}")
        if r["next_action"]:
            A(f"      next: {r['next_action']}"
              + (f"  ({r['next_action_date']})" if r["next_action_date"] else ""))
    A("-" * 78)
    A(f"  {'Unweighted open pipeline':<44}{money(a['unweighted'])}")
    A(f"  {'Expected value (age × conversion)':<44}{money(a['weighted'])}")

    if a["base_rate_assumed"]:
        A("")
        A(f"  *** CONVERSION RATE ASSUMED, NOT OBSERVED ***")
        A(f"  Only {a['n_tracked']} tracked quotation(s) on record — fewer than the "
          f"{MIN_DECIDED_FOR_RATE} needed")
        A(f"  for a rate. Expected value above uses an ASSUMED {ASSUMED_WIN_RATE:.0%} "
          f"conversion.")
        A("  Treat it as a placeholder. It is not a forecast and must not be planned against.")
    A("=" * 78)

    # --- Conversion --------------------------------------------------------
    A("  CONVERSION")
    A(f"  {'Quotations decided':<44}{a['n_decided']:>12}")
    A(f"  {'  of which tracked issue → decision':<44}{a['n_tracked']:>12}")
    A(f"  {'  of which reconstructed (wins-only record)':<44}{a['n_reconstructed']:>12}")
    A(f"  {'Won':<44}{len(a['won']):>12}")
    A(f"  {'Lost':<44}{len(a['lost']):>12}")
    if a["rate_known"]:
        A(f"  {'Win rate (by count, tracked only)':<44}{a['win_rate']*100:>11.1f}%")
        A(f"  {'Win rate (by value, tracked only)':<44}{a['value_win_rate']*100:>11.1f}%")
    else:
        A(f"  {'Win rate':<44}{'INSUFFICIENT DATA':>12}")
        A(f"      {a['n_tracked']} of {MIN_DECIDED_FOR_RATE} tracked quotes needed. "
          f"No percentage is printed from this;")
        A(f"      a rate from a handful of quotes reads identically to a real one.")
        if a["n_reconstructed"]:
            A(f"      The {a['n_reconstructed']} reconstructed row(s) are excluded: the "
              f"register recorded only wins,")
            A(f"      so including them would report a win rate close to 100%.")
    if a["avg_decide"] is not None:
        A(f"  {'Avg days to a decision':<44}{a['avg_decide']:>12.0f}")
    if a["avg_win_decide"] is not None:
        A(f"  {'Avg days to a WIN':<44}{a['avg_win_decide']:>12.0f}")
    A("=" * 78)

    # --- The G1 answer -----------------------------------------------------
    A("  WIN RATE BY MARGIN TIER   (does quoting low actually win the work?)")
    if not a["tiers"]:
        A("    no decided quotes carry a tier")
    for t in sorted(a["tiers"]):
        v = a["tiers"][t]
        if v.get("survivorship"):
            A(f"  {t:<14}n={v['n']:<4}  win rate: NOT COMPUTED — survivorship bias")
            A(f"      These are historic awards reconstructed from a register that only")
            A(f"      ever recorded wins. Their win rate is 100% by construction, not by")
            A(f"      performance. They contribute nothing to the question above.")
        elif v["rate"] is None:
            A(f"  {t:<14}n={v['n']:<4}  win rate: insufficient data "
              f"(need {MIN_DECIDED_PER_TIER})")
        else:
            A(f"  {t:<14}n={v['n']:<4}  win rate {v['rate']*100:>5.1f}%   "
              f"value quoted {v['value']:>12,.2f}   won {v['won_value']:>12,.2f}")
    A("")
    A("  This table is the point of the register. Until the low tiers show a materially")
    A("  higher win rate than the high tiers, there is no evidence that discounting buys")
    A("  work — and GOALS.md G1's floor costs nothing to hold.")
    A("=" * 78)

    # --- Losses ------------------------------------------------------------
    if a["loss_reasons"]:
        A("  LOSS REASONS")
        for reason, n in sorted(a["loss_reasons"].items(), key=lambda x: -x[1]):
            A(f"  {reason:<58}{n:>4}")
        A("=" * 78)

    # --- Concentration -----------------------------------------------------
    if conc:
        A("  CONCENTRATION IF WON   (GOALS.md G4 — direction must be down)")
        A(f"  {'Current top-2 concentration':<44}{conc['current']:>11.1f}%")
        for r in conc["rows"]:
            arrow = "↓" if r["delta"] < 0 else "↑"
            A(f"  {r['ref']:<22}{r['client'][:22]:<24}{conc['current']:>6.1f}% → "
              f"{r['after']:>5.1f}%  {arrow}{abs(r['delta']):.1f}")
        A("=" * 78)

    # --- Action ------------------------------------------------------------
    A("  ACTION REQUIRED")
    if not a["action"]:
        A("    none — every open quotation is inside validity and has recent contact")
    for r in a["action"]:
        A(f"  {r['ref']:<22}{r['client'][:22]:<24}{money(r['value'])}"
          f"   {' · '.join(r['flags'])}")
        A(f"      {r['days_open']}d open, {r['days_quiet']}d since contact "
          f"→ draft a follow-up for Farhan to send")
    A("=" * 78)
    A("  Drafted follow-ups are text for Farhan to send. This system sends nothing.")
    return "\n".join(out)


def _wrap(text, width):
    words, line, lines = text.split(), "", []
    for w in words:
        if len(line) + len(w) + 1 > width:
            lines.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    if line:
        lines.append(line)
    return lines


def main():
    ap = argparse.ArgumentParser(description="TNDK pipeline and conversion analysis")
    ap.add_argument("--data", required=True, help="pipeline JSON")
    ap.add_argument("--awards", default=None,
                    help="awards JSON, for the concentration-if-won check")
    ap.add_argument("--as-of", default=None, help="YYYY-MM-DD, defaults to today")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    with open(args.data) as f:
        data = json.load(f)

    as_of = parse_date(args.as_of) if args.as_of else (
        parse_date(data["as_of"]) if data.get("as_of") else date.today())

    a = analyse(data, as_of)

    conc = None
    if args.awards:
        with open(args.awards) as f:
            conc = concentration_if_won(json.load(f)["awards"], a["open"])

    if args.json:
        payload = {
            "as_of": as_of.isoformat(),
            "n_quotes": a["n_quotes"], "n_open": len(a["open"]),
            "n_decided": a["n_decided"], "n_tracked": a["n_tracked"],
            "n_reconstructed": a["n_reconstructed"],
            "n_won": len(a["won"]), "n_lost": len(a["lost"]),
            "unweighted_pipeline": round(a["unweighted"], 2),
            "expected_pipeline": round(a["weighted"], 2),
            "win_rate": round(a["win_rate"], 4) if a["rate_known"] else None,
            "value_win_rate": round(a["value_win_rate"], 4) if a["rate_known"] else None,
            "win_rate_status": "OBSERVED" if a["rate_known"] else "INSUFFICIENT_DATA",
            "base_rate_used": a["base_rate"],
            "base_rate_assumed": a["base_rate_assumed"],
            "avg_days_to_decision": round(a["avg_decide"], 1) if a["avg_decide"] else None,
            "tiers": {t: {"n": v["n"], "won": v["won"],
                          "rate": round(v["rate"], 4) if v["rate"] is not None else None,
                          "suppressed": "survivorship" if v.get("survivorship")
                          else ("insufficient_data" if v["rate"] is None else None)}
                      for t, v in a["tiers"].items()},
            "loss_reasons": a["loss_reasons"],
            "action_required": [{"ref": r["ref"], "client": r["client"],
                                 "value": r["value"], "flags": r["flags"]}
                                for r in a["action"]],
            "concentration": ({"current_top2_pct": round(conc["current"], 2),
                               "if_won": [{"ref": r["ref"], "after_pct": round(r["after"], 2),
                                           "delta_pct": round(r["delta"], 2)}
                                          for r in conc["rows"]]} if conc else None),
            "human_review_required": True,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(report(data, a, as_of, conc))

    if a["action"]:
        sys.exit(2)   # non-zero so a wrapper can gate on it
    return 0


if __name__ == "__main__":
    main()
