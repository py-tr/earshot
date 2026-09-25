---
argument-hint: <finding-id>
---

Before anything else, if the current mode is not "earshot", switch to the earshot mode, then continue.

For finding $1 in findings.md, follow the Earshot mode instructions: read the finding, state the expected announcement, make the minimal fix, call listen with the finding's key script, and check the transcript.

On pass, run `git commit` on the changed file with the message "$1: <one-line summary> (verified by NVDA)".

Reply VERIFIED plus the relevant transcript lines, or NEEDS HUMAN plus the full transcript if the expected announcement is absent after one retry.
