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

PIPELINE                        ← from Sunday's TNDK-SALES cycle
  Open quotations:        [n]   QAR [x] unweighted · QAR [x] expected
  Decided this week:      won [n] / lost [n]   ← loss reasons
  Past validity or quiet: [n]   QAR [x]
  Win rate:               [x]% or NOT YET ANSWERABLE ([n] of 20 tracked)

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

## Sunday 09:00 — Pipeline cycle  *(TNDK-SALES / PURSUE)*

Sunday is the first working day of the Qatar week, and this cycle runs **before** Monday's
commercial brief deliberately — its numbers feed the PIPELINE block above.

1. Enter every quotation issued since the last cycle. Anything issued and not entered is the
   defect this cycle exists to catch.
2. Run `python3 scripts/pipeline.py --data pipeline.json --awards awards.json`. Inspect the exit
   code: 2 means quotations require action.
3. For every quotation past its 15-day validity or quiet for 21+ days, draft the follow-up for
   Farhan to send. Asking for a **decision** — never offering a concession.
4. Record every outcome known since the last cycle. Losses get a reason code; `UNKNOWN` is a
   valid entry and a guess is not.
5. Report the quiet list: every open quotation with no client contact in 21 days, with value
   and age. This is the standing duty — it is where the loss record actually comes from.

**Standing item until answered:** the denominator. No conversion percentage is published until
Farhan confirms what the `QUT/DCTS/NNN/YYYY` series counts (D-011). Say so every cycle rather
than quietly publishing one.

## Thursday 16:00 — Margin review  *(PRICE)*

Trailing 10 quotes: quoted price, computed cost, realised margin, win/loss where known.
Flag any quote below the 22% floor and confirm its override was logged.

Report the **weighted** average, not the simple mean — one large low-margin job matters more
than three small good ones.

**Win/loss comes from PURSUE's pipeline register, not from memory.** Once 20 quotations have been
tracked from issue to decision, this cycle also reports win rate by margin tier — the table that
tells Farhan whether quoting low actually wins the work. Until then it reports how many of the 20
are in hand.

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

## Monthly, 1st — Conversion & concentration review  *(TNDK-SALES)*

- Conversion: win rate by count and by value, average decision time, loss reasons ranked.
  State the denominator and whether it is verified. If fewer than 20 tracked decisions exist,
  the report says "not yet answerable" and states how many are in hand. No percentage.
- **Win rate by margin tier** — the G1 answer, once the data supports it.
- Concentration: current top-2 %, and what each open opportunity would do to it if won.
- Sources: which channel produced this month's enquiries. Referral and repeat reported separately.
- Capacity: weighted pipeline plus committed work against the ceiling. If the ceiling is still
  unset (D-010), say so — PROSPECT stays at Stage 1 until it is.

## Reporting rules

- **Never hide a failed run.** A cycle that could not complete says so, with the reason.
- **Never report an unverified figure.** If the register was unreadable, that is the report.
- If nothing needs attention, confirm briefly — silence is indistinguishable from failure.
