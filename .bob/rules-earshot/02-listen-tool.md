# Using listen()

- Every listen call passes path and start explicitly. If the key script starts with "page <path>, from top:", use path=<path>, start="TOP" and only the keys after the colon; otherwise use start="Select Seat Class" and path="/flights". If listen aborts with "start control not found", retry once with start="TOP" and the finding's path; never guess other start values.
- A key script has at most one Tab token, "Tab ×N", after any typing; never "Tab ×2, Tab ×3". If your change adds a tab stop, recount N in every test on that page.
- If listen replies "running", call listen_result with that label; it waits by itself, so never sleep or poll with shell commands.
- Read the "focus:" lines: if focus stays on the page behind the dialog after the key that opens it, focus is not moving into the dialog.
