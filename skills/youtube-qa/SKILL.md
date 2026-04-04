---
name: youtube-qa
description: >
  Fetch YouTube video transcripts and answer questions about video content.
  Use this skill whenever the user shares a YouTube URL or video link and wants
  to understand, summarize, or ask questions about the video. Also trigger when
  the user mentions "YouTube transcript", "video transcript", "what does this
  video say", or wants to extract information from a YouTube video.
  Supports youtube.com, youtu.be, and all YouTube URL formats.
  Do NOT use for non-YouTube video platforms (Vimeo, TikTok, etc.).
---

# YouTube Q&A

Fetch YouTube video transcripts and answer questions about the video content.

## Prerequisites

The `youtube-transcript-api` Python package must be installed. If the script fails with an import error, tell the user to install it:

- **With nix-shell**: `nix-shell -p 'python3.withPackages (ps: [ ps.youtube-transcript-api ])'`
- **With pip**: `pip install youtube-transcript-api`

## Running the Script

Check if `nix-shell` is available on the system. If it is, use it to run the script:

```bash
nix-shell -p 'python3.withPackages (ps: [ ps.youtube-transcript-api ])' --run "python3 ${SKILL_DIR}/scripts/fetch_transcript.py fetch <url>"
```

Otherwise, fall back to plain Python (requires the package to already be installed):

```bash
python3 ${SKILL_DIR}/scripts/fetch_transcript.py fetch <url>
```

## Workflow

1. **Extract the YouTube URL** from the user's message. Supported formats:
   - `youtube.com/watch?v=ID`
   - `youtu.be/ID`
   - `youtube.com/embed/ID`, `/shorts/ID`, `/live/ID`
   - `m.youtube.com/watch?v=ID`
   - Bare 11-character video ID

2. **Fetch the transcript** using the appropriate run method above.
   Add `--lang <code>` if the user requests a specific language (e.g., `--lang es`).
   Add `--translate <code>` to translate the transcript to a different language.

3. **If the fetch fails**, read the error message:
   - **No transcript in requested language**: Run the `list` command to show available languages (same run method, replace `fetch` with `list`).
     Then re-fetch with the appropriate `--lang` flag, or use `--translate` if the user wants a specific output language.
   - **Transcripts disabled**: Tell the user that the video owner has disabled captions.
   - **Import error**: Tell the user to install the package.
   - **Other errors**: Relay the error message clearly.

4. **Answer the user's question** based on the transcript. If no specific question was asked, provide a brief summary and invite questions.

## Answering Questions

Answer in your own words based on what the transcript says. Keep it concise and natural.

- **Do not include timestamps** unless the user explicitly asks for them.
- **Do not quote the transcript** unless the user explicitly asks for quotes.
- **Skip ads, sponsor reads, and promotional segments** — focus only on the actual content of the video.
- **For summary requests**: Provide a clear, structured overview of the main points. Use the Pareto Principle mindset — focus on the content that matters most.
- **For specific questions**: Answer directly based on what the speaker said.
- **Auto-generated transcripts** may contain errors — especially with technical terms, proper nouns, and non-native speakers. Use judgment to correct obvious transcription mistakes silently.

## Language Handling

- The script defaults to English (`en`).
- Pass `--lang <code>` for other languages. Multiple codes can be comma-separated in priority order: `--lang es,en` tries Spanish first, falls back to English.
- Use `--translate <code>` to translate a transcript into a different language using YouTube's built-in translation (only works if the source transcript is marked as translatable).

## Error Reference

| Error | Meaning | What to tell the user |
|---|---|---|
| Import error | Package not installed | Run `pip install youtube-transcript-api` |
| Transcripts disabled | Video owner turned off captions | No transcript available for this video |
| No transcript found | Language not available | Show available languages, suggest alternatives |
| Request/IP blocked | YouTube rate limiting | Try again later or from a different network |
| Age restricted | Login required | Cannot fetch transcript for age-restricted videos |
| Video unavailable | Deleted/private/region-locked | Video cannot be accessed |
