# House style

Every entry here traces to a correction Farhan has actually made, usually more than once. Treat
a violation as a defect, not a difference of taste — a client can hold two TNDK documents side
by side, and inconsistency between them is what makes a company look like it is guessing.

## Contents

1. [Exact wordings](#exact-wordings)
2. [Signatories](#signatories)
3. [Money](#money)
4. [Branding](#branding)
5. [The tax rule](#the-tax-rule)
6. [Capturing a payment instrument](#capturing-a-payment-instrument)
7. [Verification before delivery](#verification-before-delivery)

---

## Exact wordings

**Payee line** — reproduce character for character:

> Cheque should be prepared under the name of: The New Doha Kitchen Equipment and Services

"Equipment **and** Services", spelled out, and **no W.L.L. on this line**. Banks reject cheques
over a name mismatch, and a rejected cheque costs weeks.

**Cheque receipts** carry: *"subject to realization of cheque."* Money on a cheque is not money
until it clears, and a receipt that says otherwise is a claim TNDK cannot support.

**LPOs** carry a *"computer generated document"* callout and **no physical signature block**.
The callout is what replaces the signature; adding one back makes the document look forged.

**Company footer:** P.O. Box 80247, Doha, Qatar · Tel 7706 0676 · farhan@dctsqatar.com

The header email stays `farhan@dctsqatar.com` regardless of who signs the document.

---

## Signatories

| Document | Signature block |
|---|---|
| Invoice | `Ronaldo / Accountant` |
| Receipt | `Ronaldo / Accountant` |
| Delivery note | `Ronaldo / Accountant` |
| Quotation | `Farhan / Sales Engineer` + both company names |
| LPO | None — the "computer generated document" callout instead |

The "Sales Engineer" title on quotations is a deliberate client-facing choice. It says nothing
about authority: Farhan is the owner, and nothing in this business needs a third party's
sign-off.

**Default letterhead is TNDK**, not Doha Cooling. Use DCTS only to match a legacy document or a
vendor who still knows the old name.

---

## Money

- **QAR by default.** Comma separators, two decimals: `QAR 59,000.00`.
- Vendor purchase orders may be SR, AED, USD or EUR as the vendor requires.
- Discounts in accounting style, in parentheses: `(3,100.00)`.
- Pass **raw numbers** to the generators. Formatting is the generator's job — formatting by
  hand is how two documents end up disagreeing on the same amount.
- **Never state a balance without its "as of" date.** A balance is a snapshot, and a snapshot
  without a timestamp is a rumour.
- Always show the chain: Contract → less received → Balance, with the stage at which the
  balance falls due.

**Margin vocabulary — keep the two apart.** The pricing guide says "margin" but computes markup
on cost (`price = cost × (1 + m)`). A "30% margin" in that sense is a 23.1% gross margin as a
share of price. Whenever margin comes up, label which one you mean; the gap is about seven
points at the default and it widens as the number grows.

---

## Branding

| Element | Value |
|---|---|
| Page | A4 portrait, margins ~900 twips |
| Font | Calibri throughout |
| Dark blue | `#1F3864` |
| Gold | `#C9A24E` |
| Light blue panel | `#D6E4F0` |
| Grey | `#F2F2F2` |
| Paid | fill `#E2EFDA`, text `#2E7D32` |
| Due | text `#C00000`, panel `#FDECEA` |
| Caution | `#FFF2CC` |

**Do not modify:** the quotation cover page, the promotional images on the pricing page, the
header and footer styling, or the 13-section quotation structure and its numbering. These are
finished work. Improving them unasked is not an improvement.

---

## The tax rule

**Absolute on invoices, receipts and delivery notes.** The document is titled `INVOICE` — never
"TAX INVOICE". The money block runs Sub-Total → Grand Total. There is no VAT line, no tax line,
no tax percentage, anywhere. The generator throws on violation; keep it that way.

**The unresolved part.** Quotations currently state that the grand total is *"excluding 5%
VAT"*. That contradicts every invoice TNDK issues, and a client can hold both documents at
once. Qatar had not implemented VAT as at the last update of these files, which makes the
quotation line questionable on its own terms.

Until Farhan rules on it, surface the contradiction on any quotation you touch and ask which
way he wants it. Do not silently pick one — a silent choice here is a decision made on his
behalf about what he is telling clients.

---

## Capturing a payment instrument

A receipt records a fact about money that arrived. It needs the evidence attached:

| Mode | Capture |
|---|---|
| Cheque | Cheque number · bank · date · drawer, plus *"subject to realization of cheque."* |
| Transfer | Transfer reference · bank · date |
| Cash | `Payment Mode: Cash` |

Then check the allocation before crediting: a drawer's name or a narration that points at a
different project than the one being credited is an escalation, not a detail. Misallocated
payments are found months later, in front of a client.

---

## Verification before delivery

Run the checker on every document:

```bash
python3 .claude/skills/george/scripts/check_document.py --type invoice "Invoice INV-253-2026.pdf"
```

It exits `0` on pass (warnings allowed), `2` on any hard breach. Types accepted:
`invoice`, `receipt`, `delivery-note`, `quotation`, `lpo`, `register`.

The script reads the text of the finished file, so it catches what actually reached the page
rather than what the input JSON intended. That distinction matters — the failures worth
catching are the ones where the data was right and the document still came out wrong.

Then read it yourself for what a script cannot judge:

- Does the arithmetic reconcile to the contract total?
- Does a balance invoice carry forward the earlier shortfall, and include any variations?
- Does the stage described match the milestone actually reached?
- Are the client's name and reference as written on the award, not as everyone says them?
- Is the "as of" date on any balance actually today's snapshot?

Deliver both the PDF and the editable source, filed and named clearly.
