# SALES DIVISION

Built 3 August 2026, on top of the commercial system built the same day.

The existing six lanes start when an enquiry arrives and stop when the money lands. **Nothing
owns the part before the enquiry, and nothing owns the quotation after it is sent.** This
division owns both ends.

---

## Why this exists

`analysis/SALES_FINDINGS.md` is the evidence. The short version:

**1 — The win rate is unknown.** Quotation numbering has reached `QUT/DCTS/066/2026`. Eight
awards are recorded anywhere in the system. Nothing records a quotation that lost, or why.

That gap is not just a sales problem. It makes **G1 unfalsifiable**. PRICE exists because a job
was quoted at 14.6% against a 30% policy, and the defence of a low price is always "we needed it
to win." Nobody can test that sentence, because no one recorded whether the low prices won.
`memory/open_loops.md` OL-012 says exactly this and assigns it to PRICE — but PRICE sees a
quotation at the moment it is priced and never again.

**2 — The concentration fix has no owner.** G4 targets top-2 concentration down *"via more
mid-size work — not by losing the big ones."* TNDK-OPS reports the percentage every week.
Reporting a number is not the same as moving it. No agent is tasked with producing the
mid-size work that is supposed to move it.

**3 — Repeat revenue is left on the table.** Every award in the book came from somewhere, and
in this market that somewhere is usually a person. CCC at Hamad International Airport and a
Ministry-adjacent JV in one quarter is a credibility asset that is being used exactly once each.

**Scale.** Excluding the top two contracts, six awards total 104,600 — an average of **17,433**.
Jollibee alone was 46,000. One additional mid-size win per quarter is 17,000–46,000 of revenue
that costs nothing in fixed overhead, and it moves concentration down without touching the
big contracts.

## Architecture

```
FARHAN (owner — goals, risk, pricing authority, all approvals)
│
├── TNDK-OPS (manager)   — delivery: scope → price → procure → invoice → collect → AMC
│
└── TNDK-SALES (manager) — demand: find → qualify → pursue → keep
    │
    ├── PROSPECT   market → target list → approach            Stage 1
    ├── QUALIFY    enquiry → qualified or declined            Stage 2
    ├── PURSUE     quotation → decision → win/loss record     Stage 2  ★ built
    └── ACCOUNT    delivered job → repeat work → referral     Stage 1
```

The two managers are peers. Neither reports to the other; both report to Farhan.
The handoff between them is a **qualified enquiry** going in (QUALIFY → TNDK-OPS → SCOPE) and a
**sent quotation** coming back (PRICE → TNDK-OPS → PURSUE).

## The boundary that makes this safe

> **No sales agent touches a price, a discount, or a delivery date. Ever. At any trust stage.**

This is the same structural separation that already exists between SCOPE and PRICE, applied to
the lane that has the strongest reason to break it. `README.md` states the principle: *the
person who wants the job does not set the number alone.* A sales function is, by definition,
the part of the business that wants the job.

So the sales lanes may say **what a client needs, what they are worth, when they decide, and
who they are talking to instead**. They may not say **what it costs, what discount is available,
or when it will be delivered**. Those three sentences are PRICE's, PRICE's, and PROCURE's.

Written as `RULES.md` A9 and D-008. It is not a trust stage and it does not get promoted.

## What each lane owns

| Lane | Owns | Never |
|---|---|---|
| **PROSPECT** | Target list, market segments, prequalification status, approach drafts | Any price. Any promise. Contacting anyone. |
| **QUALIFY** | Enquiry triage, budget/authority/timeline/competition, decline recommendations | Scoping the job technically. Quoting it. |
| **PURSUE** | Pipeline register, follow-up cadence, win/loss record, conversion data | Discounting to close. Re-quoting. Committing dates. |
| **ACCOUNT** | Client history, repeat opportunities, referrals, satisfaction after handover | Servicing (ANNUITY). Chasing money (COLLECT). |

## Where the boundaries sit with the existing lanes

| Looks like | Actually belongs to | Because |
|---|---|---|
| "What should we charge to win this?" | **PRICE** | Sales never sets a number. A9. |
| "Can we do it by the 20th?" | **PROCURE** (lead times) → Farhan | Delay penalties are contractual. Mesaieed has them. |
| "Client hasn't paid the second milestone" | **COLLECT** | PURSUE chases *decisions*, COLLECT chases *money*. |
| "Their warranty expires in 60 days" | **ANNUITY** | ACCOUNT finds new work; ANNUITY renews service. |
| "How big does the room need to be?" | **SCOPE** | QUALIFY establishes there is a job, not what it is. |
| "This tender needs a prequalification pack" | **PROSPECT** | Getting on the list is upstream of any enquiry. |

ACCOUNT and ANNUITY are the closest pair and the easiest to blur. The test: **ANNUITY sells the
maintenance of what is already installed. ACCOUNT sells the next installation.** A client who
needs both gets two assignments, sequenced — never one agent doing both.

## Why PURSUE is built first

Same reasoning that picked PRICE: largest measurable value, and it unblocks something else.

- It is the only lane that produces a **number the business does not currently have**. Conversion
  rate, average decision time, loss reasons, and win rate *by margin tier*.
- That last one closes the loop on G1. Once 20 quotes carry both a realised margin and a
  win/loss outcome, the question "does discounting actually win work here?" becomes answerable.
  Until then PRICE is enforcing a floor without evidence that the floor costs anything.
- It needs no new market knowledge, no capacity decision, and no outbound contact. It works on
  quotations that have already been issued.

PROSPECT is deliberately **not** first. Generating demand into a business with no ops staff and
one person on the critical path is how a good quarter becomes a delivery failure. PROSPECT stays
at Stage 1 until Farhan states a capacity ceiling — `DECISIONS.md` D-010.

## Files

```
agents/sales/
├── README.md              this file
├── MANAGER.md             TNDK-SALES: routing, review gate, pipeline report
├── pursue/                ★ full build
│   ├── SOUL.md · IDENTITY.md · PLAYBOOK.md · EXAMPLES.md
│   └── QA_CHECKLIST.md · OUTPUT_SCHEMA.md · SYSTEM_PROMPT.md · TESTS.md
├── prospect/IDENTITY.md
├── qualify/IDENTITY.md
└── account/IDENTITY.md
```

Supporting: `scripts/pipeline.py` · `analysis/SALES_FINDINGS.md` ·
`GOALS.md` G7–G8 · `RULES.md` A9 · `DECISIONS.md` D-007 to D-010.

## Deployment sequence

**Week 1 — reconstruct the history.** PURSUE reads every issued quotation in
`03 - Under process/` and `01 - Projects/` and builds the pipeline register: quote ref, client,
date, value, outcome, and — where it can be established — why. This is archaeology, not
forecasting. Expect gaps; record them as gaps.

**Week 2 — the denominator.** Establish what `QUT/DCTS/066/2026` actually counts: quotations,
revisions, or both, and over what period. The conversion rate is meaningless until this is
known. One question to Farhan will probably settle it.

**Weeks 2–6 — PURSUE live, Stage 2.** Every quotation issued from now on enters the register on
the day it is sent, with a follow-up date. Weekly pipeline cycle starts.

**Week 6 — QUALIFY.** Once there is a pipeline to protect, start filtering what enters it.

**Week 8 — the first conversion report.** Conversion rate, average decision time, and win rate
by margin tier. This is the report that tells Farhan whether his pricing instinct is right.

**Week 10+ — ACCOUNT, then PROSPECT.** ACCOUNT works clients TNDK already has, so it needs no
capacity ruling. PROSPECT waits for D-010.

Nothing gets promoted on a good demo. Promotion gates: `pursue/TESTS.md`.

## Trust model

Same four stages as the rest of the system, and the same hard stop.

| Lane | Stage | Reason |
|---|---|---|
| PURSUE | 2 — Draft | Drafts every follow-up; Farhan sends. |
| QUALIFY | 2 — Draft | A decline recommendation is a recommendation, never a decline. |
| ACCOUNT | 1 — Observe | Builds client history first. Nothing client-facing until it is complete. |
| PROSPECT | 1 — Observe | Blocked on the capacity ruling, D-010. |

**Sending never gets promoted** — `RULES.md` A2. There is no email, no WhatsApp and no CRM
connected (`TOOLS.md`). Every follow-up, approach and proposal this division produces is text
for Farhan to send himself. An agent that reports having "followed up" has fabricated an action.
