# Notion formatting

Notion makes it easy to reach for blocks, and the result is a page that looks
structured and reads like nothing. Default to paragraphs. Every block below has to earn
its place.

## Headings

H2 for sections, H3 for subsections. Sentence case, never Title Case. Plain and
descriptive: the thing the section is about, not a clever label. No headings in a piece
under about 600 words. No emoji in headings.

## Lists

Bullets only for things that are genuinely a list of parallel items, never as a way of
avoiding writing a paragraph. Introduce every list with a full sentence. Six items
maximum; past that it wants to be prose or a table. Numbered lists only for real
sequences where order matters. No emoji in list items.

Never the "**Bold term**: explanation sentence" list format. Write the sentences out.

## Emphasis

Bold sparingly, never on more than a few words at a time. If two things per screen are
bold, nothing is emphasised. Italics for titles and the occasional stressed word.

## Blocks

Callouts: at most one or two per page, for a genuine warning or a piece of information
a reader would be harmed by missing. Not for decoration, not for "key takeaway".

Toggles: for reference detail, FAQs, or long asides a reader can skip. Good for the
material that would otherwise tempt you into a caveat paragraph.

Dividers: sparingly. Headings usually do the job.

Tables: for genuine comparisons across shared attributes. Not for anything with one
column of content and one of labels; that's a list, and probably prose.

Table of contents block: only above roughly 1,200 words.

## Characters

Straight quotes and apostrophes. Hyphens for hyphenation, en dashes for ranges (pages
12–14), em dashes at most once per page.

## Publishing

If a Notion MCP is available and the user wants the page created, write the piece as
Markdown first, run the linter, then create the page. Notion's Markdown import maps
`##`/`###` to H2/H3, `>` to a quote block (not a callout), and `---` to a divider.
Callouts and toggles usually need the tool's own block syntax; check the tool's
description rather than guessing.
