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
**Owner:** PRICE
Quotations issued up to QUT/DCTS/066/2026, but only won jobs are recorded. Win rate unknown,
so the effect of low pricing on win rate cannot be assessed.

---

## 🔵 People — opened 6 August 2026 with the HR team

Every entry here blocks something. The HR lanes are all at Trust Stage 1 until OL-013,
OL-014 and OL-015 are closed.

### OL-013 — No staff roster exists  🔴
**Owner:** Farhan, with PEOPLE · **Raised:** 2026-08-06 · **Blocks:** every HR lane

This system holds no record of who works for TNDK. `USER.md` says only that Ronaldo handles
accounts and that there are no ops staff to delegate to — but `margin.py` charges 15% of
direct cost for labour and installation on every job, so the work is being done by somebody.

**Needed, per person:** designation, joining date, basic wage, allowances, whether food and
accommodation are provided in kind, QID + expiry, contract dates, IBAN and bank short name,
and whether they are an employee of TNDK, of DCTS, or a subcontractor.

That last question changes everything downstream — gratuity, WPS, minimum wage and permit
obligations all attach to employees and not to subcontractors.

**Goes in Drive** (`04 - HR/roster.json`), never in this repo.

### OL-014 — WPS employer identifiers and bank template unknown  🔴
**Owner:** Farhan · **Raised:** 2026-08-06 · **Blocks:** any WPS file

`scripts/payroll.py` can produce a draft SIF file, but not a usable one. Missing: the MOL
establishment ID, the company QID/CR as the bank expects it, the employer bank short name,
and — most importantly — **the bank's current SIF template**, so the field order can be
verified against it.

A file that computes correctly and is formatted wrongly is a rejected payment, which becomes
a late wage. The script refuses to write a file while the identifiers are placeholders.

### OL-015 — Qatar labour parameters unverified  🔴
**Owner:** Farhan, or a Qatari HR/PRO consultant · **Raised:** 2026-08-06
**Blocks:** any live payroll or settlement

Every figure in `agents/hr/LABOUR_LAW.md` — minimum wage, overtime multipliers, leave,
gratuity, notice, deduction cap — is recorded with its provision and marked **to verify**.
See `DECISIONS.md` D-009. A one-line confirmation on each closes this.

### OL-016 — Accrued end-of-service liability unquantified  🟠
**Owner:** EXIT · **Raised:** 2026-08-06

Gratuity has been accruing since the first hire and appears in no register, no cash forecast
and no balance sheet this system can see. On the **invented** four-person sample it is
QAR 13,803. TNDK's real figure is unknown and is a claim on the same cash the register
reports as outstanding.

Closes as soon as OL-013 does: `payroll.py check` produces it in one command.

### OL-017 — Labour is 15% of direct cost, by assumption only  🟡
**Owner:** TIME, with PRICE · **Raised:** 2026-08-06

`scripts/margin.py` charges labour and installation at a flat 15% — QAR 6,517 on the
documented Suresh example — and it has never been tested against an hour actually worked.
Every realised-margin figure in this system inherits that assumption.

**Needed:** hours booked against jobs for one completed project, priced at real wage rates.
If the true figure is 20%, margins are overstated by about QAR 2,170 on a job that size.

Related: OL-011 (register has no cost or margin column), OL-012 (no win/loss data).

### OL-018 — No employment contracts, permits or expiry dates on file  🟡
**Owner:** PEOPLE · **Raised:** 2026-08-06

No signed contract, QID expiry, health card or site pass is recorded anywhere. TNDK works on
Hamad International Airport and Mesaieed, where an expired permit stops a man at the gate on
a contract worth 33% of the order book. This is not a filing problem.

### OL-019 — No leave records  🟡
**Owner:** TIME · **Raised:** 2026-08-06

Entitlement, taken and balance are unknown for everyone. Consequence: **no final settlement
can be completed** — `payroll.py eos` blocks on a missing leave balance rather than assuming
zero, because assuming zero underpays, systematically and always in the same direction.
