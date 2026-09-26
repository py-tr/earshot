"""
Bob PreToolUse hook – puts the Earshot gate in front of git commits.

stdin: JSON with keys "tool" and "input" (input.command is the shell command).
Exit 0  → allow the command to proceed.
Exit 2  → block the command (Bob honours this for PreToolUse hooks).
"""

import json
import os
import re
import subprocess
import sys

VENV_PYTHON = os.path.join(".venv", "Scripts", "python.exe")
LOCAL_ENV   = os.path.join("earshot_mcp", "local.env")
HEAR_TESTS  = os.path.join("earshot_mcp", "hear_tests.py")
LAST_LOG    = os.path.join("takes", "bob_hook_last.txt")
VERIFIED_TREE = os.path.join(".git", "earshot-verified-tree")

UTF8 = dict(text=True, encoding="utf-8", errors="replace",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"})


def main():
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        sys.exit(0)

    inp = data.get("input") or {}
    if isinstance(inp, str):  # tolerate the tool input arriving as a JSON string
        try:
            inp = json.loads(inp)
        except json.JSONDecodeError:
            inp = {"command": inp}
    command = inp.get("command", "") if isinstance(inp, dict) else ""

    # Only act on git commit commands (including --no-verify).
    if not re.search(r"\bgit\b.*\bcommit\b", command):
        sys.exit(0)

    # Skip if no local NVDA setup.
    if not os.path.isfile(VENV_PYTHON) or not os.path.isfile(LOCAL_ENV):
        print("earshot bob-hook: skipped (no local NVDA setup)", file=sys.stderr)
        sys.exit(0)

    # Check whether any staged files are under the frontend src.
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, **UTF8
    )
    staged = result.stdout.splitlines()
    frontend_staged = [
        f for f in staged
        if f.startswith("galaxium/booking_system_frontend/src/")
    ]
    if not frontend_staged:
        sys.exit(0)

    # Run the earshot test suite against the staged tree.
    proc = subprocess.run(
        [VENV_PYTHON, HEAR_TESTS, "--staged"],
        capture_output=True, **UTF8
    )
    runner_exit = proc.returncode
    output = proc.stdout + proc.stderr

    if runner_exit == 0:
        verdict = "PASS – Earshot (Bob hook): all screen-reader announcements verified."
    elif runner_exit == 2:
        verdict = (
            "BLOCKED by Earshot (Bob hook): could not listen "
            "(is the app running on :5173 and the desktop free?); "
            "details in takes/bob_hook_last.txt"
        )
    else:
        verdict = (
            "BLOCKED by Earshot (Bob hook): this commit breaks what a screen reader hears; "
            "details in takes/bob_hook_last.txt"
        )

    log_content = output + "\n" + verdict + "\n"

    os.makedirs("takes", exist_ok=True)
    with open(LAST_LOG, "w", encoding="utf-8") as fh:
        fh.write(log_content)

    print(log_content, file=sys.stderr)

    if runner_exit == 0:
        # Record the verified tree so the git pre-commit hook can skip re-running.
        tree_proc = subprocess.run(
            ["git", "write-tree"],
            capture_output=True, **UTF8
        )
        with open(VERIFIED_TREE, "w", encoding="utf-8") as fh:
            fh.write(tree_proc.stdout.strip())
        sys.exit(0)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
