# Template map

What sits where inside `template/master.docx`, and which fields the generator
touches. Useful when the master is revised or a new field needs wiring up.

Page setup: A4 portrait (8.27 × 11.69 in), zero page margins — the layout is
carried entirely by full-width tables, which is why the cover image bleeds to
the edges. Font is Calibri throughout. Footer is `word/footer1.xml`.

Colours: `#1F3864` dark blue (section header bands, headings), `#D9E2F3` pale
blue (label column), `#2F5496` mid blue (table header rows), white text on the
dark bands.

## Document order

| # | Element | Generator |
|---|---|---|
| — | Cover image (image1.png, full bleed 8.27 × 11.70 in) | untouched |
| T0 | Brand strip: TNDK / address block | untouched |
| P | `QUOTATION` heading, centred, 16 pt, `#1F3864` | untouched |
| T1 | REFERENCE / DATE / VALIDITY | `reference`, `date`, `validity` |
| T2 | TO / FROM | `client.*`; FROM block untouched |
| P | `Subject:` line | `subject` (optional) |
| P | "Dear Sir, ..." intro | `intro` (optional) |
| T3 | Project description: ROOM TYPE / QTY / TEMPERATURE / EXTERNAL DIMENSIONS / PANEL THICKNESS | one row per `rooms[]`, cloned as needed |
| — | image2.png banner (7.46 × 2.91 in) | untouched |
| 1 | **PANEL DETAILS** + image3.png | thickness, wall/ceiling/floor coverage, total |
| 2 | **DOOR DETAILS** + image4.png | opening size, thickness, quantity |
| 3 | **ANGLES, SILICONE & ACCESSORIES** + image5.png | untouched (boilerplate) |
| 4 | **FLOORING DETAILS** + image6.jpeg | floor panel / plywood / chequered plate areas |
| 5 | **REFRIGERATION MACHINE DETAILS** + image7, image8 | `refrigeration.*` |
| 6 | **MACHINE CAPACITY (HEAT LOAD)** + image9, image10 + caption | volume, room temp, heat load, selected capacity |
| 7 | **CONTROL PANEL DETAILS** + image11 | untouched (boilerplate) |
| 8 | **SCOPE OF WORK** — 11 bullets | 4 size-dependent bullets rewritten |
| 9 | **EXCLUSIONS** — 10 bullets | untouched |
| 10 | **PRICING / BILL OF QUANTITIES** | 6 BOQ rows + GRAND TOTAL + amount in words + image12 |
| 11 | **WARRANTY** | untouched |
| 12 | **DELIVERY & WORK COMPLETION** + image13 | `delivery` patches named rows; image13 scaled to fit the page |
| 13 | **PAYMENT & COMMERCIAL TERMS** — 6 bullets | untouched |
| — | Closing paragraphs + signature block | untouched |

## Table lookup keys

Tables are found by the labels in their first column, not by index, so inserting
a row or table upstream doesn't break anything.

| Table | Lookup | Rows the generator writes |
|---|---|---|
| Reference | `"REFERENCE"` | row 1: ref, date, validity |
| Client | `"TO"` | row 1 col 0 |
| Project | `"ROOM TYPE"` | row 1..N |
| Panel | `"Panel Type"` + `"Wall Coverage"` | Panel Thickness, Wall/Ceiling/Floor Coverage, Total Panel Quantity |
| Door | `"Door Type"` | Clear Opening Size, Door Thickness, Quantity |
| Flooring | `"Insulated Floor Panel"` | Insulated Floor Panel, Plywood Layer, Top Finish |
| Refrigeration | `"System Type"` | System Type, Condensing Unit, Compressor Brand, Refrigerant, Evaporator (Air Cooler), Operating Temperature, Defrost |
| Capacity | `"Internal Volume"` | Internal Volume, Design Ambient, Design Room Temp., Estimated Heat Load, Selected Capacity |
| BOQ | `"SL#"` | rows 1..6 |
| Grand total | `"GRAND TOTAL (Lump Sum)"` | row 0, last cell |
| Delivery | `"Material Delivery"` | whichever rows `delivery` names |

The refrigeration and control-panel tables are three columns wide with
horizontally merged cells (label spans 1, value spans 2; the image caption row
spans 2 + 1). `row_cells()` de-duplicates merged cells so `cells[0]` is always
the label and `cells[-1]` the value.

## Scope-of-work bullets

Four bullets are regenerated because they restate quoted quantities. They are
matched by regex on their opening words:

- `Supply of ... sandwich panels for walls ...` → total panel sqm
- `Supply and installation of ... hinged cold room door ...` → door count and size
- `Supply and installation of insulated floor system ...` → panel thickness
- `Supply and installation of condensing unit ...` → number of sets

The other seven bullets are boilerplate and left alone.

## The service banner

image13 sits in a trailing row *inside* the delivery table, not in a paragraph
below it — worth knowing, because a search of body paragraphs will not find it.
The master sizes it 7.27 × 5.45 in, marginally taller than the space left under
section 12, so Word pushes it onto a page of its own and the quotation ends with
a mostly empty sheet. `fit_banner()` scales it to 4.4 in tall (5.87 in wide),
which pulls it back onto the section 11/12 page.

When resizing any image here, set `cx`/`cy` only on the `a:ext` inside `a:xfrm`.
The `a:ext` in an `a:extLst` takes a `uri` instead and rejects `cx`/`cy` —
writing them there produces a file Word will complain about.

## Editing the master

If the master is replaced, re-check:

1. `MASTER_INTRO` in `generate.py` must match the new intro paragraph exactly,
   otherwise the optional `intro` override silently does nothing.
2. The lookup labels above must still exist, spelled identically — including
   the trailing period in `Design Room Temp.` and the `(Lump Sum)` suffix.
3. Re-run the regression: regenerating `examples/marza-group-chiller.json`
   should still produce the reference document.

## Formatting safety

Text is written into the first run of a paragraph and surplus runs are removed,
so the run's font, size and colour carry over. Mixed-format lines (bold blue
`Amount in Words:` followed by black text) use a run-spanning replace that
edits only the matched span. Nothing rewrites `styles.xml`, `numbering.xml`,
the theme or the images.
