> **SUPERSEDED — 16 September 2026, later the same day.**
> Five further documents arrived after this was written and change two of its conclusions:
>
> - The capillary comparison here was wrong. This note said the 0.9 m assembly at 16.00 had
>   no comparator; Arctic's own ATC/NSA quotation prices a 1 m capillary **with 1/4" nut** at
>   25.00, and Airtronics a 1.5 m at 20.00. Compared per metre the supplier is the cheapest
>   of the three, not an outlier.
> - "Vendor B has no name" still holds, but the **project** is now known: Shared Services,
>   quoted by us as QUT/DCTS/237/2026.
>
> Superseded by `2026-09-16-shared-services-and-rate-card.md`. Kept, not deleted — RULES A6.

# VENDOR COMPARISON — refrigeration spares + plant

**Prepared by:** PROCURE · **Date:** 16 September 2026 · **Status:** DRAFT for Farhan
**Both quotations expire 21 September 2026** (5 days, ex-stock subject to prior sale)

---

## What was compared

| | Vendor A | Vendor B |
|---|---|---|
| Vendor | **Arctic (ACC Qatar)** | **Not named on the document** — handwritten prices on our own material list |
| Ref | ATC/AZ/QT/26/07619 **Rev1** | none |
| Addressed to | Doha Cooling Trading & Solutions | — |
| Lines | 20 | 20 |
| Stated total | **QAR 2,467.50** (verified — the lines sum to it exactly) | **none printed** |
| Terms | Cash · ex-stock subject to prior sale · 5 days | not stated · ex-stock subject to prior sale · 5 days |
| Confidence | high — vendor's own PDF | medium — transcribed from a photo of handwriting |

The two documents **do not cover the same scope.** Arctic quoted spares only.
Vendor B also priced the two pieces of plant, which are 87% of the money:

| | Vendor B |
|---|---|
| Dorin condensing unit AU-H300CC, Aeris coated | QAR 9,300.00 |
| Friga-Bohn evaporator 3C-E 3245-R+E1U+240V, Aeris coated × 2 | QAR 6,950.00 |
| **Plant sub-total** | **QAR 16,250.00** |

**Arctic has no competing price for either.** Until a second quote exists on the
condensing unit and the evaporator, there is no comparison on the part of this
order that actually matters.

---

## Headline — spares only, at the material list's own quantities

| | QAR |
|---|---|
| Arctic, quantity-matched to the material list | **2,412.50** |
| Vendor B (computed; the sheet states no total) | **2,505.00** |
| Best-of-both | **2,237.50** |

Arctic looks 3.8% cheaper. **It isn't.** Strip out the two lines that are not the
same product — the pipe insulation and the capillary — and the two suppliers are
level:

| Strictly comparable lines only | QAR |
|---|---|
| Arctic | 2,376.00 |
| Vendor B | 2,369.00 |
| **Difference** | **7.00 — 0.3%, i.e. nothing** |

The entire apparent Arctic advantage comes from two lines where the two vendors
are quoting different things. This is exactly the trap in `agents/procure/IDENTITY.md`:
compare on landed cost, not headline price.

---

## Line by line (unit prices, QAR)

| Item | Arctic | Vendor B | Cheaper | Note |
|---|---:|---:|---|---|
| Filter drier 1/2" DCL 164 | **35.00** | 50.00 | Arctic | |
| Expansion valve TE2 / TES-2 | 185.00 | **180.00** | B | |
| Orifice No. 02 | 45.00 | 45.00 | level | identical figure — good cross-check on the transcription |
| Sight glass SGI-12S | 90.00 | **65.00** | B | B specifies solder type; Arctic does not state |
| Ball valve 1/2" | 100.00 | **90.00** | B | Castel 6570/4 vs Danfoss GBC 12S — different brands |
| Pressure switch KP15 auto | 230.00 | **180.00** | B | **B includes a flexible hose in the 180** |
| Flexible connector / hose 1 m | 35.00 | 35.00 | level | Arctic quotes 3 pcs where the list needs 2 |
| Flare nut 1/2" | **3.00** | 6.00 | Arctic | commodity, brands differ |
| Flare nut 3/8" | **2.00** | 5.00 | Arctic | commodity, brands differ |
| Vibration eliminator 1/2" | 65.00 | **50.00** | B | Castel 7690/4 vs Harbax |
| Solenoid valve 1068/4A6 | 175.00 | **155.00** | B | **B states "+ COIL". Arctic does not say.** |
| Copper coil 1/2" × 50' | **260.00** | 320.00 | Arctic | 23% — the largest real gap |
| Copper coil 7/8" × 50' | **625.00** | 700.00 | Arctic | 12% |
| Pipe insulation 7/8"×3/8" | 3.25 | 13.00 | ⚠ | **not comparable** — B is a 1.8 m piece, Arctic states no length |
| Capillary 0.090" | 5.25 /m | 16.00 /ea | ⚠ | **not comparable** — B is a 0.9 m assembly with nut, Arctic is bulk tube |
| Charging union 1/4"×1/8" NPT | 8.00 | **7.00** | B | Arctic also lists a Castel 9150/R02 at 10.00 |
| P-trap 1/2" | 17.00 | **8.00** | B | 112% — the largest gap on an ordinary part |
| Vibration pad | 25.00 | **20.00** | B | Arctic specifies Airtech 18×18×3/8, B states no size |

Regenerate at any time:

```bash
python3 scripts/pricebook.py --compare
python3 scripts/pricebook.py --basket pricebook/quotes/2026-09-16-unnamed-supplier-material-list-handwritten.json
```

---

## Findings

**1. Arctic's quote is not quantity-matched to the material list — QAR 55.00 of it is surplus.**
Its stated 2,467.50 covers 3 flexible connectors where the list needs 2 (+35.00), and a
Castel 9150/R02 connector at 2 × 10.00 (+20.00) *on top of* the charging union that already
answers that line. Priced against what the list actually asks for, Arctic is 2,412.50.

**2. The solenoid coil is the one question that could change the answer.**
Vendor B's 155.00 explicitly includes the coil. Arctic's 175.00 does not say. Two valves are
needed. If Arctic's price excludes coils, Arctic is the more expensive supplier on spares
outright — and this is the only question in the pack that moves the decision.

**3. Two lines are not like-for-like and should not be priced from this comparison.**
The insulation (length unstated by Arctic) and the capillary (bulk tube vs finished assembly).
Their apparent 300% and 205% spreads are specification gaps, not savings.

**4. Splitting the order to save QAR 175.00 is not worth it.** Best-of-both is 2,237.50 against
Arctic's 2,412.50 — 7%, on an order whose real weight is the 16,250.00 of plant. Two POs, two
collections, two sets of paperwork. Not recommended on this order.

**5. Vendor B has no name on the document.** No LPO can be raised against it as it stands
(`RULES.md` A3, and PROCURE cannot commit spend to a vendor it cannot identify).

---

## Recommendation

**Not yet a recommendation to buy — three answers are needed first, and both quotes die on
21 September.**

1. **Who priced the material list?** Vendor B holds the only price on 87% of the value.
2. **Does Arctic's 175.00 solenoid include the coil?** One phone call; it decides the spares.
3. **Is there a second price on the Dorin unit and the Friga-Bohn evaporators?** 16,250.00
   with one quote against it is the exposure on this order, not the spares.

Once (2) is answered, the spares go to whichever supplier also gets the plant — the 7%
best-of split does not justify a second purchase order.

## Before any LPO — required and not yet possible

`agents/procure/IDENTITY.md` requires the exposure check on every LPO, and it cannot be
completed from these two documents:

```
Project:                   NOT STATED on either document
Contract value:            unknown
Collected to date:         unknown
Committed vendor spend:    QAR 18,755.00 if Vendor B is ordered in full
Uncollected exposure:      cannot be computed
Written award in hand?:    UNKNOWN
```

**Which project is this material for, and is there an LPO/LOA in hand for it?**
If there is no written award, `RULES.md` E says stop before ordering — and at 18,755.00
this is not a small commitment. Issuing either LPO needs Farhan's approval regardless
(`RULES.md` B).
