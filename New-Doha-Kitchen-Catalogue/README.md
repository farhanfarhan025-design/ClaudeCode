# The New Doha Kitchen — Product Catalogue

Product data sheets in TNDK branding: A4, dark blue `#1F3864`, gold `#C9A24E`, Calibri.
They are built with the Designer layout system from a JSON config.

## Data sheets

| Product | PDF | Source |
|---|---|---|
| Sliding Door Freezer | `datasheets/sliding-door-freezer/TNDK-Datasheet-Sliding-Door-Freezer.pdf` | Supplier data sheet (Dec 2021), rebranded; figures page uses the photo supplied 22 Sep 2026 |
| Hinged Door | `datasheets/hinged-door/TNDK-Datasheet-Hinged-Door.pdf` | Supplier data sheet (Jan 2021), rebranded; page 2 figure uses the photo supplied 22 Sep 2026. Strength units copied as printed (kg/m²), to confirm with supplier |

## Folder layout per data sheet

- `catalogue.json` — all content. Edit this, not the HTML.
- `images/` — photographs referenced by the config.
- `catalogue.html` — the rendered page source behind the PDF.
- `preview/` — one PNG per page, checked before delivery.

## Rebuilding

```bash
python3 <designer-skill>/scripts/build_catalogue.py \
    --config datasheets/<product>/catalogue.json \
    --outdir datasheets/<product>/out/
```

The PDF lands in `out/catalogue.pdf`. Rename it to the `TNDK-Datasheet-<Product>.pdf` pattern.
Technical figures are transcribed from the supplier sheet. Check any change against it.
