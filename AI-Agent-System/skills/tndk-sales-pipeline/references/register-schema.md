# The pipeline register — columns and data format

## Where it lives

`TNDK Documents/02 - Registers/pipeline_register.xlsx`, alongside `approved_register.xlsx`, `amounts_to_receive.xlsx` and `margin_log.xlsx`.

Drive holds the data. Build the spreadsheet from the JSON, never the other way round — the Approved Works Register broke because a formula range didn't grow with the table, and the fix was to compute every figure and write it as a literal.

## Columns

| Column | Notes |
|---|---|
| Quote ref | `QUT/DCTS/NNN/YYYY`. Never reused — check the numbering log. |
| Date sent | The date it **actually went**, not the document date. If they differ, the difference is an assumption worth recording. |
| Client | |
| Project | |
| Value (QAR) | From the issued quotation. Never recomputed. |
| Tier | `20%` / `25%` / `30%` / `35%` / `unrecorded`. Never inferred. |
| Source | referral · repeat · tender · consultant · inbound · prospecting |
| Status | `open` · `won` · `lost` · `expired` · `withdrawn`. Nothing else. |
| Days open / to decide | Computed. Days open for a live quote; days taken for a decided one. |
| Last contact | Drives the 21-day quiet flag. |
| Flag | `PAST VALIDITY` / `QUIET`, computed. |
| Next action | Every open row needs one. |
| Next date | |
| Decided | Required on any `won` or `lost` row. |
| Loss reason | Required on any `lost` row. See `follow-ups.md`. |
| Notes | Client's own words, in quotation marks, with dates. |
| Check | Formula cross-check. `MISMATCH` means the file was hand-edited. |

## JSON format

The scripts read this. One object per quotation.

```json
{
  "as_of": "2026-08-03",
  "quotes": [
    {
      "ref": "QUT/DCTS/067/2026",
      "client": "Umm Salal Farms",
      "project": "Cold room, farm store",
      "value": 47500,
      "date_sent": "2026-07-10",
      "status": "open",
      "last_contact": "2026-07-12",
      "tier": "30%",
      "source": "inbound",
      "next_action": "Confirm consultant approval received",
      "next_action_date": "2026-08-06"
    },
    {
      "ref": "QUT/DCTS/063/2026",
      "client": "Doha Central Bakery",
      "project": "Chiller + freezer",
      "value": 62000,
      "date_sent": "2026-05-05",
      "status": "lost",
      "decided_date": "2026-05-26",
      "tier": "30%",
      "loss_reason": "PRICE_LOWER",
      "source": "inbound",
      "notes": "\"about ten percent under you\" — no figure stated"
    }
  ]
}
```

**Required on every row:** `ref`, `client`, `value`, `date_sent`, `status`.
**Also required:** `decided_date` on any decided row; `loss_reason` on any lost row.

The scripts refuse to run if these are missing, or if a reference is duplicated. That's deliberate — a register that loads with gaps in it is worse than one that won't load.

## The `reconstructed` flag

Set `"reconstructed": true` on any row recovered from the award register rather than tracked from the day it was sent.

Those rows establish the **denominator** — how many quotations exist — and nothing else. They're excluded from every rate, because the register they came from only ever recorded wins: including them reports a win rate near 100% by construction. The scripts enforce this; a row with `"tier": "unrecorded"` is treated the same way.

When reconstructing history, resist three temptations:

- Don't infer a tier. It wasn't recorded; `unrecorded` is the honest value.
- Don't infer a loss reason from the absence of an award.
- Don't assume a quotation with no award was lost. It may still be open, or may never have been sent.

## Thresholds the scripts apply

| | Value | Why |
|---|---|---|
| Quotation validity | 15 days | TNDK's documented standard |
| Quiet threshold | 21 days | Three weeks with no contact isn't "open", it's unrecorded |
| Minimum tracked decisions for a win rate | 20 | Below that, a percentage from n=3 reads the same as one from n=300 |
| Minimum decisions per tier | 5 | Same reason, per tier |
| Assumed conversion, when no observed rate exists | 30% | Always reported as assumed, never as a forecast |

Age decay on open quotations: full weight inside validity, then ×0.6 to 30 days, ×0.3 to 60, ×0.1 beyond. It scales the conversion probability rather than replacing it — a 75-day-old quotation is not worth its face value however encouraging the last conversation was.

## Commands

```bash
# Weekly cycle. Exit code 2 = quotations require action.
python3 scripts/pipeline.py --data pipeline.json

# With the concentration check
python3 scripts/pipeline.py --data pipeline.json --awards awards.json

# Machine-readable
python3 scripts/pipeline.py --data pipeline.json --json

# Rebuild the branded spreadsheet
python3 scripts/build_pipeline_register.py --data pipeline.json --outdir ./out
```

Both scripts assert their totals against the source data before writing, and fail loudly rather than produce a plausible-looking register.
