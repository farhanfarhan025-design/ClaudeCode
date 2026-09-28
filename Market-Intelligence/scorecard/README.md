# Agent scorecard

Twenty-three agents write a lot of confident analysis. This grades every call they make
against what the market actually did, and answers the questions nothing else can:

- Which agents are **right more often than chance**, and which are just expensive noise?
- Does a lead add anything its analysts don't?
- When an agent says "80% confident", is it right 80% of the time?

Standard-library Python 3. No installs, no API keys.

## How it works

```
agent packs ──CALL lines──▶ ingest ──▶ ledger/calls.jsonl  (append-only, hash-chained)
                                               │
                    daily closes (CSV) ───▶ score ──▶ report: per agent · per lead · calibration
```

1. **Agents end each pack with CALL lines**: one per stock view (format below).
2. **`ingest`** pulls those lines into the ledger and stamps the time they were logged.
3. **`score`** grades each call 1, 5 and 20 trading days out, *after removing the NIFTY move*,
   so a stock that rose with the whole market doesn't count as a good call.

## 1. Give every agent the CALL contract

Paste this into the system prompt of every agent that forms a view on a stock (all 23, CMIO included):

```text
SCORED CALLS
When you hold a directional view on a stock, end your pack with one line per view:

CALL | agent=<your exact role name> | ticker=<NSE symbol> | dir=<UP|DOWN|NEUTRAL> | conf=<0.50-1.00> | as_of=<ISO timestamp with +05:30> | pack=<pack ID> | thesis=<one line>

- dir is relative to NIFTY over the next 1-20 sessions, not the absolute price.
  NEUTRAL means "moves roughly with the market".
- conf is the probability you are right. 0.50 = coin flip. Below 0.50 means you hold
  the opposite view: write that call instead.
- Every call is graded and published on a scorecard. A wrong call costs you less than a
  vague one: no CALL line means no record, and an agent with no record has no evidence
  it is worth running.
- Never emit a CALL for a move that has already happened. Grading starts from the close
  on your as_of date.
- No view, no line. Do not pad.
```

A working example is in `examples/pack-2026-09-18.txt`.

## 2. Log the calls: every evening, before the next open

```bash
python3 scorecard.py ingest packs/2026-09-18/*.txt
python3 scorecard.py verify                          # OK — 214 calls, chain intact
```

Paste each agent's pack into a text file (or pipe it: `pbpaste | python3 scorecard.py ingest -`).
Lines that aren't `CALL | …` are ignored, so the whole pack can go in.

**Deadline: before 09:15 IST on the next trading day.** A call logged after the market has
started moving against it is marked *backfilled* and not scored. That is the rule that keeps
the scorecard honest: if you ingest Friday's packs on Monday afternoon, they don't count.

## 3. Give it prices

Any CSV with `date,ticker,close` columns, **or NSE bhavcopy files as downloaded**
(`sec_bhavdata_full_DDMMYYYY.csv`, EQ series only). Include `NIFTY` as a ticker for the benchmark:

```csv
date,ticker,close
2026-09-18,BEML,4241.60
2026-09-18,NIFTY,25431.20
```

Your Market Volume Intelligence Analyst already pulls closes, so have it append to one file daily.

## 4. Score

```bash
python3 scorecard.py score --prices "prices/*.csv" --out out/scorecard.md
```

Run it weekly. `--benchmark ''` scores raw returns; `--json out/calls.json` dumps every graded call.

## Reading the report

| Column | Meaning |
|---|---|
| Hit rate | Share of calls right on excess return vs NIFTY |
| Range | Where the true hit rate plausibly sits, widened for the number of agents compared |
| Avg edge | Average excess return in the direction called (UP/DOWN) |
| Brier | Confidence quality. 0 = perfect, 0.25 = coin flip, higher = overconfident and wrong |

| Verdict | What to do |
|---|---|
| **SIGNAL** | The agent earns its place. Weight its calls more in the CMIO synthesis. |
| **NO EDGE YET** | Keep collecting. If it stays here past ~200 calls, it is probably noise: cut it or merge it. |
| **WRONG-WAY** | Reliably wrong. Its prompt or data is broken, and that's fixable. |
| **INSUFFICIENT** | Fewer than 20 resolved calls. |

## How many calls before you know anything

With 17 analysts compared at once, the scorecard needs this many calls from one agent before it
will say SIGNAL:

| If the agent is truly right… | Calls needed |
|---|---:|
| 70% of the time | ~55 |
| 65% | ~95 |
| 60% | ~215 |
| 55% | ~870 |

Real edges in markets are usually closer to 55% than 70%. **Most agents will read NO EDGE YET
for months**, and that is the honest answer. The practical consequence: an agent that makes one
call a week will never prove anything. Agents should make a call whenever they genuinely hold a view.

## Design choices, and why

- **Excess return, not raw.** On a day NIFTY rises 2%, "UP on everything" looks brilliant.
  Grading against the index removes that.
- **Conservative entry.** Entry is the close *on* the as-of date, never the previous close. A call
  made at 11:00 gets no credit for a move that happened before 11:00.
- **Hash-chained ledger.** Each call carries the hash of the one before it. Editing a wrong call,
  deleting it or reordering the file breaks the chain; `verify` names the line, and `ingest`
  refuses to append to a broken ledger. Committing `ledger/calls.jsonl` to git adds a second,
  independent record.
- **Correction for many agents.** Test 17 coin-flipping agents at plain 95% confidence and about
  one looks skilled by luck. On synthetic data with no skill planted, two agents came out as SIGNAL
  before the correction and none after. Ranges are Bonferroni-widened by the size of each table.
- **NEUTRAL has a band.** It is right when the excess move stays within 1% × √days
  (1.0% at 1 day, 2.2% at 5, 4.5% at 20).

## Tests

```bash
python3 test_scorecard.py      # tamper detection, look-ahead rules, grading, bhavcopy parsing
```
