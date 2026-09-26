"""Headline numbers must agree across the judged files (stdlib only, runs in CI).

The counts come from evidence/index.json; README.md and the report page must state them,
and must not contain the stale figures from earlier stages of the build.
"""
import json
import os
import re
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _read(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8") as f:
        return f.read()


class TestHeadlineDrift(unittest.TestCase):
    def setUp(self):
        self.index = json.loads(_read("evidence/index.json"))
        self.n = self.index["summary"]["findings"]
        self.readme = _read("README.md")
        self.report = _read("report/index.html")

    def test_index_counts_all_verified(self):
        self.assertEqual(self.index["summary"]["verified_by_ear"], self.n)

    def test_readme_states_headline(self):
        self.assertIn(f"**{self.n} of {self.n}**", self.readme)
        self.assertIn(f"**3½ of {self.n}**", self.readme)
        self.assertIn("**6 of Bob's own fixes were rejected by ear**", self.readme)
        self.assertIn("2 prompted regressions were refused", self.readme)

    def test_report_states_headline(self):
        self.assertIn(f"{self.n} / {self.n}", self.report)
        self.assertIn(f"3½ / {self.n}", self.report)

    def test_no_stale_figures(self):
        stale = [r"\b13 of 13\b", r"2½ of 13", r"\b13 / 13\b", r"2½ / 13", r"(?<!other )\btwo (real )?apps\b",
                 r"\b19 proposals\b", r"\b8 of 19\b", r"\b72 unit tests\b", r"about 32 Bobcoins"]
        for name, text in (("README.md", self.readme), ("report/index.html", self.report)):
            for pat in stale:
                with self.subTest(file=name, pattern=pat):
                    self.assertIsNone(re.search(pat, text), f"stale figure {pat!r} in {name}")


if __name__ == "__main__":
    unittest.main()
