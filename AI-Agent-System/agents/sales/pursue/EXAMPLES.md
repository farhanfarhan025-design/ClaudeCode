# EXAMPLES — PURSUE

Worked output. The register rows below use the illustrative data in
`scripts/examples/pipeline.json` — see its `_note` before quoting any figure from it.

---

## 1 — Weekly pipeline cycle

```
PIPELINE CYCLE — 3 August 2026
Status: PARTIAL — 2 quotations require action

PIPELINE
  Open quotations:          4      QAR 219,700.00 unweighted
  Expected value:           QAR  55,296.00   ← ASSUMED 30% conversion, not observed
  Decisions due this week:  2

MOVED
  Won:                      0
  Lost:                     0
  Gone quiet (>21d):        2      QAR  65,700.00

CONVERSION (trailing)
  Tracked decisions:        3 of 20 needed — win rate NOT YET ANSWERABLE
  Avg days to a decision:   34
  Win rate by tier:         not computed — fewer than 5 decisions in every tier

NEEDS YOU
  1. Umm Salal Farms — validity lapsed 9 days ago. Follow-up drafted. If they are still
     live, the re-offer is a PRICE decision, not an administrative one.
  2. Barwa Food Services — 75 days, 71 days silent. Recommend recording as
     lost · NO_RESPONSE. One line from you closes it.

DRAFTED FOR YOU TO SEND
  · Umm Salal Farms — ask whether a decision is expected
  · Barwa Food Services — final direct ask before closing the row

FLAGGED
  Denominator unverified: QUT/DCTS/066/2026 may include revisions (OL-014). No conversion
  percentage will be published until you confirm what the series counts.
```

Note what this report does **not** contain: no forecast, no "likely to close", no percentage
dressed up with a caveat. The expected value carries its basis in the same line as the number.

---

## 2 — A follow-up draft, right and wrong

**Correct:**

```
DRAFT — NOT SENT
To:      Umm Salal Farms — Mr. Abdulla
Re:      Quotation QUT/DCTS/067/2026 — cold room, farm store

Dear Mr. Abdulla,

We issued the above quotation on 10 July for the cold room at the farm store.

Is a decision expected on your side this month, or is there an approval step still to
come? Either answer is useful — it lets us plan properly around your programme.

If it is easier, a one-line reply to this message is enough.

Farhan / Sales Engineer
The New Doha Kitchen Equipment Services W.L.L.
```

**Wrong — and why each fails:**

| Draft | Failure |
|---|---|
| *"Just checking in on the below!"* | No question. This is what gets written when there is nothing to ask, and it teaches the client that TNDK's follow-ups can be ignored. |
| *"We may have some flexibility on the price if that helps."* | **A9 breach.** An offer of a concession, made by an agent with no pricing authority. Stops the handoff. |
| *"We can still deliver within 3 weeks if you confirm this week."* | **A9 breach.** A delivery commitment. Lead times belong to PROCURE, and Mesaieed's contract shows what a missed date costs. |
| *"Sorry to bother you again about this…"* | Apologetic. Asking for a decision on a document you were invited to send is not an imposition. |
| *"This price is only valid until Thursday."* | Manufactured urgency, plus a pricing statement. Validity is on the quotation; re-stating it as a threat is not PURSUE's to do. |

---

## 3 — Client asks for a discount

**Client:** *"Your number is a bit high — what can you do on the price?"*

**Correct handling:**

```
ROUTED OUT → PRICE (via TNDK-SALES → TNDK-OPS)
Quotation:      QUT/DCTS/069/2026 — Msheireb Hospitality
Client words:   "Your number is a bit high — what can you do on the price?"
Context:        Quoted 34,000 on 20 July. No competitor named. No target figure given.
                Client has not said what "high" is relative to.
Register:       status unchanged (open), last_contact updated, note recorded verbatim
```

```
DRAFT — NOT SENT
To:      Msheireb Hospitality — Ms. Al-Kuwari
Re:      Quotation QUT/DCTS/069/2026

Thank you — I have passed your note on the pricing to Farhan directly and he will come
back to you on it himself.

So that he has the full picture: is there a figure or a budget you are working to, and is
the scope as quoted still what you need?

Farhan / Sales Engineer
```

**What PURSUE did not do:** name a number, hint at flexibility, ask "how close are we?",
offer to remove something from scope, or promise a response by a particular day.

Asking what the client is working to is legitimate — it is intelligence, and PRICE needs it. It
is not a negotiation, because nothing was offered.

---

## 4 — Recording a loss

**Client:** *"We went with another supplier, they were about ten percent under you."*

```
OUTCOME CAPTURED
Quotation:      QUT/DCTS/063/2026 — Doha Central Bakery
Value:          QAR 62,000.00      Tier: 30%      Sent: 5 May 2026
Status:         lost
Decided:        26 May 2026        Days to decision: 21
Loss reason:    PRICE_LOWER
Client words:   "we went with another supplier, they were about ten percent under you"
Competitor price: NOT RECORDED — "about ten percent" is the client's characterisation,
                  not a figure they stated. Do not derive 55,800 from it.
Note for PRICE:  A 30%-tier quote lost on price. One data point, not a trend.
```

**The discipline:** "about ten percent under" is not a competitor price. Writing 55,800 into the
register would turn a client's offhand phrase into a fact the business plans against — exactly
the failure `memory/lessons.md` L-002 describes.

**Also correct:** if the client had simply stopped replying, the entry is `NO_RESPONSE`, not
`PRICE_LOWER`. TNDK does not know why it lost, and the register must not pretend otherwise.

---

## 5 — The conversion report, before there is enough data

```
CONVERSION — 3 August 2026

Win rate:                 NOT YET ANSWERABLE
                          3 quotations tracked from issue to decision. 20 needed.

Historic record:          5 awards reconstructed from the register. Excluded from every
                          rate: that register only ever recorded wins, so including them
                          reports a win rate of 100% by construction.

Denominator:              UNVERIFIED. QUT/DCTS/066/2026 is the highest reference seen. It
                          is not yet established whether the series counts quotations,
                          revisions, or both, or over what period.

Win rate by tier:         Not computed. Fewer than 5 decisions in each tier.
                          This is the table GOALS.md G1 needs. Earliest useful date, at
                          the current issue rate: [n] weeks.

What is known:            Average 34 days from issue to decision across 3 tracked quotes.
                          2 of 3 losses cited price; 1 was a shelved project.

Needs you:                Confirm what the QUT series counts. One line. Until then no
                          conversion percentage will be published.
```

An empty answer, stated precisely, is a valid deliverable. The failure mode this guards against
is a "12% conversion rate" quoted in a meeting six months from now, traced back to a week when
the denominator was a guess.
