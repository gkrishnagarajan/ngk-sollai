import re

DATE_PAT = r"\d{1,2}[./\-]\d{1,2}[./\-]\d{2,4}"

OPT_SUFFIX = r"(?:[\s\-]*ஆம்\s*தேதியன்று)?"

DATE_WITH_OPT_SUFFIX = r"(?:" + DATE_PAT + r")" + OPT_SUFFIX

SERIES_PAT = re.compile(
    r"(" + DATE_WITH_OPT_SUFFIX + r"(?:\s*,\s*" + DATE_WITH_OPT_SUFFIX + r")+)",
    re.UNICODE
)

SUFFIX_STRIP = re.compile(
    r"(" + DATE_PAT + r")[\s\-]*ஆம்\s*தேதியன்று",
    re.UNICODE
)

ALREADY_DONE_PAT = re.compile(
    r"(" + DATE_WITH_OPT_SUFFIX + r"(?:\s*,\s*" + DATE_WITH_OPT_SUFFIX + r")*)"
    r"\s*மற்றும்\s*" + DATE_WITH_OPT_SUFFIX,
    re.UNICODE
)

def fix_date_series(text):
    protected = set()
    for m in ALREADY_DONE_PAT.finditer(text):
        protected.add((m.start(), m.end()))

    def process_series(m):
        for (ps, pe) in protected:
            if m.start() < pe and m.end() > ps:
                return m.group(0)
        series_str = m.group(1)
        if "மற்றும்" in series_str:
            return series_str
        parts = re.split(r"\s*,\s*", series_str)
        parts = [p.strip() for p in parts if p.strip()]
        parts = [SUFFIX_STRIP.sub(r"\g<1>", p) for p in parts]
        if len(parts) == 1:
            return series_str
        return ", ".join(parts[:-1]) + " மற்றும் " + parts[-1]

    return SERIES_PAT.sub(process_series, text)
