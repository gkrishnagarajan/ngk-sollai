# -*- coding: utf-8 -*-
"""
Solai Kaaval - Legal Document Anonymiser (privacy-first)
=========================================================
Phase 1 (anonymise) and Phase 3 (de-anonymise) for NGK Sollai.
Phase 2 (external AI) happens outside this module: only the anonymised
text ever leaves the machine; the mapping never does.

Design principles
-----------------
1. Fail toward OVER-redaction. A missed identifier is a privacy breach;
   an over-redacted token is merely inconvenient.
2. The mapping (token <-> original) is the only thing that can
   re-identify a person. It is returned to the caller and NOTHING is
   retained here. audit() records TYPE and COUNT only, never values.
3. Referential integrity: one entity -> one token everywhere, so the
   external AI reasons about "the same person" and restoration is exact.
4. Protected allowlist shields the legal skeleton (section numbers,
   court types, statutory terms) so the document stays intelligible.
5. Dynamic multi-file architecture: every JSON in detectors/ is loaded
   regardless of count; add a family = drop a file, no engine change.

No third-party dependencies. Pure Python 3 (re, json, os, glob).
"""

import os
import re
import json
import glob

# Mathematical white square brackets U+27E6 / U+27E7 - never occur in
# legal Tamil/English text and are preserved verbatim by external AIs.
TOK_OPEN = "\u27E6"
TOK_CLOSE = "\u27E7"

# ASCII fallback for any tool that mangles Unicode brackets.
TOK_OPEN_ASCII = "[["
TOK_CLOSE_ASCII = "]]"

_BASE = os.path.dirname(os.path.abspath(__file__))


class Detector:
    """A single PII pattern. method is one of: regex | anchor | list."""

    __slots__ = ("id", "token", "method", "lane", "priority", "confidence",
                 "pattern", "regex", "anchors", "max_tokens", "stopwords",
                 "terms", "group", "direction")

    def __init__(self, spec, gazetteers):
        self.id = spec["id"]
        self.token = spec.get("token", spec["id"])
        self.method = spec["method"]
        self.lane = spec.get("lane", "both")
        self.priority = int(spec.get("priority", 100))
        self.confidence = float(spec.get("confidence", 0.9))
        self.pattern = spec.get("pattern", "")
        self.regex = None
        # 0 = replace whole match; >0 = keep match, tokenise only that group
        self.group = int(spec.get("group", 0))
        self.anchors = spec.get("anchors", [])
        self.max_tokens = int(spec.get("max_tokens", 2))
        self.stopwords = set(spec.get("stopwords", []))
        # "after"  -> name follows the anchor (திரு NAME, S/o NAME)
        # "before" -> name precedes the anchor (NAME என்பவர்)
        self.direction = spec.get("direction", "after")
        self.terms = []

        if self.method == "regex":
            self.regex = re.compile(self.pattern, re.UNICODE)
        elif self.method == "anchor":
            # Anchor + following name span. Captures 1..max_tokens tokens
            # after the anchor; \x00 (allowlist sentinel) ends the span so
            # protected legal words are never swept into a name.
            anchor_alt = "|".join(re.escape(a) for a in self.anchors)
            name_tok = r"(?:[A-Z]\.\s*)?[^\s,.;:()\[\]\u27E6\u27E7\x00]+"
            span = r"(?:" + name_tok + r"(?:\s+" + name_tok + r"){0," + \
                   str(self.max_tokens - 1) + r"})"
            if self.direction == "before":
                self.pattern = r"(" + span + r")\s+(?:" + anchor_alt + r")"
            else:
                self.pattern = r"(?<![\u0B80-\u0BFF])(?:" + anchor_alt + \
                               r")\s*[:\-]?\s*(" + span + r")"
            self.regex = re.compile(self.pattern, re.UNICODE)
            self.regex = re.compile(self.pattern, re.UNICODE)
        elif self.method == "list":
            lst = spec.get("list_file")
            if lst and lst in gazetteers:
                self.terms = gazetteers[lst]
            self.terms = sorted(set(self.terms + spec.get("terms", [])),
                                key=len, reverse=True)
            if self.terms:
                alt = "|".join(re.escape(t) for t in self.terms)
                self.pattern = r"(?<![\w\u0B80-\u0BFF])(" + alt + \
                               r")(?![\w\u0B80-\u0BFF])"
                self.regex = re.compile(self.pattern, re.UNICODE)
        else:
            raise ValueError("unknown method: %s" % self.method)


class Anonymiser:
    def __init__(self, base=None):
        self.base = base or _BASE
        self.detectors = []
        self.allow_terms = []
        self._gazetteers = {}
        self._load()

    # ---------- loading ----------
    def _load(self):
        gaz_dir = os.path.join(self.base, "gazetteer")
        for fp in sorted(glob.glob(os.path.join(gaz_dir, "*.json"))):
            with open(fp, encoding="utf-8") as fh:
                data = json.load(fh)
            self._gazetteers[os.path.basename(fp)] = data.get("terms", [])

        allow_dir = os.path.join(self.base, "allowlist")
        terms = []
        for fp in sorted(glob.glob(os.path.join(allow_dir, "*.json"))):
            with open(fp, encoding="utf-8") as fh:
                data = json.load(fh)
            terms.extend(data.get("terms", []))
        # Longest first so multi-word terms are protected before their parts.
        self.allow_terms = sorted(set(terms), key=len, reverse=True)

        det_dir = os.path.join(self.base, "detectors")
        specs = []
        for fp in sorted(glob.glob(os.path.join(det_dir, "*.json"))):
            with open(fp, encoding="utf-8") as fh:
                data = json.load(fh)
            lane = data.get("lane", "both")
            for d in data.get("detectors", []):
                d.setdefault("lane", lane)
                specs.append(d)
        specs.sort(key=lambda s: int(s.get("priority", 100)))
        self.detectors = [Detector(s, self._gazetteers) for s in specs]

    # ---------- allowlist protection ----------
    def _protect(self, text):
        saved = {}
        for i, term in enumerate(self.allow_terms):
            # Never protect a purely-numeric term: it would match inside
            # longer numbers (e.g. "34" inside a vehicle/aadhaar number).
            if term.isdigit():
                continue
            if term and term in text:
                sent = "\x00A%d\x00" % i
                text = text.replace(term, sent)
                saved[sent] = term
        return text, saved

    def _restore_protected(self, text, saved):
        for sent, term in saved.items():
            text = text.replace(sent, term)
        return text

    # ---------- core ----------
    def anonymise(self, text, ascii_tokens=False, lanes=("english", "tamil")):
        """Return (anon_text, mapping).

        mapping: {token: {"original":..., "type":..., "lane":...,
                          "confidence":..., "count":...}}
        """
        o = TOK_OPEN_ASCII if ascii_tokens else TOK_OPEN
        c = TOK_CLOSE_ASCII if ascii_tokens else TOK_CLOSE

        text, protected = self._protect(text)

        mapping = {}                 # token -> info
        by_type_original = {}        # (type, original) -> token
        counters = {}                # type -> int

        def token_for(dtype, original, lane, conf):
            key = (dtype, original)
            if key in by_type_original:
                tok = by_type_original[key]
                mapping[tok]["count"] += 1
                return tok
            counters[dtype] = counters.get(dtype, 0) + 1
            tok = "%s%s_%d%s" % (o, dtype, counters[dtype], c)
            by_type_original[key] = tok
            mapping[tok] = {"original": original, "type": dtype,
                            "lane": lane, "confidence": conf, "count": 1}
            return tok

        # Single ordered pass: each detector runs EXACTLY ONCE, in global
        # priority order. English-lane and Tamil-lane names are distinct
        # detectors (separate processing); 'both'-lane structured detectors
        # serve both and must not run twice.
        want = set(lanes)
        for det in self.detectors:
            if det.regex is None:
                continue
            if det.lane != "both" and det.lane not in want:
                continue
            text = self._apply(det, text, det.lane, token_for)

        text = self._restore_protected(text, protected)
        return text, mapping

    def _apply(self, det, text, lane, token_for):
        # anchor/list capture in group 1; regex uses det.group (0 = whole).
        cap_group = 1 if det.method in ("anchor", "list") else det.group

        def repl(m):
            whole = m.group(0)
            captured = m.group(cap_group) if cap_group else whole
            if captured is None:
                return whole
            original = captured.strip()
            if not original:
                return whole
            if det.method == "anchor":
                toks = original.split()
                if det.direction == "before":
                    # name is nearest the anchor -> scan from the right
                    kept = []
                    for w in reversed(toks):
                        if w in det.stopwords or "\x00" in w:
                            break
                        kept.insert(0, w)
                else:
                    kept = []
                    for w in toks:
                        if w in det.stopwords or "\x00" in w:
                            break
                        kept.append(w)
                original = " ".join(kept).strip(",.;:")
                if not original:
                    return whole
            tok = token_for(det.token, original, lane, det.confidence)
            if cap_group:
                # keep surrounding text (anchor / label), swap only capture
                return whole.replace(original, tok, 1)
            return tok

        return det.regex.sub(repl, text)

    # ---------- restoration ----------
    def deanonymise(self, text, mapping):
        """Exact inverse. Longest tokens first to avoid prefix overlap."""
        for tok in sorted(mapping, key=len, reverse=True):
            text = text.replace(tok, mapping[tok]["original"])
        return text

    # ---------- audit (value-free) ----------
    def audit(self, mapping):
        summary = {}
        for info in mapping.values():
            summary[info["type"]] = summary.get(info["type"], 0) + 1
        return {"total_entities": len(mapping), "by_type": summary}


# module-level convenience singleton
_default = None


def get_anonymiser():
    global _default
    if _default is None:
        _default = Anonymiser()
    return _default


if __name__ == "__main__":
    import sys
    a = get_anonymiser()
    print("Loaded %d detectors, %d allowlist terms."
          % (len(a.detectors), len(a.allow_terms)))
    sample = sys.stdin.read() if not sys.stdin.isatty() else ""
    if sample:
        anon, mp = a.anonymise(sample)
        print("\n--- ANONYMISED ---\n" + anon)
        print("\n--- AUDIT ---\n" + json.dumps(a.audit(mp),
              ensure_ascii=False, indent=2))
