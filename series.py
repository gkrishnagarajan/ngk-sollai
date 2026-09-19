#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Statutory section series formatter.

  பிரிவுகள் 341 294(b) 323 324 506(ii) ஆகியவற்றின்
    -> பிரிவுகள் 341, 294(b), 323, 324 மற்றும் 506(ii) ஆகியவற்றின்

Deliberately narrow: fires ONLY between a section opener (பிரிவு/பிரிவுகள்)
and a terminator (ஆகியவற்றின்/ஆகியவை/கீழ்). This keeps it away from
measurements and reference numbers, where commas would be wrong.
"""
import re

ENABLED = True

OPENER = r"(\u0BAA\u0BBF\u0BB0\u0BBF\u0BB5\u0BC1(?:\u0B95\u0BB3\u0BCD)?)"
TERM   = r"(\u0B86\u0B95\u0BBF\u0BAF\u0BB5\u0BB1\u0BCD\u0BB1\u0BBF\u0BA9\u0BCD|\u0B86\u0B95\u0BBF\u0BAF\u0BB5\u0BC8|\u0B95\u0BC0\u0BB4\u0BCD|\u0B86\u0B95)"
ITEM   = r"\d+(?:\([a-zA-Z0-9]+\)|[-][A-Za-z])?"
MATRUM = "\u0BAE\u0BB1\u0BCD\u0BB1\u0BC1\u0BAE\u0BCD"

def format_series(text):
    out, changes = text, []
    pat = re.compile(OPENER + r"((?:\s+" + ITEM + r"){2,})(\s*(?:" + MATRUM + r")?\s*)(" + ITEM + r")?\s*" + TERM)

    def _s(m):
        opener = m.group(1)
        body   = m.group(2).split()
        tail   = m.group(4)
        term   = m.group(5)
        items  = body + ([tail] if tail else [])
        if len(items) < 2:
            return m.group(0)
        if len(items) == 2:
            joined = items[0] + " " + MATRUM + " " + items[1]
        else:
            joined = ", ".join(items[:-1]) + " " + MATRUM + " " + items[-1]
        new = opener + " " + joined + " " + term
        changes.append({"wrong": m.group(0).strip(), "correct": new,
                        "category": "series_sections", "source": "series"})
        return new

    out = pat.sub(_s, out)
    # Also handle uppercase Roman: 506(II) -> 506(ii), 304(I) -> 304(i)
    pat2 = re.compile(r'(?<!\d)(304|506)\s*\((I{1,2})\)')
    def _s2(m):
        sec, rom = m.group(1), m.group(2).lower()
        new2 = "%s(%s)" % (sec, rom)
        if new2 == m.group(0): return m.group(0)
        changes.append({"wrong": m.group(0), "correct": new2,
                        "category": "section_citation", "source": "series"})
        return new2
    out = pat2.sub(_s2, out)
    return out, changes


def format_commaed(text):
    """Already-commaed series: last comma -> மற்றும்
       294(b), 341, 323, 324, 506(ii) ஆகிய -> ... 324 மற்றும் 506(ii) ஆகிய"""
    out, changes = text, []
    pat = re.compile(r"((?:" + ITEM + r",\s*){2,})(" + ITEM + r"),\s*(" + ITEM + r")\s*(?=" + TERM + r"|\u0B86\u0B95\u0BBF\u0BAF)")
    def _s(m):
        new = m.group(1) + m.group(2) + " " + MATRUM + " " + m.group(3) + " "
        changes.append({"wrong": m.group(0).strip(), "correct": new.strip(),
                        "category": "series_matrum", "source": "series"})
        return new
    out = pat.sub(_s, out)
    return out, changes


# Sections whose parts are UNNUMBERED in the statute; courts cite them
# with lowercase roman by convention. Verified against IPC bare act.
#   IPC 304 -> two punishment limbs (intention / knowledge)
#   IPC 506 -> general and aggravated criminal intimidation
UNNUMBERED_PART_SECTIONS = {"304", "506"}

_ROMAN = {"1": "i", "2": "ii"}

def unnumbered_part_sections(text):
    """304(2) -> 304(ii), 506(2) -> 506(ii). Leaves every other section alone."""
    out, changes = text, []
    pat = re.compile(r"(?<!\d)(\d{3})\s*\((\d)\)")
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
    # Handle uppercase Roman: 506(II)->506(ii), 304(I)->304(i)
    pat2 = re.compile(r"(?<!\d)(304|506)\s*\((I{1,2})\)")
    def _s2(m):
        sec, rom = m.group(1), m.group(2).lower()
        new2 = "%s(%s)" % (sec, rom)
        if new2 == m.group(0): return m.group(0)
        changes.append({"wrong": m.group(0), "correct": new2,
                        "category": "section_citation", "source": "series"})
        return new2
    out = pat2.sub(_s2, out)
    return out, changes




def add_section_commas(text):
    """Add commas between consecutive section numbers.
    294(b) 353 189 மற்றும் 506(ii) -> 294(b), 353, 189 மற்றும் 506(ii)
    Only fires between section numbers (digits with optional brackets).
    Does NOT fire before மணி/மணிக்கு (time expressions).
    """
    import re
    out, changes = text, []
    
    # Pattern: section_number SPACE section_number (not followed by மற்றும் or மணி)
    pat = re.compile(r'(\d+(?:\([a-zA-Z0-9]+\))?)\s+(?!மற்றும்)(?!மணிக்கு)(?!மணி)(\d+(?:\([a-zA-Z0-9]+\))?)')
    
    prev = None
    while True:
        new_out = pat.sub(lambda m: m.group(1) + ', ' + m.group(2), out)
        if new_out == out:
            break
        changes.append({"wrong": out, "correct": new_out,
                       "category": "section_commas", "source": "series"})
        out = new_out
    
    return out, changes

def fix_malformed_sections(text):
    """Fix malformed section numbers:
    506.ii) -> 506(ii)
    294..) -> 294(b)   [.. means missing letter]
    353.189 -> 353, 189
    """
    import re
    out, changes = text, []

    # Fix 506.ii) or 294.b) -> 506(ii), 294(b)
    pat = re.compile(r'(\d{3})\.([ivxab]+)\)')
    def _fix(m):
        new = "%s(%s)" % (m.group(1), m.group(2))
        changes.append({"wrong": m.group(0), "correct": new,
                        "category": "section_fix", "source": "series"})
        return new
    out = pat.sub(_fix, out)

    # Fix 294..) -> 294(b)  [corrupted bracket with dots]
    pat2 = re.compile(r'(\d{3})\.\.\)')
    def _fix2(m):
        new = "%s(b)" % m.group(1)
        changes.append({"wrong": m.group(0), "correct": new,
                        "category": "section_fix", "source": "series"})
        return new
    out = pat2.sub(_fix2, out)

    # Fix 353.189 (section number dot section number) -> 353, 189
    pat3 = re.compile(r'(\d{3})\.(\d{3})(?=\s)')
    def _fix3(m):
        new = "%s, %s" % (m.group(1), m.group(2))
        changes.append({"wrong": m.group(0), "correct": new,
                        "category": "section_fix", "source": "series"})
        return new
    out = pat3.sub(_fix3, out)

    return out, changes



def normalise_sub_clause(text):
    """Normalise sub-clause citations:
    F உட்பிரிவு G  -> F(G)   where F=1-700, G=1-100
    F சப்கிளாஸ் G  -> F(G)   (and variants)
    F சப் கிளாஸ் G -> F(G)
    F சப்கிலாஸ் G  -> F(G)
    F சப் கிலாஸ் G -> F(G)
    F சப்களாஸ் G   -> F(G)
    """
    import re
    out, changes = text, []

    # உட்பிரிவு variant
    pat1 = re.compile(
        r'(?<!\d)([1-9][0-9]{0,2}),?\s+உட்பிரிவு\s+([1-9][0-9]{0,2})(?!\d)'
    )
    def _r1(m):
        f, g = m.group(1), m.group(2)
        if int(f) > 700 or int(g) > 100: return m.group(0)
        new = "%s(%s)" % (f, g)
        changes.append({"wrong": m.group(0), "correct": new,
                        "category": "section_citation", "source": "series"})
        return new
    out = pat1.sub(_r1, out)

    # உட்கூறு variant (506/304 only, sub-clauses i and ii)
    _UTKURU_ROM = {'1': 'i', '2': 'ii'}
    pat_utkuru = re.compile(
        r'(?<!(\d))(304|506),?\s+உட்(?:கூறு|டுக்கூறு|கூரு)\s+([12])(?!\d)'
    )
    def _r_utkuru(m):
        sec, g = m.group(2), m.group(3)
        rom = _UTKURU_ROM.get(g)
        if not rom: return m.group(0)
        new = '%s(%s)' % (sec, rom)
        changes.append({'wrong': m.group(0), 'correct': new,
                        'category': 'section_citation', 'source': 'series'})
        return new
    out = pat_utkuru.sub(_r_utkuru, out)

   # சப் கிளாஸ் / சப்கிளாஸ் / சப்கிலாஸ் / சப் கிலாஸ் / சப்களாஸ் variants
    pat2 = re.compile(
        r'(?<!\d)([1-9][0-9]{0,2})\s+(?:சப்\s*கி[ளல]ாஸ்|சப்\s*க[ளல]ாஸ்|சப்கிளாஸ்|சப்கிலாஸ்|சப்களாஸ்)\s+([1-9][0-9]{0,2})(?!\d)'
    )
    def _r2(m):
        f, g = m.group(1), m.group(2)
        if int(f) > 700 or int(g) > 100: return m.group(0)
        new = "%s(%s)" % (f, g)
        changes.append({"wrong": m.group(0), "correct": new,
                        "category": "section_citation", "source": "series"})
        return new
    out = pat2.sub(_r2, out)

    return out, changes

if __name__ == "__main__":
    tests = [
      "\u0B87\u0BA8\u0BCD\u0BA4\u0BBF\u0BAF \u0BA4\u0BA3\u0BCD\u0B9F\u0BA9\u0BC8\u0B9A\u0BCD \u0B9A\u0B9F\u0BCD\u0B9F\u0BAE\u0BCD \u0BAA\u0BBF\u0BB0\u0BBF\u0BB5\u0BC1\u0B95\u0BB3\u0BCD 341 294(b) 323 324 506(ii) \u0B86\u0B95\u0BBF\u0BAF\u0BB5\u0BB1\u0BCD\u0BB1\u0BBF\u0BA9\u0BCD \u0B95\u0BC0\u0BB4\u0BCD",
      "\u0BAA\u0BBF\u0BB0\u0BBF\u0BB5\u0BC1\u0B95\u0BB3\u0BCD 341 \u0BAE\u0BB1\u0BCD\u0BB1\u0BC1\u0BAE\u0BCD 294(b) \u0B86\u0B95\u0BBF\u0BAF\u0BB5\u0BB1\u0BCD\u0BB1\u0BBF\u0BA9\u0BCD",
      "82 \u0B9A\u0BC6\u0BA9\u0BCD\u0B9F\u0BBF\u0BAE\u0BC0\u0B9F\u0BCD\u0B9F\u0BB0\u0BCD \u0BA8\u0BC0\u0BB3\u0BAE\u0BC1\u0BAE\u0BCD 14 \u0B9A\u0BC6\u0BA9\u0BCD\u0B9F\u0BBF\u0BAE\u0BC0\u0B9F\u0BCD\u0B9F\u0BB0\u0BCD",
    ]
    for t in tests:
        o, c = format_series(t)
        print(("CHANGED " if c else "unchanged") + "  " + o)

# ---------------------------------------------------------------------------
# normalise_uttpiruvu_prose  — added 2026-09-03
# Converts:  <N> உட்பிரிவு <M|word-numeral> [-ன்/-இன்]? கீழ்
#         →  <N>(<M>)-ன் கீழ்
# ---------------------------------------------------------------------------
import re as _re

_WORD_TO_DIGIT = {
    "ஒன்று": 1, "ஒன்றின்": 1, "ஒண்றின்": 1, "ஒன்னின்": 1,
    "இரண்டு": 2, "இரண்டின்": 2, "இரன்டின்": 2, "இரண்டீன்": 2,
    "மூன்று": 3, "மூன்றின்": 3, "மூன்னின்": 3, "மூன்றீன்": 3,
    "நான்கு": 4, "நான்கின்": 4, "நான்கீன்": 4, "நாங்கின்": 4,
    "ஐந்து": 5, "ஐந்தின்": 5, "அஐந்தின்": 5, "ஐந்தீன்": 5,
    "ஆறு": 6, "ஆறின்": 6, "ஆரின்": 6, "ஆறீன்": 6,
    "ஏழு": 7, "ஏழின்": 7, "ஏழீன்": 7, "யேழின்": 7,
    "எட்டு": 8, "எட்டின்": 8, "எட்டீன்": 8, "எடின்": 8,
    "ஒன்பது": 9, "ஒன்பதின்": 9, "ஒன்பதீன்": 9, "ஒம்பதின்": 9,
    "பத்து": 10, "பத்தின்": 10, "பத்தீன்": 10, "பதின்": 10,
    "பதினொன்று": 11, "பதினொன்றின்": 11, "பதினொன்னின்": 11,
    "பன்னிரண்டு": 12, "பன்னிரண்டின்": 12, "பன்னிரன்டின்": 12,
    "பதின்மூன்று": 13, "பதின்மூன்றின்": 13, "பதின்மூன்னின்": 13,
    "பதினான்கு": 14, "பதினான்கின்": 14, "பதினாங்கின்": 14,
    "பதினைந்து": 15, "பதினைந்தின்": 15, "பதினைந்தீன்": 15,
    "பதினாறு": 16, "பதினாறின்": 16, "பதினாரின்": 16,
    "பதினேழு": 17, "பதினேழின்": 17, "பதினேழீன்": 17,
    "பதினெட்டு": 18, "பதினெட்டின்": 18, "பதினெடின்": 18,
    "பத்தொன்பது": 19, "பத்தொன்பதின்": 19, "பத்தொம்பதின்": 19,
    "இருபது": 20, "இருபதின்": 20, "இருபதீன்": 20,
    "இருபத்தொன்று": 21, "இருபத்தொன்றின்": 21, "இருபத்தொன்னின்": 21,
    "இருபத்திரண்டு": 22, "இருபத்திரண்டின்": 22, "இருபத்திரன்டின்": 22,
    "இருபத்திமூன்று": 23, "இருபத்திமூன்றின்": 23, "இருபத்திமூன்னின்": 23,
    "இருபத்தினான்கு": 24, "இருபத்தினான்கின்": 24, "இருபத்திநாங்கின்": 24,
    "இருபத்தைந்து": 25, "இருபத்தைந்தின்": 25, "இருபத்தைந்தீன்": 25,
    "இருபத்தாறு": 26, "இருபத்தாறின்": 26, "இருபத்தாரின்": 26,
    "இருபத்தேழு": 27, "இருபத்தேழின்": 27, "இருபத்தேழீன்": 27,
    "இருபத்தெட்டு": 28, "இருபத்தெட்டின்": 28, "இருபத்தெடின்": 28,
    "இருபத்தொன்பது": 29, "இருபத்தொன்பதின்": 29, "இருபத்தொம்பதின்": 29,
    "முப்பது": 30, "முப்பதின்": 30, "முப்பதீன்": 30,
    "முப்பத்தொன்று": 31, "முப்பத்தொன்றின்": 31, "முப்பத்தொன்னின்": 31,
    "முப்பத்திரண்டு": 32, "முப்பத்திரண்டின்": 32, "முப்பத்திரன்டின்": 32,
    "முப்பத்திமூன்று": 33, "முப்பத்திமூன்றின்": 33, "முப்பத்திமூன்னின்": 33,
    "முப்பத்தினான்கு": 34, "முப்பத்தினான்கின்": 34, "முப்பத்திநாங்கின்": 34,
    "முப்பத்தைந்து": 35, "முப்பத்தைந்தின்": 35, "முப்பத்தைந்தீன்": 35,
    "முப்பத்தாறு": 36, "முப்பத்தாறின்": 36, "முப்பத்தாரின்": 36,
    "முப்பத்தேழு": 37, "முப்பத்தேழின்": 37, "முப்பத்தேழீன்": 37,
    "முப்பத்தெட்டு": 38, "முப்பத்தெட்டின்": 38, "முப்பத்தெடின்": 38,
    "முப்பத்தொன்பது": 39, "முப்பத்தொன்பதின்": 39, "முப்பத்தொம்பதின்": 39,
    "நாற்பது": 40, "நாற்பதின்": 40, "நாற்பதீன்": 40,
    "நாற்பத்தொன்று": 41, "நாற்பத்தொன்றின்": 41, "நாற்பத்தொன்னின்": 41,
    "நாற்பத்திரண்டு": 42, "நாற்பத்திரண்டின்": 42, "நாற்பத்திரன்டின்": 42,
    "நாற்பத்திமூன்று": 43, "நாற்பத்திமூன்றின்": 43, "நாற்பத்திமூன்னின்": 43,
    "நாற்பத்தினான்கு": 44, "நாற்பத்தினான்கின்": 44, "நாற்பத்திநாங்கின்": 44,
    "நாற்பத்தைந்து": 45, "நாற்பத்தைந்தின்": 45, "நாற்பத்தைந்தீன்": 45,
    "நாற்பத்தாறு": 46, "நாற்பத்தாறின்": 46, "நாற்பத்தாரின்": 46,
    "நாற்பத்தேழு": 47, "நாற்பத்தேழின்": 47, "நாற்பத்தேழீன்": 47,
    "நாற்பத்தெட்டு": 48, "நாற்பத்தெட்டின்": 48, "நாற்பத்தெடின்": 48,
    "நாற்பத்தொன்பது": 49, "நாற்பத்தொன்பதின்": 49, "நாற்பத்தொம்பதின்": 49,
    "ஐம்பது": 50, "ஐம்பதின்": 50, "ஐம்பதீன்": 50,
}

_WORD_ALT = "|".join(
    _re.escape(w) for w in sorted(_WORD_TO_DIGIT, key=len, reverse=True)
)

_UTTPIRUVU_RE = _re.compile(
    r"(\d+)\s+உட்பிரிவு\s+(" + _WORD_ALT + r"|\d+)\s*-?(?:ன்|இன்)?\s+கீழ்",
    _re.UNICODE,
)

# Bare form — no கீழ் suffix: பிரிவு 82 உட்பிரிவு 3 -> 82(3)
_UTTPIRUVU_BARE_RE = _re.compile(
    r"(\d+)\s+உட்பிரிவு\s+(" + _WORD_ALT + r"|\d+)"
    r"(?!\s*-?(?:ன்|இன்)?\s*கீழ்)",
    _re.UNICODE,
)

def _uttpiruvu_bare_replace(m):
    sec = m.group(1)
    sub_raw = m.group(2)
    sub = sub_raw if sub_raw.isdigit() else str(_WORD_TO_DIGIT.get(sub_raw, sub_raw))
    return f"{sec}({sub})"

def _uttpiruvu_replace(m):
    sec = m.group(1)
    sub_raw = m.group(2)
    sub = sub_raw if sub_raw.isdigit() else str(_WORD_TO_DIGIT.get(sub_raw, sub_raw))
    return f"{sec}({sub})-ன் கீழ்"

def normalise_uttpiruvu_prose(text):
    """Convert prose sub-section references to citation form.
    '223 உட்பிரிவு ஒன்றின் கீழ்'  -> '223(1)-ன் கீழ்'
    '4 உட்பிரிவு 5 ன் கீழ்'       -> '4(5)-ன் கீழ்'
    """
    new_text = _UTTPIRUVU_RE.sub(_uttpiruvu_replace, text)
    new_text = _UTTPIRUVU_BARE_RE.sub(_uttpiruvu_bare_replace, new_text)
    return new_text, new_text != text
