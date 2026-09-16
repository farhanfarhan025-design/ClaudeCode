# OPEN LOOPS

Anything awaiting someone. Every entry has an owner and a date. Closed loops move to
`lessons.md` if they taught something, otherwise they are deleted.

**Opened:** 3 August 2026.

---

## 🔴 Blocking — resolve before related work proceeds

### OL-001 — Samoosa contract value unresolved
**Owner:** Farhan · **Raised:** 2026-08-03 · **Blocks:** any Samoosa document

Three sources disagree:

| Source | Contract | Received |
|---|---|---|
| `approved_register.xlsx` (Drive, 31 Jul) | 38,500 | 20,000 |
| `register_data.json` (skill) | 39,375 | 31,500 |
| `numbering-log.md` receipts | — | 20,000 (RCT-256 only) |

The 875 is the chequered-sheet variation. The 11,500 receipt gap has no receipt number.
Invoices INV-256/257/258 exist against this job; only RCT-256 is logged.

**Needed:** which figure is correct, and whether receipts exist for the 11,500.

### OL-002 — Approved Works Register is arithmetically broken
**Owner:** LEDGER · **Raised:** 2026-08-03 · **Blocks:** any decision using register totals

Balance column reads 0.00 on every row. Total row reads 18,250 (first three rows only).
Summary block reads 0.00 throughout. Details in `analysis/FINDINGS.md`.

**Needed:** rebuild with verified arithmetic. Draft prepared 3 Aug 2026, awaiting Farhan.

### OL-003 — VAT / tax wording contradiction
**Owner:** Farhan · **Raised:** 2026-08-03 · **Blocks:** clean quotation issuance

Invoices may never say "tax". Quotations say "excluding 5% VAT". See `DECISIONS.md` D-005.

**Needed:** a ruling. Option A (remove the VAT line) recommended.

**Evidence 2026-09-16:** quotation QUT/DCTS/237/2026, issued today, carries **no VAT or tax
line at all** — Sub-Total then GRAND TOTAL, exactly as `RULES.md` A1 requires of an invoice.
The practice appears to have already moved to Option A. This loop can probably be closed by
ruling rather than by investigation.

### OL-004 — Margin floor not yet confirmed
**Owner:** Farhan · **Raised:** 2026-08-03 · **Blocks:** PRICE Stage 3 promotion

Proposed at 20% markup on cost — the pricing guide's own lowest tier. PRICE operates on this
until confirmed or changed. See `DECISIONS.md` D-004.

---

### OL-018 — QUT/DCTS/237/2026 quoted below the margin floor
**Owner:** Farhan · **Raised:** 2026-09-16 · **Blocks:** nothing mechanically — the quotation
is already signed and dated. That is why it is here.

Our Shared Services quotation prices at **QAR 21,700.00** against a best-of material cost of
**QAR 18,509.00** — **17.2% markup, 14.7% margin on price**. Below `RULES.md` B's 22% floor
and below the 20% in `margin.py` / D-004. No owner override is logged.

`analysis/FINDINGS.md` opens on the pricing guide's worked example landing at 14.6%. This
lands at 14.7%. Same gap, first time seen at the moment of quoting.

Two lines are worse than thin: the 1/2" P-trap is **sold at 7.00 against an 8.00 cost**, and
the Castel 7140/21 connector sells at cost.

**Needed:** re-price, or a written override with a reason, logged (`RULES.md` B). Clearing 22%
at best-of cost needs QAR 22,580.98 — an uplift of 881.00, 4.1% on the price.
Full working: `pricebook/comparisons/2026-09-16-shared-services-and-rate-card.md`.

### OL-019 — margin.py `unit_freezer` rate is 166% below a real quote
**Owner:** Farhan (rate change) · **Proposed by:** PROCURE · **Raised:** 2026-09-16
**Blocks:** confidence in any price built on the flat unit rates

`RATES["unit_freezer"] = 6,400.00` is meant to cover the condensing unit and evaporator for
one freezer room. Airtronics quoted the Samoosa freezer plant on 28 July 2026 at **17,050.00**
(Dorin AU2-H751CS 12,700.00 + Gunay GNE 245.8C 4,350.00).

The rate is **flat per room and does not scale with duty** — that quote is for 41.6 cbm at
−25 Te. It will be roughly right on a small room and far too low on a large one, with nothing
in the process to say which you are in.

**Needed:** duty-banded unit rates, or a "confirm against a live quote above X cbm" trigger.
PROCURE may only propose; the change is Farhan's (`agents/procure/IDENTITY.md`).

## 🟠 Cash — active

### OL-005 — Mesaieed advance bank guarantee
**Owner:** Farhan · **Raised:** LOA dated 2026-05-21 · **Value:** QAR 60,000 advance,
QAR 400,000 contract

Over ten weeks with no advance collected on 53% of the order book. Requires an advance bank
guarantee plus a performance security cheque before the 15% advance is released.

**Standing item in every weekly COLLECT cycle until cleared.** Escalate to headline status if
three consecutive weeks pass with no movement.

### OL-006 — CCC / HIA balance
**Owner:** COLLECT · **Value:** QAR 177,450 (70%)
Due on delivery / progress / completion milestones. Confirm next milestone date and whether
any has already passed without an invoice.

### OL-007 — Jollibee balance
**Owner:** COLLECT · **Value:** QAR 18,400 (40%)
Due after commissioning. Confirm commissioning status.

### OL-008 — Samoosa balance
**Owner:** COLLECT · **Value:** QAR 7,875 *(subject to OL-001)*
Due on completion.

---

## 🟡 Data gaps

### OL-009 — Rate card verification date unknown
**Owner:** PROCURE
No record of when panel, unit or door rates were last checked against a live vendor quote.
Material for any contract above ~100,000.

**Updated 2026-09-16.** Seven documents are now captured in `pricebook/`.
`python3 scripts/pricebook.py --rates` checks the card against them:

| Rate | Card | Real | Status |
|---|---|---|---|
| `door` (90×190 hinged) | 1,800.00 | 1,800.00 | **VERIFIED 29 Aug 2026** — two independent quotes |
| `control_panel` | 1,200.00 | 950.00 | 21% above real — safe direction, overstates cost |
| `unit_freezer` | 6,400.00 | 17,050.00 | **166% below real — see OL-019** |

**Still unverified against any vendor quote:** `panel_sqm`, `angle_piece`, `floor_pair`,
`unit_chiller`, `pipe_system`, `wiring_system`, `lights_per_2_rooms`.
**Still needed:** a current insulated panel quotation — it is the largest single cost in a
cold room and nothing on record touches it.

### OL-010 — No warranty expiry dates recorded
**Owner:** ANNUITY
No completed project has a warranty start or end date. Blocks the entire AMC pipeline.

### OL-011 — Register has no cost or margin column
**Owner:** LEDGER
The book shows revenue and cash but never profit. Realised margin per project is unknown.

### OL-012 — No quote-to-award conversion data
**Owner:** PRICE
Quotations issued up to QUT/DCTS/066/2026, but only won jobs are recorded. Win rate unknown,
so the effect of low pricing on win rate cannot be assessed.

## 🟡 Vendor pricing — raised 16 September 2026

### OL-013 — Vendor unidentified on the 16 Sep material list pricing
**Owner:** Farhan · **Raised:** 2026-09-16 · **Blocks:** any LPO on those rates

A material list was priced by hand and photographed. The sheet names no vendor. It holds the
**only** price on record for the Dorin condensing unit AU-H300CC (9,300.00) and the Friga-Bohn
evaporators (3,475.00 each) — QAR 16,250.00, 87% of that order.

Also unconfirmed on the same sheet: that the figures are **unit** prices rather than line
totals (read as unit prices on three cross-checks against the Arctic quotation — see the
quote file's `price_basis_evidence`), and that the currency is QAR. No total is printed on it.

**Needed:** the vendor's name, and confirmation of the basis. PROCURE cannot commit spend to
a vendor it cannot name. Both quotations expire **21 September 2026**.

### OL-014 — Does the price book belong in the repo or in Drive?
**Owner:** Farhan · **Raised:** 2026-09-16 · **Blocks:** nothing, but decide before it grows

`README.md` and `TOOLS.md` say instructions live in the repo and data lives in Drive. A vendor
price book is neither a register nor client data — it is inbound vendor offers with no other
source of truth, and its value is entirely in its version history (what a price *was* last
time). It is in `pricebook/` for now on that reasoning.

**Needed:** confirm, or nominate a Drive location and it moves. Deciding now is cheap; deciding
after fifty quotations is not.

### OL-015 — Solenoid coil inclusion unconfirmed (Arctic)
**Owner:** PROCURE · **Raised:** 2026-09-16 · **Expires with the quote, 2026-09-21**

Arctic quotes the Castel 1068/4A6 solenoid at 175.00 without saying whether the coil is
included; the competing sheet states 155.00 **including** coil. Two valves are required.
This single question decides which supplier is cheaper on the spares package.

**Needed:** one call to Arctic (Pandian, 50372315 / Jeena, 59985144).

### OL-016 — Project and written award not identified for the 16 Sep material
**Owner:** Farhan · **Raised:** 2026-09-16 · **Blocks:** the exposure check, therefore any LPO

~~Neither document names the project.~~ **Project identified 2026-09-16:** the material list is
the schedule of our quotation **QUT/DCTS/237/2026 to Shared Services** (Mr. Kenneth Ferran) —
Anantara / Tivoli / Oaks properties.

The exposure check can now be produced, and it is empty by design:

```
Contract value:            NONE — quoted 16 Sep 2026, not awarded
Collected to date:         QAR 0.00
Committed vendor spend:    QAR 0.00 — no LPO raised
Written award in hand?:    NONE
```

**Still needed:** the award. Nothing is ordered against a quotation (`RULES.md` E). Reduced
from blocking to watching — reopen the moment an LPO arrives.

### OL-017 — Are Arctic, Arctic Cooling Company and ACC Qatar one vendor?
**Owner:** Farhan · **Raised:** 2026-09-16 · **Blocks:** nothing, but it affects every comparison

Four quotations sit under three letterheads and three reference series (ATC/AZ, ATC/NSA,
ATC/RY, ACC/QT/RVD). They are recorded as **one vendor** on this evidence: Pandian, mobile
50372315, is named as the contact on both ATC/AZ/QT/26/07619 and ACC/QT/RVD/1508/2026, and the
ACC quotations route POs to arcticparts@accqatar.com.

If they are separate companies, every "cheapest vendor" call in the comparison is wrong.

**Needed:** confirm. One sentence from Farhan settles it.

### OL-020 — Arctic ATC/RY/QT/26/00286 does not add up
**Owner:** PROCURE → Arctic · **Raised:** 2026-09-16 · **Blocks:** ordering against that quote

Two lines summing to **5,500.00** against a stated total of **5,400.00**, in figures and in
words, with no discount line. A 100.00 error on the vendor's document.

**Needed:** Arctic to reissue or confirm which figure stands. Until then the quote is flagged
in `--verify` and must not be ordered against (`RULES.md` A3).

### OL-021 — Quotation numbering series has jumped
**Owner:** LEDGER · **Raised:** 2026-09-16 · **Blocks:** the next quotation number

`memory/durable_facts.md` records the quotation series as "next after **QUT/DCTS/066/2026**"
as at 13 July 2026. Today's quotation is **QUT/DCTS/237/2026**.

Either the numbering log is badly stale or there are two series in use. `RULES.md` A7 makes
the numbering log the anti-collision mechanism and A7 forbids reusing a number — neither is
safe while the series is unknown.

**Needed:** reconcile the numbering log against what has actually been issued, before the next
quotation is raised.

### OL-022 — Samoosa: first real cost evidence
**Owner:** LEDGER / PRICE · **Raised:** 2026-09-16 · **Relates to:** OL-001, OL-011

Airtronics ART-QTN-3174-26, 28 July 2026, quotes the Samoosa freezer room plant (5.2 × 3.2 ×
2.5 m = 41.6 cbm) at **QAR 18,525.00**. Against the disputed contract value of 38,500 that is
**48.1% of the job in plant alone**, before panels, doors, flooring, labour or transport.

This does not resolve OL-001 and PROCURE is not the lane that should. It is the first cost
figure that exists for that job and it bears directly on OL-011.

**Needed:** PRICE to build the full Samoosa cost against this, once OL-001 settles which
contract value is real.

