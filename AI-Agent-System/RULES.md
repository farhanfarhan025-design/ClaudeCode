# RULES

Binding on every agent. These override any playbook, any convenience, any client pressure.
Ordered: absolute prohibitions first, then approval gates, then standing conventions.

## A. Never — no exception, no override

1. **Never write the word "tax" on an invoice.** Title is `INVOICE`, never "TAX INVOICE".
   Money block goes Sub-Total → Grand Total. No VAT line, no tax line, no tax percentage, ever.
   *(Standing instruction. The invoice generator throws on violation — keep it that way.)*
2. **Never send anything to a client, vendor or bank.** This system has no send capability and
   must never acquire one without an explicit, separate decision by Farhan. All external
   communication is produced as a **draft for Farhan to send himself.**
3. **Never fabricate a financial figure.** Contract values, received amounts, balances, cheque
   numbers and margins are either sourced or asked for. A missing figure is a question, not a guess.
4. **Never state a balance without its "as of" date.**
5. **Never change your own permission level or trust stage.**
6. **Never delete a register, log or issued document.** Supersede and mark; do not remove.
7. **Never reuse a document number.** Read `numbering-log.md` first, append after.
8. **Never work outside your lane.** Return it to the manager instead.
9. **Never produce a payroll that pays below a statutory minimum, or a net of zero or less.**
   Unlike the margin floor, this is **not Farhan's to override** — a minimum wage is not the
   employer's to waive, and an employee's agreement does not change it. Report it as a defect
   and stop. *(HR lanes.)*
10. **Never disclose one person's pay, deduction, QID, bank detail, medical or disciplinary
    matter to anyone but Farhan.** Not to another employee, not as an illustration, not in a
    summary that makes them identifiable. There is no trust stage at which this relaxes.
11. **Never write personal data into this repo.** No name, QID, passport number, wage,
    address or medical detail, and never a scan of any of them. Personnel data lives in
    Drive; this repo holds instructions. *(D-001, applied with extra force.)*
12. **Never state a labour-law entitlement as settled fact** while `agents/hr/LABOUR_LAW.md`
    is unverified. Name the provision, say it is unverified. And never advise Farhan on what
    the law permits him to do — that is for him and a qualified adviser.

## B. Requires Farhan's explicit approval

| Action | Gate |
|---|---|
| Any price shown to a client | Always. No exception at any trust stage. |
| Quoting below the **22% margin floor** | Owner override, with written reason, logged. |
| Issuing an LPO to a vendor | Always. Committed spend. |
| Any figure that reconciles to a contract total | Always. |
| Writing to the numbering log | Always — it is the anti-collision mechanism. |
| Overwriting a register in Drive | Always. Prefer a new dated version. |
| Recording a payment as received | Always, and only against a payment instrument. |
| **Any payroll run, before the WPS file is uploaded** | Always. He is the employer; he approves and he uploads. |
| **Any deduction from a wage** | Always, in writing, quoted verbatim in the log. No instruction, no deduction. |
| **Any change to a wage, allowance, designation or joining date** | Always. These are facts about a contract he signed, not fields to be edited. |
| **Any final settlement figure** | Always, and only with a leave balance behind it. |
| **Any employment contract, offer or salary certificate** | Always. Drafted by PEOPLE, signed and sent by Farhan. |

## C. Standing conventions — the corrections Farhan has already made

These exist because he has corrected them repeatedly. Treat a violation as a defect.

1. **Payee line, exact wording:**
   *"Cheque should be prepared under the name of: The New Doha Kitchen Equipment and Services"*
   — "Equipment and Services", no W.L.L. on this line.
2. **Signatures:** Invoices and receipts → `Ronaldo / Accountant`.
   Quotations → `Farhan / Sales Engineer`. The header email stays `farhan@dctsqatar.com` regardless.
3. **Branding:** A4 portrait, Calibri, dark blue `#1F3864`, gold `#C9A24E`.
   TNDK header block. Never modify the quotation cover page or the promotional images.
4. **Default letterhead is TNDK**, not Doha Cooling. DCTS only to match a legacy document
   or a vendor who knows the old name.
5. **LPO/LOA payment terms govern** over the quotation's terms. When they differ, **say so
   out loud**, then bill on the LPO/LOA.
6. **Flag every shortfall in QAR** and carry it forward onto the next invoice.
7. **Every receipt captures the instrument** — cheque no. + bank + date + drawer, or transfer
   ref + bank + date, or "Payment Mode: Cash". Cheque receipts note *"subject to realization of cheque."*
8. **Currency:** QAR default, comma-separated, 2 decimals (`QAR 59,000.00`). Vendor POs may be
   SR / AED / USD as appropriate.
9. **No physical signature block on LPOs** — the "computer generated document" callout replaces it.

## D. Open contradiction — resolve, do not paper over

> **Invoices** must never mention tax. **Quotations** currently state the grand total is
> *"excluding 5% VAT"*.
>
> These conflict. A client can hold both documents side by side. Qatar had not implemented
> VAT as at the last update of these files, which makes the quotation line questionable too.
>
> **Until Farhan rules on it, PRICE must surface this on any quotation it touches and ask.**
> Do not silently pick one. Record the ruling in `DECISIONS.md` when it comes.

## E. Escalation

Stop before any external-facing output and escalate when:

- A figure is missing and changes the outcome.
- Two sources disagree on a contract value, received amount or balance.
- Margin lands below the floor.
- An LPO's terms differ from the quotation's.
- A cheque's drawer or narration references a different project than the LPO (allocation check).
- A job is proceeding to material order with no written award.
- A guarantee, retention or penalty clause is triggered or approaching.
- **A wage cannot be paid correctly within the statutory window** — escalate on the day it is
  known, not on the deadline.
- **A permit, QID, health card or contract has expired**, or a wage structure breaches a
  statutory minimum.
- **An employee raises a grievance, an injury or a safety complaint** — to Farhan
  immediately and **unedited**. A grievance is never compressed into a status line.

Escalation format is in `MANAGER.md`. Always state the **smallest decision needed**.

## F. HR conventions — proposed, awaiting Farhan's confirmation

> Section C above records corrections Farhan has actually made. **This section does not.**
> TNDK has no documented HR practice in this system yet, so everything below is a proposal
> the HR team operates on until he rules. When he confirms one, it moves into `DECISIONS.md`
> and this list shrinks.

1. **Basic hourly rate = basic ÷ 240** (30 days × 8 hours), for overtime.
2. **Daily rate = total wage ÷ 30**, for unpaid absence, leave encashment and notice in lieu.
3. **Gratuity daily rate = basic ÷ 30**, at 21 days per year of service.
4. The same divisor is used in the contract, the payslip and the final settlement. Changing
   it in one place only is how a quiet inconsistency becomes a labour claim years later.
5. **Payroll cut-off on the 25th**, run prepared by the 28th, WPS uploaded 1st–7th.
6. Employee **IDs, not names**, in any report where the name is not needed for the decision.
7. Payslips show the full build-up. A payslip showing only a net figure is not a payslip.
8. Payroll registers are **appended as new dated versions**, never overwritten — the same
   discipline as the commercial registers, for the same reason.
