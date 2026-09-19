#!/usr/bin/env python3
"""
LEVEL 4-5 ADVANCED RULES
Judicial Terminology, Register, Logic Detection
APPEND-ONLY TRAINING DATA
Created: 2026-08-15
"""

# ============================================================
# LEVEL 4: ADVANCED - Judicial Terminology Consistency
# ============================================================

LEVEL_4_JUDICIAL_TERMINOLOGY = {
    # Terminology normalization
    'terminology_standards': {
        'குற்றப்பத்திரிக்கை': 'குற்றப்பத்திரிகை',  # Formal judicial term
        'மருத்துவ சான்றிதழ்': 'மருத்துவச் சான்றிதழ்',  # Consistency with sandhi
    },
    # Compound word normalization
    'compound_words': {
        'புகார் தாரர்': 'புகார்தாரர்',
        'மருத்துவ சாட்சி': 'மருத்துவச் சாட்சி',
    },
    # Judicial register (formal tone)
    'formal_register': {
        'விவரம் என்னவென்றால்': 'better as: வழக்கின் விவரம் வருமாறு',
    },
}

# ============================================================
# LEVEL 4: CONTEXTUAL IMPROVEMENTS (not spelling)
# ============================================================

LEVEL_4_CONTEXTUAL = {
    'contextual_pronouns': {
        'rule': 'In judicial narrative, when speaker/subject is main agent, prefer தனது over அவருடைய',
        'example': {
            'found': 'அவருடைய வீட்டிற்கு சென்று',
            'better': 'தனது வீட்டிற்குச் சென்று',
            'note': 'Not a spelling error - requires context understanding',
        }
    },
    'object_construction': {
        'rule': 'Avoid dual object markers in causative-resultative constructions',
        'example': {
            'found': 'அவரை சட்டையைப் பிடித்து',
            'better': 'சட்டையைப் பிடித்து',
            'note': 'Verb takes single coherent object',
        }
    },
}

# ============================================================
# LEVEL 5: LOGICAL ERROR DETECTION PATTERNS
# ============================================================

LEVEL_5_LOGICAL_PATTERNS = {
    'evidentiary_contradictions': {
        'pattern': 'Witness claimed as eyewitness but cross-exam shows arrived after',
        'keywords': ['நேரில் பார்த்தவர்', 'சம்பவத்தை', 'குறுக்கு விசாரணை', 'பார்க்கவில்லை'],
        'action': 'FLAG: Eyewitness credibility contradiction',
        'test_case': 'P.W.2 situation',
    },
    'double_negative_detection': {
        'pattern': 'Two negatives creating ambiguity',
        'keywords': ['சந்தேகங்கள்', 'சந்தேகமே இல்லை', 'கூற முடியாது'],
        'action': 'FLAG: Double negative - suggest single clear statement',
        'test_case': 'முதல் எதிரி... இரண்டாவது எதிரி... situation',
    },
    'reasoning_conclusion_alignment': {
        'pattern': 'Conclusion acquits but reasoning unclear on WHY',
        'check': [
            'Does reasoning explain why A1 not proved?',
            'Does reasoning explain why A2 not proved?',
            'Is it clear prosecution burden not met?',
            'Is benefit of doubt clearly stated?',
        ],
        'action': 'FLAG: Reasoning-conclusion mismatch',
    },
    'medical_narrative_alignment': {
        'pattern': 'Do described injuries match assault narrative?',
        'check': [
            'Injuries: which body parts affected?',
            'Narrative: who attacked where?',
            'Do they match?',
        ],
        'action': 'FLAG if mismatch: Medical-narrative inconsistency',
    },
}

# ============================================================
# METADATA
# ============================================================

ADVANCED_RULES_METADATA = {
    'level_4_rules_added': 8,
    'level_5_patterns_added': 4,
    'purpose': 'Judicial rephrasing + logical consistency',
    'status': 'TRAINING DATA - not yet implemented in engine',
    'next_step': 'Integrate into correction engine',
}

