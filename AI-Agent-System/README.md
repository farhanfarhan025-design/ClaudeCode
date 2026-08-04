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
| Know what's blocking | `memory/open_loops.md` |
| Know the rules | `RULES.md` |

## The architecture

```
FARHAN (owner — goals, risk, pricing authority, all approvals)
│
└── TNDK-OPS (manager) — diagnose · route · review · report. Never executes.
    │
    ├── SCOPE     enquiry → technical definition          Stage 2
    ├── PRICE     cost → margin → price                   Stage 2  ★ built
    ├── PROCURE   vendor → LPO → committed spend          Stage 2
    ├── LEDGER    invoice · receipt · register integrity  Stage 3
    ├── COLLECT   milestones · guarantees · follow-ups    Stage 2
    └── ANNUITY   warranty → AMC → recurring revenue      Stage 1
```

**One agent, one lane.** SCOPE defines what is built; PRICE decides what it costs. That
separation is the structural fix for the margin problem — the person who wants the job does
not set the number alone.

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
│   └── TEMPORARY_SPECIALIST.md
├── memory/              durable_facts · preferences · open_loops · lessons
├── logs/                overrides · actions · failures
├── analysis/FINDINGS.md the evidence
└── scripts/
    ├── margin.py        cost build-up + floor check   (verified)
    ├── build_register.py corrected registers          (verified)
    └── examples/        suresh.json · awards.json
```

**Instructions live here. Data lives in Google Drive.** Never copy register data into this
repo — that duplication is what produced three different answers for Samoosa
(`memory/lessons.md` L-003).

## George — the paperwork person

`.claude/skills/george/` is the operator-facing front door to all of this. Where the agents
above are lanes, George is a person: give him a scrap — a forwarded message, a photo of an LPO,
"Suresh paid 20k" — and he works out which chain of documents it belongs to, produces them
through the existing generators (`tndk-accounts`, `tndk-lpo`, `tndk-coldroom-quotation`),
verifies them, numbers them, files them, updates the registers, and hands back a short note
saying what still needs Farhan.

He carries `RULES.md` section A as hard limits, and `scripts/check_document.py` enforces the
ones a script can see — the tax prohibition, the payee wording, numbering, signatories.

```bash
# make him available outside this repo
cp -r .claude/skills/george ~/.claude/skills/

# verify a finished document before it goes out
python3 .claude/skills/george/scripts/check_document.py --type invoice "Invoice INV-253-2026.pdf"
```

## Scripts

```bash
# Cost build-up and price ladder
python3 scripts/margin.py --config scripts/examples/suresh.json

# Check a proposed price against the floor (exit code 2 = below floor)
python3 scripts/margin.py --config scripts/examples/suresh.json --price 59000

# Rebuild both registers with verified arithmetic
python3 scripts/build_register.py --data scripts/examples/awards.json --outdir ./out
```

`margin.py` reproduces the pricing guide's worked example to the riyal (direct 43,448.45,
cost 51,465.72). `build_register.py` asserts every total against source data before writing.

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
| Aim | `GOALS.md` — six outcomes with metrics |
| Give it identity | `SOUL.md` / `IDENTITY.md` per agent; one shared `USER.md` |
| Equip it | `scripts/`, playbooks, examples, `TOOLS.md`, `memory/` |
| Narrow the scope | Six lanes, explicit out-of-lane returns |
| Trust in stages | Per-agent stage + `TESTS.md` promotion gates |
| Heartbeat | `HEARTBEAT.md` |

**One deliberate deviation:** the handbook gives each agent its own `USER.md`. Here there is
one shared `USER.md` at root. Six copies of "who Farhan is" would drift, and drift is the
failure this system exists to fix.
