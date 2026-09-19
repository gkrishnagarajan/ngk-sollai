#!/usr/bin/env python3
import json
import csv

class LabeledCorpusGenerator:
    def __init__(self):
        self.corpus = []
    
    def generate_corpus(self, num_sentences=100):
        return self.corpus
    
    def export_to_json(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.corpus, f, ensure_ascii=False, indent=2)
    
    def export_to_csv(self, filename):
        if self.corpus:
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['text', 'error', 'correction'])
                writer.writeheader()
                writer.writerows(self.corpus)
