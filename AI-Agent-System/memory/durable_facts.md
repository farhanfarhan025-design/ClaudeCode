# DURABLE FACTS

Sourced, dated commercial facts. Every entry carries source, date, confidence, status.
A fact without a source is not a fact.

**Baseline established:** 3 August 2026, from `approved_register.xlsx` (Drive, modified
31 July 2026) and the `tndk-accounts` skill reference files.

---

## Company

| Fact | Value | Source | Confidence |
|---|---|---|---|
| Legal name | The New Doha Kitchen Equipment Services W.L.L. | conventions.md | high |
| Short name | TNDK | conventions.md | high |
| Associated entity | Doha Cooling Trading & Solutions W.L.L. (DCTS) | conventions.md | high |
| Address | P.O. Box 80247, Doha, State of Qatar | conventions.md | high |
| Tel | 7706 0676 | conventions.md | high |
| Email | farhan@dctsqatar.com | conventions.md | high |
| Default letterhead | TNDK (not Doha Cooling) | tndk-lpo SKILL.md | high |

## Order book — as at 13 July 2026

| Project | Client | Ref | Type | Contract | Received | Balance |
|---|---|---|---|---|---|---|
| Freezer unit replacement | Lean N Fit | LPO 26060001 | LPO | 17,000 | 17,000 | 0 |
| Refrigeration maintenance | Al Noor Bakery | verbal | Cash | 800 | 800 | 0 |
| Cold room maintenance | BSI (Mr. Lijo) | INV-254/2026 | Cash | 450 | 450 | 0 |
| Refrigeration maintenance | Ruwais Farm | INV-014/2026 | Invoice | 1,850 | 1,850 | 0 |
| Jollibee Rasaboud cold room | Sunrise Trading & Food Stuff Co. | PO-2026-0000248 | LPO | 46,000 | 27,600 | 18,400 |
| HIA Airport cold rooms (5) | Consolidated Contractors (CCC) | DIAR-L05531 MCR | LPO | 253,500 | 76,050 | 177,450 |
| Mesaieed animal waste cold room | HBK-BWTC-BEIL JV | HBB000353-0 | LOA | 400,000 | 0 | 400,000 |
| Samoosa cold room (freezer) | Samoosa Shop | QUT/DCTS/066/2026 | Quote | ⚠️ 38,500 *or* 39,375 | ⚠️ 20,000 *or* 31,500 | ⚠️ unresolved |

**Totals (using live register figures):** contract **758,100** · received **143,750** ·
outstanding **614,350**.

> These totals are computed here, not read from the register — the register's own total row
> reads 18,250 and its summary block reads zero. See `analysis/FINDINGS.md`.

**Status:** current, except Samoosa — see `DECISIONS.md` D-006.

## Payment terms

| Client | Terms | Source | Notes |
|---|---|---|---|
| Jollibee / Sunrise | 60 / 40 | LPO PO-2026-0000248 | LPO overrode the quotation |
| CCC / HIA | 30 / 30 / 30 / 10 | LPO DIAR-L05531 MCR | |
| Mesaieed / HBK-BWTC-BEIL JV | 15 advance / 45 after delivery / 20 / 20 | LOA HBB000353-0 | Advance bank guarantee + performance cheque required; 10% retention split 5%+5%; delay penalties; AMC clause |
| Samoosa Shop | 70 / 25 / 5 | QUT/DCTS/066/2026 | No LPO — quotation only |

## Obligations outstanding

| Obligation | Project | Status | Since |
|---|---|---|---|
| Advance bank guarantee | Mesaieed | **Not posted** — blocking 60,000 advance | LOA dated 21 May 2026 |
| Performance security cheque | Mesaieed | Required before advance release | 21 May 2026 |
| Retention 10% (5% + 5%) | Mesaieed | Applies through the contract | 21 May 2026 |

## Concentration

Top-2 clients = **86.2%** of the order book (Mesaieed 52.8% + CCC 33.4%, on 758,100).
The larger of the two has collected nothing.

## Numbering — next free (as at 13 July 2026)

| Series | Next free |
|---|---|
| Invoice | INV-259/2026 |
| Receipt | RCT-257/2026 |
| Quotation | next after QUT/DCTS/066/2026 |
| Delivery note | DN-252/2026 |
| LPO | next after LPO-189/2026 |

## Pricing rate card

Recorded in `tndk-coldroom-quotation/references/pricing-guide.md` and mirrored in
`scripts/margin.py`. **Last verification date unknown** — flag before pricing large contracts.

## Known warranty / AMC position

AMC contracted value: **QAR 0**. Warranty and free-maintenance end dates are recorded for
one project of eight; the rest are still unestablished — a gap, not a finding of fact.

| Project | Cover | From | Ends | Source |
|---|---|---|---|---|
| Samoosa Shop — freezer room | 1 year free maintenance | 27-Jul-2026 | **27-Jul-2027** | Farhan, 10-Aug-2026 |

**Samoosa free maintenance.** Runs to 27 July 2027. The AMC approach is due 60 days before
that — **28 May 2027** (`GOALS.md` G5). Number of visits included in the free period is not
confirmed; the quotation QUT/DCTS/066/2026 should state it (`open_loops.md` OL-009).

Every visit under a free-maintenance period is TNDK cost at zero revenue. Where a repeat
fault has an identified, client-side cause, the recommendation goes to the client **in
writing** — otherwise the repeat visits are absorbed indefinitely and there is no record
that the cause was raised.
