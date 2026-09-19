#!/usr/bin/env python3
"""Regression test: correct sentences must emerge unchanged."""
import json, sys, os
from rule_store import load_all_rules, apply_rules

# Point to Mega data directory
DATA_DIR = os.path.expanduser("~/NGK_Solai_Data")

rules, sources = load_all_rules()
print("Loaded %d rules from %d file(s)" % (len(rules), len(sources)))
for name, added, dup in sources:
    print("  %-36s +%-5d dup:%d" % (name, added, dup))

negative_examples_path = os.path.join(DATA_DIR, "tamil_negative_examples.json")

if not os.path.exists(negative_examples_path):
    print("\n⚠️  No negative examples file found at: %s" % negative_examples_path)
    sys.exit(0)

with open(negative_examples_path, encoding="utf-8") as fh:
    sents = json.load(fh)["sentences"]

fails = []
for s in sents:
    out, changes = apply_rules(s, rules)
    if changes:
        fails.append((s, out, changes))

print("\nNegative examples: %d tested, %d false positive(s)" % (len(sents), len(fails)))
for s, out, ch in fails:
    print("\n  FALSE POSITIVE")
    print("    in : %s" % s)
    print("    out: %s" % out)
    for c in ch:
        print("    rule: %s -> %s  [%s from %s]" % (c["wrong"], c["correct"], c["category"], c["source"]))

sys.exit(1 if fails else 0)
