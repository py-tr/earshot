# earshot_mcp

The `earshot` MCP server gives IBM Bob one tool, `listen(key_script)`. It drives Chrome with real
keystrokes while the NVDA screen reader runs, and returns only the lines NVDA spoke.

- `driver.py`, `extract.py`, `proccap/`: **prepared before kickoff (2026-09-25) as spike tooling**
  and disclosed. `driver.py` presses the keys and records NVDA's audio (NVDA's process only).
  `extract.py` turns NVDA's log into a timestamped transcript. `proccap/` is the small .NET
  audio-capture tool (`dotnet publish -c Release -o out`).
- `server.py`: the MCP server, written by IBM Bob during the event (see `bob_sessions/`).

## Setup (Windows)

1. Portable NVDA, with its log level set to "input/output".
2. `python -m venv .venv` then `.venv\Scripts\pip install -r earshot_mcp\requirements.txt`
3. Create `earshot_mcp\local.env` (git-ignored and Bob-ignored) with:
   `EARSHOT_NVDA=<path to nvda.exe>` and `EARSHOT_NVDA_CONFIG=<path to its userConfig>`.
   Optional: `EARSHOT_URL` (default `http://localhost:5173/flights`), `EARSHOT_TAKES`, `EARSHOT_PROCCAP`.
4. Galaxium frontend on :5173 and backend running.
