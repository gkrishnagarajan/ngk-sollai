#!/usr/bin/env python3
"""
Fix stray quote bugs in rule files.
Finds rules where 'correct' field contains empty quotes or stray punctuation.
"""
import json, glob, os

DATA_DIR = os.path.expanduser("~/NGK_Solai_Data")

suspicious = []

for path in sorted(glob.glob(os.path.join(DATA_DIR, "tamil_rules_*.json"))):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"SKIP {path}: {e}")
        continue

    rules = data.get("rules", [])
    for r in rules:
        if not isinstance(r, dict):
            continue
        wrong = r.get("wrong", "")
        correct = r.get("correct", "")

        # Check for stray quotes or empty-like corrections
        if '""' in correct or "''" in correct:
            suspicious.append({
                "file": os.path.basename(path),
                "wrong": wrong,
                "correct": correct,
                "issue": "stray quotes in correct field"
            })

        # Check for corrections that are clearly wrong
        # (correct field is much shorter than wrong, possibly stripped accidentally)
        if correct and len(correct) < len(wrong) / 3:
            suspicious.append({
                "file": os.path.basename(path),
                "wrong": wrong,
                "correct": correct,
                "issue": "correct field suspiciously short"
            })

        # Check for பார்த்துபார்த்து specifically
        if "பார்த்துபார்த்து" in wrong:
            suspicious.append({
                "file": os.path.basename(path),
                "wrong": wrong,
                "correct": correct,
                "issue": "பார்த்துபார்த்து rule - verify correct field"
            })

        # Check for இன்றி rules that might be unanchored
        if "இன்றி" in wrong or "இன்றி" in correct:
            suspicious.append({
                "file": os.path.basename(path),
                "wrong": wrong,
                "correct": correct,
                "issue": "இன்றி rule - verify anchoring"
            })

print(f"\n{'='*60}")
print(f"SUSPICIOUS RULES FOUND: {len(suspicious)}")
print(f"{'='*60}")
for s in suspicious:
    print(f"\n📁 {s['file']}")
    print(f"   Wrong  : {s['wrong']}")
    print(f"   Correct: {s['correct']}")
    print(f"   Issue  : {s['issue']}")

print(f"\n{'='*60}")
print("Review the above rules carefully.")
print("Fix any stray quotes or anchoring issues.")
