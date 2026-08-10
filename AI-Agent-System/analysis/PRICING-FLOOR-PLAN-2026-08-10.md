# PRICING FLOOR — WORKING PLAN

**Week of Monday 10 August 2026.** Owner: Farhan. Prepared by RAIS.

The decision Farhan asked to have built out. One week, one outcome: **the price of a
TNDK job stops being set by feel.**

---

## What changed the plan

The back-test of 6 August (`analysis/BACKTEST-2026-08-06.md`) re-priced three real
quotations. The finding is not the one everybody expected.

| Quote | Date | Computed cost | Quoted | Markup |
|---|---|---|---|---|
| Samoosa `066/2026` | 13 Jul | 26,282.90 | 38,500 | **+46.5%** |
| Suresh *(guide example)* | Apr | 51,465.72 | 59,000 | **+14.6%** |
| Mecca Trading `174/2026` | 3 Aug | 46,131.04 | 46,000 | **−0.3%** |

**Weighted realised markup: 15.8%.** But the average is the least interesting number
on the page. **47 percentage points separate the best quote from the worst** — same
person, same rate card, three weeks apart.

That is not a floor set slightly too low. That is the absence of a pricing method.

**A floor alone would not fix this.** A floor catches the bottom; it does nothing
about a 47-point spread. What fixes it is a method — compute the cost, then apply a
markup — with the floor as the last line of defence rather than the whole policy.

### And the leak has a specific shape

Cost in this business is driven by **equipment count, not room size.**

| | Samoosa | Mecca |
|---|---|---|
| Rooms | 1 | 2 |
| Panel area | 60.09 sqm | **57.04 sqm** — less |
| Total cost | 26,283 | **46,131** — 75% more |
| Quoted | 38,500 | 46,000 — only 19.5% more |

Mecca has less panel than Samoosa and costs 75% more, because a second room means a
second condensing unit, a second evaporator, a second control panel, a second pipe run
and a second wiring run. **Panel area is the visible part of the job and the smallest
part of the bill.** `margin.py` now reports this directly — on Mecca, equipment is
**68.8%** of direct cost.

**Small two-room jobs are the worst case, and they are exactly the jobs that feel
routine enough to price from memory.**

---

## The prerequisite nobody can skip

**The rate card has no verification date** (`open_loops.md` OL-009). So one of two
things is true, and from here it is impossible to say which:

- The rate card is right → **Mecca `174/2026` was quoted at a loss of 131**, and needs
  revising now.
- The rate card is wrong → **every number in the back-test is wrong**, and the rate
  card is the emergency, not the floor.

**A floor computed on unverified costs is theatre.** Day 1 exists for this reason.

---

## The week

### Monday 10 August — verify four numbers *(≈1 hour)*

The Mecca quotation names specific equipment. Get today's cost for each, in writing:

| Item | Rate card assumption |
|---|---|
| Danfoss `OP-MGZD048MTA02D` condensing unit | part of the 8,800 chiller set |
| Danfoss `OP-LGQC068NTA02D` condensing unit | part of the 6,400 freezer set |
| Günay `GNE 130.4A N` evaporator | " |
| Günay `GNE 135.8D N` evaporator | " |

Four calls. Everything downstream re-runs in seconds once these exist.

**Nothing else this week is safe to act on until this is done.**

### Tuesday 11 August — re-run Mecca and decide it

```bash
python3 scripts/margin.py --config scripts/examples/mecca.json --price 46000
```

Mecca was quoted **3 August** with 15-day validity — **open until roughly 18 August.**
It is the one job where this exercise can still change the outcome instead of
explaining history.

| If the rate card is… | Then |
|---|---|
| **Right** | Mecca is at −131. To reach the 20% floor it must rise **9,357.25 → 55,357.25**. Revise before 18 Aug, or walk away deliberately. |
| **Too high** | The back-test overstates every cost. Rate card becomes blocking; no further quotation issues until it is rebuilt. |
| **Too low** | Worse than it looks, and more urgent. |

> Also fix while it is open: the header says validity *"15 Days"*, clause 13.6 says
> *"30 days"*. A client can read both. And clause 13.5 says *"exclusive of VAT, if
> applicable"* — which is `DECISIONS.md` D-005, live, on a document already issued.

### Wednesday 12 August — rule the floor *(10 minutes)*

`DECISIONS.md` **D-004 has been sitting unruled since 3 August.** Until a number is
confirmed, nothing can be enforced, because a rule that is not computed at the
decision point is a preference, not a control (`lessons.md` L-001).

**Recommended ruling — three parts, not one:**

| Band | Rule |
|---|---|
| **Below 22% markup on cost** | Owner override required, written reason, logged in `logs/overrides/` |
| **22% – 30%** | Legitimate, but carries a reason code: TENDER · REPEAT · VOLUME · STRATEGIC · CORRECTION |
| **30%+** | Default for a new client. No justification needed. |

**Why 22% and not higher.** It sits just above the pricing guide's own lowest
documented tier (20%, competitive/tender/repeat), so it does not invalidate genuine
tender pricing. It is a *floor*, not a target — the target stays 30% for new clients.
And with QAR 614,350 uncollected, this is the wrong quarter to price work away on a
theory: the win rate is still unknown, so the floor should move up on evidence, not
on hope.

**The discipline is in the middle band, not the floor.** "Competitive" becomes a
decision with a name attached instead of a drift.

### Thursday 13 August — make it a gate, not a guideline

Every quotation runs through the calculator before it is issued. No exceptions, no
"this one is small".

```bash
python3 scripts/margin.py --config <job>.json --price <proposed>
# exit code 2 = below floor
```

`margin.py` now reports, in addition to the cost build-up and price ladder:

- **Cost drivers** — envelope vs equipment as a share of direct cost
- **`*** EQUIPMENT-DRIVEN JOB ***`** when equipment is the larger half, with the
  per-room systems cost stated
- **Cost per room**
- **`IF PRICED BY ROOM SIZE`** — splits the proposed price by panel area and flags any
  room that lands under its own cost

That last check is the Mecca error made visible. On Mecca it prints:

```
  IF PRICED BY ROOM SIZE (area-weighted)
  Chiller                23,000.00 vs cost   24,491.90  <-- UNDER COST
  Freezer                23,000.00 vs cost   21,639.14

  'Chiller' is 1,491.90 under its own cost when the price is split
  by area. Equipment does not scale with size — price the equipment
  count, not the square metres.
```

### Friday 14 August — start measuring the thing everyone is guessing about

**Win rate is unknown** (OL-012). Only won jobs are recorded. That single gap is why
"the market is too competitive" cannot be tested — if quotes are being discounted and
still lost, the discounting is not buying the work, and the diagnosis changes entirely.

```bash
python3 scripts/quote_log.py add --ref QUT/DCTS/NNN/2026 --client "…" \
    --cost <from margin.py> --price <quoted> --rooms N --reason TENDER
python3 scripts/quote_log.py close --ref QUT/DCTS/NNN/2026 --outcome lost --lost-to price
python3 scripts/quote_log.py report
```

Every quote, the day it goes out. Ten closed quotes and the argument is over.

> **Also surfaced by the back-test and not yet owned:** `numbering-log.md` says the
> next quotation is "after 066". Reality is `174/2026` on 3 August and `214/2026` on
> 5 August — roughly 148 numbers unaccounted for. **The next document issued from that
> log will collide.** Not this plan's lane, but it is blocking, and it belongs to
> LEDGER this week.

---

## What this is worth

| | QAR |
|---|---|
| Mecca `174/2026`, if the rate card is right and it is revised to the floor | **9,357** |
| The three back-tested quotes, had they been priced at the 30% default | **17,544** |
| Five margin points across the 758,100 book | **≈38,000** |
| 14.6% → 25% across the book | **≈79,000** |

No new clients. No capital. No new market. This is money on work already won or
already quoted.

---

## Definition of done — Friday

- [ ] Four equipment costs verified in writing; rate card dated or flagged as wrong
- [ ] Mecca re-run on verified costs, and a decision taken — revised, held, or walked
- [ ] D-004 ruled: floor number confirmed, reason-code band confirmed, entry updated
- [ ] Every quotation issued this week has a computed cost build-up behind it
- [ ] Quote log started; every quote issued this week logged the day it went out
- [ ] Numbering-log discrepancy handed to LEDGER with the two known references

## What is deliberately not in this week

Raising prices across the board. Re-quoting closed jobs. Touching the register.
Chasing Mesaieed — that is the next plan, and it is worth more, but it is a different
week's work.

**One thing at a time, finished.**
