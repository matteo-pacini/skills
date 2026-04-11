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
