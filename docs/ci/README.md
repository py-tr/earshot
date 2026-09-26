# Earshot in CI

- **`.github/workflows/check.yml` (runs on every push):** GitHub's Linux runners replay every hear-test against the stored NVDA transcripts and run the 94 unit tests. No screen reader needed; it proves the tests still tell broken from fixed.
- **`listening-gate.yml` (template, not run by us):** the full gate with real NVDA on a self-hosted Windows runner or VM. On a pull request it replays every hear-test by ear; about 9 minutes for 13 tests. Until then, the same gate runs locally as a git pre-commit hook and a Bob lifecycle hook.
