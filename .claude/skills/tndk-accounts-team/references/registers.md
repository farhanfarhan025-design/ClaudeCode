# Registers and the close.py input

Two registers do not exist yet and have to be built: **payables** and **instruments**. This
file gives their schemas, the input contract for `scripts/close.py`, and how to build each one
from what TNDK already has.

## Contents

- [Where registers live](#where-registers-live)
- [Payables register](#payables-register)
- [Instrument register](#instrument-register)
- [close.py input fields](#closepy-input-fields)
- [Building a register from scratch](#building-a-register-from-scratch)

---

## Where registers live

```
TNDK Documents/02 - Registers/
├── approved_register.xlsx      every award to date            (LEDGER)
├── amounts_to_receive.xlsx     outstanding, maintenance/project (COLLECT)
├── margin_log.xlsx             quoted vs cost vs realised      (PRICE)
├── payables_register.xlsx      NEW — what TNDK owes            (PAYABLES)
├── instrument_register.xlsx    NEW — cheques and transfers     (CASHBOOK)
└── close/YYYY-MM/              NEW — dated close packs         (ACCOUNTS-LEAD)
```

Drive holds the data; skills and repos hold instructions. **Never copy register data into a
skill or a repo.** Duplication is what produced three different answers for one client. Read
from Drive, compute, write back a new dated version — overwriting needs approval.

---

## Payables register

One row per bill. A bill is money owed whether or not anyone has asked for it yet.

| Column | Notes |
|---|---|
| `vendor` | as written on the bill |
| `bill_ref` | vendor's own invoice number |
| `bill_date` | |
| `lpo_ref` | **the control.** No LPO → stop, do not schedule |
| `lpo_amount` | what was committed, for the variance check |
| `project` | ties the bill to a contract for the exposure check |
| `currency` | QAR default; SR / AED / USD / EUR possible |
| `rate_used` | only if not QAR — never convert silently |
| `amount` | in billed currency |
| `amount_qar` | converted, with the rate above stated |
| `due_date` | from the vendor's terms — never assume 30 days |
| `status` | open · queried · scheduled · paid · held |
| `paid_date` | |
| `instrument` | cheque no. / transfer ref used to pay it |
| `note` | why held, what was queried, what PROCURE said |

**Committed-but-not-yet-billed** is a second sheet, not a status: `lpo_ref · vendor · project ·
amount · expected_delivery`. An issued LPO with no bill yet is still money owed, and leaving it
out understates what TNDK is committed to.

---

## Instrument register

One row per instrument — not per receipt. A receipt can be settled by two cheques; each is
tracked separately because each can bounce separately.

| Column | Notes |
|---|---|
| `receipt_ref` | `RCT-NNN/YYYY` this instrument sits behind |
| `invoice_ref` | what it is allocated against. Blank = **unallocated**, report it |
| `client` | |
| `project` | for the allocation check — drawer vs project mismatches matter |
| `type` | cheque · transfer · cash |
| `number` | cheque number, or transfer reference |
| `bank` | |
| `drawer` | whose account it is drawn on — often not the client's own name |
| `instrument_date` | for a post-dated cheque this is the **future** date, not receipt date |
| `received_date` | |
| `amount` | |
| `status` | held · deposited · cleared · bounced · returned |
| `status_date` | when it last changed |
| `purpose` | payment · security · performance · retention release |

**Security and performance cheques are obligations, not cash.** Mark them by `purpose` and keep
them out of every cash figure.

**Post-dated cheques** are tracked by `instrument_date`. A cheque dated six weeks out is not
this month's money.

---

## close.py input fields

JSON. Everything is optional — **omit what you don't have rather than filling it with zero.**
An omitted section is reported as UNKNOWN, which is accurate; a zero is a lie that balances.

```jsonc
{
  "as_of": "2026-08-04",              // required — every figure is stated as of this date

  "register": [                        // the Approved Works Register rows
    {
      "project": "…",
      "client": "…",
      "contract": 46000,               // required for the row to be counted
      "received": 27600,               // required — omit the row rather than guessing
      "balance": 18400,                // optional: the STORED balance, checked against computed
      "due_since": "2026-06-20",       // optional: enables ageing; omit if blocked on a milestone
      "cost": 34500                    // optional: enables the margin column
    }
  ],

  "numbering": { "INV": [251, 252, 254], "RCT": [251] },   // issued numbers per series

  "receipts":    [ { "ref": "RCT-255/2026", "client": "…", "amount": 27600, "date": "…" } ],

  "instruments": [ { "receipt_ref": "RCT-255/2026", "invoice": "INV-252/2026",
                     "type": "cheque", "number": "000451", "bank": "…", "drawer": "…",
                     "date": "…", "amount": 27600, "status": "cleared" } ],

  "cheques_issued": [ { "number": "000112", "payee": "…", "amount": 41000, "presented": false } ],

  "opening_cash": null,                // null = not confirmed. Never estimate it.

  "payables": [ { "vendor": "…", "bill": "…", "lpo": "LPO-188/2026", "lpo_amount": 41000,
                  "project": "…", "amount": 41000, "due": "2026-08-12", "status": "open" } ],

  "committed_not_billed": [ { "lpo": "LPO-189/2026", "vendor": "…", "project": "…",
                              "amount": 62000 } ]
}
```

### What each omission costs you

| Omitted | Consequence |
|---|---|
| `register` | nothing can be computed — this is the spine |
| `receipts` or `instruments` | the three-way tie-out cannot run |
| `opening_cash` | cash on hand reported as UNKNOWN; flows still computed |
| `payables` | "what do we owe" stays unanswerable |
| `committed_not_billed` | committed spend understated, exposure check weakened |
| `due_since` on a row | that row is outstanding but not ageable |
| `cost` on a row | the book shows revenue but not profit for that row |

---

## Building a register from scratch

**Payables**, in this order. It is the one with money attached to being wrong, so build it first.

1. List every LPO issued that has not been fully settled — from the LPO numbering series and
   PROCURE's records.
2. For each, ask: has a bill arrived? Bill → payables rows. No bill →
   committed-but-not-yet-billed.
3. Match each bill to its LPO on quantity, rate and total. Any difference is a **variance to
   report in QAR**, not something to reconcile away.
4. Get vendor terms for each, and compute due dates. Missing terms is a question for Farhan,
   not a 30-day default.
5. Run `close.py` and read the VARIANCE block. Bills with no LPO are the first thing to resolve.

**Instruments.** Every logged receipt already names its instrument — the convention has been
followed on the documents, it was just never carried forward.

1. Walk the receipt series and pull the instrument details off each receipt.
2. Set status from what is known: cash → `cleared`; transfer → `cleared` unless told otherwise;
   cheque → `held` unless Farhan confirms it cleared. **When unknown, leave it uncleared** —
   overstating cleared cash is the error that costs money.
3. Flag any receipt whose instrument details cannot be found. A received amount with no
   instrument behind it is a variance, not a rounding issue.
4. Ask Farhan to confirm the opening cash position once. Until he does, the position is
   reported as UNKNOWN — and that is a correct report, not a failed one.
