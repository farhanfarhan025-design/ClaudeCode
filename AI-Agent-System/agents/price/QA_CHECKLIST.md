# QA CHECKLIST — PRICE

Run before every handoff. A failed item is a stop, not a note.

## Arithmetic

- [ ] Panel area recomputed by hand for at least one room and matches the script.
      `wall = 2(L×H) + 2(W×H)` · `ceiling = L×W` · `floor = L×W` if insulated.
- [ ] Angle count = `ceil((4(L+W) + 4H) / 6)`.
- [ ] Floor pairs = `ceil(floor_area / 2.88)`.
- [ ] Freezer used 6,400/set, chiller used 8,800/set — not swapped.
- [ ] Common items scaled by room count, not left at one room's worth.
- [ ] Labour = 15% of **direct**, not of total.
- [ ] Total cost = direct + labour + transport.

## Scope coverage

- [ ] Every item in the scope has a cost line.
- [ ] Every cost line corresponds to something in the scope.
- [ ] Insulated floor priced only where the scope includes it.
- [ ] Door count matches the scope.
- [ ] Variations entered as `extras`, not folded into a rate.

## Margin

- [ ] Realised markup computed against **total cost**, not direct cost.
- [ ] Both conventions reported and clearly labelled.
- [ ] Floor checked. Script exit code inspected.
- [ ] If below floor: override requested, and `logs/overrides/` entry written **before**
      any quotation was produced.
- [ ] If between floor and default: reason code assigned.
- [ ] Margin log appended, including tier and reason code.

## Rules compliance

- [ ] Output marked `DRAFT — NOT SENT`.
- [ ] Nothing was sent to anyone. (No send capability exists — confirm none was simulated.)
- [ ] No fabricated cost. Every figure traces to the rate card, a vendor quote, or Farhan.
- [ ] The word "tax" does not appear. If a quotation is being produced with the
      "excluding 5% VAT" line, D-005 has been surfaced.
- [ ] Rate card was **not** modified to reach a target price.

## Presentation

- [ ] Leads with the number and the decision needed.
- [ ] One recommended tier, one sentence of reasoning — not a menu.
- [ ] Money formatted `QAR 0,000.00`.
- [ ] Assumptions labelled as assumptions.
- [ ] Short enough to read in under a minute.

## Self-assessment before handoff

Answer honestly. A "no" is an escalation, not a note to self.

1. Did I meet every Definition of Done condition?
2. Is every factual claim supported by a source I can name?
3. Did I guess anything that changes the outcome?
4. Would a second reviewer reach the same total cost from the same inputs?
5. Is human review still required? **(For PRICE the answer is always yes.)**
