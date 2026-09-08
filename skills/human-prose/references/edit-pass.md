# Edit pass

Use this when text already exists and the job is to remove the machine-made quality
without changing what it says. Works on the user's drafts and on your own; running it
over your own draft as a separate step catches more than trying to follow every rule
while also thinking about content.

## Rules

- Keep the author's ideas, claims, position, tense, and person. Invent nothing: no new
  numbers, examples, anecdotes, or promises.
- Keep roughly the same length unless a section is padding, in which case cut it.
- Change only the writing.

## Steps, in order

1. Delete every sentence that restates a point already made. Say things once.
2. Replace abstract nouns and adjectives with concrete detail already present in the
   text. Where no concrete detail exists, cut the claim rather than dressing it up.
3. Swap Latinate words for short plain ones. Utilise → use. Facilitate → help.
4. Break up the symmetry: no "while X, Y", no "not only X but also Y", no "it's not X,
   it's Y". Let sentences lean.
5. Vary sentence and paragraph length until the page looks irregular.
6. Reduce em dashes to at most one. Reduce bold and bullets to what earns its place.
7. Convert any "**Term**: explanation" lists into written sentences.
8. Cut the opening if it sets a scene. Cut the closing if it summarises.
9. Remove every sentence that explains the implication of the sentence before it.
10. Add contractions.

Then run `scripts/lint.py` on the result and fix what it flags.

## Output

The edited text, then a short list of the specific patterns you removed most often, so
the author can stop producing them. Name the pattern and quote one instance from the
original. Skip the list if the user asked for the text only.

## When editing isn't enough

Editing fixes surface tells. It can't give a piece a direction it never had. If the
input has no argument, no ending it's writing toward, or paragraphs that could be
shuffled without loss, say so in one sentence and offer a redraft under the Draft mode
instead of polishing it.
