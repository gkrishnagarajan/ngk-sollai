#!/usr/bin/env python3
"""Categorised rule store. Append-only. Anchored matching."""
import json, glob, os, re

# Point to Mega data directory
DATA_DIR = os.path.expanduser("~/NGK_Solai_Data")
RULE_GLOB = os.path.join(DATA_DIR, "tamil_rules_*.json")

# User rules path — same directory as this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_RULES_PATH = os.path.join(DATA_DIR, "user_rules.json")

def load_all_rules():
    rules, seen, sources = [], set(), []

    # Load main rule files from Mega
    for path in sorted(glob.glob(RULE_GLOB)):
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception as e:
            print("  SKIP %s (%s)" % (path, e))
            continue
        entries = data.get("rules", data) if isinstance(data, dict) else (data if isinstance(data, list) else [])
        added = 0
        for r in entries:
            # Skip if not a dict
            if not isinstance(r, dict):
                continue
            w = r.get("wrong", "")
            if not w or w in seen:
                continue
            seen.add(w)
            entry = {
                "wrong": w,
                "correct": r.get("correct", ""),
                "category": r.get("category", "uncategorised"),
                "source": r.get("source", os.path.basename(path)),
                "confidence": r.get("confidence", 1.0),
            }
            if r.get("phrase_anchored"):
                entry["phrase_anchored"] = True
                if "prefix_any" in r: entry["prefix_any"] = r["prefix_any"]
                if "suffix_any" in r: entry["suffix_any"] = r["suffix_any"]
            rules.append(entry)
            added += 1
        sources.append((os.path.basename(path), added, len(entries) - added))

    # Load user rules and inject into pipeline
    user_added = 0
    if os.path.exists(USER_RULES_PATH):
        try:
            with open(USER_RULES_PATH, encoding="utf-8") as fh:
                user_data = json.load(fh)
            user_entries = user_data.get("rules", [])
            for r in user_entries:
                if not isinstance(r, dict):
                    continue
                w = r.get("wrong", "").strip()
                correct = r.get("correct", "").strip()
                if not w or not correct or w in seen:
                    continue
                seen.add(w)
                rules.append({
                    "wrong": w,
                    "correct": correct,
                    "category": "user",
                    "source": "user_rules.json",
                    "confidence": 1.0,
                })
                user_added += 1
            sources.append(("user_rules.json", user_added, len(user_entries) - user_added))
        except Exception as e:
            print("  SKIP user_rules.json (%s)" % e)

    # Sort longest first — critical for correct matching
    rules.sort(key=lambda r: len(r["wrong"]), reverse=True)
    return rules, sources


def _context_ok(text, match_start, match_end, rule):
    """Check prefix_any / suffix_any context for phrase_anchored rules.
    prefix_any: sentence-scoped — checks entire sentence containing the match.
    suffix_any: immediate 30-char window after match.
    Returns True if ANY prefix OR ANY suffix matches."""
    prefix_any = rule.get("prefix_any", [])
    suffix_any = rule.get("suffix_any", [])
    if not prefix_any and not suffix_any:
        return True
    # Sentence-scoped prefix check
    sent_start = max(
        text.rfind(".", 0, match_start) + 1,
        text.rfind("?", 0, match_start) + 1,
        text.rfind("!", 0, match_start) + 1,
        0
    )
    import re as _re
    sent_end_m = _re.search(r'[.?!]', text[match_end:])
    sent_end = match_end + sent_end_m.start() if sent_end_m else len(text)
    before_in_sent = text[sent_start:match_start]
    prefix_ok = any(p in before_in_sent for p in prefix_any) if prefix_any else False
    # Immediate suffix check
    after = text[match_end:match_end + 30]
    suffix_ok = any(s in after for s in suffix_any) if suffix_any else False
    return prefix_ok or suffix_ok

def apply_rules(text, rules, max_passes=3):
    out, changes = text, []
    fired = set()  # track rules that have already fired; key = (wrong, correct)
    for _pass in range(max_passes):
        pass_changed = False
        for r in rules:
            wrong = r["wrong"]
            correct = r["correct"]
            rule_key = (wrong, correct)
            if rule_key in fired:
                continue
            anchored = r.get("phrase_anchored", False) and (
                r.get("prefix_any") or r.get("suffix_any")
            )
            if correct.startswith(wrong) and len(correct) > len(wrong):
                suffix = re.escape(correct[len(wrong):])
                pat = r"(?<!\w)" + re.escape(wrong) + r"(?!" + suffix + r")"
            else:
                pat = r"(?<!\w)" + re.escape(wrong) + r"(?!\w)"
            if anchored:
                # Apply only where context matches
                new_out = out
                offset = 0
                changed_here = False
                for m in re.finditer(pat, out):
                    if _context_ok(out, m.start(), m.end(), r):
                        new_out = new_out[:m.start() + offset] + correct + new_out[m.end() + offset:]
                        offset += len(correct) - len(wrong)
                        changed_here = True
                if changed_here:
                    out = new_out
                    changes.append({
                        "wrong": r["wrong"],
                        "correct": r["correct"],
                        "category": r["category"],
                        "source": r["source"],
                    })
                    pass_changed = True
                    fired.add(rule_key)
            else:
                if re.search(pat, out):
                    out = re.sub(pat, r["correct"], out)
                    changes.append({
                        "wrong": r["wrong"],
                        "correct": r["correct"],
                        "category": r["category"],
                        "source": r["source"],
                    })
                    pass_changed = True
                    fired.add(rule_key)
        if not pass_changed:
            break
    return out, changes
