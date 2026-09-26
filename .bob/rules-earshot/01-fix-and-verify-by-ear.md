# Fix, then verify by ear

- Read only the finding line and the one component it names.
- State the expected NVDA announcement before making any edit.
- Make the minimal diff required to produce that announcement.
- The expected announcement is the exact phrase from the finding, or, if the finding gives a pattern, a concrete phrase you state before editing. Choose names a listener can use (for example route and date), never bare database ids.
- Before listen, state in one sentence what a mouse user sees before and after your change on hover and focus. If you hide a control (opacity:0, visibility), it must reappear on its original :hover and on :focus.
- Call listen with the finding's key script and verify the expected announcement appears in the output.
- If it does not appear, retry once; if it still fails, reply NEEDS HUMAN with the full transcript.
- Findings marked verify "human" end as NEEDS HUMAN, never VERIFIED.
- Use the nvda-expectations skill to state the expected announcement and to read the transcript (what a name, role, state, silence or repeat means).
