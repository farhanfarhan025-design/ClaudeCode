# QA CHECKLIST — PAYROLL

Run before every handoff. A failed item is a stop, not a note.

## Arithmetic

- [ ] One employee's net re-derived **by hand** and matching the script to the fils.
      Not the same employee as last month.
- [ ] Basic hourly = basic ÷ 240 — computed on **basic**, never on total wage.
- [ ] Each overtime category priced at its own multiplier: normal 1.25 · night 1.5 ·
      rest day 1.5. Not merged into one line, not averaged.
- [ ] Unpaid absence = (basic + allowances) ÷ 30 × days, and the divisor is the one in
      `DECISIONS.md` — not the number of days in this particular month.
- [ ] Earned − absence = gross. Gross − deductions − social insurance = net.
- [ ] The register total equals the sum of the lines, recomputed — not carried from the script.
- [ ] Part-month joiners/leavers pro-rated, with the divisor stated on the line.
- [ ] Social insurance applied to Qatari nationals only, on basic.

## Compliance gates — every one evaluated, including the ones that pass

- [ ] Minimum basic checked against every employee.
- [ ] Food and accommodation allowances checked, and the in-kind exemption verified against
      the roster rather than assumed.
- [ ] No net pay is zero or negative.
- [ ] Every deduction inside the 10% cap, or carrying a logged written instruction.
- [ ] Every deduction has a running balance: was owed / taken / remains.
- [ ] Every employee in the WPS file has QID, bank short name and IBAN.
- [ ] QID, contract, health card and passport expiries swept; anything expired escalated.
- [ ] Payment can be made within the statutory window from period end — checked against the
      calendar, not assumed.
- [ ] `payroll.py` exit code inspected. Exit 2 was treated as a stop.

## Source discipline

- [ ] Every wage and allowance traces to the roster, which traces to a signed contract.
- [ ] Every overtime hour and absence day traces to TIME's sheet. **Nothing estimated.**
- [ ] No timesheet was edited by PAYROLL for any reason.
- [ ] Joiners and leavers reconciled against PEOPLE's and EXIT's records, not just the roster.
- [ ] Every statutory parameter used is named, with its verification status.

## Rules compliance

- [ ] Output marked `DRAFT — NOT PAID, NOT UPLOADED`.
- [ ] Nothing was sent, uploaded, submitted or filed. No send capability exists — confirm
      none was implied or simulated.
- [ ] No wage, allowance or deduction was changed by PAYROLL.
- [ ] No wage below a statutory minimum appears anywhere in the output, in any scenario,
      including a "for comparison" one.
- [ ] No employee's figures appear in anything destined for anyone other than Farhan.
- [ ] Employee IDs used in place of names wherever the name was not needed.
- [ ] The register was appended as a new dated version. Nothing was overwritten.
- [ ] The WPS file exists only if zero blockers; its net total ties to the register exactly.

## Presentation

- [ ] Leads with the exception and the decision needed, not with the total.
- [ ] Money formatted `QAR 0,000.00`. No "approximately", no rounding for tidiness.
- [ ] Assumptions labelled as assumptions.
- [ ] The wage bill, cash cover and accrued gratuity are stated for the people brief.
- [ ] Job hours captured and handed up for PRICE.
- [ ] Short enough to read in under a minute.

## Self-assessment before handoff

Answer honestly. A "no" is an escalation, not a note to self.

1. Did I meet every Definition of Done condition?
2. Is every figure traceable to a contract, a timesheet, or Farhan's written instruction?
3. Did I estimate anything at all? *(For payroll the answer must be no. Not "not much".)*
4. Would a second reviewer reach the same net for every employee from the same inputs?
5. Could each employee, shown only their own payslip, understand how their net was reached?
6. Is human review still required? **(For PAYROLL the answer is always yes.)**
