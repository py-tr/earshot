"""Earshot NVDA driver. PREPARED BEFORE KICKOFF (2026-09-25) as spike tooling, disclosed in the README;
copied here with machine paths replaced by environment variables. Bob wraps it as the earshot MCP server.
usage: python driver.py <label> <keyscript> <gap_s> [--start=<button name>] [--collapsed]
keyscript: comma list like "ENTER,TAB*5,STAB,ESC"; tokens: TAB, STAB (Shift+Tab), ENTER, ESC.
Keys on an absolute schedule (t0+1+i*gap);
after each key the page's document.activeElement is sampled over CDP (no OS input) and logged;
Audio: NVDA-process-only loopback capture via proccap.exe (no other app is recorded). Outputs go to EARSHOT_TAKES.
Safety: a key is only sent if the foreground window is OUR Chrome window; otherwise abort.
"""
import sys, os, time, subprocess, wave, ctypes, json, re
from playwright.sync_api import sync_playwright
from pywinauto import Desktop
from pywinauto.keyboard import send_keys

label, keyscript, gap = sys.argv[1], sys.argv[2], float(sys.argv[3])
start_name = 'Filters'
for a in sys.argv:
    if a.startswith('--start='): start_name = a[8:]
KEYMAP = {'TAB': '{TAB}', 'STAB': '+{TAB}', 'ENTER': '{ENTER}', 'ESC': '{ESC}'}
keys = []
for tok in keyscript.split(','):
    k, _, n = tok.partition('*'); keys += [k] * int(n or 1)
assert all(k in KEYMAP for k in keys), keys
HERE = os.path.dirname(os.path.abspath(__file__))
# Machine-specific paths come from the environment (see earshot_mcp/README.md); outputs go to EARSHOT_TAKES.
NVDA = os.environ['EARSHOT_NVDA']                      # path to a portable nvda.exe
CFG = os.environ['EARSHOT_NVDA_CONFIG']                # its userConfig dir (log level input/output)
URL = os.environ.get('EARSHOT_URL', 'http://localhost:5173/flights')
SCR = os.environ.get('EARSHOT_TAKES', os.path.join(os.path.dirname(HERE), 'takes'))
os.makedirs(SCR, exist_ok=True)
LOG = os.path.join(SCR, f"nvda_{label}.log")
PROCCAP = os.environ.get('EARSHOT_PROCCAP', os.path.join(HERE, 'proccap', 'out', 'proccap.exe'))
META = os.path.join(SCR, f"{label}.meta.json")
user32 = ctypes.windll.user32
ACTIVE_JS = """() => { const a = document.activeElement; if (!a || a === document.body) return 'BODY';
  const n = (a.getAttribute('aria-label') || a.textContent || a.getAttribute('placeholder') || '').trim().slice(0, 50);
  return a.tagName + ' "' + n + '"' + (a.closest('[role=dialog]') ? ' [inside dialog]' : ' [page behind dialog]'); }"""

def title_of(h):
    buf = ctypes.create_unicode_buffer(512); user32.GetWindowTextW(h, buf, 512); return buf.value

def logtext():
    try: return open(LOG, 'rb').read().decode('utf-8', 'replace')
    except FileNotFoundError: return ''

def wait_log(pattern, since, timeout=10):
    t = time.time()
    while time.time() - t < timeout:
        if re.search(pattern, logtext()[since:]): return True
        time.sleep(0.2)
    return False

subprocess.run([NVDA, '-q'], timeout=30); time.sleep(2)
if os.path.exists(LOG): os.remove(LOG)
meta = {'label': label, 'keyscript': keyscript, 'gap': gap, 'start': start_name, 'aborted': None}

with sync_playwright() as p:
    br = p.chromium.launch(channel='chrome', headless=False,
                           args=['--start-maximized', '--force-renderer-accessibility'])
    ctx = br.new_context(no_viewport=True)
    page = ctx.new_page()
    page.goto(URL)
    page.wait_for_selector('text=/Showing [0-9]+ flights/')
    page.wait_for_timeout(1500)
    w = Desktop(backend='win32').window(title_re='.*booking_system_frontend.*Chrome.*')
    w.set_focus(); time.sleep(1)
    hwnd = w.handle
    subprocess.Popen([NVDA, f'--log-file={LOG}', f'--config-path={CFG}'])
    meta['nvda_init'] = wait_log(r'NVDA initialized', 0, 20); time.sleep(3)
    pc = None; STOPF = os.path.join(SCR, f'{label}.stop')
    if os.path.exists(STOPF): os.remove(STOPF)
    out = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq nvda*', '/FO', 'CSV', '/NH'], capture_output=True, text=True, creationflags=0x08000000).stdout
    pids = [int(l.split('","')[1]) for l in out.strip().splitlines() if l.startswith('"nvda')]
    meta['nvda_pids'] = pids
    pc = subprocess.Popen([PROCCAP, str(pids[0]), os.path.join(SCR, f'{label}.nvdaonly.raw.wav'), STOPF], stdout=subprocess.PIPE, text=True, creationflags=0x08000000)
    meta['proccap_start_line'] = pc.stdout.readline().strip()
    if user32.GetForegroundWindow() != hwnd:
        w.set_focus(); time.sleep(2)
    off = len(logtext())
    page.get_by_role('button', name=start_name).first.focus()
    meta['start_announced'] = wait_log(re.escape(start_name) + r"'?, 'button'|'button', '" + re.escape(start_name), off, 8)
    time.sleep(7)
    meta['fg_start'] = title_of(user32.GetForegroundWindow())
    meta['active_start'] = page.evaluate(ACTIVE_JS)
    log_off = len(logtext())
    t0 = time.time(); meta['t0'] = t0; meta['t0_str'] = time.strftime('%H:%M:%S', time.localtime(t0))
    meta['keys'] = []
    for i, k in enumerate(keys):
        tk = t0 + 1.0 + i * gap
        while time.time() < tk: time.sleep(0.01)
        fgh = user32.GetForegroundWindow()
        if fgh != hwnd:
            meta['aborted'] = f'foreground was "{title_of(fgh)}" at {time.time()-t0:.2f}s before key {i} ({k})'; break
        send_keys(KEYMAP[k])
        ts = round(time.time() - t0, 2)
        while time.time() < tk + gap - 0.3: time.sleep(0.01)
        meta['keys'].append([k, ts, page.evaluate(ACTIVE_JS)])
    time.sleep(1.5)
    open(STOPF, 'w').close(); meta['proccap_done'] = pc.communicate(timeout=30)[0].strip()
    meta['dur_wall'] = round(time.time() - t0, 2)
    meta['fg_end'] = title_of(user32.GetForegroundWindow())
    time.sleep(1)
    open(os.path.join(SCR, f'{label}.segment.log'), 'w', encoding='utf-8').write(logtext()[log_off:])
    page.screenshot(path=os.path.join(SCR, f'{label}.png'))
    br.close()
subprocess.run([NVDA, '-q'], timeout=30)
json.dump(meta, open(META, 'w'), indent=1)
print(json.dumps(meta))
if 'proccap_start_line' in meta and meta['proccap_start_line'].startswith('STARTED'):
    st_ms = int(meta['proccap_start_line'].split()[1])
    off_s = meta['t0'] - st_ms / 1000.0
    r = wave.open(os.path.join(SCR, f'{label}.nvdaonly.raw.wav'))
    sr = r.getframerate(); r.setpos(int(off_s * sr)); data = r.readframes(int(meta['dur_wall'] * sr))
    with wave.open(os.path.join(SCR, f'{label}.nvdaonly.wav'), 'wb') as wf:
        wf.setnchannels(r.getnchannels()); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes(data)
    print('trimmed offset', round(off_s, 3))
