#!/usr/bin/env python3
import re
"""
Contextual Judicial Rephraser
Handles logic, witness tracking, and context-aware corrections
Created: 2026-08-15
"""

class WitnessContradictionDetector:
    """Tracks witness status and flags contradictions"""
    
    def __init__(self):
        self.witnesses = {}
    
    def extract_witnesses(self, text):
        """Find all witness references: P.W.1, P.W.2, etc."""
        import re
        patterns = re.findall(r'P\.W\.\d+', text)
        return list(set(patterns))
    
    def track_witness_claims(self, text, witness_id):
        """Track what each witness claims"""
        import re
        claims = {
            'eyewitness_status': None,
            'arrival_time': None,
            'what_saw': None,
            'contradictions': []
        }
        wid = re.escape(witness_id)

        # Check if presented as eyewitness
        if re.search(wid + r'.{0,20}சம்பவத்தை நேரில் பார்த்தவர்', text):
            claims['eyewitness_status'] = 'eyewitness'

        # Check if arrived after — handles sandhi variants: சம்பவ இடத்துக்கு / சம்பவயிடத்துக்கு
        if re.search(wid, text) and re.search(r'சம்பவ.{0,4}இடத்துக்கு வந்தபோது|சம்பவயிடத்துக்கு வந்தபோது', text):
            claims['arrival_time'] = 'arrived_after'

        # Check if didn't see
        if re.search(wid, text) and 'பார்க்கவில்லை' in text:
            claims['what_saw'] = 'did_not_see'

        return claims
    
    def detect_contradiction(self, claims):
        """Detect if eyewitness claims are contradicted"""
        if (claims['eyewitness_status'] == 'eyewitness' and 
            claims['arrival_time'] == 'arrived_after' and 
            claims['what_saw'] == 'did_not_see'):
            return {
                'contradiction': True,
                'severity': 'CRITICAL',
                'message': 'Witness presented as eyewitness but arrived after incident'
            }
        return {'contradiction': False}


class DoubleNegativeResolver:
    """Resolves double negative ambiguities"""
    
    def detect_double_negative(self, text):
        """Find patterns like: X இல்லை என்றும் கூற முடியாது"""
        import re
        pattern = r'[\w\s]+ இல்லை என்றும் கூற முடியாது'
        matches = re.findall(pattern, text)
        return matches
    
    def resolve(self, sentence):
        """Convert double negative to clear statement"""
        # Pattern: "சந்தேகமே இல்லை என்றும் கூற முடியாது"
        # Means: "Cannot say there is no doubt"
        # Should be: "There is doubt / Evidence is insufficient"
        
        if 'சந்தேகமே இல்லை என்றும் கூற முடியாது' in sentence:
            return sentence.replace(
                'சந்தேகமே இல்லை என்றும் கூற முடியாது',
                'சந்தேகம் உள்ளது / சாட்சியம் போதுமற்றது'
            )
        return sentence


class ReasoningAlignmentChecker:
    """Ensures reasoning supports conclusion"""
    
    def extract_reasoning(self, text, accused_id):
        """Extract reasoning about specific accused"""
        reasoning = {
            'accused': accused_id,
            'evidence_strength': None,
            'conclusion': None
        }
        
        if f'{accused_id} மீது சில சந்தேகங்கள்' in text:
            reasoning['evidence_strength'] = 'weak'
        
        if f'{accused_id} மீது சந்தேகமே இல்லை' in text:
            reasoning['evidence_strength'] = 'no_doubt'
        
        return reasoning
    
    def check_alignment(self, reasoning, conclusion):
        """Does reasoning support conclusion?"""
        if reasoning['evidence_strength'] == 'weak' and conclusion == 'acquitted':
            return {
                'aligned': True,
                'reason': 'Weak evidence justifies acquittal'
            }
        
        if reasoning['evidence_strength'] == 'no_doubt' and conclusion == 'acquitted':
            return {
                'aligned': False,
                'reason': 'Strong certainty contradicts acquittal'
            }
        
        return {'aligned': True}


class ContextualPronounSelector:
    """Selects formal pronouns based on context"""
    
    def analyze_narrative_context(self, text):
        """Is this formal judicial narrative?"""
        return True  # For now, assume judicial context
    
    def recommend_pronoun(self, original_text, sentence):
        """Choose between அவருடைய (informal) and தனது (formal)"""
        if 'அவருடைய' in sentence and self.analyze_narrative_context(original_text):
            return sentence.replace('அவருடைய', 'தனது')
        return sentence


class ContextualJudicialRephraser:
    """Main coordinator for all context-aware rephrasing"""
    
    def __init__(self):
        self.witness_detector = WitnessContradictionDetector()
        self.double_neg_resolver = DoubleNegativeResolver()
        self.reasoning_checker = ReasoningAlignmentChecker()
        self.pronoun_selector = ContextualPronounSelector()
        self.flags = []
    
    def rephrase(self, text):
        """Apply all contextual improvements"""
        result = text
        self.flags = []
        
        # Step 1: Detect witness contradictions
        witnesses = self.witness_detector.extract_witnesses(text)
        for witness in witnesses:
            claims = self.witness_detector.track_witness_claims(text, witness)
            contradiction = self.witness_detector.detect_contradiction(claims)
            if contradiction['contradiction']:
                self.flags.append({
                    'type': 'WITNESS_CONTRADICTION',
                    'severity': contradiction['severity'],
                    'witness': witness,
                    'message': contradiction['message']
                })
        
        # Step 2: Resolve double negatives
        double_negs = self.double_neg_resolver.detect_double_negative(text)
        if double_negs:
            for dn in double_negs:
                resolved = self.double_neg_resolver.resolve(result)
                if resolved != result:
                    self.flags.append({
                        'type': 'DOUBLE_NEGATIVE_RESOLVED',
                        'original': dn,
                        'severity': 'HIGH'
                    })
                    result = resolved
        
        # Step 3: Improve pronouns
        sentences = result.split('।')
        improved_sentences = [
            self.pronoun_selector.recommend_pronoun(text, s) 
            for s in sentences
        ]
        result = '।'.join(improved_sentences)
        
        # Step 4: Sentence-final colloquial copula -> formal judicial copula
        # Pattern: NOUN அவர். -> NOUN ஆவார்.  (sentence-final only)
        # Also: NOUN அவர்கள். -> NOUN ஆவார்கள்.
        _COPULA_PAT = re.compile(
            r'([^\s।\.]+)\s+அவர்கள்([।\.])',
        )
        _COPULA_PAT2 = re.compile(
            r'([^\s।\.]+)\s+அவர்([।\.])',
        )
        def _copula_repl_pl(m):
            self.flags.append({
                'type': 'COPULA_FORMAL',
                'original': m.group(0),
                'correct': m.group(1) + ' ஆவார்கள்' + m.group(2),
                'severity': 'LOW'
            })
            return m.group(1) + ' ஆவார்கள்' + m.group(2)
        def _copula_repl(m):
            self.flags.append({
                'type': 'COPULA_FORMAL',
                'original': m.group(0),
                'correct': m.group(1) + ' ஆவார்' + m.group(2),
                'severity': 'LOW'
            })
            return m.group(1) + ' ஆவார்' + m.group(2)
        result = _COPULA_PAT.sub(_copula_repl_pl, result)
        result = _COPULA_PAT2.sub(_copula_repl, result)

        # Step 5: Sentence-final simple-past reporting verbs -> present-perfect
        # Voice-typing drops "உள்ள": குறிப்பிட்டார் -> குறிப்பிட்டுள்ளார்
        _PAST_PERFECT = [
            ("குறிப்பிட்டார்",   "குறிப்பிட்டுள்ளார்"),
            ("குறிப்பிட்டனர்",   "குறிப்பிட்டுள்ளனர்"),
            ("குறிப்பிட்டது",    "குறிப்பிட்டுள்ளது"),
            ("தெரிவித்தார்",     "தெரிவித்துள்ளார்"),
            ("தெரிவித்தனர்",     "தெரிவித்துள்ளனர்"),
            ("தாக்கல் செய்தார்", "தாக்கல் செய்துள்ளார்"),
            ("தாக்கல் செய்தனர்", "தாக்கல் செய்துள்ளனர்"),
        ]
        for wrong, correct in _PAST_PERFECT:
            pat = re.compile(re.escape(wrong) + r'([।\.])')
            def _pp_repl(m, _w=wrong, _c=correct):
                self.flags.append({
                    'type': 'PAST_PERFECT_FORMAL',
                    'original': _w + m.group(1),
                    'correct': _c + m.group(1),
                    'severity': 'LOW'
                })
                return _c + m.group(1)
            result = pat.sub(_pp_repl, result)

        return {
            'original': text,
            'rephrased': result,
            'flags': self.flags,
            'improvements_made': len(self.flags)
        }
