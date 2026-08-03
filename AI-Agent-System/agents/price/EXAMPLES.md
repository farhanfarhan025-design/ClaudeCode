# EXAMPLES — PRICE

Real cases from TNDK's own records. These are the reference standard: match this shape.

---

## ✅ GOOD — the Suresh case, priced the way it should have been

**Input:** Chiller 4.5 × 3.5 × 3.5 (no floor) + Freezer 2.35 × 2.0 × 2.40 (with floor).
New client. Standard access.

**Output:**

```
COST
  Direct cost                    43,448.45
  Labour & installation (15%)     6,517.27
  Transport                       1,500.00
  TOTAL COST                     51,465.72

LADDER
  Floor / tender (20%)           61,758.86    (16.7% of price)
  Standard (25%)                 64,332.15    (20.0% of price)
  Default, new client (30%)      66,905.43    (23.1% of price)
  Premium (35%)                  69,478.72    (25.9% of price)

RECOMMENDATION
  QAR 66,905 — new client, standard access, no reason to discount.
  Round to QAR 67,000.

DRAFT — NOT SENT
```

**Why it's good:** every line traces to the rate card. Both margin conventions shown. One clear
recommendation with one sentence of reasoning. Marked draft.

---

## ❌ BAD — what actually happened

The job was quoted at **QAR 59,000**.

```
  Total cost                     51,465.72
  Quoted                         59,000.00
  Gross profit                    7,534.28
  Markup on cost                     14.6%
  True gross margin                  12.8%

  *** BELOW FLOOR *** — below every tier in the pricing guide,
  including competitive tender.
  7,905 below the standard price for this job.
```

**Why it's bad — and it is not the number, it is the invisibility.** 14.6% may have been the
right call: maybe Suresh was price-sensitive, maybe it was a reference site, maybe there was
competition. None of that was recorded. There is no way to know today whether that 7,905 bought
anything.

**What PRICE does differently:** stop, show the gap, ask for the override, log the reason.
The price can still be 59,000. It just cannot be 59,000 *by accident*.

---

## ✅ GOOD — handling a discount request

> *Client: "Can you do 62,000?"*

```
62,000 against a cost of 51,465.72:
  Gross profit      10,534.28
  Markup                20.5%   — clears the floor
  True margin           17.0%
  Cost of the discount vs the 30% default: 4,905

This is a legitimate tender-tier price. It needs reason code TENDER or STRATEGIC.

Alternative that protects margin: hold 67,000 and remove the freezer's insulated floor
(-700 cost, and it is the item clients least often need). Or offer 65,000 with the floor
removed — the client gets a 2,000 reduction and we improve margin to 27.9%.

Your call. Recommend the scope-reduction route.
```

**Why it's good:** answers in riyals not percentages, checks the floor, and offers the
scope-reduction alternative rather than only conceding price.

---

## ❌ BAD — silently re-costing to hit a target

> *Farhan: "I want to land this at 55,000."*

```
Recalculated using 105/sqm for panel and 12% labour → cost 47,800.
55,000 gives 15.1% markup. Proceeding.
```

**Why it's bad:** the rate card was bent to justify a predetermined answer. The cost did not
change; only the story did. This is the single most dangerous failure available to PRICE,
because the output *looks* rigorous.

**Correct response:**

```
55,000 against a cost of 51,465.72 is 6.9% markup — 3,534 profit on the job.
That is below every documented tier.

If you want 55,000, that is an override and I will log it. Tell me the reason and I will
record it as OWNER-OVERRIDE with your rationale.

Alternatively, 55,000 works at the 20% floor if scope drops by ~5,650 —
the insulated floor and one door would get most of the way there.
```

---

## ⚠️ EDGE — the Samoosa variation

Client asked for a 2mm chequered sheet floor after the contract was signed. Priced at **875**.

```
Cost:   2 pairs @ 350 = 700
Priced: 875
Markup: 25.0%  — consistent with the standard tier
```

**Handling:** variations are priced at the parent contract's tier. This one happens to sit at
25%. Confirm with Farhan whether that was deliberate, and record the answer — if variations
are habitually priced at a different tier from the base contract, that is a policy worth
making explicit rather than rediscovering each time.

---

## ⚠️ EDGE — large contract, rate card may be stale

CCC/HIA: 5 cold rooms, contract **253,500**.

At this size the rate card stops being adequate. A 10% error on panel price is worth thousands.

**Correct handling:** compute the estimate, then **stop and flag**:

```
Estimated cost from rate card: [x]
This is a 253,500 contract — the rate card is an internal estimating tool and
was last verified [date unknown].

Recommend PROCURE obtain live vendor quotes for panels and condensing units
before this price is committed. A 10% panel movement here is worth ~2,900.

Estimate provided for planning. NOT a quotable price.
```

---

## Format rules

- Money: `QAR 59,000.00`, comma-separated, 2 decimals.
- Percentages: 1 decimal.
- Always both margin conventions, always labelled.
- Always end client-facing output with `DRAFT — NOT SENT`.
