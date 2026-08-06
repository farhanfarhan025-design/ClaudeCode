# DECISIONS

Owner-approved choices that should stay stable. Agents read this before proposing a change
to anything listed here. Supersede with a new dated entry; never edit history.

---

### D-001 — Google Drive is the operational source of truth
**Date:** 2026-08-03 · **By:** Farhan · **Status:** current

Registers and client documents live in `TNDK Documents/` in Drive. The `AI-Agent-System/`
repo holds operating instructions only. Data is never duplicated into the repo — duplication
is what caused the current three-way disagreement on Samoosa.

---

### D-002 — Drive-only tool access
**Date:** 2026-08-03 · **By:** Farhan · **Status:** current

No email, WhatsApp, bank or calendar connection. Agents draft; Farhan sends. Adding a sending
capability is a separate, explicit decision — never an incremental drift.

---

### D-003 — PRICE is the first agent built to completion
**Date:** 2026-08-03 · **By:** Farhan · **Status:** current

Chosen over COLLECT, ANNUITY and LEDGER-hardening because the documented margin gap
(30% policy vs 14.6% observed) is the largest measurable value at stake — roughly
QAR 38,000 per 5 margin points across the current book.

---

### D-004 — Margin floor set at 22%
**Date:** 2026-08-03 · **By:** proposed by system · **Status:** ⚠️ AWAITING FARHAN

Derived from the existing pricing guide, which sets 20% for competitive/tender/repeat work
and 30% as the default for new clients. 22% is proposed as the hard floor below which an
explicit owner override is required.

**This is a proposal, not a ruling.** PRICE uses 22% until Farhan confirms or changes it.
Confirm the number, then this entry becomes current.

---

### D-005 — VAT / tax wording contradiction
**Date:** 2026-08-03 · **Status:** ⚠️ UNRESOLVED — blocking

Invoices must never contain the word "tax" (absolute standing rule, script-enforced).
Quotations currently state the grand total is *"excluding 5% VAT"*.

These contradict each other and a client can see both. Options:

| Option | Effect |
|---|---|
| **A** — Remove the VAT line from quotations | Consistent with invoices. Recommended if no VAT is actually charged. |
| **B** — Keep it as a forward-looking caveat | Requires a reason that survives a client asking "so will you charge it?" |
| **C** — Something jurisdiction-specific | Needs Farhan's commercial/legal reasoning recorded here. |

**PRICE must surface this on every quotation it touches until this is ruled on.**

---

### D-006 — Samoosa contract value unresolved
**Date:** 2026-08-03 · **Status:** ⚠️ UNRESOLVED — blocking any Samoosa document

| Source | Contract | Received |
|---|---|---|
| Live `approved_register.xlsx` (Drive) | 38,500 | 20,000 |
| Skill `register_data.json` | 39,375 | 31,500 |
| Receipts logged (`numbering-log.md`) | — | 20,000 (RCT-256 only) |

The 875 difference is the chequered-sheet variation; the 11,500 difference in receipts has
no receipt number behind it. **LEDGER must not issue a Samoosa document until Farhan confirms
which is correct.**

---

### D-007 — An HR team is added, as a sub-team under TNDK-OPS
**Date:** 2026-08-06 · **By:** Farhan (requested) · **Status:** current

Four lanes — PEOPLE, TIME, PAYROLL, EXIT — under a sub-manager, TNDK-HR, which reports to
TNDK-OPS. PAYROLL is built to completion first, on the same pattern as PRICE.

**Why a sub-manager rather than four more lanes on TNDK-OPS.** The routing table works
because it is short and every row is a commercial trigger. Adding four people-lanes to it
would dilute the one thing that keeps routing reliable. HR is also a different data domain:
personal data, statutory obligations, and a confidentiality rule no commercial lane has.

**Why PAYROLL first.** It is the lane with a legal deadline attached and the one that
produces the two figures nothing in the system currently holds — the committed monthly wage
bill, and the accrued end-of-service liability.

---

### D-008 — Wage divisor conventions
**Date:** 2026-08-06 · **By:** proposed by system · **Status:** ⚠️ AWAITING FARHAN

| Convention | Proposed | Used for |
|---|---|---|
| Basic hourly | basic ÷ 240 (30 × 8 h) | Overtime |
| Daily rate | total wage ÷ 30 | Unpaid absence · leave encashment · notice in lieu |
| Gratuity daily | basic ÷ 30 | End-of-service gratuity |

Qatari law states entitlements in weeks and days; the divisor that turns a monthly wage into a
daily or hourly rate is the employer's convention. **What matters is that it is identical in
the employment contract, the payslip and the final settlement.** Using one divisor for
overtime and another for a settlement years later is the kind of quiet inconsistency that
surfaces as a claim.

`scripts/payroll.py` operates on these until Farhan confirms or changes them.

---

### D-009 — Qatar labour parameters are unverified
**Date:** 2026-08-06 · **Status:** ⚠️ UNRESOLVED — blocking any live payroll

`agents/hr/LABOUR_LAW.md` records minimum wage, overtime multipliers, leave entitlements,
gratuity basis, notice periods and the deduction cap — each with its provision. **None has
been checked against the current published law or ADLSA guidance by this system.**

A wrong parameter here is wrong every month, for everyone, silently — the same failure shape
as the register that summed three rows out of eight (`memory/lessons.md` L-002).

**Needed:** confirmation by Farhan or a Qatari HR/PRO consultant. Until then every HR output
names the provision *and* states that it is unverified, and no lane advises Farhan on what
the law permits him to do.

---

### D-010 — A statutory minimum is not an owner override
**Date:** 2026-08-06 · **By:** system, for Farhan's ratification · **Status:** current unless overruled

Every other gate in this system is a business rule Farhan may override as owner — the margin
floor, the pricing tier, the payment terms. **The statutory wage minimum is not**, and neither
is a negative net. It is not the employer's to waive, and an employee's agreement to a lower
figure does not change it.

PAYROLL therefore reports a below-minimum wage as a **defect with a cost attached**, never as
an option with trade-offs, and does not produce a run containing it. Recorded here so that the
one place the system refuses Farhan is explicit and reasoned rather than a surprise.
