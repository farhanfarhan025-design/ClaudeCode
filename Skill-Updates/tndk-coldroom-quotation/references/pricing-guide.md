# TNDK Cold Room Pricing Guide

Farhan's standard pricing methodology for cold room quotations.

## Material unit costs

These are the baseline costs Farhan uses to estimate. They are **internal estimating prices**, not the prices shown to clients.

| Item | Unit | Cost (QAR) | Notes |
|------|------|-----------|-------|
| Sandwich panel (100mm PUF) | per sqm | 115 | Includes both faces, food-grade GI |
| Cold room door (90×190 cm) | each | 1,800 | Hinged, with safety release |
| Aluminum angles | per 6m piece | 55 | 40×40×2mm L-profile |
| Chequered sheet + plywood (floor) | per pair | 350 | One pair covers ~2.88 sqm |
| Chiller condensing unit + evaporator | set | 8,800 | For chiller duty (+2 to +8°C) |
| Freezer condensing unit + evaporator | set | 6,400 | For freezer duty (smaller, lower capacity) |
| Control panel | each | 1,200 | One per room, IP55, digital controller |
| Pipe + accessories | per system | 2,500 | Refrigerant copper, drier, sight glass, EXV, vibration eliminators |
| Wiring | per system | 1,800 | Power + control wiring within room scope |
| LED vapour-proof lights | for 2 rooms | 500 | Lump sum |

## Calculation formula

For a single cold room with dimensions L × W × H metres:

| Component | Formula | Example (4.5 × 3.5 × 3.5, no floor) |
|-----------|---------|-------------------------------------|
| Wall area | `2(L×H) + 2(W×H)` | `2(4.5×3.5) + 2(3.5×3.5) = 56.00 sqm` |
| Ceiling area | `L × W` | `4.5 × 3.5 = 15.75 sqm` |
| Floor area | `L × W` (only if insulated floor) | excluded |
| **Total panel** | sum | **71.75 sqm** |
| Panel cost | `total_panel × 115` | `71.75 × 115 = 8,251 QAR` |
| Angle pieces | `ceil((4(L+W) + 4H) / 6)` | `ceil((4×8 + 14)/6) = 8 pcs → 440 QAR` |

## Markup methodology

Farhan's standard pricing flow:

1. **Direct cost** = sum of all materials + equipment for both rooms + common items (control panels, pipe, wiring, lights)
2. **Labour & installation** = 15% of direct cost (covers technician time, refrigerant charging, testing)
3. **Transportation & handling** = ~1,500 QAR lump sum within Doha
4. **Subtotal cost** = direct cost + labour + transport
5. **Quote price** = subtotal × (1 + margin), where margin is **20-30%**

| Margin | Quote multiplier | Use when |
|--------|------------------|----------|
| 20% | 1.20 | Highly competitive bid, government tender, repeat client |
| 25% | 1.25 | Standard market quote |
| **30%** | 1.30 | **Recommended default** for new clients |
| 35% | 1.35 | Premium / urgent / difficult site access |

## Worked example: Mr. Suresh case (April 2026)

**Rooms:**
- Vegetable Chiller: 4.5 × 3.5 × 3.5 m (no floor)
- Freezer: 2.35 × 2.0 × 2.40 m (with floor)

**Direct material cost: 43,448 QAR**

| Item | Calc | QAR |
|------|------|-----|
| Chiller panels | 71.75 sqm × 115 | 8,251 |
| Chiller angles | 8 pcs × 55 | 440 |
| Chiller door | 1 × 1,800 | 1,800 |
| Chiller cond+evap | 1 × 8,800 | 8,800 |
| Freezer panels | 30.28 sqm × 115 | 3,482 |
| Freezer angles | 5 pcs × 55 | 275 |
| Freezer door | 1 × 1,800 | 1,800 |
| Freezer floor (chequered+ply) | 2 pairs × 350 | 700 |
| Freezer cond+evap | 1 × 6,400 | 6,400 |
| Common: control panels | 2 × 1,200 | 2,400 |
| Common: pipe & accessories | 2 × 2,500 | 5,000 |
| Common: wiring | 2 × 1,800 | 3,600 |
| Common: lights | lump | 500 |
| **Total direct** | | **43,448** |

**Cost summary:**
- Direct: 43,448
- Labour (15%): 6,517
- Transport: 1,500
- **Subtotal cost: 51,465**

**Quote at various margins:**
- 20% → 61,758 → round to 62,000
- 25% → 64,331 → round to 64,500
- 30% → 66,905 → round to 67,000
- Final negotiated: **59,000 QAR** (effective margin ~14.6%)

## Per-room split heuristic

When a client asks for per-room pricing on a single quote, allocate:

1. **Calculate each room's direct cost** (panels + angles + door + cond/evap + floor if applicable)
2. **Add room's share of common items** (typically 50/50 if comparable, or weighted by panel area)
3. **Apply same margin %** to each
4. **Round each to nearest 500 or 1000 QAR**
5. **Verify** the two parts sum to (or close to) the desired grand total; adjust by trimming the larger room's price

For Mr. Suresh's 59,000 split: Chiller 32,500 + Freezer 26,500.

## Standard payment terms

- 50% advance with confirmed LPO
- 40% on material delivery
- 10% on testing & commissioning

These are baked into Section 13 of the master template.

## VAT

Quotes are **exclusive of 5% VAT**. The master Grand Total row already says "Lump Sum, Excluding 5% VAT" — keep that intact.

## Things to exclude from scope (already in master)

The master Section 9 already excludes:
- Civil works, foundation, levelling
- Power supply (MDB to control panel)
- Drain piping beyond 3 m
- Backup power, UPS, generator
- BMS / IoT / CCTV integration
- Lifting equipment beyond manual handling
- Working at heights above 3 m
- Anything not in scope (Section 8)

If a specific job has additional exclusions, add them in Word after generating.

## Validity

Standard validity is **15 days** (already in master). For large projects or government tenders, extend to 30 days by passing `--validity "30 days from quote date"`.
