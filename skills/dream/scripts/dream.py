#!/usr/bin/env python3
"""Read-only helpers for the dream skill: list Claude Code sessions, condense
transcripts into reviewable digests, and audit the auto-memory folder.

Nothing here writes to ~/.claude; edits to memory are made by the agent after
the user approves them.

  dream.py where    [--project PATH | --project-dir DIR]
  dream.py sessions [--project PATH | --project-dir DIR] [--last N] [--since YYYY-MM-DD]
  dream.py digest   SESSION... [--project ... ] [--subagents] [--max-chars N]
  dream.py memstat  [--project ... ] [--memory-dir DIR] [--last N]
"""

import argparse
import datetime as dt
import glob
import json
import os
import re
import sys

MEMORY_LINE_LIMIT = 200
MEMORY_BYTE_LIMIT = 25 * 1024
DREAM_MARKER = re.compile(r"<command-name>/?(?:[\w:-]+:)?dream</command-name>")
BARE_COMMAND = re.compile(r"/[\w:-]+")
# Heuristic, not a guarantee: text in tool output that talks to the model.
SUSPICIOUS = re.compile(
    r"(?:note|message|instructions?)\s+(?:to|for)\s+(?:the\s+)?(?:ai|assistant|claude|llm|agent)s?\b"
    r"|ignore\s+(?:all\s+|any\s+)?(?:previous|prior|above)\s+instructions"
    r"|\b(?:save|write|add|store)\s+(?:this|a|the\s+following)\s+(?:to\s+)?memory"
    r"|\byou\s+(?:must|should)\s+(?:now\s+)?(?:remember|always|never)\b",
    re.I)
HIDDEN_FAILURE = re.compile(r"command not found|Traceback \(most recent call last\)|: Permission denied")


def config_dir():
    return os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")


def project_dir(args):
    if args.project_dir:
        return os.path.abspath(os.path.expanduser(args.project_dir))
    cwd = os.path.abspath(os.path.expanduser(args.project or os.getcwd()))
    # Claude Code names the folder after the cwd with every non-alphanumeric
    # character replaced by "-".
    return os.path.join(config_dir(), "projects", re.sub(r"[^A-Za-z0-9]", "-", cwd))


def memory_dir(args):
    if getattr(args, "memory_dir", None):
        return os.path.abspath(os.path.expanduser(args.memory_dir))
    return os.path.join(project_dir(args), "memory")


def records(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def strip_reminders(text):
    return re.sub(r"<system-reminder>.*?</system-reminder>", "", text, flags=re.S).strip()


def user_text(rec):
    """The human-typed text of a user record, or None for tool results and
    injected skill/meta content."""
    if rec.get("type") != "user" or rec.get("isMeta"):
        return None
    content = (rec.get("message") or {}).get("content")
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        parts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
        if not parts:
            return None
        text = "\n".join(parts)
    else:
        return None
    m = re.search(r"<command-name>(.*?)</command-name>", text, re.S)
    if m:
        a = re.search(r"<command-args>(.*?)</command-args>", text, re.S)
        text = m.group(1).strip() + (" " + a.group(1).strip() if a and a.group(1).strip() else "")
    text = re.sub(r"<pasted_content[^>]*>(.*?)</pasted_content>",
                  lambda p: "[pasted: " + clip(p.group(1).strip(), 300) + "]", text, flags=re.S)
    text = strip_reminders(text)
    return text or None


def clip(text, n):
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[: n - 1] + "…"


def session_info(path):
    info = {"id": os.path.basename(path)[:-6], "path": path, "title": "", "start": None,
            "end": None, "user_turns": 0, "substantive_turns": 0, "first_prompt": "", "is_dream": False,
            "size_kb": os.path.getsize(path) // 1024}
    for r in records(path):
        ts = r.get("timestamp")
        if ts:
            info["start"] = info["start"] or ts
            info["end"] = ts
        if r.get("type") == "ai-title":
            info["title"] = r.get("aiTitle", "")
        raw = (r.get("message") or {}).get("content")
        if r.get("type") == "user" and isinstance(raw, str) and DREAM_MARKER.search(raw):
            info["is_dream"] = True
        t = user_text(r)
        if t:
            info["user_turns"] += 1
            info["substantive_turns"] += not BARE_COMMAND.fullmatch(t)
            info["first_prompt"] = info["first_prompt"] or t
    sub = os.path.join(path[:-6], "subagents")
    info["subagents"] = len(glob.glob(os.path.join(sub, "*.jsonl")))
    return info


def list_sessions(pdir, last=None, since=None):
    paths = sorted(glob.glob(os.path.join(pdir, "*.jsonl")), key=os.path.getmtime, reverse=True)
    out = []
    for p in paths:
        s = session_info(p)
        # Stubs made only of bare commands (/clear, /caveman …) hold nothing to learn from.
        if s["substantive_turns"] == 0 or s["is_dream"]:
            continue
        if since and (s["end"] or "") < since:
            continue
        out.append(s)
        if last and len(out) >= last:
            break
    return out


def resolve_session(arg, pdir):
    if os.path.isfile(arg):
        return arg
    hits = glob.glob(os.path.join(pdir, arg + "*.jsonl"))
    if len(hits) != 1:
        sys.exit(f"dream.py: session {arg!r} matched {len(hits)} files in {pdir}")
    return hits[0]


def tool_summary(name, inp):
    if not isinstance(inp, dict):
        return clip(inp, 200)
    for key in ("command", "file_path", "pattern", "url", "query", "skill", "prompt"):
        if key in inp:
            extra = f"  ({clip(inp['description'], 80)})" if key == "command" and inp.get("description") else ""
            return clip(inp[key], 300) + extra
    return clip(json.dumps(inp, ensure_ascii=False), 200)


def digest(path, max_chars):
    lines = []
    for r in records(path):
        t = r.get("type")
        if t == "queue-operation" and r.get("operation") == "enqueue" and r.get("content"):
            lines.append("[U, sent mid-turn] " + clip(r["content"], 1500))
            continue
        text = user_text(r)
        if text:
            lines.append("[U] " + clip(text, 1500))
            continue
        content = (r.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        if t == "assistant":
            for b in content:
                if b.get("type") == "text" and b.get("text", "").strip():
                    lines.append("[A] " + clip(b["text"], 600))
                elif b.get("type") == "tool_use":
                    lines.append(f"[T] {b.get('name')}: {tool_summary(b.get('name'), b.get('input'))}")
        elif t == "user":
            denied = (r.get("permissionDecision") or {}).get("decision") == "reject"
            for b in content:
                if b.get("type") != "tool_result":
                    continue
                body = b.get("content")
                if isinstance(body, list):
                    body = " ".join(x.get("text", "") for x in body if isinstance(x, dict))
                body = strip_reminders(str(body))
                m = SUSPICIOUS.search(body)
                if m:
                    lines.append("[SUSPICIOUS] tool output addresses the assistant: "
                                 + clip(body[max(0, m.start() - 80):m.end() + 200], 400))
                if b.get("is_error") or denied:
                    lines.append(("[DENIED] " if denied else "[E] ") + clip(body, 400))
                else:
                    # A failure mid-pipeline or in a ;-chain still exits 0, so
                    # the result is not flagged as an error.
                    hidden = HIDDEN_FAILURE.search(body)
                    if hidden:
                        lines.append("[E, exit 0] " + clip(body[max(0, hidden.start() - 100):hidden.end() + 100], 300))
    return shrink(lines, max_chars)


def shrink(lines, max_chars):
    """Fit a digest under max_chars by dropping tool calls, then assistant text.
    User messages, errors and denials are never dropped: they are the evidence."""
    text = "\n".join(lines)
    if len(text) <= max_chars:
        return text
    # The last assistant text before a user message is what the user reacted
    # to, so it survives even when other assistant text is dropped.
    before_user, last_a = set(), None
    for i, line in enumerate(lines):
        if line.startswith("[A]"):
            last_a = i
        elif line.startswith("[U") and last_a is not None:
            before_user.add(last_a)
            last_a = None
    for droppable in (("[T]",), ("[T]", "[A]")):
        out, skipped = [], 0
        for i, line in enumerate(lines):
            if line.startswith(droppable) and i not in before_user:
                skipped += 1
                continue
            if skipped:
                out.append(f"[… {skipped} lines omitted …]")
                skipped = 0
            out.append(line)
        if skipped:
            out.append(f"[… {skipped} lines omitted …]")
        text = "\n".join(out)
        if len(text) <= max_chars:
            break
    kinds = "tool calls" if droppable == ("[T]",) else "tool calls and assistant text"
    return f"[digest over {max_chars} chars: {kinds} omitted; rerun with a larger --max-chars for full detail]\n" + text


def cmd_where(args):
    pdir = project_dir(args)
    print(f"project_dir: {pdir}  (exists: {os.path.isdir(pdir)})")
    print(f"memory_dir:  {memory_dir(args)}  (exists: {os.path.isdir(memory_dir(args))})")


def cmd_sessions(args):
    pdir = project_dir(args)
    if not os.path.isdir(pdir):
        sys.exit(f"dream.py: no transcripts at {pdir}")
    for s in list_sessions(pdir, args.last, args.since):
        print(f"{s['id']}  {(s['end'] or '')[:16]}  turns={s['user_turns']:<3} "
              f"sub={s['subagents']:<2} {s['size_kb']:>6}KB  "
              f"{s['title'] or clip(s['first_prompt'], 70)}")


def cmd_digest(args):
    pdir = project_dir(args)
    for arg in args.session:
        path = resolve_session(arg, pdir)
        s = session_info(path)
        print(f"=== session {s['id']}  {(s['start'] or '')[:16]} → {(s['end'] or '')[:16]}  {s['title']}")
        print(digest(path, args.max_chars))
        if args.subagents:
            for sp in sorted(glob.glob(os.path.join(path[:-6], "subagents", "*.jsonl"))):
                print(f"--- subagent {os.path.basename(sp)[:-6]}")
                print(digest(sp, args.max_chars // 4))
        print()


def parse_frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        k, _, v = line.strip().partition(":")
        if v.strip():
            fm[k.strip()] = v.strip()
    return fm


def cmd_memstat(args):
    mdir = memory_dir(args)
    index = os.path.join(mdir, "MEMORY.md")
    if not os.path.isdir(mdir):
        sys.exit(f"dream.py: no memory folder at {mdir}")
    files = sorted(f for f in os.listdir(mdir) if f.endswith(".md") and f != "MEMORY.md")
    linked = []
    if os.path.isfile(index):
        raw = open(index, encoding="utf-8").read()
        n_lines, n_bytes = raw.count("\n") + (not raw.endswith("\n")), len(raw.encode())
        print(f"MEMORY.md: {n_lines}/{MEMORY_LINE_LIMIT} lines, {n_bytes}/{MEMORY_BYTE_LIMIT} bytes"
              + ("  ** OVER LOAD LIMIT: the tail is not loaded **"
                 if n_lines > MEMORY_LINE_LIMIT or n_bytes > MEMORY_BYTE_LIMIT else ""))
        linked = re.findall(r"\]\(([^)]+\.md)\)", raw)
    else:
        print("MEMORY.md: missing")
    for f in sorted(set(linked) - set(files)):
        print(f"DANGLING index link (no file): {f}")
    for f in sorted(set(files) - set(linked)):
        print(f"ORPHAN file (not in index, never loaded via index): {f}")

    names = {f[:-3] for f in files}
    texts = {f: open(os.path.join(mdir, f), encoding="utf-8").read() for f in files}
    names |= {parse_frontmatter(t).get("name", "") for t in texts.values()}
    for f, t in texts.items():
        for link in sorted(set(re.findall(r"\[\[([^\]|#]+)", t))):
            if link.strip() not in names:
                print(f"DANGLING [[{link}]] in {f}")

    # Only tool calls count: MEMORY.md itself is injected into every session,
    # so a plain text search would match every file in every session.
    reads = {f: 0 for f in files}
    writes = {f: 0 for f in files}
    pdir = project_dir(args)
    for s in list_sessions(pdir, args.last) if os.path.isdir(pdir) else []:
        seen_r, seen_w = set(), set()
        for r in records(s["path"]):
            content = (r.get("message") or {}).get("content")
            if r.get("type") != "assistant" or not isinstance(content, list):
                continue
            for b in content:
                if b.get("type") != "tool_use":
                    continue
                inp = json.dumps(b.get("input"), ensure_ascii=False)
                target = seen_w if b.get("name") in ("Write", "Edit", "MultiEdit") else seen_r
                target.update(f for f in files if f in inp)
        for f in seen_r:
            reads[f] += 1
        for f in seen_w:
            writes[f] += 1

    print(f"\n{'file':48} {'modified':10} {'bytes':>6} {'read':>4} {'wrote':>5}  type / missing frontmatter")
    for f in files:
        p = os.path.join(mdir, f)
        fm = parse_frontmatter(texts[f])
        missing = [k for k in ("name", "description") if k not in fm]
        mtime = dt.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%d")
        print(f"{f:48} {mtime:10} {os.path.getsize(p):>6} {reads[f]:>4} {writes[f]:>5}  "
              f"{fm.get('type', '?')}{'  missing: ' + ','.join(missing) if missing else ''}")
    print(f"\nread/wrote = sessions among the last {args.last} whose tool calls opened/edited the file")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", help="project working directory (default: cwd)")
    ap.add_argument("--project-dir", help="transcript folder, overrides --project")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        # Also accepted after the subcommand; SUPPRESS keeps a value given
        # before the subcommand from being reset to None.
        p.add_argument("--project", default=argparse.SUPPRESS, help="project working directory (default: cwd)")
        p.add_argument("--project-dir", default=argparse.SUPPRESS, help="transcript folder, overrides --project")
        return p

    common(sub.add_parser("where")).set_defaults(fn=cmd_where)
    p = common(sub.add_parser("sessions"))
    p.add_argument("--last", type=int, default=20)
    p.add_argument("--since", help="ISO date; only sessions active since then")
    p.set_defaults(fn=cmd_sessions)
    p = common(sub.add_parser("digest"))
    p.add_argument("session", nargs="+", help="session id (prefix ok) or .jsonl path")
    p.add_argument("--subagents", action="store_true", help="also digest subagent transcripts")
    p.add_argument("--max-chars", type=int, default=60000)
    p.set_defaults(fn=cmd_digest)
    p = common(sub.add_parser("memstat"))
    p.add_argument("--memory-dir", help="override the memory folder")
    p.add_argument("--last", type=int, default=20)
    p.set_defaults(fn=cmd_memstat)

    args = ap.parse_args()
    try:
        args.fn(args)
        sys.stdout.flush()
    except BrokenPipeError:
        # Output piped into head/grep -m: the reader left early, which is fine.
        # Point stdout at devnull so the interpreter's exit flush doesn't raise
        # again (https://docs.python.org/3/library/signal.html#note-on-sigpipe).
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(1)


if __name__ == "__main__":
    main()
