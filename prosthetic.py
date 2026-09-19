#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prosthetic இ before word-initial ர / ரா.

Tamil does not natively allow word-initial ர. Common words and loanwords
take a prosthetic இ, but ONLY when the initial syllable is ர (ra) or ரா (raa).
Words beginning ரி ரீ ரு ரூ ரெ ரே ரை ரொ ரோ ரௌ are left unchanged.

PROPER NOUN RULE (two-pass):
Pass 1: Scan entire text. Any ர-word followed by a Tamil name-marker
        (என்பவர், என்ற, என்னும் etc.) is added to a session block.
Pass 2: Apply prosthetic இ, skipping all session-blocked words.

ADDITIONAL BLOCKS:
1. Words ending in ு — typical Tamil proper noun name pattern (ராமு, ராஜு).
2. English loanwords in Tamil script — identified by loanword-typical endings.
"""
import re

_BLOCKING_SIGNS = "\u0BBF\u0BC0\u0BC1\u0BC2\u0BC6\u0BC7\u0BC8\u0BCA\u0BCB\u0BCC\u0BCD"
_ELIGIBLE = re.compile(
    r"(?<![\u0B80-\u0BFF])(?<!\u0B87)\u0BB0(?![" + _BLOCKING_SIGNS + r"])"
)

BLOCK = set()

_NAME_U_ENDING = re.compile(r"^[\u0B80-\u0BFF]+\u0BC1$")

_LOANWORD_ENDING = re.compile(
    r"(?:\u0B9F\u0BCD\u0B9F\u0BC1|\u0BB0\u0BCD\u0B9F\u0BC1|\u0BB2\u0BCD\u0B9F\u0BC1|\u0BA3\u0BCD\u0B9F\u0BC1|\u0BA9\u0BCD\u0B9F\u0BC1|\u0BB0\u0BCD\u0B9F\u0BCD|\u0BB2\u0BCD\u0B9F\u0BCD)$"
)

_NAME_MARKERS = [
    "என்பவர்", "என்பவரை", "என்பவரிடம்", "என்பவரிடமிருந்து",
    "என்பவரையும்", "என்பவரும்", "என்பவரின்", "என்பவருக்கு",
    "என்பவரால்", "என்பவருடன்", "என்பவரே",
    "என்ற", "என்னும்", "என்கிற", "ஆகியோர்",
]

_NAME_MARKER_PAT = re.compile(
    r"[\u0B80-\u0BFF\s]{0,40}?(?:" +
    "|".join(re.escape(m) for m in _NAME_MARKERS) +
    r")"
)

def _is_proper_noun_context(text, start, word):
    after = text[start + len(word): start + len(word) + 200]
    return bool(_NAME_MARKER_PAT.search(after))

def _is_blocked_by_heuristic(word):
    if _NAME_U_ENDING.match(word):
        return True
    if _LOANWORD_ENDING.search(word):
        return True
    return False

def apply_prosthetic(text):
    session_block = set(BLOCK)
    for m in _ELIGIBLE.finditer(text):
        start = m.start()
        tail = re.match(r"[\u0B80-\u0BFF]+", text[start:])
        word = tail.group(0) if tail else text[start:start+1]
        if _is_proper_noun_context(text, start, word):
            session_block.add(word)
        if _is_blocked_by_heuristic(word):
            session_block.add(word)

    changes = []
    def _sub(m):
        start = m.start()
        tail = re.match(r"[\u0B80-\u0BFF]+", text[start:])
        word = tail.group(0) if tail else text[start:start+1]
        if word in session_block:
            return m.group(0)
        changes.append({"wrong": word, "correct": "\u0B87" + word,
                        "category": "prosthetic_i", "source": "pattern"})
        return "\u0B87" + m.group(0)
    out = _ELIGIBLE.sub(_sub, text)
    return out, changes


if __name__ == "__main__":
    tests = [
        ("ரவி என்பவர் வந்தார். மேற்படி ரவி சேலம் சென்றார்.",
         "ரவி என்பவர் வந்தார். மேற்படி ரவி சேலம் சென்றார்.",
         "anaphoric name — no இ"),
        ("ரத்தம் சேர்க்கப்பட்டது. மேற்படி ரத்தம் பரிசோதிக்கப்பட்டது.",
         "இரத்தம் சேர்க்கப்பட்டது. மேற்படி இரத்தம் பரிசோதிக்கப்பட்டது.",
         "common word — both get இ"),
        ("ரூபாய் செலுத்தப்பட்டது.", "ரூபாய் செலுத்தப்பட்டது.", "ரூ blocked"),
        ("ராமு வந்தார்.", "ராமு வந்தார்.", "name ending ு — no இ"),
    ]
    all_ok = True
    for inp, expected, note in tests:
        out, _ = apply_prosthetic(inp)
        ok = out == expected
        if not ok: all_ok = False
        print(("PASS  " if ok else "FAIL  ") + note)
        if not ok:
            print("  got:      " + repr(out[:80]))
            print("  expected: " + repr(expected[:80]))
    print("All OK" if all_ok else "FAILURES above")
