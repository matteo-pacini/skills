# Deterministic Balancing Algorithm

All composition figures are **% of total mix by weight**. All POD/PAC per-sugar coefficients are on **sucrose = 100**.

> **PAC scale convention used by this skill (read once).** Mix-total PAC can be normalised two ways. This skill **validates PAC on the per-1000 g *summed* scale** — `Σ(grams_sugar × PAC)/100` over a 1000 g batch — because it is well-defined and matches the worked reference recipes: **gelato 250–290, sorbetto 270–440 (working ~320–380).** The per-100 g-*water* ("pro") figure some sources quote as 24–28 / 30–36 is reported by the calculator **for context only**: the two scales do **not** reconcile by a fixed factor (the ratio moves with each mix's water content), so never validate against a converted band. `scripts/balance.sh` already encodes these bands — run it rather than eyeballing.

---

## Shared formulas (compute these for any mix of weight B grams)

Each ingredient *i* has mass mᵢ and fractional properties: fat fᵢ, MSNF sᵢ, added-sugar fraction, plus a per-sugar breakdown (grams of each sugar it carries), and "other solids" oᵢ (cocoa/nut/yolk/fruit fibre, etc.).

```
TOTAL_FAT_g    = Σ(mᵢ · fᵢ)
TOTAL_MSNF_g   = Σ(mᵢ · sᵢ)
TOTAL_OTHER_g  = Σ(mᵢ · oᵢ)
# per sugar k present anywhere in the mix:
SUGAR_k_g      = Σ over ingredients ( mᵢ · fraction_of_sugar_k_in_i )
TOTAL_SUGAR_g  = Σ_k SUGAR_k_g                 # includes lactose from MSNF? see note
TOTAL_SOLIDS_g = TOTAL_FAT_g + TOTAL_MSNF_g + TOTAL_SUGAR_added_g + TOTAL_OTHER_g + stabiliser_g
WATER_g        = B − TOTAL_SOLIDS_g

%X = 100 · X_g / B          # for every component

# Sweetness and antifreeze (sucrose=100 coefficients):
POD_per1000   = Σ_k ( SUGAR_k_g · POD_k ) / 100        # report scaled to /1000 g
PAC_per1000   = Σ_k ( SUGAR_k_g · PAC_k ) / 100        # include lactose (PAC 100) from MSNF
                 + salt_g·585/100 + alcohol_g·740/100   # if present
PAC_pro       = [ Σ_k (SUGAR_k_g · PAC_k)/100 ] / WATER_g · 100   # per-100 g water
```

**Lactose note:** lactose from MSNF = 0.545 · TOTAL_MSNF_g. Add it to TOTAL_SUGAR_g for the PAC calc (PAC 100) but list it separately from *added* sugars when you report the "16–22% total sugars" composition target (that target conventionally counts added sugars + free sugars, with lactose's role captured via MSNF). Be consistent in the tool and label which convention the "% sugar" field uses.

**Dairy serum-point helper** (when an ingredient sheet is unavailable):
```
MSNF_fraction_of_fluid_dairy = (1 − fat_fraction) · 0.09
# within MSNF: lactose 0.545 · protein 0.36 · ash 0.095
```
Egg-yolk solids, mascarpone fat, butterfat, added sucrose are NOT MSNF.

**Stabiliser unit guard:** if a dose is given in g/kg, % = g/kg ÷ 10. Reject any single-gum "dose" > 0.6% or total > 0.5% as a probable 10× error.

**Alcohol & salt (PAC only).** Ethanol (PAC ≈ 740) and salt (PAC ≈ 585) are far stronger freezing-point depressants than any sugar and carry ~no sweetness, so they sit on a separate scale. The calculator handles them: pass an `alcohol` or `salt` ingredient (or the built-ins `rum`/`vodka`/`limoncello`/`salt`). Alcohol is volatile and non-solid — it lowers solids and stays in the liquid phase — so cap it at **~5% of the mix**; beyond that the gelato won't set (PAC climbs fast). A pinch of salt (~0.1–0.2%) sharpens flavour with negligible PAC effect.

---

## Heating & pasteurisation — pick one path

- **No-cook / cold-process:** valid when you use only cold-hydrating stabilisers (guar, xanthan, λ-carrageenan, CMC), already-pasteurised dairy, and no raw egg. Blend, age cold, churn.
- **Low (long) pasteurisation:** ~65 °C / 30 min — the gentle artisan default; kinder to flavour.
- **High (short) pasteurisation:** ~80–85 °C / 25–30 s — and this is **also the temperature that fully hydrates LBG, tara, pectin and κ-carrageenan**, so with those gums you pasteurise and hydrate in one step (hold LBG ~80 °C for 20–30 min). Custards with egg yolk pasteurise at ~71 °C.
- Whichever you use, **crash-cool to <4 °C fast** (ice bath) and start ageing.

**Ageing (4–12 h cold):** the gums finish hydrating, milk proteins and fat partially crystallise (both improve whip and slow melt), and flavours meld. Minimum ~4 h; overnight is better and the easiest home schedule. A fat-free, stabiliser-free juice sorbet benefits least — churn it sooner.

---

## A. CREAM / WHITE GELATO procedure

**Targets:** TS 36–42% · sugars 16–22% · fat 6–9% (cream styles up to 12) · MSNF 9–12% · stabiliser 0.15–0.2% (egg) or 0.3–0.4% (eggless) · **PAC 250–290 (per-1000 g summed)**.

1. **Choose style** → set fat target T_fat (lean 7, standard 8, cream 10) and MSNF target T_msnf (lean 11, standard 10, cream 8).

2. **Fix fat** with milk + cream (+ WMP/butter if needed). Solve cream grams so 100·Σ(mᵢfᵢ)/B = T_fat. With milk mass M and cream mass C (cream fat f_c), milk fat f_m, and B target:
   `C = (T_fat/100 · B − M·f_m) / f_c`. Iterate M and C to also leave room for sugar/SMP/water.

3. **Compute MSNF₀** from the chosen milk + cream: `MSNF₀_g = Σ(mᵢ·sᵢ)`.

4. **Add SMP** to hit MSNF target: `SMP_g = (T_msnf/100 · B − MSNF₀_g) / 0.96` (clamp ≥ 0).

5. **Enforce the MSNF ceiling** (Rothwell): compute all non-MSNF solids first, then
   `MSNF_max% = (100 − other_solids%) / 7`. Also require total lactose (0.545·MSNF_g) < 7% of B (or ≤9% of WATER_g). If MSNF% exceeds either, reduce SMP and accept lower TS (raise it later with low-DE syrup/maltodextrin instead).

6. **Set sugars** for sweetness (POD) AND softness (PAC) as a 2-variable solve. Pick total added sugar S% in 16–22 (start 18). Choose a blend; solve proportions of a high-PAC/low-POD sugar (dextrose) vs reference sucrose so that:
   - `POD_per1000` lands at the sweetness target (gelato ≈ 165–185 /1000 g, i.e. ~16–18% sucrose-equivalent), and
   - `PAC_per1000` lands in **250–290**.
   Practical start: ~10–12% sucrose + 3–5% dextrose (and/or a low-DE glucose syrup for body). Equal-sweetness swap: replace 1 g sucrose with 1.4 g dextrose to raise PAC without changing POD. Caps: dextrose ≤5% of mix / ≤~30% of sugars; invert ≤6%.

7. **Check TS = fat + MSNF + sugars + other + stabiliser.** If TS < 36, raise it *without* sweetness/softness by adding low-DE glucose syrup or maltodextrin (POD/PAC low) or a little more SMP (respecting step 5). If TS > 42, cut SMP or sugar.

8. **Add stabiliser** per style (egg-rich 0.15–0.2%, eggless 0.3–0.4%; e.g. LBG:guar 60:40). Water = B − solids.

9. **Validate & iterate** with `scripts/balance.sh` until all of {TS, sugars, fat, MSNF, PAC/1000g, MSNF ceiling, lactose cap, stabiliser} are in range. The tool prints a plain-English texture read (firm / scoopable / soft at −12 to −14 °C cabinet temp).

10. **Flavour rebalance by compensation:** when adding cocoa/nut/yolk/fruit "other solids," subtract milk powder/sugar/cream so TS stays 36–42, sugar 16–22, fat in range. For dark chocolate relax MSNF (8–9) and PAC checks and allow sugar 20–23 (offsets bitterness).

**Common flavour patterns** (all use built-in ingredient names — see ingredients.md):
- **Crema (egg custard):** yolk at ~10–12% (e.g. `egg_yolk` 120 g/kg); pasteurise to ~71 °C; use the egg-rich stabiliser band (0.15–0.2%). Yolk solids are fat + other (never MSNF), and yolk PAC ≈ 0, so it adds richness, not softness.
- **Gianduia:** cocoa + hazelnut paste — both "other solids"; runs to the rich end of fat. **Stracciatella:** balance a plain fior di latte, then drizzle ~5–8% melted dark chocolate into the churning gelato in the last minute — it shatters into shards; **don't rebalance for it**.
- **Inclusions (chocolate chips, biscuit, nuts, swirls/variegato):** these are added *after* churning and don't dissolve — **balance only the base mix**, then fold in 8–15% inclusions by weight at the end. Don't put them through the calculator (they'd wrongly inflate the base's fat/sugar).

---

## C. VEGAN (dairy-free cream) procedure — `type: vegan`

Same logic as cream gelato but **no MSNF**: fat comes from coconut cream / plant cream / cocoa butter, and body comes from added "other solids" (plant protein, maltodextrin, inulin) instead of milk solids. Targets: TS 36–42 · sugars 16–22 · **fat 5–12** · MSNF 0 · stabiliser 0.2–0.5% (a touch higher — no milk/egg emulsifier) · PAC 250–290.

1. Pick a plant base (`oat_milk`, `soy_milk`, `almond_milk`) + a plant fat (`coconut_cream`, `plant_cream`, or `cocoa_butter` for a neutral fat).
2. Hit fat 6–9% with the plant cream/fat.
3. Build body to TS 36–42% with **maltodextrin + inulin** (these replace MSNF's body role) — typically 6–10% combined.
4. Set sugars 16–22% with a sucrose/dextrose blend to land PAC 250–290 and POD ~165–185, exactly as for dairy gelato.
5. Stabiliser ~0.35–0.4% (guar+LBG, optionally a little λ-carrageenan). Validate with `scripts/balance.sh -` using `"type": "vegan"`.

---

## D. LIGHT / REDUCED-CALORIE gelato — `type: light`

**Set expectations first:** gelato is *already* the low-fat frozen dessert (6–9% fat vs ice cream's 10–18%), so a classic gelato is only ~170–200 kcal/100 g to begin with. A realistic "light" build lands ~120–135 kcal/100 g — a meaningful ~25–30% cut, not half. The calculator prints **`Energy kcal/100g`** (Atwater estimate) so the saving is visible; `type: light` validates it against a ≤160 ceiling and relaxes the fat and solids floors.

Lever order (biggest calorie saving first, while holding texture):
1. **Cut fat** — the biggest lever at 9 kcal/g. Swap most cream for skim milk; drop fat toward 2–4%. This alone removes the most calories.
2. **Replace some sugar with polyols/fibre.** **Maltitol** is the workhorse: ~half the calories (2.1 vs 4 kcal/g) with sucrose-like sweetness *and* anti-freeze (POD 85, PAC 99), so it swaps in ~1 : 1 without breaking the balance. Add a little **erythritol** for deeper cuts (~0 kcal) but cap it — its very high PAC (280) over-softens and it crystallises/firms above ~8%. **Inulin** (fibre, ~1.5 kcal/g) adds body without sweetness, like maltodextrin but lighter.
3. **Rebuild body** that the lost fat took with it: push **MSNF to ~11%** (protein mouthfeel — watch the lactose ceiling), and **stabiliser to the high end (0.35–0.45%)**.
4. **Hold PAC 250–290 and POD ~150–185** as usual — maltitol makes this easy; if you lean on erythritol, expect PAC to climb and pull back the dextrose.
5. Validate with `"type": "light"`. Mind the **laxative caps** on polyols (erythritol, maltitol, sorbitol in quantity) — keep total polyols moderate and tell the user.

> Intense sweeteners (stevia/sucralose) cut more calories but add **no solids and no PAC**, so you must replace both with inulin/maltodextrin/polyol or the mix freezes hard and thin — the calculator will show it as under-solids / low-PAC. Polyols + inulin (above) are the more robust home route.

---

## B. FRUIT SORBETTO procedure

**Targets:** TS 30–33% · sugars 22–30% (work ~26–28) · fat 0 · MSNF 0 · stabiliser 0.2–0.5% · **PAC 270–440 (per-1000 g summed; working ~320–380)** · final ~30–31 °Bx.

1. **Pick fruit; read its single-strength Brix** (≈ % sugar) and approximate TS from the fruit table (±2 °Bx tolerance).

2. **Choose fruit %** by acidity/intensity, clamped to the fruit's range: high-acid (lemon, passion fruit, blackcurrant, kiwi) 25–35%; medium 40–55%; low-acid mild (peach, pear, melon, fig, banana) up to 55–60% pulp (or 65–78% purée). Lock fruit grams.

3. **Fruit sugar contribution** = (fruit% /100) · fruit_Brix, as % of mix. Also note fruit-supplied solids and water.

4. **Set total sugar target** S% in 22–30 (start 26–28). Apply Corvitto's rule: sorbetto POD should sit ~5–8% (use +6) above the comparable gelato POD — i.e. push sweetness higher than a dairy base.
   `Added_sugar% = S% − fruit_sugar%`.

5. **Split added sugar** to hit POD and PAC simultaneously. Start ~70–80% sucrose + ~20–30% dextrose (≈15–25% of total sugar mass as dextrose/glucose). Solve the 2-variable system:
   - raise **dextrose** to push `PAC_per1000` toward ~320–380 (softer) without much added sweetness;
   - add a little **glucose syrup / atomized glucose** for body if needed;
   - cap **fructose/invert** to avoid cloying.

6. **Check TS (30–33%).** If low (thin/icy), add bulking solids that don't sweeten or freeze: **maltodextrin** (POD ~10, low PAC) or **inulin** (~4–4.5%, ~0 PAC). If high, cut bulking or sugar.

7. **Stabiliser 0.2–0.5%** (dose toward high end for acidic fruit, which weakens gums), pre-mixed with sugar. Pasteurise/heat if blend requires (LBG/tara/pectin → 80 °C). Cool; **age 4–12 h cold**.

8. **Add lemon juice / acid (~1–3%) cold** after pasteurisation (acid weakens hot stabiliser). Brightens; corrects low-acid fruit (banana, melon, pear). Count lemon sugar/acid in the balance.

9. **Validate with `scripts/balance.sh`: PAC/1000g in 270–440 (aim ~320–380)**, TS 30–33, sugars 22–30, final Brix ~30–31. Re-split sugar and iterate if off. For a home −18 °C freezer, push PAC to the high end or temper before serving.

10. **Churn, harden, serve −12 to −14 °C.**

**Chocolate / cocoa sorbetto** is a recognised higher-solids exception: cocoa is solid-dense, so a real chocolate water-ice runs **TS ~33–40%** (above the fruit band) and carries ~1.5–2.5% fat from cocoa butter, which the calculator reports as a `Fat` CHECK rather than a FAIL. Both are expected for the product — use ~6–9% cocoa, sugars ~25–28%, and don't starve it of cocoa to force the fruit-solids band.

---

## Harden & store
Straight from the machine it's soft-serve; harden 2–4 h in the coldest part of the freezer (faster = smaller crystals). Store in a **shallow, airtight container with cling film pressed to the surface** to limit ice and freezer burn. Best within **a few days to ~2 weeks** — homemade gelato lacks the industrial stabiliser package, so each freeze-thaw cycle coarsens it. Always **temper 10–15 min** before serving from a −18 °C freezer.

---

## Handling follow-ups
Re-run `scripts/balance.sh` on each tweak rather than eyeballing — the levers:
- **"make it less sweet"** → shift sucrose → maltodextrin / low-DE syrup (drops POD, holds PAC/body).
- **"I don't have dextrose"** → switch to the supermarket all-sucrose path; raise sugar ~2% to keep PAC, accept a sweeter, slightly firmer result (temper before serving).
- **"too hard / scoops like a rock"** → raise PAC: swap sucrose → dextrose at ~1.4 : 1 (holds sweetness); or just temper.
- **"too soft / won't set"** → lower PAC: swap dextrose → sucrose, or add maltodextrin/low-DE syrup.
- **"double it" / "scale to my machine"** → multiply all grams (percentages and all metrics are unchanged), or pass `batch_g` and let the calculator scale.
- **"no skim milk powder"** → use more cream + a little condensed milk, or accept lower MSNF/TS and lean on stabiliser; rebalance.

---

## Iteration loop (both products)

Repeat until every constraint is satisfied:
```
compute all % and POD/PAC totals
for each out-of-range metric, apply its single-lever fix:
  TS low  → +low-DE syrup / maltodextrin (gelato) or +bulking (sorbet); +SMP (gelato, if MSNF ceiling allows)
  TS high → −SMP / −sugar / −bulking
  sugar high → −sucrose; sugar low → +sucrose
  PAC low (too hard)  → swap sucrose→dextrose (1.4:1, holds POD); or +invert/fructose if also need sweeter
  PAC high (too soft) → swap dextrose→sucrose; or +low-DE syrup/maltodextrin
  POD high → shift toward maltodextrin/low-DE syrup/trehalose
  POD low  → +fructose/invert, pull some dextrose
  fat high/low (gelato) → adjust cream
  MSNF high → −SMP (and/or accept; enforce Rothwell + lactose cap)
recompute; stop when all in range and predicted serve temp ≈ −12 to −14 °C
```
Because each sugar has a distinct POD:PAC ratio, the two sugar levers (sweetness via sucrose/fructose, softness via dextrose) are near-independent — solve them as a small 2×2 system rather than one at a time when both are off.
