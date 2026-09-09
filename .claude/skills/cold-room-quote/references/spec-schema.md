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
| `phone` | no | `"+974 5503 3590"` — printed as `Tel: ...` |
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
| `panel_included` | no | `true` | `false` for an existing room being cooled — no walls, ceiling or floor counted, and the project table prints "Not applicable" for its thickness |
| `glass_front` | no | `false` | `true` drops the front face from the wall panel area — for a display chiller closed by a glass door |

**Dimensions should be strings.** JSON cannot hold the trailing zero in `2.40`,
and the house style writes `2.40`, not `2.4`. Numbers still work — they are
formatted to at most two decimals — but strings are reproduced exactly.

Note the minus sign in freezer temperatures is U+2212 (`−`), matching the master.

## `door`

| Field | Default | Notes |
|---|---|---|
| `type` | `"hinged"` | `"sliding"` relabels the hinges row as Track & Rollers; `"glass"` describes a frameless glass door and relabels the row Hinge Type. Both reword the scope and BOQ |
| `image` | — | path to a photo of the door being quoted; replaces the section 2 photograph, resized to the picture's aspect ratio |
| `glass` | — | wording for a glass door: `thickness`, `frame`, `gasket`, `handle`, `hinges`, `hardware` |
| `qty` | `1` | spelled out in scope and BOQ ("three (3) No.") |
| `opening_text` | — | verbatim Clear Opening Size row, for a job with more than one door size |
| `quantity_text` | — | verbatim Quantity row |
| `width_mm` | `900` | clear opening |
| `height_mm` | `1900` | clear opening |

## `refrigeration`

All optional — omit the block entirely to leave section 5 as the master has it.

May be a **single object** (one system) or a **list of objects** (one per room,
e.g. a chiller and a freezer on different machines). Each entry in a list may
carry a `room` label, used to tag its line. Rows where every entry agrees print
once without labels; rows that differ print one labelled line per system.

| Field | Default | Example |
|---|---|---|
| `sets` | `1` | number of split systems |
| `condensing_unit` | — | `"BITZER LH64/2DES-3Y"` |
| `room` | — | label for this system in a multi-system quote, e.g. `"Chiller"` |
| `compressor_brand` | first word of `condensing_unit` | stripped from the model when printing "model ..." |
| `cu_type` | `"semi-hermetic"` | compressor/unit type; `""` omits the claim when the type is unknown |
| `cu_origin` | — | omitted when not given |
| `evaporator` | — | `"HSE302-1DWEO"` |
| `evap_origin` | — | omitted when not given |
| `evap_note` | — | extra clause after the evaporator model, e.g. `"HC refrigerant compatible"` |
| `refrigerant` | — | `"R404A"` |
| `capacity_kw` | — | `5.60` — cooling capacity |
| `capacity_label` | from `capacity_kw` | quote the capacity verbatim when a unit is sold by horsepower, e.g. `"15 HP"` |
| `power_input_kw` | — | `3.25` |
| `current_a` | — | `6.05` |
| `power_supply` | `"400V-3-50Hz"` | |
| `sst` | — | saturated suction temp for the selection note; omitted when not given |
| `ambient` | — | Doha design ambient, e.g. `"46°C"` |
| `selection_basis` | compressor brand | whose selection software was used |
| `defrost` | — | overrides the defrost row |
| `condensing_unit_text` | — | verbatim Condensing Unit row, for a machine with no model — e.g. `"1 HP condensing unit — make and model as per availability"` |
| `compressor_text` | — | verbatim Compressor Brand row |
| `evaporator_text` | — | verbatim Evaporator row |

## Rooms without a floor

Set `floor_included: false` and the quote adjusts throughout: the panel table
reports "Not included in scope", section 4 says so on every row, the BOQ drops
its flooring line entirely, the scope bullet states the room is erected on the
client's existing floor, and the opening paragraph stops promising insulated
flooring.

## `flooring`

The build-up laid over the insulated floor panel. Defaults to the house
specification; both keys are written verbatim wherever the floor is described.

| Field | Default | Example |
|---|---|---|
| `plywood` | `"18 mm"` | marine-grade plywood thickness |
| `plate` | `"1.5 mm"` | MS chequered plate thickness — 1.5 mm is the house standard |

The figures appear in three places — the flooring table, the scope bullet and
the BOQ line — and this keeps them in step.

The plate is **1.5 mm as standard**. The reference quotation predates that and
pins 3 mm in its own spec, so it still reproduces its source document.

## Extra pictures and row overrides

| Field | Effect |
|---|---|
| `images` | list of `{after, path, caption, height_in, space_before_in}` — inserts a photograph after the paragraph or table containing `after`, with an italic caption beneath; `space_before_in` pushes it down the page, to sit it in the middle of a short section rather than tight under the last line |
| `resize` | list of `{after, before, height_in}` — scales a master photograph found between those two pieces of text |
| `replace` | list of `{after, before, path, height_in}` — swaps a master photograph for a supplied one, when the master's illustration contradicts what is quoted |
| `remove` | list of `{after, before}` — deletes a master photograph outright, for when it contradicts the offer and there is nothing to swap in |
| `panel_rows` | `{row label: value}` written verbatim into the section 1 table |
| `flooring_rows` | `{row label: value}` written verbatim into the section 4 table |
| `door_rows` | `{row label: value}` written verbatim into the section 2 table |
| `control_rows` | `{row label: value}` written verbatim into the section 7 table |
| `machine_rows` | `{row label: value}` written verbatim into the section 5 table |
| `capacity_rows` | `{row label: value}` written verbatim into the section 6 table |

The section photographs carry their captions burnt into the artwork — the door
illustration is labelled `SIZE: 90 x 190 cm`, the panel illustration says
`PU INSULATED` and lists polyurethane in its spec box. On a job quoting a
different door size or a PIR core those pictures contradict the table beneath
them, so `remove` them rather than leave the client two answers.

Adding a picture to a section only works if something on that page gives up
room, and the master's own section photograph is usually the thing with slack —
so `images` and `resize` are generally used together.

## Optional overrides

| Field | Effect |
|---|---|
| `validity` | defaults to `"15 Days from quote date"` |
| `subject` | replaces the text after `Subject:` |
| `intro` | replaces the "Dear Sir, ..." paragraph |
| `total_words` | overrides the auto-generated amount in words |
| `boq` | array of `{"description": "...", "amount": 1234}` replacing the six default lines; `amount` may be omitted for a lump-sum quote |
| `delivery` | object of `{"<row label>": "<value>"}` patching section 12, e.g. `{"Installation Period": "10 – 14 working days for civil-ready site"}` |
| `system_type` | replaces the System Type row, for a job that mixes new and re-used plant |
| `scope` | replace individual scope bullets by key: `panels`, `doors`, `floor`, `machines` |
| `sets` | number of `refrigeration` entries; set it when one machine type is repeated, e.g. 2 identical systems from one entry |
| `list_spacing_pt` | space after each numbered bullet, in points; the master leaves 2 pt, and `0` reclaims most of an inch across the scope and exclusions when the last few points spill onto their own page |
| `control_panel_height_in` | height of the two section 7 photographs, in inches; they share a page with the scope and exclusions, so trimming them pulls spilled bullets back once the lists are already tight |
| `project_banner_height_in` | height of the installation banner under the project table; a quote listing several rooms pushes it off that page |
| `pricing_banner_height_in` | height of the banner under the amount in words; a long bill of quantities pushes it off the pricing page |
| `schematic_height_in` | height of the section 6 refrigeration schematic, default `1.2`; `0` keeps the master's 1.52 in, which pushes it onto a page of its own |
| `banner_height_in` | height of the service banner under section 12, default `4.0`; `0` keeps the master's 5.45 in, which strands it on a page of its own |

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
