# TNDK AI Agent System

An agent ecosystem for **The New Doha Kitchen Equipment Services W.L.L.**, built on Dan
Martell's DATA / AGENT framework and adapted to how TNDK actually operates.

Built 3 August 2026 for Farhan (owner).

---

## Start here

| If you want to… | Read |
|---|---|
| Know what was found and why it matters | `analysis/FINDINGS.md` |
| Understand the whole design | this file |
| Deploy the first agent | `agents/price/` + the deployment sequence below |
| Understand the sales side | `agents/sales/README.md` + `analysis/SALES_FINDINGS.md` |
| Know what's blocking | `memory/open_loops.md` |
| Know the rules | `RULES.md` |

## The architecture

```
FARHAN (owner — goals, risk, pricing authority, all approvals)
│
├── TNDK-OPS (manager) — delivery. Diagnose · route · review · report. Never executes.
│   │
│   ├── SCOPE     enquiry → technical definition          Stage 2
│   ├── PRICE     cost → margin → price                   Stage 2  ★ built
│   ├── PROCURE   vendor → LPO → committed spend          Stage 2
│   ├── LEDGER    invoice · receipt · register integrity  Stage 3
│   ├── COLLECT   milestones · guarantees · follow-ups    Stage 2
│   └── ANNUITY   warranty → AMC → recurring revenue      Stage 1
│
└── TNDK-SALES (manager) — demand. Peer of TNDK-OPS, not subordinate to it.
    │
    ├── PROSPECT  market → target list → approach         Stage 1  (blocked on D-010)
    ├── QUALIFY   enquiry → qualified or declined         Stage 2
    ├── PURSUE    quotation → decision → win/loss record  Stage 2  ★ built
    └── ACCOUNT   delivered job → repeat work → referral  Stage 1
```

**One agent, one lane.** SCOPE defines what is built; PRICE decides what it costs. That
separation is the structural fix for the margin problem — the person who wants the job does
not set the number alone.

The sales division is that same principle applied to the lane with the strongest reason to break
it: **no sales agent touches a price, a discount or a delivery date, ever, at any trust stage**
(`RULES.md` A9). The two divisions exchange work through two explicit handoffs — a qualified
enquiry going in, an issued quotation coming back.

## Why PRICE first

The pricing guide sets 30% markup as the default. Its own worked example prices at **14.6%** —
below the 20% competitive-tender floor. Nothing computed realised margin at the moment of
quoting, so the gap was invisible.

Across a 758,100 book, five margin points is about **QAR 38,000**.

## Why PURSUE first on the sales side

Quotation numbering has reached `QUT/DCTS/066/2026`. Eight awards are recorded. **Nothing records
a quotation that lost** — not the client, not the value, not the reason.

That gap is what makes the margin question unanswerable. The defence of a low price is always "we
needed it to win", and nobody recorded whether the low prices won. PURSUE produces the win/loss
record that turns G1 from an argument into a measurement.

It also needs no new demand, no capacity decision and no outbound contact — it works quotations
that have already been issued. See `analysis/SALES_FINDINGS.md`.

## Files

```
AI-Agent-System/
├── USER.md              who the system works for
├── GOALS.md             G1-G8, each with a metric and a baseline
├── RULES.md             prohibitions · approval gates · standing conventions
├── TOOLS.md             permission register — Drive only
├── MANAGER.md           TNDK-OPS: routing, review gate, report formats
├── MEMORY_POLICY.md     what may be stored, retrieved, superseded
├── HEARTBEAT.md         weekly / monthly cycles
├── DECISIONS.md         owner rulings, including 5 unresolved
├── agents/
│   ├── price/           ★ full build: SOUL · IDENTITY · PLAYBOOK · EXAMPLES
│   │                      · QA_CHECKLIST · OUTPUT_SCHEMA · SYSTEM_PROMPT · TESTS
│   ├── scope|procure|ledger|collect|annuity/   IDENTITY (lane contracts)
│   ├── sales/
│   │   ├── README.md    the sales division: why, boundaries, sequence
│   │   ├── MANAGER.md   TNDK-SALES: routing, review gate, pipeline report
│   │   ├── pursue/      ★ full build (same eight files as price/)
│   │   └── prospect|qualify|account/           IDENTITY (lane contracts)
│   └── TEMPORARY_SPECIALIST.md
├── memory/              durable_facts · preferences · open_loops · lessons
├── logs/                overrides · actions · failures
├── analysis/
│   ├── FINDINGS.md      the evidence — delivery side
│   └── SALES_FINDINGS.md the evidence — demand side
├── skills/
│   └── tndk-sales-pipeline/  the sales division packaged as a Claude skill,
│                             alongside tndk-coldroom-quotation and tndk-accounts
└── scripts/
    ├── margin.py        cost build-up + floor check     (verified)
    ├── build_register.py corrected registers            (verified)
    ├── pipeline.py      conversion + pipeline analysis  (verified)
    └── examples/        suresh.json · awards.json · pipeline.json
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

# Pipeline, conversion, and what each open quote does to concentration
python3 scripts/pipeline.py --data scripts/examples/pipeline.json \
                            --awards scripts/examples/awards.json
```

`margin.py` reproduces the pricing guide's worked example to the riyal (direct 43,448.45,
cost 51,465.72). `build_register.py` asserts every total against source data before writing.
`pipeline.py` flags quotations past validity or gone quiet (exit 2), and **refuses** to print a
win rate from thin or wins-only data rather than printing a confident wrong one.

## Deployment sequence

**Week 1 — decide.** Six rulings are blocking (`memory/open_loops.md`):
the margin floor (D-004), the VAT wording (D-005), the Samoosa contract value (D-006),
whether to publish the corrected registers, the delivery capacity ceiling (D-010), and what the
quotation series actually counts (D-011).

**Week 1 — fix the register.** It currently reports 18,250 against a real book of 758,100.
Every decision made from it is being made on wrong numbers.

**Weeks 2–4 — run PRICE in observation.** Re-price the last 10 quotations. Compare computed
cost to what was actually charged. This produces the real margin baseline — the 14.6% figure
comes from a single documented example, not a trend.

**Week 5 — PRICE to draft mode.** Every new quote gets a cost build-up first.

**Week 6 — start COLLECT.** Weekly cycle. Mesaieed bank guarantee as a standing item.

**Week 8+ — ANNUITY.** Warranty register first, then AMC proposals.

Nothing gets promoted on a good demo. See the promotion gates in `agents/price/TESTS.md`.

**The sales division also ships as a skill.** `skills/tndk-sales-pipeline/` packages the PURSUE
workflow, the qualification and account/prospect guidance, and both scripts into a Claude skill
that triggers on ordinary sales language — "quotation sent", "chase them", "did we win that
one". It is the same instructions in the form Farhan already uses for quotations, LPOs and
accounts, and it is the fastest route from this repo to something he actually runs.

**In parallel, on the sales side** (`agents/sales/README.md` has the detail): PURSUE reconstructs
the quotation history in week 1 and runs live from week 2; QUALIFY starts at week 6; ACCOUNT and
then PROSPECT from week 10. The sequence is deliberate — conversion and filtering come before any
agent generates new demand, because delivery capacity has not been established (D-010).

## Trust model

| Stage | Agent may | Farhan |
|---|---|---|
| 1 Observe | analyse, recommend | reviews reasoning |
| 2 Draft | prepare work, propose actions | approves every external item |
| 3 Limited execute | allow-listed low-risk actions | reviews logs |
| 4 Autonomous | run on schedule | monitors summaries |

**Sending never gets promoted.** No agent sends anything to a client, vendor or bank at any
stage. That is `RULES.md` A2 — a design decision, not a trust level. Agents draft; Farhan sends.

## Framework mapping

| Martell | Here |
|---|---|
| DATA loop | `MANAGER.md`, and every agent's method |
| Rule of R | Applied in `analysis/FINDINGS.md` to pick PRICE first |
| Aim | `GOALS.md` — eight outcomes with metrics |
| Give it identity | `SOUL.md` / `IDENTITY.md` per agent; one shared `USER.md` |
| Equip it | `scripts/`, playbooks, examples, `TOOLS.md`, `memory/` |
| Narrow the scope | Ten lanes under two managers, explicit out-of-lane returns |
| Trust in stages | Per-agent stage + `TESTS.md` promotion gates |
| Heartbeat | `HEARTBEAT.md` |

**One deliberate deviation:** the handbook gives each agent its own `USER.md`. Here there is
one shared `USER.md` at root. Six copies of "who Farhan is" would drift, and drift is the
failure this system exists to fix.
