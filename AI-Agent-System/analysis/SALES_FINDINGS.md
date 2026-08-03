# SALES FINDINGS — 3 August 2026

Companion to `analysis/FINDINGS.md`, which reviewed the delivery side. This one reviews the
demand side: everything before an enquiry becomes a job, and everything after a quotation is sent.

**Same scope limit, stated honestly:** these come from files — the three TNDK skills, their
reference data, the live Drive register, and the agent system built the same day. No chat history
was available. Where a figure is inferred rather than read, it says so.

`analysis/FINDINGS.md` F-08 identified this gap in one paragraph and assigned the downstream half
to ANNUITY. This document works the upstream half.

---

## F-S1 — The business has no record of anything it did not win

**Severity: highest. It makes an existing goal unfalsifiable.**

Quotation numbering has reached `QUT/DCTS/066/2026` (source: the Samoosa quotation reference in
`memory/durable_facts.md`). Eight awards are recorded anywhere in the system.

Nothing records a quotation that lost. Not the client, not the value, not the reason, not the
competitor. The Approved Works Register is exactly what its name says — a register of approvals.

Three consequences, in increasing order of cost:

1. **Win rate is unknown.** So is average decision time, and so is the value of the open pipeline.
2. **Effort allocation is blind.** Nobody knows which enquiry sources produce work.
3. **`GOALS.md` G1 cannot be tested.** This is the expensive one.

G1 exists because a job was quoted at **14.6% against a 30% policy** (F-01). The standing defence
of a low price is always "we needed it to win." That sentence is currently unfalsifiable, because
nobody recorded whether the low prices won. PRICE is enforcing a floor with no evidence about
what the floor costs — and equally, no evidence that discounting buys anything.

Twenty quotations carrying both a margin tier and an outcome settle it either way.

**A caution on the denominator.** `066` does not necessarily mean 66 quotations: the series may
include revisions, may span more than one year, and may be shared with DCTS-branded documents.
**No conversion percentage should be published until that is established.** A rate on a wrong
denominator, once quoted in a meeting, does not get un-quoted.

**Fix:** PURSUE, with `scripts/pipeline.py`. Register every quotation on the day it is sent;
record every outcome with a reason; suppress every rate until the data supports one.

---

## F-S2 — The concentration goal is measured but not owned

**Severity: high. Structural, and already visible in the original findings.**

`GOALS.md` G4 sets top-2 concentration as a metric with the direction *"down, via more mid-size
work — not by losing the big ones."* Its owner is listed as **TNDK-OPS, the manager**.

Every other goal in the system has a specialist owner. G4 does not, because when the system was
built there was no lane whose job is to produce work. The manager reports 86.2% every Monday. A
weekly number with no agent tasked to move it is a dashboard, not a goal.

**The arithmetic of the fix.** Excluding the top two contracts, six awards total **104,600** — an
average of **17,433**. Jollibee alone was 46,000.

| Added mid-size work | Top-2 concentration |
|---|---|
| none (today) | 86.2% |
| +50,000 | 80.9% |
| +100,000 | 76.2% |
| +200,000 | 68.2% |

*(Computed on the 758,100 book: 653,500 top-2 over 758,100 + added work. Assumes the added work
is spread across clients outside the top two.)*

Two or three mid-size wins move this materially, with no cash exposure of the kind Mesaieed
carries and no loss of the relationships that produced the big contracts.

**Fix:** PROSPECT owns generating that work; ACCOUNT owns the cheaper half of it — repeat and
referral from clients TNDK already has. G4 gains a specialist owner alongside the manager's
weekly watch.

---

## F-S3 — Every enquiry costs a full quotation cycle from the one resource that is scarce

**Severity: medium-high. It is F-09 wearing different clothes.**

There is no step between "someone asked" and "we are quoting". A site visit, a heat load, a cost
build-up and a PRICE cycle are spent identically on a 2,000 riyal enquiry and a 400,000 tender.

`USER.md` names the constraint precisely: *"Farhan is the bottleneck. Any system that adds review
burden without removing execution burden is a net loss."* Unqualified enquiries are execution
burden that produces nothing, and nothing currently filters them.

Four questions — need, authority, timeline, basis — remove most of it, and cost one message.

**Fix:** QUALIFY, sitting between the enquiry and SCOPE. It recommends; Farhan declines.

---

## F-S4 — How every existing client was won is unrecorded

**Severity: medium. It hides the cheapest channel TNDK has.**

Eight awards. For none of them does any file record how the client arrived — referral, tender,
consultant specification, prior relationship, or inbound call.

The reactive maintenance jobs (Al Noor 800, BSI 450, Ruwais Farm 1,850) are almost certainly
word-of-mouth, and `analysis/FINDINGS.md` already observes that they are *"inbound calls, not a
business line."* The same is likely true of the acquisition channel as a whole: it works, and it
is invisible, so it cannot be worked deliberately.

Nor is there a named contact recorded at any client. The system records two people at TNDK
(Farhan, Ronaldo) and not one on the other side of any of the eight contracts.

**Fix:** ACCOUNT records source and contact for every existing client — one conversation with
Farhan establishes most of it — then works repeat and referral. PURSUE records source on every
new enquiry from now on.

---

## F-S5 — Quotation validity lapses silently, which is a pricing decision made by default

**Severity: medium. Client-facing, and it costs margin.**

Standard quotation validity is **15 days** (`memory/preferences.md`, Commercial). Nothing tracks
it. A client who returns on day 50 and says "we'll take it" is accepting a price built on a rate
card of unknown age (OL-009), against vendor costs that may have moved.

Honouring an old price is often the right commercial call. Doing it without noticing is not a
call at all — it is F-01 happening again by a different route.

**Fix:** PURSUE flags every quotation past validity. Re-offering at the same price after validity
routes to PRICE, as a pricing decision. `scripts/pipeline.py` flags it at day 16 and exits
non-zero.

---

## F-S6 — Building a sales function into fixed delivery capacity is itself a risk

**Severity: strategic. Stated here so it is not discovered later.**

This is the finding that argues against part of this build, and it belongs in the record.

`USER.md`: no ops staff, no one to delegate to, Ronaldo on accounts only, Farhan on the critical
path for everything. Into that, a demand-generation agent is capable of producing more work than
the business can deliver — and the downside is not a missed opportunity, it is a delay penalty
(Mesaieed's LOA carries them), a damaged main-contractor relationship, and a reputation in a
small market.

**Therefore, deliberately:**

- PURSUE is built first. It works quotations that have **already been issued** — zero new demand.
- QUALIFY comes second. It **reduces** load by filtering what enters the quoting process.
- ACCOUNT is third. Repeat work from existing clients, at a pace Farhan sets.
- **PROSPECT is last and stays at Stage 1** until Farhan states a capacity ceiling — `DECISIONS.md`
  D-010.

The sales division is sequenced to improve conversion and reduce waste before it generates a
single additional enquiry.

---

## Priority order

| # | Finding | Action | Value |
|---|---|---|---|
| 1 | F-S1 | Deploy PURSUE; register every quotation, capture every outcome | Makes G1 answerable |
| 2 | F-S5 | Flag validity lapses; route re-offers to PRICE | Protects margin already earned |
| 3 | F-S3 | Deploy QUALIFY | Removes wasted quoting cycles |
| 4 | F-S4 | ACCOUNT records source and contact for all 8 clients | Reveals the cheapest channel |
| 5 | F-S2 | PROSPECT owns G4 | ~17,400 per mid-size win; concentration down |
| 6 | F-S6 | Get the capacity ceiling ruled on | Prevents the whole division doing harm |

## What is working — do not break these

- **The credibility is real.** CCC at Hamad International Airport and a Ministry-adjacent JV
  subcontract in one quarter is not luck, and it is the strongest asset the sales division has.
  Every approach PROSPECT drafts should reference actual delivered work.
- **The market is small.** Everyone knows everyone. That makes referral cheap and reputation
  expensive — which is the argument both for ACCOUNT and against mass outreach.
- **Farhan signs as "Sales Engineer".** He is the sales function and he is good at it. This
  division exists to remove the record-keeping and the follow-up discipline from him, not the
  selling.
