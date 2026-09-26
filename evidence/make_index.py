"""usage: python evidence/make_index.py
Build evidence/index.json: one record per finding, linking transcripts, audio, commits, tests and Bob tasks."""
import json, os, re, subprocess
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))  # repo root

TASKS = {  # finding -> Bob tasks that fixed/verified it (from bob_sessions/INDEX.md)
    'F-01': ['03g'], 'F-02': ['05'], 'F-03': ['06'], 'N-01': ['07'], 'N-02': ['08', '23', '27'],
    'F-04': ['13a', '13b', '13d', '15'], 'F-05': ['13a', '16', '21'], 'F-06': ['13d', '17'],
    'F-07': ['22', '24', '25'], 'F-08': ['22', '26'], 'F-09': ['34'], 'F-10': ['36b', '37'],
}
SOURCE = {'F-01': 'audit', 'F-02': 'audit', 'F-03': 'audit', 'N-01': 'audit', 'N-02': 'audit',
          'F-04': 'bob-sweep /flights', 'F-05': 'bob-sweep /flights', 'F-06': 'bob-sweep /flights',
          'F-07': 'bob-sweep /', 'F-08': 'bob-sweep /', 'F-09': 'regression in our own F-01 fix, found by ear while typing', 'F-10': 'bob /earshot run on /destinations/mars'}
DECIDED = {'N-01': 'ear + human eye (the animation stopping is visual)'}

tests = {t['id']: t for t in json.load(open('hear-tests.json', encoding='utf8'))}
shots = os.listdir('bob_sessions')
records = []
for line in open('findings.md', encoding='utf8'):
    m = re.match(r'^([FN]-\d\d) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| (\w+)', line)
    if not m:
        continue
    fid, wcag, comp, keys, expect, verify = [g.strip() for g in m.groups()]
    folder = f'evidence/{fid}'
    files = sorted(os.listdir(folder)) if os.path.isdir(folder) else []
    def pick(pred):
        return [f'{folder}/{f}' for f in files if pred(f)]
    commits = subprocess.run(['git', 'log', '--format=%h %s', '--grep', fid, '--', 'galaxium/'],
                             capture_output=True, text=True, encoding='utf8').stdout.strip().splitlines()
    rec = {
        'id': fid,
        'wcag': wcag,
        'component': comp[:240],
        'source': SOURCE.get(fid, ''),
        'key_script': keys,
        'expected': expect[:240],
        'verified_by': DECIDED.get(fid, 'ear (NVDA transcript)' if verify == 'ear' else verify),
        'before': pick(lambda f: f.startswith('before') and f.endswith('.txt')),
        'rejected_attempts': pick(lambda f: ('rejected' in f or 'still_silent' in f) and f.endswith('.txt')),
        'after': pick(lambda f: (f.startswith('after') or f.startswith('ear_check')) and f.endswith('.txt')),
        'audio': pick(lambda f: f.endswith('.wav')),
        'fix_commits': commits,
        'gate_test': tests.get(fid),
        'bob_tasks': TASKS.get(fid, []),
        'bob_screenshots': sorted(f'bob_sessions/{s}' for s in shots
                                  if any(re.match(rf'pytr_task{t}(_|$)', s) or (t == '03g' and 'attempt7' in s) for t in TASKS.get(fid, []))),
    }
    records.append(rec)

manifest = {
    'project': 'Earshot: screen-reader tests for AI-written UI',
    'app': 'IBM Galaxium Travels sample app (galaxium/, Apache-2.0, upstream e4e18ae)',
    'screen_reader': 'NVDA 2026.2 (real, not simulated); transcripts are verbatim from NVDA\'s log, audio is NVDA-process-only',
    'summary': {'findings': len(records), 'verified_by_ear': sum(1 for r in records if r['verified_by'].startswith('ear')),
                'gate_tests': len(tests), 'benchmark': 'bench/RESULTS.md'},
    'gate_evidence': sorted(f'evidence/gate/{f}' for f in os.listdir('evidence/gate')),
    'findings': records,
}
json.dump(manifest, open('evidence/index.json', 'w', encoding='utf8'), indent=2, ensure_ascii=False)
print(len(records), 'findings;', 'missing after:', [r['id'] for r in records if not r['after']],
      '; no commit:', [r['id'] for r in records if not r['fix_commits']], '; no test:', [r['id'] for r in records if not r['gate_test']])
