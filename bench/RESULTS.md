# Benchmark: what standard automated accessibility checks catch, compared with Earshot

Measured 2026-09-25/26 on IBM's Galaxium Travels sample app and on TodoMVC's React example (upstream `ff43b02`, original components in `bench/baseline/todomvc/`). The "original" code is the repo's scaffold commit `0a3fb4d` (upstream `e4e18ae`); the "fixed" code is `HEAD` after Bob's `/hear` fixes.

| Finding (audit EAR-2026-09-001) | Strict React lint: eslint-plugin-jsx-a11y 6.10.2, `strict` | axe-core 4.13.0: WCAG 2.0–2.2 A/AA + best-practice, dialog open | Earshot: real NVDA 2026.2 via `listen()` |
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
| **F-09** typing in the Sign In dialog loses focus after one letter (regression from our own F-01 fix) | not flagged | not flagged (focus theft happens only while typing; a static scan never types) | heard ("N", then the dialog again), fixed, re-heard: "N, o, b, o, d, y", then "Email, edit, required" |
| **F-10** two flight links both named "Book" on /destinations/mars (found by `/earshot`) | not flagged | not flagged (measured 2026-09-26 with the labels removed: WCAG A/AA + best-practice, and again with AAA + experimental rules) | heard ("Book, link" twice), fixed, re-heard: "Book Earth to Mars, Jan 01, 2099, link" |
| **F-11** TodoMVC: todo checkboxes have no name (found by `/earshot`) | not flagged (lint on the original components in `bench/baseline/todomvc/`: only `no-autofocus` and a double-click handler) | **flagged**: `label` (critical) | heard ("check box, not checked"), fixed, re-heard: "Buy milk, check box, not checked" |
| **F-12** TodoMVC: Delete buttons `display: none` until mouse hover, so unreachable by keyboard (heard by a human) | not flagged | not flagged (hidden elements are skipped) | heard (Tab goes from the last checkbox to "All, link"), fixed, re-heard: "Delete Buy milk, button" |
| **F-13** Uptime Kuma: the logo `<object>` is a silent Tab stop (found by `/earshot` on a third app, a real product) | not measured (the React lint plugin does not apply to Vue) | **flagged**: `object-alt` (`axe_kuma_baseline.json`; gone after the fix, `axe_kuma_fixed.json`) | heard (silence), first fix (`aria-hidden` only) rejected by ear, fixed, re-heard: second Tab says "Status Pages, link" |
| **F-14** Uptime Kuma: the heartbeat chart is a second Tab stop inside every monitor link (found by `/earshot`) | not measured (Vue) | not flagged (the canvas has `role="img"`, so no nested-control rule fires) | heard ("graphic, clickable, link"), first fix rejected by ear (the link lost the heartbeat summary), fixed, re-heard. Human review then found the fix had removed the chart's Tab and arrow-key access on the Details and status pages (F-14b guard test), and the Vue compiler showed the follow-up's conditional handlers were never called; both fixed by Bob |

**Automated checks: 3½ of 15 findings flagged (lint 0 of the 13 on the two React apps, not run on Vue; axe-core 3½). Earshot: 15 of 15 verified by ear on three apps, 9 of them discovered by Bob's own sweeps, 1 (F-09) a regression Bob's own F-01 fix introduced, and 1 (F-12) heard by a human. 11 of the 15 were caught only by ear.**
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
