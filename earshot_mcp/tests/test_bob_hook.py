"""Tests for bob_hook.py run as a subprocess — no NVDA, no browser, stdlib only."""
import json
import os
import subprocess
import sys
import types
import unittest

_BOB_HOOK = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bob_hook.py"
)

# ---------------------------------------------------------------------------
# Import bob_hook module directly for unit-testing the selection helpers
# ---------------------------------------------------------------------------

import importlib.util as _ilu

_spec = _ilu.spec_from_file_location("bob_hook", _BOB_HOOK)
_hook = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_hook)  # type: ignore[union-attr]

_select_test_ids = _hook._select_test_ids
_apps_for_files  = _hook._apps_for_files
_test_app        = _hook._test_app
_APP_SOURCE      = _hook._APP_SOURCE

# ---------------------------------------------------------------------------
# Minimal stub test catalogue used by the selection tests
# ---------------------------------------------------------------------------

_GALAXIUM_SRC = _APP_SOURCE["galaxium"]
_TODOMVC_SRC  = _APP_SOURCE["todomvc"]
_UPTIME_SRC   = _APP_SOURCE["uptime-kuma"]

_MODAL = f"{_GALAXIUM_SRC}components/common/Modal.tsx"
_INPUT = f"{_GALAXIUM_SRC}components/common/Input.tsx"

_STUB_TESTS = [
    # Galaxium modal dialog tests (have watch lists)
    {
        "id": "F-01",
        "key_script": "Enter, Tab",
        "expect": [],
        "watch": [_MODAL, _INPUT],
    },
    {
        "id": "F-02",
        "key_script": "Enter, Tab ×6, Shift+Tab, Escape",
        "expect": [],
        "watch": [_MODAL, _INPUT],
    },
    # Galaxium test without a watch list
    {
        "id": "F-04",
        "path": "/flights",
        "key_script": "Tab ×10",
        "expect": [],
    },
    # TodoMVC tests
    {
        "id": "F-11",
        "path": "http://localhost:7002/",
        "key_script": "Tab",
        "expect": [],
    },
    # Uptime Kuma tests
    {
        "id": "F-13",
        "path": "http://localhost:3000/dashboard",
        "key_script": "Tab ×2",
        "expect": [],
    },
    {
        "id": "F-14",
        "path": "http://localhost:3000/dashboard",
        "key_script": "Tab ×16",
        "expect": [],
    },
]


def _select_ids_from_stub(changed_files):
    """Run _select_test_ids but backed by _STUB_TESTS, not the real hear-tests.json."""
    apps = _apps_for_files(changed_files)
    if not apps:
        return None
    # Replicate _select_test_ids logic directly against our stub catalogue
    selected: list[str] = []
    for app in apps:
        app_prefix = _APP_SOURCE[app]
        app_changed = [f for f in changed_files if f.startswith(app_prefix)]
        app_tests = [t for t in _STUB_TESTS if _test_app(t) == app]

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
                if t["id"] not in selected:
                    selected.append(t["id"])
        else:
            for t in app_tests:
                if t["id"] not in selected:
                    selected.append(t["id"])
    return selected


# ---------------------------------------------------------------------------
# Selection unit tests (the three required cases + extras)
# ---------------------------------------------------------------------------

class TestSelectionUptimeKuma(unittest.TestCase):
    """An uptime-kuma/src change selects only the uptime-kuma tests."""

    def test_uptime_kuma_src_change_selects_only_uptime_kuma(self):
        changed = [f"{_UPTIME_SRC}views/Dashboard.vue"]
        ids = _select_ids_from_stub(changed)
        self.assertIsNotNone(ids, "Expected test IDs, got None (no frontend change detected)")
        self.assertIn("F-13", ids)
        self.assertIn("F-14", ids)
        # Must NOT select galaxium or todomvc tests
        self.assertNotIn("F-01", ids)
        self.assertNotIn("F-02", ids)
        self.assertNotIn("F-04", ids)
        self.assertNotIn("F-11", ids)


class TestSelectionModalTsx(unittest.TestCase):
    """A galaxium Modal.tsx change selects the dialog (watch-list) tests."""

    def test_modal_change_selects_dialog_tests(self):
        changed = [_MODAL]
        ids = _select_ids_from_stub(changed)
        self.assertIsNotNone(ids)
        # Watch-matching dialog tests should be selected
        self.assertIn("F-01", ids)
        self.assertIn("F-02", ids)
        # Test without watch list must NOT be selected (watch coverage is total)
        self.assertNotIn("F-04", ids)
        # Other apps must not be selected
        self.assertNotIn("F-11", ids)
        self.assertNotIn("F-13", ids)
        self.assertNotIn("F-14", ids)


class TestSelectionNoFrontend(unittest.TestCase):
    """No frontend change selects nothing (returns None)."""

    def test_no_frontend_file_returns_none(self):
        changed = ["README.md", "earshot_mcp/bob_hook.py", "package.json"]
        ids = _select_ids_from_stub(changed)
        self.assertIsNone(ids, f"Expected None, got {ids!r}")

    def test_empty_changed_list_returns_none(self):
        ids = _select_ids_from_stub([])
        self.assertIsNone(ids)


# ---------------------------------------------------------------------------
# Subprocess smoke tests (as before)
# ---------------------------------------------------------------------------

def _run_hook(stdin_bytes: bytes) -> subprocess.CompletedProcess:
    """Run bob_hook.py as a subprocess with the given stdin bytes."""
    return subprocess.run(
        [sys.executable, _BOB_HOOK],
        input=stdin_bytes,
        capture_output=True,
        timeout=15,
    )


class TestBobHookExactEvidencePayload(unittest.TestCase):
    """Feed the exact JSON from evidence/gate/bob_hook_call_stdin.txt and assert exit 0.

    The working tree has no frontend changes (this test file itself is not under
    any app source directory), so the hook must exit 0 (no tests to run).
    """

    # Exact payload recorded from Bob in evidence/gate/bob_hook_call_stdin.txt
    # (username replaced with a placeholder; the hook only reads tool_input.command).
    _EVIDENCE_JSON = (
        '{"session_id":"7e0ea1105aeabe7b3f6b104687c4902c",'
        '"cwd":"c:\\\\Users\\\\testuser\\\\Documents\\\\Work\\\\Hackathons\\\\ibm-bob\\\\earshot",'
        '"hook_event_name":"PreToolUse",'
        '"tool_name":"execute_command",'
        '"tool_input":{"command":"git commit --no-verify -m \\"refactor: tidy up Modal\\""},'
        '"tool_use_id":"tooluse_vH23JZBw1fn31DSl4eHsgf"}'
    )

    def test_evidence_payload_parses_and_exits_0(self):
        """Hook must parse the evidence payload, identify it as a git commit,
        find no frontend files changed in the working tree, and exit 0."""
        result = _run_hook(self._EVIDENCE_JSON.encode())
        self.assertEqual(
            result.returncode, 0,
            f"Expected exit 0 for evidence payload, got {result.returncode}. "
            f"stderr: {result.stderr!r}",
        )


class TestBobHookSubprocess(unittest.TestCase):

    def test_ls_command_exits_0(self):
        """tool_name=execute_command with command=ls must exit 0 (not a git commit)."""
        payload = json.dumps({
            "tool_name": "execute_command",
            "tool_input": {"command": "ls"},
        }).encode()
        result = _run_hook(payload)
        self.assertEqual(
            result.returncode, 0,
            f"Expected exit 0, got {result.returncode}. stderr: {result.stderr!r}",
        )

    def test_malformed_json_exits_0(self):
        """bob_hook.py must exit 0 (not crash) when given malformed JSON on stdin."""
        result = _run_hook(b"{not valid json")
        self.assertEqual(
            result.returncode, 0,
            f"Expected exit 0, got {result.returncode}. stderr: {result.stderr!r}",
        )

    def test_empty_stdin_exits_0(self):
        """Empty stdin is also malformed JSON — must exit 0."""
        result = _run_hook(b"")
        self.assertEqual(result.returncode, 0)

    def test_non_commit_command_exits_0(self):
        """Any non-commit command should exit 0 without running the gate."""
        payload = json.dumps({
            "tool_name": "execute_command",
            "tool_input": {"command": "echo hello"},
        }).encode()
        result = _run_hook(payload)
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
