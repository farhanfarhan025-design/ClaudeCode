# MARGIN CHECK + VENDOR COMPARISON — Shared Services, and what the rate card now shows

**Prepared by:** PROCURE · **Date:** 16 September 2026 · **Status:** DRAFT — escalation to Farhan
**Supersedes** `2026-09-16-refrigeration-spares.md`

---

## 🔴 Headline — QUT/DCTS/237/2026 is quoted below the margin floor

Our quotation to **Shared Services** (Mr. Kenneth Ferran), dated today, prices the 20-item
refrigeration schedule at **QAR 21,700.00**. We now hold vendor prices for 19 of those 20
lines. Set one against the other:

| | QAR |
|---|---:|
| Quotation grand total | **21,700.00** |
| Material cost — cheapest source per line | **18,509.00** |
| Gross profit | **3,191.00** |
| **Markup on cost** | **17.2%** |
| **Margin on price** | **14.7%** |

If the whole schedule goes to the one supplier who can supply all of it — the unnamed one who
priced the material list — cost is **18,755.00**, profit **2,945.00**, markup **15.7%**.

**Both figures are below both floors on record:**

| Floor | Source | Verdict |
|---|---|---|
| 22% markup | `RULES.md` B | **BELOW** |
| 20% markup | `scripts/margin.py`, proposed in D-004 | **BELOW** |

`RULES.md` B: *"Quoting below the 22% margin floor — owner override, with written reason,
logged."* No override is logged. `RULES.md` E requires escalation when margin lands below
the floor. **This is that escalation.**

Note the number. `analysis/FINDINGS.md` opens on the pricing guide's own worked example
landing at **14.6%** margin. This quotation lands at **14.7%**. That is not a coincidence —
it is the same gap, and this is the first time it has been visible at the moment of quoting
rather than months later.

### What clearing the floor would cost the client

| To reach | On best-of cost 18,509 | On single-supplier cost 18,755 |
|---|---:|---:|
| 20% markup | 22,210.80 | 22,506.00 |
| 22% markup | 22,580.98 | 22,881.10 |

An uplift of **QAR 881.00** on the quoted figure clears `RULES.md`'s 22% at best-of cost —
4.1% on the price. Whether that is winnable against this client is Farhan's call, not PROCURE's.

### Two lines are worse than thin

| Line | Cost | Sold at | |
|---|---:|---:|---|
| Copper P-trap 1/2" × 2 | 8.00 ea | **7.00 ea** | **sold below cost — loses 2.00** |
| Castel NPT connector 7140/21 × 2 | 7.00 ea | 7.00 ea | zero margin |

Small money, but they are the kind of line that gets copied into the next quotation.

---

## 🟠 The rate card, checked against real quotes for the first time

`python3 scripts/pricebook.py --rates`

| Rate in `margin.py` | Estimating rate | Real quoted | Divergence |
|---|---:|---:|---|
| `door` — 90×190 hinged | 1,800.00 | 1,800.00 | **0% — confirmed** |
| `control_panel` — per room | 1,200.00 | 950.00 | 21% above real (safe direction) |
| `unit_freezer` — unit + evaporator | 6,400.00 | **17,050.00** | **166% above the rate** |

**The `unit_freezer` rate is the finding.** Airtronics quoted the Samoosa freezer plant on
28 July 2026: Dorin AU2-H751CS 7.5 hp at 12,700.00 plus a Gunay GNE 245.8C evaporator at
4,350.00 — **17,050.00** for what the rate card carries at **6,400.00**.

PROCURE escalates any divergence over 10%. This is 166%, and it is structural rather than a
price movement: the rate is **flat per room and does not scale with duty**. That quote is for
a 41.6 cbm freezer at −25 Te. A rate that ignores duty will be roughly right on a small room
and catastrophically low on a large one, with nothing in the process to say which you are in.

Two things follow, and both are Farhan's to decide (`agents/procure/IDENTITY.md`: PROCURE may
only *propose* a rate change, with a real quote as evidence — which this is):

1. The flat freezer and chiller unit rates should become duty-banded, or at minimum carry a
   "confirm with a live quote above X cbm" trigger.
2. Every quotation priced off `unit_freezer` since the rate was set has understated plant cost.
   How many that is, PRICE can establish during the observation weeks the README plans.

**The door rate is now verified.** Two independent quotations nine days apart, both at
1,800.00 (ACC/QT/RVD/1508/2026, 29 Aug; ATC/RY/QT/26/00286, 20 Aug). That is the first rate in
the card with a verification date — a partial answer to OL-009. Panel, angle and floor rates
are still unverified against anything.

---

## 🟡 Samoosa — cost evidence has appeared

The Airtronics quotation is for the **Samoosa freezer room**, 5.2 × 3.2 × 2.5 m = 41.6 cbm.
Plant alone: **QAR 18,525.00**.

Against the Samoosa contract value — disputed at 38,500 or 39,375 (OL-001) — plant alone is
**48.1%** of the lower figure, before panels, doors, flooring, labour or transport.

This does not resolve OL-001 and PROCURE is not the lane that should. It is handed to LEDGER
and PRICE as the first real cost figure that exists for that job, and it bears directly on
OL-011 (the register has no cost or margin column).

---

## Vendor comparison — 20 items now have two or more sources

`python3 scripts/pricebook.py --compare`

Biggest genuine gaps, specification differences excluded:

| Item | Cheapest | Dearest | Gap |
|---|---|---|---|
| Copper P-trap 1/2" | 8.00 *(unnamed)* | 17.00 Arctic | 112% |
| Filter drier DCL 164 flare | 35.00 Arctic | 50.00 *(unnamed)* | 43% |
| Vibration eliminator 1/2" | 50.00 *(unnamed)* | 65.00 Arctic | 30% |
| Pressure switch KP15 | 180.00 *(unnamed, incl. hose)* | 230.00 Arctic (switch only) | 28% |
| Copper coil 1/2" × 50' | 260.00 Arctic | 320.00 *(unnamed)* | 23% |

**A correction to the earlier comparison.** It reported the capillary as having no comparator
and flagged a 205% spread. Wrong — Arctic's own ATC/NSA quotation prices a 1 m capillary
*with 1/4" nut* at 25.00, and Airtronics a 1.5 m at 20.00. Per metre:

| Source | Length | Price | Per metre |
|---|---|---:|---:|
| Airtronics, 28 Jul | 1.5 m | 20.00 | **13.33** |
| Unnamed, 16 Sep | 0.9 m | 16.00 | 17.78 |
| Arctic, 20 Aug | 1.0 m | 25.00 | 25.00 |
| *(us, selling)* | 0.9 m | *20.00* | *22.22* |

Prices that carry a length are now recorded with it and compared per metre.

**Stable prices** — the same figure from Arctic on two dates a month apart: copper 7/8" coil
625.00, copper 1/2" coil 260.00, TE2 valve 185.00, orifice 45.00, KP15 switch 230.00. Those
five are as close to a settled market rate as this record can show.

---

## Defects found in the documents themselves

**1. Arctic ATC/RY/QT/26/00286 does not add up.** Its two lines sum to **5,500.00**; it states
**5,400.00**, in figures and in words, with no discount line. A 100.00 error on the vendor's
face. `--verify` flags it and the quote file carries the discrepancy. Do not order against it
until Arctic reissues or confirms which figure stands.

**2. Two quotations share reference 26/00286** — ATC/NSA and ATC/RY, both dated 20 August, on
different branch prefixes, different items. Not a duplicate, but worth knowing when an LPO
cites "26/00286".

**3. The hinged door is quoted as 3 frame on one document and 4 frame on the other**, both at
1,800.00. Confirm which frame that rate buys before the door rate is treated as settled.

**4. Quotation numbering.** `memory/durable_facts.md` records the quotation series as "next
after QUT/DCTS/066/2026" as at 13 July 2026. Today's quotation is **QUT/DCTS/237/2026**.
Either the numbering log is badly stale or there are two series. `RULES.md` A7 makes the
numbering log the anti-collision mechanism, so this needs reconciling before the next
quotation is raised.

**5. The quotation carries no VAT line.** Sub-Total → Grand Total, which is what D-005
Option A proposes and what `RULES.md` A1 requires on invoices. The practice appears to have
already moved. **OL-003 / D-005 can probably be closed by ruling** — the document is the
evidence.

---

## Exposure check — Shared Services

```
Project:                   Shared Services (Anantara / Tivoli / Oaks properties)
Contract value:            NONE — quoted today, not awarded
Collected to date:         QAR 0.00
Committed vendor spend:    QAR 0.00  (no LPO raised)
Uncollected exposure:      QAR 0.00
Written award in hand?:    NONE — quotation QUT/DCTS/237/2026 issued 16 Sep 2026
```

Nothing to order yet, and nothing should be ordered. `RULES.md` E: materials against no
written award is a stop.

## What PROCURE needs — all of it before 21 September, when both quotes expire

1. **A ruling on the margin floor breach.** Re-price, or override with a written reason and
   log it. The quotation is already signed and dated today, so if it has gone out, the
   override is retrospective and still has to be logged.
2. **Who priced the material list?** They hold the only price on 87% of that order's value
   and no LPO can name them (OL-013).
3. **Does Arctic's 175.00 solenoid include the coil?** Two other sources quote 155.00 *with*
   coil (OL-015).
4. **Is the Arctic / Arctic Cooling Company / ACC Qatar group one vendor?** Pandian on
   50372315 appears on both letterheads and the ACC email domain is shared. Recorded as one
   on that evidence — confirm (OL-017).
