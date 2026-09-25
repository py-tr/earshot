# Human triage of Bob's /sweep proposals for /flights (2026-09-25 23:40 CEST)

Bob swept /flights by ear (25 Tabs from the top, real NVDA; take_20260925T232659) and proposed 5 findings (`flights.md`). A human reviewed each one:

| ID | Decision | Reason |
|---|---|---|
| S-01 | **ACCEPT** → finding F-04 | Nine buttons are all announced "Select Seat Class, button", so a screen-reader user cannot tell which flight they are booking. WCAG 2.4.6 Headings and Labels (AA); 1.3.1. |
| S-02 | reject | Several "Earth" links share a name, but they also share a target (/destinations/earth). The same name for the same target is allowed (WCAG 2.4.4). |
| S-03 | reject | Same as S-02, for "Mars". |
| S-04 | reject | A link inside an h3 is a valid pattern; NVDA's "link, heading, level 3" is standard, not a failure. |
| S-05 | **ACCEPT** → finding F-05 | There is no "skip to main content" link; keyboard users must Tab through the header on every page. WCAG 2.4.1 Bypass Blocks (A). (Bob's secondary point, that Pause comes first, is only a note.) |

Result: **Bob proposed 5 findings; the human accepted 2 (S-01, S-05) and rejected 3.** Accepted items go to findings.md, then `/hear`, then the gate.
