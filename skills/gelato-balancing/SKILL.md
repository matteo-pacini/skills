---
name: gelato-balancing
description: >
  Balance and formulate authentic Italian gelato, fruit sorbetto/sorbet, and dairy-free
  (vegan) frozen desserts at home using the professional formula — total solids, sugars,
  fat, milk solids (MSNF), stabilisers, and the PAC (anti-freeze) / POD (sweetness) sugar
  balance. Use this skill whenever the user wants to MAKE, design, scale, fix, or
  scientifically balance any churned frozen dessert — gelato, sorbetto, sorbet, frozen
  yogurt, a "gelato/white base" — EVEN WHEN they only name a FLAVOUR or a MACHINE and
  never say the word "gelato". Triggers include: "how do I make pistachio gelato", "fior
  di latte recipe", "stracciatella", "vegan chocolate gelato", "a good hazelnut recipe
  for my ice cream maker", "recipe for my Ninja Creami / Cuisinart / ice cream machine",
  "balance a lemon sorbet", "lighter / lower-calorie / diet coffee gelato", "why is my
  sorbet/gelato icy / too hard / too sweet — fix the recipe", "convert this ice cream
  recipe to proper gelato", "scale this gelato to 1.5 litres", "make it less sweet / I
  don't have dextrose". Covers a supermarket-simple
  ingredient path (sucrose, milk, cream, skim milk powder, egg) and an advanced path
  (dextrose, glucose syrup, invert, inulin, stabiliser blends), and scaling to any batch
  or machine size. Do NOT use only when the user explicitly wants high-fat American/French
  custard-style ice cream and rejects gelato, or for non-frozen desserts (granita and
  semifreddo are different products — steer a sorbetto answer for granita).
---

# Italian gelato & sorbetto balancing

Balance a recipe to the professional Italian targets, then present it with the full
math shown. The numbers are not arbitrary — getting solids, sugars, fat, MSNF and the
PAC/POD sugar balance into range is what makes gelato smooth and scoopable instead of
icy, rock-hard, soupy, or sandy. Don't guess the arithmetic: **`scripts/balance.sh`
computes every metric and validates it.** Run it, iterate, then explain.

## Workflow

1. **Identify the product and flavour.** Fruit flavours default to **sorbetto** (no
   dairy); milk, nut, chocolate, coffee, caramel etc. are **cream gelato** (`type:
   gelato`). Dairy-free / vegan requests use `type: vegan` (procedure C — no MSNF, fat
   from plant cream/coconut, body from added solids). "Lighter / lower-calorie / diet"
   requests use `type: light` (procedure D — cut fat, swap sugar for maltitol/inulin; the
   calculator validates an `Energy kcal/100g` ceiling). If unclear, ask one short question;
   otherwise proceed with the sensible default. **If the user names a machine** (Ninja
   Creami, Cuisinart, no-machine/still-freeze), read `references/equipment.md` and apply
   its target nudges and batch size — the default bands assume a batch freezer, and a
   Ninja Creami in particular wants the *opposite* PAC end. **If they're fixing a defect**
   ("why is it icy/hard/gummy"), use `references/troubleshooting.md`.

2. **Pick the ingredient tier** (this is the user's choice — honor explicit cues):
   - **Supermarket-simple** if they say "simple", "supermarket", "what I have at home",
     "no special ingredients", or list only basics → sucrose, milk, cream, skim milk
     powder, eggs, lemon; stabilise with egg yolk or a pinch of guar, or skip it.
   - **Advanced** if they ask for "best/authentic/proper", name specialty sugars or
     stabilisers, or want gelateria quality → adds dextrose, glucose syrup, invert,
     inulin, and an LBG:guar stabiliser blend for independent control of sweetness,
     softness and body.
   - **If unspecified, default to Advanced** (it balances best) and append a short
     "Supermarket-simple version" so the user can choose. See the tier table in
     `references/ingredients.md`.

3. **Read the method.** Open `references/method.md` and follow procedure **A (cream
   gelato)** or **B (sorbetto)**. Pull ingredient composition from
   `references/ingredients.md` (dairy, sugars, stabilisers) and, for sorbetto, fruit
   Brix and inclusion % from `references/fruit.md`. Start from the nearest recipe in
   `references/worked-examples.md` rather than from zero. For **lean or low-Brix fruit**
   (lemon, lime, passion fruit, blackcurrant), put a non-sweetening bulking agent —
   **maltodextrin or inulin** — into the *primary* sorbetto recipe, not as an
   afterthought: it lifts total solids to mid-band so you don't have to max out sugar
   (which reads too sweet) just to clear the 30% solids floor.

4. **Build a recipe JSON and run the calculator.** Default batch 1000 g (state it). To
   scale, set `batch_g` and the calculator rescales every ingredient to hit it (or just
   multiply all grams). For a volume request, convert at ~1.07 g/mL (1.5 L ≈ 1600 g) and
   size to the machine (a Ninja Creami pint holds ~700 g). Use built-in names so
   composition is exact:

   ```bash
   scripts/balance.sh recipe.json        # or:  echo '<json>' | scripts/balance.sh -
   ```

   ```json
   {
     "type": "gelato",
     "ingredients": [
       {"name": "whole_milk", "g": 641}, {"name": "cream35", "g": 120},
       {"name": "smp", "g": 56}, {"name": "sucrose", "g": 135},
       {"name": "dextrose", "g": 45}, {"name": "lbg", "g": 3}
     ]
   }
   ```

   The library covers dairy, sugars, stabilisers, fruit, **flavour pastes** (cocoa,
   chocolate, pistachio_paste, hazelnut_paste, coffee_instant, matcha), **plant-based**
   (oat/soy/almond milk, coconut cream), and **alcohol/salt** (PAC-only). Common-name
   aliases resolve (caster_sugar, double_cream, glucose_powder…). For anything not built
   in, give composition inline as fractions, e.g.
   `{"name": "speculoos paste", "g": 60, "fat": 0.30, "sugars": {"sucrose": 0.45}, "other": 0.20}`.
   `references/ingredients.md` lists every built-in name and how to estimate composition.

5. **Iterate to BALANCED.** The calculator prints each metric with PASS / CHECK / FAIL
   and a plain-English texture read. For each out-of-range metric apply the single-lever
   fix from the iteration loop in `references/method.md` (e.g. icy/too-hard → swap some
   sucrose for dextrose at 1.4 : 1; too sweet but soft enough → shift toward maltodextrin
   or low-DE syrup) and re-run until it reports **BALANCED**. Because each sugar has a
   different POD:PAC ratio, sweetness and softness are near-independent dials — solve
   both together when both are off.

6. **Present the result** (see output format below).

## Flavour adjustments (rebalance by compensation)

When a flavour adds its own solids, subtract milk powder / sugar / cream to keep total
solids and the other targets in range:
- **Nut pastes** (pistachio, hazelnut): 8–12% of mix; they add fat + "other solids", so
  cut cream — nut gelato legitimately runs to the rich end of fat (~9–10%).
- **Cocoa / dark chocolate**: cocoa adds fat and other solids; run sugar higher (~19–22%)
  to offset bitterness and accept MSNF at the relaxed lower bound (~8–9%).
- **Fruit in a cream gelato**: counts as sugar + water + a little "other"; reduce added
  sugar accordingly.

## Output format

Show the **full math** — the user chose to see how the recipe is balanced, so don't hide
it. Structure the answer as:

1. **Recipe** — an ingredient table in grams for the stated batch size, with the
   stabiliser and any specialty sugars clearly listed. If you defaulted to Advanced, add
   a compact **Supermarket-simple version** underneath — run it through the calculator
   too and show its own metrics line, so both recipes are equally transparent (don't
   leave the fallback as unverified prose).
2. **The balance** — present the calculator's breakdown: the per-ingredient
   fat/MSNF/sugar/water contributions and the metrics table (total solids, sugars, fat,
   MSNF, stabiliser, PAC/1000 g, POD, water) each against its target. Then explain in a
   sentence or two *why* the key levers were chosen — what the dextrose/sugar split,
   MSNF and stabiliser are each doing for texture. Reference the PAC scale honestly: the
   per-1000 g summed figure is what's validated; the per-100 g-water figure is context.
3. **Method** — concise steps: combine and (if the blend needs it) heat to ~80 °C to
   pasteurise and hydrate the stabiliser (or the no-cook path — see `references/method.md`
   "Heating & pasteurisation"); cool and **age 4–12 h cold**; churn; harden; **serve at
   −12 to −14 °C** (temper a home-freezer tub 10–15 min). Add lemon/acid cold for sorbetto.
4. **Yield & keeping** — one line: total grams, approximate churned volume (gelato gains
   ~25–35% from overrun; less in a Creami), and that it keeps best a few days to ~2 weeks
   (store airtight, surface covered; texture coarsens with freeze-thaw).

**Practical notes worth surfacing:** the gum doses are tiny (tenths of a percent) — if
the user has no 0.01 g scale, steer them to the egg-yolk or no-stabiliser supermarket
version (and temper) rather than guessing a pinch. For "make it less sweet / no
dextrose / softer / double it" follow-ups, re-run the calculator with the single-lever
fix from `references/method.md` rather than eyeballing.

Keep claims grounded. Where the science is genuinely uncertain (exact PAC of some sugars,
honey composition, fruit Brix ±2), say so rather than inventing precision —
`references/science.md` documents the live disagreements if the user wants the depth.

## Running the calculator anywhere

`scripts/balance.sh` finds a Python interpreter automatically. If `python3` isn't on
PATH but the machine has **Nix** (NixOS, or macOS/Linux with the Nix package manager),
it transparently runs `nix-shell -p python3` to pull one — no install needed. The
calculator is pure-stdlib Python, so nothing else is required. If neither Python nor Nix
is available it prints how to get one. Pass `--json` (e.g.
`scripts/balance.sh recipe.json --json`) for machine-readable output instead of the
text table. The calculator flags an in-band metric as `PASS(edge)` when it sits within
5% of a band limit, and adds a `review:` note for any `CHECK` or edge results — surface
those to the user rather than calling a fragile balance "perfect."
