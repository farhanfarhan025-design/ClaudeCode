# Spec schema

The generator takes one JSON file. Only five fields are required; everything
else has a house default or is left as the master has it.

## Required

| Field | Type | Example | Notes |
|---|---|---|---|
| `reference` | string | `"QUT/DCTS/SQ073/2026"` | warns if it doesn't match `QUT/DCTS/[SQ]NNN/YYYY` |
| `date` | string | `"05 August 2026"` | printed verbatim — use `DD Month YYYY` |
| `client` | object | see below | |
| `rooms` | array | see below | at least one |
| `total` | number | `46800` | QAR, lump sum, excluding VAT |

## `client`

| Field | Required | Example |
|---|---|---|
| `name` | yes | `"M/s. Marza Group of Companies"` |
| `address` | no | `"Doha, Qatar"` — newlines become separate lines |
| `attn` | no | `"Mr. Ashik"` — printed as `Attn: Mr. Ashik` |

## `rooms[]`

| Field | Required | Default | Example |
|---|---|---|---|
| `type` | yes | — | `"CHILLER"`, `"FREEZER"` (upper-cased in the table) |
| `temperature` | yes | — | `"0°C to +8°C"`, `"−18°C to −22°C"` |
| `length` / `width` / `height` | yes | — | `"6.0"` / `"2.40"` / `"2.90"` in metres |
| `qty` | no | `1` | number of identical rooms |
| `panel_thickness` | no | `"100 mm"` | `"150 mm"` for freezers |
| `floor_included` | no | `true` | `false` prints "Not included in scope" |

**Dimensions should be strings.** JSON cannot hold the trailing zero in `2.40`,
and the house style writes `2.40`, not `2.4`. Numbers still work — they are
formatted to at most two decimals — but strings are reproduced exactly.

Note the minus sign in freezer temperatures is U+2212 (`−`), matching the master.

## `door`

| Field | Default | Notes |
|---|---|---|
| `qty` | `1` | spelled out in scope and BOQ ("three (3) No.") |
| `width_mm` | `900` | clear opening |
| `height_mm` | `1900` | clear opening |

## `refrigeration`

All optional — omit the block entirely to leave section 5 as the master has it.

| Field | Default | Example |
|---|---|---|
| `sets` | `1` | number of split systems |
| `condensing_unit` | — | `"BITZER LH64/2DES-3Y"` |
| `compressor_brand` | `"BITZER"` | stripped from the model when printing "model ..." |
| `cu_origin` | `"Germany"` | |
| `evaporator` | — | `"HSE302-1DWEO"` |
| `evap_origin` | `"South Africa"` | |
| `refrigerant` | — | `"R404A"` |
| `capacity_kw` | — | `5.60` — cooling capacity |
| `power_input_kw` | — | `3.25` |
| `current_a` | — | `6.05` |
| `power_supply` | `"400V-3-50Hz"` | |
| `sst` | `"−8°C"` | saturated suction temp for the selection note |
| `ambient` | `"43°C"` | Doha design ambient |
| `selection_basis` | `"BITZER"` | whose selection software was used |
| `defrost` | — | overrides the defrost row |

## Optional overrides

| Field | Effect |
|---|---|
| `validity` | defaults to `"15 Days from quote date"` |
| `subject` | replaces the text after `Subject:` |
| `intro` | replaces the "Dear Sir, ..." paragraph |
| `total_words` | overrides the auto-generated amount in words |
| `boq` | array of `{"description": "...", "amount": 1234}` replacing the six default lines; `amount` may be omitted for a lump-sum quote |
| `delivery` | object of `{"<row label>": "<value>"}` patching section 12, e.g. `{"Installation Period": "10 – 14 working days for civil-ready site"}` |

## Worked example

`examples/marza-group-chiller.json` is the exact spec for `QUT/DCTS/SQ072/2026`.
Running it regenerates that document identically, so it doubles as the
regression test:

```bash
python3 scripts/generate.py \
  --spec examples/marza-group-chiller.json \
  --output /tmp/check.docx --print-summary
```

Expected summary: walls 48.72, ceiling 14.40, floor 14.40, total panel 77.52
sqm, volume 41.76 m³, QAR 46,800.00.
