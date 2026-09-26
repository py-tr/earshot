"""Tests for server._normalize_keys — no NVDA, no browser, stdlib only."""
import importlib.util
import os
import sys
import unittest

# Load server.py directly by path, without importing the mcp package at module level.
# server.py itself imports mcp at the top level, so we must intercept the import.
_SERVER_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "server.py"
)


def _load_normalize_keys():
    """Import _normalize_keys from server.py, stubbing out the mcp dependency."""
    # Provide a minimal stub so 'from mcp.server.mcpserver import MCPServer' succeeds.
    import types
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

    sys.modules.setdefault("mcp", mcp_pkg)
    sys.modules.setdefault("mcp.server", mcp_server)
    sys.modules.setdefault("mcp.server.mcpserver", mcp_mcpserver)

    spec = importlib.util.spec_from_file_location("earshot_server_for_test", _SERVER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod._normalize_keys


_normalize_keys = _load_normalize_keys()


class TestNormalizeKeysFindings(unittest.TestCase):
    """Cases taken directly from the task specification."""

    def test_enter_tab6_stab_esc(self):
        # "Enter, Tab ×6, Shift+Tab, Escape" -> "ENTER,TAB*6,STAB,ESC"
        result = _normalize_keys("Enter, Tab ×6, Shift+Tab, Escape")
        self.assertEqual(result, "ENTER,TAB*6,STAB,ESC")

    def test_tab7_type_mars(self):
        # 'Tab ×7, Type "Mars"' -> 'TAB*7,TYPE=Mars'
        result = _normalize_keys('Tab ×7, Type "Mars"')
        self.assertEqual(result, "TAB*7,TYPE=Mars")


class TestNormalizeKeysDriverPassThrough(unittest.TestCase):
    """Driver-format strings must pass through unchanged."""

    def test_single_driver_token(self):
        self.assertEqual(_normalize_keys("ENTER"), "ENTER")

    def test_driver_token_with_repeat(self):
        self.assertEqual(_normalize_keys("TAB*6"), "TAB*6")

    def test_multiple_driver_tokens(self):
        self.assertEqual(_normalize_keys("ENTER,TAB*6,STAB,ESC"), "ENTER,TAB*6,STAB,ESC")

    def test_type_driver_token(self):
        self.assertEqual(_normalize_keys("TYPE=Mars"), "TYPE=Mars")

    def test_mixed_driver_tokens_with_type(self):
        result = _normalize_keys("TAB*7,TYPE=Mars")
        self.assertEqual(result, "TAB*7,TYPE=Mars")

    def test_all_driver_tokens(self):
        self.assertEqual(_normalize_keys("ENTER,TAB,STAB,ESC"), "ENTER,TAB,STAB,ESC")


class TestNormalizeKeysErrors(unittest.TestCase):
    """Unknown keys and forbidden Type text must raise ValueError."""

    def test_unknown_key_raises(self):
        with self.assertRaises(ValueError):
            _normalize_keys("Space")

    def test_unknown_key_with_repeat_raises(self):
        with self.assertRaises(ValueError):
            _normalize_keys("PageDown ×3")

    def test_type_text_with_comma_raises(self):
        # Commas are not in the allowed character class for Type text
        with self.assertRaises(ValueError):
            _normalize_keys('Type "Hello, world"')

    def test_type_text_with_brace_raises(self):
        with self.assertRaises(ValueError):
            _normalize_keys('Type "Hello{world}"')


class TestNormalizeKeysVariants(unittest.TestCase):
    """Additional normalisation variants and edge cases."""

    def test_enter_alone(self):
        self.assertEqual(_normalize_keys("Enter"), "ENTER")

    def test_tab_alone(self):
        self.assertEqual(_normalize_keys("Tab"), "TAB")

    def test_shift_tab(self):
        self.assertEqual(_normalize_keys("Shift+Tab"), "STAB")

    def test_escape_alias_esc(self):
        # lowercase 'esc' is also accepted
        self.assertEqual(_normalize_keys("Esc"), "ESC")

    def test_tab_xN_lowercase(self):
        self.assertEqual(_normalize_keys("Tab x3"), "TAB*3")

    def test_tab_star_repeat(self):
        self.assertEqual(_normalize_keys("Tab *4"), "TAB*4")

    def test_type_unquoted(self):
        self.assertEqual(_normalize_keys("Type Mars"), "TYPE=Mars")

    def test_type_quoted(self):
        self.assertEqual(_normalize_keys('Type "Mars"'), "TYPE=Mars")

    def test_multiple_tokens(self):
        result = _normalize_keys("Enter, Tab, Shift+Tab, Escape")
        self.assertEqual(result, "ENTER,TAB,STAB,ESC")


if __name__ == "__main__":
    unittest.main()
