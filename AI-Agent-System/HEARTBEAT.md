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

## Monthly, 1st — Warranty & AMC sweep  *(ANNUITY)*

Every completed project: warranty start, warranty end, AMC status.
Anything expiring within 60 days gets a drafted AMC proposal.

## Reporting rules

- **Never hide a failed run.** A cycle that could not complete says so, with the reason.
- **Never report an unverified figure.** If the register was unreadable, that is the report.
- If nothing needs attention, confirm briefly — silence is indistinguishable from failure.
