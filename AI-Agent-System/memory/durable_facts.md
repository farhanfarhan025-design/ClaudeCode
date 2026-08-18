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
| Jollibee Rasaboud cold room | Sunrise Trading & Food Stuff Co. | PO-2026-0000248 | LPO | 46,000 | 27,600 + part of 23,100 (18-08-2026) | see below |
| HIA Airport cold rooms (5) | Consolidated Contractors (CCC) | DIAR-L05531 MCR | LPO | 253,500 | 76,050 | 177,450 |
| Mesaieed animal waste cold room | HBK-BWTC-BEIL JV | HBB000353-0 | LOA | 400,000 | 0 | 400,000 |
| Samoosa cold room (freezer) | Samoosa Shop | QUT/DCTS/066/2026 | Quote | 38,500 | 38,500 | 0 — settled, confirmed by Farhan 11-08-2026 |
| Jollibee condensing unit relocation | Sunrise Trading | PO-2026-0000310 | LPO | 7,000 | part of 23,100 (18-08-2026) | see below |

**Sunrise, combined position as at 18-08-2026.** The two orders are settled together: 18,400 +
7,000 = 25,400 invoiced and outstanding, against which cheque no. 00990904 (Dukhan Bank,
dated 16-08-2026) brought in **23,100**. **Balance outstanding: QAR 2,300**, invoiced under
INV-262/2026. The client's own receipt voucher 0684 allocates the cheque to cold room work; the
split between the two orders does not change the 2,300.

The shortfall is **exactly 5% of the 46,000 cold room contract**. Neither LPO carries a
retention clause, so this reads as a retention applied by the client's accounts rather than a
keying error — see OL-027.
| Drainage system replacement | Lean N Fit | QUT/DCTS/214/2026 | Cash | 1,200 | 1,200 | 0 — completed & paid 11-08-2026 |

**Totals as at 11 August 2026:** contract **766,300** · received **163,450** ·
outstanding **602,850**.

Live (money still to collect): four projects, 706,500 contracted, 103,650 received,
**602,850 outstanding**. Completed and fully paid: 59,800 across six jobs.

Outstanding concentration: **Mesaieed 66.4%**, Mesaieed + CCC together **95.8%**.

Outstanding now sits in exactly three projects: Mesaieed 400,000 (67.1%), CCC 177,450 (29.8%),
Jollibee 18,400 (3.1%). Two clients hold **96.9% of the outstanding money**.

> These totals are computed here, not read from the register — the register's own total row
> reads 18,250 and its summary block reads zero. See `analysis/FINDINGS.md`.

**Status:** current. Samoosa settled at 38,500 — Farhan confirmed the payment cleared on
11 August 2026. Two records items remain open and are bookkeeping only, not money owed:
the 875 chequered-floor variation was never separately collected, and INV-258 (7,875) still
over-bills the final stage by 5,075 against the invoice trail. See `DECISIONS.md` D-009.

**Pending evidence:** the Samoosa final payment of 18,500 is confirmed by Farhan (6 Aug 2026)
but has **no instrument recorded yet**, so no receipt has been issued and the Drive register has
not been updated. Confidence: high on the amount, absent on the instrument.

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

## Vendor commitments

| LPO | Vendor | Project | Value | Terms | Status |
|---|---|---|---|---|---|
| LPO-194/2026, 14-07-2026 | Airtronics Trading Contracting & Maintenance | **Jollibee Rasaboud** (confirmed by Farhan 11-08-2026) | 9,500 | 100% CDC upon collection | ordered |
| LPO-195/2026, 17-08-2026 | Doha Controls Trading W.L.L. | **Oscar Prime** cold room | 14,750 | CDC | drafted, not issued |

Ordered **after** the Jollibee advance was received — LPO 6 Jul, cheque 7 Jul, materials 14 Jul.
Collected 27,600 against committed 9,500, so the project was never funded out of working capital.

This is the first real cost line the system holds. Jollibee refrigeration material is **20.7%**
of the 46,000 contract — one input toward the margin column the register still lacks (OL-011).

No vendor spend is committed against Mesaieed or CCC/HIA.

LPO-195 is the refrigeration equipment for Oscar Prime: 14,750 against a 78,000 contract, or
**18.9%**. It is drafted but not issued, and should stay that way until the 58,500 advance is
in — the same order Jollibee ran in.

**Note the entity.** The vendor quoted Doha Cooling Trading and Solutions W.L.L., so LPO-195 is
issued by Doha Cooling, while the contract and INV-261 are TNDK's. Revenue in one company,
cost in another. The Jollibee P&L raised the same split on two supplier invoices; it is now a
pattern rather than a one-off.

## New order — Oscar Prime, 17 August 2026

| Item | Value |
|---|---|
| Client | Oscar Prime Trading Contracting and Services W.L.L. (attn. Mr. Shameem) |
| Scope | Supply, installation, testing and commissioning of 2 cold rooms, 3.75 × 2.00 × 3.00 m |
| Quotation | QUT/DCTS/SQ074/2026, 16-08-2026 |
| LPO | OTTS/LPO/19082026-01/2026, 17-08-2026, signed by their General Manager |
| Contract value | **QAR 78,000.00** lump sum |
| Terms | 75% advance on confirmed LPO · 20% on delivery of material · 5% after testing, commissioning and handover |
| Invoiced to date | INV-261/2026, 58,500.00 (the 75% advance), raised 17-08-2026 — **not yet sent** |
| Duration | 05 – 07 days from LPO, subject to site readiness |

The LPO is signed and dated, so the 75% advance falls due now, not on delivery. No vendor spend
is committed against this order yet — the BITZER unit and the Guntner evaporator have to be
ordered, and the terms are written so the advance lands before that commitment is made. Keep it
that way: this is the same sequence that kept Jollibee off working capital.

## Concentration

Top-2 clients = **86.2%** of the order book (Mesaieed 52.8% + CCC 33.4%, on 758,100).
The larger of the two has collected nothing.

## Numbering — next free (as at 13 July 2026)

| Series | Next free |
|---|---|
| Invoice | INV-263/2026 — 259/260 Sunrise, 261 Oscar Prime, 262 Sunrise balance, none yet in the log |
| Receipt | RCT-257/2026 |
| Quotation | next after QUT/DCTS/220/2026, plus the separate SQ074 series — see OL-018 |
| Delivery note | DN-252/2026 |
| LPO | LPO-196/2026 — 194 to Airtronics, 195 to Doha Controls |

## Pricing rate card

Recorded in `tndk-coldroom-quotation/references/pricing-guide.md` and mirrored in
`scripts/margin.py`. **Last verification date unknown** — flag before pricing large contracts.

## Known warranty / AMC position

No warranty expiry dates recorded for any completed project. AMC contracted value: **QAR 0**.
This is a gap, not a finding of fact — ANNUITY's first task is to establish it.
