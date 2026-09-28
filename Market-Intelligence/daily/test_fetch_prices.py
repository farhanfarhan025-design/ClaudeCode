#!/usr/bin/env python3
"""Tests for fetch_prices.py parsing (no network). Run: python3 test_fetch_prices.py"""

import io
import unittest
import zipfile
from datetime import date

import fetch_prices as fp

BHAV = (
    "TradDt,BizDt,Sgmt,Src,FinInstrmTp,FinInstrmId,ISIN,TckrSymb,SctySrs,XpryDt,FininstrmActlXpryDt,"
    "StrkPric,OptnTp,FinInstrmNm,OpnPric,HghPric,LwPric,ClsPric,LastPric,PrvsClsgPric\n"
    "2026-09-25,2026-09-25,CM,NSE,STK,1,INE258A01016,BEML,EQ,,,,,BEML LIMITED,2100,2130,2090,2104.35,2105,2095.4\n"
    "2026-09-25,2026-09-25,CM,NSE,STK,2,INE000000000,SOMEBOND,N1,,,,,BOND,100,100,100,100.1,100,100\n"
    "2026-09-25,2026-09-25,CM,NSE,STK,3,INE263A01024,BEL,BE,,,,,BHARAT ELEC,300,305,298,301.2,301,299\n"
)
IDX = (
    '"Index Name","Index Date","Open Index Value","High Index Value","Low Index Value","Closing Index Value"\n'
    '"Nifty 50","25-09-2026","23063.1","23180.0","23010.5","23140.50"\n'
    '"Nifty IT","25-09-2026","1","1","1","1"\n'
)


def zipped(text):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("BhavCopy_NSE_CM_0_0_0_20260925_F_0000.csv", text)
    return buf.getvalue()


class Parse(unittest.TestCase):
    def test_equities_keep_eq_and_be_only(self):
        rows = fp.parse_equities(zipped(BHAV))
        self.assertEqual(rows, [("2026-09-25", "BEML", 2104.35), ("2026-09-25", "BEL", 301.2)])

    def test_indices_map_nifty(self):
        rows = fp.parse_indices(IDX.encode(), date(2026, 9, 25))
        self.assertEqual(rows, [("2026-09-25", "NIFTY", 23140.5)])


if __name__ == "__main__":
    unittest.main()
