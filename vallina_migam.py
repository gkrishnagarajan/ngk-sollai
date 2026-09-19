#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""வல்லினம் மிகும் விதி"""
import re

ENABLED = True
PULLI   = '\u0BCD'
KU_U    = '\u0BC1'
KU_UU   = '\u0BC2'
KU_I    = '\u0BBF'
KU_II   = '\u0BC0'

VOWEL_ENDINGS = {'\u0BBE','\u0BC8','\u0BC6','\u0BC7','\u0BCA','\u0BCB','\u0BCC'}
PURE_VOWELS   = set('அஆஇஈஉஊஎஏஐஒஓஔ')
VALLINA       = {'க':'க்','ச':'ச்','த':'த்','ப':'ப்'}

VERB_STARTS = {
    'செய்தனர்','செய்தார்','செய்தாள்','செய்தான்',
    'செய்யப்பட்டது','செய்யப்பட்டனர்','செய்யப்பட்டார்',
    'செய்துள்ளனர்','செய்துள்ளார்','செய்து','செய்ய',
    'செய்வதற்கு','செய்வதாக','தெரிவித்தார்','தெரிவித்தனர்',
    'தொடர்ந்தது','தொடங்கியது','தொடங்கினார்',
    'கண்டறியப்பட்டது','கண்டனர்','கண்டார்',
    'கொண்டார்','கொண்டனர்','கொண்டு',
    'கூறினார்','கூறினாள்','கூறினான்','கூறியதாவது',
    'பார்த்தார்','பார்த்தனர்','பார்த்து',
    'போனார்','போனான்','போகிறார்',
    'சென்றார்','சென்றனர்','சென்று',
    'ஆனது','ஆனார்','ஆனாள்','ஆனான்','ஆயிற்று',
}
VERB_PREFIXES = ('செய்','தெரி','தொட','கண்','கொண்','கூறி','பார்','போ','சென்')

def ending_type(word):
    if not word: return 'other'
    last = word[-1]
    if last in PURE_VOWELS:   return 'vowel'
    if last in VOWEL_ENDINGS: return 'vowel'
    if last in (KU_U,KU_UU):  return 'kutriyalukaram'
    if last in (KU_I,KU_II):  return 'kutriyalukaram'
    if last == PULLI and len(word)>=2:
        prev = word[-2]
        if prev=='ம':           return 'consonant_m'
        if prev in 'லரணனளழற': return 'sonorant'
        return 'consonant'
    if '\u0B95'<=last<='\u0BB9': return 'vowel'
    return 'other'

PAST_VERB_PAT = re.compile(r'[஀-௿]+(ந்தது|ட்டது|த்தது|ந்தனர்|ட்டனர்|த்தனர்|ந்தார்|ட்டார்|த்தார்|கிறது|கின்றது|யது|ிற்று|ானது|ன்னது|இனது|்னது|னது)$')

def is_verb_word(word):
    if word in VERB_STARTS: return True
    for p in VERB_PREFIXES:
        if word.startswith(p): return True
    if PAST_VERB_PAT.search(word): return True
    return False

def apply_vallina_migam(text):
    changes = []
    pat = re.compile(r'([\u0B80-\u0BFF]+)\s+([கசதப][\u0B80-\u0BFF]*)')
    def _sub(m):
        w1,w2,full = m.group(1),m.group(2),m.group(0)
        # Skip if W2 already has pulli as second char
        if len(w2)>1 and w2[1]==PULLI: return full
        # Skip if W1 already ends in ANY pulli (re-application guard)
        if w1 and w1[-1]==PULLI: return full
        # Skip if W1 already ends with pulli form of W2 start
        # e.g. வழக்குப் + பதிவு — W1 ends in ப் already
        start = w2[0]
        if w1.endswith(VALLINA.get(start,'@@')): return full
        if start not in VALLINA: return full
        if is_verb_word(w2) and 'ப்பட்' not in w2: return full
        if is_verb_word(w1): return full
        etype = ending_type(w1)
        if etype=='kutriyalukaram':
            new = w1+VALLINA[start]+' '+w2
            changes.append({'wrong':full,'correct':new,'category':'sandhi_vallina','source':'vallina_migam'})
            return new
        if etype=='consonant':
            new = w1+VALLINA[start]+' '+w2
            changes.append({'wrong':full,'correct':new,'category':'sandhi_vallina','source':'vallina_migam'})
            return new
        return full
    out = pat.sub(_sub,text)
    return out, changes
