#!/usr/bin/env python3
"""
FAILED CASES FROM JUDICIAL TAMIL TEST
Analysis of what the system MISSED
PERMANENT TRAINING DATA
Created: 2026-08-15
Source: Legal judgment review session
"""

# ============================================================
# LEVEL 4 FAILURES: Judicial Terminology & Register
# ============================================================

LEVEL_4_FAILURES = {
    'terminology_inconsistency': [
        {
            'error': 'குற்றப்பத்திரிக்கை',
            'should_be': 'குற்றப்பத்திரிகை',
            'reason': 'Legal terminology normalization - formal judicial term',
            'missed': True,
        },
        {
            'error': 'புகார் தாரர்',
            'should_be': 'புகார்தாரர்',
            'reason': 'Compound word normalization in legal context',
            'missed': True,
        },
    ],
    'contextual_pronouns': [
        {
            'text': 'அவருடைய வீட்டிற்கு சென்று',
            'better': 'தனது வீட்டிற்குச் சென்று',
            'reason': 'Narrative context - speaker is main subject',
            'type': 'contextual_not_spelling',
            'missed': True,
        },
    ],
    'sentence_structure': [
        {
            'text': 'அவரை சட்டையைப் பிடித்து இழுத்து',
            'issue': 'inappropriate dual object construction',
            'should_be': 'சட்டையைப் பிடித்து இழுத்து (single coherent object)',
            'missed': True,
        },
    ],
    'judicial_register': [
        {
            'text': 'அரசுத்தரப்பு வழக்கின் சுருக்கம் என்னவென்றால்',
            'issue': 'conversational tone, not formal judicial',
            'better': 'வழக்கின் சுருக்கம் வருமாறு',
            'reason': 'Judicial register/style normalization',
            'missed': True,
        },
    ],
    'compound_word_inconsistency': [
        {
            'text1': 'மருத்துவச் சாட்சி (correct)',
            'text2': 'மருத்துவ சான்றிதழ் (should match)',
            'issue': 'Sandhi applied inconsistently',
            'should_apply': 'மருத்துவ + சான்றிதழ் = மருத்துவச் சான்றிதழ்',
            'missed': True,
        },
    ],
}

# ============================================================
# LEVEL 5 FAILURES: Logical & Contextual Errors
# ============================================================

LEVEL_5_FAILURES = {
    'evidentiary_contradiction': [
        {
            'context': 'P.W.2 contradiction',
            'claim1': 'P.W.2 சம்பவத்தை நேரில் பார்த்தவர் என்று குற்றப்பத்திரிக்கையில் குறிப்பிடப்பட்டிருந்தாலும்',
            'claim2': 'குறுக்கு விசாரணையில் அவர் தாக்குதலை பார்க்கவில்லை',
            'fact_emerging': 'அவர் சம்பவ இடத்துக்கு வந்தபோது ஏற்கனவே சண்டை முடிந்துவிட்டது',
            'logical_error': 'Eyewitness status contradicted - he arrived after',
            'should_flag': 'CRITICAL EVIDENTIARY INCONSISTENCY',
            'missed': True,
            'severity': 'HIGH',
        },
    ],
    'double_negative_ambiguity': [
        {
            'text': 'முதல் எதிரி மீது சில சந்தேகங்கள் இருப்பதாகவும், இரண்டாவது எதிரி மீது சந்தேகமே இல்லை என்றும் கூற முடியாது',
            'context': 'Previous para: இரண்டாவது எதிரியின் மீது உள்ள சாட்சியம் போதுமானதாக இல்லை',
            'issue': 'Double negative creates ambiguity',
            'should_clarify': 'குற்றஞ்சாட்டப்பட்ட இரு எதிரிகளும் சந்தேகத்திற்கு அப்பாற்பட்ட வகையில் நிரூபிக்கப்படவில்லை',
            'missed': True,
            'severity': 'HIGH',
        },
    ],
    'reasoning_not_aligned_with_conclusion': [
        {
            'conclusion': 'இரு எதிரிகளும் விடுதலை செய்யப்படுகிறார்கள்',
            'reasoning_shows': [
                'A1: சில சந்தேகங்கள்',
                'A2: சந்தேகமே இல்லை',
            ],
            'issue': 'Reasoning does not clearly explain WHY both acquitted',
            'missing_clarity': [
                'Why is A1 not proved beyond doubt?',
                'Why is A2 not proved beyond doubt?',
                'Is entire prosecution case unreliable?',
                'Why benefit of doubt applies?',
            ],
            'should_state': 'அரசுத்தரப்பு குற்றச்சாட்டுகளை சந்தேகத்திற்கு அப்பாற்பட்ட வகையில் நிரூபிக்கத் தவறியுள்ளது',
            'missed': True,
            'severity': 'HIGH',
        },
    ],
    'medical_evidence_alignment': [
        {
            'injuries': 'இடது கன்னத்தில் வீக்கம் மற்றும் வலது கையில் சிறிய சிராய்ப்பு',
            'narrative': 'முதல் எதிரி கன்னத்தில் அடித்தார்; இரண்டாவது எதிரி சட்டையைப் பிடித்து இழுத்தார்',
            'question': 'Do injuries fully match narrative?',
            'needs_analysis': 'Consistency check between medical evidence and ocular evidence',
            'missed': True,
            'severity': 'MEDIUM',
        },
    ],
}

# ============================================================
# METADATA
# ============================================================

FAILURE_METADATA = {
    'total_missed_level4': 6,
    'total_missed_level5': 4,
    'severity_high': 5,
    'severity_medium': 1,
    'document_score': '70/100',
    'reason_for_70': 'Excellent Level 1-3, weak Level 4-5',
    'created': '2026-08-15',
}

