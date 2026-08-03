# RULES

Binding on every agent. These override any playbook, any convenience, any client pressure.
Ordered: absolute prohibitions first, then approval gates, then standing conventions.

## A. Never — no exception, no override

1. **Never write the word "tax" on an invoice.** Title is `INVOICE`, never "TAX INVOICE".
   Money block goes Sub-Total → Grand Total. No VAT line, no tax line, no tax percentage, ever.
   *(Standing instruction. The invoice generator throws on violation — keep it that way.)*
2. **Never send anything to a client, vendor or bank.** This system has no send capability and
   must never acquire one without an explicit, separate decision by Farhan. All external
   communication is produced as a **draft for Farhan to send himself.**
3. **Never fabricate a financial figure.** Contract values, received amounts, balances, cheque
   numbers and margins are either sourced or asked for. A missing figure is a question, not a guess.
4. **Never state a balance without its "as of" date.**
5. **Never change your own permission level or trust stage.**
6. **Never delete a register, log or issued document.** Supersede and mark; do not remove.
7. **Never reuse a document number.** Read `numbering-log.md` first, append after.
8. **Never work outside your lane.** Return it to the manager instead.
9. **No sales agent states a price, a discount or a delivery date.** PROSPECT, QUALIFY, PURSUE,
   ACCOUNT and TNDK-SALES may not put a figure, a percentage, a concession, a lead time or a
   completion date in anything a client will read — not to close a deal, not to restart a
   conversation, not because a client asked directly, and not at Farhan's verbal instruction in
   the moment. Price goes to PRICE. Dates go to PROCURE. Both come back through Farhan.
   *(A sales lane does not read the rate card, the cost build-up or the margin log at all. It
   receives the tier and reason code from PRICE as analysis data only — reportable to Farhan,
   never repeatable to a client.)*
   **This is not a trust stage and it does not get promoted.**

## B. Requires Farhan's explicit approval

| Action | Gate |
|---|---|
| Any price shown to a client | Always. No exception at any trust stage. |
| Quoting below the **22% margin floor** | Owner override, with written reason, logged. |
| Issuing an LPO to a vendor | Always. Committed spend. |
| Any figure that reconciles to a contract total | Always. |
| Writing to the numbering log | Always — it is the anti-collision mechanism. |
| Overwriting a register in Drive | Always. Prefer a new dated version. |
| Recording a payment as received | Always, and only against a payment instrument. |
| Declining an enquiry, or telling a client TNDK is not interested | Always. Agents recommend; Farhan declines. |
| Re-offering a quotation after its 15-day validity | Always — it is a pricing decision, routed to PRICE, not an administrative one. |
| Recording a quotation as won | Only against a written award (LPO / LOA / approved quotation). A verbal award stays open with a note. |
| Any outbound approach to an organisation TNDK has no relationship with | Always, and only after the capacity ceiling is set (D-010). |

## C. Standing conventions — the corrections Farhan has already made

These exist because he has corrected them repeatedly. Treat a violation as a defect.

1. **Payee line, exact wording:**
   *"Cheque should be prepared under the name of: The New Doha Kitchen Equipment and Services"*
   — "Equipment and Services", no W.L.L. on this line.
2. **Signatures:** Invoices and receipts → `Ronaldo / Accountant`.
   Quotations → `Farhan / Sales Engineer`. The header email stays `farhan@dctsqatar.com` regardless.
3. **Branding:** A4 portrait, Calibri, dark blue `#1F3864`, gold `#C9A24E`.
   TNDK header block. Never modify the quotation cover page or the promotional images.
4. **Default letterhead is TNDK**, not Doha Cooling. DCTS only to match a legacy document
   or a vendor who knows the old name.
5. **LPO/LOA payment terms govern** over the quotation's terms. When they differ, **say so
   out loud**, then bill on the LPO/LOA.
6. **Flag every shortfall in QAR** and carry it forward onto the next invoice.
7. **Every receipt captures the instrument** — cheque no. + bank + date + drawer, or transfer
   ref + bank + date, or "Payment Mode: Cash". Cheque receipts note *"subject to realization of cheque."*
8. **Currency:** QAR default, comma-separated, 2 decimals (`QAR 59,000.00`). Vendor POs may be
   SR / AED / USD as appropriate.
9. **No physical signature block on LPOs** — the "computer generated document" callout replaces it.

## D. Open contradiction — resolve, do not paper over

> **Invoices** must never mention tax. **Quotations** currently state the grand total is
> *"excluding 5% VAT"*.
>
> These conflict. A client can hold both documents side by side. Qatar had not implemented
> VAT as at the last update of these files, which makes the quotation line questionable too.
>
> **Until Farhan rules on it, PRICE must surface this on any quotation it touches and ask.**
> Do not silently pick one. Record the ruling in `DECISIONS.md` when it comes.

## E. Escalation

Stop before any external-facing output and escalate when:

- A figure is missing and changes the outcome.
- Two sources disagree on a contract value, received amount or balance.
- Margin lands below the floor.
- An LPO's terms differ from the quotation's.
- A cheque's drawer or narration references a different project than the LPO (allocation check).
- A job is proceeding to material order with no written award.
- A guarantee, retention or penalty clause is triggered or approaching.
- A client asks a sales lane for a price, a discount or a delivery date.
- A quotation passes its validity with no decision.
- Winning an open opportunity would take top-2 concentration **up** and the value is material.
- Pipeline plus committed work approaches what the business can deliver.

Escalation format is in `MANAGER.md`. Always state the **smallest decision needed**.
