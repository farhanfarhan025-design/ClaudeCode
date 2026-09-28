#!/usr/bin/env python3
"""
Download NSE's official end-of-day closes and write them as the scorecard's price file.

    python3 fetch_prices.py                  # today (IST)
    python3 fetch_prices.py 2026-09-25       # a given trading day
    python3 fetch_prices.py --backfill 30    # the last 30 calendar days, skipping ones already fetched

Sources (NSE archives, free, no key):
  equities  nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_YYYYMMDD_F_0000.csv.zip
  indices   nsearchives.nseindia.com/content/indices/ind_close_all_DDMMYYYY.csv  (NIFTY 50 -> NIFTY)

Writes prices/YYYY-MM-DD.csv with columns date,ticker,close (EQ and BE series only).
Exit codes: 0 written · 1 no file for that day (holiday, or not published yet) · 2 network blocked.
Standard library only.
"""

import argparse
import csv
import io
import sys
import urllib.error
import urllib.request
import zipfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

IST = timezone(timedelta(hours=5, minutes=30))
HERE = Path(__file__).resolve().parent
OUT = HERE / "prices"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept": "*/*", "Referer": "https://www.nseindia.com/"}

EQ_URL = "https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{ymd}_F_0000.csv.zip"
IDX_URL = "https://nsearchives.nseindia.com/content/indices/ind_close_all_{dmy}.csv"
INDICES = {"nifty 50": "NIFTY", "nifty bank": "BANKNIFTY", "nifty 500": "NIFTY500"}


class Blocked(Exception):
    pass


def get(url):
    """Bytes, or None when NSE has no file for that day."""
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        if e.code in (401, 403, 407):
            raise Blocked(f"{url}: HTTP {e.code}")
        raise
    except (urllib.error.URLError, OSError) as e:
        raise Blocked(f"{url}: {e}")


def parse_equities(raw_zip):
    rows = []
    with zipfile.ZipFile(io.BytesIO(raw_zip)) as z:
        name = next(n for n in z.namelist() if n.lower().endswith(".csv"))
        text = z.read(name).decode("utf-8-sig")
    for r in csv.DictReader(io.StringIO(text)):
        r = {k.strip(): (v or "").strip() for k, v in r.items() if k}
        if r.get("SctySrs") not in ("EQ", "BE"):
            continue
        try:
            rows.append((r["TradDt"], r["TckrSymb"], float(r["ClsPric"])))
        except (KeyError, ValueError):
            continue
    return rows


def parse_indices(raw_csv, day):
    rows = []
    for r in csv.DictReader(io.StringIO(raw_csv.decode("utf-8-sig"))):
        r = {k.strip(): (v or "").strip() for k, v in r.items() if k}
        ticker = INDICES.get(r.get("Index Name", "").lower())
        if not ticker:
            continue
        try:
            rows.append((day.isoformat(), ticker, float(r["Closing Index Value"])))
        except (KeyError, ValueError):
            continue
    return rows


def fetch(day):
    """Write prices/<day>.csv. Returns number of rows, or 0 if NSE has no file for the day."""
    raw = get(EQ_URL.format(ymd=day.strftime("%Y%m%d")))
    if raw is None:
        return 0
    rows = parse_equities(raw)
    idx = get(IDX_URL.format(dmy=day.strftime("%d%m%Y")))
    if idx is not None:
        rows += parse_indices(idx, day)
    OUT.mkdir(exist_ok=True)
    with open(OUT / f"{day.isoformat()}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "ticker", "close"])
        w.writerows(rows)
    return len(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("day", nargs="?", help="YYYY-MM-DD (default: today IST)")
    ap.add_argument("--backfill", type=int, metavar="DAYS")
    a = ap.parse_args(argv)

    today = datetime.now(IST).date()
    if a.backfill:
        days = [today - timedelta(days=i) for i in range(a.backfill, -1, -1)]
        days = [d for d in days if d.weekday() < 5 and not (OUT / f"{d}.csv").exists()]
    else:
        days = [date.fromisoformat(a.day) if a.day else today]

    got = 0
    for d in days:
        try:
            n = fetch(d)
        except Blocked as e:
            print(f"BLOCKED — cannot reach NSE archives ({e}). Allow nsearchives.nseindia.com in the environment's network settings.")
            return 2
        print(f"{d}: {n} closes" if n else f"{d}: no NSE file (holiday or not yet published)")
        got += bool(n)
    return 0 if got else 1


if __name__ == "__main__":
    sys.exit(main())
