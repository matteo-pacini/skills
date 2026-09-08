# Voice profile

The generic rules get most of the way. The remaining distance is the user's own voice,
and the only way to get that is samples.

## Collecting samples

Ask for 5 to 10 pieces the user actually wrote. Slack messages and emails count, and
short forms are useful because voice shows up differently at 30 words than at 1,500.
Nothing drafted with AI help: otherwise you're extracting a model's patterns back out
of the user's file and calling them theirs.

If the user points at files or a directory, read them. If they paste, separate samples
on `---`.

## Analysis

Don't summarise the samples into generic descriptions like "clear and engaging". Every
line of the profile must be specific enough that someone could follow it without ever
seeing the samples. Quote the user's actual phrasing where it's characteristic.

Cover:

- Typical sentence length and how much it varies
- How they open a piece, in structural terms, with examples
- How they end a piece
- Paragraph length habits
- Words and constructions they use repeatedly
- Words and constructions that appear nowhere in the samples and would sound wrong in
  their voice. Be specific and list plenty; this section matters most because it's the
  one that stops generic defaults leaking back in.
- Punctuation habits, including what they never use
- How formal they are, and where the register shifts
- How they handle uncertainty, disagreement, and their own mistakes
- Whether they use humour, and what kind
- Formatting instincts: headings, lists, bold, how much structure
- What they do that a competent generic writer would not do

## Output

Write it as instructions in the second person ("You write...", "You never..."), ready
to paste into a style guide. Hold it to about 400 words. It gets pasted into every
future draft's context, so every line has to earn its place, and a long profile gets
skimmed by the model the same way a long brief gets skimmed by a person. If you have
more than 400 words of genuine observation, keep the "never" list and the quoted
examples and cut the descriptive prose first. Short sections with sentence-case
headings are fine; bullets are fine for the "never" list.

Then tell the user: read it out loud. The parts that feel like being caught are right;
the parts that feel flattering are usually invented. Ask them to correct it.

## Saving

Offer to save the corrected profile to `~/.claude/human-prose/voice.md`. The Draft mode
reads that file automatically when it exists, so future drafts pick up the voice
without the user pasting it again. If they'd rather keep it per-project, any path works;
they just need to point the skill at it.
