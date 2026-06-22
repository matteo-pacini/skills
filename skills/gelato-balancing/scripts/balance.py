#!/usr/bin/env python3
"""Balance an Italian gelato or sorbetto recipe and show the full math.

Reads a recipe JSON (file path argument, or '-' for stdin) and prints a complete
composition breakdown: fat / MSNF / sugars / other solids / stabiliser / total
solids / water, plus POD (sweetness) and PAC (anti-freezing power), and validates
every metric against the target band for the chosen product.

All per-sugar POD/PAC coefficients are on the sucrose = 100 scale. The coefficient
and ingredient tables mirror references/ingredients.md (single source of truth);
update both together. Stdlib only — no third-party packages.

Recipe JSON:
{
  "type": "gelato" | "sorbetto",
  "batch_g": 1000,                      # optional; defaults to the sum of ingredient grams
  "ingredients": [
    {"name": "whole_milk", "g": 590},   # known names pull composition from the built-in library
    {"name": "sucrose",    "g": 130},
    {"name": "my paste",   "g": 60, "fat": 0.50, "other": 0.45},   # inline composition for anything
    {"name": "strawberry", "g": 600}    # fruit: sugar derived from Brix
  ]
}

Any built-in field can be overridden inline. Composition fields are FRACTIONS of the
ingredient's own mass (0..1): fat, msnf, other, stab, water, brix, and sugars{...}.
Lactose is derived automatically from MSNF (0.545 x MSNF) — never list it yourself.
"""

import json
import sys

# --- Per-sugar coefficients on sucrose = 100: (POD sweetness, PAC anti-freeze) ---
# Anhydrous-molecule values; ingredient "purity"/water is handled by the sugar
# FRACTION in each ingredient (e.g. dextrose monohydrate carries ~0.92 dextrose).
# Where sources genuinely disagree, the representative value is used here and the
# range is documented in references/ingredients.md. Flagged values are approximate.
SUGARS = {
    "sucrose":      (100, 100),
    "dextrose":     (70, 190),
    "fructose":     (173, 190),
    "invert":       (125, 190),   # alt school: ~98 / ~152
    "lactose":      (16, 100),
    "glucose_de38": (24, 45),     # low-DE syrup / atomized glucose
    "glucose_de42": (52, 90),
    "glucose_de60": (60, 110),    # interpolated — no published figure
    "maltodextrin": (10, 34),
    "trehalose":    (45, 100),
    "inulin":       (10, 15),
    "sorbitol":     (60, 188),
    "maltitol":     (85, 99),
    "erythritol":   (75, 280),    # anomalous: high theoretical PAC but firms >~8%
    "glycerol":     (60, 372),
    "fruitsugar":   (118, 172),   # default fruit sugar mix (~40% glucose/40% fructose/20% sucrose)
}
# Honey is modelled as its fructose/glucose/sucrose components in LIBRARY (more accurate
# than a single coefficient); there is intentionally no "honey" key here.

# Non-sugar freezing-point depressants on the SAME sucrose=100 PAC scale (POD ~0).
# Handled separately from sugars: salt is a solid; alcohol is volatile/non-solid. Both
# have very high PAC per gram, so a little goes a long way — see references/science.md.
PAC_ONLY = {"salt": 585, "alcohol": 740}

# Energy (Atwater, kcal/g). Per sugar/bulk component — polyols and fibre are the
# calorie levers: erythritol ~0, maltitol/sorbitol ~2, inulin ~1.5 vs sugar's 4.
ENERGY = {
    "sucrose": 4, "dextrose": 4, "fructose": 4, "invert": 4, "lactose": 4, "honey": 4,
    "glucose_de38": 4, "glucose_de42": 4, "glucose_de60": 4, "maltodextrin": 4,
    "trehalose": 4, "fruitsugar": 4,
    "inulin": 1.5, "sorbitol": 2.6, "maltitol": 2.1, "erythritol": 0.2, "glycerol": 4.3,
}
ENERGY_COMP = {"fat": 9, "msnf": 3.6, "other": 4, "stab": 2, "alcohol": 7, "salt": 0}

# --- Built-in ingredient library. Fields are fractions of the ingredient mass. ---
# "sugars" maps a SUGARS key to its fraction of the ingredient. Dairy MSNF carries
# its lactose implicitly (handled in the math); do not also list lactose here.
LIBRARY = {
    # dairy & fat (serum-point MSNF where no sheet) ----------------------------
    "whole_milk":     {"fat": 0.036, "msnf": 0.087},
    "semiskim_milk":  {"fat": 0.016, "msnf": 0.089},
    "skim_milk":      {"fat": 0.001, "msnf": 0.090},
    "cream25":        {"fat": 0.25,  "msnf": 0.0675},
    "cream35":        {"fat": 0.35,  "msnf": 0.0585},
    "cream38":        {"fat": 0.38,  "msnf": 0.0558},
    "butter":         {"fat": 0.82,  "msnf": 0.01},
    "smp":            {"fat": 0.01,  "msnf": 0.96},   # skim milk powder / NFDM
    "wmp":            {"fat": 0.27,  "msnf": 0.708},  # whole milk powder
    "condensed_milk": {"fat": 0.085, "msnf": 0.21, "sugars": {"sucrose": 0.44}},
    "evap_milk":      {"fat": 0.078, "msnf": 0.18},
    "mascarpone":     {"fat": 0.44,  "msnf": 0.04},
    "egg_yolk":       {"fat": 0.27,  "other": 0.20},  # yolk solids are fat+other, never MSNF
    # sugars ------------------------------------------------------------------
    "sucrose":          {"sugars": {"sucrose": 1.0}},
    "dextrose":         {"sugars": {"dextrose": 0.92}},   # monohydrate, as sold
    "fructose":         {"sugars": {"fructose": 1.0}},
    "invert":           {"sugars": {"invert": 0.75}},
    "glucose_syrup":    {"sugars": {"glucose_de42": 0.80}},
    "atomized_glucose": {"sugars": {"glucose_de38": 0.95}},
    "maltodextrin":     {"bulk": {"maltodextrin": 0.95}},   # body, not sugar%
    "trehalose":        {"sugars": {"trehalose": 1.0}},
    "inulin":           {"bulk": {"inulin": 0.95}},          # fibre bulking, not sugar%
    "honey":            {"sugars": {"fructose": 0.41, "dextrose": 0.37, "sucrose": 0.03}},  # ~81% solids
    # polyols / sugar alcohols (reduced-calorie sweeteners — see ENERGY) ---------
    "erythritol": {"sugars": {"erythritol": 1.0}},   # ~0 kcal; firms >~8%, cooling
    "maltitol":   {"sugars": {"maltitol": 1.0}},     # ~2.1 kcal; PAC ~sucrose
    "sorbitol":   {"sugars": {"sorbitol": 1.0}},     # ~2.6 kcal; strong anti-freeze/humectant
    "glycerol":   {"sugars": {"glycerol": 1.0}},     # ~4.3 kcal; trace softener only
    # common-name sugars/syrups (distinct splits, not just aliases) ------------
    "brown_sugar":  {"sugars": {"sucrose": 0.97}, "other": 0.02},
    "maple_syrup":  {"sugars": {"sucrose": 0.60}, "water": 0.33},          # ~66 Bx, mostly sucrose
    "agave_syrup":  {"sugars": {"fructose": 0.56, "dextrose": 0.20}, "water": 0.22},  # fructose-dominant
    "golden_syrup": {"sugars": {"sucrose": 0.28, "dextrose": 0.22, "fructose": 0.22}, "water": 0.20},
    # stabilisers (pure powders) ----------------------------------------------
    "lbg": {"stab": 1.0}, "guar": {"stab": 1.0}, "tara": {"stab": 1.0},
    "carrageenan": {"stab": 1.0}, "cmc": {"stab": 1.0}, "pectin": {"stab": 1.0},
    "xanthan": {"stab": 1.0}, "stabiliser": {"stab": 1.0}, "neutro": {"stab": 1.0},
    # flavour pastes & solids (fat + other; NEVER msnf — like egg_yolk) --------
    "cocoa_powder":    {"fat": 0.11, "other": 0.84},   # natural/Dutch 10-12% fat
    "cocoa_powder_22": {"fat": 0.22, "other": 0.73},   # "high-fat" cocoa
    "cocoa_mass":      {"fat": 0.53, "other": 0.46},   # 100% chocolate / cacao liquor
    "cocoa_butter":    {"fat": 1.0},
    "dark_chocolate":  {"fat": 0.40, "other": 0.18, "sugars": {"sucrose": 0.42}},  # ~70% couverture
    "milk_chocolate":  {"fat": 0.34, "msnf": 0.18, "sugars": {"sucrose": 0.48}},   # has milk solids
    "pistachio_paste": {"fat": 0.55, "other": 0.43},
    "hazelnut_paste":  {"fat": 0.62, "other": 0.36},
    "almond_paste":    {"fat": 0.53, "other": 0.45},
    "peanut_butter":   {"fat": 0.50, "other": 0.43, "sugars": {"sucrose": 0.05}},
    "coffee_instant":  {"other": 0.97},                # freeze-dried
    "matcha":          {"other": 0.95},
    # cultured & plant-based (plant 'milks' carry NO msnf) --------------------
    "greek_yogurt":  {"fat": 0.05,  "msnf": 0.085},    # ~10% full-fat strained
    "yogurt":        {"fat": 0.035, "msnf": 0.085},    # plain whole-milk
    "creme_fraiche": {"fat": 0.30,  "msnf": 0.045},
    "coconut_milk":  {"fat": 0.20,  "other": 0.03},    # canned full-fat
    "coconut_cream": {"fat": 0.34,  "other": 0.04},
    "oat_milk":      {"other": 0.04, "sugars": {"maltodextrin": 0.04, "dextrose": 0.02}},
    "soy_milk":      {"fat": 0.018, "other": 0.04, "sugars": {"sucrose": 0.025}},
    "almond_milk":   {"fat": 0.011, "other": 0.015, "sugars": {"sucrose": 0.02}},
    "plant_cream":   {"fat": 0.17,  "other": 0.03},    # generic oat/soy whipping cream
    # alcohol & salt (PAC only — see PAC_ONLY; ABV by volume ~= 0.79 x by weight) --
    "salt":       {"salt": 1.0},
    "ethanol":    {"alcohol": 1.0},
    "rum":        {"alcohol": 0.33, "water": 0.67},    # ~40% ABV
    "vodka":      {"alcohol": 0.33, "water": 0.67},
    "limoncello": {"alcohol": 0.25, "sugars": {"sucrose": 0.25}, "water": 0.50},
    # fruit (single-strength Brix as sugar fraction; ~1% fibre as other) -------
    "lemon":        {"brix": 0.045, "other": 0.005},
    "lime":         {"brix": 0.045, "other": 0.005},
    "strawberry":   {"brix": 0.080, "other": 0.010},
    "watermelon":   {"brix": 0.075, "other": 0.005},
    "melon":        {"brix": 0.096, "other": 0.008},
    "raspberry":    {"brix": 0.092, "other": 0.015},
    "redcurrant":   {"brix": 0.090, "other": 0.015},
    "blackberry":   {"brix": 0.100, "other": 0.012},
    "blueberry":    {"brix": 0.120, "other": 0.012},
    "peach":        {"brix": 0.105, "other": 0.010},
    "blackcurrant": {"brix": 0.110, "other": 0.015},
    "apricot":      {"brix": 0.117, "other": 0.012},
    "orange":       {"brix": 0.118, "other": 0.008},
    "pear":         {"brix": 0.120, "other": 0.012},
    "apple":        {"brix": 0.130, "other": 0.012},
    "pineapple":    {"brix": 0.128, "other": 0.012},
    "mango":        {"brix": 0.130, "other": 0.012},
    "cherry":       {"brix": 0.140, "other": 0.012},
    "sour_cherry":  {"brix": 0.120, "other": 0.014},
    "passionfruit": {"brix": 0.140, "other": 0.020},
    "pomegranate":  {"brix": 0.150, "other": 0.010},
    "grape":        {"brix": 0.170, "other": 0.008},
    "kiwi":         {"brix": 0.154, "other": 0.015},
    "fig":          {"brix": 0.182, "other": 0.015},
    "banana":       {"brix": 0.220, "other": 0.020},
    "water":        {},
}

# Spoken-name -> canonical key. Resolved before LIBRARY lookup so users need not know
# the canonical names. Note: UK "double cream" (~48% fat) maps to cream38 as the nearest
# built-in — enter fat inline for precision.
ALIASES = {
    "caster_sugar": "sucrose", "granulated_sugar": "sucrose", "caster": "sucrose",
    "table_sugar": "sucrose", "white_sugar": "sucrose", "icing_sugar": "sucrose",
    "powdered_sugar": "sucrose", "confectioners_sugar": "sucrose",
    "corn_syrup": "glucose_syrup", "glucose_powder": "dextrose", "glucose": "dextrose",
    "milk": "whole_milk", "cream": "cream35", "heavy_cream": "cream35",
    "whipping_cream": "cream35", "double_cream": "cream38",
    "skimmed_milk_powder": "smp", "nonfat_dry_milk": "smp", "milk_powder": "smp",
    "cocoa": "cocoa_powder", "cacao": "cocoa_powder", "nocciola": "hazelnut_paste",
    "instant_coffee": "coffee_instant", "espresso_powder": "coffee_instant",
}

# --- Target bands per product: (low_ok, high_ok). Outside warn band -> CHECK. ---
# PAC is validated on the per-1000 g SUMMED scale: it is well-defined and matches
# the worked reference recipes. The per-100 g-water ("pro") figure is reported for
# context only — the two scales do NOT reconcile by a fixed factor (the ratio moves
# with each mix's water content), so we never validate against a converted band.
TARGETS = {
    "gelato": {
        "Total solids %": (36, 42),
        "Total sugars %": (16, 22),
        "Fat %":          (6, 9),    # 9-12 acceptable for cream styles -> CHECK
        "MSNF %":         (9, 12),
        "Stabiliser %":   (0.15, 0.5),
        "PAC /1000g":     (250, 290),
        "Lactose %H2O":   (0, 10.5),  # sandiness: PASS <=10.5% (~MSNF 12%); CHECK 10.5-12.5; FAIL >12.5
    },
    "sorbetto": {
        "Total solids %": (30, 33),
        "Total sugars %": (22, 30),
        "Fat %":          (0, 0),   # a little cocoa-butter/nut fat (chocolate/nut sorbet) -> CHECK
        "MSNF %":         (0, 0),
        "Stabiliser %":   (0.2, 0.5),
        "PAC /1000g":     (270, 440),  # working sweet spot ~320-380
    },
    # Dairy-free cream gelato: no MSNF, fat from plant cream/coconut/cocoa butter, body
    # from added "other solids" (plant protein, maltodextrin, inulin). Wider fat band
    # because plant fats vary; slightly higher stabiliser since there's no milk/egg
    # emulsifier. Same solids/sugar/PAC logic as dairy gelato.
    "vegan": {
        "Total solids %": (36, 42),
        "Total sugars %": (16, 22),
        "Fat %":          (5, 12),
        "MSNF %":         (0, 0),
        "Stabiliser %":   (0.2, 0.5),
        "PAC /1000g":     (250, 290),
    },
    # Reduced-calorie gelato: cut fat (9 kcal/g, the biggest lever), replace some sugar
    # with polyols/inulin (hold POD/PAC at fewer calories), lean on MSNF + stabiliser for
    # body, accept a lower solids floor. Energy is the headline validated metric here.
    "light": {
        "Total solids %":   (30, 40),
        "Total sugars %":   (10, 20),
        "Fat %":            (2, 7),
        "MSNF %":           (9, 12),
        "Stabiliser %":     (0.3, 0.5),
        "PAC /1000g":       (250, 290),
        "Lactose %H2O":     (0, 10.5),
        "Energy kcal/100g": (0, 160),
    },
}
# Informational sweetness band (not a FAIL — sweetness is a preference dial).
POD_BAND = {"gelato": (165, 185), "sorbetto": (140, 270), "vegan": (165, 185),
            "light": (150, 185)}
# Per-type CHECK ceilings: a metric above its band but at/under this reads CHECK, not FAIL.
WARN_CEIL = {
    "gelato":   {"Fat %": 12, "Lactose %H2O": 12.5},
    "sorbetto": {"Fat %": 4},     # chocolate/nut sorbet carries a little fat
    "vegan":    {"Fat %": 14},
    "light":    {"Fat %": 9, "Lactose %H2O": 12.5, "Energy kcal/100g": 180},
}


COMP_FIELDS = ("fat", "msnf", "other", "stab", "water", "brix", "sugars", "bulk",
               "salt", "alcohol")


def resolve(ing):
    """Merge a built-in library entry with inline overrides into a flat spec."""
    key = ing["name"].strip().lower().replace(" ", "_")
    key = ALIASES.get(key, key)
    known = key in LIBRARY
    if not known and not any(f in ing for f in COMP_FIELDS):
        sys.exit(f"ERROR: unknown ingredient '{ing['name']}'. Either use a built-in "
                 f"name or give its composition inline (e.g. \"fat\": 0.5, \"other\": 0.45, "
                 f"or \"sugars\": {{\"sucrose\": 1.0}}). See references/ingredients.md.")
    spec = dict(LIBRARY.get(key, {}))
    for k, v in ing.items():
        if k in ("name", "g"):
            continue
        if k in ("sugars", "bulk"):
            spec[k] = dict(v)   # full override of the sugar/bulk map
        else:
            spec[k] = v
    return spec


def _coeffs(name, spec, field):
    """Resolve a {coefficient_key: fraction} map (sugars or bulk) into grams."""
    out = {}
    for k, frac in spec.get(field, {}).items():
        if k not in SUGARS:
            sys.exit(f"ERROR: unknown {field} component '{k}' in ingredient '{name}'. "
                     f"Known: {', '.join(sorted(SUGARS))}")
        out[k] = out.get(k, 0.0) + spec["_g"] * frac
    return out


def contribution(name, g, spec):
    """Grams of fat / msnf / sugars / bulk / other / stab / salt / alcohol / water.

    `sugars` count toward the sugar% target AND carry POD/PAC. `bulk` (maltodextrin,
    inulin) are non-sweet body agents: they count as OTHER solids — NOT the sugar%
    target — but still carry their (low) POD/PAC. `salt` is a solid carrying huge PAC;
    `alcohol` is volatile/non-solid (stays in the liquid phase) carrying huge PAC. Both
    have POD ~0 and are handled on the separate PAC_ONLY scale."""
    spec = {**spec, "_g": g}
    fat = g * spec.get("fat", 0.0)
    msnf = g * spec.get("msnf", 0.0)
    other = g * spec.get("other", 0.0)
    stab = g * spec.get("stab", 0.0)
    salt = g * spec.get("salt", 0.0)        # solid
    alcohol = g * spec.get("alcohol", 0.0)  # non-solid (liquid phase)
    sugars = _coeffs(name, spec, "sugars")
    if not sugars and "brix" in spec:
        sugars["fruitsugar"] = g * spec["brix"]
    bulk = _coeffs(name, spec, "bulk")
    # salt counts as a solid (folded into 'other'); alcohol does not (falls into water).
    other += salt
    accounted = fat + msnf + other + stab + sum(sugars.values()) + sum(bulk.values())
    water = g * spec["water"] if "water" in spec else g - accounted - alcohol
    return fat, msnf, sugars, bulk, other, stab, salt, alcohol, water


def band(value, low, high, warn_high=None):
    """PASS / PASS(edge) / CHECK / FAIL. 'edge' = in-band but within 5% of the band
    width of a limit — a real pass, but with little tolerance for ingredient variation."""
    if low <= value <= high:
        margin = 0.05 * (high - low)
        near_low = low > 0 and (value - low) < margin   # skip low edge on a 0-floor ceiling
        if margin > 0 and (near_low or high - value < margin):
            return "PASS(edge)"
        return "PASS"
    if warn_high is not None and high < value <= warn_high:
        return "CHECK"
    return "FAIL"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    json_mode = "--json" in sys.argv[1:]
    if not args:
        sys.exit("usage: balance.py <recipe.json | -> [--json]")
    try:
        raw = sys.stdin.read() if args[0] == "-" else open(args[0]).read()
    except OSError as e:
        sys.exit(f"ERROR: cannot read recipe file '{args[0]}': {e}")
    try:
        recipe = json.loads(raw)
    except json.JSONDecodeError as e:
        sys.exit(f"ERROR: recipe is not valid JSON ({e}).")
    ptype = recipe.get("type", "gelato").lower()
    if ptype not in TARGETS:
        sys.exit(f"ERROR: type must be one of {', '.join(TARGETS)}, got '{ptype}'")
    ings = recipe.get("ingredients")
    if not isinstance(ings, list) or not ings:
        sys.exit("ERROR: recipe needs a non-empty 'ingredients' list.")
    for i in ings:
        if "name" not in i:
            sys.exit(f"ERROR: every ingredient needs a 'name' (offending entry: {i}).")
        if not isinstance(i.get("g"), (int, float)) or i["g"] < 0:
            sys.exit(f"ERROR: ingredient '{i.get('name')}' needs a non-negative numeric 'g'.")

    # batch_g is a SCALING TARGET, not a free water knob. If given and it disagrees with
    # the ingredient sum, scale every ingredient to hit it (what "scale to 700 g" means).
    sum_g = sum(i["g"] for i in ings)
    if sum_g <= 0:
        sys.exit("ERROR: ingredient weights sum to zero.")
    target = recipe.get("batch_g")
    scaled_note = None
    if target and abs(target - sum_g) > 0.5:
        factor = target / sum_g
        ings = [{**i, "g": i["g"] * factor} for i in ings]
        scaled_note = f"scaled x{factor:.4g} to reach batch_g={target:g} (from {sum_g:g} g)"
    batch = sum(i["g"] for i in ings)

    tot = {"fat": 0.0, "msnf": 0.0, "other": 0.0, "stab": 0.0, "water": 0.0}
    salt_g = alcohol_g = 0.0
    sugar_tot, bulk_tot = {}, {}
    rows = []
    for ing in ings:
        g = ing["g"]
        fat, msnf, sugars, bulk, other, stab, slt, alc, water = contribution(ing["name"], g, resolve(ing))
        tot["fat"] += fat; tot["msnf"] += msnf; tot["other"] += other
        tot["stab"] += stab; tot["water"] += water
        salt_g += slt; alcohol_g += alc
        for k, v in sugars.items():
            sugar_tot[k] = sugar_tot.get(k, 0.0) + v
        for k, v in bulk.items():
            bulk_tot[k] = bulk_tot.get(k, 0.0) + v
        rows.append((ing["name"], g, fat, msnf, sum(sugars.values()), other + sum(bulk.values()), stab, water))

    declared_sugar_g = sum(sugar_tot.values())           # counts toward sugar% target
    bulk_g = sum(bulk_tot.values())                       # body agents — count as OTHER solids
    other_g = tot["other"] + bulk_g                       # tot['other'] already includes salt
    lactose_g = 0.545 * tot["msnf"]                       # free lactose from MSNF
    solids_g = tot["fat"] + tot["msnf"] + declared_sugar_g + other_g + tot["stab"]
    water_g = batch - solids_g

    if water_g < -0.01:
        sys.exit(f"ERROR: IMPOSSIBLE recipe — solids ({solids_g:.0f} g) exceed the batch "
                 f"({batch:.0f} g), so water is negative ({water_g:.0f} g). Reduce solids "
                 f"or add liquid.")

    # POD / PAC. Sugars + bulk + lactose, plus salt/alcohol on the PAC_ONLY scale.
    pacpod = list(sugar_tot.items()) + list(bulk_tot.items())
    pod_raw = sum(v * SUGARS[k][0] for k, v in pacpod) + lactose_g * SUGARS["lactose"][0]
    pac_raw = (sum(v * SUGARS[k][1] for k, v in pacpod) + lactose_g * SUGARS["lactose"][1]
               + salt_g * PAC_ONLY["salt"] + alcohol_g * PAC_ONLY["alcohol"])
    scale = 1000.0 / batch
    pod_1000 = pod_raw / 100 * scale
    pac_1000 = pac_raw / 100 * scale                     # validated scale
    pac_pro = (pac_raw / 100) / water_g * 100 if water_g > 0 else float("nan")  # context only

    # Energy (Atwater). Lactose's energy is already inside MSNF's 3.6 kcal/g — don't add it.
    energy_kcal = (ENERGY_COMP["fat"] * tot["fat"] + ENERGY_COMP["msnf"] * tot["msnf"]
                   + ENERGY_COMP["other"] * (tot["other"] - salt_g) + ENERGY_COMP["stab"] * tot["stab"]
                   + ENERGY_COMP["alcohol"] * alcohol_g
                   + sum(g * ENERGY[k] for k, g in sugar_tot.items())
                   + sum(g * ENERGY[k] for k, g in bulk_tot.items()))
    kcal_100 = energy_kcal / batch * 100

    pct = lambda x: 100 * x / batch

    # --- compute verdicts (same for text and JSON modes) ---
    composition = {
        "Total solids %": pct(solids_g),
        "Total sugars %": pct(declared_sugar_g),
        "Fat %":          pct(tot["fat"]),
        "MSNF %":         pct(tot["msnf"]),
        "Stabiliser %":   pct(tot["stab"]),
        "PAC /1000g":     pac_1000,
        "Lactose %H2O":   (lactose_g / water_g * 100) if water_g > 0 else 0.0,
        "Energy kcal/100g": kcal_100,
    }
    warn_for = WARN_CEIL.get(ptype, {})
    metrics, fails, checks, edges = [], 0, [], []
    for metric, (lo, hi) in TARGETS[ptype].items():
        val = composition[metric]
        warn = warn_for.get(metric)
        verdict = band(val, lo, hi, warn_high=warn)
        if verdict == "FAIL":
            fails += 1
        elif verdict == "CHECK":
            checks.append(metric)
        elif verdict == "PASS(edge)":
            edges.append(metric)
        metrics.append((metric, val, lo, hi, verdict))

    pod_lo, pod_hi = POD_BAND[ptype]
    pod_note = "in range" if pod_lo <= pod_1000 <= pod_hi else \
        ("low — a touch under-sweet" if pod_1000 < pod_lo else "high — quite sweet")
    lo, hi = TARGETS[ptype]["PAC /1000g"]
    if pac_1000 < lo:
        soft = "FIRM/icy at -12 to -14C — raise PAC (swap some sucrose -> dextrose)"
    elif pac_1000 > hi:
        soft = "SOFT/slow to set at -12 to -14C — lower PAC (swap some dextrose -> sucrose)"
    else:
        soft = "scoopable at -12 to -14C cabinet temperature"

    if fails:
        status = f"NOT BALANCED — {fails} metric(s) FAIL"
    else:
        notes = []
        if checks:
            notes.append(f"{len(checks)} CHECK ({', '.join(checks)})")
        if edges:
            notes.append(f"{len(edges)} at band edge ({', '.join(edges)})")
        status = "BALANCED — all metrics in range" + (f"; review: {'; '.join(notes)}" if notes else "")

    # --- JSON mode: machine-readable, no text report ---
    if json_mode:
        out = {
            "type": ptype, "batch_g": round(batch, 2), "balanced": fails == 0,
            "status": status,
            "composition_pct": {
                "total_solids": round(pct(solids_g), 2), "total_sugars": round(pct(declared_sugar_g), 2),
                "fat": round(pct(tot["fat"]), 2), "msnf": round(pct(tot["msnf"]), 2),
                "other": round(pct(other_g), 2), "stabiliser": round(pct(tot["stab"]), 2),
                "water": round(pct(water_g), 2),
            },
            "bulk_g": {k: round(v, 1) for k, v in sorted(bulk_tot.items())},
            "pod_1000": round(pod_1000, 1), "pac_1000": round(pac_1000, 1),
            "kcal_per_100g": round(kcal_100, 0),
            "pac_per100g_water": (round(pac_pro, 1) if water_g > 0 else None), "lactose_g": round(lactose_g, 1),
            "sugar_split_g": {k: round(v, 1) for k, v in sorted(sugar_tot.items())},
            "texture_read": soft,
            "metrics": [
                {"name": m, "value": round(v, 2), "target_low": lo_, "target_high": hi_, "verdict": vd}
                for (m, v, lo_, hi_, vd) in metrics
            ],
            "fails": fails, "checks": checks, "edges": edges,
        }
        if scaled_note:
            out["scaled"] = scaled_note
        if salt_g or alcohol_g:
            out["pac_only_g"] = {"salt": round(salt_g, 1), "alcohol": round(alcohol_g, 1)}
        print(json.dumps(out, indent=2))
        return

    # --- text report ---
    P = print
    P(f"\n{'='*64}\n  {ptype.upper()} balance — batch {batch:.0f} g\n{'='*64}")
    if scaled_note:
        P(f"  NOTE: {scaled_note}")
    P(f"\n{'ingredient':<18}{'g':>7}{'fat':>8}{'msnf':>8}{'sugar':>8}{'other':>8}{'stab':>7}{'water':>8}")
    for name, g, fat, msnf, sug, other, stab, water in rows:
        P(f"{name:<18}{g:>7.1f}{fat:>8.1f}{msnf:>8.1f}{sug:>8.1f}{other:>8.1f}{stab:>7.2f}{water:>8.1f}")
    P("-" * 72)
    P(f"{'TOTAL g':<18}{batch:>7.1f}{tot['fat']:>8.1f}{tot['msnf']:>8.1f}"
      f"{declared_sugar_g:>8.1f}{other_g:>8.1f}{tot['stab']:>7.2f}{water_g:>8.1f}")

    split = ", ".join(f"{k} {g:.1f}g" for k, g in sorted(sugar_tot.items())) or "(none)"
    P(f"\nSugar split (declared): {split}")
    if bulk_tot:
        bsplit = ", ".join(f"{k} {g:.1f}g" for k, g in sorted(bulk_tot.items()))
        P(f"Bulk agents (in 'other', not sugar%): {bsplit}")
    if salt_g or alcohol_g:
        P(f"PAC-only (high anti-freeze, ~0 sweetness): "
          f"salt {salt_g:.1f}g (PAC 585), alcohol {alcohol_g:.1f}g (PAC 740)")
    P(f"Free lactose from MSNF: {lactose_g:.1f} g  (counts toward PAC/POD, not the sugar % target)")

    P(f"\n{'metric':<18}{'value':>10}   target        verdict")
    P("-" * 56)
    for metric, val, lo_, hi_, verdict in metrics:
        tgt = f"{lo_:g}-{hi_:g}" if hi_ != lo_ else f"{lo_:g}"
        P(f"{metric:<18}{val:>10.2f}   {tgt:<12}  {verdict}")
    P("-" * 56)
    P(f"{'Water %':<18}{pct(water_g):>10.2f}")
    P(f"{'POD /1000g':<18}{pod_1000:>10.1f}   (sweetness {pod_lo}-{pod_hi}; {pod_note})")
    if "Energy kcal/100g" not in TARGETS[ptype]:     # validated row already shows it for 'light'
        P(f"{'Energy kcal/100g':<18}{kcal_100:>10.0f}   (estimate; classic gelato ~170-220)")
    pac_pro_str = f"{pac_pro:>10.1f}" if water_g > 0 else f"{'n/a':>10}"
    P(f"{'PAC per-100g H2O':<18}{pac_pro_str}   (context only — not a fixed multiple of /1000g)")
    if ptype == "sorbetto":
        P(f"{'~Final Brix':<18}{pct(solids_g):>10.1f}   (~total solids; target ~30-31)")
    P(f"{'Texture read':<18}  {soft}")
    P(f"\n>>> {status}." +
      ("" if fails == 0 else " Adjust per references/method.md (single-lever fixes) and re-run.") + "\n")


if __name__ == "__main__":
    main()
