"""Tests for hear_tests._check and _said_lines — no NVDA, no browser, stdlib only."""
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
_spec = importlib.util.spec_from_file_location("hear_tests_mod", _HEAR_TESTS_PATH)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

_check = _mod._check
_said_lines = _mod._said_lines


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_output(*phrases):
    """Build a fake _format_output string that contains the given spoken phrases."""
    lines = []
    for i, phrase in enumerate(phrases):
        lines.append(f"{i + 1:.2f}s  said: {phrase}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# _said_lines
# ---------------------------------------------------------------------------

class TestSaidLines(unittest.TestCase):

    def test_extracts_single_phrase(self):
        output = "1.00s  said: Sign In, dialog"
        self.assertEqual(_said_lines(output), ["Sign In, dialog"])

    def test_extracts_multiple_phrases(self):
        output = _make_output("Sign In, dialog", "Close modal, button")
        self.assertEqual(_said_lines(output), ["Sign In, dialog", "Close modal, button"])

    def test_ignores_non_said_lines(self):
        output = "1.00s  TAB\n2.00s  said: Hello\naudio: takes/foo.wav"
        self.assertEqual(_said_lines(output), ["Hello"])

    def test_empty_output(self):
        self.assertEqual(_said_lines(""), [])

    def test_no_said_lines(self):
        output = "1.00s  TAB\n2.00s  ENTER"
        self.assertEqual(_said_lines(output), [])


# ---------------------------------------------------------------------------
# _check — expected phrases must appear in order
# ---------------------------------------------------------------------------

class TestCheckExpectInOrder(unittest.TestCase):

    def test_single_phrase_found(self):
        output = _make_output("Sign In, dialog", "Close modal, button")
        test = {"expect": ["Sign In, dialog"]}
        passed, reason = _check(test, output)
        self.assertTrue(passed)
        self.assertEqual(reason, "")

    def test_multiple_phrases_found_in_order(self):
        output = _make_output("Sign In, dialog", "Close modal, button")
        test = {"expect": ["Sign In, dialog", "Close modal, button"]}
        passed, reason = _check(test, output)
        self.assertTrue(passed)

    def test_phrases_found_out_of_order_fails(self):
        # expect A then B, but output has B then A
        output = _make_output("Close modal, button", "Sign In, dialog")
        test = {"expect": ["Sign In, dialog", "Close modal, button"]}
        passed, reason = _check(test, output)
        self.assertFalse(passed)

    def test_missing_phrase_fails(self):
        output = _make_output("Sign In, dialog")
        test = {"expect": ["Sign In, dialog", "Close modal, button"]}
        passed, reason = _check(test, output)
        self.assertFalse(passed)
        self.assertIn("Close modal, button", reason)

    def test_no_expect_passes(self):
        output = _make_output("anything")
        test = {"expect": []}
        passed, reason = _check(test, output)
        self.assertTrue(passed)

    def test_empty_output_with_expect_fails(self):
        test = {"expect": ["something"]}
        passed, reason = _check(test, "")
        self.assertFalse(passed)
        self.assertIn("something", reason)

    def test_substring_match(self):
        # _check uses `phrase in said[pos]`, so substring matching is intentional
        output = _make_output("Sign In, dialog")
        test = {"expect": ["Sign In"]}
        passed, _ = _check(test, output)
        self.assertTrue(passed)


# ---------------------------------------------------------------------------
# _check — forbidden phrases
# ---------------------------------------------------------------------------

class TestCheckForbid(unittest.TestCase):

    def test_forbidden_phrase_fails(self):
        output = _make_output("github.com, link")
        test = {"expect": [], "forbid": ["github.com"]}
        passed, reason = _check(test, output)
        self.assertFalse(passed)
        self.assertIn("github.com", reason)

    def test_forbidden_phrase_absent_passes(self):
        output = _make_output("GitHub, link")
        test = {"expect": [], "forbid": ["github.com"]}
        passed, reason = _check(test, output)
        self.assertTrue(passed)
        self.assertEqual(reason, "")

    def test_forbidden_substring_match(self):
        output = _make_output("some github.com reference")
        test = {"expect": [], "forbid": ["github.com"]}
        passed, reason = _check(test, output)
        self.assertFalse(passed)

    def test_both_expect_and_forbid_pass(self):
        output = _make_output("Sign In, dialog", "Close modal, button")
        test = {"expect": ["Sign In, dialog"], "forbid": ["github.com"]}
        passed, _ = _check(test, output)
        self.assertTrue(passed)

    def test_expect_passes_but_forbid_fails(self):
        output = _make_output("Sign In, dialog", "github.com, link")
        test = {"expect": ["Sign In, dialog"], "forbid": ["github.com"]}
        passed, reason = _check(test, output)
        self.assertFalse(passed)


if __name__ == "__main__":
    unittest.main()
