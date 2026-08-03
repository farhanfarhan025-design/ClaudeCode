# LOGS

The audit trail. Actions, assessments, overrides and failures.

```
logs/
├── overrides/          YYYY-MM-DD-<client>.md   — below-floor price approvals
├── actions/            YYYY-MM/actions.md       — what each agent did
└── failures/           YYYY-MM/failures.md      — what went wrong, and the outcome
```

## Override log — the important one

A below-floor price cannot be quoted until its override is written. **The log precedes the
price, not the other way round.** If the entry does not exist, PRICE has not been authorised.

Template:

```markdown
# OVERRIDE — <client>, <date>

Job:              <description>
Quotation ref:    <QUT/DCTS/NNN/YYYY or pending>

Total cost:       QAR 51,465.72
Floor price (20%):QAR 61,758.86
Approved price:   QAR 59,000.00
Markup:           14.6%
True margin:      12.8%
Below floor by:   QAR 2,758.86

REASON (Farhan's words):
> <why this price, in his own words — not a reason code, the actual reasoning>

Approved by:      Farhan
Date:             <date>

Outcome:          won / lost / pending
Reviewed:         <date of the retrospective>
```

The `REASON` field is the entire point of this system. In twelve months it is what turns
"we sometimes quote low" into a question that can actually be answered: *did the discounting
win the work, or did we simply earn less on jobs we would have won anyway?*

## Retention

- Overrides: keep permanently. They are the margin history.
- Actions: 12 months.
- Failures: keep permanently until the corresponding `memory/lessons.md` entry exists,
  then 12 months.

## Rules

- Never delete a log to make a report look better.
- A failed run gets logged with the same care as a successful one.
- Every log entry is dated and attributed to an agent.
