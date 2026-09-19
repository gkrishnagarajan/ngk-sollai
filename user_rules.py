#!/usr/bin/env python3
"""User-added rules. Editable. Separate from main database."""
import json, os

# Point to Mega data directory
import os as _os
DATA_DIR = _os.path.expanduser("~/NGK_Solai_Data")
PATH = _os.path.join(DATA_DIR, "user_rules.json")

def load():
    if not os.path.exists(PATH):
        return []
    try:
        with open(PATH, encoding="utf-8") as fh:
            return json.load(fh).get("rules", [])
    except Exception:
        return []

def save(rules):
    with open(PATH, "w", encoding="utf-8") as fh:
        json.dump({"count": len(rules), "rules": rules}, fh,
                  ensure_ascii=False, indent=2)

def add(wrong, correct, note=""):
    wrong, correct = wrong.strip(), correct.strip()
    if not wrong or not correct:
        return False, "Both fields required"
    rules = load()
    for r in rules:
        if r["wrong"] == wrong:
            return False, "Rule already exists for that word"
    rules.append({"wrong": wrong, "correct": correct, "note": note.strip()})
    save(rules)
    return True, "Added"

def update(index, wrong, correct, note=""):
    rules = load()
    if not (0 <= index < len(rules)):
        return False, "Not found"
    rules[index] = {"wrong": wrong.strip(), "correct": correct.strip(), "note": note.strip()}
    save(rules)
    return True, "Updated"

def delete(index):
    rules = load()
    if not (0 <= index < len(rules)):
        return False, "Not found"
    rules.pop(index)
    save(rules)
    return True, "Deleted"

def as_correction_rules():
    """Return user rules in the same format as rule_store rules
    so they can be injected into the main correction pipeline."""
    import re
    result = []
    for r in load():
        wrong = r.get("wrong", "").strip()
        correct = r.get("correct", "").strip()
        if wrong and correct:
            result.append({
                "wrong": wrong,
                "correct": correct,
                "category": "user",
                "source": "user_rules.json",
                "confidence": 1.0,
            })
    # Sort longest first (same as rule_store)
    result.sort(key=lambda r: len(r["wrong"]), reverse=True)
    return result
