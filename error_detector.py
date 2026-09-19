#!/usr/bin/env python3
"""
NGK Sollai - Error Detector & Analyzer
Detects spelling, grammatical, and logical errors
"""

import json
import os
import re
from datetime import datetime
from collections import defaultdict

DATA_DIR = os.path.expanduser("~/NGK_Solai_Data")

class ErrorDetector:
    def __init__(self):
        self.errors_found = []
        self.error_categories = defaultdict(list)
        self.false_positives = []
        self.missed_corrections = []
    
    def detect_spelling_errors(self, text, vocabulary):
        """Detect spelling errors not caught by the system"""
        print("🔍 Detecting spelling errors...")
        
        words = text.split()
        spelling_errors = []
        
        for word in words:
            # Remove punctuation
            clean_word = re.sub(r'[,।॥।]+$', '', word)
            
            if clean_word and clean_word not in vocabulary:
                # Check for common misspellings
                if self._is_likely_misspelling(clean_word, vocabulary):
                    spelling_errors.append({
                        'word': clean_word,
                        'type': 'spelling',
                        'suggestion': self._find_suggestion(clean_word, vocabulary)
                    })
        
        return spelling_errors
    
    def detect_grammatical_errors(self, text):
        """Detect grammatical errors"""
        print("📝 Detecting grammatical errors...")
        
        errors = []
        
        # Check for sentence structure
        sentences = text.split('।')
        
        for sentence in sentences:
            if not sentence.strip():
                continue
            
            # Missing verb
            if not self._has_verb(sentence):
                errors.append({
                    'sentence': sentence.strip(),
                    'type': 'missing_verb',
                    'issue': 'Sentence may be missing a verb'
                })
            
            # Subject-verb agreement (simplified)
            if not self._check_subject_verb_agreement(sentence):
                errors.append({
                    'sentence': sentence.strip(),
                    'type': 'subject_verb_mismatch',
                    'issue': 'Possible subject-verb agreement issue'
                })
            
            # Case marking errors
            if not self._check_case_markers(sentence):
                errors.append({
                    'sentence': sentence.strip(),
                    'type': 'case_error',
                    'issue': 'Possible case marking error'
                })
        
        return errors
    
    def detect_logical_errors(self, text):
        """Detect logical inconsistencies"""
        print("⚡ Detecting logical errors...")
        
        errors = []
        
        # Check for contradictions
        contradictions = self._find_contradictions(text)
        errors.extend(contradictions)
        
        # Check for double negatives
        double_negatives = self._find_double_negatives(text)
        errors.extend(double_negatives)
        
        # Check for tense inconsistencies
        tense_issues = self._check_tense_consistency(text)
        errors.extend(tense_issues)
        
        return errors
    
    def _is_likely_misspelling(self, word, vocabulary):
        """Check if word is likely a misspelling"""
        # Simple heuristic: if word is very different from all vocab
        if len(word) < 2:
            return False
        
        # Check Levenshtein distance
        for vocab_word in list(vocabulary.keys())[:1000]:  # Check first 1000
            if self._levenshtein_distance(word, vocab_word) <= 2:
                return True
        
        return False
    
    def _levenshtein_distance(self, s1, s2):
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _find_suggestion(self, word, vocabulary):
        """Find closest match in vocabulary"""
        closest = None
        min_distance = float('inf')
        
        for vocab_word in list(vocabulary.keys())[:500]:
            dist = self._levenshtein_distance(word, vocab_word)
            if dist < min_distance:
                min_distance = dist
                closest = vocab_word
        
        return closest if min_distance <= 3 else None
    
    def _has_verb(self, sentence):
        """Check if sentence has a verb"""
        # Tamil verb endings: -ता, -अनु, etc.
        verb_patterns = [
            r'.*[உ][म]$',  # -um
            r'.*[ा][ल]$',  # -al
            r'.*[य][ु][ल]$',  # -yul
        ]
        
        for pattern in verb_patterns:
            if re.search(pattern, sentence):
                return True
        
        return False
    
    def _check_subject_verb_agreement(self, sentence):
        """Check subject-verb agreement (simplified)"""
        # This is a simplified check
        # In a real system, you'd parse the sentence structure
        return True  # Placeholder
    
    def _check_case_markers(self, sentence):
        """Check for proper case marking"""
        # Tamil case markers: ஐ, ஆல், etc.
        case_markers = ['ஐ', 'ஆல', 'ஃக', 'குறிப்', 'த', 'ல்']
        
        has_proper_marking = any(marker in sentence for marker in case_markers)
        return has_proper_marking or len(sentence.split()) < 3
    
    def _find_contradictions(self, text):
        """Find contradictory statements"""
        errors = []
        
        # Look for contradictory words
        contradictions = {
            'yet_but': [('ஆனால்', 'ஆயினும்'), ('மாறாக', 'எனினும்')],
            'positive_negative': [('ஆம்', 'இல்லை')]
        }
        
        # Simple implementation
        sentences = text.split('।')
        
        for i, sent1 in enumerate(sentences):
            for j, sent2 in enumerate(sentences[i+1:], i+1):
                # Check if sentences contradict each other
                if self._sentences_contradict(sent1, sent2):
                    errors.append({
                        'type': 'contradiction',
                        'sentence1': sent1.strip(),
                        'sentence2': sent2.strip(),
                        'issue': 'These sentences may contradict each other'
                    })
        
        return errors
    
    def _sentences_contradict(self, sent1, sent2):
        """Check if two sentences contradict"""
        # Simplified check
        negation_words = ['இல்லை', 'அல்ல', 'ஆகாது']
        
        has_neg_1 = any(word in sent1 for word in negation_words)
        has_neg_2 = any(word in sent2 for word in negation_words)
        
        # If both have negation or both don't, they might contradict
        # This is very simplified
        return False  # Placeholder
    
    def _find_double_negatives(self, text):
        """Find double negatives"""
        errors = []
        
        negation_words = ['இல்லை', 'அல்ல', 'ஆகாது']
        
        sentences = text.split('।')
        
        for sentence in sentences:
            negation_count = sum(1 for word in negation_words if word in sentence)
            
            if negation_count >= 2:
                errors.append({
                    'type': 'double_negative',
                    'sentence': sentence.strip(),
                    'issue': f'Found {negation_count} negations (may be double negative)'
                })
        
        return errors
    
    def _check_tense_consistency(self, text):
        """Check for tense consistency"""
        errors = []
        
        tenses = {
            'past': ['-ता', '-ताnot', '-ிய'],
            'present': ['-उ', '-इर', '-kinṛa'],
            'future': ['-bु', '-buff']
        }
        
        # Simplified check
        sentences = text.split('।')
        detected_tenses = []
        
        for sentence in sentences:
            for tense_type, patterns in tenses.items():
                if any(pattern in sentence for pattern in patterns):
                    detected_tenses.append(tense_type)
        
        # Check for mixing tenses inappropriately
        if detected_tenses and len(set(detected_tenses)) > 2:
            errors.append({
                'type': 'tense_inconsistency',
                'issue': f'Mixed tenses detected: {set(detected_tenses)}'
            })
        
        return errors
    
    def generate_error_report(self):
        """Generate comprehensive error report"""
        print("\n📊 ERROR DETECTION REPORT")
        print("="*60)
        
        total_errors = len(self.errors_found)
        
        print(f"Total errors found: {total_errors}")
        
        for category, errors in self.error_categories.items():
            print(f"\n{category}: {len(errors)}")
            for error in errors[:3]:  # Show first 3
                print(f"  - {error}")
        
        if self.false_positives:
            print(f"\nFalse positives: {len(self.false_positives)}")
        
        if self.missed_corrections:
            print(f"Missed corrections: {len(self.missed_corrections)}")
        
        print("="*60)
        
        return {
            'total_errors': total_errors,
            'by_category': dict(self.error_categories),
            'false_positives': self.false_positives,
            'missed_corrections': self.missed_corrections
        }
    
    def export_error_analysis(self):
        """Export error analysis to file"""
        print("\n📄 Exporting error analysis...")
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_errors': len(self.errors_found),
            'errors': self.errors_found,
            'categories': dict(self.error_categories)
        }
        
        export_file = os.path.join(DATA_DIR, f"error_analysis_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json")
        
        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
            print(f"✅ Analysis exported: {export_file}")
        except Exception as e:
            print(f"❌ Error exporting: {e}")
        
        return export_file

if __name__ == '__main__':
    detector = ErrorDetector()
    print("✅ Error Detector initialized")
