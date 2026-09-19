#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Postposition government detector.

Tamil postpositions require a particular case on the preceding noun.
This module DETECTS violations and SUGGESTS a fix. It does not rewrite,
because forming the case marker correctly needs the noun's declension
class, and a wrong guess produces confidently malformed Tamil.

Output: list of flags. Wire into the app as warnings, not corrections.
"""
import re

TA = "\u0B80-\u0BFF"

# postposition -> (required case label, marker test, human hint)
# பற்றி requires accusative -ஐ on the preceding noun.
# Recognised accusative endings: ஐ, ஐப், களை, யை, தை, னை, ணை, லை, ரை
GOVERN = {
    "பற்றி": ("accusative", ("ஐ", "ஐப்", "களை", "யை", "தை", "னை", "ணை", "லை", "ரை"), "-ஐ + பற்றி"),
}

# postpositions that take the bare/nominative form -- never flag them
NO_CASE = {
    "மூலம்", "வரை", "உடன்", "ஆக",
    "குறித்து", "எதிராக", "பிறகு", "முன்",
    "முன்னால்", "பின்னால்", "மேல்", "கீழ்",
    "அடிப்படையில்", "தொடர்பாக", "நோக்கி",
    "ஏற்ப",
}

def check_postpositions(text):
    """Return list of flags. Never modifies text."""
    flags = []
    words = re.findall(r"[" + TA + r"]+|[^\s]+", text)
    for i, w in enumerate(words):
        if w not in GOVERN or i == 0:
            continue
        prev = words[i-1]
        case, markers, hint = GOVERN[w]
        stripped = re.sub(r"[கசதப]\u0BCD$", "", prev)  # drop sandhi tail
        import re as _re
        _VD = _re.compile(r'[஀-௿](?:தற்கு|வதற்கு|றதற்கு|ததற்கு|அதற்கு)$')
        if case == 'dative' and _VD.search(prev):
            continue
        if any(prev.endswith(m) or stripped.endswith(m) for m in markers):
            continue
        flags.append({
            "type": "POSTPOSITION_CASE",
            "postposition": w,
            "noun": prev,
            "required": case,
            "phrase": prev + " " + w,
            "hint": hint,
            "severity": "MEDIUM",
        })
    return flags


if __name__ == "__main__":
    tests = [
        "நபர்களை பற்றி விவரங்கள் தெரிவிக்கவில்லை.",
        "வழக்கை பற்றி சாட்சியம் அளித்தார்.",
        "கட்டளை பிறகு வழக்கு ஒத்திவைக்கப்பட்டது.",
        "பத்திரம் மூலம் வாங்கினார்.",
    ]
    for t in tests:
        fl = check_postpositions(t)
        print(("FLAG " if fl else "ok   ") + t)
        for f in fl:
            print("        %s  (needs %s)" % (f["phrase"], f["hint"]))
