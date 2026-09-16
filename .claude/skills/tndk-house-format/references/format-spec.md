# House format — measured spec

Everything here was measured off the approved **LPO-194/2026** (Airtronics Trading Contracting
& Maintenance, 14-07-2026). Where a value looks arbitrary, it is not — it is what the approved
document does. Change these only with Farhan's say-so, and change them in one place so all
document types move together.

## Contents

- [Page and colours](#page-and-colours)
- [Vertical structure](#vertical-structure)
- [Line table](#line-table)
- [Money block](#money-block)
- [Type and weight](#type-and-weight)
- [JSON field reference](#json-field-reference)
- [Open question — company name and email](#open-question--company-name-and-email)

---

## Page and colours

| | Value |
|---|---|
| Page | A4, 595.9 × 842.9 pt (210 × 297 mm) |
| Content margin | 27 pt left and right → content width **540.8 pt** |
| Header, section bars, footer | **navy `#1F3864`** |
| Rules above/below, badge | **gold `#C9A24E`** |
| Meta strip, words band, callout, grand-total shading | **panel `#EEF2F8`** |
| Table grid lines | **`#C9CDD6`** at 0.6 pt |
| Body text | `#222222`; secondary/italic `#333333`; on navy `#FFFFFF` |

Header and footer bands are **full bleed** — they run 0 → 595.9, not inside the margin. This is
why the renderer sets `@page { margin: 0 }` and pads inside the bands instead.

## Vertical structure

Measured y-positions on the approved LPO:

| Band | y0 | y1 |
|---|---|---|
| Navy header | 0.8 | 65.2 |
| Gold rule | 65.2 | 69.0 |
| Meta strip (panel) | 69.0 | 102.8 |
| Section bar ("VENDOR INFORMATION") | 114.8 | 137.2 |
| Line table header | 210.8 | 240.0 |
| Grand-total row | 626.2 | 647.2 |
| Amount-in-words band | 652.5 | 670.5 |
| Computer-generated callout | 726.8 | 762.0 |
| Gold rule | 778.5 | 782.2 |
| Navy footer | 782.2 | 813.0 |

The gold badge sits at **x 445.5 → 568.5, y 11.2 → 57.8** — 123 × 46.6 pt, right-aligned in the
header band. Two-line badges put line 1 at 10 pt and line 2 at 14 pt; single-line badges use
14 pt so the box keeps its height.

The footer is **fixed to the page edge** and repeats on every page. A one-line delivery return
and a three-page invoice both close the same way.

## Line table

Column boundaries, measured: `27.0 · 51.8 · 327.0 · 364.5 · 402.0 · 496.5 · 567.8`

| Column | Width (pt) | % of content | Align |
|---|---|---|---|
| S/N | 24.8 | 4.59 | centre |
| DESCRIPTION | 275.2 | 50.89 | header centred, **cells bold left** |
| UNIT | 37.5 | 6.93 | centre |
| QTY | 37.5 | 6.93 | centre |
| UNIT PRICE (QAR) | 94.5 | 17.48 | right |
| TOTAL (QAR) | 71.3 | 13.18 | right |

Header row is navy with white bold 9.5 pt; the currency sits on a second line in brackets.
Delivery returns insert a **REASON** column after DESCRIPTION and drop the two money columns;
percentages are renormalised automatically, so the table always fills the content width.

## Money block

Three cells across the full content width, and the grand-total shading is deliberately partial —
this is what the approved document does:

| Cell | x range | Grand-total row |
|---|---|---|
| Filler | 27.0 → 402.0 (69.3%) | **shaded** `#EEF2F8` |
| Label | 402.0 → 496.5 (17.6%) | unshaded |
| Value | 496.5 → 568.5 (13.2%) | **shaded** `#EEF2F8` |

Sub-total and discount rows are unshaded, bold, 9.5 pt. The grand-total row is 11 pt navy bold.
Discounts and any negative amount print in parentheses: `(297.00)`.

The amount-in-words band spans the full content width beneath it, panel fill, `Amount in Words:`
in bold followed by the generated phrase.

## Type and weight

| Element | Size | Weight |
|---|---|---|
| Company name | 17 pt | bold, white |
| Company address line | 9 pt | regular, white |
| Badge line 1 / line 2 | 10 / 14 pt | bold, navy on gold |
| Meta strip | 9.5 pt | labels bold, values regular |
| Section bar | 10.5 pt | bold, white on navy |
| Body, party block, table | 9.5 pt | descriptions bold, values regular |
| Grand total | 11 pt | bold, navy |
| Notes | 8.5 pt | italic; the word "Notes:" bold italic navy |
| Callout heading | 10.5 pt | bold navy |
| Footer | 8.5 pt | line 1 bold, line 2 italic |

Font is **Arial** with Liberation Sans and Helvetica as fallbacks. The approved PDF renders in
Liberation Sans, which is the metric-compatible substitute a Linux renderer picks for Arial —
so the stack reproduces it on any machine.

> The older TNDK skills specify Calibri. The approved LPO is not Calibri, and this format
> follows the approved document. Worth a one-line ruling from Farhan if both are meant to
> coexist, but nothing is blocked on it.

## JSON field reference

| Field | Required | Notes |
|---|---|---|
| `type` | **yes** | `lpo` · `invoice` · `receipt` · `delivery_note` · `delivery_return` |
| `number` | yes in practice | From the numbering log. `INV-NNN/YYYY`, `RCT-NNN/YYYY`, `DN-NNN/YYYY`, `DR-NNN/YYYY`, `LPO-NNN/YYYY` |
| `date` | yes | `DD-MM-YYYY` |
| `ref` | recommended | The award or document this one sits under |
| `meta_labels` | no | Overrides the three strip labels for the type |
| `counterparty_label` | no | `VENDOR` / `CLIENT` on the strip's second line |
| `party.title` | no | Overrides the section bar text |
| `party.name` | yes | Legal name, as it appears on the award |
| `party.fields` | no | List of `{label, value}` or plain strings |
| `lines[].description` | yes | Printed bold |
| `lines[].unit` | no | Defaults to `Nos` |
| `lines[].qty` | yes | |
| `lines[].rate` | money types | Unit price |
| `lines[].amount` | no | Computed as qty × rate unless supplied |
| `lines[].reason` | delivery returns | Why it came back |
| `subtotal` | no | Computed; supplying it makes the check stricter, not looser |
| `discount` | no | Positive number, printed in parentheses |
| `adjustments` | no | `[{label, amount}]` — variations, retentions, carried-forward shortfalls |
| `grand_total` | no | Computed as subtotal − discount + adjustments |
| `grand_total_label` | no | e.g. `TOTAL RECEIVED` on a receipt |
| `amount_in_words` | no | Generated; if supplied it must match, or the render is refused |
| `instrument` | **receipts** | Any keys; `type: "cheque"` adds the realization note |
| `notes` | no | Numbered automatically |
| `show_prices` | no | `true` puts money on a delivery note |
| `show_payee` | no | `false` drops the payee line from an invoice |
| `company` | no | `{name, address, footer}` |
| `currency` | no | `QAR` default |
| `filename` | no | Defaults to `<type>_<number>` |

## Open question — company name and email

The approved LPO carries:

- **THE NEW DOHA KITCHEN COMPANY**
- P.O. Box 80247, Doha, Qatar | **info@dkeqatar.com**

The system's durable facts and the older skills carry:

- **The New Doha Kitchen Equipment Services W.L.L.** (TNDK)
- farhan@dctsqatar.com · Tel 7706 0676

Both are in use. The renderer defaults to the **approved LPO's** wording, because that is the
document Farhan signed off, and the payee line keeps its own exact wording — *"The New Doha
Kitchen Equipment and Services"* — which is a third variant and a standing correction in its
own right.

**This needs one ruling:** which name and email belong on the letterhead of each document type.
Until then, override per document with `company` where a different one is wanted. Nothing is
blocked; it is just worth settling before the next batch goes out.
