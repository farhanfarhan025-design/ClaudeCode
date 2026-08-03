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
