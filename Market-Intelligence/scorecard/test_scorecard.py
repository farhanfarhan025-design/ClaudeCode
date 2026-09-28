#!/usr/bin/env python3
"""Tests for scorecard.py. Run: python3 test_scorecard.py"""

import json
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

import scorecard as sc

ROSTER = sc.load_roster(Path(__file__).parent / "roster.json")
LOGGED = datetime(2026, 9, 18, 19, 45, tzinfo=sc.IST)


def call(**kw):
    fields = {"agent": "Insider Activity Analyst", "ticker": "BEML", "dir": "UP",
              "conf": "0.7", "as_of": "2026-09-18T19:44:22+05:30", **kw}
    return sc.make_call(fields, ROSTER, logged_at=kw.pop("logged_at", LOGGED))


def series(start_price, moves, start=date(2026, 9, 18)):
    """Trading days only (skips weekends)."""
    out, d, p = [], start, start_price
    for m in [0.0] + moves:
        while d.weekday() >= 5:
            d = d.fromordinal(d.toordinal() + 1)
        p *= 1 + m
        out.append((d, p))
        d = d.fromordinal(d.toordinal() + 1)
    return out


class Ledger(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "calls.jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def test_chain_intact_after_appends(self):
        sc.append_calls(self.path, [call()])
        sc.append_calls(self.path, [call(ticker="BEL")])
        recs = sc.read_ledger(self.path)
        self.assertEqual([r["id"] for r in recs], ["C00001", "C00002"])
        self.assertEqual(sc.verify_ledger(recs), [])

    def test_edited_call_is_detected(self):
        sc.append_calls(self.path, [call(), call(ticker="BEL")])
        lines = self.path.read_text().splitlines()
        rec = json.loads(lines[0])
        rec["dir"] = "DOWN"  # quietly "fix" a wrong call
        lines[0] = json.dumps(rec, sort_keys=True)
        self.path.write_text("\n".join(lines) + "\n")
        problems = sc.verify_ledger(sc.read_ledger(self.path))
        self.assertTrue(any("edited" in p for p in problems))

    def test_deleted_call_is_detected(self):
        sc.append_calls(self.path, [call(), call(ticker="BEL"), call(ticker="GRSE")])
        lines = self.path.read_text().splitlines()
        self.path.write_text(lines[0] + "\n" + lines[2] + "\n")
        self.assertTrue(sc.verify_ledger(sc.read_ledger(self.path)))

    def test_refuses_to_append_to_tampered_ledger(self):
        sc.append_calls(self.path, [call()])
        rec = json.loads(self.path.read_text())
        rec["conf"] = 0.99
        self.path.write_text(json.dumps(rec) + "\n")
        with self.assertRaises(SystemExit):
            sc.append_calls(self.path, [call(ticker="BEL")])

    def test_duplicates_skipped(self):
        sc.append_calls(self.path, [call()])
        written, skipped = sc.append_calls(self.path, [call()])
        self.assertEqual((len(written), skipped), (0, 1))


class Parsing(unittest.TestCase):
    def test_call_lines_from_pack(self):
        pack = """News Lead EOD pack MNRL-EOD-20260918
        CMIO-eligible: BEML HIGH
        - CALL | agent=CMIO | ticker=BEML | dir=up | conf=0.65 | as_of=2026-09-18T19:44:22+05:30 | thesis=NHSRCL order
        Not a call line | ticker=X
        CALL | agent=Bear Case Analyst | ticker=COCHINSHIP | dir=flat | as_of=2026-09-18T19:44"""
        got = [f for _, f in sc.parse_call_lines(pack)]
        self.assertEqual(len(got), 2)
        c = sc.make_call(got[0], ROSTER, LOGGED)
        self.assertEqual((c["agent"], c["lead"], c["dir"]), ("Chief Market Intelligence Officer",
                                                               "Chief Market Intelligence Officer", "UP"))
        c = sc.make_call(got[1], ROSTER, LOGGED)
        self.assertEqual((c["lead"], c["dir"], c["conf"]), ("Independent Research Review Lead", "NEUTRAL", 0.5))

    def test_rejects_bad_calls(self):
        with self.assertRaises(ValueError):
            call(dir="MAYBE")
        with self.assertRaises(ValueError):
            call(conf="0.3")  # a 30% UP is a 70% DOWN; make the agent say that
        with self.assertRaises(ValueError):
            sc.make_call({"agent": "x", "dir": "UP", "as_of": "2026-09-18"}, ROSTER)

    def test_unknown_agent_is_unmapped(self):
        self.assertEqual(call(agent="Crystal Ball Analyst")["lead"], "UNMAPPED")

    def test_nse_bhavcopy(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "sec_bhavdata_full_18092026.csv"
            p.write_text(
                "SYMBOL, SERIES, DATE1, PREV_CLOSE, OPEN_PRICE, CLOSE_PRICE\n"
                "BEML, EQ, 18-Sep-2026, 4000.00, 4010.00, 4241.60\n"
                "BEML, N1, 18-Sep-2026, 100.00, 100.00, 101.00\n"
                "COCHINSHIP, EQ, 18-Sep-2026, 1800.00, 1805.00, 1885.86\n")
            prices = sc.load_prices([str(p)])
        self.assertEqual(prices["BEML"], [(date(2026, 9, 18), 4241.60)])
        self.assertIn("COCHINSHIP", prices)


class Grading(unittest.TestCase):
    def test_entry_is_close_on_call_day_not_before(self):
        s = series(100, [0.05, 0.01])
        # Called at 11:00 on the 18th: entry is the 18th's close, not the 17th's.
        i = sc.entry_index(s, sc.parse_ts("2026-09-18T11:00:00+05:30"))
        self.assertEqual(s[i][0], date(2026, 9, 18))
        # Called on Saturday: entry is Monday's close.
        i = sc.entry_index(s, sc.parse_ts("2026-09-19T10:00:00+05:30"))
        self.assertEqual(s[i][0], date(2026, 9, 21))

    def test_utc_timestamp_uses_ist_date(self):
        s = series(100, [0.01])
        # 19:00 UTC on the 18th is 00:30 IST on the 19th (a Saturday) -> Monday.
        i = sc.entry_index(s, sc.parse_ts("2026-09-18T19:00:00Z"))
        self.assertEqual(s[i][0], date(2026, 9, 21))

    def test_excess_return_removes_market_move(self):
        # Stock +3%, market +5%: an UP call is wrong on excess.
        prices = {"BEML": series(100, [0.03]), "NIFTY": series(100, [0.05])}
        g = sc.grade(call(), prices, "NIFTY", 1)
        self.assertAlmostEqual(g["excess"], -0.02)
        self.assertFalse(g["hit"])
        self.assertTrue(sc.grade(call(dir="DOWN"), prices, "NIFTY", 1)["hit"])

    def test_neutral_band_scales_with_horizon(self):
        prices = {"BEML": series(100, [0.015] + [0.0] * 4)}
        c = call(dir="NEUTRAL")
        self.assertFalse(sc.grade(c, prices, None, 1)["hit"])  # 1.5% > 1.0% band
        self.assertTrue(sc.grade(c, prices, None, 5)["hit"])   # 1.5% < 2.2% band

    def test_pending_until_horizon_reached(self):
        prices = {"BEML": series(100, [0.01, 0.01])}
        self.assertEqual(sc.grade(call(), prices, None, 5), "pending")
        self.assertEqual(sc.grade(call(ticker="XYZ"), prices, None, 1), "no prices for ticker")

    def test_brier(self):
        prices = {"BEML": series(100, [0.02])}
        self.assertAlmostEqual(sc.grade(call(conf="0.9"), prices, None, 1)["brier"], 0.01)
        self.assertAlmostEqual(sc.grade(call(conf="0.9", dir="DOWN"), prices, None, 1)["brier"], 0.81)

    def test_backfilled_calls_excluded(self):
        prices = {"BEML": series(100, [0.05, 0.01])}
        # 18 Sep is a Friday; the next open is Monday 21 Sep 09:15 IST.
        late = call(logged_at=datetime(2026, 9, 21, 9, 30, tzinfo=sc.IST))
        graded, status, excluded = sc.score([late], prices, None)
        self.assertEqual(graded[1], [])
        self.assertEqual(status["backfilled (excluded)"], 1)
        graded, _, _ = sc.score([late], prices, None, include_backfilled=True)
        self.assertEqual(len(graded[1]), 1)

    def test_evening_and_weekend_logging_is_on_time(self):
        prices = {"BEML": series(100, [0.05, 0.01])}
        for logged in (datetime(2026, 9, 18, 23, 0), datetime(2026, 9, 20, 18, 0), datetime(2026, 9, 21, 9, 0)):
            c = call(logged_at=logged.replace(tzinfo=sc.IST))
            graded, status, _ = sc.score([c], prices, None)
            self.assertEqual(status["graded"], 1, logged)

    def test_deadline_without_future_prices(self):
        # Scoring the same evening: no prices after entry yet, so assume the next weekday.
        prices = {"BEML": series(100, [])}
        self.assertEqual(sc.logging_deadline(call(), prices),
                         datetime(2026, 9, 21, 9, 15, tzinfo=sc.IST))


class Verdicts(unittest.TestCase):
    def test_small_samples_are_insufficient(self):
        self.assertEqual(sc.verdict(10, 10), "INSUFFICIENT")

    def test_verdicts(self):
        self.assertEqual(sc.verdict(70, 100), "SIGNAL")
        self.assertEqual(sc.verdict(52, 100), "NO EDGE YET")
        self.assertEqual(sc.verdict(30, 100), "WRONG-WAY")

    def test_correction_for_many_agents(self):
        # 62% over 100 calls passes as one test but not as one of 17 agents compared.
        self.assertEqual(sc.verdict(62, 100, sc.z_for(1)), "SIGNAL")
        self.assertEqual(sc.verdict(62, 100, sc.z_for(17)), "NO EDGE YET")
        self.assertAlmostEqual(sc.z_for(1), 1.96, places=2)


if __name__ == "__main__":
    unittest.main()
