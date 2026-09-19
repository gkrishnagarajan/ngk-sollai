#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Punctuation aid for Tamil judicial text.

Conservative by design. Only inserts punctuation where the boundary is
grammatically certain:

  1. Closing quote before என்று / என்றும் / எனக் (end of reported speech)
  2. Opening quote after a reporting verb
  3. Comma before clause connectors (மேலும், எனவே, ஆகவே ...)

Does NOT insert full stops. Tamil sentence-boundary detection needs finite-
verb analysis, and a misplaced full stop is worse than none.

Colloquial forms inside quotes are never touched -- verbatim testimony.
"""
import re

ENABLED = True

CLOSERS = ["என்றும்", "என்று", "எனவும்", "எனக்"]
OPENERS = ["கூறி", "திட்டி", "சொல்லி", "கத்தி", "மிரட்டி",
           "வார்த்தைகளால்", "கூறியதாவது", "தெரிவிக்கையில்"]
# Connectors that start NEW sentences in judicial Tamil → full stop
FULLSTOP_CONNECTORS = ["மேலும்", "எனவே", "ஆகவே"]

# Connectors that continue same sentence → comma
COMMA_CONNECTORS = ["ஆனால்", "எனினும்", "மறுபுறம்"]

# Keep CONNECTORS for backward compatibility
CONNECTORS = FULLSTOP_CONNECTORS + COMMA_CONNECTORS

def add_quotes(text):
    """Insert a closing quote before reported-speech markers."""
    out, changes = text, []
    for cl in CLOSERS:
        pat = re.compile(r'(?<!["\u201D])\s+' + re.escape(cl) + r'(?![\u0B80-\u0BFF])')
        def _sub(m):
            changes.append({"wrong": m.group(0).strip(),
                            "correct": '" ' + cl,
                            "category": "punct_quote_close",
                            "source": "punctuation"})
            return '" ' + cl
        out = pat.sub(_sub, out, count=0)
    return out, changes

# Verb endings that signal a COMPLETED sentence (full stop needed before மேலும் etc.)
SENTENCE_ENDINGS = [
    # simple past — all persons/genders
    "னான்", "னாள்", "னார்", "னார்கள்", "னோம்", "னீர்", "னீர்கள்",
    # past with ட்ட
    "ட்டான்", "ட்டாள்", "ட்டார்", "ட்டார்கள்", "ட்டனர்", "ட்டோம்",
    # past with ந்த
    "ந்தான்", "ந்தாள்", "ந்தார்", "ந்தார்கள்", "ந்தனர்",
    # present
    "கிறான்", "கிறாள்", "கிறார்", "கிறார்கள்", "கிறனர்", "கின்றார்",
    # future
    "வான்", "வாள்", "வார்", "வார்கள்", "வர்", "வோம்",
    # neuter past
    "யது", "ந்தது", "ட்டது", "றது",
    # neuter present
    "கிறது", "கின்றது",
    # passive past
    "யப்பட்டது", "ப்பட்டது", "யப்பட்டார்", "ப்பட்டார்",
    "யப்பட்டனர்", "ப்பட்டனர்",
    # present-perfect (உள்ள series) — most common in judicial Tamil
    "உள்ளார்", "உள்ளாள்", "உள்ளான்", "உள்ளனர்", "உள்ளது",
    "ள்ளார்", "ள்ளனர்", "ள்ளது",
    # completive (விட்ட series)
    "விட்டார்", "விட்டான்", "விட்டாள்", "விட்டனர்", "விட்டது",
    # obligative / prohibitive
    "வேண்டும்", "கூடாது", "யாது",
    # formal judicial endings
    "றார்", "றனர்", "றது",
]

# Clause-initial words that confirm a NEW sentence after a வினைமுற்று
CLAUSE_STARTERS = [
    # demonstrative pronouns
    "தன்", "தனது", "அவர்", "அவரது", "அவர்கள்", "அவர்களது",
    "இவர்", "இவரது", "இவர்கள்",
    "அது", "இது", "அதன்", "இதன்", "அதை", "இதை",
    "அவ்வாறு", "இவ்வாறு", "அவ்விதம்", "இவ்விதம்",
    # party nouns — new sentence often starts with party reference
    "மனுதாரர்", "எதிர்மனுதாரர்", "வாதி", "பிரதிவாதி",
    "குற்றஞ்சாட்டப்பட்ட", "குற்றவாளி", "சாட்சி",
    # connectors not already in FULLSTOP_CONNECTORS
    "அதனால்", "எனவே", "ஆனால்", "எனினும்",
    "அதன்படி", "அதன்மேல்", "அதற்கு",
    # demonstrative adjectives
    "அந்த", "இந்த", "அவ்வகை", "இவ்வகை",
    # personal pronouns
    "அவன்", "அவள்", "நான்", "நாம்", "நீ", "நீர்",
    # temporal/manner adverbs that start main clauses
    "உடனடியாக", "உடனே", "தொடர்ந்து", "அதனிடையே", "பின்னர்",
    "மேலும்", "அவ்வேளையில்", "சிறிது நேரத்தில்",
    # location references that start new sentences
    "அங்கிருந்து", "அங்கு", "அங்கே", "இங்கிருந்து", "இங்கு",
    "அவ்விடத்திலிருந்து", "அவ்விடத்தில்",
    # discourse connector starting new sentence in judicial prose
    "மேற்படி",
    # participial adjective opening a new clause about an injured party
    "காயமடைந்த",
]

# Interrogative "ஆ" endings — built from SENTENCE_ENDINGS + ஆ
def _to_interrogative(ending):
    """Tamil sandhi: interrogative 'ஆ' fuses with the final pulli or
    vowel sign of the base word, replacing it rather than appending."""
    if ending[-1] in ("\u0bcd", "\u0bc1", "\u0bc2"):  # pulli, u, uu
        return ending[:-1] + "ா"
    return ending + "ா"

INTERROGATIVE_ENDINGS = sorted(
    set([_to_interrogative(e) for e in SENTENCE_ENDINGS] + ["தா", "மா"]),
    key=len, reverse=True
)

def fix_interrogative_punctuation(text):
    """Ensure clauses ending in the interrogative 'ஆ' sound get a '?'
    instead of a comma or full stop, and are never comma-linked as
    a run-on sentence."""
    changes = []
    out = text

    # Replace a comma right after an interrogative ending with '?'
    for end in INTERROGATIVE_ENDINGS:
        pat = re.compile(re.escape(end) + r"\s*,")
        def _repl(m, end=end):
            changes.append({"wrong": m.group(0), "correct": end + "?",
                             "category": "punct_interrogative",
                             "source": "punctuation"})
            return end + "?"
        out = pat.sub(_repl, out)

    # Ensure the clause/sentence-final terminal punctuation is '?' not '.'
    for end in INTERROGATIVE_ENDINGS:
        pat = re.compile(re.escape(end) + r"(\s*)\.(?=\s|$)")
        def _repl2(m, end=end):
            changes.append({"wrong": end + m.group(1) + ".",
                             "correct": end + m.group(1) + "?",
                             "category": "punct_interrogative",
                             "source": "punctuation"})
            return end + m.group(1) + "?"
        out = pat.sub(_repl2, out)

        # missing terminal punctuation at true end of text
        if out.rstrip().endswith(end):
            changes.append({"wrong": "", "correct": "?",
                             "category": "punct_interrogative",
                             "source": "punctuation"})
            out = out.rstrip() + "?"


    # Add '?' before embedded question markers when preceded by ஆ ending
    EMBED_MARKERS = ["என்பதில்", "என்பது", "என்பதை", "என்ற", "என்பதற்கு"]
    for end in INTERROGATIVE_ENDINGS:
        for mk in EMBED_MARKERS:
            pat = re.compile(re.escape(end) + r"(\s+)" + re.escape(mk))
            def _repl3(m, end=end, mk=mk):
                changes.append({"wrong": end + m.group(1) + mk,
                                "correct": end + "?" + m.group(1) + mk,
                                "category": "punct_interrogative",
                                "source": "punctuation"})
                return end + "?" + m.group(1) + mk
            out = pat.sub(_repl3, out)
    return out, changes


def _preceding_word_is_complete_verb(before_text):
    """Check if the text before a connector ends with a complete verb form."""
    before_text = before_text.rstrip()
    for ending in SENTENCE_ENDINGS:
        if before_text.endswith(ending):
            return True
    return False

def add_connector_commas(text):
    """Insert full stop before sentence-starting connectors (மேலும், எனவே, ஆகவே).
    Insert comma before clause-continuing connectors (ஆனால், எனினும், மறுபுறம்)."""
    out, changes = text, []

    # Full stop connectors — always start new sentence in judicial Tamil
    for cn in FULLSTOP_CONNECTORS:
        pat = re.compile(r'(?<![,.;:?!\u201D"])(?<!\s)\s+' + re.escape(cn) + r'(?=\s)')
        def _sub(m, cn=cn):
            changes.append({"wrong": m.group(0).strip(),
                            "correct": ". " + cn,
                            "category": "punct_fullstop",
                            "source": "punctuation"})
            return ". " + cn
        out = pat.sub(_sub, out)

    # Comma connectors — continue same sentence
    for cn in COMMA_CONNECTORS:
        pat = re.compile(r'(?<![,.;:?!\u201D"])(?<!\s)\s+' + re.escape(cn) + r'(?=\s)')
        def _sub(m, cn=cn):
            changes.append({"wrong": m.group(0).strip(),
                            "correct": ", " + cn,
                            "category": "punct_comma",
                            "source": "punctuation"})
            return ", " + cn
        out = pat.sub(_sub, out)

    return out, changes


AFTER_COMMA = [
    # Causal / reason markers
    "காரணமாக",
    "காரணத்தால்",
    "நிமித்தம்",
    # Scope / inclusion markers
    "குட்பட்ட",
    "உட்பட",
    "தவிர",
    "தவிர்த்து",
    # Temporal markers
    "முன்னர்",
    "முன்பு",
    "பின்னர்",
    "பின்பு",
    "அதற்கு பின்",
    "அதன் பின்",
    "இதற்கு முன்",
    # Concessive / contrast
    "எனினும்",
    "ஆயினும்",
    "என்றாலும்",
    "அப்படியிருந்தும்",
    "இருப்பினும்",
    # Conditional
    "என்றால்",
    "ஆனால்",
    "அதனால்",
    # Manner / basis
    "அடிப்படையில்",
    "பார்க்கும்போது",
    "கருதும்போது",
    "நோக்கும்போது",
    # Additive
    "மேலும்",
    "அதுமட்டுமின்றி",
    "இதுதவிர",
    # Conclusive
    "எனவே",
    "ஆகவே",
    "இவ்வாறு",
    "இதனால்",
    "இதன்படி",
    "ஆதலால்",
    # Evidential
    "என்பது தெரிகிறது",
    "என்பது வெளிப்படுகிறது",
    # Witness statement introducer
    "சாட்சியத்தில்",
]
SUFFIX_COMMA = [
    "போது",
    "தால்",
    "தாலும்",
    "என்பதால்",
    "என்றதால்",
    "ஆகையால்",
    "படியால்",
    "தோடு",
]

def add_clause_commas(text):
    out, changes = text, []
    for w in AFTER_COMMA:
        pat = re.compile(r"(?<![\u0B80-\u0BFF])" + re.escape(w) + r"(?![\u0B80-\u0BFF,])(?=\s)")
        def _s(m):
            changes.append({"wrong": w, "correct": w + ",",
                            "category": "punct_clause_comma", "source": "punctuation"})
            return w + ","
        out = pat.sub(_s, out)
    for suf in SUFFIX_COMMA:
        pat = re.compile(r"([\u0B80-\u0BFF]+" + re.escape(suf) + r")(?![,\u0B80-\u0BFF])(?=\s)")
        def _s2(m):
            changes.append({"wrong": m.group(1), "correct": m.group(1) + ",",
                            "category": "punct_clause_comma", "source": "punctuation"})
            return m.group(1) + ","
        out = pat.sub(_s2, out)
    return out, changes



# --- v3: participle and clause-final commas (from marked-up judgment) ---
# Only fire when the NEXT word starts a new clause, to avoid mid-clause commas.
PARTICIPLE_COMMA = [
    "\u0B8F\u0BB1\u0BCD\u0BAA\u0B9F\u0BC1\u0BA4\u0BCD\u0BA4\u0BBF",   # ஏற்படுத்தி
    "\u0B8E\u0B9F\u0BC1\u0BA4\u0BCD\u0BA4\u0BC1",                        # எடுத்து
    "\u0BA4\u0BCA\u0B9F\u0BB0\u0BCD\u0B9A\u0BCD\u0B9A\u0BBF\u0BAF\u0BBE\u0B95",  # தொடர்ச்சியாக
]

# words that legitimately follow these participles WITHOUT a comma
_NO_COMMA_NEXT = {
    "\u0BAE\u0BB1\u0BCD\u0BB1\u0BC1\u0BAE\u0BCD",      # மற்றும்
    "\u0B85\u0BA4\u0BC1",                                   # அது
}

def add_participle_commas(text):
    out, changes = text, []
    for w in PARTICIPLE_COMMA:
        pat = re.compile(r"(?<![\u0B80-\u0BFF])" + re.escape(w) +
                         r"(?![\u0B80-\u0BFF,])(\s+)([\u0B80-\u0BFF]+)")
        def _s(m):
            nxt = m.group(2)
            if nxt in _NO_COMMA_NEXT:
                return m.group(0)
            changes.append({"wrong": w, "correct": w + ",",
                            "category": "punct_participle_comma",
                            "source": "punctuation"})
            return w + "," + m.group(1) + nxt
        out = pat.sub(_s, out)

    # -தாகவும் / -ளதாகவும் before மேலும்  ->  comma
    pat = re.compile(r"([\u0B80-\u0BFF]+\u0BA4\u0BBE\u0B95\u0BB5\u0BC1\u0BAE\u0BCD)"
                     r"(?![,\u0B80-\u0BFF])(?=\s)")
    def _s2(m):
        changes.append({"wrong": m.group(1), "correct": m.group(1) + ",",
                        "category": "punct_clause_comma", "source": "punctuation"})
        return m.group(1) + ","
    out = pat.sub(_s2, out)
    return out, changes



# --- opening quote after a reporting verb, paired with an existing closer ---
REPORTING_VERBS = [

    "\u0B95\u0BBE\u0BA3\u0BCD\u0BAA\u0BBF\u0BA4\u0BCD\u0BA4\u0BC1", # காண்பித்து
    "\u0B95\u0BC2\u0BB1\u0BBF",                                          # கூறி
    "\u0B9A\u0BCA\u0BB2\u0BCD\u0BB2\u0BBF",                            # சொல்லி
    "\u0BA4\u0BBF\u0B9F\u0BCD\u0B9F\u0BBF",                            # திட்டி
    "\u0BAE\u0BBF\u0BB0\u0B9F\u0BCD\u0B9F\u0BBF",                     # மிரட்டி
    "\u0B95\u0BA4\u0BCD\u0BA4\u0BBF",                                   # கத்தி
]

def add_open_quotes(text):
    """For every closing quote, open one after the nearest preceding
    reporting verb. Only fires when that verb is found and no quote is
    already open, so it fails by omission rather than misplacement."""
    out, changes = text, []
    idx = 0
    while True:
        c = out.find('"', idx)
        if c == -1:
            break
        before = out[:c]
        if before.count('"') % 2 == 1:      # already paired
            idx = c + 1
            continue
        best = -1; bestv = None
        for v in REPORTING_VERBS:
            j = before.rfind(v + " ")
            if j > best:
                best, bestv = j, v
        if best == -1:
            idx = c + 1
            continue
        ins = best + len(bestv) + 1
        # Skip if opening quote already present
        if out[ins:ins+1] == '"' or out[ins:ins+2] == ' "':
            idx = c + 1
            continue
        out = out[:ins] + '"' + out[ins:]
        # ensure a space separates the verb from the opening quote
        if ins > 0 and out[ins-1] != ' ':
            out = out[:ins] + ' ' + out[ins:]
        changes.append({"wrong": bestv, "correct": bestv + ' "',
                        "category": "punct_quote_open", "source": "punctuation"})
        idx = c + 2
    return out, changes


def add_final_fullstop(text):
    """Add a full stop at the end of the text if missing."""
    out = text.rstrip()
    changes = []
    if out and out[-1] not in '.!?':
        out = out + '.'
        changes.append({"wrong": "", "correct": ".",
                        "category": "punct_final_fullstop",
                        "source": "punctuation"})
    return out, changes


def normalize_ipc_subclauses(text):
    """506, 2 -> 506(ii) | 304, 1 -> 304(i)
    Lowercase Roman numerals per court citation convention.
    """
    _roman = {1: "i", 2: "ii", 3: "iii", 4: "iv", 5: "v"}
    def _repl(m):
        sec = m.group(1)
        sub = int(m.group(2))
        return sec + "(" + _roman.get(sub, str(sub)) + ")"
    pat = r"(506|304)\s*,\s*([1-5])(?![0-9])"
    text = re.sub(pat, _repl, text)
    return text


def remove_trailing_font_i(text):
    """Remove stray இ appended to Tamil words (font-switching artifact).
    செய்யப்பட்டுள்ளதுஇ -> செய்யப்பட்டுள்ளது
    """
    result = []
    chars = list(text)
    i = 0
    while i < len(chars):
        if chars[i] == "இ" and i > 0 and chars[i-1] not in (" ", "\t", "\n", "/"):
            # Check if next char is space/end — font artifact
            if i + 1 >= len(chars) or chars[i+1] in (" ", "\t", "\n", ".", ",", "!", "?"):
                i += 1
                continue
        result.append(chars[i])
        i += 1
    return "".join(result)



# Enumerative ம்-ending connectors in indirect speech chains
# Grammar: உம்மைத்தொகை pattern — each reported clause ends with என்றும் / எனவும் etc.
# A comma is needed after each occurrence (including before the final verb).
# Rule fires ONLY on words ending in ம் — never on என்று / எனக் (no ம்).
ENUM_CLOSERS = ["என்றும்", "எனவும்", "என்பதும்", "ஆகவும்", "என்னவும்"]

def add_enumerative_commas(text):
    """Insert comma after enumerative ம்-ending indirect speech connectors.
    Fires only when the connector is followed by a space + Tamil text (not end of sentence).
    Also fires when followed by a space + the final reporting verb cluster.
    Does NOT fire if comma already present after the word.
    """
    import re
    out, changes = text, []
    for word in ENUM_CLOSERS:
        # Match word not already followed by comma, followed by space + any Tamil char
        pat = re.compile(
            re.escape(word) +
            r"(?!,)" +           # no comma already
            r"(?=\s+[\u0B80-\u0BFF])"  # followed by space + Tamil text
        )
        def _sub(m, word=word):
            changes.append({
                "wrong": word,
                "correct": word + ",",
                "category": "punct_enumerative_comma",
                "source": "punctuation"
            })
            return word + ","
        out = pat.sub(_sub, out)
    return out, changes


def add_appositive_commas(text):
    """Insert comma after என்பவர்/என்பவள்/என்பவன் when followed by a new clause subject."""
    changes = []
    # Triggers: appositive endings
    APP_ENDS = ['என்பவர்', 'என்பவள்', 'என்பவன்', 'என்பவரை', 'என்பவரின்', 'என்பவரும்']
    # Following clause starters that signal a new subject/clause
    CLAUSE_STARTERS = [
        'மேற்படி', 'அந்த', 'இந்த', 'அவர்', 'இவர்', 'அவள்', 'இவள்',
        'அவன்', 'இவன்', 'அவர்கள்', 'இவர்கள்', 'அது', 'இது',
        'தான்', 'கடந்த', 'தற்போது', 'பின்னர்', 'அதன்', 'தனது',
    ]
    import re
    for end in APP_ENDS:
        for starter in CLAUSE_STARTERS:
            pat = re.compile(
                r'(' + re.escape(end) + r')(\s+)(' + re.escape(starter) + r')'
            )
            def _repl(m, e=end, s=starter):
                changes.append({
                    'wrong':    m.group(0),
                    'correct':  m.group(1) + ',' + m.group(2) + m.group(3),
                    'category': 'punctuation',
                    'source':   'appositive_comma',
                })
                return m.group(1) + ',' + m.group(2) + m.group(3)
            text = pat.sub(_repl, text)
    return text, changes

def add_sentence_boundary_fullstop(text):
    """Insert full stop where a வினைமுற்று (finite verb) is followed by a
    clause-initial word, indicating a missing sentence boundary.

    Tamil grammar rule: வினைமுற்று is sentence-final by definition.
    Two finite verbs in sequence without punctuation = missing full stop.

    Safety guards:
    - Does not fire inside quoted speech ("...")
    - Requires the clause starter to be a known CLAUSE_STARTERS word
    - Negative lookbehind prevents double punctuation
    - Sorts endings longest-first to prevent partial matches
    """
    changes = []

    # Split on quoted segments — never touch inside quotes
    segments = re.split(r'(".*?")', text, flags=re.DOTALL)
    result_parts = []

    for seg in segments:
        if seg.startswith('"') and seg.endswith('"'):
            result_parts.append(seg)
            continue

        out = seg
        endings_sorted = sorted(SENTENCE_ENDINGS, key=len, reverse=True)
        starters_alt = "|".join(re.escape(s) for s in
                                sorted(CLAUSE_STARTERS, key=len, reverse=True))
        for ending in endings_sorted:
            pat = re.compile(
                r'(?<![.!?,;:"”])(' 
                + re.escape(ending)
                + r')(\s+)('
                + starters_alt
                + r')(?=[\s஀-௿])'
            )
            def _repl(m, _e=ending):
                new_text = m.group(1) + '. ' + m.group(3)
                changes.append({
                    "wrong": m.group(1) + m.group(2) + m.group(3),
                    "correct": new_text,
                    "category": "punct_vinaimutru_boundary",
                    "source": "punctuation"
                })
                return new_text
            out = pat.sub(_repl, out)
        result_parts.append(out)

    return "".join(result_parts), changes



def add_namelist_commas(text):
    """Insert commas and மற்றும் in name lists before ஆகியோர்.
    Pattern: [list-introducer] NAME NAME NAME ... ஆகியோர்
    Result:  [list-introducer] NAME, NAME, NAME மற்றும் NAME ஆகியோர்
    Skips lists where மற்றும் is already present.
    """
    import re as _re
    _INTRO = _re.compile(
        r'(?:சாட்சிகளான'  # சாட்சிகளான
        r'|சாட்சிகள்'           # சாட்சிகள்
        r'|ஆகியோர்களான'  # ஆகியோர்களான
        r'|என்பவர்களான'  # என்பவர்களான
        r')\s+'
    )
    _AAKIYOOR = _re.compile(
        r'\s+ஆகியோர(?:்(?:களை|களின்|களுக்கு|கள்|)|ை|)'  # ஆகியோர் or ஆகியோரை
    )
    _MATRRUM = 'மற்றும்'  # மற்றும்

    changes = []
    result = text
    offset = 0

    for m_intro in _INTRO.finditer(text):
        m_aak = _AAKIYOOR.search(text, m_intro.end())
        if not m_aak:
            continue
        intro_end = m_intro.end()
        aak_start = m_aak.start()
        segment = text[intro_end:aak_start].strip()
        if ',' in segment:
            continue
        # Split on existing மற்றும் if present, else treat last word as final
        if _MATRRUM in segment:
            parts = segment.split(_MATRRUM, 1)
            pre_words = parts[0].strip().split()
            last_name = parts[1].strip()
        else:
            pre_words = segment.split()
            last_name = pre_words.pop()
        if len(pre_words) < 2:
            continue
        new_seg = ', '.join(pre_words) + ' ' + _MATRRUM + ' ' + last_name
        original = text[intro_end:aak_start]
        result = result[:intro_end + offset] + new_seg + result[aak_start + offset:]
        offset += len(new_seg) - len(original)
        changes.append({"wrong": original.strip(), "correct": new_seg,
                        "category": "namelist_comma", "source": "punctuation"})
    return result, changes


def remove_compound_verb_comma(text):
    """Remove spurious comma between verbal participle and விட்டார் etc.
    e.g. "ஏற்படுத்தி, விட்டார்" -> "ஏற்படுத்திவிட்டார்"
    Pattern: Tamil_word ending in ி + comma + space + விட்...
    """
    import re as _re
    changes = []
    pat = _re.compile(r'([஀-௿]+ி),\s+(விட்[஀-௿]+)')
    def _repl(m):
        combined = m.group(1) + m.group(2)
        changes.append({'wrong': m.group(0), 'correct': combined,
                        'category': 'punctuation', 'source': 'punctuation'})
        return combined
    out = pat.sub(_repl, text)
    return out, changes


def add_participial_clause_comma(text):
    """Insert comma between a participial verb and a following clause-starter adverb.
    e.g. "ஏற்பட்டு உடனடியாக" -> "ஏற்பட்டு, உடனடியாக"
    Pattern: verb ending in ்து/ந்து/ட்டு/ற்று + space + clause-starter adverb
    """
    import re as _re
    changes = []
    _ADVERBS = '|'.join([
        'உடனடியாக',   # உடனடியாக
        'உடனே',                             # உடனே
        'தொடர்ந்து',  # தொடர்ந்து
        'உடனுடனே',          # உடனுடனே
    ])
    pat = _re.compile(
        r'([஀-௿]+(?:்து|ந்து'
        r'|ட்டு|ற்று))'
        r'\s+(' + _ADVERBS + r')'
    )
    def _repl(m):
        new = m.group(1) + ', ' + m.group(2)
        changes.append({'wrong': m.group(0), 'correct': new,
                        'category': 'punct_participial_comma', 'source': 'punctuation'})
        return new
    out = pat.sub(_repl, text)
    return out, changes


def add_witness_series_commas(text):
    """Insert commas and மற்றும் between witness units in a series.
    Unit = [optional title words] (அ|எ).சா.N [name]
    Comma goes AFTER name, before next unit title words.
    Termination: ஆகியோர் (any inflection).
    """
    import re as _re
    changes = []

    # Match full unit: optional title words + witness marker + name word
    # Title words = any Tamil words that are not அ.சா./எ.சா.
    _UNIT = _re.compile(
        r'((?:(?!(?:அ|எ)\.சா\.)\S+\s+)*)'  # group1: title words (greedy, stops at marker)
        r'((?:அ|எ)\.சா\.\d+)'               # group2: witness marker
        r'(?:\s+((?!ஆகியோர்)(?!மற்றும்)(?![அஎ]\.சா\.)\S+))?'  # group3: name (optional)
    )
    _AAKIYOOR = _re.compile(
        r'\s+ஆகியோர்(?:களை|களின்|களுக்கு|கள்|ை|)'
    )
    _MATRRUM = 'மற்றும்'

    out = text

    # Find all units in text
    all_units = list(_UNIT.finditer(out))
    if len(all_units) < 2:
        return out, changes

    # Group consecutive units (end of one close to start of next)
    series_groups = []
    current = [all_units[0]]
    for i in range(1, len(all_units)):
        # consecutive if start of this unit = end of previous unit (allowing whitespace)
        gap = all_units[i].start() - all_units[i-1].end()
        if gap <= 1:
            current.append(all_units[i])
        else:
            if len(current) >= 2:
                series_groups.append(current)
            current = [all_units[i]]
    if len(current) >= 2:
        series_groups.append(current)

    offset = 0
    for group in series_groups:
        series_start = group[0].start() + offset
        series_end = group[-1].end() + offset

        # Check ஆகியோர் terminator immediately after series
        after = out[series_end:]
        if not _AAKIYOOR.match(after):
            continue

        series_text = out[series_start:series_end]
        if ',' in series_text:
            continue

        # Build units from regex groups
        units = []
        for u in group:
            title = u.group(1).strip()
            # strip மற்றும் from title (already-present connector)
            title = title.replace('மற்றும்', '').strip()
            marker = u.group(2)
            name = u.group(3)
            parts = []
            if title:
                parts.append(title)
            parts.append(marker)
            if name:
                parts.append(name)
            units.append(' '.join(parts))

        if len(units) < 2:
            continue

        new_series = ', '.join(units[:-1]) + ' மற்றும் ' + units[-1]
        original = out[series_start:series_end]
        out = out[:series_start] + new_series + out[series_end:]
        offset += len(new_series) - len(original)
        changes.append({
            'wrong': original.strip(),
            'correct': new_series.strip(),
            'category': 'witness_series_comma',
            'source': 'punctuation'
        })

    return out, changes


def apply_punctuation(text, quotes=True, commas=True):
    out, changes = text, []
    out = remove_trailing_font_i(out)
    out = normalize_ipc_subclauses(out)
    if commas:
        out, c = add_connector_commas(out); changes += c
        out, c = add_clause_commas(out); changes += c
        out, c = add_participle_commas(out); changes += c
        out, c = add_enumerative_commas(out); changes += c
        out, c = add_appositive_commas(out); changes += c
        out, c = add_namelist_commas(out); changes += c
        out, c = add_witness_series_commas(out); changes += c
        out, c = add_participial_clause_comma(out); changes += c
    if quotes:
        # out, c = add_quotes(out); changes += c  # disabled: misplaced quotes
        pass
        # out, c = add_open_quotes(out); changes += c  # disabled: misplaced quotes
    out, c = remove_compound_verb_comma(out); changes += c
    out, c = add_sentence_boundary_fullstop(out); changes += c
    out, c = fix_interrogative_punctuation(out); changes += c
    out, c = add_final_fullstop(out); changes += c
    if out.count('"') % 2 == 1:
        out = out.replace('"', '')
        changes = [c for c in changes if 'quote' not in c.get('category','')]
    return out, changes


if __name__ == "__main__":
    t = ("\u0B89\u0B99\u0BCD\u0B95\u0BB3\u0BC8 \u0B95\u0BC6\u0BBE\u0BB2\u0BCD\u0BB2\u0BBE\u0BAE\u0BB2\u0BCD "
         "\u0BB5\u0BBF\u0B9F\u0BAE\u0BBE\u0B9F\u0BCD\u0B9F\u0BC7\u0BA9\u0BCD \u0B8E\u0BA9\u0BCD\u0BB1\u0BC1 "
         "\u0B95\u0BC6\u0BBE\u0BB2\u0BC8 \u0BAE\u0BBF\u0BB0\u0B9F\u0BCD\u0B9F\u0BB2\u0BCD "
         "\u0BB5\u0BBF\u0B9F\u0BC1\u0BA4\u0BCD\u0BA4\u0BC1 \u0BAE\u0BC7\u0BB2\u0BC1\u0BAE\u0BCD "
         "\u0BAE\u0BC7\u0BB1\u0BCD\u0BAA\u0B9F\u0BBF \u0BB5\u0BBF\u0BB1\u0B95\u0BC1")
    o, ch = apply_punctuation(t)
    print("IN :", t)
    print("OUT:", o)
    print("changes:", len(ch))
    for c in ch: print("   ", c["category"], "|", c["wrong"], "->", c["correct"])
