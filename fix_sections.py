#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remove the general roman_subsection converter and replace it with an
explicit, section-specific one.

Reason: IPC/BNS/BNSS all number sub-sections in ARABIC -- sub-section (1),
(2), (3). Roman numerals are a court CITATION CONVENTION used only for
sections whose parts are unnumbered in the statute (304 and 506).
A general digit->roman rule would wrongly rewrite 376(2), 354(3), etc.

Run from ~/tamil_reformulator.
"""
import io, os, re, sys

# ---------- 1. strip the general converter from series.py ----------
p = 'series.py'
if os.path.exists(p):
    s = io.open(p, encoding='utf-8').read()
    if 'def roman_subsection' in s:
        start = s.index('_ROMAN =') if '_ROMAN =' in s else s.index('def roman_subsection')
        end = s.find('\n\nif __name__', start)
        if end == -1:
            end = len(s)
        s = s[:start] + s[end:]
        io.open(p, 'w', encoding='utf-8').write(s)
        print("series.py: removed general roman_subsection")
    else:
        print("series.py: no general converter present")

# ---------- 2. add explicit, section-specific converter ----------
s = io.open(p, encoding='utf-8').read()
if 'unnumbered_part_sections' not in s:
    add = '''

# Sections whose parts are UNNUMBERED in the statute; courts cite them
# with lowercase roman by convention. Verified against IPC bare act.
#   IPC 304 -> two punishment limbs (intention / knowledge)
#   IPC 506 -> general and aggravated criminal intimidation
UNNUMBERED_PART_SECTIONS = {"304", "506"}

_ROMAN = {"1": "i", "2": "ii"}

def unnumbered_part_sections(text):
    """304(2) -> 304(ii), 506(2) -> 506(ii). Leaves every other section alone."""
    out, changes = text, []
    pat = re.compile(r"(?<!\\d)(\\d{3})\\s*\\((\\d)\\)")
    def _s(m):
        sec, num = m.group(1), m.group(2)
        if sec not in UNNUMBERED_PART_SECTIONS:
            return m.group(0)
        r = _ROMAN.get(num)
        if not r:
            return m.group(0)
        new = "%s(%s)" % (sec, r)
        changes.append({"wrong": m.group(0), "correct": new,
                        "category": "section_citation", "source": "series"})
        return new
    out = pat.sub(_s, out)
    return out, changes
'''
    s = s.replace('\n\nif __name__', add + '\n\nif __name__', 1) if '\n\nif __name__' in s else s + add
    io.open(p, 'w', encoding='utf-8').write(s)
    print("series.py: added unnumbered_part_sections")

# ---------- 3. rewire the app ----------
p2 = 'app_integrated.py'
s2 = io.open(p2, encoding='utf-8').read()
s2 = s2.replace('from series import format_series, format_commaed, roman_subsection',
                'from series import format_series, format_commaed, unnumbered_part_sections')
s2 = s2.replace('_os, _c3 = roman_subsection(_os)',
                '_os, _c3 = unnumbered_part_sections(_os)')
if 'unnumbered_part_sections' not in s2:
    # never wired at all -- add it alongside format_commaed
    s2 = s2.replace('from series import format_series, format_commaed',
                    'from series import format_series, format_commaed, unnumbered_part_sections', 1)
    s2 = s2.replace('        _os, _c2 = format_commaed(_os)\n        _cs = list(_cs) + _c2',
                    '        _os, _c2 = format_commaed(_os)\n        _os, _c3 = unnumbered_part_sections(_os)\n        _cs = list(_cs) + _c2 + _c3', 1)
io.open(p2, 'w', encoding='utf-8').write(s2)
print("app_integrated.py: rewired")

# ---------- 4. drop conflicting flat rules from the store ----------
import json, glob
CONFLICT = {"506(2)", "506 (2)", "506(1)", "506 (1)",
            "304(2)", "304 (2)", "304(1)", "304 (1)"}
removed = 0
for f in sorted(glob.glob("tamil_rules_*.json")):
    d = json.load(open(f, encoding="utf-8"))
    n = len(d["rules"])
    d["rules"] = [r for r in d["rules"] if r["wrong"] not in CONFLICT]
    if len(d["rules"]) != n:
        d["count"] = len(d["rules"])
        json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        removed += n - len(d["rules"])
print("removed %d duplicate flat section rules (pattern handles them now)" % removed)
