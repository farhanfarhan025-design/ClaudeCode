# FINDINGS — 3 August 2026

Evidence-based review of TNDK's commercial operation, from the artifacts available on this
platform: the three TNDK skills and their reference files, and the live Drive register.

**Scope limit, stated honestly:** no ChatGPT or Claude chat history was available. This
container was created fresh for this task. Everything below comes from files, not from
recalled conversation.

---

## F-01 — Quoting below the documented margin, without visibility

**Severity: highest. Largest quantified value at stake.**

The pricing guide sets **30% markup** as the "recommended default" for new clients. Its own
worked example (Mr. Suresh, April 2026) builds the cost as:

| | QAR |
|---|---|
| Direct materials | 43,448.45 |
| Labour & installation (15%) | 6,517.27 |
| Transport | 1,500.00 |
| **Total cost** | **51,465.72** |

The quoted price was **59,000** — a **14.6% markup**, or a **12.8% true gross margin**.
Less than half the stated default, and **below the 20% competitive-tender tier** that is the
lowest rung in the guide.

*Verified: `scripts/margin.py` reproduces the guide's cost build-up to the riyal.*

The price may have been correct — competition, price sensitivity, a reference site. **The
problem is that no reason was recorded, so today there is no way to know whether that 7,905
bought anything.**

**Value at stake:** ~**QAR 38,000** per 5 margin points across the current 758,100 book.

**Fix:** PRICE agent. Cost build-up and floor check on every quote; below-floor prices blocked
pending a logged override.

---

## F-02 — The live register is arithmetically broken

**Severity: high. Currently misinforming decisions.**

`approved_register.xlsx` (Drive, modified 31 July 2026):

| Defect | Shows | Should show |
|---|---|---|
| Balance column, all 8 rows | `0.00` | Contract − Received |
| Mesaieed balance | `0.00` | 400,000.00 |
| CCC balance | `0.00` | 177,450.00 |
| TOTAL — Contract | `18,250.00` | 758,100.00 |
| TOTAL — Received | `18,250.00` | 143,750.00 |
| Total Approved Value | `0.00` | 758,100.00 |
| Total Received to Date | `0.00` | 143,750.00 |
| Total Outstanding Balance | `0.00` | 614,350.00 |

`18,250` is the sum of rows 1–3 only (17,000 + 800 + 450) — a formula range that never grew
with the table.

The file does not look broken. Every figure is plausible. That is what makes it dangerous:
the summary block reads zero outstanding on a business owed over six hundred thousand riyals.

**Fix:** LEDGER rebuilds with computed values and a monthly integrity audit.

---

## F-03 — Severe client concentration, on the uncollected side

**Severity: high. Structural.**

| Client | Contract | % of book | Collected |
|---|---|---|---|
| HBK-BWTC-BEIL JV (Mesaieed) | 400,000 | 52.8% | **0** |
| Consolidated Contractors (HIA) | 253,500 | 33.4% | 76,050 |
| **Top 2 combined** | **653,500** | **86.2%** | 76,050 |

The largest contract in the book has collected nothing and has been blocked on an advance bank
guarantee since the LOA date of **21 May 2026** — over ten weeks.

Each contract individually reads as good news, which is exactly why the concentration is easy
to miss. Nothing in the current system reports it.

**Fix:** TNDK-OPS weekly concentration watch; COLLECT standing item on the guarantee;
ANNUITY building a recurring base underneath the lumpy project revenue.

---

## F-04 — Three sources disagree on the same client

**Severity: medium. Blocks correct invoicing.**

Samoosa Shop:

| Source | Contract | Received |
|---|---|---|
| Live register (Drive) | 38,500 | 20,000 |
| Skill sample data | 39,375 | 31,500 |
| Receipt log | — | 20,000 (RCT-256 only) |

The 875 is the chequered-sheet variation. The 11,500 receipt difference has **no receipt number
behind it** — three invoices exist (INV-256/257/258), one receipt.

**Fix:** `DECISIONS.md` D-006 blocks Samoosa documents until resolved. D-001 makes Drive the
single source so copies stop being made.

---

## F-05 — The register tracks revenue, never profit

**Severity: medium. Compounds F-01.**

The Approved Works Register records contract value, received and balance. There is **no cost
column and no margin column.** The project workbook has an Expenses tab, but nothing rolls up.

So even after F-01 is fixed at the quoting stage, there is still no way to see *realised*
margin after a job completes — whether the 30% quoted survived contact with the site.

**Fix:** margin column in the register; `margin_log.xlsx` capturing quoted vs cost vs outcome.

---

## F-06 — "Amounts to Receive" mixes two different quantities

**Severity: medium. Makes the receivables figure unusable for cash planning.**

For CCC it shows the full remaining 70% (177,450). For Mesaieed it shows only the 15% advance
(60,000), omitting the other 340,000. One row means "everything still owed", the next means
"the next milestone". They are summed together.

**Fix:** split into two explicit columns — *next milestone due* and *total remaining* — so the
two are never added together again.

---

## F-07 — Rules contradict across documents

**Severity: medium. Client-visible.**

Invoices must **never** contain the word "tax" — an absolute standing instruction, enforced by
a script that throws. Quotations state the grand total is *"excluding 5% VAT"*.

A client can hold a quotation and an invoice side by side. There is also no VAT regime in
Qatar reflected anywhere else in the system, which makes the quotation line questionable
independently of the contradiction.

**Fix:** `DECISIONS.md` D-005 — needs Farhan's ruling. Option A (remove the line) recommended.

---

## F-08 — The business starts at "quotation" and ends at "paid"

**Severity: medium upstream, high downstream. The biggest missed opportunity.**

**Upstream:** no enquiry capture, no pipeline, no quote-to-award conversion data. Quotations
run to QUT/DCTS/066/2026 but only *won* jobs are recorded anywhere. **Win rate is unknown** —
which means the effect of F-01's low pricing on actually winning work cannot be assessed. It is
entirely possible the discounting is not even buying the jobs.

**Downstream:** AMC appears **exactly once** in the entire system — a note on the Mesaieed LOA.
TNDK is installing cold rooms at Hamad International Airport and a Ministry-adjacent landfill,
and capturing **zero** recurring maintenance revenue systematically. The reactive maintenance
jobs (Al Noor 800, BSI 450, Ruwais 1,850) prove the demand exists; they are inbound calls, not
a business line.

**Current AMC contracted value: QAR 0.**

**Fix:** ANNUITY owns warranty tracking and AMC conversion. PRICE begins logging outcomes so
win rate becomes knowable.

---

## F-09 — Automation made the bottleneck faster, not smaller

**Severity: strategic. The ceiling on the business.**

The three TNDK skills are good engineering — templates, JSON schemas, generators, QA greps,
reference docs. They meaningfully cut the time to produce each document.

But every one still begins with Farhan deciding to run it and ends with Farhan checking it.
Sales, scoping, pricing, procurement, invoicing, collections and filing all route through one
person. Ronaldo signs invoices; Farhan generates them.

**The constraint was never document production.** It is that one person holds every trigger,
every decision and every follow-up.

**Fix:** the architecture assigns *triggers* (`HEARTBEAT.md`) and *ownership* (per-agent
Definitions of Done), not just execution. `GOALS.md` G6 measures owner-touches per job.

---

## What is working — do not break these

- **Externalised process.** The numbering log, conventions file and JSON schemas are most of an
  operations manual. Most owners keep this in their head and then cannot hire.
- **Verification built into workflow.** `pdftotext | grep -i tax` before delivery — the check
  lives in the process, not in memory. That instinct is what makes staged delegation safe here.
- **Rule-first thinking.** "LPO terms govern." "Renumber the newer document." Clear invariants,
  consistently applied. This is exactly the temperament the agent framework rewards.
- **Commercial credibility ahead of the systems.** Winning CCC at HIA and a Ministry-adjacent
  JV subcontract in one quarter is not luck.

---

## Priority order

| # | Finding | Action | Value |
|---|---|---|---|
| 1 | F-01 | Deploy PRICE | ~38,000 per 5 pts |
| 2 | F-02 | Rebuild the register | Decision integrity |
| 3 | F-03 | Weekly concentration watch + guarantee chase | 400,000 at risk |
| 4 | F-04 | Resolve Samoosa | Blocks invoicing |
| 5 | F-08 | Start AMC pipeline | New revenue line |
| 6 | F-05/06 | Margin + receivables columns | Visibility |
| 7 | F-07 | Rule on VAT wording | Client-facing consistency |
| 8 | F-09 | Shift to triggers and ownership | The actual ceiling |
