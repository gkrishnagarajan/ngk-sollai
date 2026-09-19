#!/usr/bin/env python3
"""
Level 1-5 Error Detection Rules
PERMANENT DATA COLLECTION FOR LEGAL TAMIL
Created: 2026-08-15
Status: APPEND-ONLY - Never delete, only add new rules
"""

LEVEL_1_SPELLING = {
    'செய்யபட்டு': 'செய்யப்பட்டு',
    'விசாரனை': 'விசாரணை',
    'தயாரிக்கபட்டு': 'தயாரிக்கப்பட்டு',
    'குற்றபத்திரிக்கை': 'குற்றப்பத்திரிகை',
    'விசாரிக்கபட்டுள்ளனர்': 'விசாரிக்கப்பட்டுள்ளனர்',
    'குறியீடு செய்யபட்டுள்ளது': 'குறியீடு செய்யப்பட்டுள்ளது',
    'விளக்கபட்டபோது': 'விளக்கப்பட்டபோது',
    'நிரூபிக்கபடவில்லை': 'நிரூபிக்கப்படவில்லை',
    'விடுதலை செய்யபடுகிறார்கள்': 'விடுதலை செய்யப்படுகிறார்கள்',
    'ரத்து செய்யபடுகிறது': 'ரத்து செய்யப்படுகிறது',
    'அழிக்கபட வேண்டும்': 'அழிக்கப்பட வேண்டும்',
}

LEVEL_2_MORPHOLOGY_SANDHI = {
    'இந்திய தண்டனை சட்டம்': 'இந்திய தண்டனைச் சட்டம்',
    'அரசு தரப்பு': 'அரசுத்தரப்பு',
    'புகார் தாரர்': 'புகார்தாரர்',
    'முன் விரோதம்': 'முன்விரோதம்',
    'வழி மறித்து': 'வழிமறித்து',
    'சட்டையை பிடித்து': 'சட்டையைப் பிடித்து',
    'கையினால் அடித்ததாக': 'கையால் அடித்ததாக',
    'மருத்துவ சாட்சி': 'மருத்துவச் சாட்சி',
    'மருத்துவ கருத்து': 'மருத்துவக் கருத்து',
    'பிணை பத்திரம்': 'பிணைப் பத்திரம்',
    'வழக்கு சொத்துக்கள்': 'வழக்குச் சொத்துக்கள்',
    'எதிரி தரப்பு': 'எதிரித்தரப்பு',
}

LEVEL_3_GRAMMAR = [
    ('ஆகியோர்கள் மீது', 'ஆகியோருக்கு எதிராக'),
    ('அவருடைய வீட்டிற்கு சென்று கொண்டிருந்த சமயத்தில்', 'தனது வீட்டிற்குச் சென்று கொண்டிருந்தபோது'),
]

LEVEL_4_LEGAL_REPHRASING = [
    ('அரசு தரப்பு கற்றறிந்த உதவி அரசு வழக்கறிஞர் வாதிடுகையில்', 
     'அரசுத்தரப்பு சார்பில் ஆஜரான கற்றறிந்த உதவி அரசு வழக்கறிஞர் வாதிடுகையில்'),
    ('எதிரி தரப்பு கற்றறிந்த வழக்கறிஞர்',
     'எதிரித்தரப்பு சார்பில் ஆஜரான கற்றறிந்த வழக்கறிஞர்'),
]

LEVEL_5_LOGICAL_ISSUES = {
    'double_negative': 'சந்தேகமே இல்லை + சந்தேகங்கள் இருப்பதாக',
    'witness_conflict': 'P.W.2 presented as eyewitness but cross-exam shows not witnessed',
    'medical_evidence_mismatch': 'Injuries described vs assault narrative mismatch',
}

# METADATA
RULE_METADATA = {
    'created_date': '2026-08-15',
    'source': 'Legal Tamil Grammar Training Session',
    'level_1_count': len(LEVEL_1_SPELLING),
    'level_2_count': len(LEVEL_2_MORPHOLOGY_SANDHI),
    'level_3_count': len(LEVEL_3_GRAMMAR),
    'level_4_count': len(LEVEL_4_LEGAL_REPHRASING),
    'level_5_count': len(LEVEL_5_LOGICAL_ISSUES),
    'status': 'APPEND-ONLY - No data deletion ever',
}
