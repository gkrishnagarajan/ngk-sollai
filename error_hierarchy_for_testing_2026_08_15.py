#!/usr/bin/env python3
"""
ERROR HIERARCHY FOR TRAINING CORPUS
Classification by Difficulty Level
Created: 2026-08-15
Purpose: Build test cases from EASY to VERY HARD
"""

ERROR_HIERARCHY = {
    'EASY': {
        'description': 'Basic spelling/typo errors - System should catch 95%',
        'examples': [
            {
                'error': 'விசாரனை',
                'correction': 'விசாரணை',
                'type': 'vowel substitution',
                'system_success': '✅ YES',
            },
            {
                'error': 'செய்யபட்டு',
                'correction': 'செய்யப்பட்டு',
                'type': 'missing consonant',
                'system_success': '✅ YES',
            },
            {
                'error': 'நிரூபிக்கபடவில்லை',
                'correction': 'நிரூபிக்கப்படவில்லை',
                'type': 'missing consonant group',
                'system_success': '✅ YES',
            },
        ],
        'system_accuracy': '90%',
    },
    
    'MEDIUM': {
        'description': 'Compound words, sandhi, basic grammar - System should catch 75%',
        'examples': [
            {
                'error': 'வழி மறித்து',
                'correction': 'வழிமறித்து',
                'type': 'compound word',
                'system_success': '✅ YES',
            },
            {
                'error': 'கையினால்',
                'correction': 'கையால்',
                'type': 'unnecessary vowel',
                'system_success': '✅ YES',
            },
            {
                'error': 'மருத்துவ சாட்சி',
                'correction': 'மருத்துவச் சாட்சி',
                'type': 'sandhi in compound',
                'system_success': '✅ YES',
            },
            {
                'error': 'புகார் தாரர்',
                'correction': 'புகார்தாரர்',
                'type': 'compound word normalization',
                'system_success': '❌ MISSED - inconsistent',
            },
        ],
        'system_accuracy': '75%',
    },
    
    'HARD': {
        'description': 'Contextual, judicial terminology, register - System should catch 50%',
        'examples': [
            {
                'issue': 'P.W.2 eyewitness contradiction',
                'text': 'P.W.2 சம்பவத்தை நேரில் பார்த்தவர் என்று குற்றப்பத்திரிக்கையில் குறிப்பிடப்பட்டிருந்தாலும், தான் சம்பவ இடத்துக்கு வந்தபோது ஏற்கனவே சண்டை முடிந்துவிட்டதாகவும், எதிரிகள் புகார்தாரரை அடித்ததை தான் நேரில் பார்க்கவில்லை',
                'problem': 'Contradictory eyewitness status',
                'should_flag': 'Evidentiary inconsistency',
                'system_success': '❌ MISSED',
            },
            {
                'issue': 'Dual object construction error',
                'text': 'இரண்டாவது எதிரி அவரை சட்டையைப் பிடித்து இழுத்து...',
                'problem': 'அவரை + சட்டையைப் both marked as objects',
                'should_flag': 'Grammar structure error',
                'system_success': '❌ MISSED',
            },
            {
                'issue': 'Compound word inconsistency',
                'text': 'குற்றப்பத்திரிக்கை (multiple contexts)',
                'problem': 'Legal term not normalized to preferred form',
                'should_normalize': 'குற்றப்பத்திரிகை',
                'system_success': '❌ MISSED',
            },
        ],
        'system_accuracy': '35%',
    },
    
    'VERY_HARD': {
        'description': 'Logical reasoning, evidentiary alignment, judicial structure - System catches <20%',
        'examples': [
            {
                'issue': 'Double negative ambiguity creating reasoning gap',
                'text': 'முதல் எதிரி மீது சில சந்தேகங்கள் இருப்பதாகவும், இரண்டாவது எதிரி மீது சந்தேகமே இல்லை என்றும் கூற முடியாது. [But earlier: இரண்டாவது எதிரியின் மீது உள்ள சாட்சியம் போதுமானதாக இல்லை]',
                'problem': 'Double negative obscures logical intent',
                'should_clarify': 'Both accused\'s guilt not proved beyond reasonable doubt',
                'system_success': '❌ FAILED',
                'severity': 'HIGH',
            },
            {
                'issue': 'Reasoning-conclusion alignment',
                'question': 'Does reasoning separately answer: Why A1 not proved? Why A2 not proved?',
                'current_state': 'Both discussed together, acquittal not separately justified',
                'problem': 'Logical structure of judgment unclear',
                'should_verify': 'Each accused independently assessed',
                'system_success': '❌ FAILED',
                'severity': 'HIGH',
            },
            {
                'issue': 'Medical-narrative consistency check',
                'injuries': 'இடது கன்னத்தில் வீக்கம் மற்றும் வலது கையில் சிறிய சிராய்ப்பு',
                'narrative': 'முதல் எதிரி கன்னத்தில் அடித்தார்; இரண்டாவது எதிரி சட்டையைப் பிடித்து இழுத்தார்',
                'check': 'Do injuries match assault narrative?',
                'system_success': '❌ FAILED - no medical-narrative check',
                'severity': 'MEDIUM',
            },
        ],
        'system_accuracy': '<20%',
    },
}

# ============================================================
# TEST CORPUS RECOMMENDATIONS
# ============================================================

TEST_CORPUS_RECOMMENDATIONS = {
    'current_corpus': {
        'composition': 'Heavy on EASY errors, some MEDIUM',
        'problem': 'System appears highly accurate because it catches obvious spelling',
        'weakness_hidden': 'Real gaps (logical, contextual) not visible',
    },
    
    'recommended_new_corpus': {
        'balance': {
            'EASY': '20%',
            'MEDIUM': '30%',
            'HARD': '30%',
            'VERY_HARD': '20%',
        },
        'rationale': 'Should reveal true capability level, not just spelling accuracy',
    },
    
    'corpus_characteristics': {
        'fewer_obvious_typos': 'Remove पापबट्टु-type easy catches',
        'more_logical_errors': 'Add evidentiary contradictions',
        'more_register_issues': 'Add judicial style/formality problems',
        'more_contextual_gaps': 'Add pronoun/object construction problems',
        'reasoning_challenges': 'Add cases requiring logical assessment',
    },
}

