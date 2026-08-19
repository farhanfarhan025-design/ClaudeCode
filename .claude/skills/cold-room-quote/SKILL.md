---
name: cold-room-quote
description: Produce a TNDK cold room quotation in the standard house format (The New Doha Kitchen Equipment Services W.L.L.). Use this skill whenever the user asks for a cold room, cold storage, chiller, freezer or refrigeration quotation or quote; says "make a quotation", "draft a quote", "send a price" or "quote this client" for a cold room project; mentions a QUT/DCTS reference number; or gives client name, room dimensions and a price and wants the document built. Also use when revising or re-issuing an existing cold room quotation. Produces a branded multi-page Word document with the fixed 13-section structure, computing all panel areas, floor areas and heat-load volumes from the room dimensions.
---

# Cold Room Quote

Builds a TNDK cold room quotation from the saved master template, in the exact
format of `QUT/DCTS/SQ072/2026` (Marza Group). **Every cold room quotation uses
this format** — the layout, section order and wording are fixed; only the
client, sizes, equipment and price change.

**Company:** TNDK — The New Doha Kitchen Equipment Services W.L.L., a division
of Doha Cooling Trading & Solutions W.L.L. Quotations are signed by Farhan,
Sales Engineer.

## How it works

The master (`template/master.docx`) is copied and edited in place — never
rebuilt. That is what keeps the full-bleed cover page, the brand header strip,
the footer and all thirteen section photographs intact. The generator locates
each field by its **label** ("Wall Coverage", "GRAND TOTAL (Lump Sum)"), not by
a hardcoded position, so it stays correct if rows shift.

Verified: regenerating the Marza Group quote from its spec reproduces the
original document exactly — same text, same 13 images byte-for-byte, same
brand colours, same fonts and sizes.

One layout fix is applied on top: the master sizes the service banner under
section 12 slightly too tall for the space left on the page, so it flows onto
a sheet of its own and the quotation ends with a near-empty page. The generator
scales it to fit (default 4.4 in tall), which drops one page from every
quotation. Pass `"banner_height_in": 0` to keep the master's original size.

## Workflow

### Step 1 — collect the inputs

Take whatever the user has already given and only ask about what is genuinely
missing and genuinely matters. The price and the room dimensions are the two
things never to guess.

Required:
- **Client** — name, and the contact person if known
- **Rooms** — type (chiller/freezer), quantity, operating temperature, and
  external L × W × H in metres
- **Total price** in QAR

Defaulted if not supplied:
- Reference — next in the `QUT/DCTS/SQNNN/YYYY` series
- Date — today, formatted `05 August 2026`
- Validity — `15 Days from quote date`
- Panel thickness — `100 mm` (use `150 mm` for freezers)
- Door — 1 No., 900 × 1900 mm
- Floor — included

Everything else in the document (panel construction, coving, control panel,
warranty, exclusions, payment terms) is boilerplate that stays as-is.

### Step 2 — write the spec

Create a JSON spec. Copy `examples/marza-group-chiller.json` and edit it — that
file is the exact input that reproduces the reference quotation.

```json
{
  "reference": "QUT/DCTS/SQ073/2026",
  "date": "12 August 2026",
  "client": { "name": "M/s. ABC Trading W.L.L.", "address": "Doha, Qatar", "attn": "Mr. Khalid" },
  "rooms": [
    { "type": "CHILLER", "qty": 1, "temperature": "0°C to +8°C",
      "length": "6.0", "width": "2.40", "height": "2.90",
      "panel_thickness": "100 mm", "floor_included": true }
  ],
  "door": { "qty": 1, "width_mm": 900, "height_mm": 1900 },
  "refrigeration": {
    "condensing_unit": "BITZER LH64/2DES-3Y", "cu_origin": "Germany",
    "evaporator": "HSE302-1DWEO", "refrigerant": "R404A",
    "capacity_kw": 5.60, "power_input_kw": 3.25, "current_a": 6.05
  },
  "total": 46800
}
```

**Write dimensions as strings.** `"2.40"` prints as `2.40`; the number `2.40`
prints as `2.4`, because JSON drops the trailing zero. The house style keeps it.

Full field reference: `references/spec-schema.md`.

### Step 3 — generate

```bash
python3 scripts/generate.py \
  --spec quote.json \
  --output ~/quotation_ABC_SQ073.docx \
  --print-summary
```

`--print-summary` prints the computed panel areas, volume and amount in words.
**Read it and sanity-check the numbers against the price before sending.**

### Step 4 — check before delivering

```bash
python3 /mnt/skills/public/docx/scripts/office/validate.py <output>.docx
```

Then confirm by eye: client name and reference correct, room table matches what
was asked for, grand total and the words agree, no leftover text from the
reference quote.

For a PDF to send the client:

```bash
soffice --headless --convert-to pdf --outdir . <output>.docx
```

This needs `libreoffice-writer` installed, not just `libreoffice-core` —
without it every .docx fails to load with "source file could not be loaded".

## What the generator computes

Derived from the room dimensions — never type these by hand:

| Field | Formula |
|---|---|
| Wall coverage | 2(L×H) + 2(W×H), × room qty |
| Ceiling coverage | L × W, × room qty |
| Floor coverage | L × W if floor included, else "Not included in scope" |
| Total panel quantity | walls + ceiling + floor, summed over all rooms |
| Internal volume | L × W × H, × room qty |
| Amount in words | from the total, e.g. "Qatari Riyals Forty-Six Thousand Eight Hundred Only." |

These figures appear in several places (panel table, flooring table, capacity
table, scope of work, BOQ item 1). The generator keeps them consistent — which
the hand-edited source did not: its scope bullet said 85 sqm where the panel
table and BOQ both said 77.52 sqm. The generator writes the computed 77.52.

## House rules

**Never rebuild the document from scratch.** The cover page and section
photographs cannot be reproduced from code.

**Never change** the cover page, header strip, footer, brand colours
(dark blue `#1F3864`, panel blue `#D9E2F3`), the 13 sections or their order, or
the signature block (Farhan / Sales Engineer / The New Doha Kitchen Equipment
Services W.L.L & Doha Cooling Trading & Solutions W.L.L).

**Reference numbers** run `QUT/DCTS/SQNNN/YYYY`. The last issued was
`QUT/DCTS/SQ072/2026`. Check the register before assuming the next number —
do not reuse one.

**Currency** is always QAR, written `QAR 46,800.00`, quoted as a lump sum
exclusive of VAT.

**Multiple rooms** are supported: add entries to `rooms` and the project table
grows a row each. When the rooms run on different machines, pass
`refrigeration` as a list — one entry per system, each with a `room` label.
Rows where the systems agree (brand, refrigerant) print once; rows that differ
(capacity) print one labelled line each. Coverage figures are then reported as summed totals across
all rooms rather than as a single arithmetic expression, and mixed panel
thicknesses print as `100 / 150 mm`. For a multi-room job where the client wants
a price per room, ask first — the BOQ carries one lump-sum grand total, so
splitting it means adding subtotal rows.

## Files

```
cold-room-quote/
├── SKILL.md
├── template/master.docx              frozen master — do not edit
├── scripts/
│   ├── generate.py                   spec JSON -> quotation .docx
│   └── number_to_words.py            QAR amount -> words
├── examples/
│   └── marza-group-chiller.json      reproduces QUT/DCTS/SQ072/2026 exactly
└── references/
    ├── spec-schema.md                every spec field
    ├── template-map.md               what lives where in the document
    └── pricing-guide.md              unit costs for estimating the total
```

## Related skills

`tndk-coldroom-quotation` is the earlier version of this, built on an older
master. This skill supersedes it — use this one for new quotations so every
cold room quote goes out in the same format.
