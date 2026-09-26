"""Tests for hear_tests.py --replay flag — no NVDA, no browser, stdlib only."""
import os
import subprocess
import sys
import unittest

_HEAR_TESTS_PY = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hear_tests.py"
)


class TestHearTestsReplay(unittest.TestCase):

    def test_replay_flag_exits_0(self):
        """hear_tests.py --replay must exit 0 (all stored transcripts check out)."""
        result = subprocess.run(
            [sys.executable, _HEAR_TESTS_PY, "--replay"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"--replay exited {result.returncode}.\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
