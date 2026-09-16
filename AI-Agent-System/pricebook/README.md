# PRICE BOOK — vendor rates as actually quoted

**Owner:** PROCURE · **Opened:** 16 September 2026

Every vendor quotation TNDK/DCTS receives, captured line by line, so that the next
one can be compared against it instead of against memory.

---

## Why this exists

Three things in this system needed it and none of them had it:

| Need | Where it is stated | What was missing |
|---|---|---|
| "Compare quotes on landed cost, not headline price" | `agents/procure/IDENTITY.md` | Nothing to compare against |
| "Flag when a real vendor price diverges from the estimating rate" | same | No record of any real vendor price |
| OL-009 — rate card verification date unknown | `memory/open_loops.md` | No date, because no captured quote |

A quotation that arrives, gets used once and goes in a folder teaches nothing. The
same part quoted twice, six months apart, is the only way TNDK finds out that the
estimating rate has drifted.

## What may go in here — and what may not

**In:** vendor quotations. Part, brand, model, quantity, unit price, terms, validity,
and the document reference it came from. These are *inbound offers to TNDK*, not client
data, and they have no other source of truth — nothing here duplicates a Drive register.

**Not in:** anything from `02 - Registers/`. No contract values, no received amounts,
no balances, no client names against money. That data lives in Drive and is copied
nowhere (`README.md`, `TOOLS.md`, `memory/lessons.md` L-003).

> Farhan's ruling is still wanted on whether a vendor price book belongs in the repo
> at all or in `TNDK Documents/` — logged as **OL-014**. It sits here for now because
> it needs version history to be worth anything: the whole point is what a price *was*
> last time. Moving it to Drive later is a copy and a delete of these files.

## The three rules this record keeps

1. **Nothing in a quote file is derived.** Unit prices, totals and terms are as printed.
   Where a figure is computed (the handwritten sheet has no total), it is marked
   computed and flagged for confirmation — `RULES.md` A3.
2. **A comparison is only as good as its item key.** Two vendors describing the same
   part differently map to one key in `items.json`; where they are *not* the same thing,
   the key carries a `compare_note` and the comparison prints it. A 300% spread is
   usually a specification difference, not a saving.
3. **Vendor cost is never a client price.** Costs from here go into `margin.py`, and
   the price that comes out goes to Farhan. `RULES.md` B: any price shown to a client
   needs his approval, always.

## Where the original documents live

Only the *extracted figures* are kept here. The vendor PDF and the photographed sheet are
source documents and belong in Drive under the project folder (`01 - Projects/<Client>/`),
not in this repo. Each quote file names its original in `document.source_file` so the two
can always be put back together.

## Layout

```
pricebook/
├── README.md        this file
├── items.json       canonical part registry — one key per physical thing
├── quotes/          one file per vendor quotation, named <date>-<vendor>-<ref>
└── comparisons/     dated comparison outputs, as issued to Farhan
```

## Adding a quotation

1. Add any new part to `items.json`. Re-use an existing key wherever the part is the
   same; add a `compare_note` wherever it is nearly-but-not the same.
2. Create `quotes/<YYYY-MM-DD>-<vendor>-<ref>.json`. Copy an existing file's shape.
   Record `provenance.confidence`: `high` for a vendor PDF, `medium` for a transcribed
   photo or a phone price.
3. Verify before trusting:

```bash
python3 scripts/pricebook.py --verify      # exit 2 = a quote does not add up
python3 scripts/pricebook.py --compare
python3 scripts/pricebook.py --item copper-coil-half-50ft
python3 scripts/pricebook.py --basket pricebook/quotes/<file>.json
```

`--verify` fails loudly if a line does not multiply out or a stated total does not
match its lines. Run it on every new quote before the rates are used anywhere.

## On record

| Date | Vendor | Ref | Lines | Stated total |
|---|---|---|---|---|
| 2026-09-16 | Arctic (ACC Qatar) | ATC/AZ/QT/26/07619 Rev1 | 20 | QAR 2,467.50 ✅ verified |
| 2026-09-16 | *unidentified* — handwritten on our material list | none | 20 | none on document (computes to 18,755.00) |

Both expire **21 September 2026** (5 days from issue, ex-stock subject to prior sale).
