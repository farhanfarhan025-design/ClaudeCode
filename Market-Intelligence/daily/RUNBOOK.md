# Daily run — Market Intelligence Team

The evening job follows this file exactly. It runs after NSE closes on weekdays and needs no input from anyone.
Paths are relative to `Market-Intelligence/`. Dates and times are IST.

**What this is:** paper calls for the scorecard, so the team builds a track record. It is analysis only,
never investment advice, and it never places or suggests a trade size.

## 0. Start

```bash
git fetch origin market-intelligence && git checkout market-intelligence && git pull --ff-only origin market-intelligence
TODAY=$(TZ=Asia/Kolkata date +%F)
```

If today is Saturday or Sunday, skip to step 4.

## 1. Build the brief: `daily/briefs/$TODAY.md`

Use web search (6 to 10 searches). Collect **only facts published today or after yesterday's close**:

1. Nifty 50 and Sensex close today: points and %. If the market was shut (holiday), write that, skip steps 2 and 3, go to step 4.
2. Top NSE gainers and losers today, with % moves.
3. Stock-specific events: order wins, results, guidance, block or bulk deals, promoter or insider trades,
   pledges, SEBI or exchange actions, rating changes, management changes.
4. Sector moves and their stated cause.
5. FII/DII flows, rupee, crude, and any global event the coverage links to Indian stocks.

Rules for the brief:
- Every line carries its source link. A fact without a source does not go in.
- Numbers exactly as the source gives them. If two sources disagree, write both.
- End with a **Gaps** section: what you looked for and couldn't find.
- Use NSE symbols (BEML, COCHINSHIP, …) for every company named.

## 2. Run the team: `daily/packs/$TODAY.txt`

Work through the roles in `daily/TEAM.md` in order: the four desks, then the review desk, then the Chief.
Each role reads the brief (and, for the review desk and Chief, the filings before it). Write each role's filing
into the pack under its exact roster name.

Binding on every role:
- Use only the brief. Never invent a figure, date, order value, filing, quote or source.
- Stay in the role's own job. If the brief lacks what the job needs, say so under Gaps and make no call.
- A call is a view on the stock's move **relative to NIFTY over the next 1 to 20 sessions**:
  UP, DOWN or NEUTRAL, with conf = probability of being right, 0.50 to 0.95. Only call stocks named in the brief.
  Make a call whenever the role genuinely holds a view; no call beats a weak call.
- The Research Validation Analyst names every desk claim the brief doesn't support. The Chief drops those claims.

The pack ends with every call made by any role, one per line, in exactly this form:

```
CALL | agent=<exact roster name> | ticker=<NSE symbol> | dir=<UP|DOWN|NEUTRAL> | conf=<0.50-0.95> | as_of=<now, ISO with +05:30> | pack=TEAM-<YYYYMMDD> | thesis=<one line>
```

## 3. Log the calls, before 09:15 IST next session

```bash
cd scorecard
python3 scorecard.py ingest ../daily/packs/$TODAY.txt
python3 scorecard.py verify
```

Never edit or delete `ledger/calls.jsonl`. If `verify` fails, stop and report it.

## 4. Prices

```bash
cd ../daily && python3 fetch_prices.py --backfill 35; echo "exit $?"
```

Exit 2 means NSE is blocked by the environment's network settings. Note it in the report and carry on.

## 5. Score

If `daily/prices/` holds any files:

```bash
cd ../scorecard && python3 scorecard.py score --prices "../daily/prices/*.csv" --out ../daily/reports/scorecard.md
```

## 6. Save

```bash
git add -A Market-Intelligence && git commit -m "Daily run $TODAY" && git push -u origin market-intelligence
```

If the push is rejected, `git pull --no-rebase origin market-intelligence`, then push again. Never force-push.

## 7. Report: the final message, at most 8 lines

```
Market Intelligence — <date>
Market: <Nifty close and % · one-line reason>
Chief's calls: <TICKER DIR conf · …>, or "none today"
Logged: <n> calls today · <total> in ledger
Scorecard: <graded n · any agent at SIGNAL or WRONG-WAY>, or "no prices yet"
Blockers: <e.g. NSE prices blocked by network settings>, or "none"
Paper calls for the scorecard. Not investment advice.
```
