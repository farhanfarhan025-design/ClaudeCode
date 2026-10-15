# LPO JSON config schema

This is the full schema for the JSON file passed to `generate_lpo.py --config`.

```jsonc
{
  // ===== Branding =====
  "profile": "tndk",                  // "tndk" (default) or "dcts" — controls header
                                      //   "tndk" → "THE NEW DOHA KITCHEN COMPANY" (no subtitle)
                                      //   "dcts" → "DOHA COOLING & TRADING SOLUTIONS W.L.L"
                                      //            with "The New Doha Kitchen Equipment Services" as subtitle
  "company_name":     "...",          // optional — override profile's company name
  "company_subtitle": "...",          // optional — override profile's subtitle
  "company_address":  "...",          // optional — override the standard P.O. Box address line
  "footer_company":   "...",          // optional — override the company name shown in the footer

  // ===== PO meta =====
  "po_number": "LPO-189/2026",        // required
  "po_date":   "20-04-2026",          // required — any human-readable format, kept as-is
  "ref_quote": "20-0001-10000460",    // optional — vendor's quotation reference

  // ===== Vendor =====
  "vendor":         "Insulated Doors Industrial Factory (IDIF) – Saudi Arabia",  // required
  "contact_person": "Eng. Abdulgader Hasrat | Project Manager",
  "mobile":         "+966 536 000 319",
  "website":        "www.idif-sa.com",
  "email":          "info@idif-sa.com",
  "contact_line":   "Mobile: ... | Website: ... | Email: ...",  // optional — overrides
                                                                // the auto-built mobile/website/email line
  "payment_terms":  "100% Advance Payment",
  "delivery_terms": "1–2 weeks from receiving PO and advance payment | Delivered to Doha (1 Truck included)",

  // ===== Currency =====
  "currency": "QAR",                  // QAR (default), SR, SAR, AED, USD, EUR, OMR, BHD, KWD, INR
                                      // Used in the table headers and amount-in-words

  // ===== Line items =====
  "items": [
    {
      "description": "Supply Freezer Sliding Door 2000 W × 3000 H",   // required
      "specs": [                                                       // optional — bullets under the title
        "PPGI Sheet thickness 0.5MM",
        "PVC frame thickness 10CM",
        "Leaf thickness 92MM",
        "With heater",
        "Italy (MTH Accessories)"
      ],
      "variant":    "Right Hand Side (RHS)",   // optional — italic line under specs
      "unit":       "Nos",                     // required — Nos / Sqm / Lm / Kg / Set / Lot ...
      "qty":        8,                         // required
      "unit_price": 6600.00,                   // required (in the chosen currency)
      "total":      52800.00                   // optional — auto-computed if omitted
    }
  ],

  // ===== Optional rows after the items =====
  "delivery_amount": 6500.00,                  // omit if no separate delivery line
  "delivery_label":  "Delivery to Doha (1 Truck)",   // default: "Delivery to Doha"
  "discount":        3100.00,                  // omit if no discount

  // ===== Totals =====
  // Both auto-computed; supply only when overriding.
  "subtotal":     79100.00,
  "grand_total":  76000.00,

  // ===== Amount in words =====
  // Auto-generated from grand_total + currency. Override only when needed
  // (e.g. for unusual phrasing).
  "amount_words": "Seventy-Six Thousand Saudi Riyals Only (SR 76,000.00)",

  // ===== Notes =====
  "notes": [
    "Prices are in Saudi Riyals (SR) as per vendor quotation ref: 20-0001-10000460 dated 20-04-2026.",
    "Delivery to Doha via 1 truck is included in the grand total.",
    "A discount of SR 3,100.00 has been applied to the quoted sub-total.",
    "All materials remain vendor property until payment is fully settled."
  ]
}
```

## Field-by-field notes

**`profile`** is the single switch that flips the entire branding. Use `tndk` by default unless the user specifically asks for the Doha Cooling header (which Farhan generally avoids per saved instructions).

**`po_date`** is kept as a string — pass it in whatever format you want printed (e.g. `"20-04-2026"`, `"20 April 2026"`).

**`unit_price` / `total` / `qty`** are accepted as either numbers or numeric strings. If `total` is omitted, it's computed as `qty × unit_price`. If you supply a non-numeric `qty` (rare; e.g. "Lot"), supply `total` explicitly.

**`specs`** are optional bullet points rendered under the description title. Keep each bullet short — they wrap inside the cell.

**`variant`** is for cases like the IDIF doors where two otherwise-identical line items differ only by left/right handedness. Renders as italic gray text below the specs. Skip it when not relevant.

**`amount_words`** auto-generates English using the standard short scale (Thousand / Million / Billion). Override only if the user wants different phrasing. The function knows these currencies: QAR, SR/SAR, AED, USD, EUR, OMR, BHD, KWD, INR.

**`notes`** render as italic, numbered. The default sample's note 4 ("All materials remain vendor property until payment is fully settled.") is a good standard line to keep on most POs.
