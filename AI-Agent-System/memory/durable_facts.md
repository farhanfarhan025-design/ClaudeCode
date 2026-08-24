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

## Receivables — as at 20 August 2026

| | QAR |
|---|---|
| Live contract value | 786,400.00 |
| Collected to date | (126,750.00) |
| **Total receivable** | **659,650.00** |
| — invoiced and awaiting payment | 63,450.00 |
| — contracted, not yet invoiced | 596,200.00 |

Invoiced: Oscar Prime INV-264 56,250 (transfer advised, credit unconfirmed), Al Zehrabi INV-263
4,900, Sunrise INV-262 2,300. Not yet invoiced: Mesaieed 400,000, CCC/HIA 177,450, Oscar Prime
18,750.

**Mesaieed and CCC hold 87.5% of everything owed, and neither has started on site.** Of the whole
659,650, the sum that could be collected today on the paperwork as it stands is the Mesaieed 15%
advance of 60,000, now 91 days old. Full statement: `reports/receivables_2026-08-20.html`.

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
| ~~LPO-195/2026, 17-08-2026~~ | Doha Controls Trading W.L.L. | **Oscar Prime** cold room | 14,750 | CDC | **CANCELLED** 18-08-2026, replaced by LPO-196 |
| LPO-196/2026, 18-08-2026 | Doha Controls Trading W.L.L. | **Oscar Prime** cold room | 24,500 | CDC | drafted, not issued |
| LPO-197/2026, 18-08-2026 | Al Buhsain Steel Industries W.L.L. (JMB) | **Oscar Prime** cold room (confirmed by Farhan 20-08-2026) | 8,140 | 50% advance / 50% before shipment | drafted, not issued |
| LPO-198/2026, 20-08-2026 | Arctic Cooling Company (ACC) | **Oscar Prime** cold room | 5,400 | cash | drafted, not issued |
| LPO-199/2026, 20-08-2026 | Arctic Cooling Company (ACC) | **Oscar Prime** cold room | 2,900 | cash | drafted, not issued |
| LPO-200/2026, 24-08-2026 | Doha Controls Trading W.L.L. | **project not stated** | 15,000 (quoted 15,500 less 500 agreed) | to be confirmed | drafted, not issued |

Ordered **after** the Jollibee advance was received — LPO 6 Jul, cheque 7 Jul, materials 14 Jul.
Collected 27,600 against committed 9,500, so the project was never funded out of working capital.

This is the first real cost line the system holds. Jollibee refrigeration material is **20.7%**
of the 46,000 contract — one input toward the margin column the register still lacks (OL-011).

No vendor spend is committed against Mesaieed or CCC/HIA.

### Oscar Prime — committed vendor spend as at 20 August 2026

| LPO | Vendor | Content | QAR |
|---|---|---|---|
| LPO-196 | Doha Controls | 2 condensing units + 2 evaporators | 24,500 |
| LPO-197 | Al Buhsain (JMB) | 25 panels, 71.78 m² of 100 mm PIR | 8,140 |
| LPO-198 | Arctic Cooling | 2 hinged cold room doors + 2 Subzero CRC205200 | 5,400 |
| LPO-199 | Arctic Cooling | piping, insulation, valves, driers, brazing consumables | 2,900 |
| | | **Committed** | **40,940** |

**Against the revised 75,000 the committed spend is 54.6%, leaving 34,060** for the control panel, electrical works, transport, lifting and labour, and for the profit.

**54.6% of the revised 75,000 contract, and the job is not fully bought.** Still to come: the control
panel with safeties, the internal light and door frame heater, the electrical works from the
panel onward, transport, lifting and labour — all of which SQ074 sells. What is left to cover
them and to be the profit is **34,060**.

None of the four orders has been issued. All four should follow the **56,250** advance in, not
precede it — and the advance is transferred but not yet confirmed credited (OL-037).

LPO-196 is the refrigeration equipment: **24,500**, or **31.4%** on its own. It replaces LPO-195 (14,750, 18.9%) after the vendor's revised offer -R1 added a
second condensing unit — a 3 HP LH64/2DES-3Y — so the job is now two complete sets, matching
the scope of work sold. **The equipment cost rose 9,750** while the contract has since fallen to 75,000. That is the price
of resolving OL-025 correctly, and it is cheaper than resolving it at commissioning.

Still drafted, not issued, and should stay that way until the 58,500 advance is in — the same
order Jollibee ran in.

**Note the entity.** The vendor quoted Doha Cooling Trading and Solutions W.L.L., so LPO-195 is
issued by Doha Cooling, while the contract and INV-261 are TNDK's. Revenue in one company,
cost in another. The Jollibee P&L raised the same split on two supplier invoices; it is now a
pattern rather than a one-off.

## New order — Oscar Prime, 17 August 2026

| Item | Value |
|---|---|
| Client | Oscar Prime Trading Contracting and Services W.L.L. (attn. Mr. Shameem) |
| Scope | 2 chiller rooms — **Room 01: 2.59 × 1.80 × 3.20 m  ·  Room 02: 3.94 × 2.31 × 3.20 m** (revised) |
| Quotation | QUT/DCTS/SQ074/2026, 16-08-2026 |
| LPO | **OTTS/LPO/19082026-02/2026**, 17-08-2026, signed 18-08-2026 — cancels their -01 |
| Contract value | **QAR 75,000.00** lump sum (revised 17-08-2026, was 78,000) |
| Terms | 75% advance on confirmed LPO · 20% on delivery of material · 5% after testing, commissioning and handover |
| **Advance received** | **QAR 56,250.00** — Commercial Bank transfer from Oscar Prime, value date 19-08-2026. The advice reads *Pending Approval* with no processed date; confirm the credit before relying on it |
| Invoiced to date | **INV-264/2026, 56,250.00** — cancels and replaces INV-261/2026 (58,500 on the superseded LPO) |
| Duration | 05 – 07 days from LPO, subject to site readiness |

The LPO is signed and dated, so the 75% advance falls due now, not on delivery. No vendor spend
is committed against this order yet — the BITZER unit and the Guntner evaporator have to be
ordered, and the terms are written so the advance lands before that commitment is made. Keep it
that way: this is the same sequence that kept Jollibee off working capital.

## Quoted, not yet won — as at 18 August 2026

| Client | Reference | Value | Note |
|---|---|---|---|
| Space Al-Arabi | QUT/DCTS/221/2026 | 400,000 | 8 reefer containers, 100% advance |
| Al Waha Agriculture | QUT/DCTS/222/2026 | 246,675 | cold room 138,000 + air conditioning 108,675 |

**Al Zehrabi Medical, QUT/DCTS/219/2026 — 4,900 — APPROVED 18-08-2026.** Cold room maintenance:
two units water service, one room leak test and re-gas, silicone, door gaps, 25 m pipe insulation
and an outdoor sunshade. Terms 80% advance / 20% on completion, 02 – 03 days. Work order
WO/DCTS/001/2026 issued to the site team the same day. **INV-263/2026 was first drafted for the
80% advance of 3,920, then redrafted at the full 4,900 on Farhan's instruction** before either
version left the office — one number, one document, the 80/20 schedule replaced by a single
payment. Drafted, not sent. An approved quotation is not a payment; confirm the money is in
before the team consumes materials.

The Al Waha air conditioning is bought in from Cool and Rest at 94,500 and sold at 108,675 — a
**15% markup on cost, 13.0% of the section's price**, applied on Farhan's instruction. It is the
first bought-in-and-resold line the system holds with both sides of the number recorded. Two
open questions sit on it: OL-031 on whether 94,500 is six units or seven, and OL-032 on the
missing lead time.

## Concentration

Top-2 clients = **86.2%** of the order book (Mesaieed 52.8% + CCC 33.4%, on 758,100).
The larger of the two has collected nothing.

## Numbering — next free (as at 13 July 2026)

| Series | Next free |
|---|---|
| Invoice | INV-265/2026 — 261 cancelled, 264 Oscar Prime, none yet in the log |
| Receipt | RCT-257/2026 |
| Quotation | next after QUT/DCTS/222/2026, plus the SQ038 / SQ074 series — see OL-018 |
| Delivery note | DN-252/2026 |
| LPO | LPO-201/2026 — 194 Airtronics, 195 cancelled, 196–199 Oscar Prime, 200 Doha Controls |

## Pricing rate card

Recorded in `tndk-coldroom-quotation/references/pricing-guide.md` and mirrored in
`scripts/margin.py`. **Last verification date unknown** — flag before pricing large contracts.

## Known warranty / AMC position

No warranty expiry dates recorded for any completed project. AMC contracted value: **QAR 0**.
This is a gap, not a finding of fact — ANNUITY's first task is to establish it.
