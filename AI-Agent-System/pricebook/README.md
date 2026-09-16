# PRICE BOOK — what we pay, and what we charge

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

**In:** quotations, in both directions.

| Direction | What it is | Why it is here |
|---|---|---|
| `inbound` | a vendor's offer to us | what we **pay** |
| `outbound` | our own quotation to a client | what we **charge** |

Part, brand, model, quantity, unit price, terms, validity, and the document reference it came
from. Inbound quotes are offers to TNDK with no other source of truth. Outbound quotes are
here for one reason: `--margin` sets the two against each other and checks the result against
the floor, which `analysis/FINDINGS.md` describes as the thing nobody could see at the moment
of quoting. An outbound line is never used as a cost — the script refuses it.

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
python3 scripts/pricebook.py --verify      # arithmetic, every document
python3 scripts/pricebook.py --compare     # cross-vendor unit prices
python3 scripts/pricebook.py --rates       # real prices vs the margin.py rate card
python3 scripts/pricebook.py --item copper-coil-half-50ft
python3 scripts/pricebook.py --basket pricebook/quotes/<inbound>.json
python3 scripts/pricebook.py --margin pricebook/quotes/<outbound>.json
```

`--verify` exit codes:

| Code | Meaning |
|---|---|
| 0 | every document adds up |
| 1 | the only failures are ones the quote file documents in `known_discrepancy` |
| 2 | a document does not add up and nobody has written down why — **do not use it** |

A documented discrepancy is acknowledged, never waived: it still prints in full, and the
quote still must not be ordered against. Exit 1 exists so the check stays usable while a
vendor is being chased, not so an error can be buried.

To hand Farhan something printable:

```bash
python3 scripts/pricebook_report.py                       # -> out/pricebook.html
python3 scripts/pricebook_report.py --price-list \
        --out out/pricelist.html                          # just the comparison, landscape
/opt/pw-browsers/chromium-1194/chrome-linux/chrome --headless --disable-gpu \
  --no-sandbox --no-pdf-header-footer \
  --print-to-pdf=out/TNDK-PriceBook.pdf out/pricebook.html
```

A4 portrait, house colours, marked INTERNAL on every copy — it carries vendor costs and is
not a client document. `out/` is gitignored: the report is a **view** of `pricebook/`, never a
second copy of it. Regenerate it, never edit it.

Where a line has a length or pack size, record `unit_size` and `unit_size_uom`. The script
then compares per metre instead of per piece — which is how the capillary comparison went
wrong the first time.

## On record

| Date | Direction | Party | Ref | Lines | Stated total |
|---|---|---|---|---|---|
| 2026-07-28 | inbound | Airtronics Trading Contracting & Maintenance | ART-QTN-3174-26 | 9 | QAR 18,525.00 ✅ |
| 2026-08-20 | inbound | Arctic (ACC Qatar) | ATC/NSA/QT/26/00286 | 21 | QAR 3,220.00 ✅ *(after 230.00 discount)* |
| 2026-08-20 | inbound | Arctic — Rayyan showroom | ATC/RY/QT/26/00286 | 2 | QAR 5,400.00 ⚠️ **lines sum to 5,500.00** |
| 2026-08-29 | inbound | Arctic Cooling Company | ACC/QT/RVD/1508/2026 | 1 | QAR 3,600.00 ✅ |
| 2026-09-16 | inbound | Arctic (ACC Qatar) | ATC/AZ/QT/26/07619 Rev1 | 20 | QAR 2,467.50 ✅ |
| 2026-09-16 | inbound | *unidentified* — handwritten on our material list | none | 20 | none stated *(computes to 18,755.00)* |
| 2026-09-16 | **outbound** | **Shared Services** *(our quotation)* | QUT/DCTS/237/2026 | 20 | QAR 21,700.00 ✅ |

✅ = lines re-multiplied and summed against the document's own stated total.

**Expiring 21 September 2026:** the Shared Services quotation and the two 16 September vendor
quotes behind it.

## What the record has already caught

- **QUT/DCTS/237/2026 is priced at 17.2% markup** against known cost — below both floors on
  record, with no override logged. `RULES.md` B and E. See OL-018.
- **`RATES["unit_freezer"]` is 166% below a real quote** — 6,400.00 in the card against
  17,050.00 quoted for the Samoosa freezer plant. See OL-019.
- **The door rate is confirmed** at 1,800.00 by two independent quotations. The first rate in
  the card with a verification date.
- **A vendor quotation that does not add up** — ATC/RY/QT/26/00286, out by 100.00.
- **A capillary comparison that was wrong** in the first comparison note, because lengths were
  not being normalised. Fixed, and the note is marked superseded rather than deleted.
