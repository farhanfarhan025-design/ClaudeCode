# PLAYBOOK — PRICE

## Trigger

Any of:
- A scope arrives from SCOPE (dimensions, room types, temperatures confirmed).
- Farhan asks for a price, a quote, or "what should I charge for…".
- A client requests a discount on an issued quotation.
- A variation is added to a live job (extra works, e.g. the Samoosa chequered floor).
- Thursday 16:00 — margin review cycle.

## Required inputs

Before computing anything, confirm you have:

| Input | Required? | If missing |
|---|---|---|
| Room type (chiller / freezer) | **Yes** | Ask. Changes the unit cost by 2,400. |
| L × W × H, metres, external | **Yes** | Ask. Everything derives from this. |
| Insulated floor? | **Yes** | Ask. Adds panel area + chequered/ply. |
| Number of rooms | **Yes** | Ask. |
| Doors per room | No | Default 1. |
| Panel thickness | No | Default 100mm. Note if 80/150mm — rate may differ. |
| Site access difficulty | No | Default standard. Affects tier selection. |
| Client type (new / repeat / tender) | **Yes** | Ask. Sets which tier is the default. |
| Transport beyond Doha | No | Default 1,500 lump sum. |

**Do not re-ask for anything already in the conversation.** Extract it. Farhan has an explicit
standing instruction about this and finds redundant questions irritating. Ask only for what is
genuinely absent and genuinely changes the number.

## Steps

### 1 — Build the config

Write a JSON job config to the working directory:

```json
{
  "job": "<description>",
  "client": "<client>",
  "rooms": [
    { "name": "Chiller", "type": "chiller",
      "length": 4.5, "width": 3.5, "height": 3.5, "floor": false, "doors": 1 }
  ],
  "transport": 1500,
  "extras": [
    { "item": "2mm chequered sheet", "detail": "client-requested variation", "amount": 875 }
  ]
}
```

`extras` is how variations enter the cost — never by adjusting a rate.

### 2 — Compute

```bash
python3 scripts/margin.py --config job.json                 # ladder only
python3 scripts/margin.py --config job.json --price 59000   # + floor check
python3 scripts/margin.py --config job.json --json          # machine-readable
```

Exit code `2` means below floor. Treat a non-zero exit as a hard stop.

### 3 — Select the tier

| Situation | Tier |
|---|---|
| New client, standard job | **30%** — the default |
| Repeat client with a payment history | 25% |
| Competitive tender, or a strategic reference site | 20% — the floor |
| Urgent, difficult access, tight programme | 35% |
| Anything below 20% | **Owner override only** |

Recommend one tier. Give one sentence of reasoning. Do not present five options and ask him
to choose — that is offloading your job onto him.

### 4 — Sanity-check the cost against reality

Before presenting, ask yourself:
- Does the panel area look right for the volume? (~100 sqm for two mid-size rooms)
- Is the rate card older than the last vendor quote? If PROCURE has a fresher number for
  panels or units, flag it — the rate card is an *estimate*, a vendor quote is a *fact*.
- For contracts above ~100,000: is a single lump-sum transport figure credible?
- Is anything in scope that has no cost line? (This is the most common real error.)

### 5 — Handle the floor

If below floor:

1. **Stop.** Do not produce a quotation.
2. Report: proposed price, total cost, gross profit in QAR, markup %, true margin %, and the
   riyal amount needed to reach the floor.
3. State what the price would be at the floor and at the default.
4. Ask for an explicit override.
5. If overridden, write `logs/overrides/YYYY-MM-DD-<client>.md` **before** producing the
   quotation — the log entry is a precondition, not a follow-up.

If between floor and default: assign a reason code (`TENDER`, `REPEAT`, `VOLUME`,
`STRATEGIC`, `CORRECTION`) and record it. This is not a blocker, just a record.

### 6 — Log the margin

Append to `02 - Registers/margin_log.xlsx`:

`date · client · job · quotation ref · direct · labour · transport · total cost · quoted price · markup % · true margin % · tier · reason code · outcome`

Leave `outcome` blank until won/lost is known. The trailing average is worthless without it —
and the win/loss data is what will eventually tell Farhan whether his low prices are even
buying him the work.

### 7 — Hand off

Return the output schema to the manager. If a quotation document is wanted, the
`tndk-coldroom-quotation` skill produces it — PRICE supplies the **grand total** and the
**amount in words**, nothing else. PRICE does not build documents.

## Discount requests

When a client asks for a discount, never answer with a percentage. Answer with:

- What the discount costs in QAR.
- What margin it leaves.
- Whether it clears the floor.
- What could be removed from scope to fund it instead.

That last one is the most valuable and the most often skipped. A client wanting 10% off is
often satisfied by dropping the insulated floor or a door — which costs far less than 10%
of the price.

## Variations

A variation is priced at the **same tier as the parent contract**, unless Farhan says
otherwise. The Samoosa chequered sheet went out at 875. Check what it cost: 2 pairs at 350 is
700, so 875 is a 25% markup — consistent, and worth confirming that consistency is deliberate
rather than coincidental.

## Definition of Done

- [ ] Cost build-up computed, every line traceable to a rate or vendor quote.
- [ ] Price ladder produced.
- [ ] Realised margin stated in **both** conventions.
- [ ] Floor checked; override logged if breached.
- [ ] Tier recommended with one sentence of reasoning.
- [ ] Margin log appended.
- [ ] VAT/tax contradiction (D-005) surfaced if a quotation is being produced.
- [ ] Output marked **DRAFT — NOT SENT**.
