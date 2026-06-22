# Ingredients reference — sugars, dairy, stabilisers

These are the lookup tables. `scripts/balance.py` mirrors them in its built-in
library and coefficient table (`SUGARS`, `LIBRARY`) — if you change a number here,
change it there too. All POD/PAC coefficients are on **sucrose = 100**.

## Two ingredient tiers (the "user picks" choice)

Decide the tier up front (see SKILL.md). Each balancing role has a supermarket
option and an advanced one — the *targets are identical*, only the levers differ.

| Role | Supermarket-simple | Advanced (specialty) |
|---|---|---|
| Main sugar | granulated/caster **sucrose** | sucrose backbone (50–70% of sugars) |
| Anti-freeze / softness | (none — accept a firmer scoop, temper before serving) | **dextrose**, a little **invert**, **glucose syrup** |
| Body without sweetness | a little extra sucrose; egg yolk | **maltodextrin**, low-DE glucose syrup, **inulin** |
| Milk solids (MSNF) boost | **skimmed milk powder** (sold in most supermarkets) or extra cream | SMP, precisely targeted |
| Stabiliser | egg yolk (custard style), or a pinch of **guar/cornflour**, or none | **LBG : guar 60:40** blend (+ a touch of λ-carrageenan if it wheys off) |
| Sorbetto bulking | extra sugar / honey | maltodextrin, inulin, dextrose |

Supermarket gelato will scoop a touch firmer from a home −18 °C freezer — tell the
user to temper it 10–15 min. That is the honest trade-off of skipping dextrose.

## Sugars & sweeteners (sucrose = 100)

Two independent dials: **POD** (sweetness) and **PAC** (anti-freeze). Each sugar has
a different POD:PAC ratio — that is what lets you tune sweetness and softness
separately. PAC here is the anhydrous-molecule value; an ingredient's water/purity is
handled by the sugar *fraction* it carries (e.g. dextrose monohydrate ≈ 0.92 dextrose).

| Sugar | POD | PAC | Practical cap | Role |
|---|---|---|---|---|
| Sucrose | 100 | 100 | 50–70% of sugars | Backbone: body, structure, clean sweetness |
| Dextrose (glucose) | 70 | 190 | ≤5% mix / ~30% of sugars | Anti-crystalliser; big freeze-point drop, mild sweetness |
| Fructose | 173 | 190 | 0–10% mix | Very sweet + high PAC; hygroscopic, can go gummy |
| Invert sugar | 125 | 190 (alt school 98/152) | ≤6% mix / ~30% of sugars | Anti-crystalliser, hygroscopic; prevents iciness |
| Lactose (from MSNF) | 16 | 100 | total <7–9% (sandiness) | Comes free with MSNF; counts toward PAC |
| Glucose syrup 38 DE | 24 | 45 | 5–25% | Long chains → body, chew, anti-crystallising; low sweet/PAC |
| Glucose syrup 42 DE | 52 | 90 | 5–25% | The standard syrup; moderate sweetness/PAC, good body |
| Atomized glucose (DE 38–42) | 24–50 | 45–90 | 5–25% | Spray-dried syrup; same role, dry |
| Maltodextrin (~18 DE) | 10 | 34 | 0–20% | Near-zero sweetness/PAC; pure body, firms a too-soft mix |
| Honey | ~110 (varies) | ~165 (varies) | 0–10% | Invert-like + flavour; **enter actual composition** |
| Trehalose | 45 | 100 | 0–15% | PAC like sucrose, half the sweetness — body without sweet |
| Inulin | ~10 | <20 | 0–5% | Prebiotic fibre; creamy body, not a sweetener |
| Erythritol | 75 | ~280 (anomalous) | <8% w/w | Firms >~8% despite high theoretical PAC; pair with other polyols |
| Stevia / sucralose | 200–600× | ≈0 | as needed | Sweetness but **no solids, no PAC** — replace those separately |

> Why dextrose PAC is quoted 173–190: anhydrous molecule (190) vs the monohydrate
> crystal sold (~173). Same physics, different physical form. Fructose and invert sit
> near 190 in the professional Italian/French school; some tables list ~179/~152.
>
> **As-sold caveat for the swap rule:** the calculator carries dextrose at PAC 190
> *anhydrous* and accounts for the ~92% purity of monohydrate crystal separately, so a
> gram of dextrose *as you weigh it* has an effective PAC ≈ 190 × 0.92 ≈ **175** — i.e.
> ~**1.75× sucrose per gram weighed**, not 1.9×. When you describe the sucrose→dextrose
> softening swap to the user, say "~1.75× the anti-freeze of sucrose per gram," not 1.9×.

Maltodextrin's coefficient (POD 10 / PAC 34) is a single representative figure — the
calculator is **not** DE-keyed, so don't quote a specific maltodextrin DE as if it
changed the numbers. Lower-DE maltodextrin gives even less sweetness/PAC and more body;
treat that qualitatively.

> **Bulking agents vs sugars.** Maltodextrin and inulin are listed above for their
> POD/PAC, but the calculator treats them as **"other solids", not part of the sugar%
> target** — they exist to raise total solids and body *without* adding sweetness. So
> reaching for them on a lean fruit (lemon) lifts TS and softens the scoop while letting
> you keep sugar mid-band. Dextrose, glucose syrup and atomized glucose, by contrast, ARE
> sugars and do count toward sugar%.

> **Energy (calories).** The calculator prints an `Energy kcal/100g` estimate (Atwater:
> fat 9, sugars/most carbs 4, MSNF 3.6, alcohol 7 kcal/g). The calorie levers for a
> `type: light` build are: cut **fat** (9 kcal/g — biggest), and replace sugar with
> **maltitol** (2.1 kcal/g, sucrose-like POD/PAC — the easy swap), **erythritol** (~0
> kcal but very high PAC, cap ~8%), or **inulin** (1.5 kcal/g fibre, body not sweetness).
> Polyols in quantity are laxative — keep them moderate.

**POD:PAC lever:** sucrose 1.0 · dextrose ~0.4 · fructose ~0.9 · invert ~0.7 ·
DE42 ~0.6 · trehalose 0.45 · maltodextrin ~0.5. **Equal-sweetness sucrose→dextrose
swap:** replace 1 g sucrose with ~1.4 g dextrose to raise PAC (softer) at constant
sweetness; reverse to firm up. Typical white-base blend: ~10–12% sucrose + 3–5%
dextrose (and/or a low-DE syrup for body).

## Dairy & fat composition (% by weight; TS = Fat + MSNF + Sugar)

| Ingredient | Fat | MSNF | Sugar | TS | Water |
|---|---|---|---|---|---|
| Whole milk 3.6% | 3.6 | 8.7 | 0 | 12.3 | 87.7 |
| Semi-skim 1.6% | 1.6 | 8.9 | 0 | 10.5 | 89.5 |
| Skim 0.1% | 0.1 | 9.0 | 0 | 9.1 | 90.9 |
| Cream 25% | 25 | 6.75 | 0 | 31.75 | 68.25 |
| Cream 35% | 35 | 5.85 | 0 | 40.85 | 59.15 |
| Cream 38% | 38 | 5.58 | 0 | 43.58 | 56.42 |
| Butter 82% | 82 | ~1.0 | 0 | 83 | 16.4 |
| Skim milk powder (SMP) | ~1 | 96 | 0 | 97 | ~3 |
| Whole milk powder (WMP) | 27 | 70.8 | 0 | 97.5 | 2.5 |
| Sweetened condensed milk | 8.5 | 21 | 44 | ~73 | ~26 |
| Mascarpone | ~44 | ~4 | 0 | ~50 | ~50 |
| Egg yolk | ~27 | — (NOT MSNF) | — | ~47 | ~53 |

**Serum-point rule** when you lack a data sheet: `MSNF of fluid dairy = (100 − %fat) × 0.09`.
Within MSNF: lactose 54.5%, protein 36%, ash 9.5%. **Egg-yolk solids, mascarpone fat,
butterfat and added sucrose are NOT MSNF** (yolk goes to fat + "other solids").

## More built-in ingredients (use these names; composition is in `scripts/balance.py`)

The calculator ships many more named ingredients so you rarely need inline composition:

- **Flavour pastes & solids** (fat + "other", never MSNF): `cocoa_powder` (11% fat), `cocoa_powder_22` (high-fat), `cocoa_mass`, `cocoa_butter`, `dark_chocolate`, `milk_chocolate` (has milk solids), `pistachio_paste`, `hazelnut_paste`, `almond_paste`, `peanut_butter`, `coffee_instant`, `matcha`. Couverture sugar% and cocoa fat vary by brand — enter label values when known.
- **Cultured & plant-based**: `greek_yogurt`, `yogurt`, `creme_fraiche`, `coconut_milk`, `coconut_cream`, `oat_milk`, `soy_milk`, `almond_milk`, `plant_cream`. Plant "milks" carry **no MSNF** (their solids are "other"/sugars) — use `type: vegan` so the MSNF target is zeroed.
- **Common-name sugars**: `brown_sugar`, `maple_syrup`, `agave_syrup` (fructose-dominant), `golden_syrup`. Honey is modelled as its fructose/glucose/sucrose components.
- **Alcohol & salt** (PAC only, ~0 sweetness): `salt` (PAC 585, a solid), `ethanol`, `rum`, `vodka`, `limoncello` (alcohol PAC 740, non-solid). Cap alcohol ~5% of mix. ABV is by volume ≈ 0.79 × by weight.
- **Aliases** so you needn't know canonical names: `caster_sugar`/`granulated_sugar`/`icing_sugar` → sucrose; `corn_syrup` → glucose syrup; `glucose_powder`/`glucose` → dextrose; `milk` → whole milk; `cream`/`heavy_cream`/`whipping_cream` → cream35; `double_cream` → cream38 (UK double is really ~48% fat — enter inline for precision); `milk_powder` → smp; `instant_coffee` → coffee_instant.
- **More fruit**: lime, watermelon, blueberry, apple, cherry, sour_cherry, redcurrant, pomegranate, grape (in addition to the fruit table below).

**MSNF ceiling (sandiness):** lactose super-saturates and turns gritty if MSNF is too
high. Rothwell rule: `max MSNF% = (100 − all-other-solids%) / 7`; also keep total
lactose (0.545 × MSNF) under ~7% of mix. Practical ceiling ≈ 12% MSNF. Prefer SMP
over whey powder (whey is far higher in lactose). The calculator enforces this as a
**`Lactose %H2O`** metric (lactose as a % of the water weight): **PASS ≤ 10.5%** (≈ MSNF
12% at typical ~62% water, the practical artisan ceiling), **CHECK 10.5–12.5%**, **FAIL >
12.5%** — so a recipe that is in the MSNF band but low in water (lots of other solids)
still gets caught. (The conservative long-storage rule, Goff/Hartel, is 9% of water;
home gelato eaten within days tolerates the higher figure, so the gate sits at 10.5%.)

## Stabilisers & thickeners (dose = % of total mix)

Dosed in **tenths of a percent** — use a 0.01 g scale. **% vs g/kg trap:** 0.2% = 2 g/kg
(10× apart). Reject any single-gum dose > 0.6% or total > 0.5% as a probable 10× error.

| Stabiliser | Dose % | Hydration | Overdose fault |
|---|---|---|---|
| Locust bean gum / carob (E410) | 0.1–0.2 (to 0.5 sorbet) | **HOT** ~80 °C | weeping → icy; gummy |
| Guar (E412) | 0.1–0.2 | **COLD** | chewy "toffee"; beany |
| Tara (E417) | 0.1–0.3 | partly cold; full 80 °C | sticky |
| λ-carrageenan (E407) | ~0.02 | **COLD** | gummy; anti-wheying for dairy |
| κ-carrageenan (E407) | 0.015–0.03 | **HOT** | rubbery with dairy >0.03–0.05 |
| CMC (E466) | 0.08–0.2 | cold or hot | sticky, syneresis |
| Pectin (HM/LM, E440) | 0.4–1.0 | hot; LM sets with Ca | brittle |
| Xanthan (E415) | 0.05–0.15 | **COLD**, fastest | **slimy/snotty** (classic fault) |
| Egg yolk (natural) | emulsify 0.5–1 / thicken ≥3 | pasteurise ~71 °C | eggy; subdues delicate flavours |

**Total stabiliser load:** egg-rich gelato 0.15–0.20% · eggless gelato 0.3–0.4% ·
sorbetto 0.15–0.45% · low-fat ~0.25%. Absolute ceiling 0.5%.

**DIY blends** (dry-mix, then always pre-blend the powder into the sugar and disperse
with an immersion blender; heat to 80 °C if it contains LBG/tara/carrageenan/pectin):

| Blend | Ratio | Best for | Dose |
|---|---|---|---|
| Italian classic (Caviezel) | LBG:guar 60:40 | Cream gelato (hot) | 0.2–0.4% |
| Underbelly standard | LBG:guar:λ 4:2:1 | Dairy gelato | ~0.15% |
| Sorbet | LBG:guar:ι:λ 4:2:2:1 | Fruit sorbetto | ~0.3% |
| Simplest | guar alone (cold) | Quick home | 0.05–0.2% |

Most robust home choice: **guar + LBG 40:60**; add a pinch of λ-carrageenan only if a
dairy base wheys off. **Commercial all-in-one bases** are mostly filler (sugar/SMP/
dextrose) + a few % active gum, so the *dose* is high: "Base 50" = 50 g/kg (5%) but
still only ~0.2–0.4% active stabiliser — account for its sugar/SMP in the balance.
