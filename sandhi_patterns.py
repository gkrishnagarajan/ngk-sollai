#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sandhi pattern engine: வல்லினம் மிகுதல் for closed compound families.

One pattern replaces many enumerated pairs. A pattern fires only when the
SECOND word belongs to a known family, so we never have to classify the
first word in general -- that is what keeps this safe.

Safety features:
  1. EXCEPTIONS are checked first and always win.
  2. Only families listed in ENABLED are applied.
  3. Each family carries its own doubling consonant.
"""
import re

# family head-word -> doubling consonant to insert before it
FAMILIES = {
    "சான்றிதழ்": "ச்",
    "சாட்சி":    "ச்",
    "பத்திரம்":  "ப்",
    "பட்டியல்":  "ப்",
    "தொகை":     "த்",
    "தடை":      "த்",
    "கட்டணம்":  "க்",
}

# Only these run. Add one at a time, test, then add the next.
ENABLED = {"சான்றிதழ்", "பத்திரம்"}

# pair-level overrides: exact joined form -> exact correct form.
# Checked BEFORE patterns; use for compounds that must not double.
EXCEPTIONS = {}

# stems that must NOT take doubling for a given family
BLOCK = {
    "சான்றிதழ்": set(),
    "பத்திரம்": {"உயில்"},
}

def _head_variants(head):
    """joined form and space-separated form both need matching"""
    return [head]



# --- name suffixes that always join to the preceding name element ---
NAME_SUFFIX = ["\u0B95\u0BC1\u0BAE\u0BBE\u0BB0\u0BCD"]   # குமார்

def apply_name_join(text):
    """பிரகாஷ் குமார் -> பிரகாஷ்குமார்  (also inflected: குமாரின், குமாரை ...)"""
    out, changes = text, []
    for suf in NAME_SUFFIX:
        pat = re.compile(r"(?<![\u0B80-\u0BFF])([\u0B80-\u0BFF]{2,})\s+("
                         + re.escape(suf) + r"[\u0B80-\u0BFF]*)")
        def _s(m):
            joined = m.group(1) + m.group(2)
            changes.append({"wrong": m.group(0), "correct": joined,
                            "category": "name_join", "source": "sandhi_patterns"})
            return joined
        out = pat.sub(_s, out)
    return out, changes

def apply_sandhi(text, enabled=None):
    """Return (corrected_text, changes)."""
    enabled = ENABLED if enabled is None else set(enabled)
    changes = []
    out = text

    # 1) exceptions first
    for wrong, right in EXCEPTIONS.items():
        pat = r"(?<!\w)" + re.escape(wrong) + r"(?!\w)"
        if re.search(pat, out):
            out = re.sub(pat, right, out)
            changes.append({"wrong": wrong, "correct": right,
                            "category": "sandhi_exception", "source": "EXCEPTIONS"})

    # 2) family patterns
    for head in enabled:
        if head not in FAMILIES:
            continue
        dbl = FAMILIES[head]
        blocked = BLOCK.get(head, set())

        # (a) fully joined:  மருத்துவசான்றிதழ்  ->  மருத்துவச் சான்றிதழ்
        # (b) plain spaced:  மருத்துவ சான்றிதழ் ->  மருத்துவச் சான்றிதழ்
        for sep in ("", " "):
            pat = re.compile(r"(?<!\w)([\u0B80-\u0BFF]{2,})" + sep + re.escape(head) + r"(?!\w)")
            def _sub(m):
                stem = m.group(1)
                if stem in blocked:
                    return m.group(0)
                if stem.endswith(dbl):            # already correct
                    return m.group(0)
                if stem.endswith("\u0BCD"):        # ends in pure consonant: no doubling
                    return m.group(0)
                new = stem + dbl + " " + head
                changes.append({"wrong": m.group(0), "correct": new,
                                "category": "sandhi_" + head, "source": "pattern"})
                return new
            out = pat.sub(_sub, out)

    return out, changes


if __name__ == "__main__":
    tests = [
        "மருத்துவசான்றிதழ் தாக்கல் செய்யப்பட்டது.",
        "வருமான சான்றிதழ் கோரப்பட்டது.",
        "பிறப்புசான்றிதழ் மற்றும் இறப்புசான்றிதழ் இணைக்கப்பட்டன.",
        "மருத்துவச் சான்றிதழ் ஏற்கனவே சரியானது.",
        "திருமணசான்றிதழ் நகல் வழங்கப்பட்டது.",
        "அடையாளசான்றிதழ் சரிபார்க்கப்பட்டது.",
    ]
    for t in tests:
        o, ch = apply_sandhi(t)
        flag = "CHANGED" if ch else "unchanged"
        print("[%s] %s" % (flag, t))
        if ch:
            print("        -> %s" % o)
