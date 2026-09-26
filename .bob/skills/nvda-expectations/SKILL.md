---
name: nvda-expectations
description: Use when working in earshot mode and needing to know what NVDA actually announces for common controls, what silence means, and how to distinguish a passing from a failing transcript.
---

# NVDA Announcement Patterns

Grounded in verbatim NVDA transcripts from `evidence/*/before*.txt` and `evidence/*/after*.txt`,
and in WCAG 2.2 SC 4.1.2 (Name, Role, Value), SC 2.4.3 (Focus Order), and SC 4.1.3 (Status).

---

## 1. Link

**Pattern:** `'<name>', 'link'` — optionally prefixed with landmark name on first region entry,
`'same page'` for same-page anchors, `'heading', 'level N'` when link is also a heading.

**Example:** `Speaking [..., 'Mars', 'link', 'heading', 'level 3']`
— `evidence/F-06/before_bob_sweep_listen.txt` line 48

**WCAG:** SC 4.1.2. **Failure:** `'link'` alone (name is empty), or concatenated wrapper text
producing a long unintended label.

---

## 2. Button

**Pattern:** `'<name>', 'button'` — suffix `'collapsed'`/`'expanded'` for toggle states.

**Example:** `Speaking [..., 'Close modal', 'button']`
— `evidence/F-02/after_bob_listen.txt` line 20

**WCAG:** SC 4.1.2. **Failure:** `'button'` with no preceding name token.

---

## 3. Edit (text input)

**Pattern:** `'<name>', 'edit'[, 'required'][, '<placeholder-or-value>'][, 'blank']`
Landmark announced first on region entry.

**Example:** `Speaking [..., 'Name', 'edit', 'required', ..., 'John Doe', ..., 'blank']`
— `evidence/F-09/after_bob_listen.txt` line 19

**WCAG:** SC 4.1.2. **Failure:** Placeholder read as name (e.g. `'Search by origin or
destination...', 'edit'`) when `aria-label`/`<label>` is absent.

---

## 4. Check Box

**Pattern:** `'<name>', 'check box', 'not checked'|'checked'`
Container (list/landmark) announced on first entry.

**Example:** `Speaking [..., 'main landmark', '❯ Toggle All Input', 'check box', 'not checked']`
— `evidence/F-11/before_bob_earshot_sweep_listen.txt` line 69

**WCAG:** SC 4.1.2. **Failure:** `'check box', 'not checked'` with no name token before the role.

---

## 5. Dialog

**Pattern:** On open — `'<title>', 'dialog'` then `'heading', 'level N', '<title>'`; focus moves
inside the dialog immediately.

**Example:**
```
Speaking [..., 'Sign In', 'dialog', CancellableSpeech (still valid)]
Speaking [..., 'heading', 'level 2', 'Sign In']
```
— `evidence/F-01/after_bob_listen.txt` lines 10–11

**WCAG:** SC 4.1.2 + SC 2.4.3. **Failure:** No `'dialog'` token; NVDA reads the page element
that was previously focused (before state: `'Moon', 'link', 'heading', 'level 3'`).

---

## 6. Landmark

**Pattern:** First focusable element entering a region is prefixed with its landmark type:
`'banner landmark'`, `'navigation landmark'`, `'main landmark'`, `'form landmark'`,
`'content info landmark'`.

**Example:** `Speaking [..., 'banner landmark', 'Galaxium Travels', 'link']`
— `evidence/F-04/attempt1_rejected_bob_listen.txt` line 19

**WCAG:** SC 1.3.1 / 2.4.1. Landmark tokens tell you where focus went: after Enter on a skip link,
`'main landmark'` is the pass (`evidence/F-05/after_skip_focus_listen.txt`).

---

## 7. Live Region

**Pattern:** A Speaking line with the region's text and no role, right after the change that
triggered it (here: a typed letter), while focus stays where it was.

**Example:**
```
Speaking [..., 'Showing 5 flights ']
Speaking [..., 'Showing 4 flights ']
```
— `evidence/N-02/after_bob_listen.txt` lines 32 and 35 (typing "Mars" in the search field)

**WCAG:** SC 4.1.3. **Failure:** the typed letters are echoed, then nothing: the content changed on
screen only (`evidence/N-02/before_typing_listen.txt`).

Note: a role-first order such as `'button', 'Select Seat Class, Earth to Mars'` is NVDA re-reading the
control that just regained focus (e.g. after a dialog closes), not a live region.

---

## 8. What Silence, a Repeat, or a Role Without a Name Means

**Silence** (no `Speaking` line after a key press): the key changed something NVDA was never told
about. The classic case: Enter opens a dialog and nothing is said, because focus never moved into it
(`evidence/F-01/before_bob_listen.txt`: Enter at 1.01 s, no Speaking line until the next Tab).
WCAG: SC 4.1.2 / 2.4.3. Silence at the end of a sweep, when focus shows `BODY` and NVDA then reads
browser controls, is focus leaving the page: ignore it.

**Repeated announcement** (two consecutive Speaking lines for the same control, once with tokens in
reverse order): focus-restoration fired twice. Seen on Escape in
`evidence/F-02/after_bob_listen.txt` lines 35–36: `'button', 'Select Seat Class'` then `'Select
Seat Class', 'button'`. Not a bug — both lines confirm focus returned correctly.

**Role without a name** (`'check box', 'not checked'` or `'link'` alone, with no name before the
role token): accessible name is empty. Evidence: `evidence/F-11/before_bob_earshot_sweep_listen.txt`
line 73. WCAG: SC 4.1.2.

**`'clickable'` prefix** (`'clickable', 'Pause animation', 'button'`): element has a click
handler surfaced by NVDA as an extra state token. Not itself a failure.
