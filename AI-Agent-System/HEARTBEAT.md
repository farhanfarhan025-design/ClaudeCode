# HEARTBEAT

Scheduled cycles. **None of these run unattended until the owning agent reaches Trust Stage 4.**
Until then they are run manually by Farhan — the schedule below defines the *cadence and content*,
not an automation that's already live.

Time zone: **Asia/Qatar (UTC+3)**.

## Monday 08:00 — Weekly Commercial Brief  *(TNDK-OPS)*

The one report worth reading. Everything else is on demand.

```
TNDK WEEKLY — [date]

CASH
  Outstanding:            QAR [x]  (was [y])
  Collected this week:    QAR [x]
  Blocked:                QAR [x]  ← reason, and the action this week

RISK
  Top-2 concentration:    [x]%     (baseline 86.2%)
  Cash behind an unmet precondition: QAR [x]
  Committed vendor spend on uncollected contracts: QAR [x]

MARGIN
  Quotes issued:          [n]   Weighted realised margin: [x]%
  Below floor:            [n]   ← each with its logged reason

NEEDS YOU
  [decisions, each with a recommendation and a number]

MOVED
  [what closed this week]
```

Rule: if nothing needs him, send four lines saying so. Never pad. Never skip because it's quiet.

## Monday 08:00 — Collections cycle  *(COLLECT)*

1. Read the register. Recompute every balance from Contract − Received.
2. Bucket: **due now** / **due on a milestone** / **blocked on a precondition** / **overdue**.
3. For each overdue or blocked item, draft the follow-up message for Farhan to send.
4. Escalate anything where a milestone has passed with no invoice raised.

**Standing item until cleared:** Mesaieed advance bank guarantee. 400,000 contract, zero
collected, LOA dated 21 May 2026. This gets a dated action every single week until it moves.
Do not let it become background noise — it is 53% of the book.

## Monday 09:00 — Accounts weekly page  *(ACCOUNTS-LEAD)*

Runs **after** the collections cycle, because it consumes its output. One page to TNDK-OPS,
who folds it into the commercial brief. Format in `teams/accounts/TEAM.md`.

1. COLLECT's buckets → money in.
2. PAYABLES: due now / due within 14 days / committed but not yet billed → money out.
3. CASHBOOK: cleared · in hand uncleared · committed out. Never merged into one figure.
4. Net position if everything due in 14 days is paid.
5. Projects where committed vendor spend exceeds collected cash.
6. **`UNKNOWN` block** — every figure that could not be sourced, and why. Never dropped for
   tidiness; four of the six headline figures are unknown today and saying so is the report.

## Thursday 16:00 — Margin review  *(PRICE)*

Trailing 10 quotes: quoted price, computed cost, realised margin, win/loss where known.
Flag any quote below the 22% floor and confirm its override was logged.

Report the **weighted** average, not the simple mean — one large low-margin job matters more
than three small good ones.

## Monthly, 1st — Register integrity audit  *(LEDGER)*

- [ ] Contract − Received = Balance on every row, and at the total
- [ ] Total row covers **all** rows *(this has failed before — see `analysis/FINDINGS.md`)*
- [ ] Summary block computes, not zeros
- [ ] Every "received" amount ties to a receipt number
- [ ] Numbering log has no gaps or collisions
- [ ] "As of" date is current
- [ ] Margin column populated where cost is known

Output: variance in QAR. Target zero, or explained.

This audit is **step 1 of the month-end close**, not a standalone task — see below.

## Monthly, 1st — Month-end close  *(ACCOUNTS TEAM)*

Seven steps, in order, owned by ACCOUNTS-LEAD. Full checklist in `teams/accounts/TEAM.md`.

1. LEDGER — register integrity audit (above)
2. LEDGER — numbering log: no gaps, no collisions, next-free recorded
3. CASHBOOK — instrument reconciliation; uncleared cheques listed separately, not as cash
4. PAYABLES — bill register roll-forward; LPO ↔ bill variance in QAR
5. COLLECT — receivables ageing 0–30 / 31–60 / 61–90 / 90+, each with a dated next action
6. ACCOUNTS-LEAD — the three-way tie-out:
   `receipts logged` = `Received in the register` = `instruments recorded`
7. ACCOUNTS-LEAD — margin column populated where cost is known; count the rows still without one

**A failed step stops the close; it is not skipped.** Status is PASS, PARTIAL or FAILED —
never "done". Output is a dated close pack in `02 - Registers/close/`, never an overwrite.

## Monthly, 1st — Warranty & AMC sweep  *(ANNUITY)*

Every completed project: warranty start, warranty end, AMC status.
Anything expiring within 60 days gets a drafted AMC proposal.

## Reporting rules

- **Never hide a failed run.** A cycle that could not complete says so, with the reason.
- **Never report an unverified figure.** If the register was unreadable, that is the report.
- If nothing needs attention, confirm briefly — silence is indistinguishable from failure.
