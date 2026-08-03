# GOALS

What this system exists to move. Every agent's Definition of Done ties back to one of these.

G1–G6 were set on 3 August 2026 with the delivery system. **G7 and G8 were added the same day**
with the sales division (`agents/sales/README.md`), and G4's ownership was corrected at the same
time.

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

## G4 — Concentration risk  *(measured by: TNDK-OPS · moved by: PROSPECT, ACCOUNT)*

**Problem.** Mesaieed (52.8%) + CCC/HIA (33.4%) = **86.2%** of the order book in two clients.
One is uncollected.

**Outcome.** The risk is visible and quantified every week rather than discovered late.

**Definition of Done.** Weekly brief states top-2 concentration %, cash-at-risk, and whether
committed vendor spend is exposed to an uncollected contract. Every open opportunity states what
winning it would do to the percentage, **before** it is won.

**Metric.** Top-2 concentration %. **Direction: down, via more mid-size work — not by losing the big ones.**

> **Ownership correction, 3 Aug 2026.** This was the only goal owned by a manager rather than a
> specialist, because no lane produced work. Reporting a number weekly does not move it. G8 gives
> the fix a specialist owner; TNDK-OPS keeps the measurement. Excluding the top two contracts, six
> awards total 104,600 — average 17,433. On the 758,100 book, +100,000 of mid-size work takes
> concentration from 86.2% to 76.2%. See `analysis/SALES_FINDINGS.md` F-S2.

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

## G7 — Quote conversion is measurable  *(owner: PURSUE)*

**Problem.** Quotation numbering has reached `QUT/DCTS/066/2026`. Eight awards are recorded.
**Nothing records a quotation that lost** — not the client, not the value, not the reason. So the
win rate is unknown, and the standing defence of a low price ("we needed it to win") cannot be
tested. G1 is currently an argument, not a measurement.

**Outcome.** Every quotation ends in a recorded win or a recorded loss with a reason, and the
relationship between margin tier and win rate becomes visible.

**Definition of Done.**
- Every issued quotation is in the pipeline register on the day it is sent.
- Zero open quotations with no next action dated within 7 days.
- Every decided quotation has an outcome; every loss has a reason code.
- Every quotation past its 15-day validity is flagged, and re-offers route to PRICE.
- The quotation-series denominator is verified, not assumed.

**Metric.** Win rate by count and by value, and **win rate by margin tier**.
**Baseline: unknown — that is the finding.** No percentage is published until 20 quotations have
been tracked from issue to decision. Reconstructed history is excluded: the old register recorded
only wins, so any rate drawn from it reads near 100% by construction.

**This is the goal that closes G1.** Twenty tracked quotations carrying both a tier and an outcome
answer whether discounting buys work.

## G8 — Demand that reduces concentration  *(owner: PROSPECT, with ACCOUNT)*

**Problem.** G4 wants concentration down via more mid-size work. Nothing produces mid-size work.
How every existing client was won is unrecorded, so the cheapest channel TNDK has — referral and
repeat from delivered clients — is invisible and unworked. No client has a named contact recorded.

**Outcome.** A standing supply of qualified mid-size opportunities, sourced first from clients
TNDK already has, at a volume the business can actually deliver.

**Definition of Done.**
- Source and named contact recorded for all 8 existing clients.
- Every delivered client has a live repeat opportunity or a recorded reason there is none.
- A target list and a current prequalification status for main contractors and consultants.
- Every opportunity states its concentration effect before it is pursued.

**Metric.** Number and value of mid-size opportunities (≈15,000–60,000) in the pipeline, and the
share of new enquiries arriving by referral or repeat.
**Baseline: QAR 0 tracked, source unrecorded on 8 of 8 clients.**

> **Gated.** PROSPECT stays at Stage 1 until Farhan states a delivery capacity ceiling
> (`DECISIONS.md` D-010). There are no ops staff. Generating more work than TNDK can deliver
> produces delay penalties and a damaged reputation in a small market — a worse outcome than a
> thin pipeline. See `analysis/SALES_FINDINGS.md` F-S6.
