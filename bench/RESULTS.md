# Benchmark: what standard automated accessibility checks catch, compared with Earshot

Measured 2026-09-25 on IBM's Galaxium Travels sample app. The "original" code is the repo's scaffold commit `0a3fb4d` (upstream `e4e18ae`); the "fixed" code is `HEAD` after Bob's `/hear` fixes.

| Finding (audit EAR-2026-09-001 v1.1) | Strict React lint: eslint-plugin-jsx-a11y 6.10.2, `strict` | axe-core 4.13.0: WCAG 2.0–2.2 A/AA + best-practice, dialog open | Earshot: real NVDA 2026.2 via `listen()` |
|---|---|---|---|
| **F-01** Sign In dialog silent: no name, focus not moved in | not flagged | **half**: `aria-dialog-name` (the name only; focus is not checked) | heard, fixed, re-heard: "Sign In, dialog" |
| **F-02** Tab escapes the open dialog; focus lost on close | not flagged | not flagged | heard ("github.com, link"), first fix rejected, fixed, re-heard |
| **F-03** fields announced by placeholder ("John Doe, edit") | not flagged (the label text is a variable, so the rule cannot see it) | not flagged (axe accepts a placeholder as the field name) | heard, fixed, re-heard: "Name, edit" |
| **F-04** 9 booking buttons all "Select Seat Class" (found by Bob's /sweep) | not flagged | not flagged (no rule for identical button names) | heard, first fix rejected (Button dropped aria-label), fixed, re-heard: "Select Seat Class, Earth to Mars" |
| **F-05** no skip link (found by Bob's /sweep) | not flagged | not flagged (`bypass` passes because the page has headings and landmarks) | heard, fixed, re-heard: "Skip to main content, same page, link" |
| **F-06** search field named only by its placeholder (found by Bob's /sweep) | not flagged | not flagged (`label` accepts a placeholder as the name) | heard, fixed, re-heard: "Search flights, edit" |
| **F-07** a button nested inside a link: one control, two Tab stops, in 3 places on / (found by Bob's /sweep of the Home page) | not flagged | not flagged (on /, axe reports only `link-name` and `region`) | heard ("Book a Flight, button, link" twice), first fix rejected (`tabIndex=-1` on the inner button: still "button, link"), fixed, re-heard: "Book a Flight, link" once |
| **F-08** footer GitHub icon link has no name (found by Bob's /sweep of the Home page) | not flagged | **flagged**: `link-name` | heard ("github.com, link"), fixed, re-heard: "GitHub, link" |
| **N-02** result count not announced while typing (audit; testable by ear since `listen()` can type) | not flagged | not flagged (a missing status message cannot be seen in a static scan) | heard (typed letters echoed, then silence), fixed, re-heard: "Showing 4 flights" |

**Automated checks: 1½ of 9 findings flagged (lint 0, axe-core 1½). Earshot: 9 of 9 verified by ear, 5 of them discovered by Bob's own /sweep. 7 of the 9 were caught only by ear.**
(F-04..F-06 were measured on the same original-code scans, `axe_baseline.json` and `lint_baseline.json`, of /flights. F-07, F-08 and N-02 were measured on 2026-09-26: lint on the original `Home.tsx`, `Header.tsx`, `Footer.tsx` and `Flights.tsx` in `bench/baseline/` (no messages), axe-core 4.13 on / before the F-07 fix. N-01, the starfield pause, needs a human eye and is not counted.)

## The name-only fix passes axe and still fails blind users

Bob's first F-01 attempt added only a dialog name (`aria-labelledby`; diff in `evidence/F-01/name_only_fix.diff`).

- **axe-core** on that exact version reports **no dialog violation**: `aria-dialog-name` is gone (`bench/axe_nameonly.json`).
- **NVDA** on the same version, in Bob's own `listen()` take, gives: Enter → **silence**; Tab → "Moon, link, heading, level 3", read from the page behind the dialog. See `evidence/F-01/name_only_fix_still_silent_bob_listen.txt` / `.wav`.

The checker is satisfied, and the user still cannot find the dialog. Earshot rejected that fix; axe would have accepted it.

## What the automated tools find that Earshot does not

Stated for fairness: they are complementary. axe also flags, on both versions, **22 colour-contrast failures**, **heading-order** issues, and the starfield **canvas outside landmarks**. Lint flags **8 unassociated labels in the flight filters**. None of those is an audit finding here; they are candidates for the next audit.

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
