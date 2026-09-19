#!/usr/bin/env python3
import json, os, glob
from datetime import datetime
from collections import defaultdict

DATA_DIR = os.path.expanduser("~/NGK_Solai_Data")

class DatabaseOptimizer:
    def __init__(self):
        self.rules = {}
        self.duplicates = []
        self.conflicts = []

    def load_all_rules(self):
        print("📂 Loading all rule files...")
        rule_files = sorted(glob.glob(os.path.join(DATA_DIR, "tamil_rules_*.json")))
        for rule_file in rule_files:
            fname = os.path.basename(rule_file)
            try:
                with open(rule_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                rules_list = []
                if isinstance(data, dict) and 'rules' in data:
                    rules_list = data['rules']
                elif isinstance(data, list):
                    rules_list = data
                for rule in rules_list:
                    if not isinstance(rule, dict): continue
                    if 'wrong' not in rule or 'correct' not in rule: continue
                    wrong = rule['wrong']
                    correct = rule['correct']
                    if wrong in self.rules:
                        if self.rules[wrong]['correct'] != correct:
                            self.conflicts.append({'wrong': wrong, 'correct1': self.rules[wrong]['correct'], 'correct2': correct, 'file1': self.rules[wrong]['file'], 'file2': fname})
                        else:
                            self.duplicates.append({'wrong': wrong, 'correct': correct, 'file1': self.rules[wrong]['file'], 'file2': fname})
                    else:
                        self.rules[wrong] = {'correct': correct, 'file': fname, 'category': rule.get('category','unknown'), 'confidence': rule.get('confidence', 1.0)}
                print(f"   ✅ {fname}: {len(rules_list)} rules")
            except Exception as e:
                print(f"   ⚠️  {fname}: {e}")
        print(f"✅ Total unique rules: {len(self.rules)}")
        return self.rules

    def report(self):
        print("\n📊 DATABASE REPORT")
        print("="*60)
        print(f"Total unique rules  : {len(self.rules)}")
        print(f"Duplicates found    : {len(self.duplicates)}")
        print(f"Conflicts found     : {len(self.conflicts)}")
        cats = defaultdict(int)
        for w, m in self.rules.items():
            cats[m['category']] += 1
        print("\nCategories:")
        for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
            print(f"  {cat}: {count}")
        if self.conflicts:
            print("\n⚠️  Conflicts (same wrong word, different correction):")
            for c in self.conflicts[:10]:
                print(f"  {c['wrong']}: '{c['correct1']}' vs '{c['correct2']}'")
                print(f"     ({c['file1']} vs {c['file2']})")
        print("="*60)

    def consolidate(self):
        out = {'created': datetime.now().isoformat(), 'total': len(self.rules), 'rules': {}}
        for wrong, meta in self.rules.items():
            out['rules'][wrong] = meta['correct']
        fname = os.path.join(DATA_DIR, f"tamil_rules_consolidated_{datetime.now().strftime('%Y-%m-%d')}.json")
        with open(fname, 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Consolidated ruleset saved: {fname}")
        return fname

    def optimize(self):
        print("\n" + "="*60)
        print("🚀 NGK SOLLAI DATABASE OPTIMIZER")
        print("="*60)
        self.load_all_rules()
        self.report()
        self.consolidate()
        print("\n✅ Optimization complete!")

if __name__ == '__main__':
    DatabaseOptimizer().optimize()
