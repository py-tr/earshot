"""Bob SessionStart hook: a two-second preflight so a session never starts listening into the void.
Checks the local NVDA setup and that each app under test answers; prints one line that Bob reads as
session context. Always exits 0: it informs, it never blocks.
usage (as a hook): .venv\\Scripts\\python.exe earshot_mcp\\preflight.py"""
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
APPS = {"Galaxium": "http://localhost:5173/", "TodoMVC": "http://localhost:7002/"}


def up(url):
    try:
        urllib.request.urlopen(url, timeout=2)
        return True
    except Exception:
        return False


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    env = {}
    path = os.path.join(HERE, "local.env")
    if os.path.isfile(path):
        for line in open(path, encoding="utf-8"):
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k] = v
    nvda = env.get("EARSHOT_NVDA", "")
    problems = []
    if not nvda or not os.path.isfile(nvda):
        problems.append("NVDA not found (set EARSHOT_NVDA in earshot_mcp/local.env)")
    apps = {name: up(url) for name, url in APPS.items()}
    if not any(apps.values()):
        problems.append("no app under test is running")
    status = ", ".join(f"{n} {'up' if ok else 'down'}" for n, ok in apps.items())
    if problems:
        print(f"Earshot preflight: NOT READY: {'; '.join(problems)}. Apps: {status}. "
              "Do not call listen until this is fixed; tell the user what to start.")
    else:
        print(f"Earshot preflight: ready. NVDA found. Apps: {status}. "
              "Tests for an app that is down are skipped by the gate; do not listen to a down app.")
    sys.exit(0)


if __name__ == "__main__":
    main()
