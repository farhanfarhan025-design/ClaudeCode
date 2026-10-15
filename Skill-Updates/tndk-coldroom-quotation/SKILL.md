---
name: tndk-coldroom-quotation
description: Generate TNDK cold room quotations using Farhan's saved template (The New Doha Kitchen Equipment Services W.L.L.). Use this skill whenever the user asks for a cold room quotation, cold storage quote, chiller quote, freezer quote, refrigeration quote, or mentions QUT/DCTS reference numbers, or wants to quote a client for cold storage / chiller / freezer rooms. Also use when the user says "make a quotation", "draft a quote", or "send a price" for any cold room project. The skill produces a polished, multi-page Word document with the standard 13-section TNDK structure (Panel / Door / Angles / Flooring / Refrigeration / Capacity / Control Panel / Scope / Exclusions / Pricing / Warranty / Delivery / Payment), preserving the branded cover page and corporate styling.
---

# TNDK Cold Room Quotation Generator

This skill produces a fully-formatted cold room quotation in Word format using Farhan's saved master template.

**Company context:** TNDK = The New Doha Kitchen Equipment Services W.L.L. (a division of Doha Cooling). All quotations are signed off by Farhan, Sales Engineer.

## How it works

The master template (`template/master.docx`) is a 10-page branded document containing:
- A full-bleed promotional cover page (image-based, do not modify)
- 13 numbered technical/commercial sections
- Branded header and footer on every page
- Promotional infographic images on the pricing page

The skill works by **doing precise find-and-replace on a copy of the master**, never rebuilding from scratch. This preserves all images, branding, fonts, and visual layout.

## When to use

- User asks for a cold room / chiller / freezer / refrigeration quotation
- User mentions a TNDK / DCTS reference number (QUT/DCTS/NNN/YYYY format)
- User provides client name, dimensions, and price for a cold storage project
- User says "use the saved cold room quotation format"

## Workflow

### Step 1: Gather the variable data

Before generating, confirm or ask for the following (defaults shown in italics):

**Client / Reference block:**
- Client name (e.g., "Mr. Suresh", "M/s. ABC Trading W.L.L.")
- Project / site address (e.g., "Industrial Area, Street 12")
- Contact person (e.g., "Mr. Khalid")
- Quotation reference number — *next number in the QUT/DCTS/NNN/YYYY series*
- Date — *today's date in "DD Month YYYY" format*
- Validity — *15 Days from quote date*

**Project description (per room):**
- Room type — Freezer / Chiller / Both
- Quantity
- Operating temperature (e.g., "+2°C to +8°C" for chiller, "−18°C to −22°C" for freezer)
- External dimensions (L × W × H in metres)
- Panel thickness (typically 100 mm; 80 mm for chillers, 100/150 mm for freezers)

**Technical sections** — recalculate based on dimensions:
- Wall coverage = 2(L×H) + 2(W×H)
- Ceiling coverage = L × W
- Floor coverage = L × W (only if floor included)
- Total panel quantity = sum of the above
- Internal volume = L × W × H

**Pricing:**
- Grand total in QAR (lump sum, excluding 5% VAT)
- Amount in words (auto-generated from the number)

If the user has already given enough data in the conversation (typical case), do **NOT** ask redundant clarifying questions — extract what's available and proceed. Only ask for genuinely missing fields.

### Step 2: Generate the quotation

Run the generator script:

```bash
python3 scripts/generate.py \
  --output /home/claude/quotation_output.docx \
  --client "Mr. Suresh" \
  --address "Doha, Qatar" \
  --contact "Mr. Suresh" \
  --ref "QUT/DCTS/067/2026" \
  --date "26 April 2026" \
  --validity "15 Days from quote date" \
  --room1-type "FREEZER ROOM" --room1-qty 1 --room1-temp "−18°C to −22°C" --room1-dims "2.35 × 2.0 × 2.40 m" --room1-panel "100 mm" \
  --room2-type "CHILLER" --room2-qty 1 --room2-temp "+2°C to +8°C" --room2-dims "4.5 × 3.5 × 3.5 m" --room2-panel "100 mm" \
  --total 59000 \
  --total-words "Qatari Riyals Fifty-Nine Thousand Only"
```

For full options including BOQ line item edits, panel/floor/volume recalculation, and per-section overrides, see `references/generator-options.md`.

### Step 3: Validate and present

After generation:

```bash
python3 /mnt/skills/public/docx/scripts/office/validate.py /home/claude/quotation_output.docx
```

If validation passes, copy to `/mnt/user-data/outputs/` and present to the user using the `present_files` tool.

If the user requests a PDF preview, also convert and present:

```bash
soffice --headless --convert-to pdf --outdir /mnt/user-data/outputs/ /mnt/user-data/outputs/quotation_output.docx
```

## Important rules

**Never rebuild the document from scratch.** The branded cover page and infographic images cannot be reproduced from code. Always start from `template/master.docx` and edit it.

**Never modify these elements:**
- The promotional cover page (page 1)
- The header/footer styling
- The brand colors (Dark Blue #1F3864)
- The font (Calibri throughout)
- The section structure or numbering (1-13 in fixed order)
- The promotional images on the pricing page

**Always update these elements per quote:**
- Reference number (QUT/DCTS/NNN/YYYY format)
- Date and validity
- TO block: Client name, address, contact person
- Project description table: room types, quantities, temperatures, dimensions, panel thickness
- Section 1 panel coverage figures (recalculate from dimensions)
- Section 4 flooring quantities (if floor included)
- Section 6 internal volume and heat load
- Section 10 BOQ descriptions (room dimensions, panel area)
- Grand Total amount
- Amount in words

**Reference number format:** QUT/DCTS/NNN/YYYY where NNN is sequential and YYYY is the current year. The next number after the master's `056/2026` would be `057/2026` etc.

**Currency:** Always QAR. Format with comma separator: `QAR 59,000.00`

**Signature block:** Always "Farhan / Sales Engineer / The New Doha Kitchen Equipment Services W.L.L & Doha Cooling Trading & Solutions W.L.L". Do not change.

## Per-room pricing

If the user wants per-room pricing breakdown (Chiller X + Freezer Y = Total), the BOQ section in the master uses a single "GRAND TOTAL" row. To split:

1. Update BOQ line items 1-6 to indicate which room each applies to
2. OR add per-room subtotal rows above the Grand Total

Discuss the preferred approach with the user before modifying the BOQ structure.

## Files in this skill

```
tndk-coldroom-quotation/
├── SKILL.md                      (this file)
├── template/
│   └── master.docx               (the master quotation template — DO NOT MODIFY)
├── scripts/
│   ├── generate.py               (main generator — runs find-and-replace)
│   └── number_to_words.py        (converts amount to QAR words)
└── references/
    ├── generator-options.md      (full CLI reference for the generator)
    ├── field-locations.md        (where each variable lives in the XML)
    └── pricing-guide.md          (typical pricing assumptions and material costs)
```

## Quick reference: typical pricing inputs

These are Farhan's standard unit costs (used to estimate, not for the final quote):

| Item | Unit | Cost (QAR) |
|---|---|---|
| Sandwich panel (100mm PUF) | per sqm | 115 |
| Cold room door (90×190) | each | 1,800 |
| Aluminum angles | per 6m piece | 55 |
| Chequered sheet + plywood (floor) | per pair | 350 |
| Chiller condensing unit + evaporator | set | 8,800 |
| Freezer condensing unit + evaporator | set | 6,400 |
| Control panel | each | 1,200 |
| Pipe + accessories | per system | 2,500 |
| Wiring | per system | 1,800 |
| LED lights | for 2 rooms | 500 |

Standard markup: 20-30% on top of (materials + 15% labour + transport).

For full pricing methodology, see `references/pricing-guide.md`.
