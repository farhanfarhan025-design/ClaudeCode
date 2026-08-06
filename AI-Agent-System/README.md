# TNDK AI Agent System

An agent ecosystem for **The New Doha Kitchen Equipment Services W.L.L.**, built on Dan
Martell's DATA / AGENT framework and adapted to how TNDK actually operates.

Built 3 August 2026 for Farhan (owner). HR team added 6 August 2026.

---

## Start here

| If you want to… | Read |
|---|---|
| Know what was found and why it matters | `analysis/FINDINGS.md` |
| Understand the whole design | this file |
| Deploy the first agent | `agents/price/` + the deployment sequence below |
| Set up staff and payroll | `agents/hr/HR_MANAGER.md` + the HR track below |
| Know what's blocking | `memory/open_loops.md` |
| Know the rules | `RULES.md` |

## The architecture

```
FARHAN (owner and employer — goals, risk, pricing authority, all approvals)
│
└── TNDK-OPS (manager) — diagnose · route · review · report. Never executes.
    │
    ├── SCOPE     enquiry → technical definition          Stage 2
    ├── PRICE     cost → margin → price                   Stage 2  ★ built
    ├── PROCURE   vendor → LPO → committed spend          Stage 2
    ├── LEDGER    invoice · receipt · register integrity  Stage 3
    ├── COLLECT   milestones · guarantees · follow-ups    Stage 2
    ├── ANNUITY   warranty → AMC → recurring revenue      Stage 1
    │
    └── TNDK-HR (sub-manager) — everything to do with people
        ├── PEOPLE   hiring · contracts · permits · files   Stage 1
        ├── TIME     attendance · leave · hours per job     Stage 1
        ├── PAYROLL  monthly run · WPS · payslips           Stage 1  ★ built
        └── EXIT     gratuity · settlement · clearance      Stage 1
```

**One agent, one lane.** SCOPE defines what is built; PRICE decides what it costs. That
separation is the structural fix for the margin problem — the person who wants the job does
not set the number alone. The HR team repeats the pattern: TIME records the hours, PAYROLL
prices them.

## Why an HR team

The commercial lanes were built first, and they left a hole that shows up in their own numbers:

- **`margin.py` charges labour at a flat 15% of direct cost** — QAR 6,517 on the documented
  Suresh example — and nobody has ever checked it against an hour actually worked. Every
  margin figure rests on it.
- **Wages are the one outflow that cannot wait for a slow client**, on a book with QAR 614,350
  outstanding and a 400,000 contract that has collected nothing. The weekly brief tracked
  vendor commitments and never the wage bill.
- **End-of-service gratuity accrues against no register.** It arrives as a single cash demand.

So HR here is not an administration function bolted on. It closes a hole in the margin numbers
and a hole in the cash picture — and it is where a legal deadline lives, which is why PAYROLL
was built to completion first. See `agents/hr/HR_MANAGER.md`.

**It cannot run yet.** There is no roster: no employee record, wage, permit or bank detail
exists in this system (OL-013). Everything in `agents/hr/` is built and tested against an
**invented** sample that names nobody.

## Why PRICE first

The pricing guide sets 30% markup as the default. Its own worked example prices at **14.6%** —
below the 20% competitive-tender floor. Nothing computed realised margin at the moment of
quoting, so the gap was invisible.

Across a 758,100 book, five margin points is about **QAR 38,000**.

## Files

```
AI-Agent-System/
├── USER.md              who the system works for
├── GOALS.md             G1-G6, each with a metric and a baseline
├── RULES.md             prohibitions · approval gates · standing conventions
├── TOOLS.md             permission register — Drive only
├── MANAGER.md           TNDK-OPS: routing, review gate, report formats
├── MEMORY_POLICY.md     what may be stored, retrieved, superseded
├── HEARTBEAT.md         weekly / monthly cycles
├── DECISIONS.md         owner rulings, including 3 unresolved
├── agents/
│   ├── price/           ★ full build: SOUL · IDENTITY · PLAYBOOK · EXAMPLES
│   │                      · QA_CHECKLIST · OUTPUT_SCHEMA · SYSTEM_PROMPT · TESTS
│   ├── scope|procure|ledger|collect|annuity/   IDENTITY (lane contracts)
│   ├── hr/
│   │   ├── HR_MANAGER.md    TNDK-HR: routing, interfaces, the people brief
│   │   ├── LABOUR_LAW.md    every statutory parameter — all UNVERIFIED
│   │   ├── payroll/         ★ full build, same eight files as price/
│   │   └── people|time|exit/  IDENTITY (lane contracts)
│   └── TEMPORARY_SPECIALIST.md
├── memory/              durable_facts · preferences · open_loops · lessons
├── logs/                overrides · actions · failures
├── analysis/FINDINGS.md the evidence
└── scripts/
    ├── margin.py        cost build-up + floor check   (verified)
    ├── build_register.py corrected registers          (verified)
    ├── payroll.py       payroll · compliance · gratuity (verified)
    └── examples/        suresh.json · awards.json · payroll_roster.json
```

**Instructions live here. Data lives in Google Drive.** Never copy register data into this
repo — that duplication is what produced three different answers for Samoosa
(`memory/lessons.md` L-003).

## Scripts

```bash
# Cost build-up and price ladder
python3 scripts/margin.py --config scripts/examples/suresh.json

# Check a proposed price against the floor (exit code 2 = below floor)
python3 scripts/margin.py --config scripts/examples/suresh.json --price 59000

# Rebuild both registers with verified arithmetic
python3 scripts/build_register.py --data scripts/examples/awards.json --outdir ./out

# HR: compliance sweep + accrued gratuity liability   (exit code 2 = blocking failure)
python3 scripts/payroll.py check --roster scripts/examples/payroll_roster.json \
                                 --as-of 2026-08-06

# HR: monthly run, and a draft WPS file if nothing is blocking
python3 scripts/payroll.py run --roster scripts/examples/payroll_roster.json \
                               --period scripts/examples/payroll_2026_08.json --sif ./out

# HR: end-of-service settlement for one leaver
python3 scripts/payroll.py eos --roster scripts/examples/payroll_roster.json \
                               --employee TNDK-002 --last-day 2026-09-30
```

`margin.py` reproduces the pricing guide's worked example to the riyal (direct 43,448.45,
cost 51,465.72). `build_register.py` asserts every total against source data before writing.
`payroll.py` computes wages, statutory gates and gratuity, and **withholds the WPS file
whenever anything is blocking** — verified against the invented sample roster, case by case,
in `agents/hr/payroll/TESTS.md`.

> The payroll examples name nobody real. They exist because a calculator needs test data and
> test data must never be a real person (`RULES.md` A11).

## Deployment sequence

**Week 1 — decide.** Four rulings are blocking (`memory/open_loops.md`):
the margin floor (D-004), the VAT wording (D-005), the Samoosa contract value (D-006),
and whether to publish the corrected registers.

**Week 1 — fix the register.** It currently reports 18,250 against a real book of 758,100.
Every decision made from it is being made on wrong numbers.

**Weeks 2–4 — run PRICE in observation.** Re-price the last 10 quotations. Compare computed
cost to what was actually charged. This produces the real margin baseline — the 14.6% figure
comes from a single documented example, not a trend.

**Week 5 — PRICE to draft mode.** Every new quote gets a cost build-up first.

**Week 6 — start COLLECT.** Weekly cycle. Mesaieed bank guarantee as a standing item.

**Week 8+ — ANNUITY.** Warranty register first, then AMC proposals.

Nothing gets promoted on a good demo. See the promotion gates in `agents/price/TESTS.md`.

### The HR track — runs alongside, blocked on three answers

**Week 1 — the roster.** Who works for TNDK, and are they employees or subcontractors
(OL-013)? Nothing else in HR can start, and the answer changes what is legally owed.

**Week 1 — the parameters.** Confirm `agents/hr/LABOUR_LAW.md` and rule on the divisor
conventions in D-008. A wrong parameter is wrong every month, for everyone, silently.

**Week 2 — the two numbers nobody has.** With a roster, one command produces the committed
monthly wage bill and the accrued gratuity liability. Both go into the weekly brief.
This is the highest-value hour in the whole HR track, and it does not need anyone to be paid.

**Week 2 — WPS.** Get the establishment ID and the bank's SIF template, and verify the file
layout against it (OL-014). A correctly computed file in the wrong format is a rejected
payment, which becomes a late wage.

**Weeks 3–4 — TIME in observation.** Start with the simplest sheet Farhan will actually
maintain. Book hours against CCC/HIA and Mesaieed. This is what finally tests the 15% labour
assumption every margin in this system depends on (G8).

**Week 5 — PAYROLL to draft mode.** First live run is a reconciliation exercise, not a
payment instruction: every line checked against a contract before anything is approved.

The order is deliberate. PAYROLL is built and tested, but running it on an unverified roster
with unverified parameters would produce confident, wrong numbers in people's wages — the
exact failure `memory/lessons.md` L-002 is about.

## Trust model

| Stage | Agent may | Farhan |
|---|---|---|
| 1 Observe | analyse, recommend | reviews reasoning |
| 2 Draft | prepare work, propose actions | approves every external item |
| 3 Limited execute | allow-listed low-risk actions | reviews logs |
| 4 Autonomous | run on schedule | monitors summaries |

**Sending never gets promoted.** No agent sends anything to a client, vendor or bank at any
stage. That is `RULES.md` A2 — a design decision, not a trust level. Agents draft; Farhan sends.

**Three more things never promote, all on the HR side:**

- **Payroll approval and the WPS upload stay with Farhan.** He is the employer. The system
  prepares the run; he approves it and uploads the file himself.
- **Confidentiality never relaxes.** One person's pay, permit or medical detail goes to
  Farhan and nobody else, at any stage (`RULES.md` A10).
- **A statutory minimum is the one gate Farhan cannot override** (D-010). Every other rule in
  this system is his to overrule as owner; a minimum wage is not his to waive.

## Framework mapping

| Martell | Here |
|---|---|
| DATA loop | `MANAGER.md`, and every agent's method |
| Rule of R | Applied in `analysis/FINDINGS.md` to pick PRICE first |
| Aim | `GOALS.md` — six outcomes with metrics |
| Give it identity | `SOUL.md` / `IDENTITY.md` per agent; one shared `USER.md` |
| Equip it | `scripts/`, playbooks, examples, `TOOLS.md`, `memory/` |
| Narrow the scope | Six lanes, explicit out-of-lane returns |
| Trust in stages | Per-agent stage + `TESTS.md` promotion gates |
| Heartbeat | `HEARTBEAT.md` |

**One deliberate deviation:** the handbook gives each agent its own `USER.md`. Here there is
one shared `USER.md` at root. Six copies of "who Farhan is" would drift, and drift is the
failure this system exists to fix.
