# -*- coding: utf-8 -*-
"""Build 高中6000 index.html from the 國中2000 template + official CEEC wordlist.
Merges generated content (content_progress.json) into words_full.json, then patches the template.
Safe to re-run."""
import json, re, pathlib, sys

BUILD = pathlib.Path(__file__).parent
TEMPLATE = pathlib.Path(r"C:/Users/c0787/Desktop/App專案/英語單字APP/02_國中2000/index.html")  # 資料夾已重編號
OUTDIR = BUILD.parent
OUTDIR.mkdir(parents=True, exist_ok=True)

full = json.load(open(BUILD/'words_full.json', encoding='utf-8'))
prog = {}
pf = BUILD/'content_progress.json'
if pf.exists():
    prog = json.load(open(pf, encoding='utf-8'))

# merge generated content (keyed by lowercase display word)
filled = 0
for e in full:
    k = e['word'].lower()
    if (not e.get('zh_tw')) and k in prog:
        g = prog[k]
        e['zh_tw'] = g.get('zh_tw', '')
        e['ex']    = g.get('ex', '')
        e['exZh']  = g.get('exZh', '')
        if g.get('topic'): e['topic'] = g['topic']
        if e['zh_tw']: filled += 1

missing = [e for e in full if not e.get('zh_tw')]
print(f"words: {len(full)}  filled-from-progress: {filled}  still-missing: {len(missing)}")

# re-sort by level then alpha, reassign units (50/unit)
full.sort(key=lambda e:(e['level'], e['word'].lower()))
for i,e in enumerate(full):
    e['unit'] = i//50 + 1
NUNITS = full[-1]['unit']
from collections import Counter
LC = Counter(e['level'] for e in full)

# WORDS array: only app-consumed fields (keep it compact)
def slim(e):
    o = {'word':e['word'],'pos':e['pos'],'zh_tw':e['zh_tw'],'level':e['level'],
         'topic':e['topic'] or 'general','ex':e['ex'],'exZh':e['exZh'],'unit':e['unit']}
    return o
words_json = json.dumps([slim(e) for e in full], ensure_ascii=False)

h = TEMPLATE.read_text(encoding='utf-8')

# 1) swap WORDS array
h, n = re.subn(r'const WORDS\s*=\s*\[.*?\];', 'const WORDS = '+words_json+';', h, count=1, flags=re.S)
assert n==1, "WORDS swap failed"

# 2) buildLevelChips opts -> 6 levels with counts
lvlabels = ','.join(f'{{k:{i},t:"第{i}級"}}' for i in range(1,7))
newopts = '{k:"all",t:"全部"},'+lvlabels
h, n = re.subn(r'const opts=\[\{k:"all",t:"全部"\},\{k:1,t:"[^"]*"\},\{k:2,t:"[^"]*"\}\];',
               'const opts=['+newopts+'];', h, count=1)
assert n==1, "levelChips opts swap failed"

# 3) buildLevelChips "all" on-state: length===2 -> ===6
h = h.replace('S.deck.levels.length===2', 'S.deck.levels.length===6')

# 4) pickLevel all -> [1..6]
h, n = re.subn(r'if\(k==="all"\)\s*S\.deck\.levels=\[1,2\];',
               'if(k==="all") S.deck.levels=[1,2,3,4,5,6];', h, count=1)
assert n==1, "pickLevel swap failed"

# 5) DEFAULT deck.levels:[1,2] -> [1..6] + custom deck slot
h, n = re.subn(r'deck:\{\s*levels:\[1,2\]', 'deck:{ levels:[1,2,3,4,5,6], custom:null', h, count=1)
assert n==1, "default deck swap failed"

# 6) titles
h = h.replace('<title>國中英語 2000 單字</title>', '<title>高中英語 6000 單字</title>')
h = h.replace('content="英語2000"', 'content="高中6000"')
h = h.replace('📚 國中英語 2000', '📚 高中英語 6000')

# 7) 會考 -> 學測 (UI labels only; WORDS data has no 會考)
h = h.replace('會考', '學測')

# 8) POS_ZH multi-pos helper + apply to lookups
h = h.replace('"aux":"助動詞"};',
              '"aux":"助動詞",art:"冠詞",abbr:"縮寫"}; const pz=p=>String(p||"").split("/").map(x=>POS_ZH[x]||x).join("／");', 1)
h = h.replace('POS_ZH[w.pos]||w.pos', 'pz(w.pos)')
h = h.replace('POS_ZH[w.pos2]||w.pos2', 'pz(w.pos2)')

# 9) TOPIC_ZH add general
h = h.replace('const TOPIC_ZH={daily:"日常"', 'const TOPIC_ZH={general:"一般",daily:"日常"', 1)

# 10) recolor accent red -> indigo (matches 高中6000 identity / blue icon)
h = h.replace('--accent:#ff6b6b; --accent-d:#e8504f; --accent-soft:#ffe5e5;',
              '--accent:#5b6ee1; --accent-d:#4655c8; --accent-soft:#e6e9fb;', 1)
h = re.sub(r'(name="theme-color"[^>]*content=")[^"]*(")', r'\g<1>#5b6ee1\g<2>', h)

# ============================================================
# 11) 學測考古單字盤點 feature
# ============================================================
exam = json.load(open(BUILD/'exam_words.json', encoding='utf-8'))
# slim exam rows: w, base, years, freq, ans(0/1), level
exam_slim = [{'w':e['w'],'base':e['base'],'years':e['years'],'freq':e.get('freq',1),
              'ans':1 if e['ans'] else 0,'level':e['level']} for e in exam]
exam_json = json.dumps(exam_slim, ensure_ascii=False)
exam_n = len(exam_slim)

# 11a) inject EXAM_WORDS const before POS_ZH
h, n = re.subn(r'const POS_ZH=\{n:"名詞"',
               'const EXAM_WORDS = '+exam_json+';\nconst POS_ZH={n:"名詞"', h, count=1)
assert n==1, "EXAM_WORDS inject failed"

# 11b) inDeck: honour custom deck
h, n = re.subn(r'function inDeck\(w\)\{',
               'function inDeck(w){ if(S.deck&&S.deck.custom){ return S.deck.custom.indexOf(w.word)>=0; }', h, count=1)
assert n==1, "inDeck custom failed"

# 11c) pickUnit inherited level bug: [1,2] -> all 6 (else high-level units go empty) + clear custom
h = h.replace('S.deck.unit=+u; S.deck.levels=[1,2]; S.deck.topic="all";',
              'S.deck.unit=+u; S.deck.levels=[1,2,3,4,5,6]; S.deck.topic="all";', 1)
# 11d) picking a normal deck exits exam-deck mode
h = h.replace('function pickLevel(k){', 'function pickLevel(k){ S.deck.custom=null;', 1)
h = h.replace('function pickTopic(t){', 'function pickTopic(t){ S.deck.custom=null;', 1)
h = h.replace('function pickUnit(u){', 'function pickUnit(u){ S.deck.custom=null;', 1)

# 11e) go() hook
h = h.replace('if(v==="stats") renderStats();',
              'if(v==="stats") renderStats(); if(v==="exam") renderExamPanel();', 1)

# 11e2) add a 6th bottom-nav tab for 考古 (go() already handles highlight+render)
h, n = re.subn(r'(<button id="nav-quiz"[^<]*<span class="ni">📝</span>測驗</button>)',
               r'\1\n    <button id="nav-exam" aria-label="學測考古" onclick="go(\'exam\')"><span class="ni">🎯</span>考古</button>',
               h, count=1)
assert n==1, "nav-exam tab inject failed"

# 11f) home entry button (after quick-actions block)
def _add_home_btn(m):
    return m.group(1) + '\n      <button class="exam-entry" onclick="go(\'exam\')">📝 學測考古單字盤點<small>110–115 全卷 · '+str(exam_n)+' 字 · 劃掉會的、練不會的</small></button>'
h, n = re.subn(r'(番茄鐘</button>\s*</div>)', _add_home_btn, h, count=1)
assert n==1, "home button inject failed"

# 11g) view-exam section before NAV
EXAM_VIEW = '''<section class="view" id="view-exam">
      <div class="topbar"><div class="title">📝 學測考古單字</div><button class="icon-btn" onclick="go('home')">✕</button></div>
      <div class="panel">
        <div style="font-size:12.5px;color:var(--muted);line-height:1.65">過去 6 年（110–115）學測<b style="color:var(--text)">整份考卷</b>出現、且在 6000 字表內的 __EXAM_N__ 字。<b style="color:var(--text)">認識的點一下劃掉</b>，剩下不熟的一鍵變題庫。<b>⭐</b>＝詞彙題考出的正解字；左側色條＝級別；標籤＝出現年數。</div>
        <div id="examCount" style="margin:10px 0 4px;font-size:14px"></div>
        <div class="exam-filters" id="examLevelChips"></div>
        <div class="exam-filters" id="examYearChips"></div>
        <div class="exam-toggles">
          <label><input type="checkbox" id="examReview" onchange="setExamFilter('review',this.checked)"> 🔁 複習模式</label>
          <label><input type="checkbox" id="examShowZh" onchange="setExamFilter('showZh',this.checked)"> 顯示中文</label>
          <label><input type="checkbox" id="examOnlyAns" onchange="setExamFilter('onlyAns',this.checked)"> 只看正解⭐</label>
          <label><input type="checkbox" id="examHideKnown" onchange="setExamFilter('hideKnown',this.checked)"> 隱藏已劃掉</label>
          <button class="mini" id="examPlayBtn" onclick="examPlayToggle()">🔊 聽讀</button>
          <button class="mini" onclick="examResetKnown()">清除標記</button>
        </div>
        <div style="font-size:11.5px;color:var(--muted);margin-top:6px;line-height:1.5">💡 <b>盤點模式</b>點卡＝直接劃掉；開<b>複習模式</b>後點卡＝<b>發音＋翻中文</b>、用角落 ✓ 劃掉。「🔊 聽讀」會自動念出目前不熟的字。</div>
      </div>
      <div class="exam-grid" id="examGrid"></div>
      <div class="exam-actions">
        <button class="exam-build" id="examBuildBtn" onclick="buildExamDeck('cards')"></button>
        <button class="exam-build alt" id="examQuizBtn" onclick="buildExamDeck('quiz')"></button>
      </div>
    </section>

  '''
EXAM_VIEW = EXAM_VIEW.replace('__EXAM_N__', str(exam_n))
h, n = re.subn(r'  <!-- ===== NAV ===== -->', EXAM_VIEW+'<!-- ===== NAV ===== -->', h, count=1)
assert n==1, "view-exam inject failed"

# 11h) CSS
EXAM_CSS = '''
.exam-entry{width:100%;margin-top:10px;background:var(--accent-soft);color:var(--accent-d);border:none;border-radius:14px;padding:12px 10px;font-size:14px;font-weight:800;cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:2px;line-height:1.3}
.exam-entry small{font-weight:600;color:var(--muted);font-size:10.5px}
#view-exam .exam-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(94px,1fr));gap:7px;padding:2px 12px 132px}
.exchip{position:relative;background:var(--card);border:1px solid var(--line);border-left:4px solid var(--line);border-radius:11px;padding:8px 5px 6px;cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:2px;font-weight:700;color:var(--text);transition:opacity .12s,background .12s;-webkit-tap-highlight-color:transparent}
.exchip .ew{font-size:12.5px;word-break:break-word;text-align:center;line-height:1.15}
.exchip .em{font-size:9px;color:var(--muted);font-weight:600}
.exchip.known{background:var(--bg);opacity:.5}
.exchip.known .ew{text-decoration:line-through}
.exchip.lv1{border-left-color:#7ed957}.exchip.lv2{border-left-color:#2eb872}.exchip.lv3{border-left-color:#4d8df6}.exchip.lv4{border-left-color:#5b6ee1}.exchip.lv5{border-left-color:#b06be1}.exchip.lv6{border-left-color:#e8504f}.exchip.lv0{border-left-color:#aaa}
.exchip .ez{font-size:10.5px;color:var(--accent-d);font-weight:700;text-align:center;line-height:1.2;margin-top:1px}
.exchip .exx{position:absolute;top:3px;right:4px;width:16px;height:16px;border:1.5px solid var(--line);border-radius:50%;font-size:10px;line-height:13px;text-align:center;color:var(--green);background:var(--card);font-weight:800}
.exchip .exx.on{background:var(--green);color:#fff;border-color:var(--green)}
.exchip.playing{outline:2px solid var(--accent-d);outline-offset:1px;background:var(--accent-soft)}
.exam-filters{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0 2px}
.exam-toggles{display:flex;flex-wrap:wrap;gap:12px;align-items:center;font-size:13px;color:var(--text);margin-top:8px}
.exam-toggles label{display:flex;align-items:center;gap:5px;cursor:pointer}
.exam-toggles .mini{margin-left:auto;background:none;border:1px solid var(--line);border-radius:8px;padding:4px 9px;font-size:12px;color:var(--muted);cursor:pointer}
.exam-actions{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(var(--nav-h) + env(safe-area-inset-bottom));width:min(480px,100vw);box-sizing:border-box;display:flex;gap:8px;padding:8px 12px;background:linear-gradient(transparent,var(--bg) 38%);z-index:5}
.exam-build{flex:1;background:var(--accent-d);color:#fff;border:none;border-radius:12px;padding:12px 8px;font-size:13px;font-weight:800;cursor:pointer}
.exam-build.alt{background:var(--card);color:var(--accent-d);border:2px solid var(--accent-d)}
</style>'''
h = h.replace('</style>', EXAM_CSS, 1)

# 11i) JS
EXAM_JS = r'''
let examRevealed=new Set();
let examPlaying=false, examQueue=[], examQi=0, _exwm=null;
function examWmap(){ if(!_exwm){ _exwm={}; WORDS.forEach(function(w){ const kk=w.word.toLowerCase(); if(!_exwm[kk]) _exwm[kk]=w; }); } return _exwm; }
function examZh(base){ const w=examWmap()[base]; return w?w.zh_tw:""; }
function exEsc(s){ return String(s).replace(/'/g,"\\'"); }
function examTap(w){ examRevealed.add(w); if(typeof speakText==="function") speakText(w); renderExamPanel(); }
function examKnownSet(){ if(!S.examKnown) S.examKnown={}; return S.examKnown; }
function examFilterState(){ if(!S.examFilter) S.examFilter={}; const d={year:"all",level:"all",onlyAns:false,hideKnown:false,review:false,showZh:false}; for(const kk in d){ if(S.examFilter[kk]===undefined) S.examFilter[kk]=d[kk]; } return S.examFilter; }
function setExamFilter(k,v){ examFilterState()[k]=v; save(); renderExamPanel(); }
function toggleExamKnown(w){ const k=examKnownSet(); if(k[w]) delete k[w]; else k[w]=1; save(); renderExamPanel(); }
function examResetKnown(){ if(confirm("確定清除所有『認識』標記？")){ S.examKnown={}; save(); renderExamPanel(); } }
function renderExamPanel(){
  const f=examFilterState(), k=examKnownSet();
  const years=[...new Set(EXAM_WORDS.reduce((a,e)=>a.concat(e.years),[]))].sort();
  document.getElementById("examYearChips").innerHTML=["all"].concat(years).map(function(y){return '<button class="chip '+(String(f.year)===String(y)?"on":"")+'" onclick="setExamFilter(\'year\',\''+y+'\')">'+(y==="all"?"全部年份":y+"學測")+'</button>';}).join("");
  document.getElementById("examLevelChips").innerHTML=["all",1,2,3,4,5,6].map(function(lv){return '<button class="chip '+(String(f.level)===String(lv)?"on":"")+'" onclick="setExamFilter(\'level\',\''+lv+'\')">'+(lv==="all"?"全部級別":"第"+lv+"級")+'</button>';}).join("");
  var _rv=document.getElementById("examReview"); if(_rv) _rv.checked=!!f.review;
  var _sz=document.getElementById("examShowZh"); if(_sz) _sz.checked=!!f.showZh;
  document.getElementById("examOnlyAns").checked=!!f.onlyAns;
  document.getElementById("examHideKnown").checked=!!f.hideKnown;
  let list=EXAM_WORDS.slice();
  if(f.year!=="all") list=list.filter(e=>e.years.indexOf(+f.year)>=0);
  if(f.level!=="all") list=list.filter(e=>String(e.level)===String(f.level));
  if(f.onlyAns) list=list.filter(e=>e.ans);
  if(f.hideKnown) list=list.filter(e=>!k[e.w]);
  list.sort((a,b)=>(a.level||9)-(b.level||9) || (b.freq||0)-(a.freq||0) || (a.w<b.w?-1:1));
  const total=EXAM_WORDS.length, known=EXAM_WORDS.filter(e=>k[e.w]).length;
  document.getElementById("examCount").innerHTML='共 <b>'+total+'</b> 字 ｜ 已劃掉 <b style="color:var(--green)">'+known+'</b> ｜ <b style="color:var(--accent-d)">不熟 '+(total-known)+'</b> ｜ 目前顯示 '+list.length;
  document.getElementById("examGrid").innerHTML=list.map(function(e){
    const kn=!!k[e.w];
    const yr=e.years.length>1?(e.years.length+"年"):("’"+String(e.years[0]).slice(-2));
    const wq=exEsc(e.w);
    const showzh=f.showZh || examRevealed.has(e.w);
    const zh=showzh?examZh(e.base):"";
    const play=(examPlaying&&examQueue[examQi]===e.w)?" playing":"";
    const ttl='出現年份：'+e.years.join("、")+"｜第"+e.level+"級｜全卷共"+(e.freq||1)+"次"+(e.ans?"｜詞彙題正解⭐":"");
    const body='<span class="ew">'+escapeHTML(e.w)+(e.ans?" ⭐":"")+'</span>'+(zh?'<span class="ez">'+escapeHTML(zh)+'</span>':'')+'<span class="em">'+yr+'</span>';
    if(f.review){
      return '<div id="exc-'+wq+'" class="exchip lv'+e.level+(kn?" known":"")+play+'" onclick="examTap(\''+wq+'\')" title="'+ttl+'"><span class="exx'+(kn?" on":"")+'" onclick="event.stopPropagation();toggleExamKnown(\''+wq+'\')">'+(kn?"✓":"")+'</span>'+body+'</div>';
    }
    return '<button id="exc-'+wq+'" class="exchip lv'+e.level+(kn?" known":"")+play+'" onclick="toggleExamKnown(\''+wq+'\')" title="'+ttl+'">'+body+'</button>';
  }).join("")||'<div style="grid-column:1/-1;padding:34px;text-align:center;color:var(--muted)">沒有符合的字 🙂</div>';
  const remain=EXAM_WORDS.filter(e=>!k[e.w]);
  const deckable=[...new Set(remain.map(e=>e.base).filter(Boolean))].length;
  document.getElementById("examBuildBtn").innerHTML='🃏 背不熟的 '+deckable+' 字';
  document.getElementById("examQuizBtn").innerHTML='📝 測不熟的 '+deckable+' 字';
}
function examVisibleUnknown(){
  const f=examFilterState(), k=examKnownSet();
  let list=EXAM_WORDS.slice();
  if(f.year!=="all") list=list.filter(e=>e.years.indexOf(+f.year)>=0);
  if(f.level!=="all") list=list.filter(e=>String(e.level)===String(f.level));
  if(f.onlyAns) list=list.filter(e=>e.ans);
  list=list.filter(e=>!k[e.w]);
  list.sort((a,b)=>(a.level||9)-(b.level||9) || (b.freq||0)-(a.freq||0) || (a.w<b.w?-1:1));
  return list.map(e=>e.w);
}
function examSpeakThen(t,cb){ try{ speechSynthesis.cancel(); const u=new SpeechSynthesisUtterance(t); u.lang="en-US"; u.rate=0.9; u.onend=cb; u.onerror=cb; if(S.settings.sound!==false) speechSynthesis.speak(u); else setTimeout(cb,500); }catch(e){ setTimeout(cb,300); } }
function examPlayToggle(){
  const b=document.getElementById("examPlayBtn");
  if(examPlaying){ examPlaying=false; try{speechSynthesis.cancel();}catch(e){} if(b) b.textContent="🔊 聽讀"; renderExamPanel(); return; }
  examQueue=examVisibleUnknown();
  if(!examQueue.length){ toast("目前沒有不熟的字可聽讀 🙂"); return; }
  examPlaying=true; examQi=0; if(b) b.textContent="⏹ 停止聽讀";
  examPlayStep();
}
function examPlayStep(){
  if(!examPlaying) return;
  const b=document.getElementById("examPlayBtn");
  if(examQi>=examQueue.length){ examPlaying=false; if(b) b.textContent="🔊 聽讀"; toast("聽讀完成 🎉"); renderExamPanel(); return; }
  const w=examQueue[examQi];
  examRevealed.add(w);
  renderExamPanel();
  const el=document.getElementById("exc-"+w); if(el&&el.scrollIntoView){ try{ el.scrollIntoView({block:"center",behavior:"smooth"}); }catch(e){} }
  examSpeakThen(w, function(){ if(!examPlaying) return; setTimeout(function(){ examQi++; examPlayStep(); }, 650); });
}
function buildExamDeck(target){
  const k=examKnownSet();
  const set=[...new Set(EXAM_WORDS.filter(e=>!k[e.w]).map(e=>e.base).filter(Boolean))];
  if(!set.length){ toast("沒有不熟的字了 🎉 全都劃掉了"); return; }
  if(examPlaying){ examPlaying=false; try{speechSynthesis.cancel();}catch(e){} }
  S.deck.custom=set; S.deck.topic="all"; S.deck.unit="all";
  if(target==="quiz"){
    S.settings.quizUnit="all"; if(typeof clearQuizSave==="function") clearQuizSave(); save();
    go("quiz"); if(typeof switchQuiz==="function") switchQuiz();
    toast("已用 "+set.length+" 個不熟字出題");
  } else {
    S.settings.autoSpeak=true; if(S.settings.sound===false) S.settings.sound=true; save();
    go("cards"); startStudy("free", false);
    toast("開始背 "+set.length+" 個不熟字（翻卡自動發音）");
  }
}
'''
h = h.replace('function updateDeckPreview(){ document.getElementById("deckPreview").textContent=WORDS.filter(inDeck).length; }',
              'function updateDeckPreview(){ document.getElementById("deckPreview").textContent=WORDS.filter(inDeck).length; }'+EXAM_JS, 1)

OUT = OUTDIR/'index.html'
OUT.write_text(h, encoding='utf-8')
print(f"wrote {OUT}  ({len(h):,} bytes)  units={NUNITS}  levels={dict(sorted(LC.items()))}")

# ---- build 後必須重跑注入器 ----
# 1) 模板是 02_國中2000/index.html，會夾帶「2000 的家長後台 App 代號」→ 必須 --reinject 蓋成本 App 的代號
# 2) K28 四大功能(鎖導覽/固定50題/綜合測驗/錯題分類)雖隨模板帶入，仍跑一次確保完整
import subprocess as _sp, sys as _sys
_ROOT = OUTDIR.parent   # 英語單字APP/
for _script, _args in ((_ROOT/'_k28_inject.py', []), (_ROOT/'_parentsync_inject.py', ['--reinject'])):
    if _script.exists():
        _r = _sp.run([_sys.executable, str(_script)] + _args, cwd=str(_ROOT))
        print(f"  re-inject {_script.name}: exit {_r.returncode}")
    else:
        print(f"  ⚠️ 找不到 {_script.name} → index.html 會缺少四大功能/家長後台回報！")

PY_END = True
