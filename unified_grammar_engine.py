#!/usr/bin/env python3
from grammar_database_multi_file import MultiFileGrammarDatabase
from contextual_judicial_rephraser import ContextualJudicialRephraser


class UnifiedTamilGrammarEngine:
    def __init__(self, use_database=True):
        self.rephraser = ContextualJudicialRephraser()
        self.db = MultiFileGrammarDatabase()
        self.corrections = self.db.corrections or {}
        self.add_default_rules()
    
    def add_default_rules(self):
        pass  # defaults moved to DB
    
    def correct_text(self, text):
        corrected = text
        changes = []
        import re as _re
        for wrong, correct in sorted(self.corrections.items(), key=lambda kv: -len(kv[0])):
            _pat = r"(?<![\u0B80-\u0BFF])" + _re.escape(wrong) + r"(?![\u0B80-\u0BFF])"
            if _re.search(_pat, corrected):
                corrected = _re.sub(_pat, correct, corrected)
                changes.append({'wrong': wrong, 'correct': correct})
        
        return {
            'original': text,
            'corrected': corrected,
            'changes': changes,
            'changes_count': len(changes),
            'statistics': {'total_corrections': len(self.corrections)}
        }
    
    def add_new_rule(self, wrong, correct, **kwargs):
        self.corrections[wrong] = correct
        return self.db.add_rule(wrong, correct, **kwargs)
    
    def export_rules(self, filename):
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.corrections, f, ensure_ascii=False, indent=2)
