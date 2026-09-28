#!/usr/bin/env python3
"""
Market Intelligence scorecard — grade every agent's call against what the market did.

Twenty-three agents produce a lot of confident text. This answers the only question
that matters about each of them: when it said UP, DOWN or FLAT, was it right more often
than chance, after removing what the whole market did that day?

Four subcommands:

    ingest   pull CALL lines out of an agent pack and append them to the ledger
    log      append one call by hand
    verify   check the ledger's hash chain (detects edited or deleted calls)
    score    grade every call at 1, 5 and 20 trading days; write a report

The ledger is append-only JSONL with a hash chain. A call cannot be quietly
improved after the fact: any edit breaks the chain and `verify` says where.

A call logged after the market opens on the session following its entry close is
BACKFILLED and excluded by default: an agent that "calls" a move after seeing it
has no signal.

Standard library only. Prices come from CSV (see README) because the price source
is whatever your Market Volume agent already pulls.
"""

import argparse
import csv
import glob
import hashlib
import json
import math
import re
import sys
from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from statistics import NormalDist

IST = timezone(timedelta(hours=5, minutes=30))
MARKET_OPEN = time(9, 15)  # NSE
HORIZONS = (1, 5, 20)
DIRECTIONS = ("UP", "DOWN", "NEUTRAL")
GENESIS = "0" * 64

# A NEUTRAL call is right when the stock's excess move stays inside this band.
# Scaled by sqrt(horizon): 1.0% at 1 day, 2.2% at 5, 4.5% at 20.
NEUTRAL_BAND_1D = 0.01

# Fewer resolved calls than this and the verdict is INSUFFICIENT, whatever the hit rate.
MIN_CALLS = 20

HERE = Path(__file__).resolve().parent


# --- Ledger ----------------------------------------------------------------

def _record_hash(record):
    body = {k: v for k, v in record.items() if k != "hash"}
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


def read_ledger(path):
    path = Path(path)
    if not path.exists():
        return []
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def verify_ledger(records):
    """Return a list of problems; empty means the chain is intact."""
    problems = []
    prev = GENESIS
    for i, r in enumerate(records, 1):
        if r.get("prev") != prev:
            problems.append(f"line {i} ({r.get('id', '?')}): chain broken — a record before it was edited, removed or reordered")
        if _record_hash(r) != r.get("hash"):
            problems.append(f"line {i} ({r.get('id', '?')}): contents edited after logging")
        prev = r.get("hash")
    return problems


def parse_ts(value):
    """ISO timestamp -> aware datetime. No offset means IST."""
    dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    return dt if dt.tzinfo else dt.replace(tzinfo=IST)


def load_roster(path):
    """agent name (lowercased) -> (canonical name, lead)."""
    with open(path) as f:
        roster = json.load(f)
    out = {}
    for lead, members in roster["leads"].items():
        out[lead.lower()] = (lead, lead)
        for m in members:
            out[m.lower()] = (m, lead)
    chief = roster["chief"]
    out[chief.lower()] = (chief, chief)
    for alias, target in roster.get("aliases", {}).items():
        out[alias.lower()] = out[target.lower()]
    return out


def make_call(fields, roster, logged_at=None):
    """Validate one call's fields and return a normalised dict (without chain fields)."""
    missing = [k for k in ("agent", "ticker", "dir", "as_of") if not fields.get(k)]
    if missing:
        raise ValueError(f"missing {', '.join(missing)}")

    direction = fields["dir"].strip().upper()
    direction = {"FLAT": "NEUTRAL", "BULLISH": "UP", "BEARISH": "DOWN"}.get(direction, direction)
    if direction not in DIRECTIONS:
        raise ValueError(f"dir must be UP, DOWN or NEUTRAL, got {fields['dir']!r}")

    conf = float(fields.get("conf", 0.5))
    if not 0.5 <= conf <= 1.0:
        # Below 0.5 is a call in the other direction; make the agent say so.
        raise ValueError(f"conf must be between 0.5 and 1.0, got {conf}")

    as_of = parse_ts(fields["as_of"])
    agent_raw = fields["agent"].strip()
    agent, lead = roster.get(agent_raw.lower(), (agent_raw, "UNMAPPED"))

    return {
        "agent": agent,
        "lead": lead,
        "ticker": fields["ticker"].strip().upper(),
        "dir": direction,
        "conf": round(conf, 3),
        "as_of": as_of.isoformat(),
        "logged_at": (logged_at or datetime.now(IST)).isoformat(timespec="seconds"),
        "pack": fields.get("pack", "").strip(),
        "thesis": fields.get("thesis", "").strip(),
    }


def append_calls(path, calls):
    path = Path(path)
    records = read_ledger(path)
    problems = verify_ledger(records)
    if problems:
        raise SystemExit("ledger failed verification, refusing to append:\n  " + "\n  ".join(problems))
    prev = records[-1]["hash"] if records else GENESIS
    seen = {(r["agent"], r["ticker"], r["dir"], r["as_of"]) for r in records}
    written, skipped = [], 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        for c in calls:
            key = (c["agent"], c["ticker"], c["dir"], c["as_of"])
            if key in seen:
                skipped += 1
                continue
            seen.add(key)
            rec = {"id": f"C{len(records) + len(written) + 1:05d}", **c, "prev": prev}
            rec["hash"] = _record_hash(rec)
            prev = rec["hash"]
            f.write(json.dumps(rec, sort_keys=True) + "\n")
            written.append(rec)
    return written, skipped


CALL_LINE = re.compile(r"^\s*[-*•]?\s*CALL\s*\|(.*)$", re.IGNORECASE)


def parse_call_lines(text):
    """Yield (line_number, fields) for each `CALL | k=v | k=v` line in an agent pack."""
    for n, line in enumerate(text.splitlines(), 1):
        m = CALL_LINE.match(line)
        if not m:
            continue
        fields = {}
        for part in m.group(1).split("|"):
            if "=" in part:
                k, v = part.split("=", 1)
                fields[k.strip().lower()] = v.strip()
        yield n, fields


# --- Prices ----------------------------------------------------------------

# Accepts a plain date,ticker,close CSV or an NSE bhavcopy (sec_bhavdata_full).
DATE_COLS = ("date", "date1", "timestamp", "trade_date")
TICKER_COLS = ("ticker", "symbol")
CLOSE_COLS = ("close", "close_price", "adj_close", "adj close")
DATE_FORMATS = ("%Y-%m-%d", "%d-%b-%Y", "%d-%m-%Y", "%d/%m/%Y", "%d-%B-%Y")


def _parse_date(s):
    s = s.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"unrecognised date {s!r}")


def _pick(header, options, what, path):
    for o in options:
        if o in header:
            return header[o]
    raise SystemExit(f"{path}: no {what} column (looked for {', '.join(options)})")


def load_prices(patterns):
    """ticker -> sorted list of (date, close)."""
    series = defaultdict(dict)
    files = [p for pat in patterns for p in sorted(glob.glob(pat))]
    if not files:
        raise SystemExit(f"no price files matched {patterns}")
    for path in files:
        with open(path, newline="") as f:
            reader = csv.reader(f)
            raw = next(reader)
            header = {h.strip().lower(): i for i, h in enumerate(raw)}
            di = _pick(header, DATE_COLS, "date", path)
            ti = _pick(header, TICKER_COLS, "ticker", path)
            ci = _pick(header, CLOSE_COLS, "close", path)
            si = header.get("series")
            for row in reader:
                if not row or len(row) <= max(di, ti, ci):
                    continue
                if si is not None and row[si].strip() not in ("EQ", "BE", ""):
                    continue
                try:
                    close = float(row[ci].strip().replace(",", ""))
                    d = _parse_date(row[di])
                except ValueError:
                    continue
                series[row[ti].strip().upper()][d] = close
    return {t: sorted(v.items()) for t, v in series.items()}


# --- Scoring ---------------------------------------------------------------

def entry_index(series, as_of):
    """
    Index of the entry close. Entry is the close ON the as-of date (IST) if it traded,
    otherwise the next close. Deliberately conservative: a call made at 11:00 does not
    get credit for the move between the previous close and 11:00.
    """
    day = as_of.astimezone(IST).date()
    for i, (d, _) in enumerate(series):
        if d >= day:
            return i
    return None


def close_on(series, day):
    for d, c in series:
        if d == day:
            return c
    return None


def grade(call, prices, benchmark, horizon):
    """Return a result dict, or a string saying why the call can't be graded."""
    s = prices.get(call["ticker"])
    if not s:
        return "no prices for ticker"
    i = entry_index(s, parse_ts(call["as_of"]))
    if i is None:
        return "pending"
    j = i + horizon
    if j >= len(s):
        return "pending"
    (d0, p0), (d1, p1) = s[i], s[j]
    ret = p1 / p0 - 1

    excess, bench_ret = ret, None
    b = prices.get(benchmark) if benchmark else None
    if b:
        b0, b1 = close_on(b, d0), close_on(b, d1)
        if b0 and b1:
            bench_ret = b1 / b0 - 1
            excess = ret - bench_ret

    if call["dir"] == "UP":
        signed, hit = excess, excess > 0
    elif call["dir"] == "DOWN":
        signed, hit = -excess, excess < 0
    else:
        band = NEUTRAL_BAND_1D * math.sqrt(horizon)
        signed, hit = None, abs(excess) <= band

    return {
        "entry": d0.isoformat(), "exit": d1.isoformat(),
        "ret": ret, "bench": bench_ret, "excess": excess,
        "signed": signed, "hit": hit,
        "brier": (call["conf"] - (1.0 if hit else 0.0)) ** 2,
    }


def wilson(hits, n, z=1.96):
    if n == 0:
        return 0.0, 1.0
    p = hits / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return centre - half, centre + half


def z_for(comparisons, alpha=0.05):
    """
    Two-sided critical value, Bonferroni-corrected for how many agents are compared at once.
    Grade 17 agents at plain 95% and about one looks skilled by luck alone; this stops that.
    """
    return NormalDist().inv_cdf(1 - alpha / (2 * max(1, comparisons)))


def verdict(hits, n, z=1.96):
    if n < MIN_CALLS:
        return "INSUFFICIENT"
    lo, hi = wilson(hits, n, z)
    if lo > 0.5:
        return "SIGNAL"
    if hi < 0.5:
        return "WRONG-WAY"
    return "NO EDGE YET"


def summarise(results, z=1.96):
    n = len(results)
    hits = sum(r["hit"] for r in results)
    directional = [r["signed"] for r in results if r["signed"] is not None]
    lo, hi = wilson(hits, n, z)
    return {
        "n": n,
        "hits": hits,
        "hit_rate": hits / n if n else None,
        "ci": (lo, hi),
        "avg_signed": sum(directional) / len(directional) if directional else None,
        "brier": sum(r["brier"] for r in results) / n if n else None,
        "verdict": verdict(hits, n, z),
    }


def logging_deadline(call, prices):
    """
    A call must be on record before the market opens on the first session after its entry
    close. Until then no part of the outcome it is graded on exists; after it, some does.
    """
    as_of = parse_ts(call["as_of"])
    s = prices.get(call["ticker"], [])
    i = entry_index(s, as_of)
    if i is not None and i + 1 < len(s):
        next_day = s[i + 1][0]
    else:
        # Series doesn't reach far enough yet: assume the next weekday after the entry day.
        d = s[i][0] if i is not None else as_of.astimezone(IST).date()
        while d.weekday() >= 5:
            d += timedelta(days=1)
        next_day = d + timedelta(days=1)
        while next_day.weekday() >= 5:
            next_day += timedelta(days=1)
    return datetime.combine(next_day, MARKET_OPEN, tzinfo=IST)


def score(calls, prices, benchmark, include_backfilled=False):
    graded = {h: [] for h in HORIZONS}
    status = defaultdict(int)
    excluded = []
    for c in calls:
        deadline = logging_deadline(c, prices)
        if parse_ts(c["logged_at"]) > deadline and not include_backfilled:
            status["backfilled (excluded)"] += 1
            excluded.append((c, f"logged {c['logged_at'][:16]}, after the {deadline:%d %b %H:%M} open it is graded from"))
            continue
        for h in HORIZONS:
            g = grade(c, prices, benchmark, h)
            if isinstance(g, str):
                if h == HORIZONS[0]:
                    status[g] += 1
                    if g != "pending":
                        excluded.append((c, g))
                continue
            graded[h].append({**c, **g})
            if h == HORIZONS[0]:
                status["graded"] += 1
    return graded, status, excluded


# --- Report ----------------------------------------------------------------

def pct(x, signed=False):
    if x is None:
        return "—"
    return f"{x * 100:+.2f}%" if signed else f"{x * 100:.1f}%"


def table(groups, order):
    # Each row is one of several simultaneous comparisons; the ALL row is a single test.
    z = z_for(sum(1 for g in order if g != "ALL AGENTS"))
    lines = [
        f"| | Calls | Hit rate | Range (z={z:.2f}) | Avg edge | Brier | Verdict |",
        "|---|---:|---:|---|---:|---:|---|",
    ]
    for name in order:
        s = summarise(groups[name], 1.96 if name == "ALL AGENTS" else z)
        lo, hi = s["ci"]
        lines.append(
            f"| {name} | {s['n']} | {pct(s['hit_rate'])} | {pct(lo)}–{pct(hi)} "
            f"| {pct(s['avg_signed'], True)} | {s['brier']:.3f} | **{s['verdict']}** |"
        )
    return "\n".join(lines)


def calibration(results):
    buckets = [(0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.01)]
    lines = ["| Stated confidence | Calls | Actually right |", "|---|---:|---:|"]
    for lo, hi in buckets:
        b = [r for r in results if lo <= r["conf"] < hi]
        if b:
            lines.append(f"| {lo:.1f}–{min(hi, 1.0):.1f} | {len(b)} | {pct(sum(r['hit'] for r in b) / len(b))} |")
    return "\n".join(lines)


def render(graded, status, excluded, benchmark, roster_order, as_of):
    out = [f"# Agent scorecard — {as_of}", ""]
    out.append("Every call graded against the market. **Hit rate** is how often the call was right "
               f"after removing {'the ' + benchmark + ' move' if benchmark else 'nothing (no benchmark given)'}. "
               "**Avg edge** is the average excess return in the direction called (UP/DOWN only). "
               "**Brier** scores confidence: 0 is perfect, 0.25 is a coin flip at 50%, lower is better.")
    out.append("")
    out.append(f"Verdicts need {MIN_CALLS}+ resolved calls. **SIGNAL** means the whole range sits above 50%; "
               "**WRONG-WAY** means it sits below (fade it, or fix it); **NO EDGE YET** means it can't be told apart from chance. "
               "Ranges are widened for the number of agents compared in each table (Bonferroni), because among 17 "
               "coin-flipping agents about one will look skilled at plain 95% by luck alone.")
    out.append("")
    out.append("**Ledger status (1-day horizon):** " + ", ".join(f"{k}: {v}" for k, v in sorted(status.items())))
    out.append("")

    for h in HORIZONS:
        rs = graded[h]
        out.append(f"## {h}-day horizon")
        out.append("")
        if not rs:
            out.append("No resolved calls yet.")
            out.append("")
            continue
        by_lead, by_agent = defaultdict(list), defaultdict(list)
        for r in rs:
            by_lead[r["lead"]].append(r)
            by_agent[r["agent"]].append(r)
        by_lead["ALL AGENTS"] = rs

        out.append("### By lead")
        out.append("")
        leads = [l for l in roster_order["leads"] if l in by_lead] + \
                sorted(l for l in by_lead if l not in roster_order["leads"] and l != "ALL AGENTS") + ["ALL AGENTS"]
        out.append(table(by_lead, leads))
        out.append("")
        out.append("### By agent")
        out.append("")
        agents = sorted(by_agent, key=lambda a: (-(summarise(by_agent[a])["hit_rate"] or 0), a))
        out.append(table(by_agent, agents))
        out.append("")
        out.append("### Calibration — does 80% confident mean right 80% of the time?")
        out.append("")
        out.append(calibration(rs))
        out.append("")

    rs = graded[HORIZONS[1]]
    if rs:
        out.append(f"## Best and worst {HORIZONS[1]}-day calls")
        out.append("")
        dirn = sorted((r for r in rs if r["signed"] is not None), key=lambda r: r["signed"])
        out.append("| Agent | Ticker | Call | Conf | As of | Excess move | Pack |")
        out.append("|---|---|---|---:|---|---:|---|")
        for r in dirn[-5:][::-1] + dirn[:5]:
            out.append(f"| {r['agent']} | {r['ticker']} | {r['dir']} | {r['conf']:.2f} | {r['as_of'][:16]} "
                       f"| {pct(r['excess'], True)} | {r['pack'] or '—'} |")
        out.append("")

    if excluded:
        out.append("## Not scored")
        out.append("")
        out.append("| ID | Agent | Ticker | Reason |")
        out.append("|---|---|---|---|")
        for c, why in excluded:
            out.append(f"| {c.get('id', '—')} | {c['agent']} | {c['ticker']} | {why} |")
        out.append("")

    return "\n".join(out)


# --- CLI -------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledger", default=str(HERE / "ledger" / "calls.jsonl"))
    ap.add_argument("--roster", default=str(HERE / "roster.json"))
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("ingest", help="append CALL lines from agent pack text files (or - for stdin)")
    p.add_argument("files", nargs="+")
    p.add_argument("--agent", help="default agent when a CALL line has no agent=")
    p.add_argument("--pack", help="default pack ID when a CALL line has no pack=")

    p = sub.add_parser("log", help="append one call")
    for k in ("agent", "ticker", "dir", "as_of"):
        p.add_argument(f"--{k.replace('_', '-')}", dest=k, required=True)
    p.add_argument("--conf", default="0.5")
    p.add_argument("--pack", default="")
    p.add_argument("--thesis", default="")

    sub.add_parser("verify", help="check the ledger hash chain")

    p = sub.add_parser("score", help="grade calls and write a report")
    p.add_argument("--prices", nargs="+", required=True, help="CSV files or globs (date,ticker,close or NSE bhavcopy)")
    p.add_argument("--benchmark", default="NIFTY", help="ticker in the price files to measure excess return against; '' for none")
    p.add_argument("--include-backfilled", action="store_true",
                   help="also score calls logged after the next open (never trust these results)")
    p.add_argument("--out", help="write the markdown report here (default: stdout)")
    p.add_argument("--json", help="also write per-call results as JSON here")

    a = ap.parse_args(argv)
    roster = load_roster(a.roster)

    if a.cmd == "verify":
        records = read_ledger(a.ledger)
        problems = verify_ledger(records)
        if problems:
            print("LEDGER TAMPERED\n  " + "\n  ".join(problems))
            return 1
        print(f"OK — {len(records)} calls, chain intact")
        return 0

    if a.cmd == "log":
        call = make_call(vars(a), roster)
        written, skipped = append_calls(a.ledger, [call])
        print(f"logged {written[0]['id']}" if written else "duplicate — already in ledger")
        return 0

    if a.cmd == "ingest":
        calls, errors = [], []
        for path in a.files:
            text = sys.stdin.read() if path == "-" else Path(path).read_text()
            for n, fields in parse_call_lines(text):
                fields.setdefault("agent", a.agent or "")
                fields.setdefault("pack", a.pack or "")
                try:
                    calls.append(make_call(fields, roster))
                except ValueError as e:
                    errors.append(f"{path}:{n}: {e}")
        written, skipped = append_calls(a.ledger, calls)
        unmapped = sorted({c["agent"] for c in written if c["lead"] == "UNMAPPED"})
        print(f"ingested {len(written)} calls, {skipped} duplicates skipped, {len(errors)} rejected")
        for e in errors:
            print("  REJECTED " + e)
        if unmapped:
            print("  not in roster (scored under UNMAPPED): " + ", ".join(unmapped))
        return 1 if errors else 0

    if a.cmd == "score":
        records = read_ledger(a.ledger)
        problems = verify_ledger(records)
        if problems:
            print("WARNING: ledger failed verification — results may include edited calls:\n  "
                  + "\n  ".join(problems), file=sys.stderr)
        prices = load_prices(a.prices)
        bench = a.benchmark.upper() or None
        if bench and bench not in prices:
            print(f"WARNING: benchmark {bench} not in price files — scoring raw returns", file=sys.stderr)
            bench = None
        graded, status, excluded = score(records, prices, bench, a.include_backfilled)
        with open(a.roster) as f:
            order = json.load(f)
        report = render(graded, status, excluded, bench, order, datetime.now(IST).strftime("%Y-%m-%d %H:%M IST"))
        if a.out:
            Path(a.out).parent.mkdir(parents=True, exist_ok=True)
            Path(a.out).write_text(report + "\n")
            print(f"report written to {a.out}")
        else:
            print(report)
        if a.json:
            Path(a.json).write_text(json.dumps({str(h): graded[h] for h in HORIZONS}, indent=2, default=str))
        return 0


if __name__ == "__main__":
    sys.exit(main())
