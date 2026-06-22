# Worked reference recipes (~1000 g batches)

Every recipe below was balanced and verified with `scripts/balance.py` — all metrics
land in range. Use them as anchors: start from the nearest one and adjust. PAC is on
the **per-1000 g summed** scale (the scale the calculator validates; see method.md).

To reproduce any of these, drop its ingredient list into a recipe JSON and run the
calculator — the printed breakdown matches the figures shown here.

## Fior di latte — advanced (dextrose + SMP)
Cleanest balance; dextrose lets sweetness and softness be tuned independently.

| Ingredient | g |
|---|---|
| Whole milk | 641 |
| Cream 35% | 120 |
| Skim milk powder | 56 |
| Sucrose | 135 |
| Dextrose | 45 |
| LBG : guar blend | 3 |

→ TS 36.2% · sugar 17.6% · fat 6.6% · MSNF 11.6% · stab 0.30% · PAC 277 · POD 174. Scoopable at −12/−14 °C.

## Fior di latte — supermarket-simple (no specialty sugars)
Only sucrose + skim milk powder + a pinch of guar. Note the trade-off: without
dextrose you must run sugar a little higher (~19%) to reach the same PAC, so it reads
slightly sweeter and will scoop a touch firmer from a −18 °C home freezer — temper
10–15 min before serving.

| Ingredient | g |
|---|---|
| Whole milk | 612 |
| Cream 35% | 140 |
| Skim milk powder | 52 |
| Sucrose | 193 |
| Guar gum | 3 |

→ TS 37.9% · sugar 19.3% · fat 7.2% · MSNF 11.1% · stab 0.30% · PAC 254 · POD 203 (quite sweet — the no-dextrose tax).

## Pistachio (advanced)
Nut paste brings fat and "other solids" — so use little/no cream and rebalance by
compensation. Fat runs to the rich end (~9–10%), which is correct for nut gelato.

| Ingredient | g |
|---|---|
| Whole milk | 625 |
| Cream 35% | 50 |
| Skim milk powder | 45 |
| Sucrose | 128 |
| Dextrose | 40 |
| 100% pistachio paste (≈55% fat, 43% other) | 95 |
| LBG : guar blend | 3 |

→ TS 40.8% · sugar 16.7% · fat 9.4% · MSNF 10.2% · stab 0.30% · PAC 256 · POD 165. Paste ≈ 9.6% (target 8–12%).

## Dark chocolate (advanced)
Cocoa adds both fat (cocoa butter) and "other solids." Sugar runs higher (~19%) to
offset bitterness; MSNF sits at the relaxed lower bound because cocoa displaces milk
solids — both intentional for chocolate.

| Ingredient | g |
|---|---|
| Whole milk | 600 |
| Cream 35% | 68 |
| Skim milk powder | 36 |
| Sucrose | 148 |
| Dextrose | 35 |
| Cocoa powder (≈22% fat, 73% other) | 70 |
| LBG : guar blend | 4 |

→ TS 40.3% · sugar 18.8% · fat 6.4% · MSNF 9.4% · stab 0.42% · PAC 269 · POD 186.

## Coffee gelato — `type: gelato`
Instant freeze-dried coffee is "other solids" (~1% of mix carries plenty of flavour).
Sugar runs to the low end — coffee likes a less-sweet base.

| Ingredient | g |
|---|---|
| Whole milk | 600 |
| Cream 35% | 160 |
| Skim milk powder | 40 |
| Sucrose | 120 |
| Dextrose | 45 |
| Coffee, instant freeze-dried | 25 |
| LBG : guar blend | 3 |

→ TS 36.9% · sugar 16.3% · fat 7.9% · MSNF 10.1% · PAC 255 · **182 kcal/100 g**.

## Light coffee gelato — `type: light`
Reduced-calorie version of the above: skim milk replaces most of the cream (fat is the
biggest calorie lever at 9 kcal/g); **maltitol** replaces ~half the sucrose (~half the
calories, sucrose-like sweetness and anti-freeze); inulin + high MSNF + a little extra
stabiliser carry the creaminess that the lost fat would have given. Run as `type: light`.

| Ingredient | g |
|---|---|
| Skim milk | 630 |
| Cream 35% | 75 |
| Skim milk powder | 48 |
| Sucrose | 82 |
| Maltitol | 72 |
| Dextrose | 18 |
| Inulin (body) | 28 |
| Coffee, instant freeze-dried | 12 |
| LBG : guar blend | 4 |

→ TS 35.8% · sugar 17.6% · fat 2.8% · MSNF 11.1% · PAC 255 · POD 172 · **131 kcal/100 g**
(≈ **28% lighter** than the standard coffee gelato, same scoopability). Note: maltitol/
inulin in quantity can be laxative — keep polyols moderate.

## Lemon sorbetto (advanced)
High-acid → low fruit % (lemon juice IS the fruit here, ~20%). Heavy dextrose for
softness at such low fruit; **maltodextrin is the key move** — it lifts total solids
and body without sweetness, so sugar stays mid-band instead of being maxed out just to
clear the 30% solids floor (it counts as "other solids", not sugar%).

| Ingredient | g |
|---|---|
| Water | 500 |
| Lemon juice | 200 |
| Sucrose | 150 |
| Dextrose | 72 |
| Maltodextrin (body, not sugar) | 78 |
| LBG : guar blend | 3 |

→ TS 30.2% · sugar 22.5% · PAC 316 · POD 214 · ≈ Brix 30. No fat/MSNF. (Inulin ~4% can
replace the maltodextrin for an even creamier, lower-PAC body.)

## Strawberry sorbetto (advanced)
Medium-acid → mid fruit % (~47%). Atomized glucose adds body; dextrose keeps it
scoopable without over-sweetening.

| Ingredient | g |
|---|---|
| Strawberry purée | 460 |
| Water | 260 |
| Sucrose | 168 |
| Dextrose | 68 |
| Atomized glucose | 28 |
| LBG : guar blend | 3 |

→ TS 30.6% · sugar 29.8% · PAC 367 · POD 265 · ≈ Brix 31. No fat/MSNF.

## Crema (egg-custard) gelato — `type: gelato`
The classic yellow custard base. Yolk brings fat + "other solids" (never MSNF) and ~0
PAC, so it adds richness without softening. Pasteurise to ~71 °C.

| Ingredient | g |
|---|---|
| Whole milk | 545 |
| Cream 35% | 70 |
| Egg yolk | 120 |
| Skim milk powder | 62 |
| Sucrose | 150 |
| Dextrose | 40 |
| Guar gum | 3 |

→ TS 40.6% · sugar 18.9% · fat 7.8% · MSNF 11.2% · PAC 283 · POD 187. (Lactose sits at
the band edge — egg customs run rich; fine eaten within days.)

## Vegan fior di latte-style — `type: vegan`
Dairy-free: fat from coconut cream, body from maltodextrin + inulin replacing MSNF.
Run with `"type": "vegan"` (MSNF target is zeroed; fat band 5–12%).

| Ingredient | g |
|---|---|
| Oat milk | 545 |
| Coconut cream | 210 |
| Sucrose | 125 |
| Dextrose | 58 |
| Maltodextrin (body) | 58 |
| Inulin (body) | 30 |
| LBG : guar blend | 4 |

→ TS 38.9% · sugar 20.5% · fat 6.9% · MSNF 0% · stab 0.39% · PAC 269 · POD 175. No dairy.

---

These are starting points, not dogma. Real fruit Brix varies ±2 °Bx; re-run the
calculator with the actual fruit and adjust the sugar split until it balances.
