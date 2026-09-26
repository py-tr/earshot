"""Earshot MCP server — wraps driver.py + extract.py for NVDA-assisted accessibility testing."""
import ast, os, sys, subprocess, time, re, threading

# Load local.env into environment before anything else (skip silently if absent)
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "local.env")
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _, _v = _line.partition("=")
                os.environ.setdefault(_k.strip(), _v.strip())

from mcp.server.mcpserver import MCPServer

server = MCPServer("earshot")

_HERE = os.path.dirname(os.path.abspath(__file__))

# Mapping from human-readable key names to driver format
_KEY_MAP = {
    "enter": "ENTER",
    "tab": "TAB",
    "shift+tab": "STAB",
    "escape": "ESC",
    "esc": "ESC",
}
# Tokens already in driver format (pass-through)
_DRIVER_TOKENS = {"ENTER", "TAB", "STAB", "ESC"}
# Regex for a valid TYPE=<text> driver token
_TYPE_TOKEN_RE = re.compile(r"^TYPE=[A-Za-z0-9 .\-']+$")
# Allowed characters inside Type "..." text
_TYPE_TEXT_RE = re.compile(r"^[A-Za-z0-9 .\-']+$")

# State for background takes
_results: dict = {}           # label -> result text (or None while running)
_events: dict = {}            # label -> threading.Event set when done
_current_label: str | None = None  # label of the currently running take
_state_lock = threading.Lock()


def _normalize_keys(text: str) -> str:
    """Convert findings.md key_script format to the driver's format.

    Supported tokens (comma-separated, each optionally followed by ×N / xN / *N):
      Enter, Tab, Shift+Tab, Escape   — mapped to ENTER / TAB / STAB / ESC
      Type "<text>" or Type <text>    — mapped to TYPE=<text>; text may contain
                                        letters, digits, spaces, and . - '
    """
    # If already fully in driver format, pass through unchanged.
    # Driver format: DRIVER_TOKENS optionally followed by *N, or TYPE=<text>.
    already_driver = True
    for tok in text.split(","):
        tok = tok.strip()
        if not tok:
            continue
        base, _, repeat = tok.partition("*")
        if base in _DRIVER_TOKENS and (not repeat or repeat.isdigit()):
            continue
        if _TYPE_TOKEN_RE.match(tok):
            continue
        already_driver = False
        break
    if already_driver and text.strip():
        return text.strip()

    # Parse findings.md format: comma-separated tokens, each optionally followed by ×N, xN, or *N
    result = []
    for raw in text.split(","):
        raw = raw.strip()
        if not raw:
            continue

        # --- Type "<text>" or Type <text> token (no repeat suffix allowed) ---
        type_m = re.match(r'^[Tt]ype\s+"([^"]+)"$', raw) or re.match(r'^[Tt]ype\s+(\S[^×x\*]*)$', raw)
        if type_m:
            type_text = type_m.group(1).strip()
            if not _TYPE_TEXT_RE.match(type_text):
                raise ValueError(
                    f"Type text {type_text!r} contains disallowed characters; "
                    "allowed: letters, digits, spaces, and . - '"
                )
            result.append(f"TYPE={type_text}")
            continue

        # Detect repeat suffix: ×N, xN, or *N (at the end)
        repeat_m = re.search(r"[×x\*](\d+)$", raw)
        if repeat_m:
            repeat = repeat_m.group(1)
            key_part = raw[:repeat_m.start()].strip()
        else:
            repeat = None
            key_part = raw

        key_lower = key_part.lower()
        if key_lower not in _KEY_MAP:
            raise ValueError(
                f"unknown key {key_part!r}; allowed: Enter, Tab, Shift+Tab, Escape "
                "(optional ×N), Type \"<text>\""
            )
        driver_key = _KEY_MAP[key_lower]
        if repeat:
            result.append(f"{driver_key}*{repeat}")
        else:
            result.append(driver_key)

    return ",".join(result)


def _format_output(txt_path: str, meta_label: str) -> str:
    """Parse the extract.py output file into short human-readable lines."""
    with open(txt_path, encoding="utf-8") as f:
        raw_lines = f.read().splitlines()

    # Parse focus lines from header comments:
    # #   ENTER @ 1.06s -> BUTTON "Select Seat Class" [page behind dialog]
    focus_lines = []
    for line in raw_lines:
        if not line.startswith("#"):
            break
        fm = re.match(r"#\s+(\w+)\s+@\s+[\d.]+s\s+->\s+(.*)", line)
        if fm:
            focus_lines.append((fm.group(1).upper(), fm.group(2).strip()))

    results = []
    key_index = 0  # tracks which focus entry to attach next
    for line in raw_lines:
        if line.startswith("#") or not line.strip():
            continue
        # Format: [  5.21s] Input: kb(desktop):enter
        #      OR [  5.21s] Speaking [LangChangeCommand(...), 'Sign In', 'dialog', ...]
        m = re.match(r"\[\s*(\d+\.\d+)s\]\s+(Input:|Speaking)\s+(.*)", line)
        if not m:
            continue
        ts, kind, rest = m.group(1), m.group(2), m.group(3).strip()
        if kind == "Input:":
            # e.g. "kb(desktop):enter" -> "ENTER"
            kb_m = re.match(r"kb\([^)]*\):(.*)", rest)
            key = kb_m.group(1).upper() if kb_m else rest.upper()
            results.append(f"{ts}s  {key}")
            if key_index < len(focus_lines):
                _fkey, _felem = focus_lines[key_index]
                results.append(f"       focus: {_felem}")
                key_index += 1
        else:
            # Speaking [...] — drop LangChangeCommand/CancellableSpeech markers, then
            # parse remaining bracket text as a Python list.
            cleaned = re.sub(r"\b(?:LangChangeCommand|CancellableSpeech)\s*\([^)]*\),?\s*", "", rest)
            # Remove trailing commas/spaces inside brackets before eval
            cleaned_eval = re.sub(r",\s*(\])", r"\1", cleaned.strip())
            try:
                items = ast.literal_eval(cleaned_eval)
                parts = [s for s in items if isinstance(s, str)]
            except Exception:
                parts = re.findall(r"['\"]([^'\"]+)['\"]", cleaned)
            phrase = ", ".join(parts)
            if phrase:
                results.append(f"{ts}s  said: {phrase}")

    wav_rel = f"takes/{meta_label}.nvdaonly.wav"
    results.append(f"audio: {wav_rel}")
    return "\n".join(results)


def _run_take(label: str, keys: str, start: str, gap: float, path: str = "/flights") -> None:
    """Run driver.py then extract.py and store the result text in _results[label]."""
    global _current_label
    import json as _json

    driver = os.path.join(_HERE, "driver.py")
    extract = os.path.join(_HERE, "extract.py")

    takes_dir = os.environ.get(
        "EARSHOT_TAKES",
        os.path.join(os.path.dirname(_HERE), "takes"),
    )
    txt_path = os.path.join(takes_dir, f"{label}.txt")

    try:
        # Run driver.py
        driver_result = subprocess.run(
            [sys.executable, driver, label, keys, str(gap), f"--start={start}", f"--path={path}"],
            capture_output=True, text=True, timeout=120,
        )

        # Detect abort via exit code or missing JSON meta line
        meta = None
        for _line in driver_result.stdout.splitlines():
            if _line.startswith("{"):
                try:
                    meta = _json.loads(_line)
                except Exception:
                    pass
                break

        if driver_result.returncode == 3:
            result = "aborted: the take stalled and was stopped after 95 s"
        elif driver_result.returncode != 0 or meta is None:
            result = f"aborted: driver failed (exit code {driver_result.returncode})"
        elif meta.get("aborted"):
            aborted_text = meta["aborted"]
            if "not found" in aborted_text:
                result = "aborted: start control not found (on pages other than /flights, use start=\"TOP\" with the page's path)"
            else:
                n_m = re.search(r"before key (\d+)", aborted_text)
                if n_m:
                    result = f"aborted: focus left the test window before key {n_m.group(1)}"
                else:
                    result = "aborted: driver reported an abort"
        else:
            # Run extract.py
            extract_result = subprocess.run(
                [sys.executable, extract, label, "listen", txt_path],
                capture_output=True, text=True, timeout=120,
            )
            if extract_result.returncode != 0:
                result = f"aborted: extract failed: {extract_result.stderr.strip()}"
            else:
                result = _format_output(txt_path, label)
    except Exception as exc:
        result = f"aborted: unexpected error: {exc}"
    finally:
        with _state_lock:
            _results[label] = result
            _current_label = None
        _events[label].set()


@server.tool(structured_output=False)
def listen(key_script: str, start: str = "Select Seat Class", gap: float = 2.0, path: str = "/flights") -> str:
    """key_script uses findings.md format e.g. "Tab ×5, Type \"Mars\""; path is the page URL path to load.
    start is the name of the control to focus first, or "TOP" to begin before the first focusable element of the page;
    the default "Select Seat Class" exists only on /flights, so pass start="TOP" on any other page.
    Supported tokens (comma-separated, each optionally ×N): Enter, Tab, Shift+Tab, Escape, Type "<text>".
    Returns what NVDA said, one line per key and per phrase."""
    global _current_label

    try:
        key_script = _normalize_keys(key_script)
    except ValueError as exc:
        return f"error: {exc}"

    with _state_lock:
        if _current_label is not None:
            busy_label = _current_label
            return f'busy: take {busy_label} is still running; call listen_result("{busy_label}")'

        label = "take_" + time.strftime("%Y%m%dT%H%M%S")
        _results[label] = None
        _events[label] = threading.Event()
        _current_label = label

    t = threading.Thread(target=_run_take, args=(label, key_script, start, gap, path), daemon=True)
    t.start()

    done = _events[label].wait(timeout=20.0)
    if done:
        return _results[label]
    return f'running: take {label}; call listen_result("{label}") to get the transcript'


@server.tool(structured_output=False)
def listen_result(label: str) -> str:
    """Waits up to 20 s for the named take and returns its transcript."""
    if label not in _events:
        return "error: unknown take"

    done = _events[label].wait(timeout=20.0)
    if done:
        return _results[label]
    return f'running: take {label}; call listen_result("{label}") to get the transcript'


if __name__ == "__main__":
    server.run("stdio")
