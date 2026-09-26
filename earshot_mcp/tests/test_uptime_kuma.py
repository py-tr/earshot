"""Unit tests for Uptime Kuma wiring: _test_app, _staged_apps, _select_tests, bob_hook.

No NVDA, no browser, stdlib only.
"""
import importlib.util
import json
import os
import subprocess
import sys
import types
import unittest


# ---------------------------------------------------------------------------
# Stub mcp before loading hear_tests (which imports server.py which imports mcp)
# ---------------------------------------------------------------------------

def _ensure_mcp_stub():
    if "mcp" in sys.modules:
        return
    mcp_pkg = types.ModuleType("mcp")
    mcp_server = types.ModuleType("mcp.server")
    mcp_mcpserver = types.ModuleType("mcp.server.mcpserver")

    class _FakeMCPServer:
        def __init__(self, name):
            pass
        def tool(self, **kwargs):
            def decorator(fn):
                return fn
            return decorator
        def run(self, *a, **kw):
            pass

    mcp_mcpserver.MCPServer = _FakeMCPServer
    mcp_pkg.server = mcp_server
    mcp_server.mcpserver = mcp_mcpserver
    sys.modules["mcp"] = mcp_pkg
    sys.modules["mcp.server"] = mcp_server
    sys.modules["mcp.server.mcpserver"] = mcp_mcpserver


_ensure_mcp_stub()

_HEAR_TESTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hear_tests.py"
)
_spec = importlib.util.spec_from_file_location("hear_tests_uk", _HEAR_TESTS_PATH)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

_test_app = _mod._test_app
_staged_apps = _mod._staged_apps
_select_tests = _mod._select_tests

_BOB_HOOK = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bob_hook.py"
)

_UPTIME_KUMA_PREFIX = "uptime-kuma/src/"
_TODOMVC_PREFIX = "todomvc/src/"
_GALAXIUM_PREFIX = "galaxium/booking_system_frontend/src/"


# ---------------------------------------------------------------------------
# _test_app — Uptime Kuma URL detection
# ---------------------------------------------------------------------------

class TestTestAppUptimeKuma(unittest.TestCase):

    def test_uptime_kuma_root_url(self):
        self.assertEqual(_test_app({"path": "http://localhost:3000/"}), "uptime-kuma")

    def test_uptime_kuma_dashboard_url(self):
        self.assertEqual(_test_app({"path": "http://localhost:3000/dashboard"}), "uptime-kuma")

    def test_uptime_kuma_subpath(self):
        self.assertEqual(_test_app({"path": "http://localhost:3000/status/default"}), "uptime-kuma")

    def test_todomvc_still_detected(self):
        self.assertEqual(_test_app({"path": "http://localhost:7002/"}), "todomvc")

    def test_no_path_still_galaxium(self):
        self.assertEqual(_test_app({}), "galaxium")

    def test_relative_path_still_galaxium(self):
        self.assertEqual(_test_app({"path": "/flights"}), "galaxium")


# ---------------------------------------------------------------------------
# _staged_apps — uptime-kuma/src/ files trigger "uptime-kuma"
# ---------------------------------------------------------------------------

class TestStagedAppsUptimeKuma(unittest.TestCase):

    def test_uptime_kuma_staged(self):
        self.assertEqual(
            _staged_apps([f"{_UPTIME_KUMA_PREFIX}components/StatusPage.vue"]),
            {"uptime-kuma"},
        )

    def test_uptime_kuma_js_staged(self):
        self.assertEqual(_staged_apps([f"{_UPTIME_KUMA_PREFIX}main.js"]), {"uptime-kuma"})

    def test_uptime_kuma_scss_staged(self):
        self.assertEqual(_staged_apps([f"{_UPTIME_KUMA_PREFIX}style.scss"]), {"uptime-kuma"})

    def test_uptime_kuma_and_todomvc_staged_returns_both(self):
        apps = _staged_apps([
            f"{_UPTIME_KUMA_PREFIX}main.js",
            f"{_TODOMVC_PREFIX}App.jsx",
        ])
        self.assertEqual(apps, {"uptime-kuma", "todomvc"})

    def test_uptime_kuma_outside_src_not_counted(self):
        # e.g. uptime-kuma/data/ must not trigger uptime-kuma
        self.assertEqual(_staged_apps(["uptime-kuma/data/kuma.db"]), set())


# ---------------------------------------------------------------------------
# _select_tests — staged uptime-kuma/src/ selects only uptime-kuma tests
# ---------------------------------------------------------------------------

_UK_TEST = {
    "id": "UK-01",
    "path": "http://localhost:3000/dashboard",
    "key_script": "Tab",
    "expect": [],
}
_GALAXIUM_TEST = {
    "id": "F-01",
    "key_script": "Tab",
    "expect": [],
}
_TODOMVC_TEST = {
    "id": "F-11",
    "path": "http://localhost:7002/",
    "key_script": "Tab",
    "expect": [],
}
_ALL = [_UK_TEST, _GALAXIUM_TEST, _TODOMVC_TEST]


class TestSelectTestsUptimeKuma(unittest.TestCase):

    def test_uptime_kuma_staged_selects_only_uptime_kuma(self):
        selected, reasons = _select_tests(_ALL, [f"{_UPTIME_KUMA_PREFIX}main.js"])
        ids = [t["id"] for t in selected]
        self.assertIn("UK-01", ids)
        self.assertNotIn("F-01", ids)
        self.assertNotIn("F-11", ids)
        self.assertIn("safe default", reasons["UK-01"])

    def test_galaxium_staged_does_not_select_uptime_kuma(self):
        selected, _ = _select_tests(_ALL, [f"{_GALAXIUM_PREFIX}components/Modal.tsx"])
        ids = [t["id"] for t in selected]
        self.assertNotIn("UK-01", ids)

    def test_todomvc_staged_does_not_select_uptime_kuma(self):
        selected, _ = _select_tests(_ALL, [f"{_TODOMVC_PREFIX}App.jsx"])
        ids = [t["id"] for t in selected]
        self.assertNotIn("UK-01", ids)

    def test_uptime_kuma_and_todomvc_both_staged(self):
        selected, _ = _select_tests(_ALL, [
            f"{_UPTIME_KUMA_PREFIX}main.js",
            f"{_TODOMVC_PREFIX}App.jsx",
        ])
        ids = [t["id"] for t in selected]
        self.assertIn("UK-01", ids)
        self.assertIn("F-11", ids)
        self.assertNotIn("F-01", ids)


# ---------------------------------------------------------------------------
# bob_hook — uptime-kuma/src/ treated as a frontend change
# ---------------------------------------------------------------------------

def _run_hook(stdin_bytes: bytes) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, _BOB_HOOK],
        input=stdin_bytes,
        capture_output=True,
        timeout=15,
    )


class TestBobHookUptimeKuma(unittest.TestCase):

    def test_non_commit_command_always_exits_0(self):
        """Sanity: a non-commit command still exits 0 regardless of uptime-kuma."""
        payload = json.dumps({
            "tool_name": "execute_command",
            "tool_input": {"command": "echo hello"},
        }).encode()
        result = _run_hook(payload)
        self.assertEqual(result.returncode, 0)

    def test_commit_command_exits_0_without_local_env(self):
        """git commit exits 0 when local.env is absent (no NVDA setup on this machine)."""
        payload = json.dumps({
            "tool_name": "execute_command",
            "tool_input": {"command": "git commit -m 'test'"},
        }).encode()
        result = _run_hook(payload)
        # Without local.env the hook skips and exits 0
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
