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

### gelato-balancing

Balance authentic Italian gelato, fruit sorbetto, and dairy-free (vegan) frozen desserts at home using the professional formula — total solids, sugars, fat, milk solids (MSNF), stabilisers, and the PAC (anti-freezing) / POD (sweetness) sugar balance. Ask for any flavour — or just name a machine — and get a recipe with the full balancing math shown.

**Triggers on:** "make pistachio gelato", "fior di latte recipe", "balance a lemon sorbet", "vegan chocolate gelato", "a recipe for my Ninja Creami", "my gelato is icy/rock-hard/too sweet, fix the recipe", "convert this ice cream recipe to gelato"

**Features:**
- Covers cream/milk gelato, fruit sorbetto, **and dairy-free vegan gelato**, with both a supermarket-simple and an advanced specialty-ingredient path
- Bundled stdlib-Python calculator validates every metric (solids, sugars, fat, MSNF, lactose/sandiness, stabiliser, PAC/POD) against professional targets, scales to any batch size, and gives a plain-English texture read (also a `--json` mode)
- Portable runner: uses `python3` if present, else pulls one via `nix-shell -p python3` on Nix systems — no install needed
- Large built-in ingredient library (dairy, sugars, flavour pastes, plant milks, alcohol/salt, fruit Brix) plus common-name aliases, so recipes stay concise and the arithmetic is trustworthy
- Machine-aware (batch freezer, **Ninja Creami**, Cuisinart, no-machine) with a defect troubleshooting guide and worked reference recipes
- Research-backed references reconciled from named sources (Corvitto, Caviezel, Carpigiani, icecreamscience), honest about where the science genuinely disagrees

### human-prose

Write, edit, or personalise long-form prose so it reads as written by a person: articles, blog posts, Notion pages, wiki docs, READMEs. Three modes: **draft** new prose toward a decided ending, **edit** existing text without changing what it says, and **voice** (build a reusable voice profile from your own writing samples, saved to `~/.claude/human-prose/voice.md`).

**Triggers on:** "write a blog post / Notion page / wiki article about X", "make this sound less like AI", "humanise this", "edit this so it reads better", "build a voice profile from my writing"

**Features:**
- Rules target shape, not just vocabulary: concrete over abstract, varied sentence and paragraph length, no seesaw clauses, open and close on substance, trust the reader
- Bundled stdlib-Python linter flags banned words and phrases, negative parallelism, em dashes, exclamation marks, `**Term**: explanation` lists, Title Case headings, uniform rhythm, missing contractions, scene-setting openers and summarising closers
- Notion-specific block guidance (callouts, toggles, tables, TOC) loaded only when the target is Notion
- Banned list treated as defaults to override deliberately, with sources cited

### dream

Consolidate Claude Code's auto-memory by "dreaming" over past sessions. Reviews a project's recent session transcripts alongside its memory folder, finds repeated mistakes, user corrections and stale or contradicted memories, and proposes evidence-backed edits. Nothing is written until you approve items by number.

**Triggers on:** "/dream", "consolidate / clean up my memory", "learn from past sessions", "you keep making the same mistakes", "MEMORY.md is too long"

**Features:**
- Read-only stdlib-Python helper (`dream.sh`, same python3-or-nix-shell runner) that lists sessions, condenses transcripts and audits the memory folder
- Digests shrink multi-MB transcripts ~50–200× while always keeping user messages, errors, refusals and failures hidden in successful output
- Flags tool output that addresses the assistant (likely prompt injection) instead of acting on it
- Memory audit: index size vs the 200-line / 25 KB load limit, dangling links, orphan files, broken `[[links]]`, missing frontmatter
- Fans out sub-agents per batch of sessions; checks stale claims against the repo and git log
- Proposal with session ids and "k of n sessions" counts per item; edits only what you approve

## MCP Servers

### protonmail

MCP server for managing emails via Proton Mail Bridge's local IMAP interface. List folders, search, read, move, trash, archive, flag, delete emails, and manage folders — all through Claude's tool system.

**Requires:** [Proton Mail Bridge](https://proton.me/mail/bridge) running and unlocked locally.

**Features:**
- 13 IMAP tools exposed as MCP tools
  - **Read-only:** list folders, list messages, search, read
  - **Non-destructive:** mark read/unread, star/unstar, create folder
  - **Destructive:** move, trash, archive, delete, delete folder, rename folder
- Automatic `Folders/` prefix for Proton Mail's folder structure
- Persistent IMAP connection with auto-reconnect
- MIME multipart handling with plain text preference and attachment listing
- STARTTLS with Proton Mail Bridge's self-signed localhost certs
- Destructive actions require user confirmation

**Setup:**

```bash
# Clone the repo
git clone https://github.com/matteo-pacini/skills.git

# Make the run script executable
chmod +x skills/mcp/protonmail/run.sh

# Register the MCP server with Claude Code
claude mcp add --scope user \
  -e PROTON_BRIDGE_USER="your@protonmail.com" \
  -e PROTON_BRIDGE_PASSWORD="your-bridge-password" \
  -- protonmail \
  /path/to/skills/mcp/protonmail/run.sh
```

The Bridge password is the one shown in the Proton Mail Bridge app, **not** your Proton account password.

## Installation

```bash
npx skills add matteo-pacini/skills
```

## License

MIT
