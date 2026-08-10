# THE WEALTH MACHINE

How this specific business — cold rooms in Qatar, one owner, no ops staff — actually
turns into money for Farhan. Not a motivational plan. A machine with five parts, in
the order they should be built.

All baseline figures are from the **13 July 2026** register snapshot as recorded in
`AI-Agent-System/memory/durable_facts.md`, verified 3 August 2026. Re-check the "as of"
date before quoting any of them back to him.

---

## The gap being closed

Two contractors, same city, same trade, same revenue.

**The first** wins 750,000 of work a year at 15% margin, collects most of it
eventually, does every quotation himself, sells installations, and has two clients.
He earns a good income and is worth roughly what is in his bank account.

**The second** wins the same 750,000 at 25%, collects on time, has a 150,000
maintenance book on top, has a technician and a coordinator, and eight clients where
none is over 25%. He earns considerably more, works fewer hours, and owns something a
buyer will pay a **multiple of profit** for.

Same market. Same skill. The difference is entirely in five mechanisms, none of which
require a bigger market or outside capital.

---

## Engine 1 — Margin *(the fastest money in the business)*

**Where it stands.** Documented policy 30%. The pricing guide's own worked example
delivers **14.6%**. Nothing computed realised margin at the moment of quoting, so the
gap was invisible for as long as it existed.

**What it is worth.** Across a 758,100 book, **five margin points ≈ QAR 38,000**.
Closing 14.6% → 25% is roughly **QAR 79,000 a year** — with no new clients, no new
staff and no extra hours. There is nothing else in this business that pays that fast.

**How it gets built:**
1. Realised margin computed on **every** quote before it goes out — `scripts/margin.py`
   already does this.
2. A hard floor with a logged override, not a preference. *(22% proposed, D-004,
   awaiting his ruling — get the ruling.)*
3. Vendor rates re-verified and dated. The rate card's last verification date is
   currently **unknown** (OL-009).
4. Risk loading made explicit: new client, penalty clause, tight programme,
   unverified rate.
5. Every quote and its **outcome** logged, so the discount conversation stops being
   guesswork (OL-012).

**The number he should watch:** weighted realised margin across the trailing ten
quotes. Target ≥25% on new clients.

---

## Engine 2 — Collection speed

**Where it stands.** 758,100 booked · 143,750 collected · **614,350 outstanding**.
The single largest contract, 400,000, has collected zero since 21 May 2026, blocked
behind an advance bank guarantee and a performance cheque.

**Why it matters more than it looks.** Cash velocity is a multiplier on everything
else. The same capital collected twice as fast does twice the work. And reserves are
what let him refuse a bad job — which is where margin comes from. **Collection speed
buys pricing power.** They are not separate problems.

**How it gets built:**
1. Invoice the day the milestone triggers. Any passed milestone with no invoice is a
   self-inflicted wound.
2. A written escalation ladder, executed on dates, not on mood (playbook 11).
3. Payment triggers TNDK can prove without the client's cooperation.
4. The bank guarantee treated as a standing weekly item with a dated action until it
   clears — it is 53% of the book sitting behind one piece of paper.
5. Advance in before materials out. Always.

**The number he should watch:** days-sales-outstanding, and the percentage of the book
with a next action dated inside 7 days.

---

## Engine 3 — The annuity *(the highest-value thing he is not doing)*

**Where it stands.** AMC contracted value: **QAR 0**. No completed project has a
recorded warranty end date (OL-010). AMC appears exactly once in the entire system — a
clause on one LOA.

**Why this is the biggest one long-term.** Every room he has ever installed is a
machine that needs servicing by someone. That someone should be him — he installed it,
he knows it, he is already trusted, and there is no tender. Maintenance revenue is
higher margin than installation, arrives without a bid, and **starts each year already
banked** while project revenue resets to zero every January.

And when he eventually sells: a buyer pays a modest multiple for a project pipeline
and a much higher one for a maintenance book, because one is hope and the other is
contracted.

**How it gets built:**
1. A list of every room installed, with client, date and warranty end date. This is
   an afternoon's work and it does not exist yet.
2. A standard AMC scope and price — two tiers is enough.
3. A proposal drafted 60 days before each warranty expiry, while he is still the man
   who knows the equipment.
4. An AMC register with expected annual value, tracked like the order book.

**The number he should watch:** contracted AMC annual value. Baseline zero — every
riyal is progress.

---

## Engine 4 — Client base and concentration

**Where it stands.** Top two clients = **86.2%** of the book (Mesaieed 52.8% + CCC
33.4%). The larger has paid nothing.

**The risk, stated plainly.** One client's decision — a delay, a dispute, a change of
project manager — can now end the company, because vendor commitments get made against
contracts like these.

**The fix is more revenue, not less.** Never solve concentration by shrinking. Solve
it with a steady flow of mid-size work — bakeries, restaurants, small food businesses
— which also happens to be the highest-margin, fastest-paying, least-tendered work in
the market. The big contracts are prestige and volume; the small ones are cash and
margin. A healthy book has both.

**How it gets built:**
1. Every completed job asked for a referral, on the day it is commissioned, while the
   client is happy. This is the cheapest lead source that exists and it costs nothing.
2. The installed base contacted once a year for service — which is Engine 3 doing
   double duty.
3. Two named target segments and a monthly hour spent on them, deliberately.

**The number he should watch:** top-2 concentration %. Direction: down, via growth.

---

## Engine 5 — Capacity without Farhan

**Where it stands.** Sales, quoting, procurement, invoicing, collections and filing
all begin and end with one person. The existing skills made that person faster; they
did not make him removable (`lessons.md` L-004).

**Why it is the ceiling.** Engines 1–4 all consume his attention. Without this one,
every improvement elsewhere is capped by the same 14 hours.

**How it gets built, in order:**
1. **Write the process down** before hiring anyone. Undocumented delegation is just
   interruption with extra steps.
2. **Coordinator first** — documents, filing, follow-ups, numbering. Cheapest hours,
   biggest reclaim.
3. **Technician second** — delivery without him on site.
4. **Keep forever:** pricing, client relationships, vendor negotiation.

**The number he should watch:** owner-touches per completed job. Direction: down.
**The real test:** two weeks out of Doha, and quotations still go out and money still
arrives.

---

## The order of building

Do not run them in parallel. The sequence is chosen so each one funds the next.

| Horizon | Focus | Why now |
|---|---|---|
| **0–90 days** | Engines 1 and 2 — margin and collection | Fastest money, no cost, no hiring. Fixes the leak before scaling the flow. Get the four blocking rulings made (D-004, D-005, D-006, register rebuild). |
| **3–12 months** | Engines 3 and 5 — annuity and first hire | Funded by the cash the first two release. Warranty register, first AMC proposals, coordinator hired against reclaimed hours. |
| **1–3 years** | Engines 4 and 5 — client base and a team | Concentration comes down through growth; the business starts running without him. |

**Scaling a leaking business makes the leak bigger.** That is the whole reason margin
and collection come first.

---

## The personal side

The company is not the wealth. What leaves the company is.

**Pay himself on a date, as a cost line** — not whatever survives the month (L10).

**Four accounts**, mechanically separated:

| Account | Rule |
|---|---|
| Operating | receipts land here; day-to-day only |
| Reserve | 3–6 months fixed cost; touched only for survival, never for opportunity |
| Obligation | retentions, guarantees, statutory; funded on receipt, never borrowed from |
| Owner | transferred on a fixed date every month |

**Then, in order:** reserve to target → buy back time → fund the annuity → owner's
account → equipment on the utilisation test → growth spending. Playbook 17.

**And know the exit number.** A refrigeration contracting business sells on a multiple
of sustainable profit, discounted heavily if it depends on the owner and marked up for
recurring revenue. Which means the same three things that make him money now — margin,
annuity, and a business that runs without him — are also the three things that make it
sellable. He does not have to choose between running it well and building an asset.
They are the same work.

---

## The scoreboard — seven numbers, weekly

If he only ever looks at one page, this is the page.

| # | Number | Baseline (13 Jul 2026) | Direction |
|---|---|---|---|
| 1 | **Cash collected this week** | — | up |
| 2 | **Cash in hand** | — | up, then held at reserve target |
| 3 | **Outstanding, and how much is blocked** | 614,350 · 400,000 blocked | down |
| 4 | **Realised margin, trailing 10 quotes** | 14.6% *(single observed case)* | ≥25% |
| 5 | **Top-2 client concentration** | 86.2% | down, via growth |
| 6 | **Committed vendor spend against uncollected contracts** | — | at or near zero |
| 7 | **AMC contracted annual value** | 0 | up |

Numbers 1 and 3 tell him whether he survives. Number 4 tells him whether he prospers.
Numbers 5, 6 and 7 tell him whether he is building something or just working.

Anything not on this list can wait until Tuesday.
