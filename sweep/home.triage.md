# Human triage of Bob's /sweep proposals for / (Home), 2026-09-26 10:45 CEST

Bob swept / by ear (task22; 25 Tabs from the top, real NVDA; take_20260926T102732) and asked 4 explore subagents, in parallel, to find the responsible code. It proposed 4 findings (`home.md`). A human checked each one against NVDA's log and the source:

| ID | Decision | Reason |
|---|---|---|
| S-01 | **ACCEPT** → F-07 | "Book a Flight, button, link" is heard on two Tabs in a row: a `<Button>` inside a `<Link>` (Header.tsx, Home page only) makes one control two Tab stops. WCAG 4.1.2 / 2.4.3. axe-core 4.13 did not flag it. |
| S-02 | **ACCEPT** → F-07 (same root cause) | "Explore Flights, button, link", twice (Home.tsx). |
| S-03 | **ACCEPT** → F-07 (same root cause) | "Book Your Flight Now, button, link", twice (Home.tsx). Counted as one finding with three instances: root causes, not places. |
| S-04 | **ACCEPT** → F-08 | The footer GitHub link contains only an icon, so NVDA falls back to the raw address "github.com, link". WCAG 2.4.4 / 1.1.1. axe-core does flag this one (link-name), and we say so. |

Not proposed by Bob, noted by the human: the "Learn More" button has no action at all. It is a broken button for every user, not a screen-reader issue, so it is out of scope. The destination cards (a link containing a heading and a description) are a valid pattern, rejected the same way as on /flights.

Bob's Tab numbers in `home.md` are off by 2 to 9 (a 25-Tab sweep cannot reach Tab 28) (the duplicate pairs are really Tabs 6/7, 8/9 and 18/19; github.com is Tab 20). The problems themselves match the transcript.

Result: **Bob proposed 4; the human accepted all 4 as 2 findings (F-07, F-08).** Across three sweep runs, Bob proposed 14 items and 5 findings were accepted (F-04..F-08).
