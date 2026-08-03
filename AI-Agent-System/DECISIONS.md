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
