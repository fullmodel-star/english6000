/* 還原 App 自己的 confetti；canvas-confetti 改叫 window.__lvCC */
(function(){ var cc = window.confetti; if (typeof cc === 'function' && cc.create){ window.__lvCC = cc; if (typeof window.__lvAppConfetti === 'function') window.confetti = window.__lvAppConfetti; } })();

/* 活潑層 engine：cap（905 國中會考複習）——由 sync_lively.py 串接在 lively.js 前面
   - 練習引擎 practice.js 包在 IIFE 裡（pick／finish 都不在 window），wrap 接不到 → 用 observe。
   - 單題作答（pick→lockUI、總複習 rvPick、錯題複習 rvWrongPick）都是在既有選項上 classList.add('ok'／'no')，
     MutationObserver 抓得到。答錯時正解也會被加上 .ok，所以「答對」要再看同一張題卡的回饋是 .fb.good
     （回饋框在同一段同步程式裡設定，觀察者回呼時已就位）。
   - 閱讀題組（pickG／revealG→renderGroup）每次整段 innerHTML 重畫，新選項一出生就帶 .ok／.no，
     核心的 attributes 監聽抓不到 → 改用 observe.added 接新出現的回饋框。 */
window.__LV_ENGINES = window.__LV_ENGINES || {};
window.__LV_ENGINES.cap = {
  observe: { correct: ".qcard:has(.fb.good) .opt.ok", wrong: ".qcard .opt.no",
             /* 閱讀題組整段重畫：新出現的回饋框（核心 2026-10-03 起支援 added，只在剛點過畫面時算、同批合併成一次） */
             added: { correct: ".qcard .fb.show.good", wrong: ".qcard .fb.show.bad" } },
  installBar: "#installBar"   /* App 自己的安裝列有東西時，藏起家族浮動安裝鈕，避免兩顆安裝鈕 */
};

/* 活潑層 engine 設定：conv（909 旅遊／910 家庭／911 校園／912 跑腿／913 社交 生活會話家族，909 母版換皮）
   來源：packages/lively/engines/conv.js（sync 時串接在 lively.js 前面；每支 App 都會載入本檔，
   所以本檔只登記設定，任何會動到頁面的程式都要先確認 --lv-engine＝conv 才執行）。
   答對／答錯用 observe（不碰 App 程式）：
     選擇題（聽力／中翻英／聽數字，pickOpt）：點對＝該選項加 .ok；點錯＝該選項加 .no，同時把正解也標 .ok
       → 答對選擇器排除「同組已有 .no」的情況，免得把「答錯後揭示正解」算成答對。
     拼句（sczCheck）：#sczT 加 .ok／.err。兒童圖卡遊戲（kidPick）：.kgopt 加 .kgok／.kgbad。
   level=low：彩帶只在完成時 → finishKidGame（貼紙到手）＋「一般練習 ≥70%」或「總複習過關（≥F_PASS）」。 */
window.__LV_ENGINES = window.__LV_ENGINES || {};
(function(){
  "use strict";
  window.__LV_ENGINES.conv = {
    observe: {
      correct: "#opts:not(:has(.opt.no)) > .opt.ok, #sczT.ok, .kgopt.kgok",
      wrong: "#opts > .opt.no, #sczT.err, .kgopt.kgbad"
    },
    /* 圖示：底部選單／橫幅／模式格的 emoji 大多（🆘🔎👤✈️🛡️🎧🧩🎤…）不在 vendor/fluent-emoji 清單裡，
       只換一半會變成兩種畫風並排，所以先不換（icons 留空＝核心不動 emoji）。 */
    icons: ".nav button > .ni, .banner .big, .mode .mi",   /* 2026-10-03 核心補齊 🆘🔎👤✈️🛡️🎧🧩🎤🔑🎭 等 Fluent 圖示 */
    afterRender: ["renderHome"],
    celebrateFns: ["finishKidGame", "__lvConvPassed"]
  };

  var isConv = false;
  try{ isConv = getComputedStyle(document.documentElement).getPropertyValue("--lv-engine").trim() === "conv"; }catch(e){}
  if (!isConv) return;

  /* 1.（已移到核心）App 自己的全域 confetti()（emoji 飄落）由 sync 注入的兩行保存／還原，canvas-confetti 改叫 window.__lvCC。 */

  /* 2. 過關才放彩帶：核心會把 window.__lvConvPassed 包成「呼叫就大彩帶」。 */
  window.__lvConvPassed = window.__lvConvPassed || function(){};
  try{
    var fs = window.finishSession;
    if (typeof fs === "function" && !fs.__lvConv){
      var w = function(){
        var pass = false;
        try{
          var t = Q.items.length, pct = t ? Math.round(Q.correct / t * 100) : 0;
          pass = Q.final ? pct >= F_PASS : pct >= 70;
        }catch(e){}
        var r = fs.apply(this, arguments);
        if (pass){ try{ window.__lvConvPassed(); }catch(e){} }
        return r;
      };
      w.__lvConv = true; window.finishSession = w;
    }
  }catch(e){}

  /* 3. 手機狀態列顏色跟著頁首淡主色（App 的 applyDark 寫死草綠 #E9F3E0／深藍） */
  function syncThemeColor(){
    try{
      var m = document.querySelector('meta[name="theme-color"]');
      var v = getComputedStyle(document.documentElement).getPropertyValue("--lv-soft").trim();
      if (m && v) m.content = v;
    }catch(e){}
  }
  try{
    var ad = window.applyDark;
    if (typeof ad === "function" && !ad.__lvConv){
      var wd = function(){ var r = ad.apply(this, arguments); syncThemeColor(); return r; };
      wd.__lvConv = true; window.applyDark = wd;
    }
  }catch(e){}
  syncThemeColor();
})();

/* 活潑層 engine：gsat（906 學測複習）——由 sync_lively.py 串接在 lively.js 前面
   - 單題作答（pick→lockUI、總複習 rvPick、錯題複習 rvWrongPick）都是在既有選項上 classList.add('ok'／'no') → observe。
     答錯時正解也會被加上 .ok，所以「答對」要再看同一張題卡的回饋是 .fb.good。
   - pick(k) 的參數是選項字母（永遠為真），不能用核心的 wrap.juice（它把第一個參數當對錯）。
   - 單元總結 finish() 是全域函式 → wrap.result＋resultPct：答對 ≥80% 才放過關彩帶。
   - 閱讀題組（pickG／revealG→renderGroup）每次整段重畫，attributes 監聽抓不到 → 改用 observe.added。 */
window.__LV_ENGINES = window.__LV_ENGINES || {};
window.__LV_ENGINES.gsat = {
  observe: { correct: ".qcard:has(.fb.good) .opt.ok", wrong: ".qcard .opt.no",
             /* 閱讀題組整段重畫：新出現的回饋框（核心 2026-10-03 起支援 added，只在剛點過畫面時算、同批合併成一次） */
             added: { correct: ".qcard .fb.show.good", wrong: ".qcard .fb.show.bad" } },
  installBar: "#installBar",
  wrap: { result: "finish" },
  resultPct: function(){
    try{
      /* Q／answers 是 906 主程式的頂層 let，跨 script 可直接取用 */
      var n = 0; Q.forEach(function(q, i){ if (answers[i] === q.answer) n++; });
      return Q.length ? n / Q.length : 0;
    }catch(e){ return 0; }
  }
};

/* 活潑層 engine 設定：hub（922 對外作品集入口：入口卡片、儀表板、備份還原、搜尋；沒有作答）
   來源：packages/lively/engines/hub.js（sync 時串接在 lively.js 前面）
   922 的 emoji 都和文字寫在同一個元素裡（「📊 我的學習儀表板」「📖 已學單字」），
   核心 swapEmoji 只換「整個元素就是一個 emoji」的容器 → 目前沒有可換的；App 卡片的 .ic 是品牌層，不動。
   afterRender 先接上 render／renderDash：之後若加了純 emoji 容器，改 icons 選擇器即可。 */
window.__LV_ENGINES = window.__LV_ENGINES || {};
window.__LV_ENGINES.hub = {
  icons: ".dash .lv-hub-ico",
  installBar: "#installBar",
  afterRender: ["render", "renderDash"]
};

/* 活潑層 engine 設定：pinju（903 英語拼句）
   來源：packages/lively/engines/pinju.js（sync 時串接在 lively.js 前面）

   903 的 check() 判完對錯只改「同一個」#sheet 的 class（sheet ok show／sheet no show），
   而核心 observe 用 WeakSet 記住觸發過的元素 → 只有第一題會觸發。
   在不改核心的前提下：包住 check()，每次作答把 #sheetHd 的內容包進一個「新的」標記 span，
   掛上 DOM 之後才加 lv-pj-ok／lv-pj-no → 核心 observe 每題都看得到（彈跳／搖晃也就落在面板標題上）。
   靠提示拼對的不算答對（App 自己也不計正確率），不觸發也不中斷連對。
   核心若之後支援「可重複觸發的 observe」或「wrap 一個沒有參數的判題函式＋讀結果」，這段可以拿掉。 */
(function(){
  function mark(ok){
    var hd = document.getElementById("sheetHd"); if (!hd) return;
    var s = document.createElement("span"); s.className = "lv-pj-mark";
    while (hd.firstChild) s.appendChild(hd.firstChild);
    hd.appendChild(s);
    s.className = "lv-pj-mark " + (ok ? "lv-pj-ok" : "lv-pj-no");   // 掛上去之後才改 class，observe 才收得到
  }
  function hook(){
    // 這個檔會串進「每一支」App 的 lively.js：只在 engine＝pinju 且有拼句結果面板時才動手
    var eng = ""; try{ eng = getComputedStyle(document.documentElement).getPropertyValue("--lv-engine").trim(); }catch(e){}
    if (eng !== "pinju" || !document.getElementById("sheetHd")) return;
    if (typeof window.check !== "function" || window.check.__lvpj) return;
    var orig = window.check;
    var w = function(){
      var r = orig.apply(this, arguments);
      try{
        var sh = document.getElementById("sheet");
        if (sh && sh.classList.contains("show")){
          var hinted = false; try{ hinted = !!qHinted; }catch(e){}
          if (sh.classList.contains("ok")){ if (!hinted) mark(true); }
          else if (sh.classList.contains("no")) mark(false);
        }
      }catch(e){}
      return r;
    };
    w.__lvpj = true; window.check = w;
  }
  try{ hook(); }catch(e){}
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", function(){ try{ hook(); }catch(e){} });
})();

window.__LV_ENGINES = window.__LV_ENGINES || {};
window.__LV_ENGINES.pinju = {
  observe: { correct: "#sheetHd .lv-pj-ok", wrong: "#sheetHd .lv-pj-no" },
  /* 903 的 emoji（🧩📕🧒💬…）大多不在核心 Fluent 對照表，換一半會混搭 → 不換圖示。
     icons 仍要給一個值：核心 decorate() 在 icons 空的時候會連 flame 一起跳過。 */
  icons: "#learn .lv-pj-ico",
  flame: ".hero .stats .st b",            // 首頁「🔥 連續天數」的火焰換成會晃的 Fluent 火焰
  installBar: "#installBar",
  afterRender: ["renderLearn"],
  celebrateFns: ["finish"]                 // 單元／複習完成 → 大彩帶（複習就該被獎勵）
};

/* 活潑層 engine：qbank（915 會考／916 學測 官方題庫引擎，同一套程式）
   來源：packages/lively/engines/qbank.js（sync_lively.py 串接在 lively.js 前面）

   為什麼不直接 observe「.opt.correct／.opt.wrong」：
   - 作答（pick）後 drawRun 用 innerHTML 整頁重畫，新選項一出生就帶 class → 不會有 class 變動事件；
   - 閱讀題組 revealGroup、整卷交卷會一次把好幾題標上對錯 → 一次撒好幾次彩帶；
   - 總複習／嚴格錯題本（rvLock）答錯時也會把「正解」標 .ok → 答錯會被當成答對。
   所以這裡包住 App 的作答函式，只在「這一次作答」的那一個選項加上 lv-ans-ok／lv-ans-no，
   核心的 observe 只看這兩個記號。包裝自己出錯一律吞掉，App 原本流程不受影響。 */
window.__LV_ENGINES = window.__LV_ENGINES || {};
(function(){
  "use strict";
  /* 所有 engines/*.js 都會串進每一支 App 的 lively.js → 只有 engine=qbank 的 App 才包函式 */
  var ENG = ""; try{ ENG = getComputedStyle(document.documentElement).getPropertyValue("--lv-engine").trim(); }catch(e){}
  window.__LV_ENGINES.qbank = {
    observe: { correct: ".lv-ans-ok", wrong: ".lv-ans-no" },
    icons: ".nav button > .ni, #v-home .mode .mi, #v-diagnose .mode .mi",
    afterRender: ["renderHome", "renderDiagnose", "renderWrong", "renderFav", "renderSettings"],
    celebrateFns: ["__lvQbankCheer"]
  };
  if (ENG !== "qbank") return;

  function mark(el, ok){ if (el && el.classList) el.classList.add(ok ? "lv-ans-ok" : "lv-ans-no"); }
  function wrap(name, before, after){
    var o = window[name];
    if (typeof o !== "function" || o.__lvq) return;
    var w = function(){
      var pre = null;
      try{ pre = before ? before.apply(this, arguments) : null; }catch(e){}
      var r = o.apply(this, arguments);
      try{ after.call(this, arguments, pre); }catch(e){}
      return r;
    };
    w.__lvq = true; window[name] = w;
  }
  function cheer(){ try{ if (typeof window.__lvQbankCheer === "function") window.__lvQbankCheer(); }catch(e){} }
  /* 核心用 celebrateFns 包這個空函式：呼叫它＝放大彩帶（簡潔／減少動態時核心自己會略過） */
  window.__lvQbankCheer = function(){};

  /* 單題作答（題型專練／聽力／每日一練／錯題／收藏）；整卷模擬（exam）作答當下不揭曉，不觸發 */
  wrap("pick", function(){
    /* sess 是 App 的全域 let，跨 script 可直接讀 */
    var q = sess.list[sess.i];
    return { fresh: sess.mode !== "exam" && sess.picks[q.id] == null };
  }, function(a, pre){
    if (!pre || !pre.fresh) return;
    var k = a[0], hit = null;
    document.querySelectorAll("#v-run .opts .opt").forEach(function(b){
      var kk = b.querySelector(".k"); if (kk && kk.textContent === k) hit = b;
    });
    if (hit) mark(hit, hit.classList.contains("correct"));
  });

  /* 閱讀題組「對答案」：一次揭曉整篇 → 只回饋一次（有錯＝第一個選錯的搖一下；全對＝本篇結果彈跳） */
  wrap("revealGroup", function(){
    var g = groupRange(sess.i), pk = sess.list[g[0]].pkey;
    return { fresh: !(sess.revealed && sess.revealed.has(pk)) };
  }, function(a, pre){
    if (!pre || !pre.fresh) return;
    var no = document.querySelector("#v-run .opt.wrong");
    if (no) mark(no, false); else mark(document.querySelector("#v-run > .fb.ok"), true);
  });

  /* 總複習／嚴格錯題本：rvLock 會把正解標 .ok、選錯標 .no */
  function rvAfter(box){
    return function(a, pre){
      if (!pre || !pre.fresh) return;
      var no = document.querySelector(box + " .opt.no");
      if (no) mark(no, false); else mark(document.querySelector(box + " .opt.ok"), true);
    };
  }
  wrap("rvPick", function(){ return { fresh: window.rvPk == null }; }, rvAfter("#rvopts"));
  wrap("rvWrongPick", function(){ return { fresh: window.rwPk == null }; }, rvAfter("#rwopts"));

  /* 結果頁：答對率 ≥ 80% 才放大彩帶 */
  wrap("finish", null, function(){
    var s = document.querySelector("#v-result .result .score");
    var n = s ? parseFloat(s.textContent) : 0;
    if (n >= 80 && !document.querySelector("#v-result.hidden")) setTimeout(cheer, 250);
  });
  wrap("rvFinishReview", null, function(){
    var s = document.querySelector("#v-result .scorebig");
    if (s && parseFloat(s.textContent) >= 80) setTimeout(cheer, 250);
  });

  /* 家族「📝 我的複習」重考錯題（REVIEWUI 面板）：點完選項後才有 .ok／.no */
  document.addEventListener("click", function(e){
    try{
      var el = e.target && e.target.closest && e.target.closest(".rvc-opt"); if (!el) return;
      var item = el.closest(".rvc-item"); if (!item || item.__lvq) return;
      if (!el.classList.contains("ok") && !el.classList.contains("no")) return;
      item.__lvq = true; mark(el, el.classList.contains("ok"));
    }catch(err){}
  });
})();

/* =====================================================================
   活潑層 lively.js v1.0（2026-10-03，英語對外家族共用）
   來源：packages/lively/lively.js（由 sync_lively.py 複製進各 App，請改來源再重跑）
   - 讀 lively-theme.css 的 --lv-engine／--lv-level 決定怎麼接、多熱鬧。
   - 接法兩種：
       wrap    包在 App 既有函式外面（先跑原函式，自己出錯只吞掉）
       observe 看畫面上的選項有沒有被標成答對／答錯（不碰 App 程式）
   - 強度：full＝每題答對小彩帶、連對 3/5/10…提示；mid＝答對只彈跳、連對 5/10 提示、10 連對與過關才彩帶；
           low＝答對只彈跳、連對 10 提示、過關才彩帶。
   - 「簡潔模式」或系統「減少動態效果」：不放彩帶、不跳字。
   ===================================================================== */
(function(){
  "use strict";
  var ICON_DIR = "vendor/fluent-emoji/";
  var reduceMQ = window.matchMedia ? matchMedia("(prefers-reduced-motion: reduce)") : null;
  function cssVar(n){ try{ return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }catch(e){ return ""; } }
  var ENGINE = "", LEVEL = "full";

  /* ---------- 各群設定 ---------- */
  var ENGINES = {
    /* 901／902／904／907／908／919：單字引擎（同一套程式） */
    vocab: {
      wrap: { juice: "quizJuice", celebrate: "celebrate", result: "renderQuizResult", home: "renderHome", go: "go" },
      correctEl: "#optList .opt.correct, #spellInput", wrongEl: "#optList .opt.wrong, #spellInput",
      icons: ".tiles .tile .ico, .quick-actions button > span, .nav button > .ni",
      flame: "#streakRow", hero: true, installBar: "#installBar",
      bump: ["pomoToday","masteredCount","dueCount","goalNum","streakHome"],
      minimal: function(){ try{ return !!(S.settings && S.settings.minimal); }catch(e){ return false; } },
      resultPct: function(){ try{ var t = quiz.kind==="reading" ? quiz.items.reduce(function(a,q){return a+q.questions.length;},0) : quiz.items.length; return t ? quiz.score/t : 0; }catch(e){ return 0; } },
      fresh: function(){ try{ return !S.srs || Object.keys(S.srs).length === 0; }catch(e){ return false; } },
      start: function(){ try{ startToday(); }catch(e){} },
      heroText: { h: "第一步：認識今天的新單字", p: "每天一點點，單字就會變成你的！", steps: ["① 看單字","② 翻卡片","③ 記住它"] }
    }
  };
  /* 其他群組的設定在 engines/<engine>.js（sync 時串接在本檔前面，掛在 window.__LV_ENGINES） */
  if (window.__LV_ENGINES) for (var k in window.__LV_ENGINES) ENGINES[k] = window.__LV_ENGINES[k];

  function E(){ return ENGINES[ENGINE] || {}; }
  function quiet(){
    if (reduceMQ && reduceMQ.matches) return true;
    try{ return !!(E().minimal && E().minimal()); }catch(e){ return false; }
  }
  function icon(name, cls){
    var img = document.createElement("img");
    img.src = ICON_DIR + name + "_flat.svg"; img.alt = ""; img.className = cls || "lv-ico";
    img.setAttribute("aria-hidden","true"); img.decoding = "async";
    return img;
  }

  /* ---------- 彩帶（沒載入就安靜略過） ---------- */
  var fire = null;
  function getFire(){
    if (fire) return fire;
    // canvas-confetti 載入後存成 __lvCC，window.confetti 還給 App 自己的同名函式（會話群有 emoji 飄落的 confetti()）
    var cc = window.__lvCC || window.confetti;
    if (typeof cc !== "function" || !cc.create) return null;
    var cv = document.createElement("canvas"); cv.id = "lvConfetti"; cv.setAttribute("aria-hidden","true");
    document.body.appendChild(cv);
    fire = cc.create(cv,{ resize:true, useWorker:false, disableForReducedMotion:true }); // CSP 沒開 blob worker
    return fire;
  }
  function colors(){ var c = cssVar("--lv-btn") || "#30C077"; return [c, "#ffc93c", "#ff8a65", "#7aa7ff", "#c58af9"]; }
  function burstAt(el, big){
    if (quiet()) return; var f = getFire(); if (!f) return;
    var x = .5, y = .55;
    if (el && el.getBoundingClientRect){ var r = el.getBoundingClientRect(); if (r.width){ x = (r.left + r.width/2) / innerWidth; y = (r.top + r.height/2) / innerHeight; } }
    f({ particleCount: big?70:22, spread: big?90:58, startVelocity: big?38:24, scalar: big?.95:.75, ticks: big?160:90, gravity:1.1, origin:{x:x,y:y}, colors: colors() });
  }
  function bigCelebrate(){
    if (quiet()) return; var f = getFire(); if (!f) return;
    f({ particleCount: 80, angle: 60, spread: 70, origin:{x:0,y:.75}, colors: colors() });
    f({ particleCount: 80, angle: 120, spread: 70, origin:{x:1,y:.75}, colors: colors() });
  }
  function replay(el, cls){
    if (!el || !el.classList) return; el.classList.remove(cls); void el.offsetWidth; el.classList.add(cls);
    setTimeout(function(){ el.classList.remove(cls); }, 700);
  }
  function comboChip(n){
    if (quiet()) return;
    var c = document.createElement("div"); c.className = "lv-combo"; c.setAttribute("role","status");
    c.textContent = "🔥 連對 " + n + " 題！"; document.body.appendChild(c); setTimeout(function(){ c.remove(); }, 1300);
  }

  /* ---------- 答對／答錯（依強度） ---------- */
  var combo = 0;
  function milestone(n){
    if (LEVEL === "full") return n===3 || n===5 || (n>=10 && n%5===0);
    if (LEVEL === "mid")  return n===5 || (n>=10 && n%10===0);
    return n>=10 && n%10===0;
  }
  function onCorrect(el, n){
    replay(el, "lv-pop");
    if (LEVEL === "full") burstAt(el, false);
    if (milestone(n)){
      comboChip(n);
      if ((LEVEL==="full" && n>=5) || (LEVEL!=="full" && n>=10)) burstAt(null, true);
    }
  }
  function onWrong(el){ replay(el, "lv-shake"); }

  function wrapFn(name, after){
    if (!name || typeof window[name] !== "function" || window[name].__lv) return;
    var orig = window[name];
    var w = function(){ var r = orig.apply(this, arguments); var a = arguments; try{ after.call(this, a, r); }catch(e){} return r; };
    w.__lv = true; window[name] = w;
  }

  /* observe 接法：
     - attributes：元素「從不符合變成符合」答對／答錯選擇器時觸發（同一個元素下一題再變也會觸發）。
     - added（選用）：整段重畫的畫面，新插入的元素一出生就帶答對／答錯 → 只在使用者剛點過畫面（1 秒內）才算，
       避免切回「已經對過答案」的頁面被當成又答一次。
     - 同一批變動合併成一次回饋：有答錯就搖第一個答錯的，否則彈第一個答對的（一次揭曉多題不會連撒彩帶）。 */
  var lastTap = 0;
  document.addEventListener("pointerdown", function(){ lastTap = Date.now(); }, true);
  document.addEventListener("click", function(){ lastTap = Date.now(); }, true);
  function observeAnswers(cfg){
    var o = cfg.observe, okSel = o.correct, noSel = o.wrong, add = o.added || null;
    var state = new WeakMap();
    var anySel = [okSel, noSel].filter(Boolean).join(",");
    function st(el){ try{ return (okSel && el.matches(okSel)) ? "ok" : (noSel && el.matches(noSel)) ? "no" : ""; }catch(e){ return ""; } }
    function matches(root, sel){
      if (!sel || !(root instanceof Element)) return [];
      var out = []; try{ if (root.matches(sel)) out.push(root); out = out.concat(Array.prototype.slice.call(root.querySelectorAll(sel))); }catch(e){}
      return out;
    }
    // 先記下目前已經是答對／答錯的元素：之後它們只是別的 class 變了，不會被當成「剛答對」
    matches(document.body, anySel).forEach(function(el){ state.set(el, st(el)); });
    new MutationObserver(function(muts){
      var oks = [], nos = [], fresh = add && Date.now() - lastTap < 1000;
      // 同一批裡「先插入、再加答對記號」的元素（例如整段重畫後立刻標記）要交給 class 變動判斷，插入時不先記狀態
      var touched = new Set();
      muts.forEach(function(m){ if (m.type === "attributes") touched.add(m.target); });
      muts.forEach(function(m){
        if (m.type !== "childList") return;
        m.addedNodes.forEach(function(n){
          matches(n, anySel).forEach(function(el){ if (!touched.has(el)) state.set(el, st(el)); });   // 新元素出生狀態先記錄
          if (fresh){ oks = oks.concat(matches(n, add.correct)); nos = nos.concat(matches(n, add.wrong)); }
        });
      });
      touched.forEach(function(el){
        if (!(el instanceof Element)) return;
        var now = st(el), was = state.get(el) || "";
        state.set(el, now);
        if (now && now !== was) (now === "ok" ? oks : nos).push(el);
      });
      if (nos.length){ combo = 0; onWrong(nos[0]); }
      else if (oks.length){ combo++; onCorrect(oks[0], combo); }
    }).observe(document.body, { subtree:true, attributes:true, attributeFilter:["class"], childList:true });
  }

  /* ---------- 圖示換 Fluent Emoji（依原 emoji 對照） ---------- */
  var EMOJI = {
    "🍅":["tomato","coral"], "🎯":["bullseye","green"], "📚":["books","teal"], "⭐":["glowing_star","sun"], "🌟":["glowing_star","sun"],
    "🔥":["fire","sun"], "✅":["check_mark_button","green"], "🃏":["card_index","teal"], "📝":["memo",""], "✏️":["memo",""],
    "⚡":["high_voltage",""], "🔁":["repeat_button",""], "🔄":["repeat_button",""], "🏠":["house",""], "📊":["bar_chart",""], "📈":["bar_chart",""],
    "📖":["open_book",""], "🏆":["trophy","sun"], "🚀":["rocket",""], "🎉":["party_popper",""], "✨":["sparkles",""], "🌱":["seedling",""],
    "📋":["clipboard",""], "🏀":["basketball",""],
    "🆘":["sos_button","coral"], "🔎":["magnifying_glass_tilted_right",""], "🔍":["magnifying_glass_tilted_left",""], "👤":["bust_in_silhouette",""],
    "✈️":["airplane",""], "✈":["airplane",""], "🛡️":["shield",""], "🛡":["shield",""], "🎧":["headphone",""], "🧩":["puzzle_piece",""],
    "🎤":["microphone",""], "📇":["card_index","teal"], "🔑":["key",""], "🎭":["performing_arts",""], "🔧":["wrench",""],
    "🔗":["link",""], "🔤":["input_latin_letters",""], "🧱":["brick",""], "📒":["ledger",""], "📕":["closed_book",""],
    "🧒":["child",""], "💬":["speech_balloon",""], "⚙️":["gear",""], "⚙":["gear",""], "💡":["light_bulb","sun"], "☀️":["sun","sun"], "☀":["sun","sun"],
    "✍️":["writing_hand",""], "✍":["writing_hand",""], "📒":["ledger",""], "🎮":["video_game",""], "❤️":["red_heart","coral"], "❤":["red_heart","coral"],
    "⭐️":["glowing_star","sun"], "📅":["calendar",""], "📆":["calendar",""], "🗓️":["calendar",""], "💾":["floppy_disk",""], "📤":["outbox_tray",""], "📥":["inbox_tray",""],
    "🎓":["graduation_cap",""], "📚️":["books","teal"], "🗂️":["card_index_dividers",""], "🗂":["card_index_dividers",""], "🔊":["speaker_high_volume",""], "📝️":["memo",""]
  };
  function swapEmoji(el){
    if (el.__lv) return;
    var key = (el.textContent||"").trim().replace(/️/g,"");
    var m = EMOJI[key] || EMOJI[key + "️"]; if (!m) return;
    el.__lv = true; el.textContent = ""; el.appendChild(icon(m[0], el.closest(".nav,.tabbar,nav") ? "lv-ico-sm" : "lv-ico"));
    if (m[1]) el.setAttribute("data-tint", m[1]);
  }
  /* 「📖 已學單字」這種 emoji 寫在文字開頭的元素：只換開頭那個 emoji，文字不動（對照表沒有的就整個不換） */
  function swapLead(el){
    if (el.__lvLead) return;
    var t = el.firstChild; if (!t || t.nodeType !== 3) return;
    var mm = t.nodeValue.match(/^\s*([\uD800-\uDBFF][\uDC00-\uDFFF]|[☀-➿⭐⭕])️?\s*/);
    if (!mm) return;
    var m = EMOJI[mm[1]]; if (!m) return;
    el.__lvLead = true;
    t.nodeValue = t.nodeValue.slice(mm[0].length);
    var img = icon(m[0], "lv-ico-inline"); img.style.marginRight = ".3em";
    el.insertBefore(img, t);
  }
  function decorate(){
    var c = E();
    if (c.icons) document.querySelectorAll(c.icons).forEach(swapEmoji);
    if (c.iconsLead) document.querySelectorAll(c.iconsLead).forEach(swapLead);
    if (c.flame){
      var sr = document.querySelector(c.flame);
      if (sr && !sr.__lv && sr.firstChild && sr.firstChild.nodeType===3 && sr.firstChild.nodeValue.indexOf("🔥")===0){
        sr.__lv = true; sr.firstChild.nodeValue = sr.firstChild.nodeValue.replace("🔥","");
        sr.insertBefore(icon("fire","lv-ico-inline lv-flame"), sr.firstChild);
      }
    }
  }

  /* ---------- 新手第一步卡 ---------- */
  function renderHero(){
    var c = E(); if (!c.hero || !c.fresh) return;
    var fresh = c.fresh();
    document.body.classList.toggle("lv-fresh", fresh);
    var hero = document.getElementById("lvHero");
    if (!fresh){ if (hero) hero.remove(); return; }
    if (hero) return;
    var anchor = document.querySelector("#view-home .tiles"); if (!anchor) return;
    var t = c.heroText;
    hero = document.createElement("div"); hero.id = "lvHero"; hero.className = "lv-hero";
    hero.appendChild(icon("seedling","lv-hero-ico"));
    var h = document.createElement("h3"); h.textContent = t.h; hero.appendChild(h);
    var p = document.createElement("p"); p.textContent = t.p; hero.appendChild(p);
    var st = document.createElement("div"); st.className = "lv-steps";
    t.steps.forEach(function(s){ var x = document.createElement("span"); x.textContent = s; st.appendChild(x); });
    hero.appendChild(st);
    var b = document.createElement("button"); b.className = "lv-go"; b.type = "button"; b.textContent = "出發！🚀";
    b.addEventListener("click", c.start); hero.appendChild(b);
    anchor.parentNode.insertBefore(hero, anchor);
  }
  var lastVals = {};
  function bumpNums(){
    (E().bump||[]).forEach(function(id){
      var el = document.getElementById(id); if (!el) return; var v = el.textContent;
      if (lastVals[id]!==undefined && lastVals[id]!==v && parseFloat(v) > parseFloat(lastVals[id])) replay(el, "lv-bump");
      lastVals[id] = v;
    });
  }
  function refresh(){ try{ decorate(); renderHero(); bumpNums(); }catch(e){} }

  function watchInstallBar(){
    var sel = E().installBar; var bar = sel && document.querySelector(sel); if (!bar) return;
    var sync = function(){ document.body.classList.toggle("lv-has-installbar", bar.children.length > 0); };
    sync(); new MutationObserver(sync).observe(bar, { childList:true });
  }

  function init(){
    ENGINE = cssVar("--lv-engine"); LEVEL = cssVar("--lv-level") || "full";
    var c = E(); if (!ENGINE || !ENGINES[ENGINE]) return;
    document.documentElement.setAttribute("data-lv-engine", ENGINE);
    try{
      if (c.wrap){
        var w = c.wrap;
        wrapFn(w.juice, function(a){
          var ok = a[0];
          if (ok){ var n = 0; try{ n = quiz.combo || 0; }catch(e){} onCorrect(document.querySelector(c.correctEl), n); }
          else onWrong(document.querySelector(c.wrongEl));
        });
        wrapFn(w.celebrate, function(){ bigCelebrate(); });
        wrapFn(w.result, function(){ if (c.resultPct && c.resultPct() >= .8) setTimeout(bigCelebrate, 250); });
        wrapFn(w.home, refresh);
        wrapFn(w.go, function(){ setTimeout(refresh, 0); });
      }
      if (c.observe) observeAnswers(c);
      if (c.afterRender) c.afterRender.forEach(function(n){ wrapFn(n, function(){ setTimeout(refresh, 0); }); });
      if (c.celebrateFns) c.celebrateFns.forEach(function(n){ wrapFn(n, function(){ bigCelebrate(); }); });
      refresh(); watchInstallBar();
      if (c.observeIcons) new MutationObserver(function(){ decorate(); }).observe(document.body, { childList:true, subtree:true });
    }catch(e){}
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
