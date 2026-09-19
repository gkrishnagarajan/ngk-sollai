#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
abbr_norm.py — Voiced English Abbreviation Normaliser
Converts voice-typed Tamil phonetic letter sequences to dotted English abbreviations.
Example: கே எஸ் ஆர் கல்லூரி → K.S.R. கல்லூரி

Pattern: 2–5 consecutive Tamil-voiced English letters (space-separated)
         followed by an institution trigger word.

Pipeline position: after vehicle_reg_norm, before whitespace.
"""

import re

# Tamil phonetic → English letter mapping
# Each Tamil form maps to its English letter
LETTER_MAP = {
    "ஏ":          "A",
    "பி":         "B",
    "சி":         "C",
    "டி":         "T",   # T is primary (NIT, IIT etc.); D voiced as டீ/டே
    "டீ":         "D",
    "டே":         "D",
    "இ":          "E",
    "எஃப்":       "F",
    "எஃப":        "F",
    "ஜி":         "G",
    "எச்":        "H",
    "எச":         "H",
    "ஐ":          "I",
    "ஜே":         "J",
    "கே":         "K",
    "எல்":        "L",
    "எல":         "L",
    "எம்":        "M",
    "எம":         "M",
    "என்":        "N",
    "என":         "N",
    "ஓ":          "O",
    "பீ":         "P",   # variant of பி
    "கியூ":       "Q",
    "ஆர்":        "R",
    "ஆர":         "R",
    "எஸ்":        "S",
    "எஸ":         "S",
    "டீ":         "T",   # variant
    "யூ":         "U",
    "வி":         "V",
    "டபிள்யூ":    "W",
    "டபிள்யு":    "W",
    "எக்ஸ்":      "X",
    "எக்ஸ":       "X",
    "ஒய்":        "Y",
    "ஒய":         "Y",
    "ஜட்":        "Z",
    "ஜட":         "Z",
}

# Institution trigger words — abbreviation must precede one of these
INSTITUTION_TRIGGERS = [
    "கல்லூரி",
    "பல்கலைக்கழகம்",
    "பல்கலைக்கழகத்தில்",
    "பல்கலைக்கழகத்தின்",
    "நிறுவனம்",
    "மருத்துவமனை",
    "மருத்துவமனையில்",
    "பள்ளி",
    "பள்ளியில்",
    "வங்கி",
    "நீதிமன்றம்",
    "அரசு",
    "திட்டம்",
    "சங்கம்",
    "மையம்",
]

# Build sorted letter list longest-first for greedy matching
_SORTED_LETTERS = sorted(LETTER_MAP.keys(), key=len, reverse=True)

# Regex: one Tamil-voiced letter token
_LETTER_PAT = "(?:" + "|".join(re.escape(k) for k in _SORTED_LETTERS) + ")"

# Full pattern: 2–5 letter tokens (space-separated) followed by trigger word
_TRIGGER_PAT = "(?:" + "|".join(re.escape(t) for t in INSTITUTION_TRIGGERS) + ")"
_ABB_RE = re.compile(
    r"(" + _LETTER_PAT + r"(?:\s+" + _LETTER_PAT + r"){1,4})"
    r"(\s+)"
    r"(" + _TRIGGER_PAT + r")"
)


def _convert_sequence(seq_str):
    """Convert space-separated Tamil letter sequence to dotted English abbreviation."""
    tokens = seq_str.split()
    letters = []
    for tok in tokens:
        # Try longest match first
        matched = False
        for key in _SORTED_LETTERS:
            if tok == key:
                letters.append(LETTER_MAP[key])
                matched = True
                break
        if not matched:
            return None  # unknown token — abort conversion
    return ".".join(letters) + "."


def normalise_abbreviations(text):
    """
    Normalise voiced English letter sequences before institution trigger words.
    Returns (corrected_text, changes_list).
    """
    changes = []
    result = text

    def replacer(m):
        seq, space, trigger = m.group(1), m.group(2), m.group(3)
        abbr = _convert_sequence(seq)
        if abbr is None:
            return m.group(0)  # no match — leave unchanged
        corrected = abbr + " " + trigger
        original  = seq + space + trigger
        if corrected != original:
            changes.append({
                "wrong":    original,
                "correct":  corrected,
                "category": "voiced_english_abbreviation",
                "source":   "abbr_norm",
            })
        return corrected

    result = _ABB_RE.sub(replacer, result)
    return result, changes


# ── Spot-checks when run directly ────────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        ("கே எஸ் ஆர் கல்லூரியில் படித்து வந்தார்",
         "K.S.R. கல்லூரியில் படித்து வந்தார்"),
        ("எஸ் எஸ் எல் சி பள்ளியில் படித்தார்",
         "S.S.L.C. பள்ளியில் படித்தார்"),
        ("எம் பி பி எஸ் மருத்துவமனையில்",
         "M.B.B.S. மருத்துவமனையில்"),
        ("என் ஐ டி கல்லூரி",
         "N.I.T. கல்லூரி"),
        ("பி எஸ் என் எல் வங்கி",
         "B.S.N.L. வங்கி"),
        # Safety: non-letter Tamil words must not fire
        ("அந்த கல்லூரியில் படித்தார்",
         "அந்த கல்லூரியில் படித்தார்"),
    ]
    print("Spot-checks:")
    all_pass = True
    for text, expected in tests:
        out, _ = normalise_abbreviations(text)
        st = "PASS" if out == expected else "FAIL"
        if st == "FAIL":
            all_pass = False
        print(f"  [{st}] {text!r}")
        if st == "FAIL":
            print(f"         expected: {expected!r}")
            print(f"         got:      {out!r}")
    print("\nAll PASSED" if all_pass else "\nSome FAILED")
