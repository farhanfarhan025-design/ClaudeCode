# OUTPUT SCHEMA — PRICE

Every PRICE handoff returns this structure. The manager validates against it.

## Structured payload

```json
{
  "agent": "PRICE",
  "job": "Vegetable chiller + freezer room",
  "client": "Mr. Suresh",
  "client_type": "new | repeat | tender",
  "quotation_ref": "QUT/DCTS/067/2026 | null",

  "cost": {
    "direct": 43448.45,
    "labour_pct": 0.15,
    "labour": 6517.27,
    "transport": 1500.00,
    "total": 51465.72
  },

  "ladder": {
    "20%": 61758.86,
    "25%": 64332.15,
    "30%": 66905.43,
    "35%": 69478.72
  },

  "recommendation": {
    "tier": "30%",
    "price": 66905.43,
    "rounded": 67000.00,
    "reasoning": "New client, standard access, no competitive pressure stated."
  },

  "proposed": {
    "price": 59000.00,
    "profit": 7534.28,
    "markup_on_cost": 0.1464,
    "margin_on_price": 0.1277,
    "below_floor": true,
    "gap_to_floor": 2758.86,
    "reason_code": null,
    "override": { "required": true, "granted": false, "logged_at": null }
  },

  "assumptions": [
    "Panel thickness 100mm — not stated, standard assumed",
    "Transport within Doha — 1,500 lump sum"
  ],
  "flags": [
    "D-005: quotation carries 'excluding 5% VAT' while invoices may never mention tax"
  ],
  "unresolved": [
    "Rate card last-verified date unknown"
  ],
  "status": "BLOCKED_ON_OVERRIDE",
  "human_review_required": true
}
```

## `status` values

| Value | Meaning | Manager action |
|---|---|---|
| `READY_FOR_APPROVAL` | Priced at or above floor. Draft ready. | Present to Farhan. |
| `NEEDS_REASON_CODE` | Between floor and default. | Present; capture the reason. |
| `BLOCKED_ON_OVERRIDE` | Below floor. | **Stop.** Escalate for override. |
| `BLOCKED_ON_INPUT` | Missing a required input. | Ask the one question. |
| `BLOCKED_ON_VENDOR` | Contract too large for rate-card estimating. | Route to PROCURE first. |
| `ESTIMATE_ONLY` | Planning figure, not quotable. | Label clearly; do not let it become a quote. |

## Human-readable companion

Always accompany the payload with the plain report — the table format in `EXAMPLES.md`.
Farhan reads the table; the manager validates the JSON. Both must agree; if they disagree,
that is a defect.

## Hard requirements

- `human_review_required` is **always `true`**. PRICE never returns a price that is cleared to send.
- `below_floor: true` **must** pair with `status: BLOCKED_ON_OVERRIDE`. No exceptions.
- `assumptions` is never omitted. An empty list is a claim that nothing was assumed — make sure
  that is true before writing it.
- If `override.granted` is `true`, `override.logged_at` must be non-null. The log precedes the price.
