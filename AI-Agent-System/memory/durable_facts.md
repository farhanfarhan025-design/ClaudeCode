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
`scripts/margin.py`. **Panel, door, angle and floor rates: last verification date unknown**
— flag before pricing large contracts.

**Verified as at 16 September 2026** against the seven documents in `pricebook/`
(`python3 scripts/pricebook.py --rates`):

| Rate | Card | Real | Status |
|---|---|---|---|
| `door` | 1,800.00 | 1,800.00 | verified 29 Aug 2026, two independent quotes |
| `control_panel` | 1,200.00 | 950.00 | 21% above real — overstates cost |
| `unit_freezer` | 6,400.00 | 17,050.00 | **166% below real — OL-019** |

`panel_sqm`, `angle_piece`, `floor_pair`, `unit_chiller`, `pipe_system`, `wiring_system` and
`lights_per_2_rooms` remain unverified against any vendor quote.

## Vendors

| Fact | Value | Source | Confidence |
|---|---|---|---|
| Arctic (ACC Qatar) — PO email | arcticparts@accqatar.com | Quotation ATC/AZ/QT/26/07619 Rev1, 16 Sep 2026 | high |
| Arctic — contacts | Pandian 50372315 (Sales Engineer) · Jeena 59985144 · Nikhil · Vijay | ATC/AZ, ATC/NSA, ATC/RY, ACC/QT/RVD quotations | high |
| Arctic — LPO condition | Original LPO with company stamp must be presented at the showroom on collection, or the LPO will not be processed | ATC quotations | high |
| Arctic — services | Motor rewinding, PCB repairing, bush bearing, lathe work, compressor overhauling | same | high |
| Arctic — standard terms | Cash · validity 5 days · ex-stock subject to prior sale | same | high |
| Arctic — reference series | ATC/AZ · ATC/NSA · ATC/RY (Rayyan showroom) · ACC/QT/RVD | four quotations, Jul–Sep 2026 | high |
| Arctic — one vendor or several? | Treated as **one**: Pandian / 50372315 named on both the ATC and ACC letterheads; ACC domain shared | inference, not stated | **medium — OL-017** |
| Airtronics Trading Contracting & Maintenance W.L.L. — contact | Gireesh Nath, Sales Manager, +974 3169 0622 | ART-QTN-3174-26, 28 Jul 2026 | high |
| Airtronics — terms | 100% CDC upon collection · ex-works Doha · validity 5 days if stock available | same | high |
| Airtronics — supplies | Dorin semi-hermetic units, Gunay evaporators, Subzero control panels, Danfoss/Castel line components | same | high |

> Arctic's ATC-series quotes are addressed to **Doha Cooling Trading & Solutions**, not TNDK —
> the legacy-name case in `RULES.md` C4. Its ACC/QT/RVD quotation of 29 Aug 2026 is addressed
> to **The New Doha Kitchen** directly, as is the Airtronics quotation. Both names are in live
> use with the same supplier group, so an LPO should state which entity is buying.

The supplier who priced the 16 Sep material list by hand is **not identified** — OL-013.

## Known warranty / AMC position

No warranty expiry dates recorded for any completed project. AMC contracted value: **QAR 0**.
This is a gap, not a finding of fact — ANNUITY's first task is to establish it.

## Clients — quoted, not yet awarded

| Fact | Value | Source | Confidence |
|---|---|---|---|
| Shared Services — contact | Mr. Kenneth Ferran, Purchasing Clerk, +974 3997 2849 | QUT/DCTS/237/2026, 16 Sep 2026 | high |
| Shared Services — address | P.O. Box 3496, Doha | same | high |
| Shared Services — properties | Banana Island Resort by Anantara · Souq Waqif Boutique Hotels by Tivoli · Al Najada Doha by Tivoli · Al Najada Apartments by Oaks · Souq Al Wakrah Hotel by Tivoli | same | high |
| Shared Services — quoted | QAR 21,700.00, supply only, 20-line refrigeration schedule | same | high |
| Shared Services — award | **NONE.** Quotation only, issued 16 Sep 2026, validity 5 days | same | high |

> This is a five-property hospitality group and a first order for them would be a repeat-work
> position, not a one-off. That is relevant to OL-018 — a thin price on an entry job can be a
> deliberate decision, but `RULES.md` B requires it to be a logged one.

