#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

ENABLED = True

CARD = {
 "ஒன்று":1,"இரண்டு":2,"மூன்று":3,"நான்கு":4,"ஐந்து":5,"ஆறு":6,"ஏழு":7,
 "எட்டு":8,"ஒன்பது":9,"பத்து":10,"பதினொன்று":11,"பன்னிரண்டு":12,
 "பதின்மூன்று":13,"பதிநான்கு":14,"பதினான்கு":14,"பதினைந்து":15,
 "பதினாறு":16,"பதினேழு":17,"பதினெட்டு":18,"பத்தொன்பது":19,"இருபது":20,
 "இருபத்தொன்று":21,"இருபத்திரண்டு":22,"இருபத்துமூன்று":23,"இருபத்துநான்கு":24,
 "இருபத்தைந்து":25,"இருபத்தாறு":26,"இருபத்தேழு":27,"இருபத்தெட்டு":28,
 "இருபத்தொன்பது":29,"முப்பது":30,"முப்பத்தொன்று":31,
 "முப்பத்தைந்து":35,"நாற்பது":40,"நாற்பத்தைந்து":45,"ஐம்பது":50,
 "ஐம்பத்தைந்து":55,
}
CARD.update({
 "\u0BA8\u0BBE\u0BB2\u0BC1":4,"\u0B85\u0B9E\u0BCD\u0B9A\u0BC1":5,
 "\u0BAE\u0BC2\u0BA3\u0BCD\u0B9F\u0BC1":3,"\u0BB0\u0BC6\u0BA3\u0BCD\u0B9F\u0BC1":2,
 "\u0B92\u0BA3\u0BCD\u0BA3\u0BC1":1,"\u0B8E\u0BB4\u0BC1":7,"\u0B8E\u0B9F\u0BCD\u0B9F\u0BC1":8,
 "\u0B92\u0BA9\u0BCD\u0BAA\u0BA4\u0BC1":9,"\u0BAA\u0BA4\u0BCD\u0BA4\u0BC1":10,
 "\u0BAA\u0BA9\u0BCD\u0BA9\u0BC6\u0BB0\u0BA3\u0BCD\u0B9F\u0BC1":12,
})

ORD = {
 "முதலாம்":1,"முதல்":1,"இரண்டாம்":2,"மூன்றாம்":3,"நான்காம்":4,"ஐந்தாம்":5,
 "ஆறாம்":6,"ஏழாம்":7,"எட்டாம்":8,"ஒன்பதாம்":9,"பத்தாம்":10,
 "பதினொன்றாம்":11,"பன்னிரண்டாம்":12,"பதின்மூன்றாம்":13,"பதினான்காம்":14,
 "பதினைந்தாம்":15,"பதினாறாம்":16,"பதினேழாம்":17,"பதினெட்டாம்":18,
 "பத்தொன்பதாம்":19,"இருபதாம்":20,"இருபத்தொன்றாம்":21,"இருபத்திரண்டாம்":22,
 "இருபத்துமூன்றாம்":23,"இருபத்துநான்காம்":24,"இருபத்தைந்தாம்":25,
 "இருபத்தாறாம்":26,"இருபத்தேழாம்":27,"இருபத்தெட்டாம்":28,
 "இருபத்தொன்பதாம்":29,"முப்பதாம்":30,"முப்பத்தொன்றாம்":31,
}

MONTH = {
 "ஜனவரி":1,"பிப்ரவரி":2,"பெப்ரவரி":2,"மார்ச்":3,"ஏப்ரல்":4,"மே":5,
 "ஜூன்":6,"ஜுன்":6,"ஜூலை":7,"ஜுலை":7,"ஆகஸ்ட்":8,"ஆகஸ்டு":8,
 "செப்டம்பர்":9,"அக்டோபர்":10,"நவம்பர்":11,"டிசம்பர்":12,
}

DAY_WORDS = {
 "ஒன்று":1,"இரண்டு":2,"மூன்று":3,"நான்கு":4,"ஐந்து":5,"ஆறு":6,"ஏழு":7,
 "எட்டு":8,"ஒன்பது":9,"பத்து":10,"பதினொன்று":11,"பன்னிரண்டு":12,
 "பதின்மூன்று":13,"பதினான்கு":14,"பதினைந்து":15,"பதினாறு":16,
 "பதினேழு":17,"பதினெட்டு":18,"பத்தொன்பது":19,"இருபது":20,
 "இருபத்தொன்று":21,"இருபத்திரண்டு":22,"இருபத்துமூன்று":23,
 "இருபத்துநான்கு":24,"இருபத்தைந்து":25,"இருபத்தாறு":26,
 "இருபத்தேழு":27,"இருபத்தெட்டு":28,"இருபத்தொன்பது":29,
 "முப்பது":30,"முப்பத்தொன்று":31,
}

_ORD_ALT   = "|".join(sorted(ORD, key=len, reverse=True))
_CARD_ALT  = "|".join(sorted(CARD, key=len, reverse=True))
_MON_ALT   = "|".join(sorted(MONTH, key=len, reverse=True))
_DAY_ALT   = "|".join(sorted(DAY_WORDS, key=len, reverse=True))

TETHI   = "தேதி"
MANI    = "மணி"
NIMIDAM = "நிமிடம்"
SUF     = "-ஆம் தேதியன்று"
SUF_M   = "-ம் தேதி"

def normalise(text):
    out, changes = text, []

    def rec(orig, new, kind):
        changes.append({"wrong": orig, "correct": new,
                        "category": "datetime_" + kind, "source": "datetime_norm"})

    # 0) Numeric time with space: 12 45 மணி -> 12.45 மணி
    def _num_time(m):
        s = "%s.%s மணி" % (m.group(1), m.group(2))
        rec(m.group(0), s, "time_numeric"); return s
    out = re.sub(r'\b(\d{1,2})\s+(\d{2})\s+மணி', _num_time, out)

    # 0b) கடந்த <day_word> <month_digit> <year> -> கடந்த d.mm.yyyy-ம் தேதி
    #     e.g. கடந்த இரண்டு 10 2022-ம் தேதி -> கடந்த 2.10.2022-ம் தேதி
    pat_word_date = re.compile(
        r'கடந்த\s+(' + _DAY_ALT + r')\s+(\d{1,2})\s+(\d{4})(?:\s*-?ம்)?(?:\s*தேதி)?'
    )
    def _word_date(m):
        d  = DAY_WORDS[m.group(1)]
        mo = int(m.group(2))
        yr = m.group(3)
        s  = "கடந்த %d.%02d.%s%s" % (d, mo, yr, SUF_M)
        rec(m.group(0), s, "date_word"); return s
    out = pat_word_date.sub(_word_date, out)

    # 1) ordinal day + month + 4-digit year -> dd.mm.yyyy-ஆம் தேதியன்று
    pat = re.compile(r"(?<![\u0B80-\u0BFF])(" + _ORD_ALT + r")\s+(" + _MON_ALT +
                     r")\s+(\d{4})(\s+\u0B85\u0BA9\u0BCD\u0BB1\u0BC1)?")
    def _full(m):
        d = "%02d.%02d.%s%s" % (ORD[m.group(1)], MONTH[m.group(2)], m.group(3), SUF)
        rec(m.group(0), d, "date"); return d
    out = pat.sub(_full, out)

    # 1a) digits present: 12.03.2024 அன்று -> 12.03.2024-ஆம் தேதியன்று
    pat = re.compile(r"(\d{2}\.\d{2}\.\d{4})\s+\u0B85\u0BA9\u0BCD\u0BB1\u0BC1")
    def _dig(m):
        s = m.group(1) + SUF
        rec(m.group(0), s, "date"); return s
    out = pat.sub(_dig, out)

    # 1b) numeric variants — skip if already normalized
    TAIL = r"(?:\s*-?ஆம்\s*தேதியன்று|\s*-?ம்\s*தேதி|\s*அன்று)?"
    pat = re.compile(r"(?<!\d)(\d{1,2})[\s./-](\d{1,2})[\s/.-](\d{4})" + TAIL)
    def _num(m):
        full = m.group(0)
        if "தேதியன்று" in full or "தேதி" in full:
            return full
        s2 = "%02d.%02d.%s%s" % (int(m.group(1)), int(m.group(2)), m.group(3), SUF)
        rec(full.strip(), s2, "date"); return s2
    out = pat.sub(_num, out)

    # 1c) digit day + word month-number + year (27 நாலு 2019)
    _CW = "|".join(sorted(CARD, key=len, reverse=True))
    TL = r"(?:\s*-?ஆம்)?(?:\s*தேதி)?(?:\s*அன்று)?"
    pat = re.compile(r"(?<!\d)(\d{1,2}|" + _CW + r")\s+(" + _CW + r")\s+(\d{4})" + TL)
    def _mix(m):
        full = m.group(0)
        if "தேதியன்று" in full or "தேதி" in full:
            return full
        a, b = m.group(1), m.group(2)
        d = int(a) if a.isdigit() else CARD.get(a, 0)
        mo = CARD.get(b, 0)
        if not d or not mo or mo > 12:
            return full
        s2 = "%02d.%02d.%s%s" % (d, mo, m.group(3), SUF)
        rec(full.strip(), s2, "date"); return s2
    out = pat.sub(_mix, out)

    # 2) time with minutes: <card> மணி <card> நிமிடம் -> h.mm மணி
    pat = re.compile(r"(?<![\u0B80-\u0BFF])(" + _CARD_ALT + r")\s+" + MANI +
                     r"\s+(" + _CARD_ALT + r")\s+" + NIMIDAM)
    def _hm(m):
        s = "%d.%02d %s" % (CARD[m.group(1)], CARD[m.group(2)], MANI)
        rec(m.group(0), s, "time"); return s
    out = pat.sub(_hm, out)

    # 3) bare hour: <card> மணி -> h மணி
    pat = re.compile(r"(?<![\u0B80-\u0BFF])(" + _CARD_ALT + r")\s+" + MANI)
    def _h(m):
        s = "%d %s" % (CARD[m.group(1)], MANI)
        rec(m.group(0), s, "hour"); return s
    out = pat.sub(_h, out)

    # 4) ordinal day alone -> dd-ஆம் தேதி
    pat = re.compile(r"(?<![\u0B80-\u0BFF])(" + _ORD_ALT + r")\s+" + TETHI)
    def _d(m):
        s = "%d-ஆம் %s" % (ORD[m.group(1)], TETHI)
        rec(m.group(0), s, "day"); return s
    out = pat.sub(_d, out)

    return out, changes


if __name__ == "__main__":
    tests = [
      "பன்னிரண்டாம் தேதி விசாரணை நடந்தது.",
      "பன்னிரண்டாம் மார்ச் 2024 அன்று சம்பவம் நிகழ்ந்தது.",
      "இரவு ஒன்பது மணி அளவில் நடந்தது.",
      "மாலை ஏழு மணி பதினைந்து நிமிடம் அளவில்.",
      "இருபத்தைந்தாம் ஆகஸ்ட் 2025 அன்று தாக்கல்.",
      "முதலாம் தேதி உத்தரவு பிறப்பிக்கப்பட்டது.",
      "நீதிமன்றம் விசாரணையை தொடங்கியது.",
      "பகல் 12 45 மணி முதல் 12 55 மணி வரை சாலை மறியல்.",
      "கடந்த இரண்டு 10 2022-ம் தேதி வெள்ளார் கிராமத்தில்.",
      "மாலை 6 30 மணி அளவில் நடந்தது.",
    ]
    for t in tests:
        o, ch = normalise(t)
        print(("CHANGED  " if ch else "unchanged") + "  " + t)
        if ch:
            print("          -> " + o)
