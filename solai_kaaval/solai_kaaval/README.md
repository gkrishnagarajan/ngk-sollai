# Solai Kaaval — Legal Document Anonymiser (Phase 1 + Phase 3)

Privacy-first, reversible anonymiser for NGK Sollai. Phase 2 (external AI)
happens outside this module — only the anonymised text ever leaves the
machine; the mapping never does.

## Design guarantees
- **Fail toward over-redaction.** A missed identifier is a breach; an
  over-redacted token is only inconvenient.
- **Exact reversibility.** `deanonymise(anonymise(x)) == x` (round-trip
  tested).
- **Zero retention.** The engine returns the mapping to the caller and
  keeps nothing. `audit()` records type + count only, never values.
- **Referential integrity.** One entity → one token everywhere.
- **Protected allowlist.** Section numbers, court types and statutory
  terms are shielded so the document stays legally intelligible.

## Layout (dynamic multi-file — add a family = drop a JSON)
```
solai_kaaval/
├── engine.py            core: Anonymiser.anonymise / .deanonymise / .audit
├── detectors/           one JSON per PII family (loaded regardless of count)
│     govid financial contact vehicle survey case dates address
│     person_en person_ta place
├── allowlist/           protected legal skeleton (never redacted)
│     courts statutory_terms
└── gazetteer/           name lists referenced by list-detectors
      tn_districts tn_stations
```

## Detection methods
- `regex` — structured PII (Aadhaar, PAN, IFSC, vehicle, case no., dates).
  Optional `"group": N` tokenises only that capture (e.g. keep "Account
  No." label, tokenise the number).
- `anchor` — name span next to an anchor word. `"direction":"after"`
  (திரு NAME / S/o NAME) or `"before"` (NAME என்பவர்). `stopwords` trim
  the span so only the name is taken.
- `list` — exact gazetteer match (districts, stations).

## Tokens
Default `⟦TYPE_N⟧` (U+27E6/27E7 — never occur in legal text, preserved by
external AIs). Call `anonymise(text, ascii_tokens=True)` for `[[TYPE_N]]`
if a tool mangles Unicode.

## Usage
```python
from engine import Anonymiser
a = Anonymiser()                       # loads all JSONs from this folder
anon, mapping = a.anonymise(text)      # Phase 1
# ... send `anon` to any external AI, bring the output back ...
restored = a.deanonymise(ai_output, mapping)   # Phase 3
report = a.audit(mapping)              # {type: count}, no values
```

## Known refinements (safe — privacy already holds)
- A 12-digit **contiguous** number is labelled AADHAAR even if it is a
  bank account (both are redacted and reversible; only the label differs).
- STREET / NAGAR detectors capture the single token before the keyword —
  adequate, will be tightened with an address-block detector later.
- A district inside a court name (சேலம் மாவட்ட நீதிமன்றம்) has the
  district redacted — correct for privacy.

## Tamil suffix join
If an external AI glues a case suffix to a token (⟦PERSON_1⟧யின்),
restoration is literal; run the final text through the NGK Sollai
punarchi pipeline to clean the join.

## Next build steps
1. Flask routes `/anonymise` and `/deanonymise` in `app_integrated.py`
   (before `if __name__ == '__main__':`).
2. Homepage panel: input, Anonymise / De-anonymise, editable mapping
   table, Download key / Load key, Aadhaar & case-number toggles.
3. Expand gazetteers (full station list) and org detector — one file each.
