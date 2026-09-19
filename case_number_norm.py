#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
case_number_norm.py
Normalises voice-typed case/crime number separators.
  "குற்ற எண். 259 ரூபாய் 2021" → "குற்ற எண். 259/2021"
  "C.C. 45 ஆண்டு 2019"         → "C.C. 45/2019"
Pattern: <digits> <mishear_word> <4-digit-year>
"""
import re

ENABLED = True

# Separator mishears — words voice-typing substitutes for "/"
_MISHEARS = (
    r'பார்',      # பார் — slash mishear in FIR numbers
    r'ஆப்',       # ஆப் — slash mishear variant
    r'ரூபாய்',   # rupees — most common slash mishear
    r'ஆண்டு',    # year
    r'புள்ளி',   # dot/point
    r'சாய்வு',   # slash (literal transliteration)
    r'இல்',      # locative — "259-இல் 2021"
    r'ஆம்',      # ordinal connector
    r'slash',    # English word spoken
    r'SLASH',
    r'/',        # already correct but with spaces: "259 / 2021"
)

_SEP_PAT = re.compile(
    r'(\d+)\s+(?:' + '|'.join(_MISHEARS) + r')\s+(\d{4})\b'
)

# Also normalise "259 / 2021" (spaced slash) → "259/2021"
_SPACED_SLASH = re.compile(r'(\d+)\s*/\s*(\d{4})\b')

def normalise(text):
    out, changes = text, []

    new = _SEP_PAT.sub(lambda m: f"{m.group(1)}/{m.group(2)}", out)
    if new != out:
        changes.append({
            'wrong': 'case_number_separator_mishear',
            'correct': 'normalised',
            'category': 'spelling',
            'source': 'case_number_norm',
        })
        out = new

    new = _SPACED_SLASH.sub(lambda m: f"{m.group(1)}/{m.group(2)}", out)
    if new != out:
        changes.append({
            'wrong': 'spaced_slash_in_case_number',
            'correct': 'normalised',
            'category': 'spelling',
            'source': 'case_number_norm',
        })
        out = new

    return out, changes
