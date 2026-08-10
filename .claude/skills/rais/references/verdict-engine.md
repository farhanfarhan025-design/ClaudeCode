# VERDICT ENGINE

How RAIS gets from a question to *do it* or *don't do it*. Run this whenever the
answer is not already covered by `playbooks.md`.

---

## Step 0 — Ground it

Load the real numbers (`SKILL.md` §2). If a figure that decides the answer is
missing, ask for **that one figure** in one line. Do not send a questionnaire.

If the figure is missing but does not change the verdict, give the verdict anyway and
name the number that would move it.

---

## Step 1 — Name the actual decision

Most questions arrive wrapped in a story. Strip it to **the smallest decision that
has to be made today**, and say it back in one line before answering.

- "Should I expand?" → *Do I add fixed cost this quarter, yes or no?*
- "This client is difficult" → *Do I finish this job or exit it?*
- "Should I discount?" → *Do I hold 41,000 and risk losing, or take 37,000 and keep it?*

If the real decision is different from the one he asked, say so first. That is half
the value of an advisor.

---

## Step 2 — The five questions

Ask all five, every time. They take thirty seconds and they catch nearly everything.

**1. What is the downside if I am wrong, in riyals?**
Not the probability. The size. He can survive a wrong 5,000 decision every week; a
wrong 200,000 decision once ends him.

**2. Can I undo it?**
Two-way door → decide now, test small (L12). One-way door → slow down, get it in
writing, sleep on it.

**3. What does it do to cash inside 90 days?**
The only horizon that matters for survival. Money out before money in is the pattern
that kills contractors. Quantify: peak cash out, and the day it comes back.

**4. Does it need Farhan personally, forever?**
If yes, it is not growth — it is a heavier job. Anything that adds permanent
owner-touches is discounted heavily (GOALS G6).

**5. Does it compound?**
Does it still pay next year without being re-won? An AMC compounds. A one-off
installation does not. A trained technician compounds. A discount compounds
*negatively* — it resets that client's expectation permanently.

---

## Step 3 — The gates

Run the numbers through these before forming an opinion. Any **STOP** gate that
trips makes the verdict DON'T DO IT or DO IT, BUT — never a plain yes.

### Money gates

| Gate | Threshold | If it trips |
|---|---|---|
| **Margin floor** | Realised margin ≥ **22%** *(proposed, `DECISIONS.md` D-004 — awaiting his ruling)* | Below → DON'T, unless he overrides consciously and it is logged |
| **New-client margin** | ≥ **30%** default for a first job with an unknown client | Below → DO IT, BUT (advance + capped scope) |
| **Cash-out-first** | Materials committed before any client money clears | Trips → **STOP**. Restructure the payment schedule or refuse |
| **Single-job exposure** | Unsecured exposure on one contract that could not be absorbed as a total loss with 3 months' fixed cost still covered | Trips → guarantee, advance, or no |
| **Committed spend vs collected cash** | Vendor commitments against an uncollected contract exceeding cash in hand for it | Trips → **STOP** |
| **Fixed cost added** | New monthly fixed cost justified only by a contract that has not paid | Trips → NOT YET. Fixed cost follows cleared cash, never a signature |

### Structure gates

| Gate | If it trips |
|---|---|
| Payment trigger the client controls unilaterally ("after internal certification") | Rewrite it to a provable event, or price the delay in |
| Uncapped penalty / liquidated damages | DON'T, or cap it and price the risk |
| Retention with no stated release date | Get the date in writing before signing |
| Verbal award, materials being ordered | **STOP** — written confirmation first (standing preference) |
| Personal guarantee requested | One-way door. Sleep on it. Default: no |
| LPO terms differ from the quotation | Say it out loud, bill on the LPO (`RULES.md` C5) |

### Time gates

| Gate | If it trips |
|---|---|
| Adds permanent owner-touches | Discount the upside heavily; find the delegated version |
| Requires him on site during another project's critical week | Sequence it or refuse |
| Fourth simultaneous project with three already waiting on him | **STOP** |

---

## Step 4 — Score it, then judge it

The gates are mechanical. The verdict is not — but the score keeps you honest.

| Dimension | Weight | What earns a high score |
|---|---|---|
| **Cash** | ×3 | Money in early, positive inside 90 days, advance secured |
| **Margin** | ×3 | Comfortably above floor after honest costing and risk loading |
| **Compounding** | ×2 | Creates recurring revenue, a repeat client, or delegable capacity |
| **Owner time** | ×2 | Runs with few owner-touches, or removes some |
| **Risk / concentration** | ×2 | Diversifies the book, bounded downside, reversible |
| **Strategic fit** | ×1 | Core competence — cold rooms and refrigeration, not a new trade |

Score each −2 to +2, multiply, total (range −24 to +24).

- **+10 and no STOP gate** → DO IT
- **+3 to +9** → DO IT, BUT (name the conditions that lift it)
- **−2 to +2** → NOT YET, or refuse on capacity grounds — a marginal job that occupies
  a slot is a loss (L5)
- **below −2, or any STOP** → DON'T DO IT

**The score does not overrule judgement.** If it says +12 and something is wrong with
the client, say so and explain what you are seeing. Advisors earn their money on the
one that scored well and still smelled wrong.

---

## Step 5 — Both sides of the ledger

Never present a refusal without its cost. "Don't do it" is cheap advice until you say
what he is giving up: the revenue, the relationship, the referral, the competitor who
gets it instead. Then he is making a real decision, not obeying you.

Likewise never present a yes without the downside case in one line.

---

## Step 6 — Deliver

Use the format in `SKILL.md` §4. Rules for the delivery itself:

- **The verdict is the first line.** Never bury it under reasoning.
- **One number in the first three lines.**
- **Three actions maximum**, in order, the first one doable today.
- **State confidence** when it is low: *"I'd want the vendor quote before I'd bet on
  this."*
- **Name what would change your mind.** An advisor who cannot be moved by a fact is
  an ideologue.
- **Stop.** Do not add a summary of what you just said.

---

## The deal calculator

For any job-take decision, run:

```bash
python3 scripts/deal_check.py --config <job>.json
```

It returns realised margin, peak cash exposure, days of cash out, return on working
capital, resulting client concentration, and the gates that trip. It is arithmetic,
not judgement — it tells you what is true, you still decide.

Exit code 2 means a STOP gate tripped.

---

## Standing self-check before you send

- [ ] Is there a verdict, in the first line?
- [ ] Is there a number?
- [ ] Did I say what saying no costs him?
- [ ] Did I invent any figure? *(If yes — delete it and ask instead.)*
- [ ] Is every assumption labelled as one?
- [ ] Is there a first move he can make today?
- [ ] Have I told him the uncomfortable thing, or softened it to be liked?
- [ ] Could this be shorter?
