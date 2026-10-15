# CLI options for `generate_lpo.py`

For most POs (more than one line item, or any with specs/variants), pass a JSON config:

```bash
python3 generate_lpo.py --config po.json --output po.pdf
```

For quick single-item POs, you can skip the JSON file and pass everything as flags.

## All flags

```
Required:
  --output PATH               Output PDF path

Identification:
  --po-number STRING          e.g. "LPO-190/2026"  (required if no --config)
  --po-date STRING            e.g. "27-04-2026"   (required if no --config)
  --ref-quote STRING          Vendor's quote reference

Branding:
  --profile {tndk,dcts}       Header style. Default: tndk
  --company-name STRING       Override company name in header
  --company-subtitle STRING   Override company subtitle

Vendor:
  --vendor STRING             Required vendor name
  --contact-person STRING     "Name | Title"
  --mobile STRING
  --website STRING
  --email STRING
  --payment-terms STRING
  --delivery-terms STRING

Currency / amounts:
  --currency STRING           QAR (default), SR, SAR, AED, USD, EUR, ...

Line items (repeatable):
  --item "DESC|UNIT|QTY|UNIT_PRICE[|TOTAL]"
                              Pipe-separated. Repeat for multiple items.
                              No specs or variants supported via CLI — use --config for those.

Extras:
  --delivery-amount NUMBER    e.g. 6500.00
  --delivery-label STRING     e.g. "Delivery to Doha (1 Truck)"
  --discount NUMBER           Positive number; rendered as (X,XXX.00)
  --note STRING               Repeatable; numbered italic notes

Misc:
  --keep-html                 Save the intermediate HTML next to the PDF (debugging)
```

## Example

```bash
python3 generate_lpo.py \
  --output /home/claude/lpo_quickpo.pdf \
  --profile tndk \
  --po-number "LPO-191/2026" \
  --po-date "27-04-2026" \
  --vendor "Qatar Refrigeration Trading W.L.L." \
  --contact-person "Mr. Ahmed Al-Ansari | Sales" \
  --mobile "+974 5544 7788" \
  --email "ahmed@qrt.com.qa" \
  --payment-terms "30% advance, 70% on delivery" \
  --delivery-terms "Within 5 working days" \
  --currency "QAR" \
  --item "Bitzer condensing unit 5HP — Model 4FE-25Y|Set|2|14500|29000" \
  --item "Cu-Al evaporator 12kW|Nos|2|3800|7600" \
  --delivery-amount 500 \
  --delivery-label "Delivery & unloading at site" \
  --note "Prices inclusive of all materials and standard transport." \
  --note "5% VAT excluded." \
  --note "All materials remain vendor property until payment is fully settled."
```

## CLI vs JSON — when to use which?

**Use CLI flags** for:
- Quick one-off POs with 1–3 line items
- POs without specs / variants (the `--item` flag doesn't support those)

**Use JSON** for:
- Anything with specs (the bullet list under each line description)
- Anything with variants (RHS / LHS / model A vs model B)
- 4+ line items (CLI gets unwieldy)
- Anything you'll re-run with edits — it's much easier to tweak a JSON file than a long shell command

When in doubt, just write the JSON. Copy `assets/example_tndk.json` as a starting template.

## Mixing both

CLI flags override JSON values, so you can use the JSON as a base and tweak per-run:

```bash
python3 generate_lpo.py \
  --config base.json \
  --po-number "LPO-200/2026" \
  --po-date "01-05-2026" \
  --output revised.pdf
```

Useful for revisions where only the PO number / date changes.
