// 英語番茄鐘 · 單字卡 — Service Worker（離線快取）
const CACHE = "904_english6000-icons-de0a15960d";
const ASSETS = ["./", "./index.html", "./manifest.json", "./ridgeline-ui.css", "./favicon.svg", "./icon.svg", "./icon-192.png", "./icon-512.png", "./icon-maskable-512.png", "./apple-touch-icon.png", "./lively-core.css", "./lively-engine.css", "./lively-theme.css", "./lively.js", "./vendor/canvas-confetti/confetti.browser.js", "./vendor/nunito/nunito-latin-800-normal.woff2", "./vendor/nunito/nunito-latin-900-normal.woff2", "./vendor/fluent-emoji/bar_chart_flat.svg", "./vendor/fluent-emoji/basketball_flat.svg", "./vendor/fluent-emoji/books_flat.svg", "./vendor/fluent-emoji/bullseye_flat.svg", "./vendor/fluent-emoji/card_index_flat.svg", "./vendor/fluent-emoji/check_mark_button_flat.svg", "./vendor/fluent-emoji/clipboard_flat.svg", "./vendor/fluent-emoji/fire_flat.svg", "./vendor/fluent-emoji/glowing_star_flat.svg", "./vendor/fluent-emoji/high_voltage_flat.svg", "./vendor/fluent-emoji/house_flat.svg", "./vendor/fluent-emoji/memo_flat.svg", "./vendor/fluent-emoji/open_book_flat.svg", "./vendor/fluent-emoji/party_popper_flat.svg", "./vendor/fluent-emoji/repeat_button_flat.svg", "./vendor/fluent-emoji/rocket_flat.svg", "./vendor/fluent-emoji/seedling_flat.svg", "./vendor/fluent-emoji/sparkles_flat.svg", "./vendor/fluent-emoji/star_flat.svg", "./vendor/fluent-emoji/tomato_flat.svg", "./vendor/fluent-emoji/trophy_flat.svg", "./lively-pre.js", "./vendor/fluent-emoji/airplane_flat.svg", "./vendor/fluent-emoji/brick_flat.svg", "./vendor/fluent-emoji/bust_in_silhouette_flat.svg", "./vendor/fluent-emoji/calendar_flat.svg", "./vendor/fluent-emoji/card_index_dividers_flat.svg", "./vendor/fluent-emoji/child_flat.svg", "./vendor/fluent-emoji/closed_book_flat.svg", "./vendor/fluent-emoji/floppy_disk_flat.svg", "./vendor/fluent-emoji/gear_flat.svg", "./vendor/fluent-emoji/graduation_cap_flat.svg", "./vendor/fluent-emoji/headphone_flat.svg", "./vendor/fluent-emoji/inbox_tray_flat.svg", "./vendor/fluent-emoji/input_latin_letters_flat.svg", "./vendor/fluent-emoji/key_flat.svg", "./vendor/fluent-emoji/ledger_flat.svg", "./vendor/fluent-emoji/light_bulb_flat.svg", "./vendor/fluent-emoji/link_flat.svg", "./vendor/fluent-emoji/magnifying_glass_tilted_left_flat.svg", "./vendor/fluent-emoji/magnifying_glass_tilted_right_flat.svg", "./vendor/fluent-emoji/microphone_flat.svg", "./vendor/fluent-emoji/outbox_tray_flat.svg", "./vendor/fluent-emoji/performing_arts_flat.svg", "./vendor/fluent-emoji/puzzle_piece_flat.svg", "./vendor/fluent-emoji/red_heart_flat.svg", "./vendor/fluent-emoji/shield_flat.svg", "./vendor/fluent-emoji/sos_button_flat.svg", "./vendor/fluent-emoji/speaker_high_volume_flat.svg", "./vendor/fluent-emoji/speech_balloon_flat.svg", "./vendor/fluent-emoji/sun_flat.svg", "./vendor/fluent-emoji/video_game_flat.svg", "./vendor/fluent-emoji/wrench_flat.svg", "./vendor/fluent-emoji/writing_hand_flat.svg"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)));
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// 快取優先；網路成功時順手更新快取（單檔 App、資料內嵌，離線完全可用）
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  e.respondWith(
    caches.match(e.request).then(hit => {
      const net = fetch(e.request).then(res => {
        if (res && res.status === 200 && res.type === "basic") {
          const copy = res.clone();
          caches.open(CACHE).then(c => c.put(e.request, copy));
        }
        return res;
      }).catch(() => hit);
      return hit || net;
    })
  );
});
self.addEventListener('message',e=>{if(e.data==='SKIP_WAITING'||e.data==='skipWaiting'||(e.data&&e.data.type==='SKIP_WAITING'))self.skipWaiting()});
