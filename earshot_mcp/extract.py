import json, os, re, sys, time, datetime
# usage: python extract.py <label> <state> <out.txt>  (reads <label>.meta.json and <label>.segment.log from EARSHOT_TAKES)
label, state, out = sys.argv[1], sys.argv[2], sys.argv[3]
TAKES = os.environ.get('EARSHOT_TAKES', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'takes'))
m = json.load(open(os.path.join(TAKES, f'{label}.meta.json')))
t0 = m['t0']; d0 = datetime.datetime.fromtimestamp(t0)
lines = open(os.path.join(TAKES, f'{label}.segment.log'), encoding='utf-8').read().splitlines()
res = []; ts = None
for l in lines:
    g = re.search(r'\((\d\d):(\d\d):(\d\d)\.(\d\d\d)\)', l)
    if l.startswith('IO - ') and g:
        h, mi, s, ms = map(int, g.groups())
        ts = d0.replace(hour=h, minute=mi, second=s, microsecond=ms * 1000).timestamp() - t0
    elif (l.startswith('Input:') or l.startswith('Speaking')) and ts is not None:
        res.append(f'[{ts:6.2f}s] {l}')
hdr = [f"# NVDA speech/input log for the '{state}' take ({label}), extracted verbatim from NVDA's own log (log level: input/output).",
       f"# Clip time 0.00 s = {d0.strftime('%H:%M:%S.%f')[:-3]} local ({d0.date()}). Format: [clip seconds, from NVDA log timestamp] original NVDA log line.",
       "# Only 'Input:' and 'Speaking' records are listed; LangChangeCommand/CancellableSpeech are NVDA-internal markers, kept verbatim.",
       "# Note: the timestamp is when NVDA queued the speech; audio can start slightly later if earlier speech is still playing.",
       "# DOM focus after each key (document.activeElement sampled over CDP ~0.3 s before the next key; not from NVDA):"]
hdr += [f"#   {k} @ {t:.2f}s -> {a}" for k, t, a in m['keys']]
open(out, 'w', encoding='utf-8', newline='\n').write('\n'.join(hdr + [''] + res) + '\n')
print(out, len(res))
