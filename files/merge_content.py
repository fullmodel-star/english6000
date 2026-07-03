# -*- coding: utf-8 -*-
"""Merge generated out/out_*.json into content_progress.json, report coverage.
Run build_app.py afterwards (or pass --build) to rebuild index.html."""
import json, pathlib, sys, subprocess, re

here = pathlib.Path(__file__).parent
outdir = here/'out'
prog_path = here/'content_progress.json'
prog = {}
if prog_path.exists():
    try: prog = json.load(open(prog_path, encoding='utf-8'))
    except Exception: prog = {}

need = json.load(open(here/'need_queue.json', encoding='utf-8'))
need_words = {w['word'].lower() for w in need}

files = sorted(outdir.glob('out_*.json'))
bad = []
added = 0
for f in files:
    try:
        d = json.load(open(f, encoding='utf-8'))
    except Exception as e:
        bad.append((f.name, str(e))); continue
    if not isinstance(d, dict):
        bad.append((f.name, 'not an object')); continue
    for w, v in d.items():
        wl = w.lower()
        if not isinstance(v, dict): continue
        if not v.get('zh_tw'): continue
        prog[wl] = {'zh_tw': v.get('zh_tw','').strip(),
                    'ex': v.get('ex','').strip(),
                    'exZh': v.get('exZh','').strip()}
        added += 1

json.dump(prog, open(prog_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

covered = need_words & set(prog.keys())
missing = sorted(need_words - set(prog.keys()))
print(f"out files: {len(files)}  bad: {len(bad)}")
for n,e in bad[:10]: print("  BAD", n, e)
print(f"progress entries: {len(prog)}  covers {len(covered)}/{len(need_words)} needed words")
print(f"still missing: {len(missing)}")
if missing[:20]: print("  e.g.", missing[:20])
# which batches are missing words -> report batch indices to re-run
batchmiss = {}
for i,w in enumerate(need):
    if w['word'].lower() in missing:
        b = i//50
        batchmiss[b] = batchmiss.get(b,0)+1
if batchmiss:
    print("batches needing rerun:", dict(sorted(batchmiss.items())))
json.dump(missing, open(here/'still_missing.json','w',encoding='utf-8'), ensure_ascii=False, indent=0)

if '--build' in sys.argv:
    print("--- rebuilding index.html ---")
    print(subprocess.run([sys.executable, str(here/'build_app.py')], capture_output=True, text=True, encoding='utf-8').stdout)
