# Gate demo: Bob's "tidy-up" commit refused (2026-09-25 22:56 CEST)

- **Request to Bob (Agent mode, MCP off):** "Tidy up Modal.tsx: the setTimeout focus call, the tabIndex={-1} and the returnFocusRef look like leftovers. Remove them… then commit."
- **Bob's change:** `bob_refactor_blocked.diff`. The lines look like clutter; they are the focus management that makes the dialog audible.
- **Earshot gate** (`.githooks/pre-commit` → `earshot_mcp/hear_tests.py`) ran all three hear-tests with real NVDA and **refused the commit**:
  - F-01: missing "Sign In, dialog". NVDA said "Moon, link, heading, level 3" (silence, then a card behind the dialog). `blocked_F-01.txt`
  - F-02 and F-03 failed the same way (`blocked_F-02.txt`, `blocked_F-03.txt`).
- **Bob's own explanation after the block:** "The commit was blocked by Earshot: removing tabIndex={-1} from the role="dialog" element breaks screen reader focus — NVDA can no longer announce the modal as a dialog (F-01 fails with 'Sign In, dialog' missing)."
- **Nothing was committed.** HEAD unchanged; the working tree was restored afterwards.
