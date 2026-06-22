# Gelato & Sorbetto Balancing — Master Reference

## 0. Scale conventions (read first — this prevents 10× and 100× errors)

Two quantities drive every balance: **POD** (sweetness) and **PAC** (anti-freezing / freezing-point depression). Each appears on incompatible scales in the literature. **This reference fixes one convention and uses it everywhere. Every number below is on these scales unless explicitly tagged otherwise.**

### Per-sugar coefficients — `sucrose = 100`
- **POD** = *Potere Dolcificante* (sweetening power). Sucrose = 100. Sensory, panel-derived, NOT calculable from physics; concentration-dependent for some sugars (fructose, trehalose).
- **PAC** = *Potere AntiCongelante* (anti-freezing power; also AFP / FPDF / sucrose-equivalent). Sucrose = 100. Colligative, so for a pure sugar it tracks molar concentration:
  > **PAC(sucrose=100) = (MW_sucrose / MW_sugar) × 100**, with MW_sucrose = 342.30 g/mol.

This is the scale used by Corvitto, Caviezel, Boiron, iceicedaddy, eccounpoco, gerogelato, Underbelly, icecreamcalc. (A decimal variant divides everything by 100: dextrose PAC 190 → 1.9. Multiply by 100 to return to this reference.)

### Mix totals — two reported figures, both defined, both labelled
When you sum coefficients over a recipe you get a number whose magnitude depends entirely on normalisation. **This reference reports mix totals two ways and always labels which:**

| Mix-total convention | Definition | Gelato target | Sorbetto target |
|---|---|---|---|
| **PAC/POD per-1000 g (summed)** — `Σ(grams_sugar × coeff)/100` over the whole 1000 g batch | The raw sum. Used by icecreamcalc / Underbelly. | PAC ≈ 250–290; POD ≈ 165–185 | PAC ≈ 270–440; POD ≈ 140–270 |
| **PAC "pro / Caviezel-Corvitto" (per-100 g water)** — the summed sucrose-equivalent grams divided by the mix's **water** grams, ×100 | "g sucrose-equivalent per 100 g water." Used by Caviezel, Corvitto, the Gelatologist articles. | **PAC 24–28** | **PAC 30–36** |

**Why the ~10× gap and why it is NOT a fixed factor.** The per-1000 g figure sums over the *whole batch*; the pro figure divides by *water only*. Since water is ~60% of a gelato and ~70% of a sorbetto, the ratio between the two figures changes with the recipe's water content. Treat "divide icecreamcalc-style PAC by ~10 to reach the 24–36 band" as a rough heuristic, never an exact conversion.

**Convention this skill follows:** store per-sugar coefficients on sucrose=100; compute and display **both** mix totals with explicit labels; **validate on the per-1000 g summed scale (gelato 250–290, sorbetto 270–440)** and report the per-100 g-water "pro" figure for context only. The pro band 24–28 / 30–36 quoted by Caviezel/Corvitto does **not** reproduce from the per-100 g-water formula for a normal-water mix (a typical 18%-sugar gelato lands near 40+ on that formula), and the two scales are not a fixed multiple — so the summed scale, which matches the worked recipes, is the one enforced. `scripts/balance.py` encodes this. A bare "PAC 26" vs "PAC 260" is otherwise ambiguous.

### PAC → serving-temperature rule of thumb (pro scale)
- **Gelato:** serving temp (°C) ≈ −(PAC ÷ 2) → PAC 24–28 ⇒ −12 to −14 °C
- **Sorbetto:** serving temp (°C) ≈ −(PAC ÷ 2.5) → PAC 30–36 ⇒ −12 to −14 °C

The larger divisor for sorbetto reflects that, at equal PAC and temperature, a fat-free sorbetto freezes harder (more frozen water) than a gelato. A more rigorous target is the **mix freezing point ≈ −2.75 to −3.0 °C** and the **% of water frozen at serving temp** (see §1, scoopability).

### What PAC physically does
Higher PAC lowers the freezing point, so at any fixed serving temperature a **higher-PAC mix has more unfrozen water → softer, more scoopable**; lower PAC → harder/icier. Overshoot = soupy, never sets, melts fast; undershoot = brick. icecreamcalc states it directly: "the higher the PAC, the softer your ice cream will be at any given temperature."

> **Salt and alcohol** have very high freezing-point depression per gram (reference PAC ≈ 585 for NaCl, ≈ 740 for ethanol) and are NOT well modelled by the sugar PAC scale — handle them separately from molality if present.

---

## 1. Cream / white (fior di latte) gelato — composition framework

All figures are **% of total mix by weight**. Targets for a base churned in a domestic/artisan batch freezer and served from a display cabinet at **−12 to −14 °C**.

> Identities: `Fat + MSNF + Sugars + Other solids + Stabiliser = Total solids`; `Total solids + Water = 100`.

| Component | Recommended | Min–Max seen | Role |
|---|---|---|---|
| **Total solids (TS)** | **36–42%** | 32–44% | The master texture lever. More TS = less free water = smaller ice crystals = smoother, denser, slower melt. <~35% → coarse/icy; >~44% → pasty, gummy, muted flavour. |
| **Total sugars** | **16–22%** (Carpigiani narrows to 18–22) | 16–24% | Sweetness **and** freezing-point depression. Too little = icy brick; too much = soupy, never sets, over-sweet. Use a **blend**, not all sucrose, to tune sweetness and softness independently (§3). |
| **Total fat** | **6–9%** (lean Italian white base); **up to 6–12%** for cream styles | 4–16% | Richness, creamy mouthfeel, flavour carrier, slows melt, makes crystals read smaller. Schools genuinely disagree on the band — see note below. |
| **MSNF** (milk solids-non-fat) | **9–12%** | 7–12% | Protein gives body/chew and emulsion stability; lactose + minerals add solids and depress freezing point slightly. Cheapest way to raise TS without fat/sugar — but has a **hard ceiling** (§2). |
| **Other solids** (cocoa, nut paste, yolk, fruit) | **0%** plain; 5–10% once flavoured | 0–10% | Zero in a true white base. When flavoured, these enter the TS budget → rebalance by compensation. |
| **Stabiliser/emulsifier ("neutro")** | **0.3–0.5%** (eggless); 0.15–0.2% egg-rich | 0.2–0.6% | Binds free water, slows recrystallisation, improves body/melt resistance. Too much = gummy/snotty (§5). |
| **Water** | **58–64%** | ~56–68% | The remainder. Water-to-solids ratio ultimately governs crystal size and hardness; you size everything else and water balances. |

**Fat band is school-dependent** (a real spread, not an error): Dream Scoops/Goff 4–8%; freegelatobalancing 6–9%; Caviezel/alcremista 6–12%; Carpigiani 7–16% (top end = rich cream styles). Italian white base is deliberately leaner and softer than American ice cream (10–18% fat).

### Scoopability vs serving temperature
Texture is set by the **% of water frozen at serving temp**, tuned mainly by sugars/PAC and TS. The two leading sources genuinely disagree on the target fraction — state which you follow:

| Source | Gelato (cabinet) | Ice cream / firm |
|---|---|---|
| **icecreamcalc** | **~69% frozen** at −12 to −14 °C | ~75% frozen |
| **Gelatologist** | one **75–80% band** for both gelato and sorbetto (≈75 = soft "Bologna"; ≈80 = firm; author prefers ~77–78) | — |

If a cabinet-balanced recipe (−12 to −14 °C) is stored in a domestic −18 °C freezer it will be **too hard** — raise sugars/PAC (lean toward dextrose/invert) or temper 10–15 min before serving.

### How ranges shift by style
- **Richer/cream:** push fat to 9–12% (up to 16%), drop MSNF toward 7–9% (fat and MSNF compete for the solids budget and over-stabilise the emulsion if both are high). Slightly lower sugar is fine — fat also softens perceived texture.
- **Leaner/very milky:** fat 6–8%, MSNF 10–12% (to the lactose ceiling), lean on the sugar blend + stabiliser for body and crystal control.
- **Flavoured from the white base ("rebalance by compensation"):** when cocoa/nut/yolk solids arrive, subtract milk powder, sugar or cream so TS stays 36–42%, sugar 16–22%, fat in range.

---

## 2. The MSNF ceiling (lactose / sandiness)

MSNF on a dry basis is ~**54.5% lactose, ~36% protein, ~9.5% minerals/ash** (icecreamcalc verbatim; 0.545 + 0.36 + 0.095 = 1.000). Pushed too high, lactose super-saturates in the shrinking unfrozen phase, crystallises, and gives gritty **"sandiness."** Several equivalent framings circulate; they land in a similar place but the denominator is not standardised:

- **Tharp & Young (vs total mix):** lactose **< 7–7.5%** of the mix is safe; **< 11%** is the upper bound.
- **Water-phase framing (Goff/Hartel):** lactose **≤ ~9% of the water weight** (6 g lactose / 66 g water ≈ 9%).
- **Rothwell (1985) hard ceiling — the rule to enforce:**
  > **Max MSNF (%) = (100 − all-other-solids %) / 7**
  (Sum every solid *except* MSNF, subtract from 100, divide by 7.)
- **Practical shorthand:** MSNF tops out near **12% of the mix** for a typical base. Since lactose ≈ 0.545 × MSNF, ~7.5% mix-lactose ⇄ ~13–14% MSNF in a typical formulation (the exact MSNF ceiling shifts with the mix's water/solids ratio).
- Prefer **skim-milk powder** over whey powder for MSNF — whey is far higher in lactose (skim MSNF ≈ 54% lactose).

Typical/target MSNF: **9–12% of mix** for ice cream; **gelato ~8–12%** (commonly cited 10–12, or 11–12). State the scale: this is % of the **total mix**, not % of solids.

---

## 3. Sugars & sweeteners (sucrose = 100)

Two independent dials: **POD** (sweetness) and **PAC** (anti-freeze). Because each sugar has a different **POD:PAC ratio**, swapping one sugar for another moves sweetness and softness by different amounts — that is the whole trick.

### Master sugar table

PAC for pure sugars is MW-derived (scale A). Commercial products carry water, so the **as-sold** value is the anhydrous PAC × dry-matter fraction (scale B). A tool should store either the pure value + a separate water content, **or** the discounted commercial value — never both.

| Sugar | POD | PAC (pure / MW, scale A) | PAC (commercial / as-sold, scale B) | Cap | Role |
|---|---|---|---|---|---|
| **Sucrose** (ref) | **100** | **100** | 100 | 50–70% of sugars | Backbone; body, structure, balanced sweetness |
| **Dextrose** (glucose) | 70–75 | 190 (anhydrous) | 173–180 (monohydrate, ~92% solids → 190×0.92 ≈ 174.8) | ≤5% mix / ~30% of sugars | Anti-crystalliser; big freeze-point drop, mild sweetness → adds PAC without over-sweetening |
| **Fructose** | 170–173 | 190 | 179 | 0–10% of mix (sparingly) | Very sweet + high PAC; hygroscopic → softer, can go gummy. Comes free from fruit |
| **Invert sugar** | 120–130 | 190 | 150–167 (~75–80% solids) | ≤6% mix / ~30% of sugars | Anti-crystalliser, hygroscopic; prevents iciness, extends scoopability (icecreamcalc gives a lower ~152/98 variant) |
| **Lactose** (from MSNF) | 15–16 | 100 | 100 | total lactose <~7–9% (see §2) | Comes free with MSNF; counts toward PAC; sandiness risk |
| **Glucose syrup 38 DE** | ~24 | 45 | 45 | 5–25% | More long chains → body, anti-crystallising, chewy; low sweetness/PAC |
| **Glucose syrup 42–44 DE** | 50–52 | 90 (DE42 ~80–90) | 80–90 | 5–25% | The standard syrup; moderate sweetness/PAC, good body |
| **Glucose syrup 21 DE** | 10 | 20 | 20 | 5–20% | Solids + body, very low sweetness/PAC |
| **Glucose syrup 60 DE** | ~55–65 *(est.)* | ~95–120 *(est.)* | — | 5–20% | Higher DE → sweeter, higher PAC, less body. **Direction confirmed; exact figures are interpolation** |
| **Atomized/dried glucose** (DE 38–42, powder) | 24–50 | 45–90 | 45–90 | 5–25% | Spray-dried syrup (5–7% water); same role dry; PAC/POD ≈ matching syrup × ~1.05–1.1 |
| **Maltodextrin (~18 DE)** | 5–21 | 34 | ~34 | 0–20% | Polysaccharide; near-zero sweetness, low PAC; adds solids/body, binds water, firms a too-soft mix |
| **Honey** | ~94–130 (varies) | 146–190 (≈156) | 146–156 | 0–10% | Behaves like invert + flavour; high PAC, hygroscopic. **Enter actual composition — values scatter** |
| **Trehalose** | 45 | 100 | 100 | 0–15% | Disaccharide (MW 342) → PAC like sucrose, ~½ the sweetness. Ideal to add PAC/body without sweetness |
| **Inulin** | ~10 | <20 | <20 | 0–5% | Prebiotic fibre; texturiser not sweetener; creamy body in low-fat/sorbet, binds water |
| **Sorbitol** (polyol) | 60 | ~188 (MW 182) | — | sugar-free | Strong anti-freeze/softener, humectant, cooling; pairs with erythritol |
| **Maltitol** (polyol) | 80–90 | ~99 (MW 344) | — | sugar-free | ~80–90% sweetness, PAC ≈ sucrose; laxative threshold |
| **Erythritol** (polyol) | 70–80 | ~280 (MW 122) **but anomalous** | — | <8% w/w mix | Tiny molecule → huge theoretical PAC, yet *raises* hardness / crystallises >~8% → pair with other polyols. Zero glycemic, cooling |
| **Glycerol/glycerin** | ~60 | ~372 (MW 92) | — | <2–3% (trace) | Extreme PAC per gram; micro-dose softener; off-flavour/laxative if overused |
| **Stevia / sucralose** | 200–600× per weight | ≈0 | ≈0 | as needed | High-intensity; sweetness but **no solids, no PAC** → replace missing PAC/solids with maltodextrin/polyol/inulin or it freezes rock-hard |

> **Why "dextrose PAC" is quoted 173–190:** sources differ on anhydrous molecule (190) vs the monohydrate crystal actually sold (~173), or apply an 8–9% bound-water discount (190×0.92 ≈ 174.8). Same physics, different physical form. The professional Italian/French school (iceicedaddy + Boiron) places dextrose = fructose = invert all at 190 on the pure scale.

### Blending to tune sweetness and softness independently
POD:PAC ratios (the lever): sucrose 1.0, dextrose ~0.4, fructose ~0.9, invert ~0.7, DE42 syrup ~0.6, DE38 syrup ~0.5, trehalose 0.45, maltodextrin ~0.5, honey ~0.7.

- **Low POD:PAC** (dextrose, trehalose, low-DE syrup, maltodextrin) → adds anti-freeze without much sweetness.
- **High POD:PAC** (fructose) → adds sweetness with proportionally less extra softening.
- **Classic move — partial sucrose → dextrose swap at equal sweetness:** since dextrose POD ≈ 70, use ~1.4 g dextrose per 1 g sucrose removed to hold POD constant; total PAC rises → **softer at the same sweetness**. Reverse to firm up.
- **Too sweet but too hard?** Shift toward maltodextrin / low-DE syrup / trehalose (drops POD, adds body, modest PAC).
- **Not sweet enough but already soft?** Add a touch of fructose/invert and pull some dextrose.
- **Guardrails:** total sugars 16–22% (gelato); monosaccharides/invert capped ~25–35% of total sugars (dextrose ≤~5% mix, invert ≤~6%) to avoid an over-soft, wet, hygroscopic gelato.

Typical white-base blend: **~10–12% sucrose + 3–5% dextrose and/or a low-DE glucose syrup.**

### Computing a mix's POD and PAC
For each ingredient, sum the contribution of each sugar it carries:
> grams of sugar *i* = (ingredient grams) × (its % of that sugar) — e.g. milk ≈ 4.9% lactose; commercial dextrose monohydrate ≈ 92% dextrose; fruit purées carry fructose + glucose + sucrose per the fruit profile.

- **POD_total (per-1000 g)** = Σ(grams_sugar × POD)/100
- **PAC_total (per-1000 g)** = Σ(grams_sugar × PAC)/100 + contributions from lactose/salts in MSNF (and salt/alcohol handled separately)
- **PAC_pro (per-100 g water)** = [Σ(grams_sugar × PAC)/100] ÷ (water grams) × 100

---

## 4. Dairy & fat ingredient composition

All values **% by weight**. Per row: TS = Fat + MSNF + Sugar; Water = 100 − TS. Added sucrose is the "Sugar" column; **lactose is counted inside MSNF, not here.**

**The serum-point rule** every calculator uses (a uniform-9%-serum approximation):
> **MSNF of a fluid dairy = (100 − %fat) × 0.09**, and within MSNF: lactose = 0.545·MSNF, protein = 0.36·MSNF, ash = 0.095·MSNF.

Real fluid milk is ~3.7% fat / ~9% SNF; US standardized whole milk is 3.25% fat / ≥8.25% MSNF. The table uses the serum-point scale throughout for internal consistency — swap in a technical data sheet when you have one.

| Ingredient | Fat % | MSNF % | Sugar % | TS % | Water % | Notes |
|---|---|---|---|---|---|---|
| Whole milk (3.6%) | 3.6 | 8.7 | 0 | 12.3 | 87.7 | US legal: 3.25% fat / ≥8.25% MSNF / ~12% TS |
| Semi-skim (~1.6%) | 1.6 | 8.9 | 0 | 10.5 | 89.5 | serum-point |
| Skim / nonfat (~0.1%) | 0.1 | 9.0 | 0 | 9.1 | 90.9 | ~4.8% lactose, ~3.6% protein, ~0.7% ash |
| Cream 25% | 25 | 6.75 | 0 | 31.75 | 68.25 | serum-point |
| Cream 35% | 35 | 5.85 | 0 | 40.85 | 59.15 | "heavy cream" 35–40% |
| Cream 38% | 38 | 5.58 | 0 | 43.58 | 56.42 | Italian *panna* 35–38% |
| Butter (~80–82%) | 82 | ~1.0–1.8 | 0 | 83.6 | 16.4 | serum-point gives ~1.4–1.6; real churned butter often ~1.0 (serum lost in churning); std caps non-fat ≤2%, water ≤16% |
| Skim milk powder (SMP/NFDM) | ≤1.5 (~1) | ~96–97 | 0 | ~97 | ~3 | The MSNF concentrate; fat ≤1.5% cap; calculators use 96% or 97% MSNF; prefer over whey |
| Whole milk powder (WMP) | 26–28 (~26.7) | 67–71 (~70.8) | 0 | ~97.5 | 2.5 | Legal 26–<40% fat; MSNF varies ~67–71% across 26–28% fat band; moisture ≤5% |
| Sweetened condensed milk | 8–9 | 20–22 | 43–45 | ~72–74 | 25–27 | CFR: ≥8% fat, ≥28% total milk solids (→ MSNF ≥20%); sucrose ~43.5–45% in Sugar column |
| Evaporated milk | ≥6.5 (7.5–8) | ≥16.5 (~18) | 0 | ≥23 (~25–26) | ~74–77 | CFR min 6.5/16.5/23; ~2:1 concentration of whole milk |
| Mascarpone | 40–47 (~44) | ~3.5–5 | 0 | ~47–53 | ~47–53 | Fat is **not** MSNF |
| Egg yolk (raw) | ~27 (trade 28–30) | — | — | ~47–48 | ~52–53 | Yolk solids are **fat + "other solids," never MSNF**; one large yolk ≈ 17 g, ~50% solids |

**Classification rule:** only protein + lactose + minerals from milk/cream/SMP/WMP/condensed/evaporated count as MSNF. Egg-yolk solids, mascarpone fat, butterfat, added sucrose are **not** MSNF — yolk goes to fat + "other solids."

### Computing total fat & MSNF
For a batch of weight B from masses mᵢ with fat fraction fᵢ and MSNF fraction sᵢ:
```
% fat  = 100 × Σ(mᵢ·fᵢ) / B
% MSNF = 100 × Σ(mᵢ·sᵢ) / B
```
**Worked example (1000 g target):** 700 g whole milk (f .036, s .087) + 150 g cream 35% (f .35, s .0585) + 40 g SMP (f .005, s .96):
```
Fat  = 25.2 + 52.5 + 0.2  = 77.9 g  → 7.79%
MSNF = 60.9 + 8.78 + 38.4 = 108.1 g → 10.81%
```
**Inverse (solve SMP for an MSNF target M, baseline MSNF₀, SMP at 96%):** `X = (M − MSNF₀) / 0.96`.
Two-equation Pearson-square form for skim Y + SMP Z:
```
Y + Z = serum mass remaining
0.09·Y + 0.96·Z = MSNF grams needed
```
**Procedure:** (1) fix fat with milk + cream (or butter/WMP); (2) compute MSNF₀ from that dairy; (3) add SMP X = (target − MSNF₀)/0.96; (4) check Rothwell ceiling + lactose cap and back off if exceeded.

---

## 5. Stabilisers & thickeners

Hydrocolloids bind free water, raise unfrozen-phase viscosity, slow recrystallisation (heat-shock resistance), control meltdown, improve overrun and scoopability. Dosed in **tenths of a percent of total mix** — use a 0.01 g scale.

**Number-system trap:** "% of total mix" vs "g/kg" (numerically 10×; 0.2% = 2 g/kg). Sanity check: icecreamcalc's single-gum blend = 0.8 g LBG + 0.4 g guar / 1000 g = 1.2 g/kg = **0.12%**. "1.2%" would be a 10× error. All "%" figures below are % of mix.

| Stabiliser (E#) | Function | Dose (% mix) | Hydration | Overdose fault |
|---|---|---|---|---|
| **Locust bean gum / carob (E410)** | Best conventional crystal suppressor; smooth warm creamy body; heat-shock resistance | 0.1–0.2 solo; up to 0.3–0.5 (sorbet/high-water); plateau ~0.3 | **HOT** ~80 °C, 20–30 min; ~2 h to max viscosity | Syneresis/weeping → icy; grainy; gummy; dampens flavour |
| **Guar (E412)** | Viscosity/body; less crystal control than LBG; resists wheying-off | 0.1–0.2 (to 0.25); 0.05–0.1 in blends | **COLD**, ~1 h | Chewy "toffee"; lumps; "beany" off-flavour |
| **Tara (E417)** | Between LBG and guar; improves overrun | 0.1–0.3; sorbet ~80:20 tara:guar | **PARTLY COLD**; full at 80 °C | Sticky if overdone |
| **Sodium alginate (E401)** | Small crystals; body; fluid gel under shear | 0.1–0.5 | **COLD**; best 68–71 °C; gels with Ca²⁺ | Rigid gel with too much Ca / low pH |
| **κ-Kappa carrageenan (E407)** | Anti-wheying (binds casein); firm brittle gel with dairy/Ca²⁺ | **0.015–0.03** (secondary role) | **HOT** 70–80 °C | Rubbery/sticky with dairy above ~0.03–0.05% |
| **ι-Iota carrageenan (E407)** | Soft freeze-stable shear-reversible gel | ~0.066 (sorbet blends) | Room temp + mild heat | Gummy if overdone |
| **λ-Lambda carrageenan (E407)** | Non-gelling thickener; strongest on melted-cream consistency; anti-wheying — **preferred carrageenan for dairy** | ~0.02 | **COLD**, fast | Gummy if overdone |
| **CMC / cellulose gum (E466)** | Possibly stronger crystal suppressor than LBG; body, sheen | ~0.08; up to 0.1–0.5 | **COLD or HOT** | Sticky; syneresis; over-gelling (synthetic label) |
| **HM pectin (E440)** | Casein-protective colloid in acidic/fruit gelato | ~0.4–1.0 (4–10 g/kg) | Needs **>55% solids, pH 2.8–3.5**; hydrate hot | Brittle, sticky |
| **LM pectin (E440)** | Gels with Ca²⁺ at low sugar — for sorbet | ~0.4–1.0 (to 1.5) | Cold/hot; sets ~50–70 °C (Ca-dependent; some sheets to 85) | Brittle/over-set |
| **Xanthan (E415)** | Pseudoplastic; stable hot/cold, freeze-thaw, pH, alcohol | 0.05–0.15 (light 0.06, full 0.12) | **COLD**, fastest of all gums | **Slimy/snotty** (classic fault); wheys off with milk if high/alone |
| **Gelatin (E441)** | Crystal suppression, smooth body (traditional) | ~0.2 (~2 g/kg, 1 sheet/L) | **HOT-bloom** 50–60 °C; long ageing | Brittle; cost; animal product |
| **Egg yolk** (natural emulsifier) | Lecithin emulsifier (dry creamy body, small bubbles/crystals) | **Emulsify 0.5–1%; thicken ≥3%**; custard 4–6 yolks/L | Pasteurise ~71 °C | Eggy taste; subdues delicate flavours; water leak → icy |

### Recommended TOTAL stabiliser/emulsifier load
| Product | Total (% mix) |
|---|---|
| Cream/white gelato, egg-rich (yolk does part of the work) | **0.15–0.20%** |
| Cream gelato, eggless (must replace egg function; add lecithin) | **0.3–0.4%** |
| Fruit sorbetto | **~0.15–0.45%** |
| Low-fat / fat-free | **~0.25%** |

Rule of thumb (icecreamcalc): start ~0.25% of **water weight** ≈ 0.12% of total single-gum, then adjust. Absolute ceiling 5 g/kg = 0.5%. High-pectin/pulpy fruit (mango, peach, citrus, apple, berries) needs less or no added stabiliser.

### DIY blends (dry-blend airtight; always pre-mix powder into sugar, disperse with immersion blender, heat to 80 °C for LBG/tara/carrageenan/pectin)
| Blend | Ratio | Best for | Dose |
|---|---|---|---|
| Italian classic (Caviezel) | LBG:guar = 60:40 | Cream gelato (hot) | 0.2–0.4% |
| Underbelly standard | LBG:guar:λ = 4:2:1 | Dairy gelato | ~0.15% |
| Underbelly sorbet | LBG:guar:ι:λ = 4:2:2:1 | Fruit sorbetto | ~0.3% |
| Tara sorbet (Caviezel) | tara:guar = 80:20 | Juice/low-pulp | 0.15–0.45% |
| No-cook/eggless | guar:xanthan ≈ 1:1, or gelatin:xanthan 3:1 | Cold-process home | ~0.13–0.15% |
| Simplest | guar alone (cold) | Quick home | 0.05–0.2% |

Most robust home choice: **guar + LBG ~40:60** (~¾ tsp blend/L); add a pinch of λ-carrageenan only if a dairy base wheys off.

**Commercial all-in-one bases** are mostly filler (sugar, SMP, dextrose) + a few % active gum/emulsifier, so the *dose* is high: "Base 50" = 50 g/kg (5%); "Base 100" = ~10%; concentrated "Neutro/Base 5" = 5–10 g/kg (0.5–1%). A Base 50 still delivers only ~0.2–0.4% active stabiliser.

**Overdose guardrails:** slimy = xanthan; chewy/toffee = guar; gummy/rubbery = carrageenan or total too high; weeping/icy = LBG syneresis or yolk water release; brittle/sticky = pectin/gelatin. Age the mix 4–12 h cold for full hydration.

---

## 6. Fruit sorbetto (no dairy)

Sorbetto = fruit + water + sugars + a little stabiliser. With **no fat and no MSNF**, sugars must carry both sweetness *and* texture, so sorbetto runs **higher sugar and higher PAC than dairy gelato**. **Corvitto's rule:** raise sweetness (POD) by **+5–8% (he uses +6%)** vs the gelato base — e.g. gelato ~18% POD → sorbetto ~24% POD — to land at the same scoopability.

### Targets (% of total mix)
| Parameter | Target | Notes |
|---|---|---|
| Total solids | **30–33%** (~25% floor for light dessert sorbets, soft) | Lower than gelato — no fat/MSNF |
| Total sugars | **22–30%** (working ~26–28) | vs gelato 16–22 |
| Fruit (purée/juice) | **25–70%** (typical ~40) | Driven by intensity/acidity (§7), not just sugar |
| Water (total) | **67–70%** | Added water = remainder after fruit + sugars |
| Stabiliser | **0.2–0.5%** | Acidic fruit weakens stabiliser → dose toward high end |
| Final Brix | **~30–31 °Bx** (≈17–18 °Baumé) | Dessert sorbets 25–30 °Bx |
| **PAC (pro scale)** | **30–36** | serve −12 to −14 °C (≈ PAC÷2.5); home freezers −18 °C → use high end (~36) or temper |

> Sugar spectrum is normally sucrose-heavy with ~**15–25% of sugar mass as dextrose/glucose** (a common base ~80% sucrose / ~20% dextrose) for antifreeze/scoopability.

### Raising TS without sweetness or excess PAC
- **Maltodextrin (DE ~18 and lower):** POD ~10 (the calculator's value; sources scatter 5–21), low PAC → pure body/dry-extract filler.
- **Inulin:** ~0 PAC, very low sweetness; creamy body, non-dairy. Artisan sorbet dose **~4–4.5%** (vs 6–7% industrial).
- **Dextrose** raises solids *and* softness (high PAC) when you want both.

### Lemon juice / acid
Add **~1–3% lemon juice cold (≈4 °C) after pasteurisation** — its acid weakens stabiliser if heated with it. Brightens flavour, mildly antibacterial, offsets sweet/flat low-acid fruits (banana, melon, pear). For **lemon sorbet the juice IS the fruit** — count its sugar/acid. Very acidic fruits read ~0.5–2 °Bx above their true sugar.

### Step-by-step method
1. Pick fruit; measure its Brix (≈ % sugar) and TS (refractometer or §7 table).
2. Choose fruit % by intensity/acidity (§7). Lock it in.
3. Fruit sugar contribution = fruit% × fruit Brix.
4. Set total sugar target ~26–28%. **Added sugar = target − fruit sugar.**
5. Split added sugar to hit POD and PAC: start ~70–80% sucrose + ~20–30% dextrose; add glucose syrup/atomized glucose for body. Raise dextrose to soften (PAC↑) without sweetening; cap fructose/invert.
6. Check TS (30–33%). Low → add maltodextrin or inulin (~2–4%). High → cut bulking/sugar.
7. Stabiliser 0.2–0.5% (pre-mixed with sugar); pasteurise if needed; cool; **age 4–12 h cold**.
8. Add lemon/acid cold (~1–3%).
9. Verify PAC (pro 30–36; predicted serve ≈ PAC÷2.5). Re-split sugar if off.
10. Churn, harden, serve −12 to −14 °C.

### Worked example — lemon sorbetto (icecreamcalc, verified)
Water 500 · lemon juice 200 (~20%) · sucrose 200 · dextrose 90 · inulin 12 · LBG 2 (≈1004 g) → **TS 31.5%, sugars 28.8%, water 68.5%, POD 269.1, PAC 383.3 (per-1000 g; "normalized" 559.9), freezing point −3.6 °C** → ≈ **pro PAC ~33–38**. Heavy dextrose (softness for very low fruit %) + inulin (solids/body without sweetening) = textbook citrus sorbet construction.

---

## 7. Fruit composition for sorbetto

Brix (1 °Bx ≈ 1 g sugar+soluble-solids/100 g) lets a balancer subtract fruit sugar from the added-sugar requirement; recommended fruit % bounds the fruit slider. Tolerance on any Brix ≈ **±2 °Bx** (ripeness/variety).

**Two fruit-% scales — don't confuse them.** Ponthier publishes *purée %* (actual weight fraction of fruit in the finished mix — the operative number for a home balancer); the Italian artisan/Caviezel school quotes lower *fruit-pulp %* because it counts only pulp against a separately-built sugar/water base. Both are bookkeeping conventions, not a disagreement about taste — both columns are given so the range brackets reality.

**Brix basis:** the SS column is FruitSmart/Greenwood "Single Strength Brix Values" (cite 21 CFR). This differs from the **19 CFR §151.91 customs table** (which lists higher values for several fruits) — do not cross-correct the two. For a **home balancer using fresh fruit, use the single-strength / unsweetened-purée figure**; the higher "purée" Brix figures come from sweetened commercial purées.

| Fruit | Brix SS (°Bx) | Water % | Acidity | Ponthier purée % | Artisan pulp % | Raw/cooked |
|---|---|---|---|---|---|---|
| Strawberry | 8.0 (≈8–9 unsweetened) | ~91–92 | Med (pH 3.3–3.5) | 72.5 | 40–45 | Raw |
| Raspberry | 9.2 red / 11.1 black | ~86–87 | Med-high | 78 | 35–45 | Raw; sieve seeds |
| Blackberry | 10.0 | ~88 | Med | 72.5 | 35–45 | Raw; sieve |
| Lemon (juice) | 4.5 | ~89–92 | **High** (pH 2.2–2.6) | 35 | 25–30 | Raw juice + zest |
| Orange | 11.8 | ~87 | Med | 70 | 50–60 | Raw juice |
| Mango | 13.0 (cultivar 17–23.5) | ~83–86 | Low-med | 74–80 | 40–50 | Raw |
| Peach | 10.5 | ~88–89 | Low-med | 76.5 | 45–55 | Raw or lightly blanched |
| Apricot | 11.7 | ~86 | Med | 67 | 40–50 | Often lightly poached |
| Banana | 22.0 | ~74–81 | **Low** (pH 4.5–5.2) | 78 | 25–35 | Raw + lemon |
| Pineapple | 12.8 | ~86–87 | Med | 78 | 45–55 | Raw |
| Melon | 9.6 | ~90 | **Low** (pH 6.1–6.6) | 70 | 50–60 | Raw |
| Pear | 12.0 | ~84 | Low | 75.5 | 45–55 | Raw + lemon or poached |
| Fig | 18.2 | ~79–80 | Low | 78 | 40–50 | Raw, skin-on |
| Passion fruit | 14.0 | ~73 | **High** (pH 2.8–3.3) | 78 sweetened / ~35 raw pulp | 20–30 | Raw; sieve seeds |
| Kiwi | 15.4 | ~83–84 | Med-high | 65 | 40–50 | Raw; never cook; sieve |
| Blackcurrant | 11.0 | ~82 | **High** (pH 2.7–3.2) | 67 | 25–35 | Raw purée |

### Acidity → inclusion logic
- **High acid → LOW inclusion** (~25–35% pulp; may need extra sugar): lemon, lime, passion fruit, blackcurrant, redcurrant, sour cherry, kiwi.
- **Medium acid → mid:** strawberry, raspberry, blackberry, apricot, pineapple, orange, mango (~40–55% pulp / 65–78% purée).
- **Low acid / mild-sweet → HIGH inclusion** (need lots of fruit for flavour): peach, pear, melon, fig, banana (up to 55–60% pulp / 70–78% purée).

### Processing
- **Raw (purée/juice), most fruit;** sieve berries + passion fruit.
- **Add lemon to prevent browning:** banana, pear, peach, apricot.
- **Light cooking/poaching helps** (softens, de-skins, cuts astringency; re-measure Brix after — cooking concentrates it): apricot, peach, pear, sometimes fig.
- **Never cook kiwi** (muddy off-flavour); avoid heating raw pineapple/kiwi with dairy/egg (proteases).

---

## 8. Worked reference recipes (~1000 g batches)

Computed values marked *(calc)*; source-reported marked *(source)*. PAC mix-totals below are on the **per-1000 g summed** scale unless noted; divide by ~10 for an approximate pro-scale figure (see §0).

### White base — three triangulated versions
**1a. Dream Scoops (no milk powder):** whole milk 402, cream 32% 86, sucrose 48, dextrose 48, LBG 3 → fat **7.1%**, MSNF **7.1%**, sugar **16.4%**, TS **31.0%** *(calc)*.
**1b. alcremista/Caviezel:** whole milk 350, cream 35% 120, sucrose 110 → fat **9.4%** *(source)*, sugar **19%** *(source)*, water **65%** *(source)*, TS **35.0%**, MSNF **6.7%** *(calc)*.
**1c. Professional consensus (Messina-style):** fat 6–8%, MSNF 9–11%, sugar 16–18%, TS 35–38% (milk + cream + SMP + sucrose + dextrose + stabiliser, no eggs).
> **Safe auto-balance white-base target: fat 7–8%, MSNF 9–11%, sugar 17–18%, TS 35–37%.**

### Pistachio — two versions
**2a. Matt Adlard (no cream, fat from nuts):** milk 670, SMP 50, sugar 145, dextrose 50, 100% pistachio paste 100, LBG 2 → fat **7.7%**, MSNF **10.7%**, sugar **19.2%**, TS **42.0%**, paste ~10% *(calc)*.
**2b. cucina.li (yolk + cream):** milk 440, cream 35% 55, sucrose 90, dextrose 35, SMP 15, yolk 20, pistachio paste 56, salt 1.5, LBG 2.8 → fat **10.1%**, MSNF **8.0%**, sugar **17.5%**, TS **40.0%**, paste ~7.8% *(calc)*.
> 100% pure pistachio paste dosage 80–120 g/kg (8–12%). **Target: fat 8–10%, MSNF 8–11%, sugar 17–19%, TS 40–42%, paste 8–10%.**

### Dark chocolate (icecreamcalc)
Cocoa-cream pre-mix (make 1000 g, use 200 g): water 400, sucrose 150, dextrose 150, 21%-fat cacao 300. Gelato per 1000 g: milk 3% 501.6, cream 40% 100.8, SMP 38.4, sucrose 106.4, glucose syrup 28.8, dextrose 20, stabiliser 4, cocoa cream 200 → butterfat **5.6%**, total fat **6.8%**, MSNF **8.6%**, TS **41.2%**, POD **191.6**, freezing point **−3.5 °C** *(source)*; **total sugar ≈ 21%** *(calc; defensibly 20–22%)*. MSNF and serving-temp checks deliberately relaxed because cocoa solids replace some milk solids; the high sugar offsets cocoa bitterness.
> **Target: total fat 6–9%, sugar ~20–23%, TS 40–43%; relax MSNF/PAC checks vs white base.**

### Lemon sorbetto (icecreamcalc) — see §6 worked example
TS 31.5%, sugar 28.8%, water 68.5%, POD 269.1, PAC 383.3 (per-1000 g) ≈ pro PAC ~33–38, FP −3.6 °C.

### Strawberry sorbetto — two versions
**5a. iceicedaddy (60% fruit, sweeter):** strawberries 600, lemon juice 30, water 130, sucrose 120, dextrose 60, invert 40, glucose 38 DE 15, stabiliser 5 → fruit **60%**, sugar **~28%**, TS **~30%** *(calc, strawberry ~7 °Bx)*.
**5b. Underbelly (specialty-sugar, low POD high PAC):** lots of strawberries + little water + dextrose/dried glucose/trehalose/some sucrose + stabiliser cocktail + inulin + salt + lemon → fat 0%, TS **24.7%**, POD **144/1000 g** (≈14% sucrose-eq, deliberately low), PAC **318/1000 g** (absolute 438), serve −12 to −14 °C (~74% ice at −14 °C) *(source)*.
> The pair brackets the design range: iceicedaddy sweeter/sucrose-forward; Underbelly drives PAC up but POD down (dextrose/trehalose/glucose syrup) to stay scoopable without being cloying. Corvitto syrup-base school: finished sorbet ~24% POD + PAC ≈ 270/1000 g (≈ pro PAC 30–34).

### Auto-balancer target summary
| Type | Fat % | MSNF % | Sugar % | TS % | PAC (pro) | PAC (/1000 g summed) | POD (/1000 g) |
|---|---|---|---|---|---|---|---|
| Milk gelato / white base | 6–12 (~7–9) | 9–12 | 16–22 | 36–42 (icecreamcalc 35–40) | **24–28** | ~250–290 | 165–185 |
| Sorbet (fruit) | 0 | 0 | 24–30 | 30–33 (Underbelly low 24.7) | **30–36** | 270–440 | 140–270 |
| Dark chocolate | 6–9 | 8–9 (relaxed) | ~20–23 | 40–43 | (relaxed) | — | ~190 |
