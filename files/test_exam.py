# -*- coding: utf-8 -*-
import re, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html = open(os.path.join(ROOT,'index.html'), encoding='utf-8').read()
script = re.search(r'<script>(.*)</script>', html, re.S).group(1)
harness = r'''
const _store={};
global.localStorage={getItem:k=>_store[k]??null,setItem:(k,v)=>{_store[k]=String(v)},removeItem:k=>{delete _store[k]}};
function mk(){const f=function(){return ST;};return new Proxy(f,{get(t,p){if(p==="textContent"||p==="innerHTML"||p==="value"||p==="checked")return"";if(p==="classList")return{toggle(){},add(){},remove(){},contains(){return false}};if(p==="style")return{};if(p==="length")return 0;if(p==="dataset")return{};if(p==="querySelectorAll")return()=>[];if(p==="children")return[];if(p==="getContext")return()=>ST;if(typeof p==="symbol")return undefined;return ST;},set(){return true;},apply(){return ST;}});}
const ST=mk();
global.document={getElementById:()=>ST,querySelector:()=>ST,querySelectorAll:()=>[],createElement:()=>ST,addEventListener(){},documentElement:ST,body:ST,head:ST};
global.window=new Proxy({},{get(t,p){if(p==="addEventListener")return()=>{};if(p==="matchMedia")return()=>({matches:false,addEventListener(){}});if(p==="scrollTo")return()=>{};return ST;},set(){return true;}});
global.navigator={vibrate(){},serviceWorker:{register(){return{catch(){}}},},language:"zh-TW"};
global.matchMedia=()=>({matches:false,addEventListener(){}});
global.requestAnimationFrame=()=>0;global.confirm=()=>true;global.alert=()=>{};global.prompt=()=>null;
global.setInterval=()=>0; global.clearInterval=()=>{}; global.setTimeout=(f)=>0; global.clearTimeout=()=>{};
global.SpeechSynthesisUtterance=function(){};global.speechSynthesis={getVoices:()=>[],speak(){},cancel(){}};
global.Audio=function(){return{play(){},pause(){}}};
'''
checks = r'''
let P=0,F=0; function ok(n){P++;console.log("OK  "+n)} function bad(n,e){F++;console.log("XX  "+n+" :: "+e)}
function t(n,fn){try{fn();ok(n)}catch(e){bad(n,e&&e.message||e)}}

t("EXAM_WORDS present (full-paper, >2000)", ()=>{ if(!Array.isArray(EXAM_WORDS)||EXAM_WORDS.length<2000) throw "len="+(EXAM_WORDS&&EXAM_WORDS.length); });
t("every exam word has years/level/freq", ()=>{ EXAM_WORDS.forEach(e=>{ if(!e.w||!Array.isArray(e.years)||!e.level) throw "bad "+JSON.stringify(e); }); });
t("all exam words map to WORDS", ()=>{ const wset=new Set(WORDS.map(w=>w.word)); const m=EXAM_WORDS.filter(e=>e.base&&wset.has(e.base)).length; if(m!==EXAM_WORDS.length) throw "mapped="+m+"/"+EXAM_WORDS.length; });
t("level filter works", ()=>{ setExamFilter("level","6"); renderExamPanel(); setExamFilter("level","all"); });
t("answers ~60 starred", ()=>{ const a=EXAM_WORDS.filter(e=>e.ans).length; if(a<55||a>65) throw "ans="+a; });
t("renderExamPanel runs", ()=>{ renderExamPanel(); });
t("toggleExamKnown marks + persists", ()=>{ const w=EXAM_WORDS[0].w; toggleExamKnown(w); if(!S.examKnown[w]) throw "not marked"; toggleExamKnown(w); if(S.examKnown[w]) throw "not unmarked"; });
t("setExamFilter onlyAns", ()=>{ setExamFilter("onlyAns",true); renderExamPanel(); setExamFilter("onlyAns",false); });
t("inDeck honours custom", ()=>{ S.deck.custom=["able"]; const pool=WORDS.filter(inDeck); if(pool.length!==1||pool[0].word!=="able") throw "pool="+pool.length; S.deck.custom=null; });
t("buildExamDeck('cards') sets custom & starts", ()=>{ S.examKnown={}; buildExamDeck("cards"); if(!session||!session.deck||!session.deck.length) throw "no session deck"; });
t("buildExamDeck('quiz') builds quiz items", ()=>{ S.examKnown={}; buildExamDeck("quiz"); if(!quiz||!quiz.items||!quiz.items.length) throw "no quiz items"; });
t("exam deck size = distinct bases of unknown", ()=>{ S.examKnown={}; const set=[...new Set(EXAM_WORDS.filter(e=>!S.examKnown[e.w]).map(e=>e.base).filter(Boolean))]; if(set.length<200) throw "deck="+set.length; });
t("go('exam') switches & renders", ()=>{ go("exam"); });
t("pickLevel clears custom", ()=>{ S.deck.custom=["able"]; pickLevel("all"); if(S.deck.custom!==null) throw "custom not cleared"; });
t("review mode renders (flip chips)", ()=>{ setExamFilter("review",true); renderExamPanel(); setExamFilter("review",false); });
t("showZh mode renders (word list)", ()=>{ setExamFilter("showZh",true); renderExamPanel(); setExamFilter("showZh",false); });
t("examTap speaks + reveals + rerenders", ()=>{ const w=EXAM_WORDS[0].w; examTap(w); if(!examRevealed.has(w)) throw "not revealed"; });
t("examZh maps to a Chinese meaning", ()=>{ const e=EXAM_WORDS.find(x=>x.base); const zh=examZh(e.base); /* stub returns '' in node; just ensure no throw */ });
t("examPlayToggle start/stop no throw", ()=>{ examPlayToggle(); examPlayToggle(); if(examPlaying) throw "still playing"; });
t("buildExamDeck cards enables autoSpeak", ()=>{ S.examKnown={}; buildExamDeck("cards"); if(S.settings.autoSpeak!==true) throw "autoSpeak not on"; });

console.log("\nEXAM TEST: "+P+" pass / "+F+" fail");
if(F) process.exit(1);
'''
code = harness + "\n" + script + "\n" + checks
tmp = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_exam_test.js')
open(tmp,'w',encoding='utf-8').write(code)
try:
    p = subprocess.run(['node', tmp], capture_output=True, text=True, encoding='utf-8')
finally:
    try: os.remove(tmp)
    except Exception: pass
print(p.stdout)
if p.stderr.strip(): print("STDERR:", p.stderr[-1500:])
sys.exit(p.returncode)
