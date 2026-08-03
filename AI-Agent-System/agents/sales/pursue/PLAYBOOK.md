# PLAYBOOK — PURSUE

## Trigger

Any of:
- A quotation is sent. **Same day.** This is the only entry point that matters; everything else
  in this playbook depends on it.
- Sunday 09:00 — weekly pipeline cycle.
- A client responds to a quotation, in any way.
- Farhan asks "where did that quote for X get to?".
- An award, LPO or LOA arrives (outcome capture).

## Required inputs

From the `QUOTATION ISSUED → TNDK-SALES` handoff (`agents/sales/MANAGER.md`):

| Input | Required? | If missing |
|---|---|---|
| Quotation ref | **Yes** | Ask. Without it there is no row. |
| Client, and client type | **Yes** | Ask. Type drives the follow-up cadence. |
| Grand total | **Yes** | Take it from the issued quotation — never recompute it. |
| Date actually sent | **Yes** | Ask Farhan. The date on the document is not the date it went. |
| Tier and reason code | No | From PRICE. If absent, record `unrecorded` — never guess it. |
| Decision-maker name | No | Record `UNKNOWN` rather than assume. |
| Client's stated timeline | No | Record verbatim if given. |

**Do not re-ask for anything already in the conversation.** Extract it. Ask only for what is
genuinely absent and genuinely changes the record.

## Steps

### 1 — Enter the quotation on the day it is sent

Append to `02 - Registers/pipeline_register.xlsx`:

`quote ref · date sent · client · client type · project · value · tier · reason code · source ·
decision-maker · status · last contact · next action · next action date · decided date ·
outcome · loss reason · notes`

`status` is one of `open` · `won` · `lost` · `expired` · `withdrawn`. Nothing else.

A quotation entered a week late has already lost the only data this register exists to capture:
what the client did in the first week.

### 2 — Run the pipeline

```bash
python3 scripts/pipeline.py --data pipeline.json
python3 scripts/pipeline.py --data pipeline.json --awards examples/awards.json   # + concentration
python3 scripts/pipeline.py --data pipeline.json --json                          # machine-readable
```

Exit code `2` means one or more quotations require action — past validity, or quiet for 21 days.
Treat a non-zero exit as work to do, not as an error.

The script refuses to print a win rate from fewer than 20 tracked quotations, and refuses to
compute one from reconstructed history at all. **Do not work around either refusal by hand.**

### 3 — Follow the cadence

| Day | Action | Question being asked |
|---|---|---|
| 3 | Confirm receipt | "Did this reach you, and is anything missing from it?" |
| 10 | Before validity lapses | "Is there a decision expected before the 15th day?" |
| 16 | Validity lapsed | "Should we treat this as still live?" → route to PRICE if it is |
| 30 | Final direct ask | "Is this something you are still considering, or should we close it?" |
| 45 | No response | Recommend recording as **lost · NO_RESPONSE** |

Tender and JV clients run slower — a main contractor's approval chain is not the same as a
bakery owner's. Extend the cadence for `tender` and `JV` client types, and say in the register
that you did. Never extend it silently to keep a row looking alive.

**Validity extension is a pricing decision, not an administrative one.** A quotation re-offered
at the same price 40 days later is a price decision made by silence. Route it to PRICE.

### 4 — Draft the follow-up

Every draft: reference, one question, one easy action, nothing else.

```
DRAFT — NOT SENT
To:      [client contact]
Re:      Quotation [QUT/DCTS/NNN/YYYY] — [project]

[One line of context: what was quoted and when.]
[The question — asking for a decision, an approval step, or a date to expect one.]
[One easy action: a person to reply to, or a document to confirm.]

Farhan / Sales Engineer
```

**Check before handing it over — every sentence, every time:**

- No price, no discount, no percentage, no "we could look at…".
- No delivery date, no lead time, no "we can have it ready by…".
- No scope change offered to restart the conversation.
- Nothing that implies a decision has been made on TNDK's side that has not.

If a client's last message asked about price or delivery, the draft does **not** answer it. It
says the question has gone to Farhan. That is true, and it is the correct answer.

### 5 — Record the outcome, the day it is known

**Won:** requires a written award — LPO, LOA, or approved quotation. Record the award reference.
A verbal award is recorded as `open` with a note, not as `won`. Then hand off: the client leaves
this lane for LEDGER and COLLECT.

**Lost:** requires a reason code. Use the client's own words in `notes` alongside the code.

| Code | Meaning |
|---|---|
| `PRICE_LOWER` | A competitor was cheaper. Record their price only if the client stated it. |
| `PRICE_BUDGET` | Above the client's budget; no competitor mentioned. |
| `SPEC` | Competitor's technical offer preferred. |
| `LEAD_TIME` | TNDK's delivery timing lost it. |
| `RELATIONSHIP` | Incumbent supplier or prior relationship. |
| `NO_DECISION` | Project deferred, shelved or cancelled. Nobody won it. |
| `NO_RESPONSE` | Client never answered. Reason genuinely unknown. |
| `WITHDRAWN` | TNDK withdrew — capacity, credit, or scope. |
| `UNKNOWN` | Lost, reason not established. **A valid entry. Never dress it up.** |

`PRICE_LOWER` and `PRICE_BUDGET` are different findings and must not be merged. The first says
TNDK was beaten. The second says TNDK was quoting the wrong client. Only one of them is an
argument for lower prices.

### 6 — Report conversion

Weekly: the pipeline report in `agents/sales/MANAGER.md`.

Monthly, or whenever tracked decisions cross 20: the conversion report — win rate by count and
by value, average decision time, loss reasons ranked, and **win rate by margin tier**.

That last table is what this lane is for. State plainly what it does and does not yet show. If
the tiers have fewer than 5 decisions each, the honest sentence is "not yet answerable", not a
percentage with a caveat under it.

### 7 — Hand off

Return the output schema to TNDK-SALES. Won jobs go to TNDK-OPS with the award reference. Price
questions, delivery questions and technical questions go to TNDK-OPS routed to PRICE, PROCURE
and SCOPE respectively — with the client's words quoted, not summarised.

## Reconstructing the historic pipeline (week 1, once)

Read every quotation in `01 - Projects/` and `03 - Under process/`. For each, record ref, client,
date, value. Set `reconstructed: true`.

Then stop. Do **not**:
- infer a tier for a historic quotation (PRICE did not record one — `unrecorded` is the answer),
- infer a loss reason from the absence of an award,
- infer that a quotation with no award was lost. It may still be open, or may never have been
  sent.

Reconstructed rows are excluded from every rate the script computes, because the source recorded
only wins. Their purpose is to establish the **denominator** — how many quotations actually
exist — and nothing else.

## The denominator question

`QUT/DCTS/066/2026` does not necessarily mean 66 quotations. It may include revisions, may span
more than one year, and may share a series with DCTS-branded documents. **Establish what the
series counts before reporting any conversion figure.** One question to Farhan will settle it;
a conversion rate published on the wrong denominator will not be un-published.

Open loop: `memory/open_loops.md` OL-014.

## Definition of Done

- [ ] Every issued quotation is in the register, entered on the day it was sent.
- [ ] Every open row has a next action and a date.
- [ ] Every row past validity or quiet 21+ days has a drafted follow-up.
- [ ] Every decided row has an outcome; every lost row has a reason code.
- [ ] Won rows carry a written award reference.
- [ ] No draft contains a price, discount, margin or delivery date.
- [ ] Conversion figures state their denominator and whether it is verified.
- [ ] Reconstructed rows are flagged and excluded from every rate.
- [ ] Output marked **DRAFT — NOT SENT**.
