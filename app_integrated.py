import os
NGK_VERSION = '20260916202340'
from pathlib import Path
import glob

DATA_DIR = os.path.expanduser("~/NGK_Solai_Data")
os.makedirs(DATA_DIR, exist_ok=True)

RULES_PATTERN = os.path.join(DATA_DIR, "tamil_rules_*.json")
NEGATIVE_EXAMPLES = os.path.join(DATA_DIR, "negative_examples.json")
AUDIT_LOG = os.path.join(DATA_DIR, "audit_log.txt")

#!/usr/bin/env python3
from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for, send_from_directory
import json
from pathlib import Path
from unified_grammar_engine import UnifiedTamilGrammarEngine
from contextual_judicial_rephraser import ContextualJudicialRephraser
from functools import wraps

app = Flask(__name__)

# Local visual assets
ASSETS_DIR = Path(__file__).resolve().parent / "assets"

@app.route("/assets/<path:filename>")
def serve_asset(filename):
    return send_from_directory(ASSETS_DIR, filename)

app.config['JSON_AS_ASCII'] = False
app.secret_key = 'tamil-neethi-nayam-secret-2026'

import user_manager as um
# ── Solai Kaaval anonymiser ───────────────────────────────────────────────────
import sys as _sys
_sys.path.insert(0, os.path.expanduser("~/solai_kaaval"))
from engine import Anonymiser as _SolaiAnonymiser
_solai = _SolaiAnonymiser(os.path.expanduser("~/solai_kaaval"))
_SOLAI_TOGGLES = {"aadhaar": ["AADHAAR"], "case": ["CASE", "FIR"], "dates": ["DATE", "DOB"]}
print("\u2705 Solai Kaaval: %d detectors loaded" % len(_solai.detectors))
# ─────────────────────────────────────────────────────────────────────────────


# Initialise admin on first run — change this password immediately after first login
um.init_admin('admin', 'Admin@2026!')

print("\n" + "="*70)
print("TAMIL NEETHI NAYAM — TAMIL JUDICIAL LANGUAGE INTELLIGENCE")
print("="*70)
print(f"\n📁 Data Directory: {DATA_DIR}")
print("📥 Initializing systems...")

engine = UnifiedTamilGrammarEngine(use_database=True)
rephraser = ContextualJudicialRephraser()
print(f"✅ Grammar Engine: {len(engine.corrections)} rules loaded")

DICTIONARY = {}
dict_files = ['wiktionary_tamil_enhanced.json','wiktionary_tamil_dict.json','tamil_dictionary_auto.json']
for dict_file in dict_files:
    dict_path = os.path.join(DATA_DIR, dict_file)
    try:
        if os.path.exists(dict_path):
            with open(dict_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    DICTIONARY.update(data.get('dictionary', data))
                print(f"   ✅ Loaded {dict_file}: {len(DICTIONARY):,} words")
    except Exception as e:
        print(f"   ⚠️  {dict_file}: {e}")

print(f"✅ Dictionary: {len(DICTIONARY):,} words total")
print("="*70)
print(f"\n🌐 Open: http://127.0.0.1:5000\n")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ── Shared styles (header + sidebar) ──────────────────────────────────────────
SHARED_STYLE = r'''
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Noto+Sans+Tamil:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
    *, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }

    :root {
        --navy:   #0d1b3e;
        --navy2:  #162040;
        --gold:   #c9a84c;
        --gold2:  #e8c76a;
        --white:  #ffffff;
        --text:   #e8eaf0;
        --muted:  #8b96b0;
        --accent: #1a73e8;
        --green:  #1e8e3e;
        --orange: #e37400;
        --red:    #d93025;
        --bg:     #f0f2f7;
        --card:   #ffffff;
        --border: #e0e4ed;
        --sidebar-w: 220px;
    }

    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: var(--bg);
        color: #202124;
        height: 100vh;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }

    /* ══ TOP HEADER ══ */
    .top-header {
        background: var(--navy);
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 20px 0 0;
        flex-shrink: 0;
        border-bottom: 2px solid var(--gold);
        position: relative;
    }
    .header-left {
        display: flex;
        align-items: center;
        height: 100%;
    }
    .sidebar-logo {
        width: var(--sidebar-w);
        height: 100%;
        background: var(--navy);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        border-right: 1px solid rgba(201,168,76,0.3);
        padding: 0 16px;
        flex-shrink: 0;
    }
    .logo-icon {
        width: 36px; height: 36px;
        background: var(--gold);
        border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        font-size: 18px; font-weight: 800; color: var(--navy);
        font-family: 'Cinzel', serif;
        flex-shrink: 0;
    }
    .logo-text {
        font-family: 'Cinzel', serif;
        font-size: 15px;
        font-weight: 700;
        color: var(--gold);
        letter-spacing: 0.5px;
        line-height: 1.2;
    }
    .logo-sub {
        font-size: 9px;
        color: var(--muted);
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .header-title {
        display: flex;
        align-items: center;
        gap: 16px;
        padding-left: 24px;
    }
    .header-divider {
        width: 1.5px;
        height: 28px;
        background: rgba(201,168,76,0.4);
    }
    .header-tamil {
        font-family: 'Noto Sans Tamil', sans-serif;
        font-size: 20px;
        font-weight: 700;
        color: var(--gold);
        letter-spacing: 1px;
    }
    .header-english {
        font-family: 'Cinzel', serif;
        font-size: 13px;
        font-weight: 600;
        color: rgba(255,255,255,0.7);
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    .header-right {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .header-badge {
        background: rgba(201,168,76,0.15);
        border: 1px solid rgba(201,168,76,0.3);
        color: var(--gold2);
        font-size: 11px;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 500;
    }
    .logout-btn {
        background: transparent;
        color: var(--muted);
        border: 1px solid rgba(255,255,255,0.15);
        padding: 6px 14px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
        transition: all 0.2s;
    }
    .logout-btn:hover { background: rgba(255,255,255,0.08); color: #fff; }

    /* ══ BODY LAYOUT ══ */
    .app-body {
        display: flex;
        flex: 1;
        overflow: hidden;
    }

    /* ══ SIDEBAR ══ */
    .sidebar {
        width: var(--sidebar-w);
        background: var(--navy2);
        display: flex;
        flex-direction: column;
        overflow-y: auto;
        flex-shrink: 0;
        border-right: 1px solid rgba(201,168,76,0.15);
    }
    .sidebar-section {
        padding: 16px 0 8px;
    }
    .sidebar-section-label {
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: var(--muted);
        padding: 0 16px 6px;
    }
    .nav-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 16px;
        cursor: pointer;
        transition: all 0.15s;
        border-left: 3px solid transparent;
        color: var(--muted);
        font-size: 13px;
        font-weight: 500;
        user-select: none;
    }
    .nav-item:hover {
        background: rgba(255,255,255,0.05);
        color: var(--text);
    }
    .nav-item.active {
        background: rgba(201,168,76,0.1);
        border-left-color: var(--gold);
        color: var(--gold2);
    }
    .nav-icon {
        font-size: 16px;
        width: 20px;
        text-align: center;
        flex-shrink: 0;
    }
    .sidebar-footer {
        margin-top: auto;
        padding: 12px 16px;
        border-top: 1px solid rgba(255,255,255,0.06);
        font-size: 11px;
        color: var(--muted);
        text-align: center;
    }

    /* ══ MAIN CONTENT ══ */
    .main-content {
        flex: 1;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
    }

    /* ══ DASHBOARD ══ */
    #page-dashboard { padding: 24px; }
    .dash-hero {
        background: var(--navy);
        border-radius: 12px;
        padding: 28px 32px;
        display: flex;
        align-items: center;
        gap: 32px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .dash-hero::after {
        content: '⚖';
        position: absolute;
        right: 24px;
        font-size: 120px;
        opacity: 0.06;
        color: var(--gold);
    }
    .hero-icon {
        width: 72px; height: 72px;
        background: rgba(201,168,76,0.15);
        border: 2px solid rgba(201,168,76,0.4);
        border-radius: 16px;
        display: flex; align-items: center; justify-content: center;
        font-size: 36px;
        flex-shrink: 0;
    }
    .hero-text h1 {
        font-family: 'Cinzel', serif;
        font-size: 22px;
        font-weight: 700;
        color: var(--gold);
        margin-bottom: 6px;
    }
    .hero-text p {
        font-size: 13px;
        color: rgba(255,255,255,0.6);
        line-height: 1.6;
        max-width: 500px;
    }
    .hero-btn {
        margin-top: 14px;
        background: var(--gold);
        color: var(--navy);
        border: none;
        padding: 10px 24px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 700;
        cursor: pointer;
        font-family: 'Cinzel', serif;
        letter-spacing: 0.5px;
        transition: all 0.2s;
    }
    .hero-btn:hover { background: var(--gold2); }

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    .stat-card {
        background: var(--card);
        border-radius: 10px;
        padding: 18px 20px;
        border: 1px solid var(--border);
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .stat-icon {
        width: 48px; height: 48px;
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 22px;
        flex-shrink: 0;
    }
    .stat-icon.blue   { background: #e8f0fe; color: var(--accent); }
    .stat-icon.green  { background: #e6f4ea; color: var(--green); }
    .stat-icon.purple { background: #f3e8fd; color: #7b1fa2; }
    .stat-icon.orange { background: #fef3e2; color: var(--orange); }
    .stat-num {
        font-size: 24px;
        font-weight: 700;
        color: #202124;
        line-height: 1;
        margin-bottom: 3px;
    }
    .stat-label {
        font-size: 12px;
        color: #5f6368;
        font-weight: 500;
    }

    .features-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    .feature-card {
        background: var(--card);
        border-radius: 10px;
        padding: 20px;
        border: 1px solid var(--border);
        cursor: pointer;
        transition: all 0.2s;
        position: relative;
    }
    .feature-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    .feature-icon {
        width: 44px; height: 44px;
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px;
        margin-bottom: 12px;
    }
    .feature-card h3 {
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .feature-card p {
        font-size: 12px;
        color: #5f6368;
        line-height: 1.5;
    }
    .feature-arrow {
        position: absolute;
        bottom: 16px;
        right: 16px;
        font-size: 18px;
        color: #dadce0;
    }
    .fc-blue   h3 { color: var(--accent); } .fc-blue   .feature-icon { background: #e8f0fe; color: var(--accent); }
    .fc-green  h3 { color: var(--green);  } .fc-green  .feature-icon { background: #e6f4ea; color: var(--green); }
    .fc-purple h3 { color: #7b1fa2;       } .fc-purple .feature-icon { background: #f3e8fd; color: #7b1fa2; }
    .fc-orange h3 { color: var(--orange); } .fc-orange .feature-icon { background: #fef3e2; color: var(--orange); }
    .fc-navy  h3 { color: #0d1b3e;       } .fc-navy  .feature-icon { background: #e8eaf5; color: #0d1b3e; }

    .bottom-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin-bottom: 24px;
    }
    .info-card {
        background: var(--card);
        border-radius: 10px;
        padding: 20px;
        border: 1px solid var(--border);
    }
    .info-card h3 {
        font-size: 13px;
        font-weight: 700;
        color: #3c4043;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .activity-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 7px 0;
        border-bottom: 1px solid #f1f3f4;
        font-size: 12px;
    }
    .activity-item:last-child { border-bottom: none; }
    .activity-dot {
        width: 7px; height: 7px;
        border-radius: 50%;
        background: var(--green);
        margin-right: 10px;
        flex-shrink: 0;
    }
    .activity-text { color: #3c4043; }
    .activity-time { color: #9aa0a6; font-size: 11px; }
    .status-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 7px 0;
        border-bottom: 1px solid #f1f3f4;
        font-size: 12px;
    }
    .status-item:last-child { border-bottom: none; }
    .status-ok { color: var(--green); font-weight: 600; }
    .status-label { color: #3c4043; }

    /* ══ GRAMMAR CHECK PAGE ══ */
    #page-grammar {
        display: none;
        flex: 1;
        flex-direction: column;
        overflow: hidden;
    }
    .grammar-toolbar {
        background: white;
        border-bottom: 1px solid var(--border);
        padding: 8px 16px;
        display: flex;
        gap: 8px;
        flex-shrink: 0;
    }
    .tool-btn {
        background: white; color: #3c4043;
        border: 1px solid #dadce0;
        padding: 6px 14px; border-radius: 4px;
        cursor: pointer; font-size: 13px; font-weight: 500;
        transition: all 0.2s;
    }
    .tool-btn:hover { background: #f8f9fa; }
    .grammar-body {
        flex: 1;
        display: grid;
        grid-template-columns: 1fr 48px 1fr 340px;
        overflow: hidden;
    }
    .editor-panel {
        display: flex; flex-direction: column;
        background: white; overflow: hidden;
    }
    .panel-header {
        background: #f8f9fa;
        padding: 10px 16px;
        border-bottom: 1px solid var(--border);
        font-size: 11px; font-weight: 700;
        color: #5f6368; letter-spacing: 0.8px;
        text-transform: uppercase;
        display: flex; justify-content: space-between; align-items: center;
        flex-shrink: 0;
    }
    .copy-btn {
        background: white; color: var(--accent);
        border: 1px solid #dadce0;
        padding: 4px 10px; border-radius: 3px;
        cursor: pointer; font-size: 12px;
        text-transform: none; font-weight: 500;
    }
    .panel-content { flex:1; padding:20px; overflow-y:auto; }
    .editor {
        width:100%; height:100%; border:none; outline:none;
        font-family:'Noto Sans Tamil',-apple-system,sans-serif;
        font-size:15px; line-height:1.9; color:#202124;
        resize:none; background:white;
    }
    .editor::placeholder { color:#bdc1c6; }
    .output-text {
        font-family:'Noto Sans Tamil',-apple-system,sans-serif;
        font-size:15px; line-height:1.9; color:#202124;
        white-space:pre-wrap; min-height:100%;
    }
    .middle-col {
        display:flex; align-items:center; justify-content:center;
        background:white; border-left:1px solid var(--border);
        border-right:1px solid var(--border);
    }
    .check-btn {
        background:var(--accent); color:white; border:none;
        width:36px; height:36px; border-radius:50%;
        cursor:pointer; font-size:18px;
        display:flex; align-items:center; justify-content:center;
        transition:all 0.3s;
        box-shadow:0 2px 8px rgba(26,115,232,.35);
    }
    .check-btn:hover { background:#1557b0; transform:scale(1.08); }
    .check-btn.loading { animation:spin 0.8s linear infinite; }
    @keyframes spin { to { transform:rotate(360deg); } }

    /* Issues sidebar */
    .issues-panel {
        background:#fff;
        border-left:1px solid #e0e0e0;
        display:flex; flex-direction:column; overflow:hidden;
    }
    .issues-header {
        padding:12px 16px;
        border-bottom:1px solid #e0e0e0;
        display:flex; align-items:center; justify-content:space-between;
        background:#fff; flex-shrink:0;
    }
    .issues-title {
        font-size:12px; font-weight:700; color:#3c4043;
        letter-spacing:0.5px; display:flex; align-items:center; gap:8px;
    }
    .issues-badge {
        background:var(--accent); color:#fff;
        font-size:11px; font-weight:600;
        padding:2px 8px; border-radius:10px;
    }
    .issues-badge.zero  { background:var(--green); }
    .issues-badge.warn  { background:var(--orange); }
    .issues-badge.error { background:var(--red); }
    .score-ring {
        width:38px; height:38px; border-radius:50%;
        border:3px solid var(--green);
        display:flex; align-items:center; justify-content:center;
        font-size:12px; font-weight:700; color:var(--green);
    }
    .score-ring.medium { border-color:var(--orange); color:var(--orange); }
    .score-ring.low    { border-color:var(--red);    color:var(--red); }
    .issues-list {
        flex:1; overflow-y:auto; padding:8px; background:#f8f9fa;
    }
    .issue-card {
        background:#fff; border-radius:6px;
        padding:12px 14px 10px; margin-bottom:6px;
        border:1px solid #e0e0e0; border-left:4px solid #e0e0e0;
        transition:box-shadow 0.1s;
    }
    .issue-card:hover { box-shadow:0 2px 8px rgba(60,64,67,0.12); cursor:pointer; }
    .issue-card.correction { border-left-color:var(--accent); }
    .issue-card.warning    { border-left-color:var(--orange); }
    .issue-card.error      { border-left-color:var(--red); }
    .issue-card.info       { border-left-color:var(--green); }
    .issue-chip {
        display:inline-block; font-size:9px; font-weight:700;
        letter-spacing:0.9px; text-transform:uppercase;
        padding:2px 8px; border-radius:3px; margin-bottom:8px;
    }
    .issue-chip.correction { background:#e8f0fe; color:var(--accent); }
    .issue-chip.warning    { background:#fef3e2; color:#b06000; }
    .issue-chip.error      { background:#fce8e6; color:var(--red); }
    .issue-chip.info       { background:#e6f4ea; color:var(--green); }
    .issue-card.logic      { border-left-color:#7c3aed; }
    .issue-chip.logic      { background:#f3e8ff; color:#7c3aed; }
    .issue-card.logic      { border-left-color:#7c3aed; }
    .issue-chip.logic      { background:#f3e8ff; color:#7c3aed; }
    .issue-wrong {
        font-size:15px; color:var(--red);
        text-decoration:line-through; text-decoration-thickness:1.5px;
        margin-bottom:2px;
        font-family:'Noto Sans Tamil',Georgia,serif; line-height:1.6;
    }
    .issue-arrow { font-size:11px; color:#9aa0a6; margin-bottom:2px; font-style:italic; }
    .issue-correct {
        font-size:16px; color:var(--green); font-weight:700;
        font-family:'Noto Sans Tamil',Georgia,serif; line-height:1.6;
    }
    .issue-msg { font-size:13px; color:#3c4043; line-height:1.55; }
    .sidebar-empty {
        flex:1; display:flex; flex-direction:column;
        align-items:center; justify-content:center;
        padding:32px 20px; text-align:center; background:#f8f9fa;
    }
    .empty-icon { font-size:44px; margin-bottom:12px; opacity:0.25; }
    .empty-title { font-size:14px; font-weight:600; color:#3c4043; margin-bottom:6px; }
    .empty-sub   { font-size:12px; color:#80868b; line-height:1.6; }

    .grammar-status {
        background:#f8f9fa; padding:6px 16px;
        border-top:1px solid var(--border);
        font-size:12px; color:#5f6368;
        display:flex; justify-content:space-between;
        flex-shrink:0;
    }

    /* ── Modals ── */
    .modal {
        display:none; position:fixed; z-index:1000;
        left:0; top:0; width:100%; height:100%;
        background:rgba(0,0,0,0.4);
    }
    .modal.show { display:flex; align-items:center; justify-content:center; }
    .modal-content {
        background:white; padding:24px; border-radius:8px;
        width:90%; max-width:480px;
        box-shadow:0 8px 24px rgba(0,0,0,0.15);
    }
    .modal-header { font-size:17px; font-weight:600; margin-bottom:16px; color:#202124; }
    .modal-input {
        width:100%; padding:10px;
        border:1px solid #dadce0; border-radius:4px;
        font-size:15px; margin-bottom:12px;
        font-family:'Noto Sans Tamil',sans-serif;
    }
    .modal-input:focus { outline:none; border-color:var(--accent); }
    .modal-buttons { display:flex; gap:8px; justify-content:flex-end; margin-top:14px; }
    .btn-cancel {
        background:white; color:#3c4043;
        border:1px solid #dadce0; padding:8px 20px;
        border-radius:4px; cursor:pointer; font-size:14px;
    }
    .btn-submit {
        background:var(--accent); color:white; border:none;
        padding:8px 20px; border-radius:4px;
        cursor:pointer; font-size:14px;
    }



    /* ========================================================
       TNN — SINGLE PROFESSIONAL TITLE BAR
       ======================================================== */

    .top-header {
        height: 72px !important;
        min-height: 72px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        padding: 0 18px !important;
        box-sizing: border-box !important;
        overflow: hidden !important;
    }

    .tnn-single-identity {
        height: 100%;
        display: flex;
        align-items: center;
        gap: 14px;
        min-width: 0;
    }

    .tnn-logo-single {
        width: 58px !important;
        height: 58px !important;
        min-width: 58px !important;
        max-width: 58px !important;
        object-fit: contain !important;
        display: block !important;
    }

    .tnn-single-text {
        min-width: 0;
        line-height: 1;
    }

    .tnn-single-tamil {
        font-family: 'Noto Sans Tamil', sans-serif;
        font-size: 20px;
        font-weight: 700;
        color: #f4d98b;
        white-space: nowrap;
        line-height: 1.15;
    }

    .tnn-single-english {
        font-family: 'Cinzel', serif;
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 2px;
        color: rgba(255,255,255,.9);
        margin-top: 4px;
        white-space: nowrap;
    }

    .tnn-single-tagline {
        font-family: 'Noto Sans Tamil', sans-serif;
        font-size: 8px;
        color: rgba(255,255,255,.62);
        margin-top: 4px;
        white-space: nowrap;
    }

    .tnn-single-tagline span {
        padding: 0 5px;
        color: rgba(244,217,139,.65);
    }

    .tnn-single-actions {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-shrink: 0;
    }

    .tnn-single-actions .header-badge {
        white-space: nowrap;
    }

    .tnn-single-actions .logout-btn {
        white-space: nowrap;
    }

    @media (max-width: 900px) {
        .top-header {
            padding: 0 10px !important;
        }

        .tnn-single-tagline {
            display: none;
        }

        .tnn-single-tamil {
            font-size: 17px;
        }
    }

    /* ========================================================
       TAMIL NEETHI NAYAM — CLEAN VISUAL IDENTITY
       ======================================================== */

    .tnn-logo {
        width: 46px !important;
        height: 46px !important;
        max-width: 46px !important;
        max-height: 46px !important;
        display: block;
        flex: 0 0 46px;
        object-fit: contain;
    }

    .tnn-brand {
        min-width: 0;
        text-align: left;
        line-height: 1.15;
    }

    .tnn-brand-tamil {
        font-family: 'Noto Sans Tamil', sans-serif;
        font-size: 15px;
        font-weight: 700;
        color: var(--gold);
        white-space: nowrap;
    }

    .tnn-brand-english {
        font-family: 'Cinzel', serif;
        font-size: 8px;
        font-weight: 600;
        color: rgba(255,255,255,.78);
        letter-spacing: 1.25px;
        margin-top: 3px;
        white-space: nowrap;
    }

    .tnn-header-title {
        padding-left: 22px;
        min-width: 0;
    }

    .tnn-header-tamil {
        font-family: 'Noto Sans Tamil', sans-serif;
        font-size: 19px;
        line-height: 1.15;
        font-weight: 700;
        color: #f4d98b;
        white-space: nowrap;
    }

    .tnn-header-english {
        font-family: 'Cinzel', serif;
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 1.8px;
        color: rgba(255,255,255,.86);
        margin-top: 3px;
        white-space: nowrap;
    }

    .tnn-header-tagline {
        font-family: 'Noto Sans Tamil', sans-serif;
        font-size: 9px;
        color: rgba(255,255,255,.62);
        margin-top: 2px;
        white-space: nowrap;
    }

    .tnn-court-watermark {
        position: absolute;
        right: 18px;
        bottom: 14px;
        width: 300px;
        max-width: 28vw;
        opacity: .16;
        pointer-events: none;
        z-index: 0;
    }

    .tnn-book-watermark {
        position: absolute;
        right: 36px;
        bottom: 28px;
        width: 150px;
        opacity: .065;
        pointer-events: none;
        z-index: 1;
    }

    .dash-hero {
        position: relative;
        overflow: hidden;
    }

    .dash-hero > * {
        position: relative;
        z-index: 2;
    }

    .dash-hero::before {
        content: "";
        position: absolute;
        right: 0;
        bottom: 0;
        width: 330px;
        height: 230px;
        background: url('/assets/madras_high_court.svg')
                    right bottom / contain no-repeat;
        opacity: .18;
        pointer-events: none;
        z-index: 0;
    }

    .tnn-hero-art {
        position: absolute;
        right: 30px;
        bottom: 18px;
        width: 145px;
        opacity: .075;
        pointer-events: none;
        z-index: 1;
    }

    .sidebar-footer strong {
        display: block;
        font-family: 'Noto Sans Tamil', sans-serif;
        font-size: 11px;
        color: var(--gold2);
        margin-bottom: 2px;
    }

    .sidebar-footer .tnn-footer-en {
        display: block;
        font-family: 'Cinzel', serif;
        font-size: 7px;
        letter-spacing: 1px;
        color: rgba(255,255,255,.65);
        margin-bottom: 3px;
    }

    .sidebar-footer .tnn-footer-ta {
        display: block;
        font-family: 'Noto Sans Tamil', sans-serif;
        font-size: 8px;
        color: var(--muted);
    }

    @media (max-width: 900px) {
        .tnn-header-tagline {
            display: none;
        }

        .tnn-header-english {
            letter-spacing: 1px;
        }

        .tnn-court-watermark {
            width: 200px;
        }
    }
    </style>
'''

LOGIN_PAGE = r'''<!DOCTYPE html>
<html>
<head>
    <title>தமிழ் நீதி நயம் — Tamil Neethi Nayam</title>
    ''' + SHARED_STYLE + r'''
    <style>
    body {
        background: linear-gradient(135deg, #0d1b3e 0%, #162040 100%);
        display: flex; align-items: center; justify-content: center;
        min-height: 100vh; flex-direction: column; overflow: auto;
    }
    .login-card {
        background: white; border-radius: 16px;
        box-shadow: 0 24px 64px rgba(0,0,0,0.4);
        padding: 48px; width: 100%; max-width: 420px;
    }
    .login-logo {
        text-align: center; margin-bottom: 32px;
    }
    .login-emblem {
        font-size: 48px; margin-bottom: 12px;
    }
    .login-title {
        font-family: 'Cinzel', serif;
        font-size: 24px; font-weight: 700;
        color: #0d1b3e; margin-bottom: 4px;
    }
    .login-title span { color: #c9a84c; }
    .login-sub {
        font-family: 'Noto Sans Tamil', sans-serif;
        font-size: 13px; color: #80868b;
    }
    .form-row { margin-bottom: 18px; }
    .form-row label {
        display: block; font-size: 12px; font-weight: 600;
        color: #3c4043; margin-bottom: 6px; letter-spacing: 0.3px;
        text-transform: uppercase;
    }
    .form-row input {
        width: 100%; padding: 12px 14px;
        border: 1.5px solid #e0e0e0; border-radius: 6px;
        font-size: 15px; transition: all 0.2s;
        font-family: inherit;
    }
    .form-row input:focus { outline: none; border-color: #c9a84c; box-shadow: 0 0 0 3px rgba(201,168,76,0.1); }
    .login-btn {
        width: 100%; padding: 13px;
        background: #0d1b3e;
        color: #c9a84c; border: 2px solid #c9a84c;
        border-radius: 6px; font-size: 14px; font-weight: 700;
        font-family: 'Cinzel', serif; letter-spacing: 1px;
        cursor: pointer; transition: all 0.2s; margin-top: 8px;
        text-transform: uppercase;
    }
    .login-btn:hover { background: #c9a84c; color: #0d1b3e; }
    .error-msg {
        background: #fce8e6; color: #c5221f;
        padding: 10px 14px; border-radius: 6px;
        margin-bottom: 16px; font-size: 13px;
        border-left: 4px solid #c5221f;
    }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="login-logo">
            <div class="login-emblem">⚖️</div>
            <div class="login-title">
                <span style="font-family:'Noto Sans Tamil',sans-serif;">
                    தமிழ் நீதி நயம்
                </span>
            </div>
            <div class="login-sub">
                TAMIL NEETHI NAYAM<br>
                <span style="font-size:11px;">
                    செம்மையான தமிழுக்கான நுண்ணறிவு
                </span>
            </div>
        </div>
        {% if error %}<div class="error-msg">{{ error }}</div>{% endif %}
        <form method="POST">
            <div class="form-row">
                <label>Username</label>
                <input type="text" name="username" required autofocus>
            </div>
            <div class="form-row">
                <label>Password</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="login-btn">Enter System</a>
        </form>
    </div>
</body>
</html>'''

HTML = r'''<!DOCTYPE html>
<html>
<head>
    <title>தமிழ் நீதி நயம்</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    ''' + SHARED_STYLE + r'''
</head>
<body>

<!-- ══ TOP HEADER ══ -->
<div class="top-header">

    <div class="tnn-single-identity">

        <img src="/assets/tnn_logo.webp"
             class="tnn-logo-single"
             alt="Tamil Neethi Nayam">

        <div class="tnn-single-text">
            <div class="tnn-single-tamil">தமிழ் நீதி நயம்</div>
            <div class="tnn-single-english">TAMIL NEETHI NAYAM</div>
            <div class="tnn-single-tagline">
                செம்மையான தமிழுக்கான நுண்ணறிவு
                <span>·</span>
                Intelligence for Refined Tamil
            </div>
        </div>

    </div>

    <div class="tnn-single-actions">
        <div class="header-badge" id="rulesLoadedBadge">Loading…</div>
        <form method="POST" action="/logout" style="margin:0">
            <button type="submit" class="logout-btn">Logout</button>
        </form>
    </div>

</div>

<!-- ══ APP BODY ══ -->
<div class="app-body">

    <!-- SIDEBAR -->
    <div class="sidebar">
        <div class="sidebar-section">
            <div class="sidebar-section-label">Main</div>
            <div class="nav-item active" onclick="showPage('dashboard')" id="nav-dashboard">
                <span class="nav-icon">🏠</span> Dashboard
            </div>
            <div class="nav-item" onclick="showPage('grammar')" id="nav-grammar">
                <span class="nav-icon">✍️</span> Grammar Check
            </div>
        </div>
        <div class="sidebar-section">
            <div class="sidebar-section-label">Tools</div>
            <div class="nav-item" onclick="showPage('grammar')" id="nav-rephrase">
                <span class="nav-icon">⚖️</span> Rephrase (Judicial)
            </div>
            <div class="nav-item" onclick="showAddRuleModal()">
                <span class="nav-icon">➕</span> Add Correction
            </div>
            <div class="nav-item" onclick="location.href='/rules'">
                <span class="nav-icon">📋</span> Manage Rules
            </div>
            <div class="nav-item" onclick="location.href='/negative-examples'">
                <span class="nav-icon">🛡</span> Negative Examples
            </div>
           <div class="nav-item" onclick="showSolaiPanel()">
               <span class="nav-icon">🔐</span> Solai Kaaval
           </div>
            <div class="nav-item" onclick="location.href='/qr-generator'">
                <span class="nav-icon">⬛</span> QR குறியீடு
            </div>
            <div class="nav-item" onclick="location.href='/change-password'">
                <span class="nav-icon">🔑</span> கடவுச்சொல் மாற்றம்
            </div>
        {%- if session.get("role") == "admin" %}
        <div class="sidebar-section">
            <div class="sidebar-section-label">Admin</div>
            <div class="nav-item" onclick="location.href='/admin/users'">
                <span class="nav-icon">👥</span> பயனர் நிர்வாகம்
            </div>
        </div>
        {%- endif %}
        </div>
        <div class="sidebar-section">
            <div class="sidebar-section-label">Reports</div>
            <div class="nav-item" onclick="showStats()">
                <span class="nav-icon">📊</span> Statistics
            </div>
            <div class="nav-item">
                <span class="nav-icon">📁</span> Audit Log
            </div>
        </div>
        <div class="sidebar-footer">
            <strong>தமிழ் நீதி நயம்</strong>
            <span class="tnn-footer-en">TAMIL NEETHI NAYAM</span>
            <span class="tnn-footer-ta">செம்மையான தமிழுக்கான நுண்ணறிவு</span>
        </div>
    </div>

    <!-- MAIN CONTENT -->
    <div class="main-content">

        <!-- ── DASHBOARD PAGE ── -->
        <div id="page-dashboard">

            <!-- Hero -->
            <div class="dash-hero">
                <img src="/assets/tnn_book_paper.svg"
                     class="tnn-hero-art"
                     alt=""
                     aria-hidden="true">
                <div class="hero-icon">⚖️</div>
                <div class="hero-text">
                    <h1>தமிழ் நீதி நயம்</h1>
                    <p>
        செம்மையான தமிழுக்கான நுண்ணறிவு — நீதிமன்றத் தீர்ப்புகள்,
        ஆவணங்கள் மற்றும் சட்டத் தமிழுக்கான இலக்கணம், எழுத்துப்பிழை
        மற்றும் நடைச் சீரமைப்பு.
    </p>
                    <button class="hero-btn" onclick="showPage('grammar')">Open Grammar Check →</button>
                </div>
            </div>

            <!-- Stats -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon blue">📚</div>
                    <div>
                        <div class="stat-num" id="stat-rules">—</div>
                        <div class="stat-label">Rules Loaded</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon green">📖</div>
                    <div>
                        <div class="stat-num" id="stat-words">—</div>
                        <div class="stat-label">Dictionary Words</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon purple">✅</div>
                    <div>
                        <div class="stat-num">128</div>
                        <div class="stat-label">Negative Examples</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon orange">⚡</div>
                    <div>
                        <div class="stat-num">9</div>
                        <div class="stat-label">Processing Layers</div>
                    </div>
                </div>
            </div>

            <!-- Feature Cards -->
            <div class="features-grid">
                <div class="feature-card fc-blue" onclick="showPage('grammar')">
                    <div class="feature-icon">✍️</div>
                    <h3>Grammar Check</h3>
                    <p>Check and correct Tamil grammar, spelling, and usage errors in judicial text.</p>
                    <div class="feature-arrow">›</div>
                </div>
                <div class="feature-card fc-green" onclick="showPage('grammar')">
                    <div class="feature-icon">⚖️</div>
                    <h3>Rephrase (Judicial)</h3>
                    <p>Rephrase sentences in formal judicial Tamil register.</p>
                    <div class="feature-arrow">›</div>
                </div>
                <div class="feature-card fc-purple" onclick="showStats()">
                    <div class="feature-icon">📊</div>
                    <h3>Statistics</h3>
                    <p>View rule counts, dictionary size, and system performance metrics.</p>
                    <div class="feature-arrow">›</div>
                </div>
                <div class="feature-card fc-orange" onclick="showAddRuleModal()">
                    <div class="feature-icon">➕</div>
                    <h3>Add Correction</h3>
                    <p>Add new correction rules to the live database instantly.</p>
                    <div class="feature-arrow">›</div>
                </div>
                <div class="feature-card fc-navy" onclick="showQRWidget()">
                    <div class="feature-icon">⬛</div>
                    <h3>QR குறியீடு</h3>
                    <p>Generate court document QR codes for case IDs and references.</p>
                    <div class="feature-arrow">›</div>
                </div>
            </div>

            <!-- QR Widget inline -->
            <div id="qr-widget" style="display:none;margin-top:20px;">
              <div style="background:#fff;border:1px solid #e0e4ed;border-radius:12px;padding:24px;">
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:18px;padding-bottom:14px;border-bottom:2px solid #c9a84c;">
                  <span style="font-size:1.5rem;">⬛</span>
                  <div>
                    <div style="font-size:1rem;font-weight:700;color:#0d1b3e;">QR குறியீடு உருவாக்கி</div>
                    <div style="font-size:.75rem;color:#6b7280;">Court Document QR Generator</div>
                  </div>
                  <button onclick="document.getElementById('qr-widget').style.display='none'" style="margin-left:auto;background:#f0f2f7;border:none;border-radius:6px;padding:6px 12px;cursor:pointer;font-size:.8rem;color:#4a4a6a;">✕ Close</button>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start;">
                  <div>
                    <label style="display:block;font-size:.78rem;font-weight:600;color:#4a4a6a;margin-bottom:6px;">வழக்கு எண் அல்லது ஆவண குறிப்பு</label>
                    <div style="position:relative;">
                      <input id="dqin" type="text" maxlength="60" placeholder="e.g. TNSA18-000604-2025"
                             autocomplete="off" spellcheck="false"
                             style="width:100%;padding:10px 80px 10px 12px;border:1.5px solid #e0e4ed;border-radius:6px;font-family:'Courier New',monospace;font-size:.95rem;font-weight:700;letter-spacing:.06em;outline:none;"
                             oninput="dqrLive(this)">
                      <span id="dqctr" style="position:absolute;right:10px;top:50%;transform:translateY(-50%);font-size:.7rem;font-weight:700;color:#8a90a4;">0 / 20</span>
                    </div>
                    <div id="dqprev" style="margin-top:6px;font-size:.74rem;color:#4a4a6a;min-height:16px;">சுத்தப்படுத்தப்பட்ட வெளியீடு இங்கு தோன்றும்</div>
                    <button onclick="dgenQR()" style="margin-top:12px;width:100%;padding:10px;background:#0d1b3e;color:#fff;border:none;border-radius:6px;font-size:.88rem;font-weight:700;cursor:pointer;">QR உருவாக்கு ▶</button>
                  </div>
                  <div id="dqr-out" style="display:none;flex-direction:column;align-items:center;gap:10px;">
                    <div id="dqr-wrap" style="background:#fff;padding:10px;border-radius:7px;box-shadow:0 2px 10px rgba(13,27,62,.12);"></div>
                    <div id="dqr-val" style="font-family:'Courier New',monospace;font-size:.85rem;font-weight:700;letter-spacing:.08em;color:#0d1b3e;background:#f0f2f7;border-radius:4px;padding:4px 12px;"></div>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;width:100%;">
                      <button onclick="dDL_PNG()" style="padding:7px 4px;border:1px solid #e0e4ed;border-radius:5px;background:#fff;cursor:pointer;font-size:.7rem;font-weight:600;">🖼 PNG</button>
                      <button onclick="dDL_SVG()" style="padding:7px 4px;border:1px solid #e0e4ed;border-radius:5px;background:#fff;cursor:pointer;font-size:.7rem;font-weight:600;">📐 SVG</button>
                      <button onclick="dCP_TXT(this)" style="padding:7px 4px;border:1px solid #e0e4ed;border-radius:5px;background:#fff;cursor:pointer;font-size:.7rem;font-weight:600;">📋 நகல்</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Bottom info -->
            <div class="bottom-grid">
                <div class="info-card">
                    <h3>⏱ Processing Pipeline</h3>
                    <div class="activity-item"><span class="activity-text">① unified_grammar_engine</span><span class="activity-time">43 rules</span></div>
                    <div class="activity-item"><span class="activity-text">② rule_store (longest-first)</span><span class="activity-time">887 rules</span></div>
                    <div class="activity-item"><span class="activity-text">③ sandhi_patterns</span><span class="activity-time">compound</span></div>
                    <div class="activity-item"><span class="activity-text">④ prosthetic இ insertion</span><span class="activity-time">ர/ரா</span></div>
                    <div class="activity-item"><span class="activity-text">⑤ datetime_norm</span><span class="activity-time">dates/times</span></div>
                    <div class="activity-item"><span class="activity-text">⑥ series (IPC sections)</span><span class="activity-time">citation</span></div>
                    <div class="activity-item"><span class="activity-text">⑦ punctuation</span><span class="activity-time">commas/quotes</span></div>
                    <div class="activity-item"><span class="activity-text">⑧ whitespace tidy</span><span class="activity-time">cleanup</span></div>
                    <div class="activity-item"><span class="activity-text">⑨ postposition check</span><span class="activity-time">warnings</span></div>
                </div>
                <div class="info-card">
                    <h3>🛡 System Status</h3>
                    <div class="status-item"><span class="status-label">Grammar Engine</span><span class="status-ok">● Active</span></div>
                    <div class="status-item"><span class="status-label">Dictionary</span><span class="status-ok">● Active</span></div>
                    <div class="status-item"><span class="status-label">Rule Store</span><span class="status-ok">● Active</span></div>
                    <div class="status-item"><span class="status-label">Date Timeline Checker</span><span class="status-ok">● Active</span></div>
                    <div class="status-item"><span class="status-label">Duplicate Detector</span><span class="status-ok">● Active</span></div>
                    <div class="status-item"><span class="status-label">Mega Cloud Sync</span><span class="status-ok">● Synced</span></div>
                    <div class="status-item"><span class="status-label">GitHub Repository</span><span class="status-ok">● Connected</span></div>
                    <div class="status-item"><span class="status-label">False Positives</span><span class="status-ok">● 0 / 128</span></div>
                    <div class="status-item"><span class="status-label">Authentication</span><span class="status-ok">● Secured</span></div>
                </div>
            </div>
        </div>

        <!-- ── GRAMMAR CHECK PAGE ── -->
        <div id="page-grammar" style="display:none; flex:1; flex-direction:column; overflow:hidden;">

            <div class="grammar-toolbar">
                <button class="tool-btn" onclick="showPage('dashboard')">← Dashboard</button>
                <button class="tool-btn" onclick="clearGrammar()">🗑 Clear</button>
                <button class="tool-btn" onclick="location.href='/rules'">✎ Rules</button>
                <button class="tool-btn" onclick="showAddRuleModal()">＋ Add Rule</button>
                <button class="tool-btn" onclick="showStats()">📊 Stats</button>
            </div>

            <div class="grammar-body">
                <!-- Input -->
                <div class="editor-panel">
                    <div class="panel-header">
                        Original Text
                        <button class="copy-btn" onclick="copyInput()" id="copyInputBtn">Copy</button>
                    </div>
                    <div class="panel-content">
                        <textarea id="editor" class="editor"
                            placeholder="Paste or type Tamil judicial text here…"></textarea>
                    </div>
                </div>

                <!-- Middle -->
                <div class="middle-col">
                    <button class="check-btn" id="checkBtn" onclick="checkGrammar()" title="Check Grammar">✓</button>
                </div>

                <!-- Output -->
                <div class="editor-panel">
                    <div class="panel-header">
                        Corrected Text
                        <button class="copy-btn" onclick="copyOutput()" id="copyOutputBtn">Copy</button>
                    </div>
                    <div class="panel-content">
                        <div id="output-text" class="output-text" style="color:#9aa0a6;font-size:14px;">
                            Click ✓ to check your text…
                        </div>
                    </div>
                </div>

                <!-- Issues -->
                <div class="issues-panel">
                    <div class="issues-header">
                        <div class="issues-title">
                            Issues
                            <span class="issues-badge zero" id="issueCount">0</span>
                        </div>
                        <div class="score-ring" id="scoreRing">—</div>
                    </div>
                    <div class="issues-list" id="issuesList">
                        <div class="sidebar-empty">
                            <div class="empty-icon">✓</div>
                            <div class="empty-title">Ready to check</div>
                            <div class="empty-sub">Paste Tamil text and click ✓ to see corrections here.</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="grammar-status">
                <span id="statusText">Ready</span>
                <span id="statsText"></span>
            </div>
        </div>

    </div><!-- /main-content -->
</div><!-- /app-body -->

<!-- Add Rule Modal -->
<div id="addRuleModal" class="modal">
    <div class="modal-content">
        <div class="modal-header">Add New Rule</div>
        <input type="text" id="wrongWord" class="modal-input" placeholder="Wrong word (Tamil)">
        <input type="text" id="correctWord" class="modal-input" placeholder="Correct word (Tamil)">
        <div class="modal-buttons">
            <button class="btn-cancel" onclick="closeAddRuleModal()">Cancel</button>
            <button class="btn-submit" onclick="addNewRule()">Add Rule</button>
        </div>
    </div>
</div>

<!-- Stats Modal -->
<div id="statsModal" class="modal">
    <div class="modal-content">
        <div class="modal-header">📊 System Statistics</div>
        <div id="statsContent"></div>
        <div class="modal-buttons">
            <button class="btn-submit" onclick="closeStatsModal()">Close</button>
        </div>
    </div>
</div>

<script>
const CAT = {
    'spelling':             ['SPELLING',       'correction'],
    'morphology':           ['MORPHOLOGY',     'correction'],
    'contextual':           ['CONTEXTUAL',     'info'],
    'register':             ['LEGAL REGISTER', 'info'],
    'punctuation':          ['PUNCTUATION',    'correction'],
    'datetime_date':        ['DATE FORMAT',    'correction'],
    'datetime_time':        ['TIME FORMAT',    'correction'],
    'datetime_time_numeric':['TIME FORMAT',    'correction'],
    'datetime_date_word':   ['DATE FORMAT',    'correction'],
    'datetime_hour':        ['TIME FORMAT',    'correction'],
    'section_fix':          ['SECTION NO.',    'warning'],
    'section_commas':       ['SECTION FORMAT', 'correction'],
    'series_sections':      ['SECTION SERIES', 'correction'],
    'series_matrum':        ['SECTION SERIES', 'correction'],
    'duplicate_phrase':     ['DUPLICATE',      'warning'],
    'whitespace':           ['WHITESPACE',     'info'],
    'user':                 ['USER RULE',      'correction'],
    'punct_fullstop':       ['FULL STOP',      'correction'],
    'punct_comma':          ['COMMA',          'correction'],
    'punct_clause_comma':   ['COMMA',          'correction'],
    'punct_quote_close':    ['QUOTE',          'correction'],
    'punct_quote_open':     ['QUOTE',          'correction'],
    'uncategorised':        ['CORRECTION',     'correction'],
};

function showQRWidget() {
  var w = document.getElementById('qr-widget');
  w.style.display = w.style.display === 'none' ? 'block' : 'none';
  if (w.style.display === 'block') setTimeout(function(){ w.scrollIntoView({behavior:'smooth',block:'start'}); }, 50);
}
var _dc='',_dsvg='',_dpng='',_dqr=null;
function dqrClean(r){ return r.toUpperCase().replace(/[^A-Z0-9]/g,'').slice(0,20); }
function dqrLive(el){
  var c=dqrClean(el.value),l=c.length;
  var ct=document.getElementById('dqctr');
  ct.textContent=l+' / 20';
  ct.style.color=l===20?'#1a7a4a':l>15?'#c8960c':'#8a90a4';
  document.getElementById('dqprev').innerHTML=c?'சுத்தம்: <b style="color:#1a5276;font-family:monospace;">'+c+'</b>':'சுத்தப்படுத்தப்பட்ட வெளியீடு இங்கு தோன்றும்';
}
function dgenQR(){
  var c=dqrClean(document.getElementById('dqin').value.trim());
  if(!c||c.length<3)return;
  _dc=c;
  var wrap=document.getElementById('dqr-wrap');
  wrap.innerHTML='';
  if(_dqr){try{_dqr.clear();}catch(e){}}
  _dqr=new QRCode(wrap,{text:c,width:200,height:200,colorDark:'#0d1b3e',colorLight:'#ffffff',correctLevel:QRCode.CorrectLevel.H});
  setTimeout(function(){
    var cv=wrap.querySelector('canvas');
    if(cv)_dpng=cv.toDataURL('image/png');
    document.getElementById('dqr-val').textContent=c;
    document.getElementById('dqr-out').style.display='flex';
    buildDSVG(c);
  },350);
}
function buildDSVG(text){
  var d=document.createElement('div');
  d.style.cssText='position:absolute;left:-9999px;visibility:hidden';
  document.body.appendChild(d);
  new QRCode(d,{text:text,width:400,height:400,colorDark:'#0d1b3e',colorLight:'#fff',correctLevel:QRCode.CorrectLevel.H});
  setTimeout(function(){
    var cv=d.querySelector('canvas');
    if(cv){
      var ctx=cv.getContext('2d'),w=cv.width,data=ctx.getImageData(0,0,w,w).data,ms=1,inR=false;
      for(var x=0;x<w;x++){var dk=data[x*4]<128;if(!inR&&dk){inR=true;}else if(inR&&!dk){ms=x;break;}}
      if(!ms)ms=Math.round(w/21);
      var mods=Math.round(w/ms),rects='';
      for(var r=0;r<mods;r++)for(var cc=0;cc<mods;cc++){
        var idx=(Math.round(r*ms)*w+Math.round(cc*ms))*4;
        if(data[idx]<128)rects+='<rect x="'+cc+'" y="'+r+'" width="1" height="1" fill="#0d1b3e"/>';
      }
      _dsvg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 '+mods+' '+mods+'" width="400" height="400" shape-rendering="crispEdges"><rect width="'+mods+'" height="'+mods+'" fill="#fff"/>'+rects+'</svg>';
    }
    document.body.removeChild(d);
  },250);
}
function dDL_PNG(){if(!_dpng)return;var a=document.createElement('a');a.href=_dpng;a.download='QR_'+_dc+'.png';a.click();}
function dDL_SVG(){if(!_dsvg){setTimeout(dDL_SVG,400);return;}var b=new Blob([_dsvg],{type:'image/svg+xml'}),a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='QR_'+_dc+'.svg';a.click();}
function dCP_TXT(btn){if(!_dc)return;navigator.clipboard.writeText(_dc).then(function(){var o=btn.textContent;btn.textContent='✓ நகல்';setTimeout(function(){btn.textContent=o;},1500);});}

function showPage(page) {
    document.getElementById('page-dashboard').style.display = page === 'dashboard' ? 'block' : 'none';
    const gp = document.getElementById('page-grammar');
    gp.style.display = page === 'grammar' ? 'flex' : 'none';
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const nav = document.getElementById('nav-' + page);
    if (nav) nav.classList.add('active');
}

function checkGrammar() {
    const text = document.getElementById('editor').value;
    if (!text.trim()) { alert('Please enter some text'); return; }
    const btn = document.getElementById('checkBtn');
    btn.classList.add('loading');
    document.getElementById('statusText').textContent = 'Checking…';
    fetch('/api/correct', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
    })
    .then(r => r.json())
    .then(data => {
        btn.classList.remove('loading');
        document.getElementById('output-text').textContent = data.corrected;
        document.getElementById('output-text').style.color = '#202124';
        renderSidebar(data);
        const n = data.changes_count;
        document.getElementById('statusText').textContent =
            n > 0 ? `${n} correction${n>1?'s':''} applied` : 'No corrections needed';
        document.getElementById('statsText').textContent = `${n} changes`;
    })
    .catch(() => {
        btn.classList.remove('loading');
        document.getElementById('statusText').textContent = 'Error — try again';
    });
}

function renderSidebar(data) {
    const list  = document.getElementById('issuesList');
    const badge = document.getElementById('issueCount');
    const ring  = document.getElementById('scoreRing');
    const corrections = (data.changes || []).filter(c => c.wrong && c.wrong !== 'spacing');
    const warnings    = data.warnings || [];
    const flags       = data.flags || [];
    const total = corrections.length + warnings.length + flags.length;
    badge.textContent = total;
    badge.className = 'issues-badge ' + (total===0?'zero':warnings.length>0||flags.length>0?'error':'warn');
    const score = total===0?100:Math.max(0,Math.round(100-corrections.length*2-warnings.length*8-flags.length*10));
    ring.textContent = score;
    ring.className = 'score-ring'+(score>=80?'':score>=55?' medium':' low');
    if (total===0) {
        list.innerHTML=`<div class="sidebar-empty"><div class="empty-icon">✅</div><div class="empty-title">All good!</div><div class="empty-sub">No issues found in this text.</div></div>`;
        return;
    }
    let html='';
    flags.forEach(f => {
        const typeMap = {'WITNESS_CONTRADICTION':'சாட்சி முரண்பாடு','DOUBLE_NEGATIVE_RESOLVED':'இரட்டை எதிர்மறை','COPULA_FORMAL':'முறையான முடிவு'};
        const fLabel = typeMap[f.type] || f.type;
        const fMsg = f.message || (f.original ? f.original + ' → தெளிவுபடுத்தப்பட்டது' : '');
        html+=`<div class="issue-card logic" onclick="jumpToText(this.dataset.w)" data-w="${f.witness||''}"><div class="issue-chip logic">⚖️ ${escapeHtml(fLabel)}</div><div class="issue-msg">${escapeHtml(fMsg)}</div></div>`;
    });
    warnings.forEach(w => {
        const wLabel = (w && w.label) ? w.label : 'Warning';
        const wMsg = (w && w.message) ? w.message : w;
        const wQuote = (wMsg.match(/"([^"]+)"/) || [])[1] || wMsg;
        html+=`<div class="issue-card error" onclick="jumpToText(this.dataset.w)" data-w="${wQuote}"><div class="issue-chip error">${escapeHtml(wLabel)}</div><div class="issue-msg">${escapeHtml(wMsg)}</div></div>`;
    });
    corrections.forEach(ch => {
        const cat=ch.category||'uncategorised';
        const [label,type]=CAT[cat]||['CORRECTION','correction'];
        html+=`<div class="issue-card ${type}" onclick="jumpToText(this.dataset.w)" data-w="${ch.wrong||ch.correct}"><div class="issue-chip ${type}">${label}</div><div class="issue-wrong">${escapeHtml(ch.wrong)}</div><div class="issue-arrow">corrected to</div><div class="issue-correct">${escapeHtml(ch.correct)}</div></div>`;
    });
    list.innerHTML=html;
}

function escapeHtml(str) {
    if(!str) return '';
    return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
function jumpToText(searchStr) {
    if (!searchStr) return;
    const ed = document.getElementById('editor');
    const val = ed.value;
    const idx = val.indexOf(searchStr);
    if (idx === -1) return;
    ed.focus();
    ed.setSelectionRange(idx, idx + searchStr.length);
    const lineHeight = parseInt(getComputedStyle(ed).lineHeight) || 20;
    const lines = val.substring(0, idx).split('\n').length;
    ed.scrollTop = (lines - 3) * lineHeight;
}
function copyText(text, btnId) {
    const b = document.getElementById(btnId);
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            b.textContent='✓ Copied'; setTimeout(()=>b.textContent='Copy',2000);
        });
    } else {
        // HTTP fallback for intranet IP access
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.focus(); ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        b.textContent='✓ Copied'; setTimeout(()=>b.textContent='Copy',2000);
    }
}
function copyInput() {
    copyText(document.getElementById('editor').value, 'copyInputBtn');
}
function copyOutput() {
    copyText(document.getElementById('output-text').textContent, 'copyOutputBtn');
}
function clearGrammar() {
    document.getElementById('editor').value='';
    document.getElementById('output-text').textContent='Click ✓ to check your text…';
    document.getElementById('output-text').style.color='#9aa0a6';
    document.getElementById('issuesList').innerHTML=`<div class="sidebar-empty"><div class="empty-icon">✓</div><div class="empty-title">Ready to check</div><div class="empty-sub">Paste Tamil text and click ✓ to see corrections here.</div></div>`;
    document.getElementById('issueCount').textContent='0';
    document.getElementById('issueCount').className='issues-badge zero';
    document.getElementById('scoreRing').textContent='—';
    document.getElementById('scoreRing').className='score-ring';
    document.getElementById('statusText').textContent='Ready';
    document.getElementById('statsText').textContent='';
}
function showAddRuleModal() {
    editing = -1;
    document.getElementById('addRuleModal').classList.add('show');
}
function closeAddRuleModal() {
    document.getElementById('addRuleModal').classList.remove('show');
    document.getElementById('wrongWord').value='';
    document.getElementById('correctWord').value='';
}
function addNewRule() {
    const wrong=document.getElementById('wrongWord').value;
    const correct=document.getElementById('correctWord').value;
    if(!wrong.trim()||!correct.trim()){alert('Please fill both fields');return;}
    fetch('/api/add-rule',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({wrong,correct})})
    .then(r=>r.json()).then(()=>{alert('✓ Rule added');closeAddRuleModal();});
}
function showStats() {
    fetch('/api/stats').then(r=>r.json()).then(data=>{
        document.getElementById('statsContent').innerHTML=`
            <div style="line-height:2;font-size:14px;">
                <div><strong>Grammar Rules:</strong> ${data.total_rules}</div>
                <div><strong>Dictionary Words:</strong> ${data.dictionary_words.toLocaleString()}</div>
            </div>`;
        document.getElementById('statsModal').classList.add('show');
    });
}
function closeStatsModal(){document.getElementById('statsModal').classList.remove('show');}
window.onclick=e=>{
    ['addRuleModal','statsModal'].forEach(id=>{
        const m=document.getElementById(id);
        if(e.target===m)m.classList.remove('show');
    });
};

// Load stats on startup
// ── Solai Kaaval ─────────────────────────────────────────────────────────
var _skMap = {};

function showSolaiPanel(){
  document.getElementById('solai-panel').style.display='block';
  window.scrollTo(0,0);
}
function hideSolaiPanel(){
  document.getElementById('solai-panel').style.display='none';
}

function _skDis(){
  var d=[];
  if(!document.getElementById('sk-t-aadhaar').checked) d.push('aadhaar');
  if(!document.getElementById('sk-t-case').checked)    d.push('case');
  if(!document.getElementById('sk-t-dates').checked)   d.push('dates');
  return d;
}
function _skLanes(){
  var l=[];
  if(document.getElementById('sk-l-en').checked) l.push('english');
  if(document.getElementById('sk-l-ta').checked) l.push('tamil');
  return l;
}

async function skAnon(){
  var body={text:document.getElementById('sk-src').value,
            ascii:document.getElementById('sk-ascii').checked,
            disable:_skDis(), lanes:_skLanes()};
  var r=await fetch('/api/solai/anonymise',{method:'POST',
        headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  var data=await r.json();
  _skMap=data.mapping;
  document.getElementById('sk-anon').value=data.anon;
  skRenderTable(data.mapping);
  var a=data.audit, parts=[];
  for(var k in a.by_type) parts.push('<b>'+k+'</b>: '+a.by_type[k]);
  document.getElementById('sk-audit').innerHTML=
    a.total_entities+' item(s) redacted &nbsp;&mdash;&nbsp;'+parts.join(' &nbsp;');
}

async function skDeanon(){
  var body={text:document.getElementById('sk-aiout').value,
            mapping:skCollectMap()};
  var r=await fetch('/api/solai/deanonymise',{method:'POST',
        headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  var data=await r.json();
  document.getElementById('sk-restored').value=data.restored;
}

function skRenderTable(mapping){
  var tb=document.getElementById('sk-tbl').getElementsByTagName('tbody')[0];
  tb.innerHTML='';
  for(var tok in mapping){
    var info=mapping[tok];
    skAddRowVals(tok, info.type||'', info.original||'');
  }
}
function skAddRowVals(tok,type,orig){
  var tb=document.getElementById('sk-tbl').getElementsByTagName('tbody')[0];
  var tr=document.createElement('tr');
  tr.innerHTML='<td style="border:1px solid #d9d2c4;padding:5px 7px;'+
    'font-family:monospace;white-space:nowrap" contenteditable>'+skE(tok)+'</td>'+
    '<td style="border:1px solid #d9d2c4;padding:5px 7px" contenteditable>'+skE(type)+'</td>'+
    '<td style="border:1px solid #d9d2c4;padding:5px 7px" contenteditable>'+skE(orig)+'</td>'+
    '<td style="border:1px solid #d9d2c4;padding:5px 7px;text-align:center;'+
    'color:#9b2c2c;cursor:pointer;font-weight:700" onclick="this.parentNode.remove()">&times;</td>';
  tb.appendChild(tr);
}
function skAddRow(){ skAddRowVals('⟦PERSON_9⟧','PERSON',''); }

function skCollectMap(){
  var m={}, rows=document.getElementById('sk-tbl').getElementsByTagName('tbody')[0].rows;
  for(var i=0;i<rows.length;i++){
    var c=rows[i].cells;
    var tok=c[0].innerText.trim();
    if(tok) m[tok]={type:c[1].innerText.trim(), original:c[2].innerText.trim()};
  }
  return m;
}

function skCopy(){ navigator.clipboard.writeText(document.getElementById('sk-anon').value); }

function skDownloadKey(){
  var blob=new Blob([JSON.stringify(skCollectMap(),null,2)],{type:'application/json'});
  var u=URL.createObjectURL(blob), a=document.createElement('a');
  a.href=u; a.download='solai_key.json'; a.click(); URL.revokeObjectURL(u);
}
function skLoadKey(ev){
  var f=ev.target.files[0]; if(!f) return;
  var rd=new FileReader();
  rd.onload=function(){ try{ skRenderTable(JSON.parse(rd.result)); }
                        catch(e){ alert('Not a valid key file'); } };
  rd.readAsText(f);
}
function skClear(){
  ['sk-src','sk-anon','sk-aiout','sk-restored'].forEach(function(id){
    document.getElementById(id).value='';
  });
  document.getElementById('sk-tbl').getElementsByTagName('tbody')[0].innerHTML='';
  document.getElementById('sk-audit').innerHTML='';
}
function skE(s){ return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
// ─────────────────────────────────────────────────────────────────────────────

fetch('/api/stats').then(r=>r.json()).then(data=>{
    document.getElementById('stat-rules').textContent=data.total_rules.toLocaleString();
    document.getElementById('stat-words').textContent=data.dictionary_words.toLocaleString();
    document.getElementById('rulesLoadedBadge').textContent=data.total_rules+' Rules Active';
}).catch(()=>{});
</script>

<!-- ── Solai Kaaval Panel ─────────────────────────────────────────────── -->
<div id="solai-panel" style="display:none;position:fixed;top:0;left:220px;right:0;bottom:0;
     background:#f4f1ea;z-index:900;overflow-y:auto;padding:24px 28px 60px">

  <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px">
    <span style="font-size:22px">&#128272;</span>
    <div>
      <h2 style="margin:0;font-size:18px;color:#1a1e3c">Solai Kaaval &mdash; Legal Document Anonymiser</h2>
      <p style="margin:3px 0 0;font-size:12px;color:#6b655a">
        Runs offline on this computer. Nothing you type here is sent anywhere.
      </p>
    </div>
    <button onclick="hideSolaiPanel()" style="margin-left:auto;background:#1a1e3c;color:#fff;
            border:none;border-radius:8px;padding:8px 16px;cursor:pointer;font-size:13px">
      &#8592; Back
    </button>
  </div>

  <!-- Phase 1 -->
  <div style="background:#fff;border:1px solid #d9d2c4;border-radius:10px;padding:16px;margin-bottom:16px">
    <h3 style="margin:0 0 10px;font-size:14px;color:#3a5a40">1. Original document</h3>
    <textarea id="sk-src" placeholder="Paste the Tamil / English document text here..."
      style="width:100%;min-height:140px;padding:10px;border:1px solid #d9d2c4;border-radius:8px;
             font-family:inherit;font-size:14px;resize:vertical"></textarea>
    <div style="display:flex;flex-wrap:wrap;gap:16px;align-items:center;margin:10px 0;font-size:13px;color:#6b655a">
      <span>Redact:</span>
      <label><input type="checkbox" id="sk-t-aadhaar" checked> Aadhaar</label>
      <label><input type="checkbox" id="sk-t-case" checked> Case / FIR numbers</label>
      <label><input type="checkbox" id="sk-t-dates" checked> Dates</label>
      <span style="margin-left:10px">Language:</span>
      <label><input type="checkbox" id="sk-l-en" checked> English</label>
      <label><input type="checkbox" id="sk-l-ta" checked> Tamil</label>
      <label style="margin-left:10px"><input type="checkbox" id="sk-ascii"> ASCII tokens [[ ]]</label>
    </div>
    <div style="display:flex;gap:8px">
      <button onclick="skAnon()"
        style="background:#7a5c2e;color:#fff;border:none;border-radius:8px;
               padding:9px 18px;cursor:pointer;font-size:14px">
        Anonymise &#8594;
      </button>
      <button onclick="skClear()"
        style="background:#eee;color:#22201b;border:1px solid #d9d2c4;border-radius:8px;
               padding:9px 18px;cursor:pointer;font-size:14px">
        Clear
      </button>
    </div>
  </div>

  <!-- Phase 2 + 3 grid -->
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">

    <div style="background:#fff;border:1px solid #d9d2c4;border-radius:10px;padding:16px">
      <h3 style="margin:0 0 10px;font-size:14px;color:#3a5a40">2. Anonymised &mdash; copy this to your AI</h3>
      <textarea id="sk-anon" placeholder="Anonymised text appears here..."
        style="width:100%;min-height:130px;padding:10px;border:1px solid #d9d2c4;border-radius:8px;
               font-family:inherit;font-size:14px;resize:vertical"></textarea>
      <div style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap">
        <button onclick="skCopy()"
          style="background:#eee;color:#22201b;border:1px solid #d9d2c4;border-radius:8px;
                 padding:7px 14px;cursor:pointer;font-size:13px">
          Copy text
        </button>
        <button onclick="skDownloadKey()"
          style="background:#eee;color:#22201b;border:1px solid #d9d2c4;border-radius:8px;
                 padding:7px 14px;cursor:pointer;font-size:13px">
          Download key
        </button>
        <label style="background:#eee;color:#22201b;border:1px solid #d9d2c4;border-radius:8px;
                      padding:7px 14px;cursor:pointer;font-size:13px">
          Load key <input type="file" id="sk-keyfile" accept=".json"
                          style="display:none" onchange="skLoadKey(event)">
        </label>
      </div>
      <div id="sk-audit" style="font-size:12px;color:#6b655a;margin-top:8px"></div>
    </div>

    <div style="background:#fff;border:1px solid #d9d2c4;border-radius:10px;padding:16px">
      <h3 style="margin:0 0 10px;font-size:14px;color:#3a5a40">3. AI output &#8594; restore</h3>
      <textarea id="sk-aiout" placeholder="Paste the text your AI returned (tokens still in it)..."
        style="width:100%;min-height:80px;padding:10px;border:1px solid #d9d2c4;border-radius:8px;
               font-family:inherit;font-size:14px;resize:vertical"></textarea>
      <button onclick="skDeanon()"
        style="background:#3a5a40;color:#fff;border:none;border-radius:8px;
               padding:9px 18px;cursor:pointer;font-size:14px;margin:8px 0">
        &#8592; De-anonymise
      </button>
      <textarea id="sk-restored" placeholder="Restored text appears here..."
        style="width:100%;min-height:80px;padding:10px;border:1px solid #d9d2c4;border-radius:8px;
               font-family:inherit;font-size:14px;resize:vertical"></textarea>
    </div>
  </div>

  <!-- Mapping table -->
  <div style="background:#fff;border:1px solid #d9d2c4;border-radius:10px;padding:16px">
    <h3 style="margin:0 0 6px;font-size:14px;color:#3a5a40">Mapping &mdash; review &amp; correct</h3>
    <p style="font-size:12px;color:#6b655a;margin:0 0 10px">
      Edit an original if a name was captured imperfectly. Delete a row to leave it un-restored.
      Add a row to redact something the tool missed (put your own token in the anonymised text above).
    </p>
    <table id="sk-tbl" style="width:100%;border-collapse:collapse;font-size:13px">
      <thead>
        <tr style="background:#efe9dd">
          <th style="border:1px solid #d9d2c4;padding:6px 8px;text-align:left">Token</th>
          <th style="border:1px solid #d9d2c4;padding:6px 8px;text-align:left">Type</th>
          <th style="border:1px solid #d9d2c4;padding:6px 8px;text-align:left">Original</th>
          <th style="border:1px solid #d9d2c4;padding:6px 8px;width:30px"></th>
        </tr>
      </thead>
      <tbody></tbody>
    </table>
    <button onclick="skAddRow()"
      style="background:#eee;color:#22201b;border:1px solid #d9d2c4;border-radius:8px;
             padding:7px 14px;cursor:pointer;font-size:13px;margin-top:8px">
      + Add row
    </button>
  </div>

  <div style="background:#fbf6ea;border:1px solid #e7d9b8;border-radius:8px;
              padding:10px 14px;font-size:12px;color:#5b4a29;margin-top:14px">
    Privacy: this panel makes no internet request. The document, tokens and key file
    stay on this machine. Only the anonymised text in box 2 &mdash; which you copy
    out yourself &mdash; should ever go to an online AI.
  </div>
</div>
<!-- ── end Solai Kaaval Panel ─────────────────────────────────────────── -->

</body>
</html>'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password','')
        user = um.authenticate(username, password)
        if user:
            session['username'] = username
            session['role'] = user.get('role', 'user')
            if user.get('must_change'):
                return redirect(url_for('change_password_forced'))
            return redirect(url_for('index'))
        error = 'பயனர் பெயர் அல்லது கடவுச்சொல் தவறு'
    return render_template_string(LOGIN_PAGE, error=error)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template_string(HTML)

@app.route('/api/correct', methods=['POST'])
@login_required
def correct():
    data = request.json
    text = data.get('text', '')
    # Strip quotes - Tamil judicial text never uses them
    for q in ('"', '“', '”', '‘', '’'):
        text = text.replace(q, "")

    result = engine.correct_text(text)
    try:
        from rule_store import load_all_rules, apply_rules
        _r, _ = load_all_rules()
        _out, _ch = apply_rules(result.get('corrected', text), _r)
        result['corrected'] = _out
        result['changes'] = list(result.get('changes', [])) + _ch
        result['changes_count'] = len(result['changes'])
    except Exception as e:
        print("rule_store error:", e)
    try:
        from sandhi_patterns import apply_sandhi
        _out2, _ch2 = apply_sandhi(result.get('corrected', text))
        result['corrected'] = _out2
        result['changes'] = list(result.get('changes', [])) + _ch2
        result['changes_count'] = len(result['changes'])
    except Exception as e:
        print("sandhi error:", e)
    try:
        from prosthetic import apply_prosthetic
        _o3, _c3 = apply_prosthetic(result.get('corrected', text))
        result['corrected'] = _o3
        result['changes'] = list(result.get('changes', [])) + _c3
        result['changes_count'] = len(result['changes'])
    except Exception as e:
        print("prosthetic error:", e)
    try:
        from datetime_norm import normalise as _dtnorm
        _o4, _c4 = _dtnorm(result.get('corrected', text))
        result['corrected'] = _o4
        result['changes'] = list(result.get('changes', [])) + _c4
        result['changes_count'] = len(result['changes'])
    except Exception as e:
        print("datetime error:", e)
    try:
        from series import format_series, format_commaed, unnumbered_part_sections, fix_malformed_sections, add_section_commas, normalise_sub_clause, normalise_uttpiruvu_prose
        _os, _cs = format_series(result.get('corrected', text))
        _os, _c2 = format_commaed(_os)
        _os, _c3 = unnumbered_part_sections(_os)
        _os, _c4 = fix_malformed_sections(_os)
        _os, _c5 = add_section_commas(_os)
        _os, _c6s = normalise_sub_clause(_os)
        _os, _ = normalise_uttpiruvu_prose(_os)
        _cs = list(_cs) + _c2 + _c3 + _c4 + _c5 + _c6s
        result['corrected'] = _os
        result['changes'] = list(result.get('changes', [])) + _cs
        result['changes_count'] = len(result['changes'])
    except Exception as e:
        print("series error:", e)
    try:
        from date_series import fix_date_series
        _o4b = fix_date_series(result.get("corrected", text))
        if _o4b != result.get("corrected", text):
            result["changes"] = list(result.get("changes", [])) + [{"type": "date_series", "note": "தேதி வரிசை மற்றும் சேர்க்கை"}]
        result["corrected"] = _o4b
        result["changes_count"] = len(result["changes"])
    except Exception as e:
        print("date_series error:", e)
    try:
        from case_number_norm import normalise as _cnnorm
        _ocn, _ccn = _cnnorm(result.get('corrected', text))
        result['corrected'] = _ocn
        result['changes'] = list(result.get('changes', [])) + _ccn
        result['changes_count'] = len(result['changes'])
    except Exception as e:
        print("case_number_norm error:", e)
    try:
        from punctuation import apply_punctuation
        _o5, _c5 = apply_punctuation(result.get('corrected', text))
        result['corrected'] = _o5
        result['changes'] = list(result.get('changes', [])) + _c5
        result['changes_count'] = len(result['changes'])
    except Exception as e:
        print("punctuation error:", e)
    try:
        from vehicle_reg_norm import normalize_vehicle_reg
        _o7vr, _c7vr = normalize_vehicle_reg(result.get('corrected', text))
        result['corrected'] = _o7vr
        result['changes'] = list(result.get('changes', [])) + _c7vr
        result['changes_count'] = len(result['changes'])
    except Exception as e:
        print('vehicle_reg_norm error:', e)
    try:
        from abbr_norm import normalise_abbreviations
        _oab, _cab = normalise_abbreviations(result.get('corrected', text))
        result['corrected'] = _oab
        result['changes'] = list(result.get('changes', [])) + _cab
        result['changes_count'] = len(result['changes'])
    except Exception as e:
        print('abbr_norm error:', e)
    try:
        from whitespace import tidy as _wstidy
        _o6, _c6 = _wstidy(result.get('corrected', text))
        result['corrected'] = _o6
        result['changes'] = list(result.get('changes', [])) + _c6
        result['changes_count'] = len(result['changes'])
    except Exception as e:
        print("whitespace error:", e)
    try:
        from ordinal_party import apply_ordinal_party
        _o8, _c8 = apply_ordinal_party(result.get('corrected', text))
        result['corrected'] = _o8
        result['changes'] = list(result.get('changes', [])) + _c8
        result['changes_count'] = len(result['changes'])
    except Exception as e:
        print("ordinal_party error:", e)
    try:
        from exhibit_norm import normalise_exhibits
        _o9, _c9 = normalise_exhibits(result.get('corrected', text))
        result['corrected'] = _o9
        result['changes'] = list(result.get('changes', [])) + _c9
        result['changes_count'] = len(result['changes'])
    except Exception as e:
        print("exhibit_norm error:", e)
    try:
        from postposition import check_postpositions
        _pp_flags = check_postpositions(result.get('corrected', text))
        _case_label = {
            'dative': 'நான்காம் வேற்றுமை (-க்கு)',
            'accusative': 'இரண்டாம் வேற்றுமை (-ஐ)',
        }
        result['warnings'] = [
            {
                'label': 'Grammar',
                'message': '"%s" — "%s" என்ற சொல் %s உருபு பெற வேண்டும்' % (
                    f.get('phrase', ''),
                    f.get('noun', ''),
                    _case_label.get(f.get('required', ''), f.get('required', '')),
                )
            }
            for f in _pp_flags
        ]
    except Exception as e:
        print("postposition error:", e)
        result['warnings'] = []
    try:
        from date_timeline_checker import summarise_dates
        timeline = summarise_dates(result.get('corrected', text))
        if timeline['warnings']:
            result['warnings'] = result.get('warnings', []) + [
                {'label': 'Timeline Warning', 'message': w['message']}
                for w in timeline['warnings']
            ]
    except Exception as e:
        print("timeline error:", e)

    rephrased = rephraser.rephrase(result['corrected'])
    result['corrected'] = rephrased['rephrased']
    return jsonify({
        'original': text,
        'corrected': result['corrected'],
        'rephrased': rephrased['rephrased'],
        'changes': result['changes'],
        'changes_count': result['changes_count'],
        'flags': rephrased['flags'],
        'total_flags': len(rephrased['flags']),
        'warnings': result.get('warnings', []),
        'statistics': result.get('statistics', {})
    })

@app.route('/api/add-rule', methods=['POST'])
@login_required
def add_rule():
    data = request.json
    engine.add_new_rule(data.get('wrong'), data.get('correct'))
    return jsonify({'success': True})

@app.route('/api/stats', methods=['GET'])
def stats():
    from rule_store import load_all_rules
    return jsonify({
        'total_rules': len(load_all_rules()[0]),
        'dictionary_words': len(DICTIONARY),
    })

import user_rules

RULES_PAGE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>தமிழ் நீதி நயம் - Rules</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f8f9fa;padding:0}
.hd{background:linear-gradient(135deg,#0d1b3e,#162040);color:#fff;padding:18px 24px;border-bottom:2px solid #c9a84c;}
.hd h1{font-size:21px;font-weight:600;font-family:'Cinzel',serif;color:#c9a84c;}
.hd a{color:#e8c76a;text-decoration:none;font-size:14px;}
.wrap{max-width:900px;margin:24px auto;background:#fff;border-radius:6px;box-shadow:0 1px 3px rgba(60,64,67,.3);padding:24px}
.row{display:flex;gap:10px;margin-bottom:20px;flex-wrap:wrap}
input{flex:1;min-width:180px;padding:10px;border:1px solid #dadce0;border-radius:4px;font-size:15px}
button{background:#1a73e8;color:#fff;border:none;padding:10px 20px;border-radius:4px;cursor:pointer;font-size:15px;font-weight:500}
button:hover{background:#1557b0}
button.del{background:#d93025}button.del:hover{background:#a50e0e}
button.sec{background:#fff;color:#3c4043;border:1px solid #dadce0}
table{width:100%;border-collapse:collapse;margin-top:8px}
th{text-align:left;padding:10px;border-bottom:2px solid #dadce0;font-size:14px;color:#5f6368}
td{padding:10px;border-bottom:1px solid #eee;font-size:15px}
.empty{padding:30px;text-align:center;color:#9aa0a6}
</style></head><body>
<div class="hd"><h1>Rule Manager</h1><a href="/">← தமிழ் நீதி நயம்</a></div>
<div class="wrap">
  <div class="row">
    <input id="w" placeholder="Wrong word">
    <input id="c" placeholder="Correct word">
    <input id="n" placeholder="Note (optional)">
    <button onclick="save()" id="btn">Add Rule</button>
    <button onclick="reset()" class="sec" id="cancel" style="display:none">Cancel</button>
  </div>
  <div id="list"></div>
</div>
<script>
var editing=-1;
function load(){fetch('/api/user-rules').then(function(r){return r.json()}).then(function(d){
if(!d.rules.length){document.getElementById('list').innerHTML='<div class="empty">No rules yet.</div>';return}
var h='<table><tr><th>Wrong</th><th>Correct</th><th>Note</th><th></th></tr>';
d.rules.forEach(function(r,i){h+='<tr><td>'+r.wrong+'</td><td>'+r.correct+'</td><td>'+(r.note||'')+'</td>'+
'<td><button class="sec" onclick="edit('+i+')">Edit</button> <button class="del" onclick="del('+i+')">Delete</button></td></tr>';});
document.getElementById('list').innerHTML=h+'</table>';});}
function save(){var w=document.getElementById('w').value,c=document.getElementById('c').value,n=document.getElementById('n').value;
if(!w.trim()||!c.trim()){alert('Both word fields required');return}
var url=editing<0?'/api/user-rules/add':'/api/user-rules/update';
fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({index:editing,wrong:w,correct:c,note:n})})
.then(function(r){return r.json()}).then(function(d){if(!d.ok){alert(d.msg);return}reset();load();});}
function edit(i){fetch('/api/user-rules').then(function(r){return r.json()}).then(function(d){
var r=d.rules[i];document.getElementById('w').value=r.wrong;document.getElementById('c').value=r.correct;
document.getElementById('n').value=r.note||'';editing=i;document.getElementById('btn').textContent='Save Changes';
document.getElementById('cancel').style.display='inline-block';});}
function del(i){if(!confirm('Delete this rule permanently?'))return;
fetch('/api/user-rules/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({index:i})}).then(function(){load();});}
function reset(){editing=-1;document.getElementById('w').value='';document.getElementById('c').value='';
document.getElementById('n').value='';document.getElementById('btn').textContent='Add Rule';
document.getElementById('cancel').style.display='none';}
load();
</script></body></html>"""


NEG_EXAMPLES_PAGE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Negative Examples</title>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Noto+Sans+Tamil:wght@400;500&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#f8f9fa;}
.hd{background:linear-gradient(135deg,#0d1b3e,#162040);padding:16px 24px;border-bottom:2px solid #c9a84c;display:flex;align-items:center;justify-content:space-between;}
.hd h1{font-size:18px;font-weight:700;color:#c9a84c;font-family:Cinzel,serif;}
.hd a{color:#e8c76a;text-decoration:none;font-size:13px;}
.badge{background:rgba(201,168,76,0.2);border:1px solid rgba(201,168,76,0.4);color:#f4d98b;padding:3px 12px;border-radius:20px;font-size:12px;margin-left:12px;}
.wrap{max-width:960px;margin:24px auto;padding:0 16px;}
.add-box{background:#fff;border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,0.08);padding:20px;margin-bottom:20px;border:1px solid #e0e0e0;}
.add-box h2{font-size:12px;font-weight:700;color:#5f6368;margin-bottom:12px;text-transform:uppercase;letter-spacing:0.8px;}
.input-row{display:flex;gap:8px;}
.sent-input{flex:1;padding:10px 14px;border:1.5px solid #dadce0;border-radius:6px;font-size:15px;font-family:Noto Sans Tamil,sans-serif;}
.sent-input:focus{outline:none;border-color:#1a73e8;}
.btn{padding:10px 16px;border-radius:6px;cursor:pointer;font-size:13px;font-weight:600;border:none;white-space:nowrap;}
.btn.blue{background:#1a73e8;color:#fff;} .btn.blue:hover{background:#1557b0;}
.btn.gray{background:#f8f9fa;color:#3c4043;border:1px solid #dadce0;} .btn.gray:hover{background:#e8eaed;}
.btn.green{background:#1e8e3e;color:#fff;}
.btn.red{background:#d93025;color:#fff;}
.test-result{margin-top:10px;padding:10px 14px;border-radius:6px;font-size:13px;font-family:Noto Sans Tamil,sans-serif;display:none;}
.safe{background:#e6f4ea;color:#137333;border:1px solid #ceead6;}
.unsafe{background:#fce8e6;color:#c5221f;border:1px solid #f5c6c2;}
.list-card{background:#fff;border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,0.08);border:1px solid #e0e0e0;overflow:hidden;}
.list-hd{background:#f8f9fa;padding:10px 16px;border-bottom:1px solid #e0e0e0;display:flex;align-items:center;justify-content:space-between;}
.list-hd span{font-size:13px;font-weight:600;color:#3c4043;}
.search{padding:6px 12px;border:1px solid #dadce0;border-radius:4px;font-size:13px;width:220px;}
.row{display:flex;align-items:center;padding:9px 16px;border-bottom:1px solid #f1f3f4;gap:10px;}
.row:last-child{border-bottom:none;} .row:hover{background:#f8f9fa;}
.num{font-size:11px;color:#9aa0a6;width:30px;flex-shrink:0;font-weight:600;}
.txt{flex:1;font-size:14px;font-family:Noto Sans Tamil,sans-serif;color:#202124;line-height:1.5;}
.edit-inp{flex:1;padding:5px 10px;border:1.5px solid #1a73e8;border-radius:4px;font-size:14px;font-family:Noto Sans Tamil,sans-serif;display:none;}
.acts{display:flex;gap:5px;flex-shrink:0;}
.ab{background:#f8f9fa;color:#5f6368;border:1px solid #dadce0;padding:4px 10px;border-radius:4px;cursor:pointer;font-size:12px;}
.ab:hover{background:#e8eaed;} .ab.r{color:#d93025;} .ab.g{color:#1e8e3e;}
.empty{padding:40px;text-align:center;color:#9aa0a6;font-size:14px;}
</style></head><body>
<div class="hd">
  <div style="display:flex;align-items:center;">
    <h1>🛡 Negative Examples</h1>
    <span class="badge" id="badge">{{ count }} sentences</span>
  </div>
  <a href="/">← Dashboard</a>
</div>
<div class="wrap">
  <div class="add-box">
    <h2>Add New Correct Sentence</h2>
    <div class="input-row">
      <input type="text" class="sent-input" id="newSent" placeholder="Type a correct Tamil sentence that must NOT be changed by any rule…">
      <button class="btn gray" onclick="testSent()">Test</button>
      <button class="btn blue" onclick="addSent()">Add</button>
    </div>
    <div class="test-result" id="testRes"></div>
  </div>
  <div class="list-card">
    <div class="list-hd">
      <span id="listLabel">All Sentences</span>
      <input type="text" class="search" placeholder="Search…" oninput="filter(this.value)">
    </div>
    <div id="list"></div>
  </div>
</div>
<script>
var all=[];
function load(){
  fetch('/api/negative-examples').then(r=>r.json()).then(d=>{
    all=d.sentences||[];
    document.getElementById('badge').textContent=all.length+' sentences';
    render(all);
  });
}
function render(arr){
  var el=document.getElementById('list');
  if(!arr.length){el.innerHTML='<div class="empty">No sentences yet.</div>';return;}
  el.innerHTML=arr.map(function(s,i){
    var ri=all.indexOf(s);
    return '<div class="row" id="r'+ri+'">' +
      '<div class="num">'+(ri+1)+'</div>' +
      '<div class="txt" id="t'+ri+'">'+esc(s)+'</div>' +
      '<input class="edit-inp" id="e'+ri+'" value="'+esc(s)+'">' +
      '<div class="acts">' +
        '<button class="ab" onclick="startEdit('+ri+')">Edit</button>' +
        '<button class="ab g" id="sv'+ri+'" style="display:none" onclick="saveEdit('+ri+')">Save</button>' +
        '<button class="ab r" onclick="del('+ri+')">Delete</button>' +
      '</div></div>';
  }).join('');
}
function filter(q){
  q=q.toLowerCase();
  render(q?all.filter(s=>s.toLowerCase().includes(q)):all);
}
function testSent(){
  var s=document.getElementById('newSent').value.trim();
  if(!s){alert('Enter a sentence first');return;}
  var res=document.getElementById('testRes');
  res.style.display='block';res.className='test-result';res.textContent='Testing…';
  fetch('/api/negative-examples/test',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sentence:s})})
  .then(r=>r.json()).then(d=>{
    if(d.safe){res.className='test-result safe';res.textContent='✅ Safe — no rules fire. Good to add!';}
    else{res.className='test-result unsafe';res.textContent='⚠ Rules fire: '+d.changes.map(c=>c.wrong+'→'+c.correct).join(', ')+'. Fix before adding.';}
  });
}
function addSent(){
  var s=document.getElementById('newSent').value.trim();
  if(!s){alert('Enter a sentence');return;}
  fetch('/api/negative-examples/add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sentence:s})})
  .then(r=>r.json()).then(d=>{
    if(d.ok){document.getElementById('newSent').value='';document.getElementById('testRes').style.display='none';load();}
    else alert(d.msg);
  });
}
function startEdit(i){
  document.getElementById('t'+i).style.display='none';
  document.getElementById('e'+i).style.display='block';
  document.getElementById('sv'+i).style.display='inline-block';
  document.getElementById('e'+i).focus();
}
function saveEdit(i){
  var s=document.getElementById('e'+i).value.trim();
  if(!s){alert('Cannot be empty');return;}
  fetch('/api/negative-examples/update',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({index:i,sentence:s})})
  .then(r=>r.json()).then(d=>{if(d.ok)load();else alert(d.msg);});
}
function del(i){
  if(!confirm('Delete this sentence?'))return;
  fetch('/api/negative-examples/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({index:i})})
  .then(r=>r.json()).then(d=>{if(d.ok)load();else alert(d.msg);});
}
function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
load();
</script></body></html>"""

@app.route('/negative-examples')
@login_required
def negative_examples_page():
    import os, json
    DATA_DIR = os.path.expanduser("~/NGK_Solai_Data")
    path = os.path.join(DATA_DIR, "tamil_negative_examples.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        sentences = data.get("sentences", [])
    except:
        sentences = []
    return render_template_string(NEG_EXAMPLES_PAGE, sentences=sentences, count=len(sentences))

@app.route('/api/negative-examples', methods=['GET'])
@login_required
def api_neg_get():
    import os, json
    DATA_DIR = os.path.expanduser("~/NGK_Solai_Data")
    path = os.path.join(DATA_DIR, "tamil_negative_examples.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return jsonify({'sentences': data.get("sentences", [])})
    except:
        return jsonify({'sentences': []})

@app.route('/api/negative-examples/add', methods=['POST'])
@login_required
def api_neg_add():
    import os, json
    DATA_DIR = os.path.expanduser("~/NGK_Solai_Data")
    path = os.path.join(DATA_DIR, "tamil_negative_examples.json")
    d = request.json or {}
    sentence = d.get('sentence', '').strip()
    if not sentence:
        return jsonify({'ok': False, 'msg': 'Empty sentence'})
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {"description": "Negative examples", "sentences": []}
    if sentence in data['sentences']:
        return jsonify({'ok': False, 'msg': 'Already exists'})
    data['sentences'].append(sentence)
    with open(path, 'w', encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return jsonify({'ok': True, 'count': len(data['sentences'])})

@app.route('/api/negative-examples/delete', methods=['POST'])
@login_required
def api_neg_delete():
    import os, json
    DATA_DIR = os.path.expanduser("~/NGK_Solai_Data")
    path = os.path.join(DATA_DIR, "tamil_negative_examples.json")
    d = request.json or {}
    idx = int(d.get('index', -1))
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if 0 <= idx < len(data['sentences']):
            data['sentences'].pop(idx)
            with open(path, 'w', encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'msg': str(e)})
    return jsonify({'ok': False, 'msg': 'Invalid index'})

@app.route('/api/negative-examples/update', methods=['POST'])
@login_required
def api_neg_update():
    import os, json
    DATA_DIR = os.path.expanduser("~/NGK_Solai_Data")
    path = os.path.join(DATA_DIR, "tamil_negative_examples.json")
    d = request.json or {}
    idx = int(d.get('index', -1))
    sentence = d.get('sentence', '').strip()
    if not sentence:
        return jsonify({'ok': False, 'msg': 'Empty sentence'})
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if 0 <= idx < len(data['sentences']):
            data['sentences'][idx] = sentence
            with open(path, 'w', encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'msg': str(e)})
    return jsonify({'ok': False, 'msg': 'Invalid index'})

@app.route('/api/negative-examples/test', methods=['POST'])
@login_required
def api_neg_test():
    """Test a sentence against all rules — should return 0 changes."""
    from rule_store import load_all_rules, apply_rules
    d = request.json or {}
    sentence = d.get('sentence', '').strip()
    if not sentence:
        return jsonify({'ok': False, 'msg': 'Empty'})
    rules, _ = load_all_rules()
    out, changes = apply_rules(sentence, rules)
    return jsonify({
        'ok': True,
        'original': sentence,
        'corrected': out,
        'changes': changes,
        'safe': len(changes) == 0
    })

@app.route('/rules')
@login_required
def rules_page():
    return render_template_string(RULES_PAGE)

@app.route('/api/user-rules')
@login_required
def api_user_rules():
    return jsonify({'rules': user_rules.load()})

@app.route('/api/user-rules/add', methods=['POST'])
@login_required
def api_user_add():
    d = request.json or {}
    ok, msg = user_rules.add(d.get('wrong',''), d.get('correct',''), d.get('note',''))
    if ok:
        engine.corrections[d.get('wrong','').strip()] = d.get('correct','').strip()
    return jsonify({'ok': ok, 'msg': msg})

@app.route('/api/user-rules/update', methods=['POST'])
@login_required
def api_user_update():
    d = request.json or {}
    ok, msg = user_rules.update(int(d.get('index',-1)), d.get('wrong',''),
                                d.get('correct',''), d.get('note',''))
    return jsonify({'ok': ok, 'msg': msg})

@app.route('/api/user-rules/delete', methods=['POST'])
@login_required
def api_user_delete():
    d = request.json or {}
    ok, msg = user_rules.delete(int(d.get('index',-1)))
    return jsonify({'ok': ok, 'msg': msg})

# ─── Password & User Management Routes ───────────────────────────────────────

CHANGE_PW_PAGE = '''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>கடவுச்சொல் மாற்றம்</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f0f2f5;display:flex;align-items:center;justify-content:center;min-height:100vh}
.card{background:#fff;padding:36px;border-radius:10px;box-shadow:0 2px 12px rgba(0,0,0,.15);width:100%;max-width:420px}
h2{color:#0d1b3e;margin-bottom:6px;font-size:20px}
.sub{color:#666;font-size:13px;margin-bottom:24px}
label{display:block;font-size:13px;color:#444;margin-bottom:4px;margin-top:14px}
input{width:100%;padding:10px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px}
input:focus{outline:none;border-color:#c9a84c}
.btn{width:100%;margin-top:20px;padding:11px;background:#0d1b3e;color:#fff;border:none;border-radius:6px;font-size:15px;cursor:pointer}
.btn:hover{background:#c9a84c;color:#0d1b3e}
.error{background:#fff0f0;color:#c0392b;padding:10px;border-radius:6px;font-size:13px;margin-top:12px}
.rules{background:#f8f9fa;padding:10px 14px;border-radius:6px;font-size:12px;color:#555;margin-top:12px;line-height:1.8}
</style></head><body>
<div class="card">
  <h2>கடவுச்சொல் மாற்றம்</h2>
  <p class="sub">{% if forced %}முதல் உள்நுழைவு — புதிய கடவுச்சொல் அமைக்கவும்{% else %}உங்கள் கடவுச்சொல்லை மாற்றவும்{% endif %}</p>
  {% if error %}<div class="error">{{ error }}</div>{% endif %}
  <form method="POST">
    {% if not forced %}
    <label>தற்போதைய கடவுச்சொல்</label>
    <input type="password" name="current_password" required>
    {% endif %}
    <label>புதிய கடவுச்சொல்</label>
    <input type="password" name="new_password" required>
    <label>புதிய கடவுச்சொல் உறுதிப்படுத்தல்</label>
    <input type="password" name="confirm_password" required>
    <div class="rules">
      ✔ குறைந்தது 8 எழுத்துகள்<br>
      ✔ பெரிய எழுத்து (A-Z)<br>
      ✔ சிறிய எழுத்து (a-z)<br>
      ✔ எண் (0-9)<br>
      ✔ சிறப்பு எழுத்து (!@#$ போன்றவை)
    </div>
    <button type="submit" class="btn">மாற்றம் செய்</button>
  </form>
</div></body></html>'''

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    error = None
    if request.method == 'POST':
        current = request.form.get('current_password', '')
        new_pw  = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')
        username = session['username']
        if not um.authenticate(username, current):
            error = 'தற்போதைய கடவுச்சொல் தவறு'
        elif new_pw != confirm:
            error = 'புதிய கடவுச்சொல் பொருந்தவில்லை'
        else:
            ok, err = um.change_password(username, new_pw)
            if ok:
                return redirect(url_for('index'))
            error = err
    return render_template_string(CHANGE_PW_PAGE, error=error, forced=False)

@app.route('/change-password-forced', methods=['GET', 'POST'])
def change_password_forced():
    if 'username' not in session:
        return redirect(url_for('login'))
    error = None
    if request.method == 'POST':
        new_pw  = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')
        if new_pw != confirm:
            error = 'கடவுச்சொல் பொருந்தவில்லை'
        else:
            ok, err = um.change_password(session['username'], new_pw)
            if ok:
                return redirect(url_for('index'))
            error = err
    return render_template_string(CHANGE_PW_PAGE, error=error, forced=True)

# ─── Admin User Management Page ───────────────────────────────────────────────

ADMIN_USERS_PAGE = '''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>பயனர் நிர்வாகம்</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f0f2f5}
.hd{background:linear-gradient(135deg,#0d1b3e,#162040);color:#fff;padding:16px 24px;display:flex;align-items:center;gap:16px;border-bottom:2px solid #c9a84c}
.hd h1{font-size:18px;color:#c9a84c;flex:1}
.hd a{color:#e8c76a;font-size:13px;text-decoration:none}
.wrap{max-width:860px;margin:28px auto;padding:0 16px}
.card{background:#fff;border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,.12);padding:24px;margin-bottom:24px}
h2{font-size:16px;color:#0d1b3e;margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid #eee}
table{width:100%;border-collapse:collapse;font-size:14px}
th{background:#f8f9fa;padding:10px 12px;text-align:left;color:#444;font-weight:600;border-bottom:2px solid #eee}
td{padding:10px 12px;border-bottom:1px solid #f0f0f0;color:#333}
.badge{display:inline-block;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600}
.badge-admin{background:#fff3cd;color:#856404}
.badge-user{background:#d1ecf1;color:#0c5460}
.badge-warn{background:#f8d7da;color:#721c24}
label{display:block;font-size:13px;color:#444;margin-bottom:4px;margin-top:12px}
input,select{width:100%;padding:9px 11px;border:1px solid #ddd;border-radius:6px;font-size:13px}
input:focus,select:focus{outline:none;border-color:#c9a84c}
.btn{padding:9px 18px;border:none;border-radius:6px;font-size:13px;cursor:pointer;font-weight:600}
.btn-primary{background:#0d1b3e;color:#fff}
.btn-primary:hover{background:#c9a84c;color:#0d1b3e}
.btn-danger{background:#dc3545;color:#fff;font-size:12px;padding:5px 12px}
.btn-danger:hover{background:#b02a37}
.btn-sm{font-size:12px;padding:5px 12px}
.msg{padding:10px 14px;border-radius:6px;font-size:13px;margin-bottom:16px}
.msg-ok{background:#d4edda;color:#155724}
.msg-err{background:#f8d7da;color:#721c24}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.rules{font-size:11px;color:#888;margin-top:6px;line-height:1.7}
</style></head><body>
<div class="hd">
  <h1>⚖ பயனர் நிர்வாகம்</h1>
  <a href="/">← முகப்பு</a>
</div>
<div class="wrap">
  {% if msg %}<div class="msg msg-ok">{{ msg }}</div>{% endif %}
  {% if err %}<div class="msg msg-err">{{ err }}</div>{% endif %}

  <div class="card">
    <h2>பயனர்கள்</h2>
    <table>
      <tr><th>பயனர் பெயர்</th><th>பங்கு</th><th>நிலை</th><th>உருவாக்கிய தேதி</th><th>நடவடிக்கை</th></tr>
      {% for u in users %}
      <tr>
        <td>{{ u.username }}</td>
        <td><span class="badge badge-{{ u.role }}">{{ u.role }}</span></td>
        <td>{% if u.must_change %}<span class="badge badge-warn">கடவுச்சொல் மாற்றம் தேவை</span>{% else %}சரி{% endif %}</td>
        <td>{{ u.created[:10] if u.created else '-' }}</td>
        <td>
          {% if u.username != session_user %}
          <form method="POST" action="/admin/users/delete" style="display:inline" onsubmit="return confirm('நீக்கவா?')">
            <input type="hidden" name="username" value="{{ u.username }}">
            <button class="btn btn-danger">நீக்கு</button>
          </form>
          {% endif %}
          <form method="POST" action="/admin/users/reset-password" style="display:inline;margin-left:6px">
            <input type="hidden" name="username" value="{{ u.username }}">
            <input type="text" name="new_password" placeholder="புதிய கடவுச்சொல்" style="width:160px;display:inline;padding:4px 8px" required>
            <button class="btn btn-sm btn-primary" style="margin-left:4px">மீட்டமை</button>
          </form>
        </td>
      </tr>
      {% endfor %}
    </table>
  </div>

  <div class="card">
    <h2>புதிய பயனர் சேர்</h2>
    <form method="POST" action="/admin/users/add">
      <div class="row2">
        <div>
          <label>பயனர் பெயர்</label>
          <input type="text" name="username" placeholder="letters, numbers, _" required>
        </div>
        <div>
          <label>பங்கு</label>
          <select name="role">
            <option value="user">user</option>
            <option value="admin">admin</option>
          </select>
        </div>
      </div>
      <label>தற்காலிக கடவுச்சொல்</label>
      <input type="text" name="password" placeholder="பயனர் முதல் உள்நுழைவில் மாற்ற வேண்டும்" required>
      <div class="rules">
        ✔ குறைந்தது 8 எழுத்துகள் &nbsp;✔ பெரிய எழுத்து &nbsp;✔ சிறிய எழுத்து &nbsp;✔ எண் &nbsp;✔ சிறப்பு எழுத்து (!@#$)
      </div>
      <button type="submit" class="btn btn-primary" style="margin-top:16px">பயனர் சேர்</button>
    </form>
  </div>
</div></body></html>'''

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        if not um.is_admin(session['username']):
            return "அணுகல் மறுக்கப்பட்டது", 403
        return f(*args, **kwargs)
    return decorated

@app.route('/admin/users')
@admin_required
def admin_users():
    return render_template_string(ADMIN_USERS_PAGE,
        users=um.list_users(),
        session_user=session['username'],
        msg=request.args.get('msg'),
        err=request.args.get('err'))

@app.route('/admin/users/add', methods=['POST'])
@admin_required
def admin_add_user():
    username = request.form.get('username','').strip()
    password = request.form.get('password','')
    role     = request.form.get('role','user')
    ok, err  = um.add_user(username, password, role)
    if ok:
        return redirect(url_for('admin_users', msg=f"'{username}' சேர்க்கப்பட்டது"))
    return redirect(url_for('admin_users', err=err))

@app.route('/admin/users/delete', methods=['POST'])
@admin_required
def admin_delete_user():
    username = request.form.get('username','')
    ok, err  = um.delete_user(username)
    if ok:
        return redirect(url_for('admin_users', msg=f"'{username}' நீக்கப்பட்டது"))
    return redirect(url_for('admin_users', err=err))

@app.route('/admin/users/reset-password', methods=['POST'])
@admin_required
def admin_reset_password():
    username = request.form.get('username','')
    new_pw   = request.form.get('new_password','')
    ok, err  = um.change_password(username, new_pw)
    if ok:
        # Mark must_change so user resets on next login
        import json
        data_dir = os.environ.get("DATA_DIR", os.path.expanduser("~/NGK_Solai_Data"))
        uf = os.path.join(data_dir, "users.json")
        with open(uf, "r", encoding="utf-8") as f:
            data = json.load(f)
        if username in data:
            data[username]['must_change'] = True
            with open(uf, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        return redirect(url_for('admin_users', msg=f"'{username}' கடவுச்சொல் மீட்டமைக்கப்பட்டது"))
    return redirect(url_for('admin_users', err=err))

# ── Solai Kaaval routes ───────────────────────────────────────────────────────
@app.route('/solai-kaaval')
def solai_kaaval_page():
    from flask import session, redirect, url_for
    if not session.get('user'):
        return redirect(url_for('login'))
    return redirect('/#solai')   # served inline via the SPA panel below

@app.route('/api/solai/anonymise', methods=['POST'])
def solai_anonymise():
    from flask import session, jsonify, request
    if not session.get('user'):
        return jsonify({'error': 'not authenticated'}), 401
    data = request.get_json(force=True) or {}
    text     = data.get('text', '')
    ascii_tok = bool(data.get('ascii', False))
    disable  = data.get('disable', [])
    lanes    = tuple(data.get('lanes') or ('english', 'tamil'))
    anon, mapping = _solai.anonymise(text, ascii_tokens=ascii_tok, lanes=lanes)
    kill = set()
    for key in disable:
        for t in _SOLAI_TOGGLES.get(key, []):
            kill.add(t)
    if kill:
        for tok in list(mapping):
            if mapping[tok]['type'] in kill:
                anon = anon.replace(tok, mapping[tok]['original'])
                del mapping[tok]
    return jsonify({'anon': anon, 'mapping': mapping,
                    'audit': _solai.audit(mapping)})

@app.route('/api/solai/deanonymise', methods=['POST'])
def solai_deanonymise():
    from flask import session, jsonify, request
    if not session.get('user'):
        return jsonify({'error': 'not authenticated'}), 401
    data = request.get_json(force=True) or {}
    restored = _solai.deanonymise(data.get('text', ''), data.get('mapping', {}))
    return jsonify({'restored': restored})
# ─────────────────────────────────────────────────────────────────────────────

# ── QR Code Generator — opens as separate window ──────────────────────────────
@app.route('/qr-generator')
@login_required
def qr_generator():
    return render_template_string(QR_PAGE_HTML)

QR_PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>QR குறியீடு — Tamil Neethi Nayam</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
<style>
:root {
  --navy:    #0d1b3e;
  --navy2:   #162040;
  --gold:    #c8960c;
  --gold-bg: #fdf3e3;
  --gold-bd: #d4a027;
  --accent:  #1a5276;
  --acc-lt:  #2e86c1;
  --acc-bg:  #eaf3fb;
  --safe:    #1a7a4a;
  --safe-bg: #eaf7ef;
  --paper:   #f8f7f4;
  --rule:    #d0cdc5;
  --ink:     #1a1a2e;
  --ink-mid: #4a4a6a;
  --ink-dim: #8a90a4;
}
*,*::before,*::after { box-sizing:border-box; margin:0; padding:0; }
body { font-family:'Segoe UI',system-ui,sans-serif; background:var(--paper); color:var(--ink); min-height:100vh; display:flex; flex-direction:column; }

header { background:var(--navy); color:#fff; padding:14px 28px; display:flex; align-items:center; gap:12px; border-bottom:3px solid var(--acc-lt); flex-shrink:0; }
.h-icon { font-size:1.4rem; }
.h-t h1 { font-size:1.15rem; font-weight:700; letter-spacing:.01em; }
.h-t p  { font-size:.72rem; color:#8ab; margin-top:2px; }
.h-badge { margin-left:auto; background:var(--safe); color:#fff; font-size:.68rem; font-weight:600; padding:4px 11px; border-radius:20px; letter-spacing:.05em; }
.h-close { margin-left:12px; background:rgba(255,255,255,.12); border:none; color:#fff; font-size:.8rem; font-weight:600; padding:6px 14px; border-radius:6px; cursor:pointer; }
.h-close:hover { background:rgba(255,255,255,.22); }

main { flex:1; overflow-y:auto; padding:28px; }
.grid { max-width:820px; margin:0 auto; display:grid; grid-template-columns:1fr 1fr; gap:20px; }
@media(max-width:580px){ .grid{ grid-template-columns:1fr; } }

.card { background:#fff; border:1px solid var(--rule); border-radius:9px; box-shadow:0 1px 8px rgba(26,26,46,.07); padding:22px; }
.card.full { grid-column:1/-1; }
.card-title { font-size:.67rem; font-weight:700; letter-spacing:.11em; text-transform:uppercase; color:var(--accent); margin-bottom:14px; padding-bottom:8px; border-bottom:2px solid var(--acc-bg); }

label.lbl { display:block; font-size:.79rem; font-weight:600; color:var(--ink-mid); margin-bottom:6px; }
.inp-wrap { position:relative; }
input.qin { width:100%; padding:10px 82px 10px 13px; border:1.5px solid var(--rule); border-radius:6px; font-size:.98rem; font-family:'Courier New',monospace; font-weight:700; letter-spacing:.07em; color:var(--ink); background:var(--paper); outline:none; transition:border-color .15s; }
input.qin:focus { border-color:var(--acc-lt); background:#fff; }
.ctr { position:absolute; right:10px; top:50%; transform:translateY(-50%); font-size:.72rem; font-weight:700; color:var(--ink-dim); pointer-events:none; }
.ctr.warn { color:var(--gold); }
.ctr.full { color:var(--safe); }
.prev { margin-top:7px; font-size:.76rem; color:var(--ink-mid); min-height:16px; }
.prev .cv { font-family:'Courier New',monospace; font-weight:700; color:var(--accent); }
.prev .ct { background:var(--acc-bg); color:var(--accent); border-radius:3px; padding:1px 5px; font-size:.68rem; font-weight:700; margin-left:5px; }
.err { display:none; background:#fdecea; border:1px solid #fecaca; color:#922b21; border-radius:6px; padding:8px 12px; font-size:.78rem; font-weight:600; margin-top:8px; }
.btn-gen { margin-top:16px; width:100%; padding:11px; background:var(--navy); color:#fff; border:none; border-radius:6px; font-size:.9rem; font-weight:700; cursor:pointer; letter-spacing:.04em; transition:background .14s,transform .1s; }
.btn-gen:hover { background:var(--navy2); }
.btn-gen:active { transform:scale(.97); }

.rules { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
.chip { background:var(--acc-bg); border:1px solid #c5d2f0; border-radius:5px; padding:8px 10px; font-size:.72rem; color:var(--accent); font-weight:600; display:flex; gap:6px; }

.qr-stage { display:flex; flex-direction:column; align-items:center; gap:12px; padding:18px; background:var(--acc-bg); border-radius:8px; border:1.5px solid #c5d2f0; }
.qr-lbl { font-size:.68rem; font-weight:700; letter-spacing:.1em; color:var(--accent); text-transform:uppercase; }
#qr-wrap { background:#fff; padding:12px; border-radius:7px; box-shadow:0 2px 10px rgba(26,82,118,.13); }
#qr-wrap canvas, #qr-wrap img { display:block; }
.qr-val { font-family:'Courier New',monospace; font-size:.92rem; font-weight:700; letter-spacing:.1em; color:var(--ink); background:#fff; border:1px solid var(--rule); border-radius:4px; padding:5px 14px; }

.dl-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:9px; }
.dl-btn { display:flex; flex-direction:column; align-items:center; gap:5px; padding:11px 8px; border:1.5px solid var(--rule); border-radius:7px; background:#fff; cursor:pointer; text-align:center; transition:border-color .14s,background .14s,transform .1s; }
.dl-btn:hover { border-color:var(--acc-lt); background:var(--acc-bg); }
.dl-btn:active { transform:scale(.97); }
.dl-btn .di { font-size:1.4rem; }
.dl-btn .dn { font-size:.73rem; font-weight:700; color:var(--ink); }
.dl-btn .dd { font-size:.66rem; color:var(--ink-dim); }
.dl-btn.cp { border-color:var(--safe); background:var(--safe-bg); }
.dl-btn.cp .dn { color:var(--safe); }

.fmt { background:#fffbec; border:1px solid #f5dfa0; border-radius:7px; padding:12px 16px; }
.fmt h4 { font-size:.75rem; font-weight:700; color:var(--gold); margin-bottom:8px; }
.fmt ul { list-style:none; display:flex; flex-direction:column; gap:5px; }
.fmt li { font-size:.75rem; color:var(--ink-mid); display:flex; gap:7px; }
.fmt li::before { content:"▸"; color:var(--gold); flex-shrink:0; }
</style>
</head>
<body>

<header>
  <span class="h-icon">⬛</span>
  <div class="h-t">
    <h1>QR குறியீடு உருவாக்கி</h1>
    <p>Tamil Neethi Nayam — Court Document QR Generator</p>
  </div>
  
  <a class="h-close" href="/">🏠 Home</a>     
</header>

<main>
<div class="grid">

  <div class="card">
    <div class="card-title">Case / Document Identifier</div>
    <label class="lbl" for="qin">வழக்கு எண் அல்லது ஆவண குறிப்பு</label>
    <div class="inp-wrap">
      <input class="qin" type="text" id="qin" maxlength="60"
             placeholder="e.g. TNSA18-000604-2025"
             autocomplete="off" spellcheck="false">
      <span class="ctr" id="qctr">0 / 20</span>
    </div>
    <div class="prev" id="qprev">சுத்தப்படுத்தப்பட்ட வெளியீடு இங்கு தோன்றும்</div>
    <div class="err" id="qerr"></div>
    <button class="btn-gen" onclick="genQR()">QR குறியீடு உருவாக்கு ▶</button>
  </div>

  <div class="card">
    <div class="card-title">தானியங்கி சுத்திகரிப்பு விதிகள்</div>
    <div class="rules">
      <div class="chip">⬆ சிறிய → பெரிய எழுத்து</div>
      <div class="chip">✂ இடைவெளி நீக்கம்</div>
      <div class="chip">✂ சிறப்பு எழுத்துகள் நீக்கம்</div>
      <div class="chip">🔢 எழுத்து &amp; எண் மட்டும்</div>
      <div class="chip">📏 அதிகபட்சம் 20 எழுத்துகள்</div>
      <div class="chip">🔒 Error Level H (உயர்நிலை)</div>
    </div>
  </div>

  <div class="card full" id="qout" style="display:none">
    <div class="card-title">உருவாக்கப்பட்ட QR குறியீடு</div>
    <div class="qr-stage">
      <div class="qr-lbl">ஸ்கேன் செய்து சரிபார்க்கவும்</div>
      <div id="qr-wrap"><div id="qr-render"></div></div>
      <div class="qr-val" id="qr-val"></div>
    </div>
    <br>
    <div class="card-title">பதிவிறக்கம் &amp; நகல்</div>
    <div class="dl-grid">
      <button class="dl-btn" onclick="dlPNG()">
        <span class="di">🖼️</span><span class="dn">PNG — High-Res</span><span class="dd">600×600 · அச்சிட</span>
      </button>
      <button class="dl-btn" onclick="dlSVG()">
        <span class="di">📐</span><span class="dn">SVG — Vector</span><span class="dd">ODT/DOCX-க்கு சிறந்தது</span>
      </button>
      <button class="dl-btn" onclick="dlPDF()">
        <span class="di">📄</span><span class="dn">PDF பக்கம்</span><span class="dd">தனி அச்சு பக்கம்</span>
      </button>
      <button class="dl-btn" id="b-svg" onclick="cpSVG(this)">
        <span class="di">📋</span><span class="dn">SVG குறியீடு நகல்</span><span class="dd">ODT / DOCX-ல் ஒட்டவும்</span>
      </button>
      <button class="dl-btn" id="b-b64" onclick="cpB64(this)">
        <span class="di">🔗</span><span class="dn">Base64 URI நகல்</span><span class="dd">HTML-ல் பொதிக்க</span>
      </button>
      <button class="dl-btn" id="b-txt" onclick="cpTxt(this)">
        <span class="di">🅰</span><span class="dn">உரை நகல்</span><span class="dd">20 எழுத்து மதிப்பு</span>
      </button>
    </div>
    <br>
    <div class="fmt">
      <h4>📌 DigiSign-பாதுகாப்பான ஆவண இணைப்பு வழிகாட்டி</h4>
      <ul>
        <li><strong>LibreOffice ODT:</strong> SVG பதிவிறக்கம் → செருகு → படம் → .svg கோப்பு. வெக்டர் வடிவம் — DigiSign மூலம் அழிக்கப்படாது.</li>
        <li><strong>MS Word DOCX:</strong> SVG பதிவிறக்கம் → செருகு → படங்கள் → .svg கோப்பு. Word 2016+ SVG-ஐ நேரடியாக ஆதரிக்கிறது.</li>
        <li><strong>மாற்று வழி:</strong> SVG குறியீட்டை நகலெடுத்து ஆவண XML மூலத்தில் நேரடியாக ஒட்டவும்.</li>
        <li><strong>அச்சு தரம்:</strong> PNG 600×600, Error Level H — நீதிமன்ற முத்திரையின் கீழும் படிக்கக்கூடியது.</li>
      </ul>
    </div>
  </div>

</div>
</main>

<script>
var _clean='', _svg='', _png='', _qr=null;

function cleanVal(r) {
  return r.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 20);
}

document.getElementById('qin').addEventListener('input', function() {
  var c = cleanVal(this.value), l = c.length;
  var ct = document.getElementById('qctr');
  ct.textContent = l + ' / 20';
  ct.className = 'ctr' + (l===20 ? ' full' : l>15 ? ' warn' : '');
  var pv = document.getElementById('qprev');
  pv.innerHTML = c
    ? 'சுத்தம்: <span class="cv">' + c + '</span><span class="ct">' + (l===20 ? 'தயார்' : (20-l) + ' மேலும்') + '</span>'
    : 'சுத்தப்படுத்தப்பட்ட வெளியீடு இங்கு தோன்றும்';
  document.getElementById('qerr').style.display = 'none';
});

document.getElementById('qin').addEventListener('keydown', function(e) {
  if (e.key === 'Enter') genQR();
});

function genQR() {
  var c = cleanVal(document.getElementById('qin').value.trim());
  var er = document.getElementById('qerr');
  if (!c) { er.textContent = '⚠ வழக்கு எண்ணை உள்ளிடவும்.'; er.style.display = 'block'; return; }
  if (c.length < 3) { er.textContent = '⚠ மிகவும் குறுகியது — குறைந்தது 3 எழுத்துகள் தேவை.'; er.style.display = 'block'; return; }
  er.style.display = 'none';
  _clean = c;

  var wrap = document.getElementById('qr-render');
  wrap.innerHTML = '';
  if (_qr) { try { _qr.clear(); } catch(e) {} }
  _qr = new QRCode(wrap, {
    text: c, width: 280, height: 280,
    colorDark: '#0d1b3e', colorLight: '#ffffff',
    correctLevel: QRCode.CorrectLevel.H
  });

  setTimeout(function() {
    var cv = wrap.querySelector('canvas');
    if (cv) _png = cv.toDataURL('image/png');
    document.getElementById('qr-val').textContent = c;
    document.getElementById('qout').style.display = 'block';
    document.getElementById('qout').scrollIntoView({ behavior: 'smooth', block: 'start' });
    buildSVG(c);
  }, 350);
}

function buildSVG(text) {
  var d = document.createElement('div');
  d.style.cssText = 'position:absolute;left:-9999px;visibility:hidden';
  document.body.appendChild(d);
  new QRCode(d, {
    text: text, width: 500, height: 500,
    colorDark: '#0d1b3e', colorLight: '#fff',
    correctLevel: QRCode.CorrectLevel.H
  });
  setTimeout(function() {
    var cv = d.querySelector('canvas');
    if (cv) {
      if (!_png || _png.length < 100) _png = cv.toDataURL('image/png');
      var ctx = cv.getContext('2d'), w = cv.width, data = ctx.getImageData(0, 0, w, w).data;
      var ms = 1, inR = false;
      for (var x = 0; x < w; x++) {
        var dk = data[x * 4] < 128;
        if (!inR && dk) { inR = true; }
        else if (inR && !dk) { ms = x; break; }
      }
      if (!ms) ms = Math.round(w / 21);
      var mods = Math.round(w / ms), rects = '';
      for (var r = 0; r < mods; r++) {
        for (var cc = 0; cc < mods; cc++) {
          var idx = (Math.round(r * ms) * w + Math.round(cc * ms)) * 4;
          if (data[idx] < 128)
            rects += '<rect x="' + cc + '" y="' + r + '" width="1" height="1" fill="#0d1b3e"/>';
        }
      }
      _svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + mods + ' ' + mods + '" width="500" height="500" shape-rendering="crispEdges">'
           + '<rect width="' + mods + '" height="' + mods + '" fill="#fff"/>' + rects + '</svg>';
    }
    document.body.removeChild(d);
  }, 250);
}

function dlPNG() {
  if (!_png) return;
  var a = document.createElement('a');
  a.href = _png; a.download = 'QR_' + _clean + '.png'; a.click();
}

function dlSVG() {
  if (!_svg) { setTimeout(dlSVG, 400); return; }
  var b = new Blob([_svg], { type: 'image/svg+xml' });
  var a = document.createElement('a');
  a.href = URL.createObjectURL(b); a.download = 'QR_' + _clean + '.svg'; a.click();
  setTimeout(function() { URL.revokeObjectURL(a.href); }, 2000);
}

function dlPDF() {
  var h = '<!DOCTYPE html><html><head><meta charset="UTF-8">'
    + '<style>@page{size:A4;margin:40mm}body{display:flex;flex-direction:column;align-items:center;'
    + 'justify-content:center;font-family:sans-serif;color:#0d1b3e}'
    + 'h2{font-size:13pt;margin-bottom:10px}.code{font-family:monospace;font-size:14pt;font-weight:700;'
    + 'letter-spacing:.1em;margin-top:12px;border:1px solid #d0cdc5;padding:6px 18px;border-radius:5px}'
    + 'svg{width:200px;height:200px}.note{font-size:8pt;color:#8a90a4;margin-top:16px}</style></head>'
    + '<body><h2>Case Reference QR Code</h2>' + (_svg || '')
    + '<div class="code">' + _clean + '</div>'
    + '<div class="note">Tamil Neethi Nayam \xb7 Salem District Courts</div>'
    + '<script>window.onload=function(){window.print();}<\\/script></body></html>';
  var url = URL.createObjectURL(new Blob([h], { type: 'text/html' }));
  window.open(url, '_blank');
  setTimeout(function() { URL.revokeObjectURL(url); }, 5000);
}

function cpSVG(btn) {
  if (!_svg) { setTimeout(function() { cpSVG(btn); }, 500); return; }
  navigator.clipboard.writeText(_svg).then(function() { flash(btn, 'SVG நகல் ✓'); });
}
function cpB64(btn) {
  if (!_png) return;
  navigator.clipboard.writeText(_png).then(function() { flash(btn, 'Base64 நகல் ✓'); });
}
function cpTxt(btn) {
  if (!_clean) return;
  navigator.clipboard.writeText(_clean).then(function() { flash(btn, 'உரை நகல் ✓'); });
}
function flash(btn, msg) {
  var orig = btn.querySelector('.dn').textContent;
  btn.classList.add('cp'); btn.querySelector('.dn').textContent = msg;
  setTimeout(function() { btn.classList.remove('cp'); btn.querySelector('.dn').textContent = orig; }, 2000);
}
</script>
</body>
</html>"""
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
