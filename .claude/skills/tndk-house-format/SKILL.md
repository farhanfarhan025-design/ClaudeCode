---
name: tndk-house-format
description: The single house format for every TNDK document — invoice, LPO, receipt, delivery note, delivery return, and anything else on company letterhead. Use this skill whenever the user asks to make, raise, draft, prepare, issue or re-issue any of those; mentions INV-NNN, RCT-NNN, DN-NNN, DR-NNN or LPO-NNN; asks for a purchase order, payment receipt, delivery challan, goods return or credit-side paperwork; or supplies line items, quantities and prices and wants a document built. Also trigger on "same format", "usual format", "house format", "our template", "make it match", on any request to restyle or reproduce an existing TNDK document, and on any new accounts document type not listed here — one layout covers all of them. Farhan approved this format on LPO-194/2026 and it is the default for every document TNDK issues; do not invent a layout, and do not fall back to a plain table.
---

# TNDK House Format

One layout for every document TNDK issues. It was approved on **LPO-194/2026** (Airtronics,
14-07-2026) and measured off that PDF — colours, column widths and band heights in
`references/format-spec.md` are taken from the file, not chosen here.

**Do not design a document.** Fill in JSON and render. If a new document type is needed that
isn't listed below, extend `TYPES` in the renderer rather than hand-building a one-off — a
second layout is how a house format dies.

## Render it

```bash
python3 scripts/render_doc.py job.json --outdir out/
```

Chromium's print-to-PDF is used when present, LibreOffice otherwise, so the same JSON produces
the same document on any machine. `--keep-html` leaves the intermediate HTML if you need to
inspect the markup.

Worked inputs for every type are in `assets/` — `example_lpo.json` reproduces the approved
Airtronics LPO exactly, and is the reference to copy from.

## The seven types

Everything shares the header, meta strip, party block, line table and footer. Only four things
change, and the renderer already knows them — do not override them casually:

| `type` | Badge | Party block | Money | Signed |
|---|---|---|---|---|
| `lpo` | LOCAL PURCHASE / ORDER | VENDOR INFORMATION | yes | computer-generated callout, **no signature** |
| `invoice` | INVOICE | BILL TO | yes | `Ronaldo / Accountant` + payee line |
| `receipt` | RECEIPT | RECEIVED FROM | yes | `Ronaldo / Accountant` + instrument block |
| `delivery_note` | DELIVERY / NOTE | DELIVER TO | no | delivered-by / received-by |
| `delivery_return` | DELIVERY / RETURN | RETURNED FROM | no | returned-by / received-back-by, adds a REASON column |
| `quotation` | QUOTATION | TO | yes | `Farhan / Sales Engineer` |
| `handover` | HANDOVER / CERTIFICATE | HANDOVER TO | no | handed-over-by / received-and-accepted-by, adds a VERIFIED tick column |

A handover certificate is a checklist signed at site: each line is ticked by both parties, and
the client's signature starts the warranty. Leave the verification column as `"☐"` rather than
asserting a test passed — a certificate that pre-ticks its own checks is worthless as evidence.

The footer follows the signature mode. Two-party documents say *"This document requires the
signature of both parties to be valid"*; documents signed by one TNDK signatory say *"valid when
signed and stamped by an authorised signatory"*; only the LPO, which carries no signature at all,
carries the computer-generated line. A handover that denied needing a signature would contradict itself on its own face.

Quotations are signed `Farhan / Sales Engineer` and invoices and receipts `Ronaldo /
Accountant`. That split is a standing convention, not a preference — do not let a quotation go
out under the accountant's name.

A line description may contain newlines; they render as line breaks. That is how a lump-sum
quotation carries a numbered scope inside one priced row without inventing a price split for
each item.

The signature rules are not stylistic. LPOs carry the "computer generated document" callout
*instead of* a signature; invoices and receipts are signed by the accountant; delivery documents
need two physical signatures because they are the proof that goods moved.

## Minimum input

```jsonc
{
  "type": "invoice",
  "number": "INV-259/2026",          // read the numbering log first, append after
  "date": "06-08-2026",              // DD-MM-YYYY, as on every issued TNDK document
  "ref": "LPO PO-2026-0000248",      // the award this document sits under
  "party": {
    "name": "Client or vendor legal name",
    "fields": [ {"label": "Attention", "value": "..."}, "a plain line with no label" ]
  },
  "lines": [
    {"description": "...", "unit": "Nos", "qty": 2, "rate": 180.00}   // amount computed
  ],
  "discount": 297.00,                // optional, shown in parentheses
  "adjustments": [{"label": "Chequered floor variation", "amount": 875.00}],   // optional
  "notes": ["...", "..."]            // optional, numbered automatically
}
```

Optional: `badge` (override the type's badge — INV-253 went out as *ADVANCE INVOICE*, so its
final counterpart says *FINAL INVOICE* rather than a label the client has not seen),
`currency` (QAR default), `company` (`{name, address, footer, legal}` — `legal` is the entity
named above a signature, kept separate because the header name is set in capitals), `amount_in_words`
(computed if omitted), `grand_total_label`, `show_prices` (put prices on a delivery note),
`instrument` (**required** on receipts), `meta_labels`, `counterparty_label`, `filename`,
`extra_column` (`{label, field, width, align, position}` — `position: "end"` puts it after the
money columns, which is where a tick box belongs).

Full field reference: `references/format-spec.md`.

## What the renderer refuses to do

Three checks run before any PDF is written. Each **raises** and returns exit code 2 — none of
them warns, because a document that looks right and is wrong is worse than no document.

1. **The word "tax" or "VAT" anywhere on the page.** TNDK documents never carry one. If policy
   ever changes, that is Farhan's ruling to make and record first — not something a generator
   quietly permits.
2. **Arithmetic that does not hold.** Line totals must sum to the sub-total, and
   sub-total − discount + adjustments must equal the grand total. A stated `amount_in_words`
   must match the grand total; mismatches name both figures so you can see which is wrong.
3. **A receipt with no payment instrument.** Cheque no. + bank + date + drawer, transfer ref +
   bank + date, or `Payment Mode: Cash`. A receipt without one is a received amount nobody can
   trace, and cheque receipts automatically carry *"subject to realization of cheque."*

When a check fires, fix the source data. Do not adjust a total to make the check pass — that
inverts the whole point of having it.

## Conventions the format carries for you

- **Match the letterhead the client already holds.** TNDK trades under more than one name:
  the Airtronics LPO says *The New Doha Kitchen Company / info@dkeqatar.com*, while Jollibee's
  INV-253, their quotation and their cheque all say *The New Doha Kitchen Equipment Services
  W.L.L.* Pass `company` per client rather than accepting the default, and check an earlier
  document to that client before issuing. A second invoice under a different name invites a
  question you do not want asked.
- **Payee line on invoices**, exact wording: *"Cheque should be prepared under the name of:
  The New Doha Kitchen Equipment and Services"*.
- **Negatives in parentheses**, accounting style: `(27,600.00)`.
- **QAR, comma-separated, two decimals.** Pass raw numbers; formatting is the renderer's job.
- **Amount in words** generated from the grand total, in the approved phrasing:
  *"Nine Thousand Five Hundred Qatari Riyals Only (QAR 9,500.00)"*.
- **Footer on every page**, pinned to the page edge however short the document is — and on
  every page of a document that runs to two or three, which is where it is easiest to lose.
- **Pages after the first open with a top margin.** Page 1 is full bleed so the navy header
  touches the paper edge; a continuation page that starts hard against the top of the sheet
  reads as a broken page. Both are handled by the repeating `thead`/`tfoot` spacers on
  `table.pagegrid`, not by `@page` margins — a `@page` top margin pushes the fixed footer
  off every page after the first. Do not swap one for the other.
- **Bold marks headings, not body copy.** A single-line item renders bold, as on the approved
  LPO. In a lump-sum scope, each numbered clause has its heading bolded and its body set in
  normal weight; a full page of bold reads as shouting.

## Before it goes anywhere

The renderer produces a **draft**. No agent sends anything to a client, vendor or bank —
Farhan sends. Before handing one over:

- [ ] Number read from the numbering log **before** issuing, and appended after. On a
      collision, renumber the newer document.
- [ ] Terms match the LPO/LOA, not the quotation, where they differ — and the difference is
      said out loud.
- [ ] Totals reconcile to the contract value; any shortfall flagged in QAR and carried forward.
- [ ] The right signature block for the type (the renderer picks it; confirm it's the one you
      meant).
- [ ] Deliver both the PDF and its JSON, so the document can be regenerated rather than retyped.

## Extending it

A new document type is a new entry in `TYPES` in `scripts/render_doc.py`: badge lines, party
title, meta labels, whether it carries money, and how it is signed. That is the whole contract
— roughly ten lines. Everything else is inherited, which is what keeps twelve document types
looking like one company.

## Reference

- `references/format-spec.md` — the measured geometry, colours, fonts and the full JSON field
  reference. This is the authority; the renderer implements it.
- `assets/example_*.json` — one worked input per type.
