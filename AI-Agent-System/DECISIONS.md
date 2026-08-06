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
**Date:** 2026-08-03 · **Status:** superseded → D-008 (2026-08-06)

| Source | Contract | Received |
|---|---|---|
| Live `approved_register.xlsx` (Drive) | 38,500 | 20,000 |
| Skill `register_data.json` | 39,375 | 31,500 |
| Receipts logged (`numbering-log.md`) | — | 20,000 (RCT-256 only) |

The 875 difference is the chequered-sheet variation; the 11,500 difference in receipts has
no receipt number behind it. **LEDGER must not issue a Samoosa document until Farhan confirms
which is correct.**

---

### D-007 — Accounts becomes a team, with two new lanes
**Date:** 2026-08-04 · **By:** proposed by system · **Status:** ⚠️ AWAITING FARHAN

LEDGER and COLLECT are grouped under **ACCOUNTS-LEAD** as a team (`teams/accounts/TEAM.md`),
and two lanes are added: **PAYABLES** (vendor bills, due dates, payment runs) and **CASHBOOK**
(cash and bank position, instrument custody).

**Reasoning.** Receivables are tracked to the riyal — 614,350 across eight clients. Payables are
tracked nowhere, and nothing distinguishes cleared money from an uncleared cheque. PROCURE's own
exposure check asks for "committed vendor spend vs collected cash" and nothing can answer the
first half after the LPO is issued. Three questions define a finance function; TNDK could answer
one. See `GOALS.md` G7.

**What this does not change.** No new authority. No bank connection. No payment capability —
PAYABLES proposes a run, Farhan pays. D-002 (Drive-only, agents draft and Farhan sends) stands
unchanged, and this decision must not be read as eroding it.

**Needed from Farhan:** confirm the team structure, confirm Ronaldo remains the human counterpart
and the signatory on invoices and receipts, and confirm which of the two new registers is built
first. Recommended: **payables**, because it is the one with money attached to being wrong.

---

### D-008 — Samoosa figures resolved: the register was right
**Date:** 2026-08-06 · **By:** Farhan · **Status:** superseded → D-009 (same day). The
ruling on the amount stands; the conclusion drawn from it was wrong.

Farhan confirmed the final Samoosa payment as **QAR 18,500**, which settles the three-way
disagreement that had blocked every Samoosa document since 3 August:

| Source | Contract | Received before final | Verdict |
|---|---|---|---|
| Live `approved_register.xlsx` | 38,500 | 20,000 | **correct** |
| Skill `register_data.json` | 39,375 | 31,500 | **wrong — do not use** |
| Receipts logged (`numbering-log.md`) | — | 20,000 (RCT-256) | consistent with the register |

Samoosa is now fully settled: contract 38,500, received 38,500, balance nil.

**Consequence for the system, not just for Samoosa:** the copied data in the skill's assets was
the wrong one. That is `lessons.md` L-003 confirmed in practice — the copy drifted, and the copy
was the one that disagreed. Any remaining figures in skill assets are suspect until checked
against Drive.

**Still outstanding:** the payment instrument (cheque no. + bank + date + drawer, transfer
reference, or cash). The receipt cannot be issued and the register cannot be updated without it
— `RULES.md` B and C7.

---

### D-009 — Samoosa is not settled: the variation and INV-258 do not reconcile
**Date:** 2026-08-06 · **By:** system · **Status:** ⚠️ OPEN — supersedes D-008

D-008 concluded Samoosa was closed. That was wrong, and the error was mine: I offered
"QAR 18,500" as the settlement figure because the live register shows 38,500 − 20,000. The
register's 38,500 **excludes the 875 chequered-floor variation.** The numbering log's client
registry records the contract as *"38,500 + 875 variation (2mm chequered floor) = 39,375"*.

    20,000 already received + 18,500 confirmed = 38,500
    contract including the variation           = 39,375
    still outstanding                          =    875

**Second and larger problem — the invoice trail does not tie.** Three invoices were issued:

| Invoice | Amount | Composition |
|---|---|---|
| INV-256 | 20,000 | advance |
| INV-257 | 16,575 | 9,625 (25% stage) + 6,950 carried shortfall |
| INV-258 | 7,875 | 7,000 + 875 variation |

The 6,950 carried shortfall reconciles exactly: 70% of 38,500 is 26,950, and 26,950 − 20,000 =
6,950. So the base contract of 38,500 and the 20,000 receipt are both confirmed.

But the final stage should be 5% + variation = 1,925 + 875 = **2,800**. INV-258 was issued at
**7,875 — over by 5,075.** That 7,875 is exactly 39,375 − 31,500, so INV-258 was computed on
the assumption that **31,500** had been received. Only 20,000 has a receipt (RCT-256, cash).

**Two possibilities, and they are not both true:**

1. Only 20,000 was ever received → INV-258 over-bills by 5,075 and should be superseded by a
   corrected invoice at 2,800; after the 18,500, **875 remains outstanding**.
2. 31,500 was genuinely received → 11,500 has no receipt, INV-258's 7,875 was correct, and the
   settlement should have been 7,875, not 18,500.

**Needed from Farhan:** how much has Samoosa actually paid in total, and against which invoices.
Until then, no Samoosa receipt is issued and the register is not updated. The client may be owed
a corrected invoice or a refund; both are worse to discover later.

**Process lesson:** I offered a figure derived from one source and treated the owner's selection
as confirmation of that source's correctness. Confirming an amount is not the same as confirming
the reconciliation behind it. Options presented for approval must carry their own reconciliation,
or they launder an assumption into a ruling.
