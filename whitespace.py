#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whitespace tidy. Runs LAST, after all other layers.

  - collapse runs of spaces/tabs to one
  - remove space before , . ; : ? ! and closing quote
  - ensure one space after , ; :
  - trim leading/trailing space on each line
"""
import re


def remove_duplicate_phrases(text):
    """Remove consecutively repeated phrases (voice typing errors).
    Works on any repeated sequence of 2+ words.
    Example: இரண்டாவது குற்றஞ்சாட்டப்பட்ட நபர் இரண்டாவது குற்றஞ்சாட்டப்பட்ட நபர்
          -> இரண்டாவது குற்றஞ்சாட்டப்பட்ட நபர்
    """
    import re
    words = text.split()
    changes = []

    # அடுக்குத்தொடர் exceptions
    ADUKKU_EXCEPTIONS = {
        "சிறு", "சின்னச்", "சின்ன", "குறு", "கொஞ்சம்", "துளித்",
        "துளி", "சொட்டு", "அணு", "துகள்", "மெல்ல", "மெது",
        "மிக", "மிகவும்", "ரொம்ப", "பெரிதும்", "அதிகம்",
        "நிறைய", "முழுமையாக", "முற்றிலும்", "நன்கு",
        "பெரு", "நீள்", "மென்", "வெள்", "கரு", "பசு",
        "சுடு", "குளு", "கலகல",
        "மீண்டும்", "அடிக்கடி", "பல", "பெரும்", "நாளுக்கு",
        "ஒன்றன்பின்", "தனித்தனியாக",
    }

    # Try removing repeated sequences of 2 to 8 words
    for length in range(8, 0, -1):
        i = 0
        new_words = []
        while i < len(words):
            # Check if next `length` words repeat
            if i + length * 2 <= len(words):
                phrase1 = words[i:i+length]
                phrase2 = words[i+length:i+length*2]
                if phrase1 == phrase2 and not (
                        length == 1 and phrase1[0] in ADUKKU_EXCEPTIONS
                ):
                    new_words.extend(phrase1)
                    orig = ' '.join(phrase1 + phrase2)
                    corr = ' '.join(phrase1)
                    changes.append({
                        "wrong": orig,
                        "correct": corr,
                        "category": "duplicate_phrase",
                        "source": "whitespace"
                    })
                    i += length * 2
                    continue
            new_words.append(words[i])
            i += 1
        words = new_words
    
    return ' '.join(words), changes

def tidy(text):
    before = text
    out = text
    # Compound word joins — voice-typing splits these with a space
    _COMPOUND_JOINS = [
        ('காவல் நிலை', 'காவல்நிலை'),   # காவல் நிலை -> காவல்நிலை
        ('புறக்காவல் நிலை', 'புறக்காவல்நிலை'),  # புறக்காவல் நிலை -> புறக்காவல்நிலை
        ('நீதி மன்றம்', 'நீதிமன்றம்'),       # நீதி மன்றம் -> நீதிமன்றம்
        ('அலுவலக ம்', 'அலுவலகம்'),         # அலுவலக ம் -> அலுவலகம் (voice split)
        ('வளாக ம்', 'வளாகம்'),                 # வளாக ம் -> வளாகம்
    ]
    for _wrong, _right in _COMPOUND_JOINS:
        out = out.replace(_wrong, _right)
    # Split Tamil words glued without space:
    # Vowel letters (U+0B85-U+0B94) can only appear word-initially in Tamil.
    # When one follows any Tamil char with no space, a word boundary is missing.
    # Vowel-letter word-split — guarded against Tamil transliterations
    # Protect known tokens before splitting, restore after
    _VL_PROTECT = [
        ('டிஎன்', '__TN__'),
        ('டிவிஎஸ்', '__TVS__'),
        ('எக்ஸ்எல்', '__XL__'),
        ('கேஎல்', '__KL__'),
        ('எம்எச்', '__MH__'),
        ('எப்', '__AP__'),
       ('வாய்ப்பில்லை', '__VAIPPILLAI__'),
       ('வாய்ப்பில்லாத', '__VAIPPILLATHA__'),
       ('வாய்ப்பில்லாமல்', '__VAIPPILLAMAL__'),
       ('வாய்ப்பில்லாத', '__VAIPPILLATHA__'),
       ('இல்லாத', '__ILLATHA__'),
       ('இல்லாமல்', '__ILLAMAL__'),
       ('இல்லாவிட்டால்', '__ILLAVITTA__'),
       ('இல்லாவிடில்', '__ILLAVIDIL__'),
       ('இல்லை', '__ILLAI__'),
       ('வில்லை', '__VILLAI__'),
       ('யில்லை', '__YILLAI__'),
       ('கில்லை', '__KILLAI__'),
       ('பில்லை', '__PILLAI__'),
       ('மில்லை', '__MILLAI__'),
       ('தில்லை', '__TILLAI__'),
       ('டில்லை', '__DILLAI__'),
       ('ணில்லை', '__NNILLAI__'),
       ('னில்லை', '__NNILLAI2__'),
       ('ரில்லை', '__RILLAI__'),
       ('லில்லை', '__LLILLAI__'),
       ('ழில்லை', '__ZLILLAI__'),
    ]
    for _tok, _ph in _VL_PROTECT:
        out = out.replace(_tok, _ph)
    out = re.sub(r'([஀-௿])([அ-ஔ])', r'\1 \2', out)
    # Matra-anchored suffix split (safe, zero false positives):
    # ிடம் + consonant = word boundary (idam dative suffix)
    # ில் + consonant = word boundary (locative suffix)
    import re as _re2
    _PAT_IDAM = _re2.compile('ிடம்([க-ஹ])')
    _PAT_IL   = _re2.compile('ில்([க-ஹ])')
    out = _PAT_IDAM.sub('ிடம் ' + r'\1', out)
    out = _PAT_IL.sub('ில் ' + r'\1', out)
    for _tok, _ph in _VL_PROTECT:
        out = out.replace(_ph, _tok)
    out = re.sub(r'[ \t]+', ' ', out)                 # collapse runs
    out = re.sub(r'([\u0B80-\u0BFF])\d+', r'\1', out)  # strip digits glued to Tamil chars
    out = re.sub(r' +([,.;:?!])', r'\1', out)         # no space before punctuation
    out = re.sub(r' +(\u201D)', r'\1', out)           # no space before curly closing quote
    out = re.sub(r'([,;:])(?=[^\s\d])', r'\1 ', out)  # one space after , ; :
    out = re.sub(r'\s+([.,])', r'\1', out)            # no space before . or ,
    out = re.sub(r'\.{2,}', '.', out)                 # collapse .. or ... to .
    # Space after full stop before Tamil word (e.g. கொடுத்துள்ளார்.கடந்த -> கொடுத்துள்ளார். கடந்த)
    # Protect abbreviation tokens before firing, restore after
    _ABB_PROTECT = [
        ('அ.சா.ஆ.', '__ASAA__'),
        ('அ.சா.', '__ASA__'),
        ('எ.சா.ஆ.', '__ESAA__'),
        ('எ.சா.', '__ESA__'),
    ]
    for _abb, _ph in _ABB_PROTECT:
        out = out.replace(_abb, _ph)
    out = re.sub(r'\.(?=[஀-௿])', r'. ', out)  # space after . before Tamil word
    for _abb, _ph in _ABB_PROTECT:
        out = out.replace(_ph, _abb)
    out = re.sub(r',{2,}', ',', out)                  # collapse duplicate commas
    out = re.sub(r'[ \t]+\n', '\n', out)              # trailing space on lines
    out = re.sub(r'\n[ \t]+', '\n', out)              # leading space on lines
    out = re.sub(r'\n{3,}', '\n\n', out)              # max one blank line
    out = out.strip()
    # Remove space between abbreviations and digits: அ.சா. 7 -> அ.சா.7
    out = re.sub(r'(அ\.\u0b9aா\.(?:ஆ\.)?)\ +(\d)', r'\1\2', out)
    # Normalise spoken witness serial: ஆசாரி/ஆச்சாரி <numword> <name> -> அ.சா.<digit> <name>
    from exhibit_norm import _WORD_TO_DIGIT as _W2D
    _ASA_NUMS = sorted(_W2D.keys(), key=len, reverse=True)
    _ASA_PAT = re.compile(
        r'(?:ஆசாரி|ஆச்சாரி|ஆசா)\.?\s+(' +
        '|'.join(re.escape(w) for w in _ASA_NUMS) +
        r')\s+'
    )
    def _asa_repl(m):
        return 'அ.சா.' + _W2D[m.group(1)] + ' '
    out = _ASA_PAT.sub(_asa_repl, out)
    # Normalise spoken exhibit serial: ஆசா ஆ/ஆவணம் <numword|digit> -> அ.சா.ஆ.<digit>
    _ASAA_PAT = re.compile(
        r'(?:ஆசாரி|ஆச்சாரி|ஆசா)\.?\s+(?:ஆவணம்|ஆ)\s+('
        + '|'.join(re.escape(w) for w in _ASA_NUMS)
        + r'|\d+)'
    )
    def _asaa_repl(m):
        tok = m.group(1)
        digit = str(_W2D[tok]) if tok in _W2D else tok
        return 'அ.சா.ஆ.' + digit
    out = _ASAA_PAT.sub(_asaa_repl, out)
    # Remove consecutive duplicate phrases (voice typing errors)
    out, dup_changes = remove_duplicate_phrases(out)
    changes = list(dup_changes)
    if out != before:
        changes.append({"wrong": "spacing", "correct": "normalised",
                        "category": "whitespace", "source": "whitespace"})
    return out, changes

if __name__ == "__main__":
    t = "வழக்கு  ,  மேலும்   கையால் ஓங்கி . இரண்டு   பேர்"
    print(repr(t))
    print(repr(tidy(t)[0]))
