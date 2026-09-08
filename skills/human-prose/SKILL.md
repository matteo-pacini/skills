---
name: human-prose
description: >
  The default skill for any written document meant to be read as prose: blog posts,
  Notion and wiki pages, announcements, changelog and deprecation notices, retrospectives
  and incident write-ups, README sections, newsletters, help-centre articles, essays.
  Trigger on the output type, not the wording. "Write the retro", "draft the
  announcement", "newsletter intro, 150 words", "write up a post from my notes", "explain
  the on-call rota on a Notion page" all qualify even when style, tone, or AI is never
  mentioned, because readers spot generated prose and stop reading, and the user wants
  every piece checked. Also use when the user wants existing text to sound human, less
  AI, less corporate, tighter, or like their own voice ("humanise", "de-AI", "it has that
  AI smell", "make this read better"), or wants a voice profile built from samples of
  their writing. Three modes: draft, edit (preserve meaning), voice. Brings resources not
  otherwise in context: a lint script for machine-writing tells (banned words, negative
  parallelism, em dashes, bold-term lists, uniform rhythm), the banned list, Notion block
  rules, and the user's saved voice profile at ~/.claude/human-prose/voice.md. Do not use
  for code, docstrings, commit messages, one-line replies, chat messages, translation,
  proofreading-only, title brainstorming, slides, or reference tables where a list is the
  right shape.
---

# Human prose

Readers have learned to spot machine-made writing and stop reading when they see it.
The tells are not mainly vocabulary. They are shape: every paragraph the same length,
every claim balanced against a counter-claim, an opening that describes the state of
the world, a closing that recaps, and a steady business-casual register that never
moves. This skill exists to remove those, and the linter exists because a model editing
its own draft misses the tells it produces most.

## Pick a mode

- **Draft**: the user wants new prose. Follow "Before drafting", write, then run the
  final pass.
- **Edit**: the user has text (theirs, or a draft you already wrote) and wants it to
  read better without changing what it says. Read `references/edit-pass.md` and follow
  its ordered steps. Editing can only fix surface tells; it can't give a piece a
  direction it never had, so if the input has no argument, say so in one line and offer
  a redraft.
- **Voice**: the user wants a profile of how they write, built from samples, to reuse
  in future drafts. Read `references/voice-profile.md`.

Draft then Edit is the strongest combination: write the piece, then run the edit pass
over it as a separate step with fresh eyes. The second pass catches what the first
couldn't while it was also thinking about content.

## Before drafting

Establish four things. Ask only for what you can't infer from the request or the
repository; one short question at most, otherwise proceed with sensible defaults and
state them at the top of your reply (not inside the piece).

- **Audience**: who reads this, what they already know, how senior.
- **Where it's published**: Notion page, blog, README, help centre, email. This decides
  the formatting rules. For Notion, read `references/notion-formatting.md` before
  writing.
- **Voice**: if `~/.claude/human-prose/voice.md` exists, read it and follow it; it wins
  over the generic tone rules below where they conflict. If the user pasted a voice
  profile or described their voice, use that. Otherwise default to plain, direct, and
  confident, in the English variant the user writes in.
- **Length**: a word count, or "as short as the argument allows". Shorter is usually
  right; padding is the first thing readers notice.

Then, before writing a word, decide the last sentence of the piece. Write toward it. A
human knows where the piece ends, so every paragraph is pointed somewhere. A model
discovers its thesis in paragraph nine. Don't.

## The core rule

Every paragraph must give the reader something they did not have before it. If a
paragraph restates, reframes, or contextualises what the previous one already said,
delete it. Motion is not progress.

## Wording

Concrete over abstract, always. If a sentence can't be pictured, it isn't finished.
"The rollout was slow" is abstract; "the rollout took eleven weeks and two of the five
teams never switched" is concrete. Reach for the specific number, the named tool, the
actual quote, the real example. When you have no specific detail, say so plainly or cut
the claim. Never paper over the gap with adjectives, and never invent a number or an
anecdote to fill it.

Prefer short Germanic words to long Latinate ones. Use, not utilise. Help, not
facilitate. Show, not demonstrate. Start, not commence. Enough, not sufficient. Latinate
vocabulary is how text signals authority, and it's why generated prose feels stuck in
business-casual register.

Use contractions. It's, don't, won't, you're, we've. Their absence is one of the fastest
ways prose starts sounding like a policy document.

Em dashes: at most one per piece. Use commas, brackets, or a full stop. Where you'd
reach for an em dash, a full stop is usually better anyway.

The full banned list (words, phrases, structures) is in `references/banned-list.md`
and encoded in the linter. The structures matter more than the words, because a
synonym swap leaves the emptiness in place. The three to hold in mind while writing:

- Negative parallelism: "It's not just X, it's Y." "This isn't about X. It's about Y."
  "Not only X but also Y." State the claim directly.
- Triads used for rhythm rather than fact: three adjectives, three benefits, three
  examples. If there are two reasons, give two.
- The tailing participial flourish: "...changing how teams work", "...reshaping the
  industry". End the sentence on information.

## Sentences

Vary length hard. A twenty-eight-word sentence next to a four-word one. Then a
middle-length one. If three consecutive sentences are within five words of each other
in length, rewrite one.

Don't balance clauses. Generated writing is symmetrical: every claim gets a
counterweight, every sentence pivots on "while" or "however" or "though". Write spiky
sentences that lean into the claim and stop. Hedge once, when the hedge is real, not as
a reflex. "While the tool saves time, it's important to consider the learning curve"
becomes "The tool saves about an hour a week. It also takes a fortnight to get
comfortable with."

Vary how sentences open. Not every one starts with the subject. Not every one starts
with a transition either.

## Paragraphs

One idea per paragraph. When the idea changes, break.

Length must vary visibly: one sentence, then five, then two, then three. A page of
uniform four-sentence blocks reads as machine-made before a single word is processed.

A one-sentence paragraph is the strongest emphasis tool you have. Two or three per
piece, no more, or the effect dies.

Don't open a paragraph by announcing what it will contain, and don't close it by
summarising what it contained. Don't end on a portentous flourish about significance.
End on the last piece of information.

## Shape of the piece

Open on substance. The first sentence is a claim, a specific fact, a concrete
situation, or something that happened. Never a description of the state of the world,
the industry, or the era. If your opening paragraph would work unchanged on a piece
about a different topic, delete it and start at paragraph two.

Put the useful thing early. Don't withhold the answer to build up to it.

Close on substance too. No recap, no "in conclusion", no inspirational forward-look, no
call to reflect. The last paragraph carries the last real idea, then stops. Ending
abruptly reads as confidence.

## Trust the reader

This is the tell that survives everything else. Say the thing once, at the right level
of detail, and stop.

- Don't explain your own point after making it.
- Don't state the implication of a fact you've just given.
- Don't explain a joke, a metaphor, or an analogy.
- Don't connect every logical step. Leave one gap the reader crosses themselves.
- Don't restate the question or brief before answering it.
- Cut caveats nobody asked for. If a limitation changes what someone would do, name it
  in one sentence. Otherwise leave it out.

## Tone

Have a position and hold it. Vague, balanced, both-sides prose is the default setting
and it's what people recognise as generated. Where you assess something, assess it:
this works, this doesn't, this is worth the money, this is overrated.

Confident, not enthusiastic. No exclamation marks. No "exciting", "powerful",
"incredible", "amazing". Warmth comes from being direct and useful, not from adjectives.

Register can move. A plain, almost blunt sentence next to a slightly technical one,
next to an aside that sounds like speech. Staying in one register for 1,500 words is
what makes text feel extruded.

## Formatting

Prose first. Default to paragraphs. Headings in sentence case, plain and descriptive,
none in a piece under about 600 words. Bullets only for genuine lists of parallel
items, introduced by a full sentence, six items at most. Numbered lists only for real
sequences. Bold on a few words at a time, rarely. Never the "**Bold term**: explanation
sentence" list format; it is the most recognisable generated pattern there is. Write
the sentences out.

Notion has more block types and more ways to go wrong; `references/notion-formatting.md`
covers callouts, toggles, dividers, tables, and table of contents.

## Final pass

Write the draft to a file, then run the linter:

```bash
python3 scripts/lint.py path/to/draft.md
```

It reports banned words and phrases, negative parallelism, em dash count, exclamation
marks, `**Term**:` lists and `**Term.**` bold lead-in paragraphs, Title Case headings,
runs of same-length sentences, uniform paragraph lengths, missing contractions, and
scene-setting or summarising openers and closers. Fix what it flags by rewriting the sentence, not by swapping a synonym; the
synonym usually carries the same emptiness. Rerun until clean or until the only
remaining flags are deliberate (say which, in one line, outside the piece).

The linter can't check the things that matter most, so do these by hand, in order:

1. Read the opening sentence alone. Does it say something specific about this subject,
   or set a scene? If it sets a scene, cut it.
2. Read the closing paragraph alone. Summary or uplift? Cut it and end on the one above.
3. Find every abstract claim and check it has a concrete detail attached. Add one or
   cut the claim.
4. Ask of each paragraph: what does the reader now know that they didn't one paragraph
   ago? If nothing, delete it.
5. Read it out loud in your head. Any sentence that sounds like a press release, a
   LinkedIn post, or a product page gets rewritten.

## Output

Output the piece only. No preamble, no notes on approach, no offer to adjust it
afterwards. If you had to assume audience, venue, or length, state the assumptions in
one line before the piece, separated from it.

## On the banned list

The vocabulary list is a population-level signal, not proof of anything. Some of those
words were rising before 2022, and em dash frequency varies more by model than by
author. Much of the list descends from Wikipedia's "Signs of AI writing" catalogue,
which was built for neutral encyclopaedic prose. If the piece needs a strong point of
view, a few of those flags are things to do more of, not less. Treat the list as
defaults to override deliberately, and say when you have.
