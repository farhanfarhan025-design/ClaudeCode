---
name: tndk-lpo
description: Generate TNDK Local Purchase Orders (LPOs) for vendors using Farhan's saved style — dark blue header band, gold "LOCAL PURCHASE ORDER" badge, vendor information block, line item table with sub-total/discount/grand total, italic notes, and the "computer generated document" callout. Use this skill whenever the user asks for an LPO, local purchase order, vendor PO, or just "PO", or mentions an LPO reference number (LPO-NNN/YYYY format), or wants to issue a purchase order to a supplier (especially for cold room components, refrigeration parts, insulated panels, doors, condensing units, evaporators, or similar HVAC/cold storage materials). Also trigger when the user says "make a PO", "draft a PO", "issue an LPO to [vendor]", "create a purchase order for [vendor]", or pastes vendor quotation details and asks for a PO. Produces a polished single-page PDF matching Farhan's IDIF/2026 sample exactly.
---

# TNDK Local Purchase Order Generator

This skill produces a polished single-page LPO PDF in Farhan's saved TNDK / DCTS style — the same format as `LPO-189/2026 (IDIF)`.

**Company context:** Farhan issues POs from one of two letterheads:
- **TNDK** — *The New Doha Kitchen Company* (default; Farhan's preferred branding)
- **DCTS** — *Doha Cooling & Trading Solutions W.L.L.* with "The New Doha Kitchen Equipment Services" as subtitle (legacy header used on the IDIF sample)

The user picks per PO via the `profile` field.

## How it works

The script renders a Jinja-style HTML template (`assets/lpo_template.html`) into a single-page A4 PDF using `playwright` (Chromium). The PDF matches the saved sample down to the dark blue (`#1F3864`) and gold (`#C9A24E`) accents.

The skill is intentionally **data-driven**: pass a JSON config with vendor, line items, and totals, and out comes a finished PO. Sub-total and grand total are auto-computed; amount-in-words is auto-generated from the grand total and currency.

## When to use

- User asks to issue / draft / create an LPO or purchase order
- User pastes a vendor quotation and asks "make this into a PO"
- User mentions an `LPO-NNN/YYYY` reference number
- User wants to send a PO to a vendor (any product — cold room panels, doors, refrigeration units, kitchen equipment, etc.)
- User says "use the saved LPO format" or "same format as IDIF"

## Workflow

### Step 1: Gather the variable data

Collect (or extract from the conversation) the following. Don't re-ask for things the user has already given — extract from context.

**Header / meta**
- Profile: `tndk` (default) or `dcts` — ask only if Farhan hasn't said which letterhead
- PO number — *next number in the LPO-NNN/YYYY series*
- PO date — *today's date in `DD-MM-YYYY` format*
- Vendor's quotation reference (the `REF QUOTE` field) — optional
- Currency — *QAR by default; SR for Saudi vendors; AED for UAE, etc.*

**Vendor block**
- Vendor company name + country (e.g. "Insulated Doors Industrial Factory (IDIF) – Saudi Arabia")
- Contact person + title (e.g. "Eng. Abdulgader Hasrat | Project Manager")
- Mobile, website, email (any combination — leave any out that you don't have)
- Payment terms (e.g. "100% Advance Payment", "30% advance, 70% on delivery")
- Delivery terms (e.g. "1–2 weeks from receiving PO and advance payment")

**Line items** — one entry per product:
- Description (bold title in the cell)
- Specs (optional bullet list shown beneath the title)
- Variant (optional — used by the IDIF sample to distinguish RHS vs LHS doors)
- Unit (Nos / Sqm / Lm / Kg / Set / Lot ...)
- Qty
- Unit price

**Optional rows after the items**
- Delivery amount + label (e.g. "Delivery to Doha (1 Truck)")
- Discount (positive number; rendered as `(3,100.00)` in parentheses)

**Notes** — usually 3–5 numbered italic lines. Standard final note: *"All materials remain vendor property until payment is fully settled."*

### Step 2: Generate the LPO

Build a JSON config in the workspace, then run the generator:

```bash
python3 /path/to/skill/scripts/generate_lpo.py \
  --config /home/claude/po_config.json \
  --output /home/claude/lpo_output.pdf
```

The schema is documented in `references/json_schema.md` — read it whenever you need to confirm a field name or what's required vs optional.

For one-off single-item POs, you can skip the JSON config and pass everything as CLI flags (see `references/cli_options.md`).

### Step 3: Validate and present

Open the PDF (or convert to image and inspect) to spot-check before delivering it. In particular check:
- **PO number, date, currency** all correct
- **Sub-total and grand total** match the user's intent (auto-computed; verify the math)
- **Amount in words** reads naturally
- **Single page** — if it spilled to a 2nd page, trim a long spec list or shorten notes
- **Vendor block** has the right contact info

Then copy to `/mnt/user-data/outputs/` and present with the `present_files` tool.

```bash
cp /home/claude/lpo_output.pdf /mnt/user-data/outputs/LPO_<vendor>_<topic>.pdf
```

The output filename should be human-readable — match the IDIF sample's naming: `LPO_IDIF_FreezingDoors.pdf`, `LPO_AlWatania_Panels.pdf`, etc.

## Important rules

**Default to TNDK profile** unless Farhan specifies otherwise — his saved instructions say to use "The New Doha Kitchen Company" branding by default and avoid the "Doha Cooling" header. The DCTS profile exists for cases where he wants to match a legacy PO (like the IDIF one) or a vendor that knows the old name.

**Default currency is QAR.** Switch to SR/SAR for Saudi Arabian vendors, AED for UAE, etc. The currency code is shown in the table headers (`UNIT PRICE (SR)`, `TOTAL (SR)`) and used to build the amount-in-words.

**Reference number format:** `LPO-NNN/YYYY` where NNN is sequential and YYYY is the current year. The next number after `LPO-189/2026` is `LPO-190/2026`. Ask Farhan for the next number if it's not obvious from context.

**Numbers are formatted with thousands separators and 2 decimal places** automatically — pass them as raw numbers (`6600.00`, not `"6,600.00"`).

**Discount is entered as a positive number** — the template renders it as `(3,100.00)` in parentheses, conventional accounting style.

**Never modify these elements:**
- The dark blue (#1F3864) and gold (#C9A24E) colors
- The "LOCAL PURCHASE ORDER" badge in the top-right
- The "*** COMPUTER GENERATED DOCUMENT ***" callout above the footer
- The footer text "This is a computer-generated document and does not require a physical signature."

**No physical signature block.** Per Farhan's saved instructions, all TNDK POs are computer-generated and the callout replaces a signature block.

## Quick reference: typical PO scenarios

| Scenario | Profile | Currency | Notes |
|---|---|---|---|
| Local Qatar vendor | `tndk` | QAR | Standard payment terms vary; include VAT note if applicable |
| Saudi import (IDIF, etc.) | `dcts` or `tndk` | SR | Usually 100% advance; delivery to Doha included |
| UAE import | `tndk` | AED | Often 50/50 advance/delivery |
| US/EU import | `tndk` | USD/EUR | Add letter-of-credit note if relevant |

## Files in this skill

```
tndk-lpo/
├── SKILL.md                    (this file)
├── scripts/
│   └── generate_lpo.py         (main generator — JSON or CLI args → PDF)
├── assets/
│   ├── lpo_template.html       (the HTML template with all the styling)
│   ├── example_idif.json       (reproduces the uploaded IDIF sample exactly)
│   └── example_tndk.json       (a TNDK-profile multi-item example)
└── references/
    └── json_schema.md          (full JSON config schema with field-by-field notes)
```

## Quick start

To reproduce Farhan's IDIF sample exactly:

```bash
python3 scripts/generate_lpo.py \
  --config assets/example_idif.json \
  --output /home/claude/lpo_test.pdf
```

To generate a fresh TNDK PO from scratch, copy `assets/example_tndk.json`, edit the fields, and run the same command.
