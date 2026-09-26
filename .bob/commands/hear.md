---
argument-hint: <finding-id>
---

Before anything else, if the current mode is not "earshot", switch to the earshot mode, then continue.
If finding $1's verify column is "human": you may make the minimal fix and use listen only for what can be heard (e.g. that a new control is announced), but never reply VERIFIED. Reply NEEDS HUMAN, list what the screen reader confirmed, and state exactly what a person must check by eye or by judgement.

For finding $1 in findings.md, follow the Earshot mode instructions: read the finding, state the expected announcement, make the minimal fix, call listen with the finding's key script, and check the transcript.

On pass, add the hear-test for $1 to hear-tests.json exactly as the Earshot mode instructions say, then stage the changed frontend file AND hear-tests.json together and run `git commit` with the message "$1: <one-line summary> (verified by NVDA)". Your todo list must include "Write hear-test". Never reply VERIFIED without it.

Reply VERIFIED plus the relevant transcript lines, or NEEDS HUMAN plus the full transcript if the expected announcement is absent after one retry.
