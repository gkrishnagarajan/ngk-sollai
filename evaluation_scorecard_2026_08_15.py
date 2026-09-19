#!/usr/bin/env python3
"""
DETAILED PERFORMANCE SCORECARD
Software Capability Assessment
Created: 2026-08-15
Purpose: Measure capability levels separately
Status: TRAINING/EVALUATION DATA
"""

CAPABILITY_SCORES = {
    'spelling_correction': {
        'score': 90,
        'status': '✅ Excellent',
        'examples_working': [
            'செய்யபட்டு → செய்யப்பட்டு',
            'விசாரனை → விசாரணை',
            'தயாரிக்கபட்டு → தயாரிக்கப்பட்டு',
            'நிரூபிக்கபடவில்லை → நிரூபிக்கப்படவில்லை',
        ],
        'note': 'Basic typo/consonant correction working well',
    },
    
    'basic_grammar': {
        'score': 80,
        'status': '✅ Good',
        'examples_working': [
            'விடுதலை செய்யபடுகிறார்கள் → செய்யப்படுகிறார்கள்',
            'ரத்து செய்யபடுகிறது → செய்யப்படுகிறது',
            'அழிக்கபட → அழிக்கப்பட',
        ],
        'partially_missed': [
            'அவரை சட்டையைப் பிடித்து (dual object problem)',
        ],
    },
    
    'compound_words_sandhi': {
        'score': 75,
        'status': '⚠️ Inconsistent',
        'examples_working': [
            'வழி மறித்து → வழிமறித்து',
            'கையினால் → கையால்',
            'மருத்துவ சாட்சி → மருத்துவச் சாட்சி',
            'வழக்கு சொத்துக்கள் → வழக்குச் சொத்துக்கள்',
        ],
        'examples_missed': [
            'புகார் தாரரான → புகார்தாரரான (NOT CORRECTED)',
            'மருத்துவ சான்றிதழ் (should match மருத்துவச் pattern)',
        ],
        'note': 'Applies sometimes but not consistently',
    },
    
    'legal_terminology': {
        'score': 75,
        'status': '⚠️ Partial',
        'examples_working': [
            'Recognized some legal terms need sandhi',
        ],
        'examples_missed': [
            'குற்றப்பத்திரிக்கை - not normalized to preferred judicial form',
            'Terminology preference not established',
        ],
    },
    
    'formal_judicial_style': {
        'score': 60,
        'status': '❌ Weak',
        'examples_missed': [
            'அரசுத்தரப்பு வழக்கின் சுருக்கம் என்னவென்றால் (conversational, not formal)',
            'அவருடைய கன்னத்தில் (acceptable but not formal judicial)',
            'P.W.3 மருத்துவ அதிகாரி. (fragment - style issue)',
        ],
        'note': 'No register/style normalization attempted',
    },
    
    'contextual_rephrasing': {
        'score': 50,
        'status': '❌ Poor',
        'examples_missed': [
            'அவருடைய vs தனது selection (requires narrative context)',
            'P.W.2 contradiction not flagged despite multiple clues',
            'Sentence structure problems not identified',
            'Object construction errors (அவரை + சட்டையைப்) not caught',
        ],
        'note': 'Requires understanding of context, not just patterns',
    },
    
    'logical_consistency': {
        'score': 35,
        'status': '❌ Critical Gap',
        'examples_missed': [
            'P.W.2 eyewitness contradiction (CRITICAL)',
            'Double negative ambiguity not resolved',
            'A1/A2 reasoning not separately assessed',
            'Medical-narrative alignment not checked',
        ],
        'note': 'Most important gaps for judicial rephrasing',
    },
}

# ============================================================
# OVERALL ASSESSMENT
# ============================================================

OVERALL_ASSESSMENT = {
    'current_score': '70/100',
    'good_for': 'Basic Tamil spelling correction',
    'insufficient_for': 'Judicial language rephrasing system',
    
    'capability_analysis': {
        'levels_1_3': {
            'spelling_grammar_morphology': '~82% average',
            'assessment': 'Adequate for basic spell checker',
        },
        'levels_4_5': {
            'judicial_logic': '~45% average',
            'assessment': 'INSUFFICIENT - major gap',
        },
    },
    
    'critical_weakness': 'System does not understand judicial context or logical structure',
    'primary_value': 'Corrects mechanical/spelling errors efficiently',
}

