#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Date Timeline Checker for NGK Sollai.
Extracts all dates from judicial text and checks for logical order.
Flags inconsistencies as warnings (detect only, not auto-corrected).
"""
import re
from datetime import datetime

DATE_PAT = re.compile(r'(\d{2})\.(\d{2})\.(\d{4})')

DATE_CONTEXT = {
    'incident': ['சம்பவம்', 'நிகழ்ந்தது', 'நடந்தது', 'தாக்கினார்', 'கொன்றார்', 'நிகழ்ந்த'],
    'fir': ['புகார்', 'வழக்கு பதிவு', 'குற்ற எண்', 'காவல் நிலைய', 'பதிவு செய்யப்பட்டது'],
    'arrest': ['கைது', 'கைதுசெய்யப்பட்டார்', 'கைது செய்யப்பட்டார்'],
    'chargesheet': ['இறுதி அறிக்கை', 'குற்றப்பத்திரிகை', 'தாக்கல்'],
    'trial': ['விசாரணை', 'வாதம்', 'சாட்சி'],
    'judgment': ['தீர்ப்பு', 'உத்தரவு', 'தண்டனை'],
}

def extract_dates_with_context(text):
    dates_found = []
    sentences = re.split(r'\.(?!\d)|\n', text)
    for sent in sentences:
        for m in DATE_PAT.finditer(sent):
            try:
                day   = int(m.group(1))
                month = int(m.group(2))
                year  = int(m.group(3))
                if month > 12 or day > 31:
                    continue
                date_obj = datetime(year, month, day)
                context_type = 'unknown'
                for ctx_type, keywords in DATE_CONTEXT.items():
                    if any(kw in sent for kw in keywords):
                        context_type = ctx_type
                        break
                dates_found.append({
                    'date': date_obj,
                    'date_str': m.group(0),
                    'context': context_type,
                    'sentence': sent.strip()[:100]
                })
            except ValueError:
                continue
    return dates_found

def check_timeline(text):
    warnings = []
    dates = extract_dates_with_context(text)
    if len(dates) < 2:
        return warnings

    incidents = [d for d in dates if d['context'] == 'incident']
    firs      = [d for d in dates if d['context'] == 'fir']
    arrests   = [d for d in dates if d['context'] == 'arrest']

    for fir in firs:
        for incident in incidents:
            if fir['date'] < incident['date']:
                warnings.append({
                    'type': 'timeline_error',
                    'message': 'FIR date %s is BEFORE incident date %s' % (fir['date_str'], incident['date_str']),
                    'severity': 'critical'
                })

    for arrest in arrests:
        for fir in firs:
            if arrest['date'] < fir['date']:
                warnings.append({
                    'type': 'timeline_error',
                    'message': 'Arrest date %s is BEFORE FIR date %s' % (arrest['date_str'], fir['date_str']),
                    'severity': 'critical'
                })

    today = datetime.now()
    for d in dates:
        if d['date'] > today:
            warnings.append({
                'type': 'future_date',
                'message': 'Date %s is in the future' % d['date_str'],
                'severity': 'warning'
            })
        if d['date'].year < 1947:
            warnings.append({
                'type': 'suspicious_date',
                'message': 'Date %s is before 1947 — possible typo' % d['date_str'],
                'severity': 'warning'
            })

    return warnings

def summarise_dates(text):
    dates    = extract_dates_with_context(text)
    warnings = check_timeline(text)
    return {
        'dates_found': len(dates),
        'dates': dates,
        'warnings': warnings,
        'has_errors': any(w['severity'] == 'critical' for w in warnings)
    }

if __name__ == '__main__':
    test = (
        "15.08.2022-ஆம் தேதியன்று காவல் நிலையத்தில் புகார் பதிவு செய்யப்பட்டது. "
        "10.08.2022-ஆம் தேதியன்று சம்பவம் நடந்தது. "
        "20.08.2022-ஆம் தேதியன்று கைது செய்யப்பட்டார்."
    )
    result = summarise_dates(test)
    print("Dates found: %d" % result['dates_found'])
    for d in result['dates']:
        print("  %s — %s" % (d['date_str'], d['context']))
    print("Warnings: %d" % len(result['warnings']))
    for w in result['warnings']:
        print("  [%s] %s" % (w['severity'], w['message']))
