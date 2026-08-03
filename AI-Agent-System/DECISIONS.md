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

### D-007 — A sales division is added, as a peer of TNDK-OPS
**Date:** 2026-08-03 · **By:** proposed by system · **Status:** current

The original six lanes start at an enquiry and stop at collected cash. Nothing owned the part
before the enquiry or the part after a quotation was sent. TNDK-SALES is added as a **peer**
manager, not a subordinate one, with four lanes: PROSPECT, QUALIFY, PURSUE, ACCOUNT.

Two managers rather than ten lanes under one, because the cadences differ (a pipeline moves
weekly on client decisions; delivery moves on milestones) and because the review gates differ —
every sales output needs an A9 sweep that no delivery output needs.

Evidence: `analysis/SALES_FINDINGS.md`. Structure: `agents/sales/README.md`.

---

### D-008 — No sales agent states a price, a discount or a delivery date
**Date:** 2026-08-03 · **By:** proposed by system · **Status:** current · **Structural**

Written as `RULES.md` A9. Sales lanes do not read the rate card, cost build-ups or the margin
log at all. They receive tier and reason code from PRICE as analysis data, reportable to Farhan
and never repeatable to a client.

This is the SCOPE/PRICE separation applied to the lane with the strongest incentive to break it.
`README.md` states the principle: the person who wants the job does not set the number alone. A
sales function is by definition the part of the business that wants the job.

**It is not a trust stage and it does not get promoted.** Farhan may of course give any discount
he likes — the rule is that the concession is priced by PRICE and approved by him, not typed into
a follow-up by the agent trying to move the deal.

---

### D-009 — PURSUE is the first sales agent built to completion
**Date:** 2026-08-03 · **By:** proposed by system · **Status:** current

Chosen over QUALIFY, ACCOUNT and PROSPECT for three reasons:

1. It produces a number the business does not have — win rate, decision time, and win rate **by
   margin tier**.
2. That last figure is what makes G1 testable. PRICE is currently holding a floor with no
   evidence about what the floor costs, and the defence of a low price ("we needed it to win")
   cannot be checked.
3. It generates no new demand and needs no capacity ruling — it works quotations already issued.

---

### D-010 — Delivery capacity ceiling
**Date:** 2026-08-03 · **Status:** ⚠️ AWAITING FARHAN — blocking PROSPECT

**How many concurrent cold-room projects, and roughly what value per month, can TNDK deliver
without slipping a programme?**

`USER.md` records no ops staff, no one to delegate to, and Farhan on the critical path for
everything. A demand-generation agent can produce more work than the business can deliver, and
the downside is not a missed opportunity — it is a delay penalty (Mesaieed's LOA carries them),
a damaged main-contractor relationship, and a reputation in a small market.

**Until this is answered, PROSPECT stays at Stage 1** — market map, target list and
prequalification status only. It contacts no one and drafts no approach.

A rough number is enough. "Two mid-size rooms a month alongside the current book" is a usable
answer; no answer is not.

---

### D-011 — What the quotation series counts
**Date:** 2026-08-03 · **Status:** ⚠️ AWAITING FARHAN — blocking any conversion figure

`QUT/DCTS/066/2026` is the highest quotation reference on record. It is **not** established
whether the series counts quotations only or also revisions, whether it runs continuously or
resets annually, or whether it is shared with DCTS-branded documents.

Every conversion percentage depends on this denominator. **PURSUE publishes no win rate until it
is settled** — a rate quoted on a wrong denominator does not get un-quoted.

One line from Farhan will almost certainly resolve it.
