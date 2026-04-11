#!/usr/bin/env python3
"""
MCP Server for Proton Mail Bridge.

Provides IMAP email management tools: list, search, read, move, trash,
archive, flag, mark read/unread, delete emails, and manage folders
(create, delete, rename) via Proton Mail Bridge running locally with STARTTLS.
"""

from __future__ import annotations

import asyncio
import html.parser
import imaplib
import json
import logging
import os
import re
import ssl
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import date
from email import message_from_bytes, policy
from email.utils import parsedate_to_datetime
from typing import Any, Optional

from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration from environment
# ---------------------------------------------------------------------------

IMAP_HOST = os.environ.get("PROTON_BRIDGE_HOST", "127.0.0.1")
IMAP_PORT = int(os.environ.get("PROTON_BRIDGE_PORT", "1143"))
IMAP_USER = os.environ.get("PROTON_BRIDGE_USER", "")
IMAP_PASS = os.environ.get("PROTON_BRIDGE_PASSWORD", "")

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ImapError(Exception):
    pass


class ImapConnectionError(ImapError):
    pass


class ImapAuthError(ImapError):
    pass


class ImapOperationError(ImapError):
    pass


# ---------------------------------------------------------------------------
# HTML tag stripper
# ---------------------------------------------------------------------------


class _HTMLStripper(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self._parts.append(data)

    def get_text(self) -> str:
        return "".join(self._parts)


def strip_html(text: str) -> str:
    s = _HTMLStripper()
    s.feed(text)
    return s.get_text()


# ---------------------------------------------------------------------------
# Modified UTF-7 (IMAP folder names)
# ---------------------------------------------------------------------------


def decode_mutf7(data: bytes) -> str:
    result: list[str] = []
    i = 0
    while i < len(data):
        if data[i : i + 1] == b"&":
            end = data.index(b"-", i + 1)
            if end == i + 1:
                result.append("&")
            else:
                encoded = data[i + 1 : end]
                utf7 = b"+" + encoded.replace(b",", b"/") + b"-"
                result.append(utf7.decode("utf-7"))
            i = end + 1
        else:
            result.append(chr(data[i]))
            i += 1
    return "".join(result)


# ---------------------------------------------------------------------------
# IMAP response helpers
# ---------------------------------------------------------------------------

LIST_RE = re.compile(rb'\((?P<flags>.*?)\) "(?P<delim>.*?)" (?P<name>.+)')


def check_ok(typ: str, data: list, operation: str) -> list:
    if typ == "OK":
        return data
    msg = data[0].decode() if data and data[0] else "Unknown error"
    if typ == "NO":
        raise ImapOperationError(f"{operation} refused: {msg}")
    raise ImapOperationError(f"{operation} error: {typ} {msg}")


def parse_list_response(data: list[bytes | None]) -> list[dict[str, Any]]:
    folders = []
    for item in data:
        if item is None:
            continue
        m = LIST_RE.match(item)
        if m:
            flags = m.group("flags").decode()
            name_raw = m.group("name").strip(b' "')
            name = decode_mutf7(name_raw)
            folders.append({"name": name, "flags": flags})
    return folders


def parse_uids(data: list[bytes | None]) -> list[str]:
    if not data or data[0] is None or data[0] == b"":
        return []
    return data[0].decode().split()


def parse_header_value(raw: str | None) -> str:
    return raw.strip() if raw else ""


# ---------------------------------------------------------------------------
# Email parsing
# ---------------------------------------------------------------------------

MAX_BODY_CHARS = 50_000


def parse_email_full(raw: bytes) -> dict[str, Any]:
    msg = message_from_bytes(raw, policy=policy.default)
    result: dict[str, Any] = {
        "from": parse_header_value(msg["From"]),
        "to": parse_header_value(msg["To"]),
        "cc": parse_header_value(msg["Cc"]),
        "bcc": parse_header_value(msg["Bcc"]),
        "reply_to": parse_header_value(msg["Reply-To"]),
        "subject": parse_header_value(msg["Subject"]) or "(no subject)",
        "date": parse_header_value(msg["Date"]),
        "message_id": parse_header_value(msg["Message-ID"]),
    }

    body_part = msg.get_body(preferencelist=("plain", "html"))
    if body_part:
        try:
            content = body_part.get_content()
        except Exception:
            content = "(could not decode body)"
        if body_part.get_content_type() == "text/html":
            content = strip_html(content)
        result["body"] = content[:MAX_BODY_CHARS]
        result["body_truncated"] = len(content) > MAX_BODY_CHARS
    else:
        result["body"] = "(no readable body)"
        result["body_truncated"] = False

    attachments = []
    try:
        for part in msg.iter_attachments():
            att: dict[str, Any] = {
                "filename": part.get_filename() or "(unnamed)",
                "content_type": part.get_content_type(),
            }
            try:
                payload = part.get_content()
                att["size"] = len(payload) if hasattr(payload, "__len__") else None
            except Exception:
                att["size"] = None
            attachments.append(att)
    except Exception:
        pass
    result["attachments"] = attachments

    return result


def parse_email_headers(raw: bytes) -> dict[str, Any]:
    msg = message_from_bytes(raw, policy=policy.default)
    return {
        "from": parse_header_value(msg["From"]),
        "to": parse_header_value(msg["To"]),
        "subject": parse_header_value(msg["Subject"]) or "(no subject)",
        "date": parse_header_value(msg["Date"]),
    }


# ---------------------------------------------------------------------------
# IMAP Client
# ---------------------------------------------------------------------------


@dataclass
class ImapClient:
    host: str
    port: int
    username: str
    password: str
    _conn: imaplib.IMAP4 | None = field(default=None, init=False, repr=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)
    _selected_folder: str | None = field(default=None, init=False, repr=False)
    _special_folders: dict[str, str] = field(default_factory=dict, init=False, repr=False)

    def _ssl_context(self) -> ssl.SSLContext:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    def _connect_sync(self) -> imaplib.IMAP4:
        try:
            conn = imaplib.IMAP4(self.host, self.port)
        except ConnectionRefusedError:
            raise ImapConnectionError(
                f"Cannot connect to Proton Mail Bridge at {self.host}:{self.port}. "
                "Is Bridge running and unlocked?"
            )
        except (OSError, TimeoutError) as e:
            raise ImapConnectionError(
                f"Connection to Proton Mail Bridge failed: {e}"
            )

        try:
            conn.starttls(ssl_context=self._ssl_context())
        except imaplib.IMAP4.error as e:
            raise ImapConnectionError(f"STARTTLS failed: {e}")

        try:
            conn.login(self.username, self.password)
        except imaplib.IMAP4.error as e:
            raise ImapAuthError(
                f"Authentication failed: {e}. "
                "Use the Bridge password, not your Proton account password."
            )

        return conn

    def _disconnect_sync(self) -> None:
        if self._conn is not None:
            try:
                self._conn.logout()
            except Exception:
                pass
            self._conn = None
            self._selected_folder = None

    def _ensure_connected_sync(self) -> imaplib.IMAP4:
        if self._conn is not None:
            try:
                typ, _ = self._conn.noop()
                if typ == "OK":
                    return self._conn
            except Exception:
                logger.warning("IMAP connection lost, reconnecting...")
                self._conn = None
                self._selected_folder = None
        self._conn = self._connect_sync()
        return self._conn

    def _detect_special_folders_sync(self) -> None:
        conn = self._ensure_connected_sync()
        typ, data = conn.list()
        if typ != "OK":
            return
        for item in data:
            if item is None:
                continue
            m = LIST_RE.match(item)
            if not m:
                continue
            flags = m.group("flags").decode().lower()
            name_raw = m.group("name").strip(b' "')
            name = decode_mutf7(name_raw)
            if "\\trash" in flags:
                self._special_folders["trash"] = name
            if "\\archive" in flags or "\\all" in flags:
                self._special_folders["archive"] = name
            if "\\sent" in flags:
                self._special_folders["sent"] = name
            if "\\drafts" in flags:
                self._special_folders["drafts"] = name
            if "\\junk" in flags:
                self._special_folders["spam"] = name

        # Fallback defaults if not detected
        self._special_folders.setdefault("trash", "Trash")
        self._special_folders.setdefault("archive", "Archive")

    # Proton Mail stores user folders under "Folders/".
    # Auto-prefix bare names so callers can just say "Amazon" instead of "Folders/Amazon".
    _RESERVED_FOLDERS = frozenset({
        "INBOX", "Sent", "Drafts", "Trash", "Spam", "Archive",
        "All Mail", "Starred",
    })

    def _resolve_folder(self, folder: str) -> str:
        if folder in self._RESERVED_FOLDERS:
            return folder
        if folder.startswith("Folders/"):
            return folder
        if folder in self._special_folders.values():
            return folder
        return f"Folders/{folder}"

    def _select_sync(self, conn: imaplib.IMAP4, folder: str, readonly: bool = False) -> int:
        folder = self._resolve_folder(folder)
        quoted = f'"{folder}"'
        typ, data = conn.select(quoted, readonly=readonly)
        check_ok(typ, data, f"SELECT {folder}")
        self._selected_folder = folder
        return int(data[0])

    async def connect(self) -> None:
        async with self._lock:
            self._conn = await asyncio.to_thread(self._connect_sync)
            await asyncio.to_thread(self._detect_special_folders_sync)

    async def disconnect(self) -> None:
        async with self._lock:
            await asyncio.to_thread(self._disconnect_sync)

    async def execute(self, fn: Any) -> Any:
        async with self._lock:
            conn = await asyncio.to_thread(self._ensure_connected_sync)
            return await asyncio.to_thread(fn, conn)

    @property
    def trash_folder(self) -> str:
        return self._special_folders.get("trash", "Trash")

    @property
    def archive_folder(self) -> str:
        return self._special_folders.get("archive", "Archive")


# ---------------------------------------------------------------------------
# FastMCP app
# ---------------------------------------------------------------------------


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[ImapClient]:
    if not IMAP_USER or not IMAP_PASS:
        raise RuntimeError(
            "PROTON_BRIDGE_USER and PROTON_BRIDGE_PASSWORD environment variables are required."
        )
    client = ImapClient(
        host=IMAP_HOST,
        port=IMAP_PORT,
        username=IMAP_USER,
        password=IMAP_PASS,
    )
    await client.connect()
    try:
        yield client
    finally:
        await client.disconnect()


mcp = FastMCP("email_mcp", lifespan=app_lifespan)


def _get_client(ctx: Context) -> ImapClient:
    return ctx.request_context.lifespan_context


# ---------------------------------------------------------------------------
# Shared helpers for list/search result fetching
# ---------------------------------------------------------------------------


def _fetch_message_summaries(
    conn: imaplib.IMAP4, uids: list[str]
) -> list[dict[str, Any]]:
    if not uids:
        return []
    uid_str = ",".join(uids)
    typ, data = conn.uid(
        "FETCH",
        uid_str,
        "(UID FLAGS RFC822.SIZE BODY.PEEK[HEADER.FIELDS (FROM TO SUBJECT DATE)])",
    )
    check_ok(typ, data, "FETCH headers")

    results: list[dict[str, Any]] = []
    i = 0
    while i < len(data):
        item = data[i]
        if item is None or item == b")":
            i += 1
            continue
        if isinstance(item, tuple) and len(item) == 2:
            meta_line, header_bytes = item
            meta = meta_line.decode(errors="replace")

            uid_match = re.search(r"UID (\d+)", meta)
            uid = uid_match.group(1) if uid_match else "?"

            size_match = re.search(r"RFC822\.SIZE (\d+)", meta)
            size = int(size_match.group(1)) if size_match else 0

            flags_match = re.search(r"FLAGS \(([^)]*)\)", meta)
            flags = flags_match.group(1).split() if flags_match else []

            headers = parse_email_headers(header_bytes)
            results.append(
                {
                    "uid": uid,
                    "from": headers["from"],
                    "to": headers["to"],
                    "subject": headers["subject"],
                    "date": headers["date"],
                    "flags": flags,
                    "size": size,
                }
            )
        i += 1

    return results


# ---------------------------------------------------------------------------
# Tool: email_list_folders
# ---------------------------------------------------------------------------


@mcp.tool(
    name="email_list_folders",
    annotations={
        "title": "List Email Folders",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def email_list_folders(ctx: Context) -> str:
    """List all IMAP folders with message counts and unread counts.

    Call this first to discover available folder names before other operations.
    Returns a JSON array of folders with name, total messages, and unread count.
    """
    client = _get_client(ctx)

    def _do(conn: imaplib.IMAP4) -> str:
        typ, data = conn.list()
        check_ok(typ, data, "LIST")
        folders = parse_list_response(data)

        results = []
        for f in folders:
            if "\\noselect" in f["flags"].lower():
                results.append(
                    {"name": f["name"], "flags": f["flags"], "total": None, "unread": None}
                )
                continue
            try:
                typ2, status_data = conn.status(
                    f'"{f["name"]}"', "(MESSAGES UNSEEN)"
                )
                if typ2 == "OK" and status_data[0]:
                    status_str = status_data[0].decode()
                    msgs = re.search(r"MESSAGES (\d+)", status_str)
                    unseen = re.search(r"UNSEEN (\d+)", status_str)
                    results.append(
                        {
                            "name": f["name"],
                            "total": int(msgs.group(1)) if msgs else 0,
                            "unread": int(unseen.group(1)) if unseen else 0,
                        }
                    )
                else:
                    results.append({"name": f["name"], "total": 0, "unread": 0})
            except Exception:
                results.append({"name": f["name"], "total": None, "unread": None})
        return json.dumps(results, indent=2)

    return await client.execute(_do)


# ---------------------------------------------------------------------------
# Tool: email_list_messages
# ---------------------------------------------------------------------------


class ListMessagesInput(BaseModel):
    folder: str = Field(default="INBOX", description='IMAP folder name, e.g. "INBOX", "Sent", "Archive"')
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Messages per page")


@mcp.tool(
    name="email_list_messages",
    annotations={
        "title": "List Messages in Folder",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def email_list_messages(params: ListMessagesInput, ctx: Context) -> str:
    """List email headers in a folder, newest first, with pagination.

    Returns subject, from, to, date, flags, and size for each message.
    Use BODY.PEEK so messages are not marked as read.
    """
    client = _get_client(ctx)

    def _do(conn: imaplib.IMAP4) -> str:
        client._select_sync(conn, params.folder, readonly=True)
        typ, data = conn.uid("SEARCH", None, "ALL")
        check_ok(typ, data, "SEARCH")
        all_uids = parse_uids(data)

        # Newest first
        all_uids.reverse()
        total = len(all_uids)
        total_pages = max(1, (total + params.page_size - 1) // params.page_size)
        start = (params.page - 1) * params.page_size
        page_uids = all_uids[start : start + params.page_size]

        messages = _fetch_message_summaries(conn, page_uids)

        return json.dumps(
            {
                "folder": params.folder,
                "total": total,
                "page": params.page,
                "page_size": params.page_size,
                "total_pages": total_pages,
                "messages": messages,
            },
            indent=2,
        )

    return await client.execute(_do)


# ---------------------------------------------------------------------------
# Tool: email_search
# ---------------------------------------------------------------------------


class SearchInput(BaseModel):
    folder: str = Field(default="INBOX", description="Folder to search in")
    from_addr: Optional[str] = Field(default=None, description="Sender address or name substring")
    to_addr: Optional[str] = Field(default=None, description="Recipient address or name substring")
    subject: Optional[str] = Field(default=None, description="Subject substring")
    body: Optional[str] = Field(default=None, description="Body text substring")
    since: Optional[str] = Field(default=None, description="Messages on or after this date (YYYY-MM-DD)")
    before: Optional[str] = Field(default=None, description="Messages before this date (YYYY-MM-DD)")
    is_unread: Optional[bool] = Field(default=None, description="True=unread only, False=read only, None=both")
    is_flagged: Optional[bool] = Field(default=None, description="True=flagged only, False=unflagged, None=both")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Results per page")


def _imap_date(iso_date: str) -> str:
    d = date.fromisoformat(iso_date)
    return d.strftime("%d-%b-%Y")


@mcp.tool(
    name="email_search",
    annotations={
        "title": "Search Emails",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def email_search(params: SearchInput, ctx: Context) -> str:
    """Search emails in a folder by multiple criteria (AND logic).

    Supports filtering by sender, recipient, subject, body text, date range,
    and read/flagged status. Returns paginated results, newest first.
    """
    client = _get_client(ctx)

    def _do(conn: imaplib.IMAP4) -> str:
        client._select_sync(conn, params.folder, readonly=True)

        criteria: list[str] = []
        if params.from_addr:
            criteria.extend(["FROM", f'"{params.from_addr}"'])
        if params.to_addr:
            criteria.extend(["TO", f'"{params.to_addr}"'])
        if params.subject:
            criteria.extend(["SUBJECT", f'"{params.subject}"'])
        if params.body:
            criteria.extend(["BODY", f'"{params.body}"'])
        if params.since:
            criteria.extend(["SINCE", _imap_date(params.since)])
        if params.before:
            criteria.extend(["BEFORE", _imap_date(params.before)])
        if params.is_unread is True:
            criteria.append("UNSEEN")
        elif params.is_unread is False:
            criteria.append("SEEN")
        if params.is_flagged is True:
            criteria.append("FLAGGED")
        elif params.is_flagged is False:
            criteria.append("UNFLAGGED")

        if not criteria:
            criteria.append("ALL")

        typ, data = conn.uid("SEARCH", None, *criteria)
        check_ok(typ, data, "SEARCH")
        all_uids = parse_uids(data)
        all_uids.reverse()

        total = len(all_uids)
        total_pages = max(1, (total + params.page_size - 1) // params.page_size)
        start = (params.page - 1) * params.page_size
        page_uids = all_uids[start : start + params.page_size]

        messages = _fetch_message_summaries(conn, page_uids)

        return json.dumps(
            {
                "folder": params.folder,
                "query": {k: v for k, v in params.model_dump().items() if v is not None and k not in ("page", "page_size", "folder")},
                "total": total,
                "page": params.page,
                "page_size": params.page_size,
                "total_pages": total_pages,
                "messages": messages,
            },
            indent=2,
        )

    return await client.execute(_do)


# ---------------------------------------------------------------------------
# Tool: email_read
# ---------------------------------------------------------------------------


class ReadEmailInput(BaseModel):
    uid: str = Field(..., description="Message UID to read")
    folder: str = Field(default="INBOX", description="Folder containing the message")
    mark_as_read: bool = Field(default=True, description="Mark the message as read after fetching")
    prefer_html: bool = Field(default=False, description="Return HTML body instead of plain text")


@mcp.tool(
    name="email_read",
    annotations={
        "title": "Read Email",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def email_read(params: ReadEmailInput, ctx: Context) -> str:
    """Read the full content of a single email by UID.

    Parses MIME multipart messages, extracts plain text (or HTML if preferred),
    and lists attachments with metadata. By default marks the message as read.
    """
    client = _get_client(ctx)

    def _do(conn: imaplib.IMAP4) -> str:
        client._select_sync(conn, params.folder, readonly=not params.mark_as_read)

        fetch_part = "BODY[]" if params.mark_as_read else "BODY.PEEK[]"
        typ, data = conn.uid("FETCH", params.uid, f"(UID FLAGS {fetch_part})")
        check_ok(typ, data, "FETCH")

        raw_email: bytes | None = None
        flags: list[str] = []
        for item in data:
            if isinstance(item, tuple) and len(item) == 2:
                meta = item[0].decode(errors="replace")
                flags_match = re.search(r"FLAGS \(([^)]*)\)", meta)
                if flags_match:
                    flags = flags_match.group(1).split()
                raw_email = item[1]
                break

        if raw_email is None:
            return json.dumps({"error": f"Message UID {params.uid} not found in {params.folder}."})

        result = parse_email_full(raw_email)
        result["uid"] = params.uid
        result["flags"] = flags
        result["folder"] = params.folder

        # If user prefers HTML and we stripped it, re-parse
        if params.prefer_html:
            msg = message_from_bytes(raw_email, policy=policy.default)
            html_part = msg.get_body(preferencelist=("html",))
            if html_part:
                try:
                    result["body"] = html_part.get_content()[:MAX_BODY_CHARS]
                    result["body_type"] = "text/html"
                except Exception:
                    pass

        return json.dumps(result, indent=2, default=str)

    return await client.execute(_do)


# ---------------------------------------------------------------------------
# Tool: email_move
# ---------------------------------------------------------------------------


class MoveInput(BaseModel):
    uids: list[str] = Field(..., min_length=1, description="Message UIDs to move")
    source_folder: str = Field(..., description="Source folder")
    destination_folder: str = Field(..., description="Destination folder")


@mcp.tool(
    name="email_move",
    annotations={
        "title": "Move Emails",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def email_move(params: MoveInput, ctx: Context) -> str:
    """Move one or more emails from one folder to another.

    Confirm with the user before calling this tool. This copies messages to the
    destination and removes them from the source folder.
    """
    client = _get_client(ctx)

    def _do(conn: imaplib.IMAP4) -> str:
        client._select_sync(conn, params.source_folder, readonly=False)
        uid_str = ",".join(params.uids)
        dest = client._resolve_folder(params.destination_folder)

        typ, _ = conn.uid("COPY", uid_str, f'"{dest}"')
        check_ok(typ, _, f"COPY to {dest}")

        conn.uid("STORE", uid_str, "+FLAGS", "(\\Deleted)")
        conn.expunge()

        return json.dumps(
            {
                "moved": len(params.uids),
                "source": params.source_folder,
                "destination": params.destination_folder,
                "uids": params.uids,
            },
            indent=2,
        )

    return await client.execute(_do)


# ---------------------------------------------------------------------------
# Tool: email_trash
# ---------------------------------------------------------------------------


class TrashInput(BaseModel):
    uids: list[str] = Field(..., min_length=1, description="Message UIDs to trash")
    folder: str = Field(default="INBOX", description="Source folder containing the messages")


@mcp.tool(
    name="email_trash",
    annotations={
        "title": "Trash Emails",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def email_trash(params: TrashInput, ctx: Context) -> str:
    """Move one or more emails to the Trash folder.

    Confirm with the user before calling this tool. Messages can be recovered
    from Trash until it is emptied.
    """
    client = _get_client(ctx)

    def _do(conn: imaplib.IMAP4) -> str:
        trash = client.trash_folder
        client._select_sync(conn, params.folder, readonly=False)
        uid_str = ",".join(params.uids)

        typ, _ = conn.uid("COPY", uid_str, f'"{trash}"')
        check_ok(typ, _, f"COPY to {trash}")

        conn.uid("STORE", uid_str, "+FLAGS", "(\\Deleted)")
        conn.expunge()

        return json.dumps(
            {
                "trashed": len(params.uids),
                "source": params.folder,
                "trash_folder": trash,
                "uids": params.uids,
            },
            indent=2,
        )

    return await client.execute(_do)


# ---------------------------------------------------------------------------
# Tool: email_archive
# ---------------------------------------------------------------------------


class ArchiveInput(BaseModel):
    uids: list[str] = Field(..., min_length=1, description="Message UIDs to archive")
    folder: str = Field(default="INBOX", description="Source folder containing the messages")


@mcp.tool(
    name="email_archive",
    annotations={
        "title": "Archive Emails",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def email_archive(params: ArchiveInput, ctx: Context) -> str:
    """Move one or more emails to the Archive folder.

    Confirm with the user before calling this tool. Archived messages are
    preserved but removed from the source folder.
    """
    client = _get_client(ctx)

    def _do(conn: imaplib.IMAP4) -> str:
        archive = client.archive_folder
        client._select_sync(conn, params.folder, readonly=False)
        uid_str = ",".join(params.uids)

        typ, _ = conn.uid("COPY", uid_str, f'"{archive}"')
        check_ok(typ, _, f"COPY to {archive}")

        conn.uid("STORE", uid_str, "+FLAGS", "(\\Deleted)")
        conn.expunge()

        return json.dumps(
            {
                "archived": len(params.uids),
                "source": params.folder,
                "archive_folder": archive,
                "uids": params.uids,
            },
            indent=2,
        )

    return await client.execute(_do)


# ---------------------------------------------------------------------------
# Tool: email_mark_read
# ---------------------------------------------------------------------------


class MarkReadInput(BaseModel):
    uids: list[str] = Field(..., min_length=1, description="Message UIDs to modify")
    folder: str = Field(default="INBOX", description="Folder containing the messages")
    read: bool = Field(..., description="True to mark as read, False to mark as unread")


@mcp.tool(
    name="email_mark_read",
    annotations={
        "title": "Mark Emails Read/Unread",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def email_mark_read(params: MarkReadInput, ctx: Context) -> str:
    """Mark one or more emails as read or unread.

    Setting a flag that is already set is a no-op (idempotent).
    """
    client = _get_client(ctx)

    def _do(conn: imaplib.IMAP4) -> str:
        client._select_sync(conn, params.folder, readonly=False)
        uid_str = ",".join(params.uids)
        op = "+FLAGS" if params.read else "-FLAGS"
        typ, _ = conn.uid("STORE", uid_str, op, "(\\Seen)")
        check_ok(typ, _, "STORE \\Seen")

        return json.dumps(
            {
                "uids": params.uids,
                "folder": params.folder,
                "marked_as": "read" if params.read else "unread",
            },
            indent=2,
        )

    return await client.execute(_do)


# ---------------------------------------------------------------------------
# Tool: email_flag
# ---------------------------------------------------------------------------


class FlagInput(BaseModel):
    uids: list[str] = Field(..., min_length=1, description="Message UIDs to modify")
    folder: str = Field(default="INBOX", description="Folder containing the messages")
    flagged: bool = Field(..., description="True to star/flag, False to remove star/flag")


@mcp.tool(
    name="email_flag",
    annotations={
        "title": "Star/Unstar Emails",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def email_flag(params: FlagInput, ctx: Context) -> str:
    """Star (flag) or unstar (unflag) one or more emails.

    Setting a flag that is already set is a no-op (idempotent).
    """
    client = _get_client(ctx)

    def _do(conn: imaplib.IMAP4) -> str:
        client._select_sync(conn, params.folder, readonly=False)
        uid_str = ",".join(params.uids)
        op = "+FLAGS" if params.flagged else "-FLAGS"
        typ, _ = conn.uid("STORE", uid_str, op, "(\\Flagged)")
        check_ok(typ, _, "STORE \\Flagged")

        return json.dumps(
            {
                "uids": params.uids,
                "folder": params.folder,
                "flagged": params.flagged,
            },
            indent=2,
        )

    return await client.execute(_do)


# ---------------------------------------------------------------------------
# Tool: email_delete
# ---------------------------------------------------------------------------


class DeleteInput(BaseModel):
    uids: list[str] = Field(..., min_length=1, description="Message UIDs to permanently delete")
    folder: str = Field(..., description='Folder containing the messages (typically "Trash")')


@mcp.tool(
    name="email_delete",
    annotations={
        "title": "Permanently Delete Emails",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def email_delete(params: DeleteInput, ctx: Context) -> str:
    """Permanently delete one or more emails. THIS IS IRREVERSIBLE.

    Confirm with the user before calling this tool. Prefer email_trash instead
    unless the user explicitly asks for permanent deletion.
    """
    client = _get_client(ctx)

    def _do(conn: imaplib.IMAP4) -> str:
        client._select_sync(conn, params.folder, readonly=False)
        uid_str = ",".join(params.uids)
        conn.uid("STORE", uid_str, "+FLAGS", "(\\Deleted)")
        conn.expunge()

        return json.dumps(
            {
                "deleted": len(params.uids),
                "folder": params.folder,
                "uids": params.uids,
            },
            indent=2,
        )

    return await client.execute(_do)


# ---------------------------------------------------------------------------
# Folder management helpers
# ---------------------------------------------------------------------------


def _assert_not_reserved(folder: str) -> None:
    if folder in ImapClient._RESERVED_FOLDERS:
        raise ImapOperationError(
            f"'{folder}' is a reserved system folder and cannot be created, deleted, or renamed."
        )


# ---------------------------------------------------------------------------
# Tool: email_create_folder
# ---------------------------------------------------------------------------


class CreateFolderInput(BaseModel):
    folder: str = Field(..., description="Name for the new folder (e.g. \"Receipts\")")


@mcp.tool(
    name="email_create_folder",
    annotations={
        "title": "Create Folder",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def email_create_folder(params: CreateFolderInput, ctx: Context) -> str:
    """Create a new IMAP folder and subscribe to it.

    The folder name is automatically prefixed with "Folders/" for Proton Mail
    compatibility. Reserved system folders cannot be created.
    """
    _assert_not_reserved(params.folder)
    client = _get_client(ctx)

    def _do(conn: imaplib.IMAP4) -> str:
        resolved = client._resolve_folder(params.folder)
        quoted = f'"{resolved}"'
        typ, data = conn.create(quoted)
        check_ok(typ, data, "CREATE")
        try:
            conn.subscribe(quoted)
        except Exception:
            pass

        return json.dumps(
            {"created": resolved, "subscribed": True},
            indent=2,
        )

    return await client.execute(_do)


# ---------------------------------------------------------------------------
# Tool: email_delete_folder
# ---------------------------------------------------------------------------


class DeleteFolderInput(BaseModel):
    folder: str = Field(..., description="Name of the folder to delete")


@mcp.tool(
    name="email_delete_folder",
    annotations={
        "title": "Delete Folder",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def email_delete_folder(params: DeleteFolderInput, ctx: Context) -> str:
    """Delete an IMAP folder. ALL MESSAGES IN THE FOLDER WILL BE LOST.

    Confirm with the user before calling this tool. Reserved system folders
    cannot be deleted.
    """
    _assert_not_reserved(params.folder)
    client = _get_client(ctx)

    def _do(conn: imaplib.IMAP4) -> str:
        resolved = client._resolve_folder(params.folder)
        quoted = f'"{resolved}"'
        try:
            conn.unsubscribe(quoted)
        except Exception:
            pass
        typ, data = conn.delete(quoted)
        check_ok(typ, data, "DELETE")

        return json.dumps(
            {"deleted": resolved, "unsubscribed": True},
            indent=2,
        )

    return await client.execute(_do)


# ---------------------------------------------------------------------------
# Tool: email_rename_folder
# ---------------------------------------------------------------------------


class RenameFolderInput(BaseModel):
    old_name: str = Field(..., description="Current folder name")
    new_name: str = Field(..., description="New folder name")


@mcp.tool(
    name="email_rename_folder",
    annotations={
        "title": "Rename Folder",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def email_rename_folder(params: RenameFolderInput, ctx: Context) -> str:
    """Rename an IMAP folder.

    Confirm with the user before calling this tool. Reserved system folders
    cannot be renamed.
    """
    _assert_not_reserved(params.old_name)
    _assert_not_reserved(params.new_name)
    client = _get_client(ctx)

    def _do(conn: imaplib.IMAP4) -> str:
        old_resolved = client._resolve_folder(params.old_name)
        new_resolved = client._resolve_folder(params.new_name)
        old_quoted = f'"{old_resolved}"'
        new_quoted = f'"{new_resolved}"'

        typ, data = conn.rename(old_quoted, new_quoted)
        check_ok(typ, data, "RENAME")
        try:
            conn.unsubscribe(old_quoted)
        except Exception:
            pass
        try:
            conn.subscribe(new_quoted)
        except Exception:
            pass

        return json.dumps(
            {
                "old_name": old_resolved,
                "new_name": new_resolved,
                "subscribed": True,
            },
            indent=2,
        )

    return await client.execute(_do)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
