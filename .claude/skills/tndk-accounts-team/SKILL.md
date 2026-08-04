---
name: tndk-accounts-team
description: Run TNDK's accounts function as a team — the discipline layer above document generation. Use this skill whenever the user asks what TNDK is owed, what it owes, or how much cash it actually has; asks for a weekly accounts page, a month-end close, a reconciliation, a tie-out, or an ageing; mentions payables, vendor bills, supplier statements, a payment run, or whether a bill matches its LPO; asks whether a cheque cleared or bounced, about cheques in hand, post-dated cheques, or the cash/bank position; wants receipts reconciled against the register; asks who should handle an accounts task or how accounts work is split; or reports a payment landing that may not match an invoice. Also trigger on "do the books", "close the month", "reconcile", "what's our position", "can we afford to pay X", exposure of committed vendor spend against collected cash, and any request that spans more than one accounts lane (invoice + chase, receipt + register + cheque status). This skill routes and reconciles; the tndk-accounts skill produces the actual invoices, receipts and registers.
---

# TNDK Accounts Team

The operating discipline for TNDK's accounts function. `tndk-accounts` produces documents;
this skill decides whether the numbers going into them are trustworthy, who does what, and
whether the books tie out.

**Full architecture:** `AI-Agent-System/teams/accounts/TEAM.md` in the ClaudeCode repo, with a
lane contract per member under `AI-Agent-System/agents/`. This skill is that team, made runnable.

## The three questions

A finance function exists to answer three things. Track which ones you can currently answer,
and say so plainly when you cannot:

| Question | Owner | Source |
|---|---|---|
| What are we owed? | COLLECT | Approved Works Register, recomputed from Contract − Received |
| What do we owe? | PAYABLES | Payables register — **build it if it does not exist yet** |
| What have we got? | CASHBOOK | Instrument register + Farhan's confirmed opening cash |

TNDK could historically answer only the first. When a question has no source, the answer is
**"unknown, and here is why"** — never a modelled figure. That honesty is the product here.

## Hard rules — inherited, not negotiable

These come from `RULES.md` and exist because Farhan has corrected them repeatedly.

1. **Never write the word "tax."** Title is `INVOICE`. Sub-Total → Grand Total. No VAT line.
2. **Never send anything** to a client, vendor or bank. Produce drafts; Farhan sends.
3. **Never fabricate a financial figure.** A missing amount is a question, not a guess.
4. **Never state a balance without its "as of" date.**
5. **Never record a payment without an instrument** (cheque no. + bank + date + drawer,
   transfer ref + bank + date, or "Cash") and Farhan's confirmation.
6. **Never reuse or skip a document number.** Read the numbering log first, append after.
7. **Never approve or make a payment.** There is no bank connection. Propose a run; Farhan pays.
8. **Never delete a register or an issued document.** Supersede and mark.

Payee line, exactly: *"Cheque should be prepared under the name of: The New Doha Kitchen
Equipment and Services"*. Invoices and receipts sign `Ronaldo / Accountant`.

## Route it — one lane, one job

Identify the lane before doing anything. The separation is what keeps the books honest; an
agent that drifts across lanes ends up reconciling its own work.

| The task | Lane |
|---|---|
| Invoice, receipt, delivery note, numbering, register rebuild | **LEDGER** |
| Outstanding money, milestones, guarantees, follow-up drafts | **COLLECT** |
| Vendor bill, due date, payment run, LPO-to-bill matching | **PAYABLES** |
| Cash/bank position, cheque status, instrument reconciliation | **CASHBOOK** |
| Two or more of the above, or a close | **ACCOUNTS-LEAD** — coordinate, don't merge |
| Price, cost, discount, margin | **out of team** → PRICE |
| Vendor choice, RFQ, LPO drafting, rate card | **out of team** → PROCURE |

**Sequence multi-lane work, never merge it.** "Invoice CCC and chase the balance" is LEDGER
then COLLECT, with the invoice number passed between them. Out-of-team work goes back to the
user or TNDK-OPS — this skill does not price and does not negotiate with vendors.

The standing handoffs that must not be skipped:

```
LEDGER → COLLECT     invoice no · client · amount · due trigger · terms source (LPO/LOA/quote)
LEDGER → CASHBOOK    every receipt, so the instrument behind it gets recorded and tracked
PROCURE → PAYABLES   LPO no · vendor · committed amount · currency · expected delivery
PAYABLES → CASHBOOK  proposed payment run, checked against what actually exists
CASHBOOK → LEDGER    instrument cleared / bounced → the receipt's status changes
CASHBOOK → COLLECT   a receipt matching no invoice → allocation check, never spread it
```

## Running the numbers

`scripts/close.py` recomputes everything from source rows. Use it rather than reading totals —
the live register's own total row once read 18,250 against a book of 758,100, and looked fine.

```bash
python3 scripts/close.py --data close.json            # month-end close, 7 steps
python3 scripts/close.py --data close.json --weekly   # the weekly accounts page
python3 scripts/close.py --data close.json --json     # machine-readable status
```

Exit code `0` = PASS, `1` = PARTIAL (something unknown), `2` = FAILED (something disagrees).
**Treat a non-zero exit as a stop, not a warning.** Input shape: `assets/example_close.json`,
field-by-field in `references/registers.md`.

What it checks: row-level and total arithmetic · numbering gaps and collisions · the cash split
· payables buckets and LPO matching · receivables ageing · the three-way tie-out · the margin
column · per-project exposure of committed spend against collected cash.

Anything it cannot source lands in an `UNKNOWN` block; anything that disagrees lands in
`VARIANCE`. **Report both verbatim.** Dropping the unknowns to make a report look finished is
the exact failure this system was built to fix.

## The weekly page

Runs Monday, after collections. One page — Farhan's scarcest resource is attention.

```
ACCOUNTS WEEKLY — [date]

IN        Receivables outstanding QAR [x] · collected this week QAR [x]
          Blocked QAR [x] ← reason and this week's action
OUT       Payables due within 14 days QAR [x] · overdue QAR [x]
          Committed but not yet billed QAR [x]
NET       Position if everything due in 14 days is paid: QAR [x]
INSTRUMENTS  Cheques held uncleared [n] / QAR [x] · issued unpresented [n] / QAR [x]
EXPOSURE  Projects where committed spend exceeds collected cash: [list]
NEEDS YOU [decisions, each with a number and a recommendation]
UNKNOWN   [every figure above that could not be sourced, and why]
```

If nothing needs him, say so in four lines. Never pad, and never skip a quiet week — silence
is indistinguishable from a failed run.

## The month-end close

Seven steps, in order, on the 1st. A step that fails **stops** the close; it is not skipped.

1. **LEDGER** — register integrity: Contract − Received = Balance on every row *and* the total.
2. **LEDGER** — numbering: no gaps, no collisions, next-free recorded per series.
3. **CASHBOOK** — instruments: every "received" amount ties to a receipt *and* an instrument.
   Uncleared cheques listed separately; they are not cash.
4. **PAYABLES** — bills: every open LPO reconciled to bills received, variance in QAR.
5. **COLLECT** — ageing: 0–30 / 31–60 / 61–90 / 90+, each with an owner and a dated action.
6. **ACCOUNTS-LEAD** — the three-way tie-out (below).
7. **ACCOUNTS-LEAD** — margin column populated where cost is known; count what still isn't.

Status is **PASS, PARTIAL or FAILED** — never "done". Output goes to a dated close pack in
`02 - Registers/close/YYYY-MM/`, never over the previous month.

### The three-way tie-out

```
receipts logged  =  Received in the register  =  instruments recorded
```

When they disagree, report the variance in QAR, which two of the three agree, and the documents
involved — then **stop**. Do not take the majority answer. This is live today: one client shows
20,000 in the register, 31,500 in a copied data file, and a single logged receipt supporting
20,000. Three sources, three answers, no ruling — so no figure for that client is reported.

## Common jobs

**A vendor bill arrives.** Match it three ways — LPO ↔ delivery ↔ invoice — before it goes near
a payment schedule. No LPO behind it is a **stop**: an unmatched bill is how a business pays for
something it never ordered. A bill exceeding its LPO goes back to PROCURE with the variance in
QAR; never absorb the difference.

**Farhan asks "can we pay X?"** Never answer with a yes. Answer with the payment-run format in
`references/lanes.md`: what is due, in what order, what it leaves, and which projects it pushes
past their collected cash. Then let him decide.

**A payment lands.** Three things happen and none substitutes for another: LEDGER issues the
receipt, CASHBOOK records the instrument and its status, COLLECT closes the balance. A cheque
is not cash until it clears — receipts carry *"subject to realization of cheque"* for exactly
that reason.

**A cheque bounces.** Notify LEDGER (receipt status changes) and COLLECT (the balance is live
again), and log it. Supersede and mark; never quietly reduce a received figure.

**A receipt matches no invoice.** Report it as unallocated. Do not spread it across balances to
make them tidy — check whether the drawer or narration points at a different project.

## Escalate — stop and ask

- The tie-out fails and the cause is not one identifiable document.
- Two sources disagree on a contract value, received amount or balance.
- Payables due within 14 days exceed the cash that can be evidenced.
- Committed spend exceeds collected cash on any project — same day, loudly.
- A bill with no LPO, or a bill exceeding its LPO.
- A "received" amount with no receipt or no instrument behind it.
- A close that cannot complete → report **FAILED**, name the step. Never a PASS by omission.

Always state the **smallest decision** Farhan needs to make, with a recommendation attached.

## Reference files

- `references/lanes.md` — the five lane contracts in full, trust stages, the payment-run and
  escalation formats, and what each lane may never do.
- `references/registers.md` — column schemas for the payables and instrument registers, the
  `close.py` input fields, and how to build either register from scratch.
- `assets/example_close.json` — a worked input carrying four deliberate defects, so you can see
  what a FAILED close looks like before you meet a real one.
