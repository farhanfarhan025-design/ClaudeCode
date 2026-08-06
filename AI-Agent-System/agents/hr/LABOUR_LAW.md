# QATAR LABOUR PARAMETERS — the numbers HR computes with

Every statutory figure this system uses, in one place, each with the provision it comes from
and its verification status.

> ## ⚠️ Verification status of this entire file: **UNVERIFIED**
>
> Nothing below has been checked against the current published text of the law or against
> ADLSA's current guidance by this system. It was assembled from general knowledge of Qatari
> labour legislation and **must be confirmed by Farhan or a Qatari HR/PRO consultant before
> the first live payroll run.** `memory/open_loops.md` OL-015.
>
> This is not a formality. A wrong overtime multiplier is wrong every month, quietly, for
> everyone — the same failure mode as the register that summed three rows out of eight
> (`memory/lessons.md` L-002).
>
> **These are minimums set by law. TNDK's own contracts may be more generous — where they
> are, the contract governs and the law is only the floor.**

## How to use this file

- `scripts/payroll.py` holds these values in `DEFAULT_POLICY`; a roster's `policy` block
  overrides them. **Change them in the roster, never mid-run.**
- Every HR output that relies on one of these numbers names the provision and repeats the
  verification status. "Gratuity is 8,721.04" is not an acceptable output. "Gratuity
  8,721.04, at 21 days' basic per year (Art. 54, unverified)" is.
- When Farhan confirms a value, record it in `DECISIONS.md` and change the status here to
  **confirmed**, with the date and who confirmed it.

## Legislation referenced

| Instrument | Covers |
|---|---|
| Law No. 14 of 2004 (Labour Law) | The main body: hours, leave, wages, termination, gratuity |
| Decree-Law No. 1 of 2015 | Wage Protection System — wages paid through a Qatari bank |
| Law No. 17 of 2020 | Minimum wage (in force March 2021) |
| Law No. 18 of 2020 | Change of employer; notice periods |
| Ministerial decisions (ADLSA) | Summer working hours, WPS file format, contract templates |

Qatar has **no personal income tax** on wages. There is no PAYE deduction to compute.
Social insurance applies to **Qatari nationals only** — expatriate employees have no
employee or employer social-insurance contribution.

## The parameter table

| # | Parameter | Value used | Provision | Status |
|---|---|---|---|---|
| 1 | Minimum basic wage | QAR **1,000**/month | Law 17/2020 | to verify |
| 2 | Minimum food allowance | QAR **500**/month, unless food is actually provided | Law 17/2020 | to verify |
| 3 | Minimum accommodation allowance | QAR **300**/month, unless accommodation is actually provided | Law 17/2020 | to verify |
| 4 | Ordinary working hours | **8**/day, **48**/week | Art. 73 | to verify |
| 5 | Ramadan hours | **6**/day, **36**/week | Art. 73 | to verify |
| 6 | Maximum with overtime | **10** hours/day | Art. 73–74 | to verify |
| 7 | Overtime rate | basic hourly **× 1.25** | Art. 74 | to verify |
| 8 | Night work 21:00–06:00 | basic hourly **× 1.50** (shift workers excepted) | Art. 74 | to verify |
| 9 | Rest-day (Friday) work | **× 1.50**, or a compensatory rest day | Art. 75 | to verify |
| 10 | Basic hourly rate | basic **÷ 240** (30 days × 8 h) | practice, not statute | **convention — confirm** |
| 11 | Weekly rest | **1 day**, normally Friday | Art. 75 | to verify |
| 12 | Annual leave, under 5 years | **3 weeks** (21 days) | Art. 79 | to verify |
| 13 | Annual leave, 5 years and over | **4 weeks** (28 days) | Art. 79 | to verify |
| 14 | Public holidays | Eid al-Fitr 3 · Eid al-Adha 3 · National Day 3 · plus employer-set days | Art. 78 | to verify |
| 15 | Sick leave (after 3 months' service) | 2 weeks full · 4 weeks half · 6 weeks unpaid | Art. 82 | to verify |
| 16 | Maternity leave (after 1 year) | **50 days** paid | Art. 96 | to verify |
| 17 | Hajj leave | up to 2 weeks unpaid, once in service | Art. 81 | to verify |
| 18 | End-of-service gratuity | **3 weeks (21 days) basic** per year, after 1 completed year, pro-rata thereafter | Art. 54 | to verify |
| 19 | Gratuity daily rate | basic **÷ 30** | practice | **convention — confirm** |
| 20 | Probation period | maximum **6 months** | Art. 39 | to verify |
| 21 | Notice, service ≤ 2 years | **1 month** | Art. 49 / Law 18/2020 | to verify |
| 22 | Notice, service > 2 years | **2 months** | Art. 49 / Law 18/2020 | to verify |
| 23 | Wage payment frequency | at least **monthly**, within **7 days** of the due date, in QAR through a Qatari bank | Art. 66 / Decree-Law 1/2015 | to verify |
| 24 | Deduction cap for loans/advances | **10%** of wage | Art. 71 | to verify |
| 25 | Repatriation | employer bears return travel at end of service | Art. 55 | to verify |
| 26 | Change of employer | no NOC required | Law 18/2020 | to verify |
| 27 | Social insurance — Qatari nationals | employee 5% · employer 10% of basic | social insurance legislation | to verify |
| 28 | Social insurance — expatriates | **none** | — | to verify |
| 29 | Summer outdoor work ban | outdoor work prohibited in the middle of the day across the summer months | ADLSA ministerial decision | **to verify — dates and hours change; check every year** |

### Items 10 and 19 are conventions, not law

The law states entitlements in weeks and days; it does not always state the divisor used to
turn a monthly wage into a daily or hourly rate. TNDK's own practice decides that, and it
must be **consistent between the employment contract, the payslip and the final settlement**.
Using ÷30 for gratuity and ÷26 for overtime, for example, is not illegal — but it is the kind
of quiet inconsistency that turns into a labour-court claim years later.

**Farhan confirms both divisors once, they go into `DECISIONS.md`, and nothing changes them
afterwards without a new ruling.**

### Item 29 matters more here than in most businesses

TNDK installs cold rooms on live sites — Hamad International Airport, Mesaieed. The summer
midday outdoor-work restriction directly constrains when installation labour can be on site,
which affects programme, which affects the labour hours PRICE assumes. PEOPLE tracks the
current year's dates and hours; SCOPE and PRICE need to know them before committing to a
summer programme.

## What this file deliberately does not contain

- **Legal advice.** These are parameters for arithmetic. Anything that turns on interpretation
  — whether a dismissal falls under Art. 61, whether a role is exempt, whether a contract term
  is enforceable — is escalated to Farhan and, where it matters, to a qualified adviser.
  An agent must never tell Farhan what he is legally entitled to do.
- **Employee data.** No name, QID, wage or contract lives in this repo. `DECISIONS.md` D-001.

## Confirmation record

| Date | Confirmed by | Items | Recorded in |
|---|---|---|---|
| — | — | *nothing confirmed yet* | — |
