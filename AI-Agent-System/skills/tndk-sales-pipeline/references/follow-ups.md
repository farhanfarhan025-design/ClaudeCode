# Drafting follow-ups, and recording outcomes

## The shape of a good follow-up

One line of context, one question, one easy action. Reference the quotation number so the client can find it without searching.

```
DRAFT — NOT SENT
To:      [client contact]
Re:      Quotation [QUT/DCTS/NNN/YYYY] — [project]

Dear [name],

We issued the above quotation on [date] for [the job in six words].

Is a decision expected on your side this month, or is there an approval step
still to come? Either answer is useful — it lets us plan properly around your
programme.

If it is easier, a one-line reply to this message is enough.

Farhan / Sales Engineer
The New Doha Kitchen Equipment Services W.L.L.
```

Note what makes it work: it asks something answerable, it makes "no" as easy to send as "yes", and it gives a reason why the answer helps the client rather than TNDK.

## What fails, and why

| Draft | Why it fails |
|---|---|
| *"Just checking in on the below!"* | Contains no question. This is what gets written when there's nothing to ask, and it teaches the client that these messages can be ignored. |
| *"We may have some flexibility on the price if that helps."* | A concession offered without a margin check or Farhan's approval. This is the rule that matters most. |
| *"We can still deliver within 3 weeks if you confirm this week."* | A delivery commitment. Lead times depend on vendors, and the Mesaieed contract shows what a missed date costs. |
| *"Sorry to bother you again about this…"* | Apologetic. Asking for a decision on a document you were invited to send is not an imposition. |
| *"This price is only valid until Thursday."* | Manufactured urgency plus a pricing statement. Validity is printed on the quotation; restating it as a threat is a different act. |
| *"Are we close on price?"* | Invites a negotiation this skill has no authority to hold. |

## When the client asks about price

Record their words verbatim. Route the question to Farhan. In the draft, say so — and it's legitimate to ask what they're working to, because that's intelligence Farhan needs before he decides.

```
DRAFT — NOT SENT
To:      [client contact]
Re:      Quotation [QUT/DCTS/NNN/YYYY]

Thank you — I have passed your note on the pricing to Farhan directly and he
will come back to you on it himself.

So that he has the full picture: is there a figure or a budget you are working
to, and is the scope as quoted still what you need?

Farhan / Sales Engineer
```

What that draft does **not** do: name a number, hint at flexibility, ask "how close are we", offer to drop something from scope, or promise a reply by a particular day.

Asking what the client is working to is not a negotiation, because nothing was offered.

## Loss reason codes

Every lost quotation gets one, plus the client's own words in the notes.

| Code | Meaning |
|---|---|
| `PRICE_LOWER` | A competitor was cheaper. Record their price **only** if the client stated a figure. |
| `PRICE_BUDGET` | Above the client's budget; no competitor mentioned. |
| `SPEC` | Competitor's technical offer was preferred. |
| `LEAD_TIME` | TNDK's delivery timing lost it. |
| `RELATIONSHIP` | Incumbent supplier or a prior relationship. |
| `NO_DECISION` | Project deferred, shelved or cancelled. Nobody won it. |
| `NO_RESPONSE` | The client never answered. Reason genuinely unknown. |
| `WITHDRAWN` | TNDK withdrew — capacity, credit, or scope. |
| `UNKNOWN` | Lost, reason not established. A valid entry. Never dress it up. |

`PRICE_LOWER` and `PRICE_BUDGET` must stay separate. The first says TNDK was beaten on a job it was in the running for. The second says TNDK was quoting the wrong client. They point at opposite fixes, and only one of them is an argument for lower prices.

## Recording a loss — a worked example

**Client says:** *"We went with another supplier, they were about ten percent under you."*

```
OUTCOME CAPTURED
Quotation:        QUT/DCTS/063/2026 — Doha Central Bakery
Value:            QAR 62,000.00     Tier: 30%     Sent: 5 May 2026
Status:           lost
Decided:          26 May 2026       Days to decision: 21
Loss reason:      PRICE_LOWER
Client words:     "we went with another supplier, they were about ten percent
                   under you"
Competitor price: NOT RECORDED — "about ten percent" is the client's
                   characterisation, not a figure they gave.
Note:             A 30%-tier quote lost on price. One data point, not a trend.
```

The discipline: "about ten percent under" is not a competitor price. Writing `55,800` into the register would turn an offhand phrase into a fact the business plans against.

And if the client had simply stopped replying, the entry is `NO_RESPONSE`. TNDK doesn't know why it lost, and the register shouldn't pretend it does.

## The report, when there isn't enough data yet

```
CONVERSION — [date]

Win rate:        NOT YET ANSWERABLE
                 [n] quotations tracked from issue to decision. 20 needed.

Historic record: [n] awards reconstructed from the register. Excluded from
                 every rate: that register only recorded wins, so including
                 them reports a win rate of 100% by construction.

Denominator:     UNVERIFIED. Highest reference seen is QUT/DCTS/066/2026. Not
                 established whether the series counts revisions, or what
                 period it spans.

By tier:         Not computed — fewer than 5 decisions in each tier. This is
                 the table that shows whether quoting low actually wins work.

What is known:   Average [n] days from issue to decision. [n] of [n] losses
                 cited price.

Needs you:       Confirm what the QUT series counts. One line. Until then no
                 conversion percentage will be published.
```

An empty answer stated precisely is a valid deliverable. The failure this guards against is a "12% conversion rate" quoted in a meeting six months from now, traceable back to a week when the denominator was a guess.
