"""Unit tests for hear_tests selection logic (_test_app, _staged_apps, _select_tests).

No NVDA, no browser, stdlib only.
"""
import importlib.util
import os
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
_spec = importlib.util.spec_from_file_location("hear_tests_sel", _HEAR_TESTS_PATH)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

_test_app = _mod._test_app
_staged_apps = _mod._staged_apps
_select_tests = _mod._select_tests


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_GALAXIUM_PREFIX = "galaxium/booking_system_frontend/src/"
_TODOMVC_PREFIX = "todomvc/src/"
_MODAL = f"{_GALAXIUM_PREFIX}components/common/Modal.tsx"
_INPUT = f"{_GALAXIUM_PREFIX}components/common/Input.tsx"
_OTHER = f"{_GALAXIUM_PREFIX}components/flights/FlightCard.tsx"

_WATCH_LIST = [_MODAL, _INPUT]

# Minimal test entries
_GALAXIUM_TEST_WATCH = {"id": "F-01", "key_script": "Enter", "expect": [], "watch": _WATCH_LIST}
_GALAXIUM_TEST_NO_WATCH = {"id": "F-04", "path": "/flights", "key_script": "Tab", "expect": []}
_TODOMVC_TEST = {"id": "F-11", "path": "http://localhost:7002/", "key_script": "Tab", "expect": []}

ALL_TESTS = [_GALAXIUM_TEST_WATCH, _GALAXIUM_TEST_NO_WATCH, _TODOMVC_TEST]


# ---------------------------------------------------------------------------
# _test_app
# ---------------------------------------------------------------------------

class TestTestApp(unittest.TestCase):

    def test_no_path_is_galaxium(self):
        self.assertEqual(_test_app({}), "galaxium")

    def test_relative_path_is_galaxium(self):
        self.assertEqual(_test_app({"path": "/flights"}), "galaxium")

    def test_todomvc_url(self):
        self.assertEqual(_test_app({"path": "http://localhost:7002/"}), "todomvc")

    def test_todomvc_url_subpath(self):
        self.assertEqual(_test_app({"path": "http://localhost:7002/todos"}), "todomvc")

    def test_other_http_url_is_uptime_kuma(self):
        self.assertEqual(_test_app({"path": "http://localhost:3000/"}), "uptime-kuma")


# ---------------------------------------------------------------------------
# _staged_apps
# ---------------------------------------------------------------------------

class TestStagedApps(unittest.TestCase):

    def test_empty_staged_returns_empty(self):
        self.assertEqual(_staged_apps([]), set())

    def test_galaxium_staged(self):
        self.assertEqual(_staged_apps([_MODAL]), {"galaxium"})

    def test_todomvc_staged(self):
        self.assertEqual(_staged_apps([f"{_TODOMVC_PREFIX}App.tsx"]), {"todomvc"})

    def test_both_apps_staged(self):
        apps = _staged_apps([_MODAL, f"{_TODOMVC_PREFIX}App.tsx"])
        self.assertEqual(apps, {"galaxium", "todomvc"})

    def test_unrelated_file_ignored(self):
        self.assertEqual(_staged_apps(["README.md", "package.json"]), set())

    def test_prefix_boundary_respected(self):
        # A file starting with galaxium/ but NOT under src/ must not count
        self.assertEqual(_staged_apps(["galaxium/booking_system_frontend/README.md"]), set())


# ---------------------------------------------------------------------------
# _select_tests — no staged changes
# ---------------------------------------------------------------------------

class TestSelectTestsNoChanges(unittest.TestCase):

    def test_no_staged_returns_empty(self):
        selected, reasons = _select_tests(ALL_TESTS, [])
        self.assertEqual(selected, [])
        self.assertEqual(reasons, {})


# ---------------------------------------------------------------------------
# _select_tests — watch list narrows selection
# ---------------------------------------------------------------------------

class TestSelectTestsWatchNarrows(unittest.TestCase):

    def test_modal_only_staged_selects_watch_tests(self):
        """Only Modal.tsx staged → all staged files covered by watch list → watch tests only."""
        selected, reasons = _select_tests(ALL_TESTS, [_MODAL])
        ids = [t["id"] for t in selected]
        self.assertIn("F-01", ids)
        self.assertNotIn("F-04", ids)  # no watch list, safe default only if needed
        self.assertNotIn("F-11", ids)  # todomvc app not staged
        self.assertEqual(reasons["F-01"], "watch match (galaxium)")

    def test_input_only_staged_selects_watch_tests(self):
        """Only Input.tsx staged → watch tests cover it."""
        selected, reasons = _select_tests(ALL_TESTS, [_INPUT])
        ids = [t["id"] for t in selected]
        self.assertIn("F-01", ids)
        self.assertNotIn("F-04", ids)

    def test_both_modal_and_input_staged_selects_watch_tests(self):
        """Both watched files staged → still all covered by watch list."""
        selected, reasons = _select_tests(ALL_TESTS, [_MODAL, _INPUT])
        ids = [t["id"] for t in selected]
        self.assertIn("F-01", ids)
        self.assertNotIn("F-04", ids)

    def test_multiple_watch_tests(self):
        """Multiple tests sharing the same watch list are all selected."""
        t2 = {"id": "F-02", "key_script": "Enter", "expect": [], "watch": _WATCH_LIST}
        tests = [_GALAXIUM_TEST_WATCH, t2, _GALAXIUM_TEST_NO_WATCH]
        selected, reasons = _select_tests(tests, [_MODAL])
        ids = [t["id"] for t in selected]
        self.assertIn("F-01", ids)
        self.assertIn("F-02", ids)
        self.assertNotIn("F-04", ids)


# ---------------------------------------------------------------------------
# _select_tests — safe default (unmatched file → all app tests)
# ---------------------------------------------------------------------------

class TestSelectTestsSafeDefault(unittest.TestCase):

    def test_unmatched_file_triggers_all_galaxium_tests(self):
        """A staged file NOT covered by any watch list → run all galaxium tests."""
        selected, reasons = _select_tests(ALL_TESTS, [_OTHER])
        ids = [t["id"] for t in selected]
        self.assertIn("F-01", ids)
        self.assertIn("F-04", ids)
        self.assertNotIn("F-11", ids)
        for tid in ids:
            self.assertIn("safe default", reasons[tid])

    def test_mixed_covered_and_uncovered_triggers_all(self):
        """Modal.tsx + FlightCard.tsx staged → FlightCard not covered → safe default."""
        selected, reasons = _select_tests(ALL_TESTS, [_MODAL, _OTHER])
        ids = [t["id"] for t in selected]
        self.assertIn("F-01", ids)
        self.assertIn("F-04", ids)

    def test_todomvc_staged_without_watch_triggers_all_todomvc(self):
        """Staged todomvc file with no watch tests → run all todomvc tests."""
        selected, reasons = _select_tests(ALL_TESTS, [f"{_TODOMVC_PREFIX}App.tsx"])
        ids = [t["id"] for t in selected]
        self.assertIn("F-11", ids)
        self.assertNotIn("F-01", ids)
        self.assertNotIn("F-04", ids)


# ---------------------------------------------------------------------------
# _select_tests — app isolation
# ---------------------------------------------------------------------------

class TestSelectTestsAppIsolation(unittest.TestCase):

    def test_galaxium_change_does_not_select_todomvc(self):
        selected, _ = _select_tests(ALL_TESTS, [_MODAL])
        for t in selected:
            self.assertNotEqual(_test_app(t), "todomvc")

    def test_todomvc_change_does_not_select_galaxium(self):
        selected, _ = _select_tests(ALL_TESTS, [f"{_TODOMVC_PREFIX}App.tsx"])
        for t in selected:
            self.assertNotEqual(_test_app(t), "galaxium")

    def test_both_apps_staged_selects_from_both(self):
        selected, _ = _select_tests(ALL_TESTS, [_MODAL, f"{_TODOMVC_PREFIX}App.tsx"])
        apps = {_test_app(t) for t in selected}
        self.assertIn("galaxium", apps)
        self.assertIn("todomvc", apps)


if __name__ == "__main__":
    unittest.main()
