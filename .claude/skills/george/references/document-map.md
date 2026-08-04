# Document map

The chains a job belongs to, the numbers it consumes, and where the files land.

Use this at the start of every job: identify which chain the request sits in, then work the
whole chain rather than the one document that was named.

## Contents

1. [The six chains](#the-six-chains)
2. [Numbering](#numbering)
3. [Filing tree](#filing-tree)
4. [Open loops each stage creates](#open-loops-each-stage-creates)
5. [Reading an award](#reading-an-award)

---

## The six chains

### 1 — Enquiry arrives

*Trigger: site dimensions, a temperature, a forwarded WhatsApp, "what would a 3×4 chiller cost".*

| Step | Document | Skill |
|---|---|---|
| Define the technical scope | — (questions back to Farhan) | — |
| Price it | cost build-up, margin check | `AI-Agent-System/scripts/margin.py` |
| Issue | Quotation `QUT/DCTS/NNN/YYYY` | `tndk-coldroom-quotation` |
| File | `03 - Under process/` | — |

The price shown to a client is always Farhan's decision, at every trust stage. Draft it,
compute the realised margin, present both — then wait.

**Creates:** a follow-up loop dated at the quotation's validity (standard 15 days).

### 2 — Award lands

*Trigger: an LPO, an LOA, a signed/approved quotation, or "they confirmed verbally".*

| Step | Document | Skill |
|---|---|---|
| Read the award terms and compare to the quotation's | — (flag differences out loud) | — |
| Register the project | row in Approved Works Register | `tndk-accounts` |
| Build the project file | project workbook (summary + expenses tabs) | `tndk-accounts` |
| Bill the advance | Invoice `INV-NNN/YYYY` | `tndk-accounts` |

**The award's payment terms govern**, even where the quotation said something else. Say so
explicitly, then bill on the award.

**Creates:** the payment schedule as dated milestones, plus any precondition the award attaches
(bank guarantee, insurance, submittals). A precondition is an open loop from day one — the
Mesaieed contract has collected QAR 0 against 400,000 because an advance bank guarantee has sat
unposted since the LOA was dated.

**A verbal award with materials about to be ordered is an escalation**, not a paperwork task.
Recommend written confirmation first.

### 3 — Procurement

*Trigger: materials need ordering, a vendor quoted, "raise a PO to ...".*

| Step | Document | Skill |
|---|---|---|
| Vendor RFQ / comparison | — | — |
| Purchase order | `LPO-NNN/YYYY` | `tndk-lpo` |
| Record committed spend | expenses tab of the project workbook | `tndk-accounts` |

Issuing an LPO commits real money and always needs Farhan's approval. Vendor POs may be in SR,
AED or USD — client documents stay QAR.

**Creates:** an exposure to watch — committed vendor spend against a contract that has not
collected yet.

### 4 — Delivery

*Trigger: materials went to site, "we delivered yesterday".*

| Step | Document | Skill |
|---|---|---|
| Delivery note `DN-NNN/YYYY` | | `tndk-accounts` |
| Check whether a milestone just fell due | milestone invoice, if so | `tndk-accounts` |

**Creates:** in most payment schedules, delivery triggers the next invoice. Raise it within
three working days rather than waiting to be asked.

### 5 — Payment lands

*Trigger: a cheque photo, a transfer slip, "Suresh paid 20k".*

| Step | Document | Skill |
|---|---|---|
| Receipt `RCT-NNN/YYYY`, capturing the instrument | | `tndk-accounts` |
| Rebuild both registers | Approved Works + Amounts to Receive | `tndk-accounts` |
| Shortfall check against the agreed percentage | flag in QAR, carry forward | — |

Recording a payment as received needs an actual instrument — a cheque number, a transfer
reference, or an explicit "cash" — and Farhan's confirmation. Cheque receipts carry
*"subject to realization of cheque."*

Check the allocation: if the drawer's name or the narration points at a different project than
the one being credited, stop and ask.

**Creates:** a moved or closed loop, and a revised outstanding balance that must carry its
"as of" date wherever it is quoted.

### 6 — Settlement and after

*Trigger: final payment, project completed, warranty running out.*

| Step | Document | Skill |
|---|---|---|
| Final receipt, project marked fully paid | | `tndk-accounts` |
| Record the warranty end date | project file | — |
| Draft the AMC approach, 60 days before expiry | proposal | `tndk-coldroom-quotation` |

Every installed room is a maintenance contract nobody has asked for yet. AMC value across the
book is currently QAR 0.

---

## Numbering

Read the log before issuing. Append after issuing. Every time, without exception — a reused
number corrupts every register that references it.

The live log is `references/numbering-log.md` inside the `tndk-accounts` skill.

| Series | Format | Notes |
|---|---|---|
| Invoice | `INV-NNN/YYYY` | Main series runs from INV-251 upward |
| Receipt | `RCT-NNN/YYYY` | |
| Quotation | `QUT/DCTS/NNN/YYYY` | Keeps the DCTS reference form |
| Delivery note | `DN-NNN/YYYY` | |
| Purchase order | `LPO-NNN/YYYY` | Vendor-side |

A client with an inherited series keeps it — Ruwais Farm runs its own `INV-014/2026`. On a
collision, renumber the **newer** document to the next free main-series number; the older one
is already out in the world.

Writing to the numbering log is an approval gate. It is the anti-collision mechanism, so
changes to it are deliberate.

---

## Filing tree

Instructions live in the repo. **Data lives in Google Drive.** Never copy register data into
the repo — that duplication is exactly what produced three different answers for one client.

```
TNDK Documents/
├── 01 - Projects/
│   └── <Client>/          quotation · invoices · receipts · delivery notes ·
│                          project workbook · expense & profit record
├── 02 - Registers/
│   ├── approved_register.xlsx      every award to date
│   ├── amounts_to_receive.xlsx     outstanding, split maintenance / project
│   └── margin_log.xlsx             quoted vs cost vs realised margin
└── 03 - Under process/    live jobs not yet awarded
```

File names read like a human wrote them: `Invoice INV-253-2026 (Advance).pdf`,
`Receipt RCT-254-2026.pdf`. Deliver the PDF **and** the editable source.

Creating new files in Drive is fine. Overwriting a register needs approval — prefer a new
dated version. Deleting anything is forbidden; supersede and mark instead.

---

## Open loops each stage creates

The loops matter more than the documents, because a loop nobody is holding is how money stops
moving. Every loop needs an owner and a date.

| Stage | Loop it creates |
|---|---|
| Quotation issued | Follow-up at validity expiry (15 days standard) |
| Award received | Every precondition — guarantee, insurance, submittal — dated weekly until cleared |
| Award received | Each payment milestone, dated to its trigger event |
| LPO issued | Committed spend exposed to an uncollected contract |
| Delivery made | Milestone invoice due within 3 working days |
| Payment short | Shortfall in QAR, carried onto the next invoice |
| Project completed | Warranty end date, and an AMC approach 60 days before it |

---

## Reading an award

When an LPO or LOA arrives, extract these before producing anything. If a field is genuinely
absent from the document, ask — do not carry the quotation's value across and hope.

- Award reference and date
- Client's legal name as written on the award (it may differ from how everyone says it)
- Contract value — and whether it matches the quotation; if not, **that is the headline**
- Payment schedule: each stage, its percentage or amount, and its trigger event
- Preconditions: bank guarantee, insurance, submittals, retention
- Delivery period and any penalty clause
- Who signs and who receives invoices

Where the award and the quotation disagree, the award governs — and the disagreement gets
stated out loud, not absorbed.
