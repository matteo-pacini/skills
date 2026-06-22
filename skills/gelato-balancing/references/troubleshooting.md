# Troubleshooting — symptom → cause → fix

When a user's gelato came out wrong (or you're diagnosing a recipe they already used),
match the symptom here, then re-balance with `scripts/balance.sh` to confirm the fix.
Every row traces to the science in `science.md` / `ingredients.md`. Most defects are a
**single out-of-range metric** — run the calculator first; it usually names the culprit.

| Symptom | Likely cause | Fix |
|---|---|---|
| **Icy / coarse crystals** | Total solids too low (<~35%); no/under-dosed stabiliser; slow home freezing | Raise TS (SMP or maltodextrin); add/raise stabiliser to 0.3–0.4%; churn colder/faster; if still-freezing, stir more often |
| **Rock-hard from the freezer** | PAC too low (all-sucrose); or a cabinet recipe (−12/−14 °C) stored at −18 °C | Swap some sucrose → dextrose at ~1.4 : 1 (holds sweetness, raises PAC); or simply **temper 10–15 min**; for a Ninja Creami, re-spin instead |
| **Soupy / never sets / melts too fast** | PAC too high; too much dextrose/invert/honey; or too much alcohol (>~5%) | Swap dextrose → sucrose; add maltodextrin/low-DE syrup (body, low PAC); cut the alcohol |
| **Gummy / chewy / "snotty"** | Total stabiliser too high (xanthan = slimy, guar = toffee-chewy); or TS >~44% | Cut total stabiliser toward 0.15–0.3%; identify the offending gum; reduce SMP/sugar if TS too high |
| **Sandy / gritty** | MSNF over the lactose ceiling — lactose crystallises | Drop SMP; keep `Lactose %H2O` ≤ ~10.5% (≈ MSNF 12%); prefer SMP over whey powder |
| **Too sweet (but soft enough)** | POD too high | Shift sugar toward maltodextrin / low-DE syrup / trehalose (drops POD, holds PAC) |
| **Not sweet enough (but soft)** | POD too low | Add a touch of fructose/invert; pull some dextrose |
| **Buttery / greasy / churns to butter** | Fat too high and/or over-churned (fast home machines) | Lower fat toward 6–9%; stop churning sooner; this also explains very low overrun |
| **Weeping / wheys off (dairy separates)** | LBG syneresis; egg-yolk water release; under-hydrated gums | Add a pinch of λ-carrageenan; hydrate LBG at ~80 °C; age the mix 4–12 h |
| **Greasy nut/chocolate gelato** | Nut paste / cocoa butter pushed fat over band | Cut cream (the flavour paste brings its own fat); rebalance solids with SMP/sugar |

## Fast diagnosis from the calculator
Run the user's recipe as-is and read the verdict line:
- `Fat %` high → buttery/greasy. `MSNF %` low → thin/icy; high → sandy risk (check `Lactose %H2O`).
- `PAC /1000g` low → too hard; high → too soft. `Total solids %` low → icy; high → gummy/pasty.
- `Stabiliser %` 0 → icy and fast-melting. `POD` out of band → sweetness preference, not a defect.

The `Texture read` line translates the PAC verdict into "firm / scoopable / soft at
−12 to −14 °C" directly. A single FAIL almost always maps to one row above.
