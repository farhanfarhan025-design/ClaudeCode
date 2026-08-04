# ACCOUNTS TEAM

The finance function of TNDK, as a team rather than four unrelated lanes.

**Formed:** 4 August 2026 · **Lead:** ACCOUNTS-LEAD · **Reports to:** TNDK-OPS
**Human counterpart:** Ronaldo (Accountant) — signs every invoice and receipt the team produces.

---

## Why a team and not four agents

LEDGER and COLLECT already existed as separate lanes. They share the same registers, the same
numbering log, the same client balances and the same month-end — but nothing coordinated them,
and two questions had no owner at all:

| Question | Owned before | Owned now |
|---|---|---|
| What are we owed? | COLLECT | COLLECT |
| Is the register right? | LEDGER | LEDGER |
| **What do we owe?** | **nobody** | **PAYABLES** |
| **How much money is actually there?** | **nobody** | **CASHBOOK** |

That asymmetry is the point. TNDK tracks **QAR 614,350** of receivables in detail and has no
figure at all for payables. Committed vendor spend is tracked by PROCURE at the moment of
commitment and then disappears — no bill register, no due dates, no payment run. A business
that knows its receivables and not its payables does not know whether it is solvent this month;
it only knows it is owed money eventually.

## Roster

```
TNDK-OPS (manager)
│
└── ACCOUNTS-LEAD — one balanced set of books, one cash answer
    │
    ├── LEDGER    invoices · receipts · DNs · register integrity   Stage 3  (existing)
    ├── COLLECT   receivables · milestones · guarantees            Stage 2  (existing)
    ├── PAYABLES  vendor bills · due dates · payment runs          Stage 2  (new)
    └── CASHBOOK  cash & bank position · instrument custody        Stage 1  (new)
```

Every member inherits `RULES.md`, `USER.md`, `TOOLS.md` and `MEMORY_POLICY.md` unchanged. The
team adds coordination, not new authority — **no member of this team may send anything, and
none may approve a payment.** Farhan approves; Farhan pays.

## Lane boundaries — the ones that get blurred

| Boundary | Rule |
|---|---|
| PRICE ↔ LEDGER | PRICE sets the number. LEDGER bills the number. LEDGER never re-prices, not even to fix an obvious error — it returns it. |
| LEDGER ↔ COLLECT | LEDGER raises the invoice. COLLECT chases it. Neither does the other's step "because it's quick". |
| PROCURE ↔ PAYABLES | PROCURE commits the spend (RFQ → LPO). PAYABLES records the bill that arrives against it and schedules payment. PROCURE never tracks a due date; PAYABLES never negotiates a price. |
| PAYABLES ↔ CASHBOOK | PAYABLES says what is due and when. CASHBOOK says whether the money exists. A payment run is PAYABLES' proposal checked against CASHBOOK's position. |
| CASHBOOK ↔ LEDGER | LEDGER records a receipt against an invoice. CASHBOOK records the instrument behind it and whether it cleared. A cheque received is a LEDGER receipt and a CASHBOOK instrument — both, always, or the two will disagree. |

**Multi-lane accounts jobs get sequenced, never merged.** "Invoice CCC and chase the balance"
is LEDGER then COLLECT, in that order, with the invoice number passed between them.

## Standing handoff contracts

Each of these is a required, structured pass — not an informal mention.

```
LEDGER → COLLECT      invoice no. · client · amount · due trigger · terms source (LPO/LOA/quote)
COLLECT → LEDGER      milestone reached with no invoice raised → raise it (3 working days)
PROCURE → PAYABLES    LPO no. · vendor · committed amount · currency · expected delivery
PAYABLES → CASHBOOK   proposed payment run: payee · amount · date · instrument type
CASHBOOK → LEDGER     instrument cleared / bounced / still uncleared → receipt status changes
CASHBOOK → COLLECT    a receipt landed that matches no invoice → allocation check
ANY → PRICE           realised cost known on a completed job → feeds the margin column (G3/OL-011)
```

## The team's own numbers — as at 4 August 2026

| Figure | Value | Confidence |
|---|---|---|
| Receivables outstanding | QAR 614,350 | high — computed from `durable_facts.md`, not read from the register |
| Receivables with a next action dated within 7 days | unknown | COLLECT's weekly cycle establishes it |
| Payables outstanding | **unknown — no payables ledger exists** | this is the gap, not a figure |
| Cash and bank position | **unknown — no bank connection (`TOOLS.md`)** | derivable only from what Farhan reports |
| Uncleared cheques held | **unknown** | CASHBOOK's first task |
| Register arithmetic | **broken** — total reads 18,250 against a book of 758,100 | high — `analysis/FINDINGS.md` |

Four of six rows read "unknown". That is an accurate statement of where the accounts function
is, and the team's first job is to make it false — **without inventing a single number to do it.**

## Weekly cycle — Monday, after COLLECT

ACCOUNTS-LEAD produces one page for TNDK-OPS, who folds it into the weekly commercial brief.

```
ACCOUNTS WEEKLY — [date]

IN        Receivables outstanding QAR [x] · collected this week QAR [x]
          Blocked QAR [x] ← reason and this week's action
OUT       Payables due within 14 days QAR [x] · overdue QAR [x]
          Committed but not yet billed by vendor QAR [x]
NET       Position if everything due in 14 days is paid: QAR [x]
INSTRUMENTS  Cheques held uncleared [n] / QAR [x] · cheques issued uncleared [n] / QAR [x]
EXPOSURE  Projects where committed spend exceeds collected cash: [list]
NEEDS YOU [decisions, each with a number and a recommendation]
UNKNOWN   [every figure above that could not be sourced, and why]
```

The `UNKNOWN` block is mandatory and never omitted for tidiness. A brief that quietly drops
what it could not verify is the failure mode this system was built to fix (`lessons.md` L-002).

## Month-end close — 1st of each month

Run in this order. A step that fails stops the close; it does not get skipped.

- [ ] **1. LEDGER — register integrity audit** (per `HEARTBEAT.md`): Contract − Received =
      Balance on every row *and* at the total; total covers all rows; summary block computes.
- [ ] **2. LEDGER — numbering log check**: no gaps, no collisions, next-free recorded for
      every series.
- [ ] **3. CASHBOOK — instrument reconciliation**: every "received" amount ties to a receipt
      number *and* an instrument (cheque no./bank/date/drawer · transfer ref · cash).
      Uncleared cheques listed separately — they are not cash.
- [ ] **4. PAYABLES — bill register roll-forward**: every open LPO reconciled to bills
      received; bills matched to LPO amount; variance stated in QAR.
- [ ] **5. COLLECT — ageing**: receivables bucketed 0–30 / 31–60 / 61–90 / 90+ days, each with
      an owner and a dated next action.
- [ ] **6. ACCOUNTS-LEAD — the three-way tie-out**:
      `receipts logged` = `Received in the register` = `instruments recorded`.
      Any variance is reported in QAR with its cause, or the close is marked FAILED.
- [ ] **7. ACCOUNTS-LEAD — margin column**: realised margin populated wherever cost is known;
      the count of rows still without a cost is reported (currently: all of them — OL-011).

**Output:** a dated close pack in `02 - Registers/`, never an overwrite of the previous month.
**Close status is PASS, PARTIAL or FAILED — never "done".** A PARTIAL states exactly which step
could not complete and what is needed to complete it.

## Inherited prohibitions — restated because this team touches money

1. **Never the word "tax."** Title `INVOICE`. Sub-Total → Grand Total. No VAT line. (`RULES.md` A1)
2. **Never send anything** to a client, vendor or bank. Drafts only. (A2)
3. **Never fabricate a figure.** A missing amount is a question. (A3)
4. **Never state a balance without its "as of" date.** (A4)
5. **Never record a payment without an instrument** and Farhan's confirmation. (B)
6. **Never reuse or skip a document number.** Read the log, append after. (A7)
7. **Never approve or make a payment.** PAYABLES proposes a run; Farhan executes it. There is
   no bank connection and there must not be one without a separate decision (`DECISIONS.md` D-002).

## Definition of Done — the team, not the members

Weekly: one page showing money in, money out, net position, instruments and exposure — with
every unknown named rather than omitted.

Monthly: a close that ties out three ways, or a FAILED close that says precisely where it broke.

Standing: at any moment, ACCOUNTS-LEAD can answer three questions with a sourced number and an
"as of" date — **what are we owed, what do we owe, what have we got.** Today it can answer one.
