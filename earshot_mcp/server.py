"""Earshot MCP server — wraps driver.py + extract.py for NVDA-assisted accessibility testing."""
import os, sys, subprocess, time, re

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


def _strip_markers(line: str) -> str:
    """Remove NVDA-internal speech markers, keeping the human-readable parts."""
    # Strip LangChangeCommand and CancellableSpeech wrappers
    line = re.sub(r"LangChangeCommand\([^)]*\),?\s*", "", line)
    line = re.sub(r"CancellableSpeech\([^)]*\),?\s*", "", line)
    line = line.strip().rstrip(",")
    return line


def _format_output(txt_path: str, meta_label: str) -> str:
    """Parse the extract.py output file into short human-readable lines."""
    with open(txt_path, encoding="utf-8") as f:
        raw_lines = f.read().splitlines()

    results = []
    for line in raw_lines:
        if line.startswith("#") or not line.strip():
            continue
        # Format: [  5.21s] Input: key ENTER  OR  [  5.21s] Speaking: ...
        m = re.match(r"\[\s*(\d+\.\d+)s\]\s+(Input:|Speaking)\s+(.*)", line)
        if not m:
            continue
        ts, kind, rest = m.group(1), m.group(2), m.group(3).strip()
        rest = _strip_markers(rest)
        if not rest:
            continue
        if kind == "Input:":
            # e.g. "Input: key ENTER" -> "5.21s  ENTER"
            key_m = re.search(r"key\s+(\S+)", rest)
            key = key_m.group(1) if key_m else rest
            results.append(f"{ts}s  {key}")
        else:
            # Speaking: "Sign In, dialog"  -> "5.21s  said: Sign In, dialog"
            phrase = rest.strip('"').strip("'")
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
    driver_result = subprocess.run(
        [sys.executable, driver, label, key_script, str(gap), f"--start={start}"],
        capture_output=True, text=True, timeout=120,
    )
    if driver_result.returncode != 0:
        # Check for aborted message in stdout (driver prints JSON with aborted key)
        import json as _json
        try:
            meta = _json.loads(driver_result.stdout)
            if meta.get("aborted"):
                return f"aborted: {meta['aborted']}"
        except Exception:
            pass
        return f"aborted: driver exited with code {driver_result.returncode}"

    # Run extract.py
    extract_result = subprocess.run(
        [sys.executable, extract, label, "listen", txt_path],
        capture_output=True, text=True, timeout=120,
    )
    if extract_result.returncode != 0:
        return f"aborted: extract failed: {extract_result.stderr.strip()}"

    return _format_output(txt_path, label)


server.run("stdio")
