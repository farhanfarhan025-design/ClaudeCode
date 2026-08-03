# OPEN LOOPS

Anything awaiting someone. Every entry has an owner and a date. Closed loops move to
`lessons.md` if they taught something, otherwise they are deleted.

**Opened:** 3 August 2026.

---

## 🔴 Blocking — resolve before related work proceeds

### OL-001 — Samoosa contract value unresolved
**Owner:** Farhan · **Raised:** 2026-08-03 · **Blocks:** any Samoosa document

Three sources disagree:

| Source | Contract | Received |
|---|---|---|
| `approved_register.xlsx` (Drive, 31 Jul) | 38,500 | 20,000 |
| `register_data.json` (skill) | 39,375 | 31,500 |
| `numbering-log.md` receipts | — | 20,000 (RCT-256 only) |

The 875 is the chequered-sheet variation. The 11,500 receipt gap has no receipt number.
Invoices INV-256/257/258 exist against this job; only RCT-256 is logged.

**Needed:** which figure is correct, and whether receipts exist for the 11,500.

### OL-002 — Approved Works Register is arithmetically broken
**Owner:** LEDGER · **Raised:** 2026-08-03 · **Blocks:** any decision using register totals

Balance column reads 0.00 on every row. Total row reads 18,250 (first three rows only).
Summary block reads 0.00 throughout. Details in `analysis/FINDINGS.md`.

**Needed:** rebuild with verified arithmetic. Draft prepared 3 Aug 2026, awaiting Farhan.

### OL-003 — VAT / tax wording contradiction
**Owner:** Farhan · **Raised:** 2026-08-03 · **Blocks:** clean quotation issuance

Invoices may never say "tax". Quotations say "excluding 5% VAT". See `DECISIONS.md` D-005.

**Needed:** a ruling. Option A (remove the VAT line) recommended.

### OL-004 — Margin floor not yet confirmed
**Owner:** Farhan · **Raised:** 2026-08-03 · **Blocks:** PRICE Stage 3 promotion

Proposed at 20% markup on cost — the pricing guide's own lowest tier. PRICE operates on this
until confirmed or changed. See `DECISIONS.md` D-004.

---

## 🟠 Cash — active

### OL-005 — Mesaieed advance bank guarantee
**Owner:** Farhan · **Raised:** LOA dated 2026-05-21 · **Value:** QAR 60,000 advance,
QAR 400,000 contract

Over ten weeks with no advance collected on 53% of the order book. Requires an advance bank
guarantee plus a performance security cheque before the 15% advance is released.

**Standing item in every weekly COLLECT cycle until cleared.** Escalate to headline status if
three consecutive weeks pass with no movement.

### OL-006 — CCC / HIA balance
**Owner:** COLLECT · **Value:** QAR 177,450 (70%)
Due on delivery / progress / completion milestones. Confirm next milestone date and whether
any has already passed without an invoice.

### OL-007 — Jollibee balance
**Owner:** COLLECT · **Value:** QAR 18,400 (40%)
Due after commissioning. Confirm commissioning status.

### OL-008 — Samoosa balance
**Owner:** COLLECT · **Value:** QAR 7,875 *(subject to OL-001)*
Due on completion.

---

## 🟡 Data gaps

### OL-009 — Rate card verification date unknown
**Owner:** PROCURE
No record of when panel, unit or door rates were last checked against a live vendor quote.
Material for any contract above ~100,000.

### OL-010 — No warranty expiry dates recorded
**Owner:** ANNUITY
No completed project has a warranty start or end date. Blocks the entire AMC pipeline.

### OL-011 — Register has no cost or margin column
**Owner:** LEDGER
The book shows revenue and cash but never profit. Realised margin per project is unknown.

### OL-012 — No quote-to-award conversion data
**Owner:** ~~PRICE~~ → **PURSUE** *(reassigned 2026-08-03)*
Quotations issued up to QUT/DCTS/066/2026, but only won jobs are recorded. Win rate unknown,
so the effect of low pricing on win rate cannot be assessed.

Moved out of PRICE because PRICE sees a quotation once, at the moment it is priced, and never
learns what happened to it. PURSUE now owns the pipeline register and the win/loss record; PRICE
consumes the resulting win-rate-by-tier table. See `GOALS.md` G7.

---

## 🟢 Sales — opened 2026-08-03

### OL-013 — No pipeline register exists
**Owner:** PURSUE · **Blocks:** G7, and any conversion figure

Nothing records a quotation that did not become an award. Week-1 task is reconstruction from
`01 - Projects/` and `03 - Under process/`, flagged `reconstructed` and excluded from every rate —
the source recorded only wins.

**Needed:** the register built, then every new quotation entered on the day it is sent.

### OL-014 — Quotation denominator unverified
**Owner:** Farhan · **Blocks:** publishing any conversion percentage

Does `QUT/DCTS/066/2026` count quotations, revisions, or both? Over what period? Shared with
DCTS-branded documents? See `DECISIONS.md` D-011. One line settles it.

### OL-015 — Delivery capacity ceiling undefined
**Owner:** Farhan · **Blocks:** PROSPECT leaving Stage 1

No ops staff, one person on the critical path. Generating demand into that produces delay
penalties, not growth. See `DECISIONS.md` D-010. A rough number is enough.

### OL-016 — Client acquisition source unrecorded, on all 8 awards
**Owner:** ACCOUNT

Referral, tender, consultant specification, prior relationship or inbound — unknown for every
client in the book. The cheapest channel TNDK has cannot be worked because it cannot be seen.
No client has a named contact recorded either.

**Needed:** one conversation with Farhan covering all eight, then recorded permanently.

### OL-017 — Prequalification status unknown
**Owner:** PROSPECT

No record of where TNDK stands with main contractors and MEP consultants — who has it on a bid
list and who does not. Being on the list is upstream of every tender enquiry, and the lead time
to get on one is long.
