# What belongs here, and what routes elsewhere

## The three TNDK skills

| Skill | Owns |
|---|---|
| `tndk-coldroom-quotation` | Producing the quotation document, and the price on it |
| **`tndk-sales-pipeline`** | Everything before that quotation exists, and everything after it is sent — until it is won or lost |
| `tndk-accounts` | Everything downstream of an award: invoices, receipts, delivery notes, registers, money owed |
| `tndk-lpo` | Purchase orders to vendors |

A won quotation leaves this skill immediately. The moment there's an award, it's an accounts job.

## Requests that look like they belong here but don't

| Request | Where it goes | Why |
|---|---|---|
| "What should we charge to win this?" | Quotation skill / Farhan | The part that wants the deal doesn't set the number. |
| "Can we do it by the 20th?" | Farhan (vendor lead times) | Delay penalties are contractual. |
| "Can we knock 8% off?" | Farhan | A discount needs a margin check and his approval — not a sentence in a follow-up. |
| "Client hasn't paid the second milestone" | `tndk-accounts` | This skill chases **decisions**; that one chases **money**. |
| "How big does the room need to be?" | Quotation skill | Qualification establishes there's a job, not what it is. |
| "Their warranty expires in 60 days" | Maintenance / AMC work | That sells servicing of what's installed; this sells the next installation. |
| "Raise the invoice for the advance" | `tndk-accounts` | The job left this lane when it was won. |

## Chasing a decision vs chasing money

The distinction worth keeping sharp, because the same client can be in both states:

| | This skill | `tndk-accounts` |
|---|---|---|
| Chases | a decision on a quotation | payment on an invoice |
| The client owes | an answer | money |
| Ends when | won or lost | paid |
| Tone | patient | firm |

If you find yourself asking a client about a payment, you're in the other skill.

## The pricing boundary, in full

No price, rate, percentage, discount, margin or delivery date goes into anything a client will read. This holds when:

- The client asks directly. (Answer: it has gone to Farhan.)
- The client asks for "just a ballpark to know if it's worth proceeding". (Still Farhan. A number invented to keep a conversation warm becomes a number the client believes they were quoted.)
- A quotation has gone quiet and a concession would obviously restart it.
- Farhan says in the moment "tell them 5% off". (He may absolutely give 5% — but it gets priced and recorded, not typed into a follow-up. Route it, and it comes back approved.)

Tier and reason code from the quotation are **analysis data**: useful for reporting win rate by tier to Farhan, never repeatable to a client.

The reason this is a hard line rather than a guideline: a quotation was priced at 14.6% against a 30% default and nobody noticed, because nothing checked the margin at the moment of quoting. Every informal concession is that failure repeating, one message at a time.

## What this skill can never do

There is no email, WhatsApp, CRM or bank connection. It reads and drafts. Every follow-up, every approach, every referral ask is text for Farhan to send himself.

"I have drafted the follow-up for you to send" is correct.
"I have followed up" would be a fabrication.

If something needs a capability that isn't there, say so and stop — don't approximate it.
