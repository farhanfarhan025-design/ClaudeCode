# QA CHECKLIST — PURSUE

Run before every handoff. A failed item is a stop, not a note.

## The A9 sweep — run this first, on every client-facing draft

Read each draft **one sentence at a time** and confirm none of the following appears:

- [ ] A price, a total, a rate, a percentage, or a number in QAR that is not the quotation
      reference itself.
- [ ] A discount, a concession, or a hint that one might exist ("we may have some flexibility").
- [ ] A delivery date, a lead time, a duration, or a completion promise.
- [ ] A scope change offered to restart the conversation.
- [ ] A commitment of any kind that Farhan has not made in writing.
- [ ] An answer to a client's price or delivery question. The correct answer is that it has gone
      to Farhan.

A single failure here stops the handoff. This is `RULES.md` A9 and it does not have a
"but the client asked" exception.

## Register integrity

- [ ] Every issued quotation known to the system is in the register.
- [ ] Every row's `date_sent` is the date it was actually sent, not the document date — or the
      difference is recorded as an assumption.
- [ ] No duplicate quotation reference. (`RULES.md` A7 — a reused number is a defect upstream.)
- [ ] Every `open` row has a next action and a next action date.
- [ ] Every `won` row carries a written award reference (LPO / LOA / approved quotation).
- [ ] Every `lost` row carries a reason code from the standard list.
- [ ] `reconstructed: true` is set on every historic row and on no current row.
- [ ] Status values are only `open` / `won` / `lost` / `expired` / `withdrawn`.

## Arithmetic and method

- [ ] `scripts/pipeline.py` ran clean; its exit code was inspected, not assumed.
- [ ] Unweighted pipeline recomputed by hand for at least one row and matches.
- [ ] Expected value states its basis — observed rate or assumed rate — in the same sentence
      as the number.
- [ ] No win rate is reported from fewer than 20 tracked decisions.
- [ ] No rate includes reconstructed rows.
- [ ] Per-tier rates suppressed below 5 decisions in that tier.
- [ ] Days-open and days-quiet computed against the stated `as of` date, and that date is in
      the report. (`RULES.md` A4 — no figure without its "as of".)

## Truthfulness

- [ ] Every loss reason is one the client actually gave, or is `UNKNOWN`. Nothing inferred from
      silence.
- [ ] No outcome recorded without a document or Farhan's confirmation.
- [ ] Client words quoted are verbatim, in quotation marks, and not paraphrased into something
      tidier.
- [ ] Nothing is described as sent, said or agreed that was not.
- [ ] Where the record is incomplete, the report says so rather than smoothing it over.

## Rules compliance

- [ ] Output marked `DRAFT — NOT SENT`.
- [ ] Nothing was sent to anyone. (No send capability exists — confirm none was simulated.)
- [ ] No fabricated figure. Values come from the issued quotation, not from a recollection.
- [ ] The word "tax" does not appear.
- [ ] The rate card, cost build-up and margin log were not read. PURSUE has no business in them.

## Presentation

- [ ] Leads with what moved and what needs a decision.
- [ ] Weighted figure first; unweighted labelled as unweighted.
- [ ] Money formatted `QAR 0,000.00`.
- [ ] Assumptions labelled as assumptions.
- [ ] Drafts are ready to send unedited.
- [ ] Short enough to read in under a minute.

## Self-assessment before handoff

Answer honestly. A "no" is an escalation, not a note to self.

1. Did I meet every Definition of Done condition?
2. Is every factual claim supported by a source I can name?
3. Did I infer any outcome, reason or intent that nobody stated?
4. Would a second reviewer produce the same pipeline totals from the same register?
5. Is there a number in a client-facing draft? **(The answer must be no.)**
6. Is human review still required? **(For PURSUE the answer is always yes.)**
