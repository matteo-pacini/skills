# Proton Mail MCP Server

Manage emails through Proton Mail Bridge's local IMAP interface. This is an MCP server — its tools appear directly in Claude's tool list when configured.

## Setup

### 1. Prerequisites

- **Proton Mail Bridge** running and unlocked on localhost
- **Python 3.9+** with the `mcp` package

### 2. Install dependencies

**With nix (automatic via run.sh):** No manual install needed — the wrapper script fetches dependencies.

**With pip:**
```bash
pip install "mcp[cli]"
```

### 3. Register the MCP server

```bash
chmod +x /path/to/mcp/protonmail/run.sh

claude mcp add --scope user \
  -e PROTON_BRIDGE_USER="your@protonmail.com" \
  -e PROTON_BRIDGE_PASSWORD="your-bridge-password" \
  -- protonmail \
  /path/to/mcp/protonmail/run.sh
```

The Bridge password is the one shown in the Proton Mail Bridge app, **not** your Proton account password.

### 4. Verify

```bash
claude mcp list
```

You should see `protonmail` listed and connected.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PROTON_BRIDGE_USER` | Yes | — | Bridge username (full email address) |
| `PROTON_BRIDGE_PASSWORD` | Yes | — | Bridge password (from Bridge app UI) |
| `PROTON_BRIDGE_HOST` | No | `127.0.0.1` | Bridge IMAP host |
| `PROTON_BRIDGE_PORT` | No | `1143` | Bridge IMAP port |

## Available Tools

### Read-only

- **email_list_folders** — List all folders with message counts and unread counts. Call this first.
- **email_list_messages** — List messages in a folder (paginated, newest first). Shows from, to, subject, date, flags, size.
- **email_search** — Search by from, to, subject, body, date range, read/unread, flagged. AND logic. Paginated.
- **email_read** — Read full email content by UID. Handles MIME multipart, lists attachments. Marks as read by default.

### Mutating (non-destructive)

- **email_mark_read** — Mark messages as read or unread. Idempotent.
- **email_flag** — Star or unstar messages. Idempotent.

### Folder management

- **email_create_folder** — Create a new folder and subscribe to it. Idempotent.

### Destructive — always confirm with the user first

- **email_move** — Move messages between folders.
- **email_trash** — Move messages to Trash.
- **email_archive** — Move messages to Archive.
- **email_delete** — Permanently delete messages. Irreversible. Prefer email_trash.
- **email_delete_folder** — Delete a folder and all its messages. Irreversible.
- **email_rename_folder** — Rename a folder (preserves messages).

## Folder Name Resolution

Proton Mail stores user-created folders under `Folders/` (e.g. `Folders/Amazon`, `Folders/Steam`). The server automatically prefixes bare folder names:

- `"Amazon"` → `"Folders/Amazon"`
- `"Food/Butcher"` → `"Folders/Food/Butcher"`

Reserved names are passed through unchanged: `INBOX`, `Sent`, `Drafts`, `Trash`, `Spam`, `Archive`, `All Mail`, `Starred`.

Names already starting with `Folders/` are not double-prefixed.

## Usage Guidelines

1. **Start with `email_list_folders`** to discover folder names — they may vary by account.
2. **Use `email_search`** to find specific messages before reading them.
3. **Always confirm** before calling destructive tools (move, trash, archive, delete).
4. **Prefer `email_trash`** over `email_delete` — deletion is permanent.
5. **UIDs are stable** within a session but may change between sessions.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Cannot connect to Proton Mail Bridge" | Start Bridge and ensure it is unlocked |
| "Authentication failed" | Use the Bridge password from the Bridge app, not your Proton account password |
| "STARTTLS failed" | Check that Bridge is configured for STARTTLS on port 1143 |
| "Folder not found" | Run `email_list_folders` to see actual folder names |
| Slow body search | IMAP `BODY` search scans all messages — use date ranges to narrow scope |

## Technical Notes

- Uses STARTTLS with certificate verification disabled (safe for localhost self-signed certs)
- Persistent IMAP connection with automatic reconnection on failure
- All operations use UIDs (not sequence numbers) for stability
- Email bodies capped at 50,000 characters to keep context manageable
- `BODY.PEEK` used for list/search to avoid marking messages as read
