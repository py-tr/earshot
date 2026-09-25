# Benchmark: what standard automated accessibility checks catch, compared with Earshot

Measured 2026-09-25 on IBM's Galaxium Travels sample app. The "original" code is the repo's scaffold commit `0a3fb4d` (upstream `e4e18ae`); the "fixed" code is `HEAD` after Bob's `/hear` fixes.

| Finding (audit EAR-2026-09-001 v1.1) | Strict React lint: eslint-plugin-jsx-a11y 6.10.2, `strict` | axe-core 4.13.0: WCAG 2.0–2.2 A/AA + best-practice, dialog open | Earshot: real NVDA 2026.2 via `listen()` |
|---|---|---|---|
| **F-01** Sign In dialog silent: no name, focus not moved in | not flagged | **half**: `aria-dialog-name` (the name only; focus is not checked) | heard, fixed, re-heard: "Sign In, dialog" |
| **F-02** Tab escapes the open dialog; focus lost on close | not flagged | not flagged | heard ("github.com, link"), first fix rejected, fixed, re-heard |
| **F-03** fields announced by placeholder ("John Doe, edit") | not flagged (the label text is a variable, so the rule cannot see it) | not flagged (axe accepts a placeholder as the field name) | heard, fixed, re-heard: "Name, edit" |

**Automated checks: 1 of 3 findings flagged, and only half of that one. Earshot: 3 of 3 verified by ear.**

## The name-only fix passes axe and still fails blind users

Bob's first F-01 attempt added only a dialog name (`aria-labelledby`; diff in `evidence/F-01/name_only_fix.diff`).

- **axe-core** on that exact version reports **no dialog violation**: `aria-dialog-name` is gone (`bench/axe_nameonly.json`).
- **NVDA** on the same version, in Bob's own `listen()` take, gives: Enter → **silence**; Tab → "Moon, link, heading, level 3", read from the page behind the dialog. See `evidence/F-01/name_only_fix_still_silent_bob_listen.txt` / `.wav`.

The checker is satisfied, and the user still cannot find the dialog. Earshot rejected that fix; axe would have accepted it.

## What the automated tools find that Earshot does not

Stated for fairness: they are complementary. axe also flags, on both versions, **22 colour-contrast failures**, an **unnamed footer link** (github.com), **heading-order** issues, and the starfield **canvas outside landmarks**. Lint flags **8 unassociated labels in the flight filters**. None of those is an audit finding here; they are candidates for the next audit.

## Reproduce

```
cd bench && npm install                      # eslint, eslint-plugin-jsx-a11y, typescript-eslint, axe-core
# lint: export the two versions, then lint each
git -C .. archive 0a3fb4d galaxium/booking_system_frontend/src | tar -x -C baseline
npx eslint --no-config-lookup -c eslint.config.js baseline/galaxium/booking_system_frontend/src
# axe: serve each version (vite), then
python axe_run.py http://localhost:<port> axe_<name>.json
```

Raw outputs: `lint_baseline.json`, `lint_fixed.json`, `axe_baseline.json`, `axe_nameonly.json`, `axe_fixed.json`.
