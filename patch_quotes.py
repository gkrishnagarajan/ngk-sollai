# -*- coding: utf-8 -*-
"""Add opening-quote insertion after reporting verbs. Run in ~/tamil_reformulator."""
import io, sys
p='punctuation.py'
s=io.open(p,encoding='utf-8').read()

if 'REPORTING_VERBS' in s:
    print("already present"); sys.exit(0)

add = '''

# --- opening quote after a reporting verb, paired with an existing closer ---
REPORTING_VERBS = [
    "\\u0BA8\\u0BBF\\u0BB1\\u0BC1\\u0BA4\\u0BCD\\u0BA4\\u0BBF",              # நிறுத்தி
    "\\u0B95\\u0BBE\\u0BA3\\u0BCD\\u0BAA\\u0BBF\\u0BA4\\u0BCD\\u0BA4\\u0BC1", # காண்பித்து
    "\\u0B95\\u0BC2\\u0BB1\\u0BBF",                                          # கூறி
    "\\u0B9A\\u0BCA\\u0BB2\\u0BCD\\u0BB2\\u0BBF",                            # சொல்லி
    "\\u0BA4\\u0BBF\\u0B9F\\u0BCD\\u0B9F\\u0BBF",                            # திட்டி
    "\\u0BAE\\u0BBF\\u0BB0\\u0B9F\\u0BCD\\u0B9F\\u0BBF",                     # மிரட்டி
    "\\u0B95\\u0BA4\\u0BCD\\u0BA4\\u0BBF",                                   # கத்தி
]

def add_open_quotes(text):
    """For every closing quote, open one after the nearest preceding
    reporting verb. Only fires when that verb is found and no quote is
    already open, so it fails by omission rather than misplacement."""
    out, changes = text, []
    idx = 0
    while True:
        c = out.find('"', idx)
        if c == -1:
            break
        before = out[:c]
        if before.count('"') % 2 == 1:      # already paired
            idx = c + 1
            continue
        best = -1; bestv = None
        for v in REPORTING_VERBS:
            j = before.rfind(v + " ")
            if j > best:
                best, bestv = j, v
        if best == -1:
            idx = c + 1
            continue
        ins = best + len(bestv) + 1
        out = out[:ins] + '"' + out[ins:]
        changes.append({"wrong": bestv, "correct": bestv + ' "',
                        "category": "punct_quote_open", "source": "punctuation"})
        idx = c + 2
    return out, changes
'''

old = "    if quotes:\n        out, c = add_quotes(out); changes += c"
new = "    if quotes:\n        out, c = add_quotes(out); changes += c\n        out, c = add_open_quotes(out); changes += c"

s = s.replace("def apply_punctuation", add + "\ndef apply_punctuation", 1)
if old in s:
    s = s.replace(old, new, 1)
else:
    # fallback: append call at end of apply_punctuation body
    s = s.replace("    return out, changes\n\n\nif __name__",
                  "    out, c = add_open_quotes(out); changes += c\n    return out, changes\n\n\nif __name__", 1)
io.open(p,'w',encoding='utf-8').write(s)
print("opening-quote rule added")
