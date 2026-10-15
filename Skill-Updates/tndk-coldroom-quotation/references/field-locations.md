# Field Locations in Master Template

This document maps each variable field to its location in the master `template/master.docx`. Useful for debugging when text replacement fails or when extending the generator.

## Header / Reference block (page 2)

| Field | Master value | Location | Notes |
|-------|--------------|----------|-------|
| Reference | `QUT/DCTS/056/2026` | Reference column | Single contiguous run |
| Date | `25 April 2026` | Date column | Single contiguous run |
| Validity | `15 Days from quote date` | Validity column | Single contiguous run |

## TO block (page 2)

The TO block has 4 lines:
```
M/s. [Client Name]
[Project / Site Address]
Doha, Qatar
Attn: [Contact Person]
```

| Field | Placeholder | Notes |
|-------|-------------|-------|
| Client name | `[Client Name]` | Bracketed placeholder |
| Address | `[Project / Site Address]` | Bracketed placeholder. **Don't pass `Doha, Qatar` here** — the master has that line below as a fixed constant. The generator handles this automatically. |
| Contact | `[Contact Person]` | Bracketed placeholder |

## Project description table (page 2)

```
| ROOM TYPE     | QTY | TEMPERATURE | EXTERNAL DIMENSIONS | PANEL THICKNESS |
| FREEZER ROOM  | 1   | (empty)     | (empty)             | (empty)         |
| CHILLER       | 1   | (empty)     | (empty)             | (empty)         |
```

The Type and Qty columns have content; the other three columns are empty `<w:t></w:t>` runs that need to be filled in. **The current generator does NOT fill these** — the user must edit in Word, or the generator must be extended to inject text into the empty `<w:t>` elements (more complex than find-and-replace).

## Section 1 - Panel Details

| Field | Master value | Run boundaries |
|-------|--------------|----------------|
| Wall coverage | `2 × (4.0 × 2.5) + 2 × (5.0 × 2.5) = 45.00 sqm` | Single run |
| Ceiling coverage | `4.0 × 5.0 = 20.00 sqm` | Single run |
| Floor coverage | `4.0 × 5.0 = 20.00 sqm` | Single run (covered by same replacement as ceiling) |
| Total panel quantity | `85.00 sqm` | Single run |

## Section 4 - Flooring Details

Three rows mention `20.00 sqm`:
- `100 mm PUF panel, same specification as wall panels — 20.00 sqm` ✓ contiguous
- `18 mm Marine-grade plywood laid over the floor panel — 20.00 sqm` ✓ contiguous
- `3 mm Mild Steel Chequered (Checkered) Plate, slip-resistant — 20.00 sqm` ⚠️ Word's spell-checker put "Chequered" in its own run; replacement uses ` (Checkered) Plate, slip-resistant — 20.00 sqm` (skipping "3 mm Mild Steel Chequered" which is split)

## Section 6 - Machine Capacity

| Field | Master value | Run boundaries |
|-------|--------------|----------------|
| Internal Volume | `4.0 × 5.0 × 2.5 = 50 m³` | ⚠️ "m³" is in a separate run (superscript style). Replacement uses `4.0 × 5.0 × 2.5 = 50 ` (trailing space, no `m³`) |

## Section 10 - BOQ

Item 1 description (single contiguous run):
```
Supply, fabrication & installation of cold storage room — internal size 4.0 m (L) × 5.0 m (W) × 2.5 m (H) — Internal Volume: 50 m³, complete with 100 mm PUF sandwich panels for walls, ceiling and floor (total panel area: 85.00 sqm), all aluminum coving, corner angles, silicone sealing, fasteners and accessories.
```

The whole sentence is in one run. The `m³` here is also in that single run (different from §6).

Item 3 description (split run):
- `Supply & installation of insulated floor system: 100 mm PUF floor panel + 18 mm marine plywood + 3 mm MS chequered plate.` — first run, ends with period
- `chequered plate (20.00 sqm).` — wait, actually two text fragments

Investigation showed: the text `chequered plate (20.00 sqm)` is one contiguous chunk that exists separately from "3 mm MS chequered plate." (the period-terminated version). Use the contiguous chunk for replacement.

## Grand Total

| Field | Master value | Notes |
|-------|--------------|-------|
| Total amount | `QAR 51,450.00` | Single run |

## Amount in Words (page 8)

The line is split across **two runs with different formatting**:
- Run 1 (bold): `Amount in Words: ` then ` Qatari Riyals `
- Run 2 (bold + italic): `Fifty One Thousand Four Hundred Fifty Only.`

Because the formatting differs, the runs cannot be merged. Replace only the inner italic portion: `Fifty One Thousand Four Hundred Fifty Only.` → new amount-in-words. The "Qatari Riyals " prefix from the master is preserved automatically.

## Signature block (last page)

| Field | Value | Notes |
|-------|-------|-------|
| Name | `Farhan` | Constant |
| Title | `Sales Engineer` | Constant |
| Company | `The New Doha Kitchen Equipment Services W.L.L & Doha Cooling Trading & Solutions W.L.L` | Constant |
| Email | `farhan@dctsqatar.com` | Constant |

These are **never modified** by the generator.

## Header / Footer (every page except cover)

| Element | Value | Notes |
|---------|-------|-------|
| Header left | `TNDK` | Constant |
| Header right | `The New Doha Kitchen Equipment Services W.L.L. / P.O. Box 80247, Doha – Qatar / farhan@dctsqatar.com` | Constant |
| Footer | `The New Doha Kitchen Equipment Services W.L.L. \| P.O. Box 80247, Doha – Qatar \| farhan@dctsqatar.com / Page X of Y` | Auto-paginated |

## Cover page (page 1)

The cover is a full-bleed image insertion. **Do not modify.** It contains:
- TNDK logo
- Hero photo of cold room installation
- Marketing copy ("COLD ROOM & REFRIGERATION SYSTEMS")
- 4 product photos (compressor / fans / panels / control panel)
- 5 benefit icons
- Footer with website / mobile / email / QR code

The cover is preserved verbatim in every quotation.
