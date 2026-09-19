#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run sandhi patterns against negative examples. Any change = false positive."""
import json, sys
from sandhi_patterns import apply_sandhi, ENABLED

with open("tamil_negative_examples.json", encoding="utf-8") as fh:
    sents = json.load(fh)["sentences"]

print("enabled families:", ", ".join(sorted(ENABLED)))
fails = []
for s in sents:
    out, ch = apply_sandhi(s)
    if ch:
        fails.append((s, out, ch))

print("tested %d sentences, %d false positive(s)" % (len(sents), len(fails)))
for s, out, ch in fails:
    print("\n  FALSE POSITIVE")
    print("    in : %s" % s)
    print("    out: %s" % out)
    for c in ch:
        print("    %s -> %s  [%s]" % (c["wrong"], c["correct"], c["category"]))
sys.exit(1 if fails else 0)
