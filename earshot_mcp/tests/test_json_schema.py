"""Tests for hear-tests.json schema and consistency — no NVDA, no browser, stdlib only."""
import importlib.util
import json
import os
import re
import sys
import types
import unittest

# ---------------------------------------------------------------------------
# Stub mcp so we can load server.py (for _normalize_keys)
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

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_HEAR_TESTS_JSON = os.path.join(_ROOT, "hear-tests.json")
_FINDINGS_MD = os.path.join(_ROOT, "findings.md")

_SERVER_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "server.py")
_spec = importlib.util.spec_from_file_location("earshot_server_schema_test", _SERVER_PATH)
_server_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_server_mod)
_normalize_keys = _server_mod._normalize_keys

# ---------------------------------------------------------------------------
# Load the data once
# ---------------------------------------------------------------------------

with open(_HEAR_TESTS_JSON, encoding="utf-8") as _f:
    _TESTS = json.load(_f)

# Extract IDs from findings.md: any token matching ^[A-Z]-\d+ (optionally a lowercase suffix,
# e.g. F-14b for a regression guard of F-14) at the start of a line
with open(_FINDINGS_MD, encoding="utf-8") as _f:
    _findings_content = _f.read()
_FINDINGS_IDS = set(re.findall(r"^([A-Z]-\d+[a-z]?)\s*\|", _findings_content, re.MULTILINE))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestHearTestsJson(unittest.TestCase):

    def test_valid_json_and_is_list(self):
        # File already parsed into _TESTS; verify it is a non-empty list
        self.assertIsInstance(_TESTS, list)
        self.assertGreater(len(_TESTS), 0)

    def test_every_test_has_id(self):
        for i, test in enumerate(_TESTS):
            with self.subTest(index=i):
                self.assertIn("id", test, f"Test at index {i} is missing 'id'")
                self.assertIsInstance(test["id"], str)
                self.assertTrue(test["id"].strip(), f"Test at index {i} has empty 'id'")

    def test_every_test_has_key_script(self):
        for test in _TESTS:
            with self.subTest(id=test.get("id", "?")):
                self.assertIn("key_script", test)
                self.assertIsInstance(test["key_script"], str)
                self.assertTrue(test["key_script"].strip())

    def test_every_test_has_expect(self):
        for test in _TESTS:
            with self.subTest(id=test.get("id", "?")):
                self.assertIn("expect", test)
                self.assertIsInstance(test["expect"], list)

    def test_every_key_script_normalizes(self):
        """Every key_script must not raise ValueError when normalized."""
        for test in _TESTS:
            with self.subTest(id=test.get("id", "?")):
                try:
                    result = _normalize_keys(test["key_script"])
                    self.assertIsInstance(result, str)
                    self.assertTrue(result.strip())
                except ValueError as exc:
                    self.fail(
                        f"Test {test['id']!r}: _normalize_keys raised ValueError: {exc}"
                    )

    def test_every_id_exists_in_findings_md(self):
        """Every test id must appear in findings.md."""
        for test in _TESTS:
            with self.subTest(id=test["id"]):
                self.assertIn(
                    test["id"],
                    _FINDINGS_IDS,
                    f"ID {test['id']!r} not found in findings.md",
                )

    def test_no_duplicate_ids(self):
        ids = [t["id"] for t in _TESTS]
        self.assertEqual(len(ids), len(set(ids)), f"Duplicate IDs found: {ids}")


if __name__ == "__main__":
    unittest.main()
