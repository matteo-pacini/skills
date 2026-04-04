#!/usr/bin/env python3
"""Fetch YouTube video transcripts for the youtube-qa skill."""

import argparse
import re
import sys
from urllib.parse import parse_qs, urlparse

try:
    from youtube_transcript_api import (
        AgeRestricted,
        IpBlocked,
        NoTranscriptFound,
        RequestBlocked,
        TranscriptsDisabled,
        VideoUnavailable,
        VideoUnplayable,
        YouTubeTranscriptApi,
    )
except ImportError:
    print(
        "Error: youtube-transcript-api is not installed.\n"
        "Install it with: pip install youtube-transcript-api",
        file=sys.stderr,
    )
    sys.exit(1)


def extract_video_id(url_or_id: str) -> str:
    """Extract a YouTube video ID from various URL formats or a bare ID."""
    url_or_id = url_or_id.strip()

    # Bare video ID (11 chars, alphanumeric + hyphens + underscores)
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url_or_id):
        return url_or_id

    # Add scheme if missing so urlparse works
    if not url_or_id.startswith(("http://", "https://")):
        url_or_id = "https://" + url_or_id

    parsed = urlparse(url_or_id)
    host = parsed.hostname or ""

    # youtu.be/ID
    if host in ("youtu.be", "www.youtu.be"):
        video_id = parsed.path.lstrip("/").split("/")[0]
        if re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
            return video_id

    # youtube.com variants
    if host in ("youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"):
        # /watch?v=ID
        if parsed.path == "/watch":
            qs = parse_qs(parsed.query)
            if "v" in qs:
                video_id = qs["v"][0]
                if re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
                    return video_id

        # /embed/ID, /shorts/ID, /live/ID, /v/ID
        match = re.match(r"^/(?:embed|shorts|live|v)/([A-Za-z0-9_-]{11})", parsed.path)
        if match:
            return match.group(1)

    raise ValueError(
        f"Could not extract a YouTube video ID from: {url_or_id}\n"
        "Supported formats: youtube.com/watch?v=ID, youtu.be/ID, "
        "youtube.com/embed/ID, youtube.com/shorts/ID, or a bare 11-character video ID."
    )


def format_timestamp(seconds: float, use_hours: bool) -> str:
    """Format seconds into [M:SS] or [H:MM:SS]."""
    total = int(seconds)
    h, remainder = divmod(total, 3600)
    m, s = divmod(remainder, 60)
    if use_hours:
        return f"[{h}:{m:02d}:{s:02d}]"
    return f"[{m}:{s:02d}]"


def format_transcript(snippets: list, video_id: str, language_info: str) -> str:
    """Merge snippets into timestamped paragraphs (~30s intervals)."""
    if not snippets:
        return f"Transcript for {video_id} ({language_info}): (empty)\n"

    last_end = snippets[-1].start + snippets[-1].duration
    use_hours = last_end >= 3600

    lines = [f"Transcript for {video_id} ({language_info}):\n"]

    current_text = []
    last_ts = 0.0
    ts_interval = 30.0

    for snippet in snippets:
        # Insert timestamp marker at intervals
        if not current_text or (snippet.start - last_ts) >= ts_interval:
            if current_text:
                lines.append(" ".join(current_text))
                current_text = []
            ts = format_timestamp(snippet.start, use_hours)
            current_text.append(ts)
            last_ts = snippet.start

        # Clean up text: collapse internal newlines into spaces
        text = snippet.text.replace("\n", " ").strip()
        if text:
            current_text.append(text)

    if current_text:
        lines.append(" ".join(current_text))

    # Total duration
    duration_ts = format_timestamp(last_end, use_hours)
    lines.append(f"\nTotal duration: {duration_ts.strip('[]')}")

    return "\n".join(lines)


def cmd_fetch(args: argparse.Namespace) -> None:
    video_id = extract_video_id(args.url)
    languages = [l.strip() for l in args.lang.split(",")] if args.lang else ["en"]

    api = YouTubeTranscriptApi()

    if args.translate:
        # Fetch in source language, then translate
        transcript_list = api.list(video_id)
        transcript = transcript_list.find_transcript(languages)
        if not transcript.is_translatable:
            print(
                f"Error: The {transcript.language} transcript is not translatable.",
                file=sys.stderr,
            )
            sys.exit(1)
        translated = transcript.translate(args.translate)
        result = translated.fetch()
        language_info = f"language: {args.translate}, translated from {transcript.language}"
    else:
        result = api.fetch(video_id, languages=languages)
        # Determine language info from the transcript list
        try:
            transcript_list = api.list(video_id)
            matched = transcript_list.find_transcript(languages)
            lang_label = matched.language
            if matched.is_generated:
                lang_label += ", auto-generated"
            language_info = f"language: {lang_label}"
        except Exception:
            language_info = f"language: {languages[0]}"

    snippets = list(result)
    print(format_transcript(snippets, video_id, language_info))


def cmd_list(args: argparse.Namespace) -> None:
    video_id = extract_video_id(args.url)
    api = YouTubeTranscriptApi()
    transcript_list = api.list(video_id)

    print(f"Available transcripts for {video_id}:\n")
    for t in transcript_list:
        flags = []
        if t.is_generated:
            flags.append("auto-generated")
        else:
            flags.append("manual")
        if t.is_translatable:
            flags.append("translatable")
        flags_str = ", ".join(flags)
        print(f"  {t.language_code:<8} {t.language} ({flags_str})")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch YouTube video transcripts.",
        prog="fetch_transcript.py",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # fetch
    fetch_parser = subparsers.add_parser("fetch", help="Fetch a video transcript")
    fetch_parser.add_argument("url", help="YouTube URL or video ID")
    fetch_parser.add_argument(
        "--lang",
        default="en",
        help="Language code(s), comma-separated in priority order (default: en)",
    )
    fetch_parser.add_argument(
        "--translate",
        default=None,
        help="Translate transcript to this language code",
    )

    # list
    list_parser = subparsers.add_parser("list", help="List available transcript languages")
    list_parser.add_argument("url", help="YouTube URL or video ID")

    args = parser.parse_args()

    try:
        if args.command == "fetch":
            cmd_fetch(args)
        elif args.command == "list":
            cmd_list(args)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except TranscriptsDisabled:
        print(
            "Error: Transcripts are disabled for this video.\n"
            "The video owner has turned off captions.",
            file=sys.stderr,
        )
        sys.exit(1)
    except NoTranscriptFound:
        print(
            "Error: No transcript found in the requested language.\n"
            "Run with the 'list' command to see available languages.",
            file=sys.stderr,
        )
        # Try to list available languages as a hint
        try:
            video_id = extract_video_id(args.url)
            api = YouTubeTranscriptApi()
            transcript_list = api.list(video_id)
            print("\nAvailable languages:", file=sys.stderr)
            for t in transcript_list:
                label = "auto-generated" if t.is_generated else "manual"
                print(f"  {t.language_code}: {t.language} ({label})", file=sys.stderr)
        except Exception:
            pass
        sys.exit(1)
    except (RequestBlocked, IpBlocked):
        print(
            "Error: YouTube blocked the request (IP-based restriction).\n"
            "This can happen in cloud environments. Try again later or from a different network.",
            file=sys.stderr,
        )
        sys.exit(1)
    except AgeRestricted:
        print(
            "Error: This video is age-restricted.\n"
            "Transcripts cannot be fetched for age-restricted content.",
            file=sys.stderr,
        )
        sys.exit(1)
    except (VideoUnavailable, VideoUnplayable):
        print(
            "Error: This video is unavailable.\n"
            "It may have been deleted, made private, or is region-restricted.",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
