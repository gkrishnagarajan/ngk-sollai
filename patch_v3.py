# -*- coding: utf-8 -*-
"""Adds v3 comma rules to punctuation.py. Run from ~/tamil_reformulator."""
import io, sys

p = 'punctuation.py'
s = io.open(p, encoding='utf-8').read()

if 'add_clause_commas' not in s:
    print("ERROR: v2 patch not applied yet. Run the v2 patch first.")
    sys.exit(1)

if 'PARTICIPLE_COMMA' in s:
    print("v3 already present")
    sys.exit(0)

add = '''

# --- v3: participle and clause-final commas (from marked-up judgment) ---
# Only fire when the NEXT word starts a new clause, to avoid mid-clause commas.
PARTICIPLE_COMMA = [
    "\\u0B8F\\u0BB1\\u0BCD\\u0BAA\\u0B9F\\u0BC1\\u0BA4\\u0BCD\\u0BA4\\u0BBF",   # ஏற்படுத்தி
    "\\u0B8E\\u0B9F\\u0BC1\\u0BA4\\u0BCD\\u0BA4\\u0BC1",                        # எடுத்து
    "\\u0BA4\\u0BCA\\u0B9F\\u0BB0\\u0BCD\\u0B9A\\u0BCD\\u0B9A\\u0BBF\\u0BAF\\u0BBE\\u0B95",  # தொடர்ச்சியாக
]

# words that legitimately follow these participles WITHOUT a comma
_NO_COMMA_NEXT = {
    "\\u0BAE\\u0BB1\\u0BCD\\u0BB1\\u0BC1\\u0BAE\\u0BCD",      # மற்றும்
    "\\u0B85\\u0BA4\\u0BC1",                                   # அது
}

def add_participle_commas(text):
    out, changes = text, []
    for w in PARTICIPLE_COMMA:
        pat = re.compile(r"(?<![\\u0B80-\\u0BFF])" + re.escape(w) +
                         r"(?![\\u0B80-\\u0BFF,])(\\s+)([\\u0B80-\\u0BFF]+)")
        def _s(m):
            nxt = m.group(2)
            if nxt in _NO_COMMA_NEXT:
                return m.group(0)
            changes.append({"wrong": w, "correct": w + ",",
                            "category": "punct_participle_comma",
                            "source": "punctuation"})
            return w + "," + m.group(1) + nxt
        out = pat.sub(_s, out)

    # -தாகவும் / -ளதாகவும் before மேலும்  ->  comma
    pat = re.compile(r"([\\u0B80-\\u0BFF]+\\u0BA4\\u0BBE\\u0B95\\u0BB5\\u0BC1\\u0BAE\\u0BCD)"
                     r"(?![,\\u0B80-\\u0BFF])(?=\\s)")
    def _s2(m):
        changes.append({"wrong": m.group(1), "correct": m.group(1) + ",",
                        "category": "punct_clause_comma", "source": "punctuation"})
        return m.group(1) + ","
    out = pat.sub(_s2, out)
    return out, changes
'''

old = '''        out, c = add_clause_commas(out); changes += c'''
new = '''        out, c = add_clause_commas(out); changes += c
        out, c = add_participle_commas(out); changes += c'''

s = s.replace("def apply_punctuation", add + "\ndef apply_punctuation", 1)
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print("v3 comma rules added")
