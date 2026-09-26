"""Earshot regression gate — replays each verified finding and checks NVDA output."""
import argparse
import json
import os
import subprocess
import sys
import time

# ---------------------------------------------------------------------------
# Reuse server helpers without starting the MCP server
# ---------------------------------------------------------------------------
import importlib.util as _ilu

_SERVER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server.py")
_spec = _ilu.spec_from_file_location("earshot_server", _SERVER_PATH)
_server_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_server_mod)  # type: ignore[union-attr]

_normalize_keys = _server_mod._normalize_keys
_format_output = _server_mod._format_output
_HERE = _server_mod._HERE

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TESTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hear-tests.json")

_APP_SOURCE = {
    "galaxium": "galaxium/booking_system_frontend/src/",
    "todomvc": "todomvc/src/",
}
_TODOMVC_URL_PREFIX = "http://localhost:7002"


def _load_tests():
    with open(_TESTS_PATH, encoding="utf-8") as f:
        return json.load(f)


def _test_app(test: dict) -> str:
    """Return 'todomvc' if the test path starts with the TodoMVC URL, else 'galaxium'."""
    path = test.get("path", "")
    if path.startswith(_TODOMVC_URL_PREFIX):
        return "todomvc"
    return "galaxium"


def _staged_files() -> list[str]:
    """Return the list of staged file paths (relative to repo root)."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, text=True,
    )
    return result.stdout.splitlines()


def _staged_apps(staged: list[str]) -> set[str]:
    """Return the set of app names that have staged files under their source folder."""
    apps = set()
    for app, prefix in _APP_SOURCE.items():
        if any(f.startswith(prefix) for f in staged):
            apps.add(app)
    return apps


def _select_tests(tests: list[dict], staged: list[str]) -> tuple[list[dict], dict[str, str]]:
    """Select tests to run based on staged files.

    Returns (selected_tests, reasons) where reasons maps test id -> why it was selected.
    Rule: for each app with staged changes:
      - If every staged file of that app is covered by the watch list of at least one test,
        run only those watch-covering tests.
      - Otherwise run all tests for that app (safe default).
    """
    apps_with_changes = _staged_apps(staged)

    selected: list[dict] = []
    reasons: dict[str, str] = {}

    for app in apps_with_changes:
        app_prefix = _APP_SOURCE[app]
        app_staged = [f for f in staged if f.startswith(app_prefix)]
        app_tests = [t for t in tests if _test_app(t) == app]

        # Find tests whose watch list covers at least one staged file
        watch_covering = [
            t for t in app_tests
            if t.get("watch") and any(
                any(f.startswith(w) or f == w for w in t["watch"])
                for f in app_staged
            )
        ]

        # Check if every staged file is covered by at least one watch-covering test
        all_covered = bool(watch_covering) and all(
            any(
                any(f.startswith(w) or f == w for w in (t.get("watch") or []))
                for t in watch_covering
            )
            for f in app_staged
        )

        if all_covered:
            for t in watch_covering:
                selected.append(t)
                reasons[t["id"]] = f"watch match ({app})"
        else:
            for t in app_tests:
                selected.append(t)
                reasons[t["id"]] = f"all tests for {app} (safe default)"

    return selected, reasons


def _staged_touches_frontend() -> bool:
    """Return True if any staged file is under the frontend source tree."""
    return bool(_staged_apps(_staged_files()))


def _run_take(keys: str, start: str = "Select Seat Class", gap: float = 2.0, path: str | None = None) -> str:
    """Run a single take (driver + extract) and return formatted output."""
    label = "take_" + time.strftime("%Y%m%dT%H%M%S")

    takes_dir = os.environ.get(
        "EARSHOT_TAKES",
        os.path.join(os.path.dirname(_HERE), "takes"),
    )
    txt_path = os.path.join(takes_dir, f"{label}.txt")

    driver = os.path.join(_HERE, "driver.py")
    extract = os.path.join(_HERE, "extract.py")

    cmd = [sys.executable, driver, label, keys, str(gap), f"--start={start}"]
    if path is not None:
        cmd.append(f"--path={path}")
    driver_result = subprocess.run(
        cmd,
        capture_output=True, text=True, timeout=120,
    )

    import json as _json

    meta = None
    for _line in driver_result.stdout.splitlines():
        if _line.startswith("{"):
            try:
                meta = _json.loads(_line)
            except Exception:
                pass
            break

    if driver_result.returncode == 3:
        return "aborted: the take stalled and was stopped after 95 s"
    if driver_result.returncode != 0 or meta is None:
        err = (driver_result.stderr or "").strip().splitlines()[-1:] or ["no error output"]
        return f"aborted: driver failed (exit code {driver_result.returncode}): {err[0][:200]}"
    if meta.get("aborted"):
        return f"aborted: {meta['aborted']}"

    extract_result = subprocess.run(
        [sys.executable, extract, label, "listen", txt_path],
        capture_output=True, text=True, timeout=120,
    )
    if extract_result.returncode != 0:
        return f"aborted: extract failed: {extract_result.stderr.strip()}"

    return _format_output(txt_path, label)


def _said_lines(output: str) -> list[str]:
    """Extract the text after 'said: ' from each spoken line."""
    lines = []
    for line in output.splitlines():
        idx = line.find("said: ")
        if idx != -1:
            lines.append(line[idx + 6:])
    return lines


def _check(test: dict, output: str) -> tuple[bool, str]:
    """Return (passed, reason). reason is empty when passed."""
    said = _said_lines(output)
    joined = "\n".join(said)

    # Check expect phrases in order
    pos = 0
    for phrase in test.get("expect", []):
        found = False
        while pos < len(said):
            if phrase in said[pos]:
                pos += 1
                found = True
                break
            pos += 1
        if not found:
            return False, f"missing '{phrase}'"

    # Check forbid phrases
    for phrase in test.get("forbid", []):
        for line in said:
            if phrase in line:
                return False, f"forbidden '{phrase}' heard"

    return True, ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _replay() -> int:
    """Offline check, any OS, no NVDA: each test must PASS on its stored 'after' transcript
    and FAIL on its stored 'before' / rejected-fix transcripts (so it tells broken from fixed)."""
    import glob
    root = os.path.dirname(_TESTS_PATH)
    ok = True
    for test in _load_tests():
        d = os.path.join(root, "evidence", test["id"])
        def pick(*patterns):
            return sorted({f for p in patterns for f in glob.glob(os.path.join(d, p))})
        afters = pick("after*.txt", "ear_check*.txt")
        befores = pick("before*.txt", "*rejected*.txt", "*still_silent*.txt")
        passing = [os.path.basename(f) for f in afters if _check(test, _format_output(f, "replay"))[0]]
        caught = [os.path.basename(f) for f in befores if not _check(test, _format_output(f, "replay"))[0]]
        missed = [os.path.basename(f) for f in befores if os.path.basename(f) not in caught]
        good = bool(passing) and not missed
        ok &= good
        print(f"{'PASS' if good else 'FAIL'} {test['id']}: fixed transcript passes: {passing or 'NONE'}"
              f" | broken transcripts fail: {caught or '-'}" + (f" | NOT caught: {missed}" if missed else ""))
    return 0 if ok else 1


def main():
    # window titles and NVDA speech can contain any character; never crash on the Windows console encoding
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Earshot regression gate")
    parser.add_argument("--replay", action="store_true",
                        help="Offline, any OS: check the tests against the stored NVDA transcripts in evidence/")
    parser.add_argument("--staged", action="store_true",
                        help="Run only tests whose app has staged files; use watch lists to narrow further")
    parser.add_argument("--plan", action="store_true",
                        help="Print which tests would run and why, then exit 0 without listening")
    parser.add_argument("--only", metavar="ID",
                        help="Run only the test with this ID")
    args = parser.parse_args()

    if args.replay:
        sys.exit(_replay())

    tests = _load_tests()

    if args.staged:
        staged = _staged_files()
        if not _staged_apps(staged):
            print("earshot gate: no UI changes")
            sys.exit(0)
        tests, reasons = _select_tests(tests, staged)
    else:
        reasons = {}

    if args.only:
        tests = [t for t in tests if t["id"] == args.only]
        if not tests:
            print(f"No test with ID {args.only!r}")
            sys.exit(1)

    if args.plan:
        for t in tests:
            why = reasons.get(t["id"], "explicitly selected" if args.only else "all tests")
            print(f"WOULD RUN {t['id']}: {why}")
        sys.exit(0)

    any_failed = False
    could_not_listen = 0
    for test in tests:
        tid = test["id"]
        keys = _normalize_keys(test["key_script"])
        test_path = test.get("path")
        if test_path and test_path.startswith(("http://", "https://")):  # a second app: skip when it is not running
            import urllib.request
            try:
                urllib.request.urlopen(test_path, timeout=3)
            except Exception:
                print(f"SKIP {tid}: {test_path} is not running")
                continue
        test_start = test.get("start", "Select Seat Class")
        output = _run_take(keys, start=test_start, path=test_path)

        passed, reason = _check(test, output)
        if passed:
            print(f"PASS {tid}")
        else:
            any_failed = True
            said = _said_lines(output)
            if output.startswith("aborted"):
                reason = "could not listen (" + output + ")"
                could_not_listen += 1
            print(f"FAIL {tid}: {reason}")
            for line in said:
                print(f"  said: {line}")

    # exit 2: nothing could be heard (app down, focus stolen); exit 1: a real screen-reader regression
    sys.exit((2 if could_not_listen == len(tests) else 1) if any_failed else 0)


if __name__ == "__main__":
    main()
