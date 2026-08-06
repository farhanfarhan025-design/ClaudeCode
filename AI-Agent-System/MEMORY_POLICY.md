# MEMORY POLICY

Memory exists so Farhan stops re-teaching the same correction. It is not a diary.

## Three tiers

| File | Holds | Changes |
|---|---|---|
| `memory/durable_facts.md` | Client registry, contract values, LPO/LOA terms, guarantee obligations, warranty dates | When a fact changes — with date and source |
| `memory/preferences.md` | Standing conventions, format rules, things corrected before | Rarely. Every entry traces to a real correction |
| `memory/open_loops.md` | Anything awaiting someone: guarantees, milestones, unpaid balances, unanswered questions | Constantly. Closed loops move out |
| `memory/lessons.md` | What went wrong and what rule changed as a result | On every corrected failure |

## Record format

Every memory entry carries:

```
Statement:   [the fact]
Source:      [file, document number, or "Farhan, <date>"]
Date:        [when established]
Confidence:  high / medium / low
Scope:       [which agent(s) it binds]
Status:      current / superseded → [link]
```

A fact without a source is not a fact. Write it as an assumption or ask.

## May store

- Preferences Farhan has confirmed or corrected.
- Durable commercial facts: contract values, payment terms, client references, LPO numbers.
- Approved decisions and their reasoning (these also go in `DECISIONS.md`).
- Open loops with an owner and a date.
- Corrections that change a playbook — with the playbook version they changed.

## Must not store

- Bank credentials, cheque images beyond the reference details, or any secret.
- Guesses written as facts.
- Client personal data beyond what the commercial relationship needs.
- Speculation about a client's finances or intentions.
- Superseded decisions without marking them superseded.
- Anything copied "just in case" — that is how context rot starts.

## Personal data — stricter than everything above

The HR lanes handle people's data, not the company's. The rules there are tighter, and they
do not relax with trust stage.

**May be stored in this repo:**

- Headcount, and the *existence* of a lane's obligations ("a roster is required", "gratuity
  accrues from year one").
- Confirmed policy: divisor conventions, the payroll cut-off date, the leave year.
- Open loops with an owner and a date, written with an **employee ID** and no name.

**Must never be stored in this repo, in any file, including memory and logs:**

- A name, QID, passport or visa number, address, or bank detail.
- A wage, allowance, deduction, advance balance or settlement figure for a real person.
- Medical information, a grievance, or a disciplinary matter — in any form, summarised or not.
- A scan or photograph of any identity or medical document.

All of it lives in Drive (`04 - HR/`), where access can be scoped per employee. `RULES.md`
A11. The examples in `scripts/examples/` are invented for exactly this reason: the calculator
needed test data, and test data must never be a real person.

**One consequence worth stating plainly:** an HR agent cannot answer a question about an
employee from memory. It re-reads the source every time. That is slower, and it is the point.

## Retrieval discipline

**Load narrowly.** An agent pricing a Samoosa variation needs: the Samoosa row, the quotation
terms, the pricing guide. It does **not** need the CCC contract, the Mesaieed LOA, or the
full client registry.

The failure mode here is specific and worth naming: with 8 clients and 4 register files, it is
tempting to load everything because it's small. Do not. The habit needs to survive to 80 clients.

## Conflict rule

1. A current instruction from Farhan **always** wins over stored memory.
2. When memory conflicts with a live document (LPO, register, receipt), **the document wins**
   — and the conflict gets reported, not silently resolved.
3. After any conflict, propose the memory update explicitly. Do not update silently.

## Known live conflict

> `numbering-log.md` and the skill's `register_data.json` show **Samoosa at 39,375 contract /
> 31,500 received** (including an 875 chequered-sheet variation).
> The live `approved_register.xlsx` in Drive shows **38,500 / 20,000**.
> Logged receipts support only **20,000** (RCT-256).
>
> Three sources, three answers. **LEDGER must resolve this with Farhan before either figure
> is used on a document.** Recorded in `memory/open_loops.md`.
