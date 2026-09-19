#!/usr/bin/env python3
import json

class TamilDictionaryBuilder:
    def __init__(self):
        self.dictionary = {}
    
    def build_dictionary(self):
        return self.dictionary
    
    def export_to_json(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.dictionary, f, ensure_ascii=False, indent=2)
