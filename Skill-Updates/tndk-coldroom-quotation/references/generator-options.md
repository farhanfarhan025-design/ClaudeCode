# Generator CLI Options

Full command-line reference for `scripts/generate.py`.

## Synopsis

```bash
python3 scripts/generate.py --output PATH --client NAME --ref REF --date DATE \
    --total AMOUNT --total-words WORDS [other options]
```

## Required arguments

| Flag | Description | Example |
|------|-------------|---------|
| `--output` | Output .docx file path | `/tmp/quote.docx` |
| `--client` | Client name | `"Mr. Suresh"` or `"M/s. ABC Trading W.L.L."` |
| `--ref` | Reference number (QUT/DCTS/NNN/YYYY) | `"QUT/DCTS/067/2026"` |
| `--date` | Quote date (DD Month YYYY) | `"26 April 2026"` |
| `--total` | Grand total in QAR (number) | `59000` |
| `--total-words` | Amount written out (without "Qatari Riyals" prefix) | `"Fifty-Nine Thousand Only"` |

## Optional arguments

### Client / Reference block

| Flag | Default | Description |
|------|---------|-------------|
| `--address` | `Doha, Qatar` | Project / site address. If `Doha, Qatar`, leaves the master's existing line in place to avoid duplication |
| `--contact` | (uses `--client`) | Contact person name |
| `--validity` | `15 Days from quote date` | Quotation validity period |
| `--subject` | Standard subject | Custom subject line |

### Room descriptions

The master template includes two rooms — a Freezer (room 1) and a Chiller (room 2). Section 1, 4, 6 and the BOQ are calculated using the chiller dimensions in the master.

| Flag | Default | Description |
|------|---------|-------------|
| `--room1-type` | `FREEZER ROOM` | Type label for room 1 |
| `--room1-qty` | `1` | Quantity |
| `--room1-temp` | (empty) | Operating temperature, e.g., `"−18°C to −22°C"` |
| `--room1-dims` | (empty) | External dimensions: `"L × W × H m"` (e.g., `"2.35 × 2.0 × 2.40 m"`) |
| `--room1-panel` | `100 mm` | Panel thickness |
| `--room2-type` | `CHILLER` | Type label for room 2 |
| `--room2-qty` | `1` | Quantity |
| `--room2-temp` | (empty) | Operating temperature, e.g., `"+2°C to +8°C"` |
| `--room2-dims` | (empty) | External dimensions |
| `--room2-panel` | `100 mm` | Panel thickness |

### Calculation control

| Flag | Description |
|------|-------------|
| `--use-room2-for-section1` | Use room 2 dimensions to recalculate section 1, 4, 6 panel areas (default: prefer room 2 if dims given) |
| `--keep-master-figures` | Keep the master's panel/volume figures verbatim (don't recalculate) |

If neither room provides dimensions, the master's defaults (4.0 × 5.0 × 2.5 m / 50 m³ / 85.00 sqm) remain.

## What gets recalculated from room dimensions

When room dimensions are provided, the following figures recalculate automatically:

| Location | Master value (4.0 × 5.0 × 2.5) | Calculated for new (L × W × H) |
|----------|-------------------------------|-------------------------------|
| §1 Wall coverage | `2 × (4.0 × 2.5) + 2 × (5.0 × 2.5) = 45.00 sqm` | `2(L×H) + 2(W×H)` |
| §1 Ceiling coverage | `4.0 × 5.0 = 20.00 sqm` | `L × W` |
| §1 Total panel | `85.00 sqm` | `walls + ceiling + floor` |
| §4 Floor panel area | `20.00 sqm` (×3) | `L × W` |
| §6 Internal volume | `4.0 × 5.0 × 2.5 = 50 m³` | `L × W × H` |
| §10 Item 1 dimensions | `4.0 m (L) × 5.0 m (W) × 2.5 m (H)` | new dims |
| §10 Item 1 volume | `50 m³` | `L × W × H` |
| §10 Item 1 panel area | `85.00 sqm` | total |
| §10 Item 3 floor area | `20.00 sqm` | `L × W` |

## Known limitations

**Project description table at the top of page 2** (TYPE / QTY / TEMP / DIMENSIONS / PANEL THICKNESS) — the master has empty cells for QTY, TEMPERATURE, EXTERNAL DIMENSIONS, PANEL THICKNESS that the generator does not currently fill. After running the generator, open the file in Word and fill these cells manually, OR use `scripts/fill_room_table.py` (if available) to inject values.

**Per-room pricing** — the master uses a single GRAND TOTAL row. To split prices per room (e.g., Chiller 32,500 + Freezer 26,500), edit the BOQ table in Word after generating, or modify the master template to add per-room subtotal rows.

## Examples

### Single chiller room
```bash
python3 scripts/generate.py \
    --output /tmp/chiller_only.docx \
    --client "Mr. Ahmed" \
    --ref "QUT/DCTS/068/2026" \
    --date "26 April 2026" \
    --total 35000 \
    --total-words "Thirty-Five Thousand Only" \
    --room1-type "CHILLER" \
    --room1-temp "+2°C to +8°C" \
    --room1-dims "5.0 × 4.0 × 3.0 m"
```

### Freezer + Chiller (matches Mr. Suresh quote)
```bash
python3 scripts/generate.py \
    --output /tmp/suresh.docx \
    --client "Mr. Suresh" \
    --ref "QUT/DCTS/067/2026" \
    --date "26 April 2026" \
    --total 59000 \
    --total-words "Fifty-Nine Thousand Only" \
    --room1-dims "2.35 × 2.0 × 2.40 m" \
    --room1-temp "−18°C to −22°C" \
    --room2-dims "4.5 × 3.5 × 3.5 m" \
    --room2-temp "+2°C to +8°C"
```

### Keep master figures (just update header/total)
```bash
python3 scripts/generate.py \
    --output /tmp/quick.docx \
    --client "M/s. XYZ Trading W.L.L." \
    --ref "QUT/DCTS/070/2026" \
    --date "26 April 2026" \
    --total 51450 \
    --total-words "Fifty-One Thousand Four Hundred Fifty Only" \
    --keep-master-figures
```
