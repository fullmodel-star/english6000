# 對 index.html 做煙霧測試：抽出 <script>，用 DOM stub 跑遍主要流程，抓被誤刪/未定義的函式。
# 用法： python files/smoke_test.py
import re, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html = open(os.path.join(ROOT,'index.html'), encoding='utf-8').read()
script = re.search(r'<script>(.*)</script>', html, re.S).group(1)

harness = r'''
const _store={};
global.localStorage={getItem:k=>_store[k]??null,setItem:(k,v)=>{_store[k]=String(v)},removeItem:k=>{delete _store[k]}};
function mk(){const f=function(){return ST;};return new Proxy(f,{get(t,p){if(p==="textContent"||p==="innerHTML"||p==="value")return"";if(p==="classList")return{toggle(){},add(){},remove(){},contains(){return false}};if(p==="style")return{};if(p==="length")return 0;if(p==="dataset")return{};if(p==="querySelectorAll")return()=>[];if(p==="children")return[];if(p==="getContext")return()=>ST;if(typeof p==="symbol")return undefined;return ST;},set(){return true;},apply(){return ST;}});}
const ST=mk();
global.document={getElementById:()=>ST,querySelector:()=>ST,querySelectorAll:()=>[],createElement:()=>ST,addEventListener(){},documentElement:ST,body:ST,head:ST};
global.window=new Proxy({},{get(t,p){if(p==="addEventListener")return()=>{};if(p==="matchMedia")return()=>({matches:false,addEventListener(){}});if(p==="scrollTo")return()=>{};return ST;},set(){return true;}});
global.navigator={vibrate(){},serviceWorker:{register(){return{catch(){}}}},language:"zh-TW"};
global.matchMedia=()=>({matches:false,addEventListener(){}});
global.requestAnimationFrame=()=>0;global.confirm=()=>true;global.alert=()=>{};global.prompt=()=>null;
global.setInterval=()=>0; global.clearInterval=()=>{}; global.setTimeout=(f)=>0; global.clearTimeout=()=>{};
global.SpeechSynthesisUtterance=function(){};global.speechSynthesis={getVoices:()=>[],speak(){},cancel(){}};
global.Audio=function(){return{play(){},pause(){}}};
'''
footer = r'''
const out=[];
function T(name,fn){ try{ fn(); out.push("OK  "+name); }catch(e){ out.push("XX  "+name+" -> "+e.message); } }
T("applyTheme",()=>applyTheme());
T("setupGestures",()=>typeof setupGestures==="function"&&setupGestures());
T("renderHome",()=>renderHome());
T("go(cards)",()=>go("cards"));
T("go(quiz)",()=>go("quiz"));
T("go(stats)",()=>go("stats"));
T("go(home)",()=>go("home"));
T("openDeckPicker",()=>openDeckPicker());
T("pickUnit",()=>pickUnit(3));
T("pickLevel",()=>pickLevel(1));
T("pickTopic",()=>pickTopic("all"));
T("applyDeck",()=>applyDeck());
T("startToday",()=>typeof startToday==="function"&&startToday());
T("startStudy(review)",()=>startStudy("review",false));
T("rate(ok)",()=>{ session={deck:[WORDS[0]],i:0,mode:"free",correct:0}; flipped=true; rate("ok"); });
T("rate(no)",()=>{ session={deck:[WORDS[1]],i:0,mode:"free",correct:0}; flipped=true; rate("no"); });
T("switchQuiz",()=>switchQuiz("vocab"));
T("answerOne",()=>{ quiz={kind:"vocab",items:genVocabQuiz(5),i:0,score:0,answered:false,wrongItems:[]}; answerOne(0); });
T("buildDeck(wrong)",()=>buildDeck("wrong"));
T("startStudy(wrong)",()=>startStudy("wrong",false));
T("openSettings",()=>openSettings());
T("renderStats",()=>renderStats());
T("checkBadges",()=>typeof checkBadges==="function"&&checkBadges());
const fail=out.filter(x=>x.startsWith("XX"));
console.log(out.join("\n"));
console.log("\n總結: "+out.filter(x=>x.startsWith("OK")).length+" 通過 / "+fail.length+" 失敗");
if(fail.length) process.exit(1);
'''
tmp = os.path.join(ROOT,'_smoke_run.js')
open(tmp,'w',encoding='utf-8').write(harness+script+footer)
try:
    r = subprocess.run(['node', tmp], capture_output=True, text=True, encoding='utf-8')
    print(r.stdout);
    if r.stderr: print('STDERR:', r.stderr[:500])
    sys.exit(r.returncode)
finally:
    os.remove(tmp)
