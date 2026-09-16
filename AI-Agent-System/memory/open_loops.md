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

**Partially addressed 2026-09-16.** Two live quotations are now captured in `pricebook/`
(refrigeration spares, plus a Dorin condensing unit and Friga-Bohn evaporators). This gives
a first verification point for *spares and plant* rates. It does **not** touch the panel,
door or angle rates in `margin.py`, which remain unverified against any vendor quote.
**Still needed:** a current panel and door quotation.

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

### OL-013 — Vendor unidentified on the 16 Sep material list pricing
**Owner:** Farhan · **Raised:** 2026-09-16 · **Blocks:** any LPO on those rates

A material list was priced by hand and photographed. The sheet names no vendor. It holds the
**only** price on record for the Dorin condensing unit AU-H300CC (9,300.00) and the Friga-Bohn
evaporators (3,475.00 each) — QAR 16,250.00, 87% of that order.

Also unconfirmed on the same sheet: that the figures are **unit** prices rather than line
totals (read as unit prices on three cross-checks against the Arctic quotation — see the
quote file's `price_basis_evidence`), and that the currency is QAR. No total is printed on it.

**Needed:** the vendor's name, and confirmation of the basis. PROCURE cannot commit spend to
a vendor it cannot name. Both quotations expire **21 September 2026**.

### OL-014 — Does the price book belong in the repo or in Drive?
**Owner:** Farhan · **Raised:** 2026-09-16 · **Blocks:** nothing, but decide before it grows

`README.md` and `TOOLS.md` say instructions live in the repo and data lives in Drive. A vendor
price book is neither a register nor client data — it is inbound vendor offers with no other
source of truth, and its value is entirely in its version history (what a price *was* last
time). It is in `pricebook/` for now on that reasoning.

**Needed:** confirm, or nominate a Drive location and it moves. Deciding now is cheap; deciding
after fifty quotations is not.

### OL-015 — Solenoid coil inclusion unconfirmed (Arctic)
**Owner:** PROCURE · **Raised:** 2026-09-16 · **Expires with the quote, 2026-09-21**

Arctic quotes the Castel 1068/4A6 solenoid at 175.00 without saying whether the coil is
included; the competing sheet states 155.00 **including** coil. Two valves are required.
This single question decides which supplier is cheaper on the spares package.

**Needed:** one call to Arctic (Pandian, 50372315 / Jeena, 59985144).

### OL-016 — Project and written award not identified for the 16 Sep material
**Owner:** Farhan · **Raised:** 2026-09-16 · **Blocks:** the exposure check, therefore any LPO

Neither document names the project. Committed spend of up to QAR 18,755.00 cannot be set
against a contract value, collected cash or a written award, so PROCURE's mandatory exposure
check cannot be produced (`agents/procure/IDENTITY.md`).

**Needed:** which project, and whether an LPO/LOA is in hand.

