# Pricing guide

Internal estimating figures for arriving at the lump-sum total. These are
**costs, not client prices** — nothing here appears in the quotation.

The generator does not price anything. It takes `total` as given. Use this only
to sanity-check a number before quoting it.

## Material unit costs

| Item | Unit | Cost (QAR) | Notes |
|---|---|---|---|
| Sandwich panel, 100 mm PUF | per sqm | 115 | both faces, food-grade GI |
| Sandwich panel, 150 mm PUF | per sqm | 145 | freezer duty |
| Cold room door 900 × 1900 | each | 1,800 | hinged, safety release |
| Aluminium angles | per 6 m piece | 55 | 40 × 40 × 2 mm L-profile |
| Chequered sheet + plywood | per pair | 350 | one pair covers ≈ 2.88 sqm |
| Chiller condensing unit + evaporator | set | 8,800 | hermetic/scroll, +2 to +8 °C |
| Freezer condensing unit + evaporator | set | 6,400 | small capacity |
| Control panel | each | 1,200 | IP54/55, digital controller |
| Pipe & accessories | per system | 2,500 | copper, drier, sight glass, EXV |
| Wiring | per system | 1,800 | within room scope |
| LED vapour-proof lights | per 2 rooms | 500 | lump sum |

**The equipment line is the one that moves.** The 8,800 set covers a standard
packaged unit. A BITZER semi-hermetic package of the kind quoted on
`QUT/DCTS/SQ072/2026` costs substantially more, and that difference dominates
the estimate — price the actual selection rather than the table row.

## Quantities

For a room L × W × H metres:

| Component | Formula |
|---|---|
| Wall area | `2(L×H) + 2(W×H)` |
| Ceiling area | `L × W` |
| Floor area | `L × W`, only with an insulated floor |
| Total panel | sum of the above |
| Angle pieces | `ceil((4(L+W) + 4H) / 6)` |
| Floor pairs | `ceil(floor_area / 2.88)` |

`generate.py --print-summary` prints the panel and floor areas, so the
arithmetic can be lifted straight from there.

## Build-up

1. **Direct cost** — materials + equipment + control panel, pipe, wiring, lights
2. **Labour & installation** — 15% of direct
3. **Transport & handling** — ≈ 1,500 lump sum within Doha
4. **Subtotal** = direct + labour + transport
5. **Quote** = subtotal × (1 + margin)

| Margin | Use when |
|---|---|
| 20% | competitive bid, government tender, repeat client |
| 25% | standard market quote |
| 30% | default for a new client |
| 35%+ | premium, urgent, or difficult site access |

## Back-check: QUT/DCTS/SQ072/2026

Chiller 6.0 × 2.40 × 2.90 m with insulated floor, 77.52 sqm panel.

| Item | Calc | QAR |
|---|---|---|
| Panels | 77.52 × 115 | 8,915 |
| Door | 1 × 1,800 | 1,800 |
| Angles | 8 pcs × 55 | 440 |
| Floor | 5 pairs × 350 | 1,750 |
| Condensing unit + evaporator | baseline set | 8,800 |
| Control panel | 1 × 1,200 | 1,200 |
| Pipe & accessories | | 2,500 |
| Wiring | | 1,800 |
| Lights | | 500 |
| **Direct** | | **27,705** |
| Labour | 15% | 4,156 |
| Transport | | 1,500 |
| **Subtotal** | | **33,361** |

Against the quoted **QAR 46,800** that is a 40% margin on the baseline — which
is the tell that the baseline equipment line is too low for a BITZER
semi-hermetic package, not that the job carried a 40% margin. Substitute the
real equipment cost before reading anything into the percentage.

## Terms already fixed in the master

- **Payment:** 75% with LPO, 20% on delivery, 5% after commissioning
- **Delivery:** material 4–6 days from LPO; installation 7–10 working days;
  total approx. 18–22 days
- **Warranty:** 12 months across panels, door, compressor, coils, controls and
  workmanship
- **VAT:** prices are exclusive
- **Exclusions:** civil works, MDB and main cable, drain beyond 3 m, backup
  power, BMS/CCTV, lifting equipment, work above 3 m

Change these per-job through the `delivery` override or by editing the
generated file — not by editing the master.

## Known inconsistency in the master

Section 13 says *"This quotation is valid for 30 days from the date of issue"*
while the reference block says *15 Days from quote date*. The master carries
both. Decide which applies and correct the generated document, or pass
`"validity": "30 Days from quote date"` to make them agree.
