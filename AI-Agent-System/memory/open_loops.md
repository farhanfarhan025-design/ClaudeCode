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

### OL-010 — Mesaieed: LOA requires drawings and stamped design calculations the quotation excluded
**Owner:** Farhan · **Raised:** 2026-08-17 · **Value at risk:** unpriced scope on a 400,000 contract

Quotation DCTS/QT/SQ0005/2026 excludes, at Exclusions item 4(b), "preparation and submission of
architectural/MEP/shop drawings for approval" — client scope.

LOA HBB000353-0 clause 6(iii) requires the Subcontractor to provide "complete drawings with
proper fixing details, Design Calculations with Third party verification and stamping, Method
statements etc." Clause 6(ii) adds all documentation submittals for formal approval.

The LOA governs (`RULES.md` C5). Third-party verification and stamping of a refrigeration load
calculation is a paid external engagement, and it was not in the price.

**Needed:** a decision on who carries the cost, and whether it is raised as a variation. The
consultant has already asked for both the load calculation (comment 9) and shop drawings
(comment 17) in the CDM Smith review of C2024/78-MM-CJV-SPC-0013.

### OL-011 — Mesaieed: LOA folds two years of AMC into the lump sum
**Owner:** Farhan · **Raised:** 2026-08-17 · **Value at risk:** quoted separately at QR 72,000 / 5 years

Quotation SQ0005 offers AMC as an optional extra — "AMC FOR THE COMPLETE SYSTEM FOR EXTENDED 05
YEARS QR 72,000" — and warrants materials for 2 years.

LOA clause 8(a) states the lump sum "includes comprehensive AMC for the initial two years incl
labour, and maintenance." Clause 8(b) makes any extended warranty, AMC or spares beyond two
years a Provisional Sum under Annexure-2 Part B, executed only on written instruction.

Two years of comprehensive AMC including labour is therefore inside the 400,000, not additional.

**Needed:** confirm the cost of two years' comprehensive AMC is carried in the margin on this
contract, and record the AMC obligation in the maintenance log so the visits are actually
planned rather than absorbed ad hoc. This is also the first real entry for `GOALS.md` G5.

### OL-008 — Samoosa: PVC strip curtain not fitted
**Owner:** Farhan → client · **Raised:** 2026-08-10 · **Verify by:** 2026-09-10

Free-maintenance visit on 10 Aug 2026 cleared ice formation on the evaporator fan. Cause is
a missing PVC strip curtain to the door — warm humid air enters every time it opens. The
client was advised verbally on site.

Until the curtain is fitted the icing recurs, and every recurrence is a free call-out
against a 1-year free-maintenance obligation running to 27 Jul 2027.

**Needed:** the recommendation confirmed to the client in writing, and a decision on whether
TNDK supplies and fits the curtain as a chargeable item. Verify at the 10 Sep visit.

### OL-009 — Samoosa: free-maintenance visit count not confirmed
**Owner:** Farhan · **Raised:** 2026-08-10

The free-maintenance period runs 27 Jul 2026 → 27 Jul 2027, but how many visits it includes
is not recorded. Without it the maintenance log cannot say whether TNDK is ahead or behind,
and a client can ask for more visits than were priced.

**Needed:** the visit count from QUT/DCTS/066/2026, entered in the maintenance log.

### OL-003 — VAT / tax wording contradiction ✅ CLOSED 2026-08-10
**Owner:** Farhan · **Raised:** 2026-08-03 · **Closed:** 2026-08-10

Ruled: no VAT mention in any quote. See `DECISIONS.md` D-005. The master quotation template
still carries the old wording and is patched per document — correct it at source on the next
template revision.

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
**Owner:** PRICE
Quotations issued up to QUT/DCTS/066/2026, but only won jobs are recorded. Win rate unknown,
so the effect of low pricing on win rate cannot be assessed.
