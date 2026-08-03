# OUTPUT SCHEMA — PURSUE

Every PURSUE handoff returns this structure. TNDK-SALES validates against it.

## Structured payload

```json
{
  "agent": "PURSUE",
  "cycle": "weekly-pipeline | outcome-capture | conversion-report | single-quote",
  "as_of": "2026-08-03",

  "pipeline": {
    "open_count": 4,
    "unweighted": 219700.00,
    "expected": 55296.00,
    "expected_basis": "ASSUMED 30% — only 3 tracked decisions on record",
    "action_required": [
      { "ref": "QUT/DCTS/067/2026", "client": "Umm Salal Farms", "value": 47500.00,
        "flags": ["PAST VALIDITY", "QUIET"], "days_open": 24, "days_quiet": 22,
        "draft_ready": true }
    ]
  },

  "moved": {
    "won":  [ { "ref": "QUT/DCTS/065/2026", "value": 46000.00,
                "award_ref": "PO-2026-0000248", "decided_date": "2026-07-06" } ],
    "lost": [ { "ref": "QUT/DCTS/063/2026", "value": 62000.00,
                "loss_reason": "PRICE_LOWER", "client_words": "another supplier came in lower",
                "decided_date": "2026-05-26" } ]
  },

  "conversion": {
    "denominator_verified": false,
    "tracked_decisions": 3,
    "win_rate": null,
    "win_rate_status": "INSUFFICIENT_DATA",
    "avg_days_to_decision": 34,
    "by_tier": {
      "20%": { "n": 1, "rate": null, "suppressed": "insufficient_data" },
      "25%": { "n": 1, "rate": null, "suppressed": "insufficient_data" },
      "30%": { "n": 1, "rate": null, "suppressed": "insufficient_data" },
      "unrecorded": { "n": 5, "rate": null, "suppressed": "survivorship" }
    }
  },

  "concentration": {
    "current_top2_pct": 86.2,
    "if_won": [ { "ref": "QUT/DCTS/068/2026", "after_pct": 88.1, "delta_pct": 1.9 } ]
  },

  "drafts": [
    { "ref": "QUT/DCTS/067/2026", "client": "Umm Salal Farms",
      "purpose": "Ask whether a decision is expected; quotation validity lapsed 9 days ago",
      "contains_price": false, "contains_date_commitment": false, "status": "DRAFT — NOT SENT" }
  ],

  "routed_out": [
    { "ref": "QUT/DCTS/069/2026", "to": "PRICE",
      "reason": "Client asked for 8% off", "client_words": "can you do better on the price" }
  ],

  "assumptions": [
    "Date sent taken from the quotation document date — not confirmed with Farhan"
  ],
  "flags": [
    "Denominator unverified — QUT series may include revisions (OL-014)"
  ],
  "unresolved": [
    "Decision-maker unknown on 2 of 4 open quotations"
  ],
  "status": "READY_FOR_REVIEW",
  "human_review_required": true
}
```

## `status` values

| Value | Meaning | Manager action |
|---|---|---|
| `READY_FOR_REVIEW` | Cycle complete, drafts ready. | Present to Farhan. |
| `ACTION_REQUIRED` | Quotations past validity or quiet. | Present the list with the drafts. |
| `BLOCKED_ON_INPUT` | Missing a ref, value or send date. | Ask the one question. |
| `BLOCKED_ON_OWNER` | An outcome needs Farhan's confirmation (e.g. verbal award). | Escalate. |
| `ROUTED_OUT` | The request was a price, date or scope question. | Hand to TNDK-OPS. |
| `RECONSTRUCTION_ONLY` | Historic backlog entered; no rates computed. | Label clearly. |

## Human-readable companion

Always accompany the payload with the pipeline report format in `agents/sales/MANAGER.md`, plus
the drafted follow-ups in full. Farhan reads the report and the drafts; the manager validates the
JSON. Both must agree; if they disagree, that is a defect.

## Hard requirements

- `human_review_required` is **always `true`**. PURSUE never returns a message cleared to send.
- Every entry in `drafts` **must** carry `contains_price: false` and
  `contains_date_commitment: false`. A `true` on either is a `RULES.md` A9 breach and the draft
  does not leave the agent.
- `win_rate` is `null` unless `tracked_decisions >= 20`. `win_rate_status` must then read
  `INSUFFICIENT_DATA`. Never emit a number with a caveat instead.
- Any tier whose `suppressed` is `survivorship` must never be presented as performance.
- `conversion.denominator_verified: false` **must** appear in `flags` on any output that reports
  a conversion figure.
- `moved.won` entries require an `award_ref`. No written award, no win.
- `lost` entries require a `loss_reason` from the standard list. `UNKNOWN` is permitted;
  an empty string is not.
- `assumptions` is never omitted. An empty list is a claim that nothing was assumed.
