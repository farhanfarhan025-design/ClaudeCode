# GOALS

What this system exists to move. Every agent's Definition of Done ties back to one of these.

Baseline figures are as at the **13 July 2026** register snapshot, verified against the live
`approved_register.xlsx` in Drive on **3 August 2026**.

## G1 — Margin discipline  *(owner: PRICE)*

**Problem.** The documented default margin is **30%**. The worked example in the pricing guide
prices a job at cost 51,465 and quotes **59,000** — a realised margin of **14.6%**. Policy and
practice have diverged and nothing measures the gap.

**Outcome.** Every quotation carries a computed cost build-up and a stated realised margin
before it goes out. Nothing is priced below the floor without a logged, deliberate override.

**Definition of Done.**
- Every quote has a `margin-worksheet` entry with direct cost, labour, transport, price, realised %.
- Zero quotes issued below the 20% floor without an owner override recorded in `logs/overrides/`.
- A rolling realised-margin figure exists for the trailing 10 quotes.

**Metric.** Weighted average realised margin. Baseline 14.6% (single observed case).
**Target: ≥25% on new clients within 90 days.**
Each 5 points across a 758k book ≈ **QAR 38,000**.

## G2 — Cash conversion  *(owner: COLLECT)*

**Problem.** QAR **614,350** outstanding. No follow-up cadence. The largest contract
(Mesaieed, 400,000) has collected **zero** and is blocked on a bank guarantee that has been
outstanding since the LOA was dated **21 May 2026** — over ten weeks.

**Outcome.** Every outstanding riyal has a named next action, an owner and a date.

**Definition of Done.**
- Weekly collections brief: due / blocked / overdue, each with a drafted follow-up.
- Zero milestones pass their trigger without an invoice raised within 3 working days.
- The bank-guarantee blocker has a dated action every week until cleared.

**Metric.** Days-sales-outstanding, and % of book with a next action dated within 7 days.

## G3 — Register integrity  *(owner: LEDGER)*

**Problem.** The live register displays a **TOTAL of 18,250** against an actual book of
**758,100** — the total formula covers only the first three rows. Balance column reads
**0.00 on every row**, including a 400,000 contract with nothing received. The summary block
reads 0.00 throughout. It was last updated 31 July and is already out of step with the
skill's own data on Samoosa.

**Outcome.** One register, correct arithmetic, current date, no silent drift.

**Definition of Done.**
- Contract − Received = Balance holds on every row and at the total.
- Receipts logged reconcile to Received in the register, or the variance is stated.
- Register carries an "as of" date no more than 7 days old.
- A margin column exists so the book shows *profit*, not just revenue.

**Metric.** Reconciliation variance in QAR. **Target: 0, or explained.**

## G4 — Concentration risk  *(owner: TNDK-OPS manager)*

**Problem.** Mesaieed (52.8%) + CCC/HIA (33.4%) = **86.2%** of the order book in two clients.
One is uncollected.

**Outcome.** The risk is visible and quantified every week rather than discovered late.

**Definition of Done.** Weekly brief states top-2 concentration %, cash-at-risk, and whether
committed vendor spend is exposed to an uncollected contract.

**Metric.** Top-2 concentration %. **Direction: down, via more mid-size work — not by losing the big ones.**

## G5 — Recurring revenue  *(owner: ANNUITY)*

**Problem.** AMC appears exactly once in the entire system — a note on the Mesaieed LOA.
Every room installed is an annuity not being captured.

**Outcome.** Every completed installation generates a warranty-expiry date and an AMC approach.

**Definition of Done.**
- Every completed project has a warranty end date recorded.
- An AMC proposal is drafted 60 days before each warranty expiry.
- An AMC pipeline register exists with expected annual value.

**Metric.** AMC contracted annual value. **Baseline: QAR 0.**

## G6 — Owner off the critical path  *(cross-cutting)*

**Problem.** Sales, quoting, procurement, invoicing, collections and filing all run through
one person. The existing skills made that person *faster*, not *replaceable*.

**Outcome.** Farhan's time goes to pricing decisions, client relationships and vendor
negotiation. Document production and tracking do not need him.

**Definition of Done.** For a standard job — enquiry to quote to LPO to invoice to receipt —
Farhan makes **decisions** (scope, price, approve-to-send) and touches **no document production**.

**Metric.** Owner-touches per completed job. **Direction: down.**

## G7 — Payroll integrity and labour compliance  *(owner: TNDK-HR / PAYROLL)*

**Problem.** Staff work existed in no lane of this system. There is no roster, no timesheet,
no leave record and no payroll register. Wages are the one outflow that cannot wait for a slow
client, and nothing measured them. Qatar's labour parameters — minimum wage, overtime
multipliers, gratuity basis — are recorded nowhere and unverified.

**Outcome.** Every employee paid the right amount, through WPS, inside the statutory window,
on a build-up anyone can re-derive.

**Definition of Done.**
- A verified roster exists: wage, allowances, joining date, QID, contract dates, IBAN, for
  every person.
- Every monthly run passes the compliance sweep before it is prepared — minimum wage,
  deduction cap, negative net, WPS readiness — with every gate reported, including the clear ones.
- Zero wages paid late, zero below a statutory minimum, zero deductions without a written
  instruction.
- `agents/hr/LABOUR_LAW.md` confirmed, and the divisor conventions ruled in `DECISIONS.md`.

**Metric.** Runs paid correctly and on time, as a share of runs. **Baseline: not measured —
no payroll exists in this system.** Target 100%, from the first live run.

## G8 — Labour cost visible  *(owner: TIME, with PAYROLL and PRICE)*

**Problem.** `scripts/margin.py` charges labour at a flat **15% of direct cost** — QAR 6,517
on the documented Suresh example — and nobody has ever checked it against an hour actually
worked. Every margin figure this system produces rests on that assumption. Separately,
end-of-service gratuity accrues against no register: on the invented sample roster four people
carry QAR 13,803, and TNDK's real figure is unknown.

**Outcome.** Labour stops being an assumption. Hours are booked against jobs, priced at real
wage rates, and compared with what PRICE assumed. The gratuity liability is a monthly number.

**Definition of Done.**
- Every site day allocated to a project or explicitly to "workshop".
- A realised labour cost exists for at least one completed project, set against the 15% estimate.
- The register carries labour cost per job (feeds G3's margin column).
- Accrued gratuity liability reported every month and visible to LEDGER and TNDK-OPS.

**Metric.** Actual labour as a % of direct cost, against the assumed 15%.
**Baseline: unknown.** The first real measurement is the deliverable; the direction comes after.

> If the true figure is 20%, every margin in this system is overstated by roughly 5 points of
> direct cost — on the Suresh example, about QAR 2,170 a job. That is the same order as the
> margin gap G1 exists to close, and it is currently invisible.
