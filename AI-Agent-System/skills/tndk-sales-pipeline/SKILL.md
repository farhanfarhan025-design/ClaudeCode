---
name: tndk-sales-pipeline
description: Track TNDK (The New Doha Kitchen Equipment Services W.L.L.) sales — every quotation from the day it is sent to the day it is won or lost, plus enquiry qualification, follow-up drafting, win/loss reasons, conversion rate and client concentration. Use this skill whenever the user says a quotation has been sent or asks what happened to one; asks to follow up, chase, or check on a client or a quote; says a job was won, lost, awarded, or that a client went quiet; asks about the pipeline, win rate, conversion, "how many quotes did we win", "should I follow up", or who owes a decision; reports a new enquiry, lead or referral; asks whether an enquiry is worth quoting; or mentions a QUT/DCTS reference outside of producing the document itself. Also trigger on "they want a discount", "we were too expensive", "we haven't heard back", and on any request for a weekly or monthly sales report. Sits between tndk-coldroom-quotation (makes the quotation) and tndk-accounts (bills the award).
---

# TNDK Sales Pipeline

This skill tracks the part of TNDK's business that nothing currently records: **what happens to a quotation after it is sent.**

**Where this sits:** `tndk-coldroom-quotation` produces the quotation → **this skill tracks it to a decision** → `tndk-accounts` bills the award. It also handles the step before a quotation exists: deciding whether an enquiry is worth quoting.

## Why this matters — read once, then it explains everything below

Quotation numbering has reached `QUT/DCTS/066/2026`. Eight awards are recorded anywhere in Farhan's system. **Nothing records a quotation that lost** — not the client, not the value, not the reason.

So the win rate is unknown. And the standing defence of a low price — "we needed it to win" — cannot be tested, because nobody wrote down whether the low prices won. The pricing guide's own worked example quotes at 14.6% against a 30% default. Whether that discount bought anything is currently unknowable.

Everything in this skill exists to make that answerable: log the quotation, chase the decision, record the outcome **with a reason**, and never publish a number the data doesn't support.

## The golden rules

**1. Never state a price, a discount or a delivery date to a client.** Not to close a deal, not to restart a stalled conversation, not because the client asked directly, and not on a verbal instruction in the moment. Price questions go to Farhan (or the quotation skill). Delivery questions go to Farhan (vendor lead times). This is the single most important rule here, and the reason is structural: the part of the business that wants the deal must not be the part that sets the number. A discount typed into a follow-up has skipped both the margin check and Farhan's approval.

When a client asks, the correct reply is that the question has gone to Farhan. That is true, and it is enough.

**2. Never send anything.** No email, WhatsApp or CRM is connected. This skill drafts; Farhan sends. "I have drafted the follow-up for you" is correct. "I have followed up" would be a fabrication.

**3. Never invent a loss reason.** `UNKNOWN` is a valid, useful entry. A plausible reconstruction is not. If a client simply stopped replying, the reason is `NO_RESPONSE` — not "price", however likely that feels.

**4. Never record a win without a written award.** LPO, LOA or approved quotation. A verbal go-ahead stays `open` with a note, because material gets ordered against wins.

**5. Never publish a win rate from thin or wins-only data.** Fewer than 20 tracked decisions is not a rate. History reconstructed from the award register is worse than thin — it recorded only wins, so any rate drawn from it reads near 100% by construction. Say "not yet answerable" and state what's missing. `scripts/pipeline.py` enforces both refusals; don't recompute around it by hand.

**6. Record the client's words, not a reading of them.** "They sounded keen" is not a pipeline entry. Quote what they said, with the date.

## The workflow

### When a quotation is sent — same day

Add a row to the pipeline register. This is the whole discipline: one entry per quotation, on the day it goes out. A quotation entered a week late has already lost the only thing worth capturing — what the client did in the first week.

Capture: quote ref · date **actually sent** (not the document date) · client · client type · project · value (from the issued quotation, never recomputed) · tier and reason code if PRICE recorded one · how the enquiry arrived.

Nothing currently records how enquiries arrive. Referral, tender, consultant spec, repeat, inbound — ask once, record permanently. It's the only way to learn which source is worth working.

### Follow-up cadence

| Day | Ask |
|---|---|
| 3 | "Did this reach you, and is anything missing from it?" |
| 10 | "Is a decision expected before the quotation's 15-day validity?" |
| 16 | Validity lapsed — "Should we treat this as still live?" |
| 30 | "Still considering, or should we close it?" |
| 45 | Recommend recording as lost · `NO_RESPONSE` |

Main contractors and JVs run slower than an owner-operator — extend the cadence for them, and say in the register that you did. Never extend it silently to keep a row looking alive.

**Re-offering a quotation after its validity has lapsed is a pricing decision, not an administrative one.** Rates move. Route it to Farhan rather than quietly honouring an old price.

### Drafting the follow-up

One question, one easy action, nothing else. Reference the quote number. Professional and warm — these clients are main contractors and JVs, and the relationship outlasts any single job.

Before handing a draft over, read it one sentence at a time and confirm there is no price, no percentage, no discount, no hint of flexibility, no delivery date, and no commitment Farhan hasn't made in writing. If the client's last message asked about price or delivery, the draft does **not** answer it.

Avoid "just checking in" — it contains no question, and it teaches clients that TNDK's follow-ups can be ignored. Avoid apologising for asking. Avoid manufactured urgency.

Worked examples, right and wrong, plus the full loss-reason list: `references/follow-ups.md`.

### When the outcome is known — same day

**Won** (with a written award): record the award reference, then hand off to `tndk-accounts` for invoicing.

**Lost**: record a reason code and the client's own words alongside it. `PRICE_LOWER` (a competitor was cheaper) and `PRICE_BUDGET` (above their budget, no competitor) are different findings and must not be merged — only one of them is an argument for lower prices.

### Weekly cycle

Run the pipeline, draft what's needed, report:

```bash
python3 scripts/pipeline.py --data pipeline.json --awards awards.json
```

Exit code 2 means quotations require action — past validity, or quiet for 21 days. That's work to do, not an error.

Report format: what moved (won/lost/quiet), what needs a decision from Farhan, the drafts ready to send, and the flagged items. If the pipeline didn't move, say so in four lines. A quiet week reported honestly is data; a quiet week padded is noise.

### Rebuilding the register spreadsheet

```bash
python3 scripts/build_pipeline_register.py --data pipeline.json --outdir ./out
```

Produces `pipeline_register.xlsx` in TNDK branding, with every figure computed in Python and written as a literal — the Approved Works Register broke because formula ranges didn't grow with the table, and this one is built not to. Convert to PDF the usual way if a copy is wanted:

```bash
python /mnt/skills/public/docx/scripts/office/soffice.py --headless --convert-to pdf FILE
```

## Two questions that block the numbers

Ask these once, then record the answers permanently:

1. **What does the `QUT/DCTS/NNN/YYYY` series count** — quotations only, or revisions too? Does it reset each year? Is it shared with DCTS-branded documents? Every conversion percentage depends on this denominator, and a rate published on a wrong one doesn't get un-published.

2. **What can TNDK actually deliver** — roughly how many rooms a month alongside the current book? There are no ops staff. Generating more work than the business can deliver produces delay penalties (the Mesaieed LOA carries them) and a damaged reputation in a small market. Until there's an answer, don't do outbound prospecting.

## Concentration — check before celebrating

Two clients are **86.2%** of the order book, and the larger one has collected nothing. So a big new job from an existing top-2 client makes that worse, not better.

Before a large opportunity is pursued, say what winning it would do to that percentage. Pass `--awards` to the pipeline script and it computes this per open quotation. It's not a reason to decline anything — it's Farhan's call, and more work from a good client is rarely wrong. It should just never be a surprise afterwards.

Excluding the top two, six awards total 104,600 — an average of **17,433**. Mid-size work is what moves concentration down.

## Beyond tracking quotations

Three adjacent jobs, each with its own reference file. Read the relevant one when the work comes up:

- **`references/qualify.md`** — a new enquiry arrives and it isn't obvious whether it's worth quoting. Need, authority, timeline, basis. Recommending a decline is allowed; declining is Farhan's.
- **`references/accounts-and-prospects.md`** — repeat work and referrals from delivered clients (the cheapest work TNDK can win), and target lists for clients it doesn't have yet.
- **`references/boundaries.md`** — what routes where, and the exact line between this skill, `tndk-accounts` (money owed), and maintenance/AMC work.

## Data files

- `references/register-schema.md` — the pipeline register columns and the JSON the scripts read.
- `assets/pipeline_example.json` — a worked example. Read its `_note` first: it mixes real awards with clearly-marked illustrative rows, and no illustrative figure may enter a report.
- `assets/awards_example.json` — the award book, for the concentration check.
