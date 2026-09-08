#!/usr/bin/env python3
"""Flag machine-writing tells in a Markdown or plain-text draft.

Usage: lint.py FILE [FILE ...]   (or read stdin with '-')

Exit status is 1 when any hard flag fires (banned words/phrases, negative
parallelism, more than one em dash, exclamation marks, "**Term**:" lists and
bold lead-in paragraphs), 0 otherwise. Soft flags (rhythm, contractions,
Title Case headings, openers and closers) are advisory, prefixed "~".

Every flag is a default to override deliberately, not proof of anything. The
script reads text, not intent: "landscape" in a piece about gardening is fine.
"""
import re
import statistics
import sys

BANNED_WORDS = [
    "delve", "delves", "delving", "dive into", "dives into", "diving into",
    "navigate", "navigating", "underscore", "underscores", "underscoring",
    "bolster", "bolsters", "bolstering", "foster", "fosters", "fostering",
    "harness", "harnessing", "leverage", "leverages", "leveraging", "unpack",
    "unpacks", "unpacking", "unlock", "unlocks", "unlocking", "shed light on",
    "sheds light on", "pave the way", "paves the way", "paving the way",
    "streamline", "streamlines", "streamlining", "streamlined", "elevate",
    "elevates", "elevating", "empower", "empowers", "empowering", "pivotal",
    "groundbreaking", "cutting-edge", "transformative", "game-changing",
    "game-changer", "game changer", "innovative", "robust", "comprehensive",
    "seamless", "seamlessly", "intricate", "vibrant", "multifaceted",
    "holistic", "testament", "tapestry", "landscape", "realm", "ecosystem",
    "journey", "crucial", "vital", "myriad", "plethora", "meticulous",
    "meticulously", "curated", "bespoke", "actionable", "granular",
    "exciting", "powerful", "incredible", "amazing",
]

# "key" only as an adjective before a noun; "key to the door" is fine.
KEY_ADJ = re.compile(r"\bkey\s+(?:\w+\s+)?(?:role|factor|component|takeaway|takeaways|"
                     r"point|points|insight|insights|area|areas|driver|drivers|part|"
                     r"element|elements|aspect|aspects|feature|features|benefit|"
                     r"benefits|step|steps|player|players|difference|differences)\b", re.I)

LATINATE = {
    "utilise": "use", "utilize": "use", "utilising": "using", "utilizing": "using",
    "facilitate": "help", "facilitates": "helps", "facilitating": "helping",
    "demonstrate": "show", "demonstrates": "shows", "commence": "start",
    "commences": "starts", "purchase": "buy", "sufficient": "enough",
    "additional": "more", "numerous": "many", "obtain": "get", "prior to": "before",
    "in order to": "to", "assist": "help", "implement": "build",
}

BANNED_PHRASES = [
    r"in today'?s (?:\w+[- ])*(?:world|landscape|environment|era|age)",
    r"it'?s (?:important|worth) (?:to note|noting)", r"\bthat said\b",
    r"one of the most (?:important|significant|crucial|critical|powerful)",
    r"when it comes to", r"\bat its core\b", r"at the end of the day",
    r"\bthe reality is\b", r"this is where \w+ comes in", r"let'?s break it down",
    r"let'?s dive in", r"plays? a (?:crucial|vital|key|pivotal|critical) role",
    r"cannot be overstated", r"underscor\w+ the importance",
    r"highlight\w* the need for", r"reflect\w* a broader trend",
    r"mark\w* a significant shift", r"^\s*(?:in conclusion|in summary|ultimately|overall)\b",
    r"^\s*whether you'?re\b", r"^\s*(?:ever wondered|have you ever wondered)",
    r"^\s*what if i told you", r"^\s*as an? \w+, you know",
]

NEGATIVE_PARALLELISM = [
    r"\bnot (?:just|only|merely|simply) \b[^.]{2,80}?\b(?:but|it'?s|it is)\b",
    r"\b(?:isn'?t|is not|wasn'?t|is no longer) (?:just |only )?about \b[^.]{2,80}\.\s+it'?s about\b",
    r"\bit'?s not \b[^.,]{2,60}[,;]\s*it'?s\b",
    r"\bthis isn'?t \b[^.,]{2,60}[,.;]\s*(?:it'?s|this is)\b",
]

BOLD_TERM_LIST = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+\*\*[^*]+\*\*\s*[:–—]", re.M)
# "**Reliability.** Jenkins runs on..." / "**Will we lose history?** Yes." The list
# pattern with the bullet removed; reads as a label, not a sentence.
BOLD_LEAD_IN = re.compile(r"^\*\*[^*\n]{2,80}\*\*[.:?]?\s+[A-Z]", re.M)
HEADING = re.compile(r"^#{1,6}\s+(.+)$", re.M)
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
SMALL_WORDS = {"a", "an", "the", "and", "or", "but", "of", "to", "in", "on", "for",
               "with", "at", "by", "from", "vs", "via", "as", "is"}
CONTRACTIONS = re.compile(r"\b\w+'(?:t|s|re|ve|ll|d|m)\b", re.I)
UNCONTRACTED = re.compile(r"\b(?:do not|does not|did not|is not|are not|was not|were not|"
                          r"cannot|can not|will not|would not|should not|could not|"
                          r"it is|that is|there is|we have|you are|we are|they are|I am)\b", re.I)


def strip_code(text):
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", text)


def paragraphs(text):
    paras = []
    for block in re.split(r"\n\s*\n", text):
        block = block.strip()
        if not block or block.startswith("#") or re.match(r"^\s*(?:[-*+]|\d+\.)\s", block):
            continue
        if block.startswith(("|", ">", "---")):
            continue
        paras.append(" ".join(block.split()))
    return paras


def sentences(para):
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"'(])", para)
    return [p for p in parts if len(p.split()) > 1]


def lint(text):
    hard, soft = [], []
    body = strip_code(text)
    plain = body
    lower = plain.lower()

    for w in BANNED_WORDS:
        for m in re.finditer(r"\b" + re.escape(w) + r"\b", lower):
            ctx = plain[max(0, m.start() - 30):m.end() + 30].replace("\n", " ")
            note = " (fine if literal)" if w in {"navigate", "navigating", "landscape",
                                                 "ecosystem", "journey", "realm"} else ""
            hard.append(f"banned word '{w}'{note}: ...{ctx}...")
    for m in KEY_ADJ.finditer(plain):
        hard.append(f"'key' as adjective: {m.group(0)}")
    for w, alt in LATINATE.items():
        n = len(re.findall(r"\b" + re.escape(w) + r"\b", lower))
        if n:
            soft.append(f"latinate '{w}' x{n}: prefer '{alt}'")

    for pat in BANNED_PHRASES:
        for m in re.finditer(pat, plain, re.I | re.M):
            hard.append(f"banned phrase: '{m.group(0).strip()}'")
    seen = []
    for pat in NEGATIVE_PARALLELISM:
        for m in re.finditer(pat, plain, re.I):
            if any(a <= m.start() < b or m.start() <= a < m.end() for a, b in seen):
                continue
            seen.append((m.start(), m.end()))
            hard.append(f"negative parallelism: '{m.group(0)[:90]}'")

    dashes = plain.count("—") + len(re.findall(r"\s--\s", plain))
    if dashes > 1:
        hard.append(f"{dashes} em dashes (max 1)")
    bangs = plain.count("!")
    if bangs:
        hard.append(f"{bangs} exclamation mark(s)")
    for m in BOLD_TERM_LIST.finditer(plain):
        hard.append(f"'**Term**: explanation' list item: {m.group(0).strip()[:60]}")
    for m in BOLD_LEAD_IN.finditer(plain):
        hard.append(f"bold lead-in paragraph: {m.group(0).strip()[:60]}")

    for m in HEADING.finditer(plain):
        h = m.group(1).strip()
        if EMOJI.search(h):
            hard.append(f"emoji in heading: {h}")
        words = [w for w in re.findall(r"[A-Za-z][\w'-]*", h)]
        # Skip acronyms (CI) and brand casing (GitHub): they're capitalised in any case style.
        plain_words = [w for w in words[1:] if w.lower() not in SMALL_WORDS
                       and not (w.isupper() or re.search(r"[a-z][A-Z]", w))]
        caps = [w for w in plain_words if w[0].isupper()]
        if len(caps) >= 3 and len(caps) * 2 >= len(plain_words):
            soft.append(f"Title Case heading? (proper nouns can trip this): {h}")
    for m in re.finditer(r"^\s*(?:[-*+]|\d+\.)\s+(.*)$", plain, re.M):
        if EMOJI.search(m.group(1)):
            hard.append(f"emoji in list item: {m.group(1)[:60]}")
    if re.search(r"[“”‘’]", plain):
        soft.append("curly quotes present; use straight quotes")

    paras = paragraphs(body)
    all_sents = [s for p in paras for s in sentences(p)]
    lens = [len(s.split()) for s in all_sents]
    runs = 0
    for i in range(len(lens) - 2):
        a, b, c = lens[i:i + 3]
        if max(a, b, c) - min(a, b, c) <= 5 and min(a, b, c) >= 8:
            runs += 1
    if runs:
        soft.append(f"{runs} run(s) of 3 consecutive sentences within 5 words of each other in length")
    if len(lens) >= 6 and statistics.pstdev(lens) < 4:
        soft.append(f"sentence lengths barely vary (stdev {statistics.pstdev(lens):.1f} words)")

    pcounts = [len(sentences(p)) for p in paras]
    if len(pcounts) >= 4 and max(pcounts) - min(pcounts) <= 1:
        soft.append(f"paragraphs all {min(pcounts)}-{max(pcounts)} sentences; vary visibly")
    singles = sum(1 for c in pcounts if c == 1)
    if singles > 3:
        soft.append(f"{singles} one-sentence paragraphs; two or three per piece keeps the effect")

    words = len(re.findall(r"\w+", plain))
    if words > 250:
        c, u = len(CONTRACTIONS.findall(plain)), len(UNCONTRACTED.findall(plain))
        if c == 0 or (u and c / (c + u) < 0.3):
            soft.append(f"few contractions ({c} contracted vs {u} uncontracted)")

    if paras:
        first = sentences(paras[0])[:1]
        if first and re.match(r"^(?:in (?:today|recent|the (?:modern|digital|current))|"
                              r"as (?:organisations|organizations|teams|companies|businesses)|"
                              r"(?:the|our) (?:world|industry|landscape) (?:of|is|has))", first[0], re.I):
            soft.append(f"opening sets a scene: '{first[0][:80]}'")
        last = paras[-1]
        if re.match(r"^(?:in (?:conclusion|summary|short)|to (?:sum up|conclude|summarise|summarize)|"
                    r"ultimately|overall|so,|the (?:bottom line|takeaway))", last, re.I):
            soft.append(f"closing summarises: '{last[:80]}'")
        elif re.search(r"\b(?:future|forward|ahead|next chapter|only the beginning|"
                       r"time will tell|remains to be seen|exciting times)\b", last, re.I):
            soft.append(f"closing may be an uplift/forward-look: '...{last[-80:]}'")

    triads = re.findall(r"\b\w+, \w+,? and \w+\b", plain)
    if len(triads) > 2:
        soft.append(f"{len(triads)} 'X, Y and Z' triads; check each is a fact, not a rhythm")

    stats = f"{words} words, {len(paras)} paragraphs, {len(all_sents)} sentences"
    return hard, soft, stats


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    status = 0
    for path in argv:
        text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
        hard, soft, stats = lint(text)
        print(f"== {path}: {stats}")
        for h in hard:
            print(f"  ! {h}")
        for s in soft:
            print(f"  ~ {s}")
        if not hard and not soft:
            print("  clean")
        if hard:
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
