"""Tests for bob_hook.py run as a subprocess — no NVDA, no browser, stdlib only."""
import json
import os
import subprocess
import sys
import unittest

_BOB_HOOK = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bob_hook.py"
)


def _run_hook(stdin_bytes: bytes) -> subprocess.CompletedProcess:
    """Run bob_hook.py as a subprocess with the given stdin bytes."""
    return subprocess.run(
        [sys.executable, _BOB_HOOK],
        input=stdin_bytes,
        capture_output=True,
        timeout=15,
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
