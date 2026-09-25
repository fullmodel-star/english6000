# -*- coding: utf-8 -*-
"""Fix 4 malformed word entries from PDF line-wrapping artifacts, then align content keys."""
import json, pathlib
here = pathlib.Path(__file__).parent
full = json.load(open(here/'words_full.json', encoding='utf-8'))
prog = json.load(open(here/'content_progress.json', encoding='utf-8'))

# alias generated content to clean keys
if 'spokesperson/spokesman/spokeswoman' in prog:
    prog['spokesperson'] = prog['spokesperson/spokesman/spokeswoman']
if 'sportsman/sportswoman' in prog:
    prog['sportsman'] = prog['sportsman/sportswoman']
json.dump(prog, open(here/'content_progress.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

out = []
for e in full:
    w = e['word']
    if w == 'calm v./adj./n camel':
        # split into two real words
        out.append({**e, 'word':'calm', 'pos':'v/adj/n'})
        out.append({**e, 'word':'camel', 'pos':'n'})
        continue
    if w == 'neither adj./adv./pron./':
        e = {**e, 'word':'neither', 'pos':'adv/conj/pron/adj'}
    elif w == 'spokesperson/ spokesman/ spokeswoman':
        e = {**e, 'word':'spokesperson', 'pos':'n'}
    elif w == 'sportsman/sportswoma n':
        e = {**e, 'word':'sportsman', 'pos':'n'}
    out.append(e)

# dedup by word (calm/camel/neither may already exist elsewhere? unlikely, but guard)
seen=set(); ded=[]
for e in out:
    k=e['word'].lower()
    if k in seen: continue
    seen.add(k); ded.append(e)
json.dump(ded, open(here/'words_full.json','w',encoding='utf-8'), ensure_ascii=False)
print(f"fixed. words: {len(full)} -> {len(ded)}")
for w in ['calm','camel','neither','spokesperson','sportsman']:
    hit=[e for e in ded if e['word']==w]
    print(' ',w,'in words_full:',bool(hit),'| content:', w in prog)
