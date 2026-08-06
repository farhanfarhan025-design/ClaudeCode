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

PEOPLE
  Wage bill (committed):  QAR [x]/month
  Months covered by collected cash: [n]
  Accrued gratuity:       QAR [x]  ← the liability in no register
  Expiring inside 30 days:[n]      ← QID · contract · health card

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

## Monthly, 25th — Payroll cut-off  *(TIME)*

Timesheets close. Every active employee gets a complete month or a named gap:

- Overtime **split by category** — normal · night · rest day. A merged figure is unusable.
- Unpaid absence days, distinguished from authorised paid leave.
- Leave taken, and the resulting balance.
- Every site day allocated to a job, or explicitly to "workshop".

Delivered to PAYROLL on the 25th. **A missing day is reported as unknown, never filled in.**

## Monthly, 26th–28th — Payroll run  *(PAYROLL)*

1. `payroll.py check` **first** — minimum wage, deduction cap, WPS readiness, expiries.
   A blocker found on the 26th is a conversation; the same blocker found on the 5th is a late wage.
2. Build the period file from TIME's sheet. Nothing estimated.
3. `payroll.py run`. Exit code 2 is a hard stop.
4. Re-derive one employee's net **by hand** — a different one each month.
5. Register, payslips, draft WPS file. The WPS file only if nothing is blocking.
6. Hand to Farhan with the exception on top, not the total.

```
25th          TIME closes
26th–28th     PAYROLL prepares
by month end  Farhan approves
1st–7th       Farhan uploads the WPS file      ← the statutory window
```

## Monthly, 1st — HR compliance sweep  *(PEOPLE, with EXIT)*

- [ ] Every active employee has a signed contract on file
- [ ] QID · passport · health card · contract expiries inside 90 days, each with an owner
- [ ] Anything **expired** — escalate the same day; it stops a man working on a live site
- [ ] Roster reconciles to last month's payroll: no ghost employee, no missing joiner
- [ ] Accrued end-of-service liability recomputed *(EXIT)* and handed to LEDGER
- [ ] Summer outdoor-work restriction dates confirmed for the year, and who they affect
- [ ] Labour hours by job passed to PRICE — the 15% assumption against actuals

Output: the people brief in `agents/hr/HR_MANAGER.md`. If nothing needs him, four lines.

## Monthly, 1st — Warranty & AMC sweep  *(ANNUITY)*

Every completed project: warranty start, warranty end, AMC status.
Anything expiring within 60 days gets a drafted AMC proposal.

## Reporting rules

- **Never hide a failed run.** A cycle that could not complete says so, with the reason.
- **Never report an unverified figure.** If the register was unreadable, that is the report.
- If nothing needs attention, confirm briefly — silence is indistinguishable from failure.
