# OUTPUT SCHEMA — PAYROLL

Every PAYROLL handoff returns this structure. TNDK-HR validates against it.

`scripts/payroll.py --json` emits the computational core of this payload; the agent adds the
narrative fields (`assumptions`, `flags`, `needs_decision`, `handoffs`).

## Structured payload

```json
{
  "agent": "PAYROLL",
  "run_type": "monthly | part_month | correction | estimate",
  "month": "2026-08",
  "cut_off": "2026-08-25",
  "pay_by": "2026-09-07",

  "headcount": 4,
  "totals": {
    "earned": 10445.00,
    "absence": 200.00,
    "gross": 10245.00,
    "deductions": 500.00,
    "social_insurance": 0.00,
    "net": 9745.00
  },

  "employees": [
    {
      "id": "TNDK-001",
      "basic": 1400.00,
      "allowances": 1000.00,
      "overtime": { "normal_hours": 12, "night_hours": 0, "restday_hours": 8,
                    "amount": 157.50 },
      "additions": 0.00,
      "absence_days": 0,
      "absence": 0.00,
      "gross": 2557.50,
      "deductions": [ { "item": "salary advance repayment", "amount": 500.00,
                        "instruction": "Farhan, 2026-07-28",
                        "balance_before": 1500.00, "balance_after": 1000.00 } ],
      "net": 2057.50,
      "job_hours": { "CCC-HIA": 104, "Samoosa": 16 }
    }
  ],

  "compliance": {
    "blocking": [
      { "code": "MIN-BASIC", "employee": "TNDK-003",
        "message": "basic 900.00 below statutory minimum 1,000.00",
        "provision": "Law 17/2020", "verified": false, "shortfall": 100.00 },
      { "code": "NO-IBAN", "employee": "TNDK-003",
        "message": "no IBAN — cannot be paid through WPS" }
    ],
    "flags": [
      { "code": "DEDUCTION-CAP", "employee": "TNDK-001",
        "message": "deductions 19.6% of gross, above the 10% cap",
        "provision": "Art. 71", "verified": false,
        "compliant_alternative": 255.75 }
    ],
    "cleared": ["NEGATIVE-NET", "MIN-FOOD", "MIN-ACCOM", "EXPIRED"]
  },

  "wps": {
    "file": null,
    "withheld_reason": "blocking compliance failures",
    "layout_verified_against_bank": false,
    "uploaded": false
  },

  "brief_figures": {
    "wage_bill_monthly": 9745.00,
    "accrued_gratuity_liability": 13803.23,
    "months_of_cover_from_collected_cash": null,
    "expiries_within_90_days": [
      { "employee": "TNDK-002", "item": "QID", "date": "2026-09-20", "days": 45 }
    ]
  },

  "handoffs": [
    { "to": "PRICE",  "what": "job hours for CCC-HIA (312 h) to test the 15% labour line" },
    { "to": "LEDGER", "what": "monthly labour cost by job for the margin column" },
    { "to": "PEOPLE", "what": "TNDK-003 has no IBAN; TNDK-002 QID renewal due" }
  ],

  "parameters_used": [
    { "name": "minimum basic wage", "value": 1000.00, "provision": "Law 17/2020",
      "verified": false },
    { "name": "overtime multiplier, normal", "value": 1.25, "provision": "Art. 74",
      "verified": false },
    { "name": "basic hourly divisor", "value": 240, "provision": "TNDK convention",
      "verified": false }
  ],

  "assumptions": [],
  "flags": [],
  "needs_decision": [
    { "question": "TNDK-003's basic is below the statutory minimum. Raise to 1,000.00?",
      "cost": "100.00/month · 1,200.00/year",
      "recommendation": "raise — there is no compliant alternative" }
  ],
  "status": "BLOCKED_ON_COMPLIANCE",
  "human_review_required": true
}
```

## `status` values

| Value | Meaning | Manager action |
|---|---|---|
| `READY_FOR_APPROVAL` | Every gate clear. Draft register and WPS file produced. | Present to Farhan. |
| `NEEDS_INSTRUCTION` | Computable, but a deduction or exception needs Farhan's written word. | Present; capture the instruction verbatim. |
| `BLOCKED_ON_COMPLIANCE` | A statutory gate failed. | **Stop.** No WPS file. Escalate with the cost of the fix. |
| `BLOCKED_ON_INPUT` | Timesheet, roster field or joiner/leaver date missing. | Ask the one question. Never estimate. |
| `BLOCKED_ON_EMPLOYER_DATA` | WPS establishment ID, company QID or bank template missing. | OL-014. No file can be produced at all. |
| `ESTIMATE_ONLY` | A planning figure — a forecast wage bill, a costing for a proposed hire. | Label clearly. It must never become a run. |

## Hard requirements

- `human_review_required` is **always `true`**. PAYROLL never returns a run cleared to pay.
- `wps.uploaded` is **always `false`**. There is no code path that sets it true.
- Any entry in `compliance.blocking` **must** pair with `status: BLOCKED_ON_COMPLIANCE`
  and `wps.file: null`. No exceptions.
- Every entry in `parameters_used` carries `verified`. While `LABOUR_LAW.md` is unconfirmed,
  every one of them is `false` — and the human-readable report says so in words.
- Every deduction carries an `instruction` and both balances. A deduction without an
  instruction is a defect, not a line item.
- `compliance.cleared` is not decoration: it is the evidence that a gate was *evaluated*
  rather than skipped. An empty `blocking` list with an empty `cleared` list means the checks
  did not run.
- `assumptions` is never omitted. An empty list is a claim that nothing was assumed — for a
  payroll that claim should be true, so make sure it is before writing it.

## Human-readable companion

Always accompany the payload with the plain register — the table format in `EXAMPLES.md`.
Farhan reads the table; TNDK-HR validates the JSON. Both must agree; a disagreement is a
defect, not a formatting difference.
