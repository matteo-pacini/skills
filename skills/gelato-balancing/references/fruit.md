# Fruit reference (for sorbetto)

Brix ≈ % sugar by weight. Subtract the fruit's sugar from the added-sugar requirement;
the inclusion range bounds how much fruit to use. For fresh fruit use the
**single-strength Brix** below (commercial sweetened purées read higher — don't mix
the two). Brix tolerance ≈ **±2 °Bx** with ripeness/variety; a refractometer beats the
table when you have one. `scripts/balance.py` carries these Brix values in its library.

| Fruit | Brix °Bx | Acidity | Inclusion % (pulp → purée) | Processing |
|---|---|---|---|---|
| Lemon (juice) | 4.5 | High | 25–35 | Raw juice + zest |
| Strawberry | 8.0 | Med | 40–45 (→72) | Raw |
| Melon | 9.6 | Low | 50–60 (→70) | Raw + lemon |
| Raspberry | 9.2 | Med-high | 35–45 (→78) | Raw; sieve seeds |
| Blackberry | 10.0 | Med | 35–45 | Raw; sieve |
| Peach | 10.5 | Low-med | 45–55 (→76) | Raw or lightly poached |
| Blackcurrant | 11.0 | High | 25–35 | Raw purée |
| Apricot | 11.7 | Med | 40–50 | Often lightly poached |
| Orange | 11.8 | Med | 50–60 | Raw juice |
| Pear | 12.0 | Low | 45–55 | Raw + lemon or poached |
| Pineapple | 12.8 | Med | 45–55 | Raw (don't heat with dairy) |
| Mango | 13.0 | Low-med | 40–50 (→74–80) | Raw |
| Passion fruit | 14.0 | High | 20–30 | Raw; sieve seeds |
| Kiwi | 15.4 | Med-high | 40–50 | Raw; **never cook** |
| Fig | 18.2 | Low | 40–50 | Raw, skin-on |
| Banana | 22.0 | Low | 25–35 | Raw + lemon |

## Acidity → inclusion logic
- **High acid → LOW inclusion** (~25–35%; often needs extra sugar): lemon, lime,
  passion fruit, blackcurrant, redcurrant, sour cherry, kiwi.
- **Medium acid → mid** (~40–55%): strawberry, raspberry, blackberry, apricot,
  pineapple, orange, mango.
- **Low-acid / mild → HIGH inclusion** (need lots of fruit for flavour, ~50–60%):
  peach, pear, melon, fig, banana — and add ~1–3% lemon juice to lift them.

## Sorbetto-specific notes
- **No fat, no MSNF**, so sugars carry both sweetness and texture → sorbetto runs
  higher sugar (22–30%) and higher PAC than dairy gelato. Corvitto's rule: aim ~+6%
  sweetness (POD) over the comparable gelato base.
- **Raise solids without sweetness** with maltodextrin or inulin (~2–4.5%) so a
  high-water, low-fruit sorbet (e.g. lemon) isn't thin and icy.
- **Add lemon/acid cold** (~1–3%, after any pasteurisation — acid weakens hot
  stabiliser). It brightens flavour and offsets flat low-acid fruit.
- High-pectin/pulpy fruit (mango, peach, citrus, apple, berries) needs less or no
  added stabiliser — it already bodies the mix.
- Don't heat raw pineapple or kiwi with dairy/egg (proteases); never cook kiwi
  (muddy off-flavour). Add lemon to banana/pear/peach/apricot to prevent browning.
