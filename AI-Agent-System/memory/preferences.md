# PREFERENCES

Standing conventions. **Every entry here traces to a correction Farhan actually made** — this
file is not a place for guesses about what he might like.

Source note: the `tndk-accounts` conventions file states these "reflect corrections Farhan has
made repeatedly." Treat a violation as a defect, not a style difference.

---

## Documents

| Preference | Detail | Confidence |
|---|---|---|
| **No tax, ever, on invoices** | Title `INVOICE`, never "TAX INVOICE". Sub-Total → Grand Total. No VAT line. Script-enforced. | high — explicit permanent instruction |
| Payee line wording | *"The New Doha Kitchen Equipment and Services"* — no W.L.L. on this line | high |
| Invoice / receipt signature | `Ronaldo / Accountant` | high |
| Quotation signature | `Farhan / Sales Engineer` + both company names | high |
| Header email | `farhan@dctsqatar.com` regardless of signatory | high |
| LPO signature | None — "computer generated document" callout instead | high |
| Default letterhead | TNDK. DCTS only for legacy match | high |

## Branding

| Element | Value |
|---|---|
| Page | A4 portrait, margins ~900 twips |
| Font | Calibri throughout |
| Dark blue | `#1F3864` |
| Gold | `#C9A24E` |
| Light blue panel | `#D6E4F0` · grey `#F2F2F2` |
| Paid | `#E2EFDA` fill, `#2E7D32` text |
| Due | `#C00000` text, `#FDECEA` panel |
| Caution | `#FFF2CC` |

**Never modify:** the quotation cover page, the promotional images on the pricing page, the
header/footer styling, the 13-section quotation structure and its numbering.

## Numbering

- Read `numbering-log.md` before issuing; append after. Always.
- Formats: `INV-NNN/YYYY` · `RCT-NNN/YYYY` · `QUT/DCTS/NNN/YYYY` · `DN-NNN/YYYY` · `LPO-NNN/YYYY`
- A client with an inherited series keeps it (Ruwais Farm `INV-014/2026`).
- On collision, renumber the **newer** document.

## Money

- QAR default. Comma separators, 2 decimals: `QAR 59,000.00`.
- Vendor POs may be SR (Saudi), AED (UAE), USD/EUR.
- Discounts shown in parentheses, accounting style: `(3,100.00)`.
- Pass raw numbers to generators; formatting is the generator's job.

## Working style — how to interact with Farhan

| Preference | Evidence |
|---|---|
| **Don't re-ask what's already been said.** Extract from context; ask only for genuinely missing fields. | Explicit instruction in two separate skills |
| **Never guess a financial figure.** A clarifying question beats a wrong contract total. | Explicit: "a balance invoice with the wrong contract total is worse than a one-line clarifying question" |
| **Be the second pair of eyes on money.** Flag shortfalls, LPO/quote discrepancies, cheque allocation mismatches. | Explicit standing instruction |
| **Verify before delivering.** `pdftotext | grep` checks, totals reconciled. | Built into his own workflow |
| Deliver both PDF and editable source | Standing convention |
| File into the standard Drive tree, named clearly | Standing convention |

## Commercial

- LPO/LOA payment terms **govern** over quotation terms. Flag the difference, then bill on the LPO.
- Flag shortfalls in QAR and carry them forward.
- Recommend written confirmation before ordering materials on a verbal award.
- Standard quotation validity: 15 days.
- Standard markup: 20–30%, 30% default for new clients *(and see `analysis/FINDINGS.md` —
  practice has diverged from this)*.
