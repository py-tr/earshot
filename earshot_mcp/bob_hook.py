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
TESTS_JSON  = os.path.join("hear-tests.json")
LAST_LOG    = os.path.join("takes", "bob_hook_last.txt")
VERIFIED_TREE = os.path.join(".git", "earshot-verified-tree")

UTF8 = dict(text=True, encoding="utf-8", errors="replace",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"})

# ---------------------------------------------------------------------------
# Selection logic — mirrors hear_tests._APP_SOURCE / _select_tests
# ---------------------------------------------------------------------------

_APP_SOURCE = {
    "galaxium": "galaxium/booking_system_frontend/src/",
    "todomvc": "todomvc/src/",
    "uptime-kuma": "uptime-kuma/src/",
}

_TODOMVC_URL_PREFIX = "http://localhost:7002"
_UPTIME_KUMA_URL_PREFIX = "http://localhost:3000"


def _test_app(test: dict) -> str:
    """Return the app name for a test based on its path."""
    path = test.get("path", "")
    if path.startswith(_TODOMVC_URL_PREFIX):
        return "todomvc"
    if path.startswith(_UPTIME_KUMA_URL_PREFIX):
        return "uptime-kuma"
    return "galaxium"


def _diff_head_files() -> list[str]:
    """Return file paths that differ from HEAD in the working tree."""
    result = subprocess.run(
        ["git", "diff", "HEAD", "--name-only"],
        capture_output=True, **UTF8
    )
    return result.stdout.splitlines()


def _apps_for_files(files: list[str]) -> set[str]:
    """Return the set of app names that have files under their source folder."""
    apps: set[str] = set()
    for app, prefix in _APP_SOURCE.items():
        if any(f.startswith(prefix) for f in files):
            apps.add(app)
    return apps


def _select_test_ids(changed_files: list[str]) -> list[str] | None:
    """Return a list of test IDs to run, or None if no frontend files changed.

    Uses the same two-pass logic as hear_tests._select_tests:
      - For each app with changed files, if every changed file is covered by
        the watch list of at least one test, run only those watch-covering tests.
      - Otherwise run all tests for that app (safe default).
    """
    apps_with_changes = _apps_for_files(changed_files)
    if not apps_with_changes:
        return None

    try:
        with open(TESTS_JSON, encoding="utf-8") as fh:
            tests = json.load(fh)
    except OSError:
        return None

    selected_ids: list[str] = []

    for app in apps_with_changes:
        app_prefix = _APP_SOURCE[app]
        app_changed = [f for f in changed_files if f.startswith(app_prefix)]
        app_tests = [t for t in tests if _test_app(t) == app]

        watch_covering = [
            t for t in app_tests
            if t.get("watch") and any(
                any(f.startswith(w) or f == w for w in t["watch"])
                for f in app_changed
            )
        ]

        all_covered = bool(watch_covering) and all(
            any(
                any(f.startswith(w) or f == w for w in (t.get("watch") or []))
                for t in watch_covering
            )
            for f in app_changed
        )

        if all_covered:
            for t in watch_covering:
                if t["id"] not in selected_ids:
                    selected_ids.append(t["id"])
        else:
            for t in app_tests:
                if t["id"] not in selected_ids:
                    selected_ids.append(t["id"])

    return selected_ids


def main():
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    # Log every call (next to this script, so the working directory does not matter)
    try:
        import datetime
        log = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "takes", "bob_hook_calls.log")
        with open(log, "a", encoding="utf-8") as fh:
            fh.write(f"{datetime.datetime.now():%H:%M:%S} cwd={os.getcwd()} stdin={raw[:600]}\n")
    except OSError:
        pass
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        sys.exit(0)

    # Bob 2.x sends tool_name/tool_input; the lifecycle-hooks docs say tool/input. Accept both.
    inp = data.get("tool_input") or data.get("input") or {}
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

    # Determine which files differ from HEAD (covers both staged and unstaged changes,
    # because Bob often runs "git add X; git commit" in one command and nothing is staged
    # yet when the hook fires — the dev server serves the working tree either way).
    changed = _diff_head_files()
    selected_ids = _select_test_ids(changed)

    if selected_ids is None:
        # No frontend files changed — nothing for Earshot to verify.
        sys.exit(0)

    print(f"earshot bob-hook: selected tests: {selected_ids}", file=sys.stderr)

    # Run only the selected tests.
    cmd = [VENV_PYTHON, HEAR_TESTS, "--ids", ",".join(selected_ids)]
    proc = subprocess.run(cmd, capture_output=True, **UTF8)
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
