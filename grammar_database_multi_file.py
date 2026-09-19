#!/usr/bin/env python3
import json
from pathlib import Path
import importlib

class MultiFileGrammarDatabase:
    def __init__(self, db_dir='databases'):
        self.db_dir = Path(db_dir)
        self.db_dir.mkdir(exist_ok=True)
        self.corrections = {}
        self.metadata = {}
        self.load_all()
    
    def load_all(self):
        """UPDATED: Load from ALL sources"""
        # Load from databases/ directory
        for db_file in self.db_dir.glob('*.json'):
            try:
                with open(db_file) as f:
                    data = json.load(f)
                    if 'rules' in data:
                        self.corrections.update(data['rules'])
            except:
                pass
        
        # ADDED: Load from Python module (tamil_legal_rules_level1_5.py)
        try:
            import tamil_legal_rules_level1_5 as legal_rules
            # Level 1
            self.corrections.update(legal_rules.LEVEL_1_SPELLING)
            # Level 2
            self.corrections.update(legal_rules.LEVEL_2_MORPHOLOGY_SANDHI)
            # Level 3
            for wrong, correct in legal_rules.LEVEL_3_GRAMMAR:
                self.corrections[wrong] = correct
            # Level 4
            for wrong, correct in legal_rules.LEVEL_4_LEGAL_REPHRASING:
                self.corrections[wrong] = correct
            self.metadata['legal_rules_loaded'] = True
        except ImportError:
            self.metadata['legal_rules_loaded'] = False
    
    def add_rule(self, wrong, correct, **kwargs):
        import json, os
        self.corrections[wrong] = correct
        data_dir = os.environ.get("DATA_DIR", os.path.expanduser("~/NGK_Solai_Data"))
        user_rules_path = os.path.join(data_dir, "user_rules.json")
        try:
            if os.path.exists(user_rules_path):
                with open(user_rules_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            else:
                existing = {"rules": []}
            if not any(r.get("wrong") == wrong for r in existing["rules"]):
                existing["rules"].append({
                    "wrong": wrong,
                    "correct": correct,
                    "category": kwargs.get("category", "user_added"),
                    "source": "dialog_box"
                })
                with open(user_rules_path, "w", encoding="utf-8") as f:
                    json.dump(existing, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("add_rule write error:", e)
        self.save()
        return {'success': True}
    
    def save(self):
        db_file = self.db_dir / f'vocab.db.json'
        data = {'rules': self.corrections}
        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
