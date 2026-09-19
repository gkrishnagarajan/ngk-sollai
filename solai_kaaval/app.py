# -*- coding: utf-8 -*-
"""
Solai Kaaval - offline web panel (standalone tester).
Runs entirely on your machine: binds to 127.0.0.1 only, loads no external
resources (no CDN, no fonts, no analytics), and never makes a network call.
The document and the mapping never leave this computer.

Run:   python3 app.py
Open:  http://127.0.0.1:5000
Stop:  Ctrl+C in the terminal
"""

import os
import json
from flask import Flask, request, jsonify, Response

from engine import Anonymiser

app = Flask(__name__)
_anon = Anonymiser(os.path.dirname(os.path.abspath(__file__)))

# toggle key -> the detector types it controls
TOGGLE_TYPES = {
    "aadhaar": ["AADHAAR"],
    "case": ["CASE", "FIR"],
    "dates": ["DATE", "DOB"],
}

PAGE = r"""<!DOCTYPE html>
<html lang="ta">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Solai Kaaval — Anonymiser</title>
<style>
  :root{
    --bg:#f4f1ea; --panel:#fffdf8; --ink:#22201b; --muted:#6b655a;
    --line:#d9d2c4; --accent:#7a5c2e; --accent2:#3a5a40; --danger:#9b2c2c;
  }
  *{box-sizing:border-box}
  body{margin:0;font-family:"Segoe UI",system-ui,Arial,sans-serif;
       background:var(--bg);color:var(--ink);line-height:1.5}
  header{background:var(--accent);color:#fff;padding:14px 20px}
  header h1{margin:0;font-size:19px;letter-spacing:.3px}
  header p{margin:3px 0 0;font-size:12px;opacity:.9}
  .wrap{max-width:1080px;margin:0 auto;padding:18px 20px 60px}
  .grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}
  @media(max-width:820px){.grid{grid-template-columns:1fr}}
  .card{background:var(--panel);border:1px solid var(--line);
        border-radius:10px;padding:16px;margin-bottom:18px}
  .card h2{margin:0 0 10px;font-size:15px;color:var(--accent2)}
  textarea{width:100%;min-height:150px;padding:10px;border:1px solid var(--line);
           border-radius:8px;font-family:inherit;font-size:14px;resize:vertical;
           background:#fff;color:var(--ink)}
  .controls{display:flex;flex-wrap:wrap;gap:14px;align-items:center;margin:10px 0}
  label.chk{font-size:13px;color:var(--muted);cursor:pointer;user-select:none}
  button{font-family:inherit;font-size:14px;padding:9px 16px;border:none;
         border-radius:8px;cursor:pointer;color:#fff;background:var(--accent)}
  button.ghost{background:#eee;color:var(--ink);border:1px solid var(--line)}
  button.go2{background:var(--accent2)}
  button:disabled{opacity:.5;cursor:default}
  .row-btns{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
  table{width:100%;border-collapse:collapse;margin-top:10px;font-size:13px}
  th,td{border:1px solid var(--line);padding:6px 8px;text-align:left;
        vertical-align:top}
  th{background:#efe9dd;font-weight:600}
  td.tok{font-family:"Cascadia Code",Consolas,monospace;white-space:nowrap}
  td [contenteditable]{outline:none;min-width:60px}
  .del{color:var(--danger);cursor:pointer;font-weight:700;text-align:center}
  .muted{color:var(--muted);font-size:12px}
  .audit{font-size:12px;color:var(--muted);margin-top:8px}
  .pill{display:inline-block;background:#efe9dd;border:1px solid var(--line);
        border-radius:20px;padding:2px 10px;margin:2px 4px 0 0;font-size:12px}
  .note{background:#fbf6ea;border:1px solid #e7d9b8;border-radius:8px;
        padding:10px 12px;font-size:12px;color:#5b4a29;margin-top:12px}
</style>
</head>
<body>
<header>
  <h1>Solai Kaaval &middot; Legal Document Anonymiser</h1>
  <p>Runs offline on this computer. Nothing you type here is sent anywhere.</p>
</header>
<div class="wrap">

  <div class="card">
    <h2>1. Original document</h2>
    <textarea id="src" placeholder="Paste the Tamil / English document text here..."></textarea>
    <div class="controls">
      <span class="muted">Redact:</span>
      <label class="chk"><input type="checkbox" id="t_aadhaar" checked> Aadhaar</label>
      <label class="chk"><input type="checkbox" id="t_case" checked> Case / FIR numbers</label>
      <label class="chk"><input type="checkbox" id="t_dates" checked> Dates</label>
      <span class="muted" style="margin-left:12px">Language:</span>
      <label class="chk"><input type="checkbox" id="l_en" checked> English</label>
      <label class="chk"><input type="checkbox" id="l_ta" checked> Tamil</label>
      <label class="chk" style="margin-left:12px"><input type="checkbox" id="ascii"> ASCII tokens [[ ]]</label>
    </div>
    <div class="row-btns">
      <button onclick="doAnon()">Anonymise &rarr;</button>
      <button class="ghost" onclick="clearAll()">Clear</button>
    </div>
  </div>

  <div class="grid">
    <div class="card">
      <h2>2. Anonymised — copy this to your AI</h2>
      <textarea id="anon" placeholder="Anonymised text appears here. You can edit it to catch anything missed."></textarea>
      <div class="row-btns">
        <button class="ghost" onclick="copyAnon()">Copy text</button>
        <button class="ghost" onclick="downloadKey()">Download key file</button>
        <label class="chk ghost" style="padding:9px 16px;border-radius:8px;border:1px solid var(--line);background:#eee">
          Load key file <input type="file" id="keyfile" accept=".json" style="display:none" onchange="loadKey(event)">
        </label>
      </div>
      <div class="audit" id="audit"></div>
    </div>

    <div class="card">
      <h2>3. Bring back the AI output &rarr; restore</h2>
      <textarea id="aiout" placeholder="Paste the text your AI returned (with the tokens still in it)."></textarea>
      <div class="row-btns">
        <button class="go2" onclick="doDeanon()">&larr; De-anonymise</button>
      </div>
      <textarea id="restored" placeholder="Restored text (originals put back) appears here." style="margin-top:10px"></textarea>
    </div>
  </div>

  <div class="card">
    <h2>Mapping — review &amp; correct before using</h2>
    <p class="muted">This table is the only thing that can re-identify the document. Edit an original if a name was captured imperfectly; delete a row to leave that item un-restored; use “Add row” to redact something the tool missed (put your own token, e.g. ⟦PERSON_9⟧, into the anonymised text above and add it here).</p>
    <table id="maptbl"><thead><tr><th>Token</th><th>Type</th><th>Original</th><th></th></tr></thead><tbody></tbody></table>
    <div class="row-btns"><button class="ghost" onclick="addRow()">+ Add row</button></div>
  </div>

  <div class="note">Privacy: this page loads no external code and makes no internet request. The document, the tokens and the key file stay on this machine. Only the anonymised text in box 2 — which you copy out yourself — should ever go to an online AI.</div>
</div>

<script>
function $(id){return document.getElementById(id);}

function disabledTypes(){
  var d=[];
  if(!$('t_aadhaar').checked) d.push('aadhaar');
  if(!$('t_case').checked)    d.push('case');
  if(!$('t_dates').checked)   d.push('dates');
  return d;
}
function lanes(){
  var l=[];
  if($('l_en').checked) l.push('english');
  if($('l_ta').checked) l.push('tamil');
  return l;
}

async function doAnon(){
  var body={text:$('src').value, ascii:$('ascii').checked,
            disable:disabledTypes(), lanes:lanes()};
  var r=await fetch('/anonymise',{method:'POST',
        headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  var data=await r.json();
  $('anon').value=data.anon;
  renderTable(data.mapping);
  var a=data.audit, parts=[];
  for(var k in a.by_type){parts.push('<span class="pill">'+k+': '+a.by_type[k]+'</span>');}
  $('audit').innerHTML='<b>'+a.total_entities+'</b> item(s) redacted &nbsp;'+parts.join(' ');
}

function renderTable(mapping){
  var tb=$('maptbl').getElementsByTagName('tbody')[0];
  tb.innerHTML='';
  for(var tok in mapping){
    var info=mapping[tok];
    addRowValues(tok, info.type||'', info.original||'');
  }
}
function addRowValues(tok,type,orig){
  var tb=$('maptbl').getElementsByTagName('tbody')[0];
  var tr=document.createElement('tr');
  tr.innerHTML='<td class="tok" contenteditable>'+esc(tok)+'</td>'+
               '<td contenteditable>'+esc(type)+'</td>'+
               '<td><span contenteditable>'+esc(orig)+'</span></td>'+
               '<td class="del" onclick="this.parentNode.remove()">&times;</td>';
  tb.appendChild(tr);
}
function addRow(){addRowValues('⟦PERSON_9⟧','PERSON','');}

function collectMapping(){
  var m={}, rows=$('maptbl').getElementsByTagName('tbody')[0].rows;
  for(var i=0;i<rows.length;i++){
    var c=rows[i].cells;
    var tok=c[0].innerText.trim();
    if(!tok) continue;
    m[tok]={type:c[1].innerText.trim(), original:c[2].innerText.trim()};
  }
  return m;
}

async function doDeanon(){
  var body={text:$('aiout').value, mapping:collectMapping()};
  var r=await fetch('/deanonymise',{method:'POST',
        headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  var data=await r.json();
  $('restored').value=data.restored;
}

function copyAnon(){navigator.clipboard.writeText($('anon').value);}
function downloadKey(){
  var blob=new Blob([JSON.stringify(collectMapping(),null,2)],{type:'application/json'});
  var u=URL.createObjectURL(blob), a=document.createElement('a');
  a.href=u; a.download='solai_key.json'; a.click(); URL.revokeObjectURL(u);
}
function loadKey(ev){
  var f=ev.target.files[0]; if(!f) return;
  var rd=new FileReader();
  rd.onload=function(){try{renderTable(JSON.parse(rd.result));}catch(e){alert('Not a valid key file');}};
  rd.readAsText(f);
}
function clearAll(){
  $('src').value='';$('anon').value='';$('aiout').value='';$('restored').value='';
  $('maptbl').getElementsByTagName('tbody')[0].innerHTML='';$('audit').innerHTML='';
}
function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
</script>
</body>
</html>"""


# ----- routes (kept BEFORE the __main__ block) -----
@app.route("/")
def index():
    return Response(PAGE, mimetype="text/html")


@app.route("/anonymise", methods=["POST"])
def route_anonymise():
    data = request.get_json(force=True) or {}
    text = data.get("text", "")
    ascii_tokens = bool(data.get("ascii", False))
    disable = data.get("disable", [])
    lanes = tuple(data.get("lanes") or ("english", "tamil"))

    anon, mapping = _anon.anonymise(text, ascii_tokens=ascii_tokens, lanes=lanes)

    # apply redaction toggles: for a disabled type, put originals back and
    # drop those rows so nothing about them is retained.
    kill = set()
    for key in disable:
        for t in TOGGLE_TYPES.get(key, []):
            kill.add(t)
    if kill:
        for tok in list(mapping):
            if mapping[tok]["type"] in kill:
                anon = anon.replace(tok, mapping[tok]["original"])
                del mapping[tok]

    return jsonify({"anon": anon, "mapping": mapping,
                    "audit": _anon.audit(mapping)})


@app.route("/deanonymise", methods=["POST"])
def route_deanonymise():
    data = request.get_json(force=True) or {}
    text = data.get("text", "")
    mapping = data.get("mapping", {})
    restored = _anon.deanonymise(text, mapping)
    return jsonify({"restored": restored})


if __name__ == "__main__":
    # 127.0.0.1 = this machine only; never exposed to any network.
    app.run(host="127.0.0.1", port=5000, debug=False)
