# Human triage of the headless Bob Shell sweep of /destinations/earth (2026-09-26 21:42 CEST)

Run from the terminal, no IDE: `bob run --mode earshot-sweep --max-cost 1.5 "Sweep /destinations/earth. This is an unattended run: do not ask the user anything; write the sweep file and finish."` (Bob Shell 2.0.5, 0.31 Bobcoins, 2 minutes, two parallel explore subagents). NVDA transcript: `evidence/headless/sweep_earth_listen.txt`.

| ID | Decision | Reason |
|---|---|---|
| S-01 | reject | "GitHub, link" is an adequate name for a link to GitHub (the F-08 fix). A longer name would be nicer, not required. |

Result: **1 proposal, 0 accepted** on a page that had already been fixed through F-10 (the Book links now say "Book Mars to Earth, Jan 03, 2099"). The sweep invented nothing.

A first headless attempt (same day) could not write this file: Bob Shell checks the mode's `fileRegex` against the absolute Windows path, while the Bob IDE uses the workspace-relative path; the fences now accept both. That attempt also misread our prompt ("Nobody can answer questions") as a feature request; its proposals were discarded.
