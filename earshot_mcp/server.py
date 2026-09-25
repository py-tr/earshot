"""Earshot MCP server — wraps driver.py + extract.py for NVDA-assisted accessibility testing."""
import ast, os, sys, subprocess, time, re

# Load local.env into environment before anything else
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "local.env")
with open(_env_path) as _f:
    for _line in _f:
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

from mcp.server.mcpserver import MCPServer

server = MCPServer("earshot")

_HERE = os.path.dirname(os.path.abspath(__file__))


def _format_output(txt_path: str, meta_label: str) -> str:
    """Parse the extract.py output file into short human-readable lines."""
    with open(txt_path, encoding="utf-8") as f:
        raw_lines = f.read().splitlines()

    results = []
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


@server.tool(structured_output=False)
def listen(key_script: str, start: str = "Select Seat Class", gap: float = 2.0) -> str:
    """Run driver.py then extract.py and return a short human-readable transcript."""
    label = "take_" + time.strftime("%Y%m%dT%H%M%S")
    driver = os.path.join(_HERE, "driver.py")
    extract = os.path.join(_HERE, "extract.py")

    takes_dir = os.environ.get(
        "EARSHOT_TAKES",
        os.path.join(os.path.dirname(_HERE), "takes"),
    )
    txt_path = os.path.join(takes_dir, f"{label}.txt")

    # Run driver.py
    import json as _json
    driver_result = subprocess.run(
        [sys.executable, driver, label, key_script, str(gap), f"--start={start}"],
        capture_output=True, text=True, timeout=120,
    )
    # driver.py always exits 0; detect abort via the first JSON line in stdout
    meta = {}
    for _line in driver_result.stdout.splitlines():
        if _line.startswith("{"):
            try:
                meta = _json.loads(_line)
            except Exception:
                pass
            break
    if meta.get("aborted"):
        aborted_text = meta["aborted"]
        # Extract "before key N" fragment; strip any window title context
        n_m = re.search(r"before key (\d+)", aborted_text)
        if n_m:
            return f"aborted: focus left the test window before key {n_m.group(1)}"
        return "aborted: driver reported an abort"

    # Run extract.py
    extract_result = subprocess.run(
        [sys.executable, extract, label, "listen", txt_path],
        capture_output=True, text=True, timeout=120,
    )
    if extract_result.returncode != 0:
        return f"aborted: extract failed: {extract_result.stderr.strip()}"

    return _format_output(txt_path, label)


if __name__ == "__main__":
    server.run("stdio")
