# Skills

A collection of skills for [Claude Code](https://claude.com/claude-code) and other coding agents.

## Skills

### revealjs-presentation

Generate stunning, production-quality [Reveal.js](https://revealjs.com/) presentations as single self-contained HTML files. Opens directly in any browser — no build step, no local server, no npm install.

**Triggers on:** "Reveal.js presentation", "slide deck", "HTML presentation", "web-based slides", "interactive presentation", "animated slide deck"

**Features:**
- Single `.html` file output with CDN links (Reveal.js 5.2.1, Google Fonts)
- Professional typography with curated Google Font pairings
- Dark and light theme support with CSS custom properties
- Fragment animations, speaker notes, syntax-highlighted code slides
- Responsive 1920x1080 base resolution

### youtube-qa

Fetch YouTube video transcripts and answer questions about video content. Paste a YouTube URL and ask anything — get concise answers in the model's own words.

**Triggers on:** YouTube URL, "video transcript", "what does this video say", "summarize this video"

**Features:**
- Single dependency: `youtube-transcript-api` (no API key needed)
- Answers in own words — no quotes or timestamps unless you ask
- Automatically skips ads, sponsor reads, and promotional segments
- Multi-language support with translation
- Handles auto-generated and manual captions

## Installation

```bash
npx skills add matteo-pacini/skills
```

## License

MIT
