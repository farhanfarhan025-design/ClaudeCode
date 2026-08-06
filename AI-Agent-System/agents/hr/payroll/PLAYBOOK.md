# PLAYBOOK — PAYROLL

## Trigger

Any of:
- The monthly cycle (`HEARTBEAT.md`): cut-off on the 25th, run prepared 26th–28th.
- A new joiner or leaver inside the month — a part-month calculation.
- Farhan asks what the wage bill is, or what someone's pay works out to.
- A deduction, advance or bonus is instructed.
- A timesheet arrives from TIME.

**Not a trigger:** an employee asking about their own pay. That goes to Farhan. PAYROLL does
not correspond with employees.

## Required inputs

| Input | Required? | If missing |
|---|---|---|
| Roster: basic, allowances, joining date, IBAN, QID | **Yes** | Stop. This is OL-013 — there is no roster yet. |
| Whether food / accommodation is provided in kind | **Yes** | Ask. It decides whether the allowance minimum applies. |
| The month being run | **Yes** | Ask. |
| Timesheet from TIME: overtime hours by category, unpaid days | **Yes**, if anyone worked overtime or was absent | Ask TIME. **Never estimate.** |
| Deductions, with Farhan's written instruction | Only if any apply | No instruction, no deduction. |
| Additions: bonus, site allowance | Only if any apply | Ask. |
| Joiners / leavers in the month, with dates | **Yes** | Ask. A missed leaver is an overpayment; a missed joiner is a late first wage. |
| Job allocation of hours | No — but ask for it | Without it, the labour figure cannot reach PRICE. |

**Do not re-ask for anything already in the conversation.** Extract it. Ask only for what is
genuinely absent and genuinely changes a number.

## Steps

### 1 — Sweep before you run

```bash
python3 scripts/payroll.py check --roster roster.json --as-of YYYY-MM-DD
```

This is cheap, and it catches the things that are painful to discover mid-run: wages below the
minimum, missing IBANs, expired QIDs, and the accrued gratuity liability. Exit code `2` means
at least one blocking failure.

Do this **before** asking TIME for the timesheet, not after. A blocked employee is a
conversation with Farhan, and that conversation takes longer than the payroll does.

### 2 — Build the period file

The roster is durable; the month is not. Everything variable goes in the period file:

```json
{
  "month": "2026-08",
  "cut_off": "2026-08-25",
  "entries": [
    { "id": "TNDK-001",
      "ot_normal_hours": 12,
      "ot_restday_hours": 8,
      "unpaid_days": 0,
      "additions":  [ { "item": "site allowance", "amount": 300 } ],
      "deductions": [ { "item": "salary advance repayment", "amount": 500 } ],
      "job_hours":  { "CCC-HIA": 104, "Samoosa": 16 } }
  ]
}
```

`job_hours` is not used in the wage arithmetic. It is there so the labour actually spent on
CCC/HIA can eventually be compared with what PRICE assumed. Capture it even when it is
incomplete — an incomplete allocation, labelled as incomplete, still beats no data.

### 3 — Run

```bash
python3 scripts/payroll.py run --roster roster.json --period 2026-08.json
python3 scripts/payroll.py run --roster roster.json --period 2026-08.json --sif ./out
python3 scripts/payroll.py run --roster roster.json --period 2026-08.json --json
```

Exit code `2` means a blocking compliance failure. Treat it as a hard stop. The script
**withholds the WPS file** when anything is blocking — that is deliberate. Do not work around
it by running without `--sif` and hand-building a file.

### 4 — Check the arithmetic by hand

Pick one employee — not the same one every month — and re-derive their net without the script:

```
basic + allowances
  + (basic ÷ 240) × overtime hours × multiplier, per category
  + additions
  − (basic + allowances) ÷ 30 × unpaid days
  = gross
  − deductions − social insurance (Qatari nationals only)
  = net
```

If it does not match to the fils, the run stops. This is not ceremony: `margin.py` was trusted
because someone reproduced its worked example to the riyal, and the register was wrong for
months because nobody ever recomputed a total by hand (`memory/lessons.md` L-002).

### 5 — Handle the exceptions

| Gate | What it means | What you do |
|---|---|---|
| `MIN-BASIC` / `MIN-FOOD` / `MIN-ACCOM` | The wage structure is below a statutory minimum | **Stop.** Not an override — it is not Farhan's to waive. Report it, with the shortfall in QAR, and what the compliant figure would be. |
| `NO-IBAN` / `NO-QID` / `NO-BANK` | The employee cannot be paid through WPS | Stop for that employee. Route to PEOPLE. Ask Farhan how they are to be paid this month, and record the answer. |
| `NEGATIVE-NET` | Deductions exceed the wage | **Stop.** Never issue a run with a negative net. Propose a repayment schedule inside the cap instead. |
| `DEDUCTION-CAP` | Deductions exceed 10% of gross (Art. 71) | Stop and ask. Present the compliant amount and how many months it would take. Farhan may instruct otherwise — log the instruction verbatim. |
| `EXPIRED` | QID, contract or health card has expired | Escalate with PEOPLE. Do not quietly pay and move on; an expired permit is a legal exposure that grows every month. |
| `EXPIRING` | Expiry inside 90 days | Not a blocker. Goes in the people brief with a date. |
| `EMPLOYER-ID` | Employer WPS identifiers missing | No WPS file can be produced. OL-014. |
| `SIF-WITHHELD` | The file was suppressed by a blocker | Correct behaviour. Fix the blocker, do not bypass it. |

### 6 — Timing

Wages are due within the statutory window from the end of the period (item 23,
`LABOUR_LAW.md` — unverified, treat as 7 days). Work backwards:

```
25th          TIME closes the timesheet
26th–28th     PAYROLL runs, checks, and hands the draft to Farhan
by month end  Farhan approves
1st–7th       Farhan uploads the WPS file to the bank
```

If a blocker will not clear in time, escalate on the day you find it, not on the deadline.
"The run is blocked and payday is in nine days" is useful. "The run was blocked" on the 7th
is a failure report.

### 7 — Produce the outputs

1. **Payroll register** — one line per employee, appended to Drive as a new dated file in
   `04 - HR/Payroll/`. Never overwrite last month's.
2. **Payslips** — one per employee, draft, showing the full build-up. A payslip that shows
   only a net figure is not a payslip.
3. **Draft WPS SIF** — only if nothing is blocking. Filename ends `-DRAFT`. It stays a draft
   until Farhan has checked it against the bank's template.
4. **The three numbers for the people brief:** wage bill, months of cash cover, accrued
   gratuity liability.
5. **Job hours** — handed to TNDK-HR for routing to PRICE and LEDGER.

### 8 — Hand off

Return the `OUTPUT_SCHEMA.md` payload plus the human-readable register to TNDK-HR. State the
smallest decision Farhan needs to make. Usually there is exactly one, and it is not "approve
the payroll" — it is the exception sitting on top of it.

## Part-month calculations

| Case | Rule |
|---|---|
| Joiner mid-month | Total wage ÷ days in month × days employed. State the divisor used. |
| Leaver mid-month | Same, and hand the rest to EXIT — the settlement is not yours. |
| Unpaid leave | Total wage ÷ 30 × days *(TNDK convention — item 10, confirm)*. |
| Month with 28 or 31 days | The divisor convention does not change with the month. Fix it once, in `DECISIONS.md`, and apply it every month. Inconsistency here is what gets noticed years later. |

## Deductions — the rule that protects everyone

A deduction needs three things, and no run proceeds without all three:

1. **A written instruction from Farhan**, quoted in the log.
2. **A running balance** — what was owed, what is being taken, what remains.
3. **A cap check** — inside 10% of gross, or an explicitly logged instruction to exceed it.

The running balance matters more than it looks. An advance repaid without a balance is the
kind of thing that produces a dispute in month nine, and the person who remembers it
differently is usually the one who was not keeping the record.

## Definition of Done

- [ ] Compliance sweep run **before** the payroll, and every gate reported.
- [ ] Every active employee present; joiners and leavers pro-rated with the divisor stated.
- [ ] Overtime split by category, priced on basic, at the right multiplier.
- [ ] One employee's net re-derived by hand and matching to the fils.
- [ ] Totals reconcile: earned − absence = gross; gross − deductions = net.
- [ ] Every deduction has a written instruction and a running balance.
- [ ] WPS file produced only with zero blockers, marked DRAFT, totals tying to the register.
- [ ] Register appended as a new dated version — nothing overwritten.
- [ ] Wage bill, cash cover and accrued gratuity stated.
- [ ] Job hours captured and handed up.
- [ ] Statutory parameters named with verification status.
- [ ] Output marked **DRAFT — NOT PAID, NOT UPLOADED**.
