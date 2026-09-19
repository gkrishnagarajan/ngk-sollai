#!/usr/bin/env python3
"""Import corpus TSV/JSON into a dated rule file. Never overwrites."""
import json, sys, os, csv
from datetime import datetime

def read_pairs(path):
    pairs = []
    if path.endswith(".json"):
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        items = data if isinstance(data, list) else data.get("rules", [])
        for r in items:
            pairs.append((r.get("wrong",""), r.get("correct",""), r.get("category","uncategorised")))
    else:
        with open(path, encoding="utf-8") as fh:
            for row in csv.reader(fh, delimiter="\t"):
                if len(row) >= 2:
                    pairs.append((row[0].strip(), row[1].strip(),
                                  row[2].strip() if len(row) > 2 else "uncategorised"))
    return pairs

def main(src):
    pairs = read_pairs(src)
    stamp = datetime.now().strftime("%Y-%m-%d")
    out = "tamil_rules_%s.json" % stamp
    n = 1
    while os.path.exists(out):
        n += 1
        out = "tamil_rules_%s_%02d.json" % (stamp, n)

    rules, skipped = [], 0
    for w, c, cat in pairs:
        if not w or not c or w == c:
            skipped += 1
            continue
        rules.append({"wrong": w, "correct": c, "category": cat,
                      "source": os.path.basename(src), "confidence": 1.0})

    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"created": stamp, "source_file": os.path.basename(src),
                   "count": len(rules), "rules": rules}, fh,
                  ensure_ascii=False, indent=2)

    by_cat = {}
    for r in rules:
        by_cat[r["category"]] = by_cat.get(r["category"], 0) + 1
    print("Wrote %s" % out)
    print("  imported: %d   skipped: %d" % (len(rules), skipped))
    for k in sorted(by_cat):
        print("    %-28s %4d" % (k, by_cat[k]))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python3 import_corpus.py <corpus.tsv|corpus.json>")
        sys.exit(1)
    main(sys.argv[1])
