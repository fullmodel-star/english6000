# -*- coding: utf-8 -*-
"""Build EXAM_WORDS dataset from the FULL past-6-year (110-115) 學測英文 exam papers.
Extract every English word from each 試題.pdf, map to the 6005 wordlist base forms
(keep only curriculum words), aggregate years+freq, and tag words that were
詞彙題(vocab MC) answers (ans) using exams_db.json. Output files/exam_words.json."""
import json, re, pathlib, fitz, sys
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
here = pathlib.Path(__file__).parent
app = here.parent
DESK = pathlib.Path.home()/'Desktop'
EXAMDIR = DESK/'大學聯考'
YEARS = [110, 111, 112, 113, 114, 115]

W = json.loads(re.search(r'const WORDS = (\[.*?\]);',
        (app/'index.html').read_text(encoding='utf-8'), re.S).group(1))
wl = {w['word'].lower(): w for w in W}

def base_of(w):
    w = w.lower().strip()
    if w in wl: return w
    cands = []
    for suf, rep in [('s',''),('es',''),('ies','y'),('ied','y'),('ed',''),('d',''),
                     ('ing',''),('ing','e'),('ly',''),('er',''),('er','e'),('est',''),
                     ('iest','y'),('ier','y'),('ment',''),('ment','e'),('ful',''),('ness',''),
                     ('ation','ate'),('ation',''),('tion','t'),('sion',''),('ity',''),
                     ('ous',''),('ious','y'),('ously',''),('ably',''),('ably','able'),
                     ('ibly','ible'),('ive',''),('al',''),('ic',''),('ical','')]:
        if w.endswith(suf) and len(w) > len(suf)+1:
            cands.append(w[:-len(suf)] + rep)
    if w.endswith('ing') and len(w) > 4 and w[-4] == w[-5]: cands.append(w[:-4])
    if w.endswith('ed') and len(w) > 3 and w[-3] == w[-4]: cands.append(w[:-3])
    for c in cands:
        if c in wl: return c
    return None

from collections import defaultdict, Counter
years = defaultdict(set); freq = Counter()
for y in YEARS:
    pdf = EXAMDIR/f'{y}學年度學測英文'/f'{y}學年度學測英文_試題.pdf'
    if not pdf.exists():
        print("MISSING", pdf); continue
    d = fitz.open(pdf)
    txt = ''.join(p.get_text() for p in d)
    for tok in re.findall(r'[A-Za-z]{2,}', txt):
        b = base_of(tok)
        if b:
            years[b].add(y); freq[b] += 1

# 詞彙題 answers (⭐) from exams_db
ans_words = set()
edb = EXAMDIR/'exams_db.json'
if edb.exists():
    for q in json.load(open(edb, encoding='utf-8')):
        aw = base_of(q['options'][q['answer']].strip())
        if aw: ans_words.add(aw)

rows = []
for w in sorted(years):
    info = wl[w]
    rows.append({'w': w, 'base': w, 'years': sorted(years[w]),
                 'freq': freq[w], 'ans': 1 if w in ans_words else 0,
                 'level': info['level']})

print(f"exam-vocab words (mapped to 6005): {len(rows)}")
lc = Counter(r['level'] for r in rows)
print("by level:", dict(sorted(lc.items())))
print("詞彙題正解字(⭐):", sum(r['ans'] for r in rows))
print("multi-year (>=3 年):", sum(1 for r in rows if len(r['years']) >= 3))
json.dump(rows, open(here/'exam_words.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
