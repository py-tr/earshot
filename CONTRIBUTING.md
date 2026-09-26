# Contributing to Earshot

## Check the tests without a screen reader (any OS)
```
pip install mcp==2.2.0
python earshot_mcp/hear_tests.py --replay
python -m unittest discover -s earshot_mcp/tests
```
Every test must pass on its stored fixed transcript and fail on every broken one in `evidence/<ID>/`.

## Add a finding and its hear-test
1. Add one line to `findings.md`: `ID | WCAG | component | key script | expected announcement | ear`. The key script is the keys from a start point, e.g. `page /flights, from top: Tab ×7`, with at most one `Tab ×N` after any typing. The expected announcement is the exact phrase NVDA should say.
2. In IBM Bob, run `/hear <ID>` in the Earshot mode. Bob fixes, verifies with NVDA, writes the test into `hear-tests.json` and commits through the gate. Or run `/earshot <page>` to sweep a page, triage the proposals and fix the accepted ones in one command.
3. Keep the stored transcripts: put the before/after takes in `evidence/<ID>/` so `--replay` covers the new test.

## The live gate (Windows, NVDA)
See the README's Setup section. `git config core.hooksPath .githooks` enables the pre-commit gate; `.bob/settings.json` adds the Bob lifecycle hooks. The gate replays every test with NVDA whenever app source is committed; tests for an app that is not running are skipped.
