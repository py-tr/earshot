# /earshot: the whole loop in one command

Start by writing a todo list with update_todo_list (Sweep, Triage, Record findings, Fix each finding, Summary) and tick items off as you go.

## Step A — Sweep

If the page is a list app that starts empty (the first Tab stop is an edit field for new items, e.g. TodoMVC), use this sweep key script instead, so there are items to hear: Tab, Type "Buy milk", Enter, Type "Walk dog", Enter, Tab ×20.
The page may be a full URL of another app (e.g. http://localhost:7002/); pass it as path unchanged.

Derive the page slug from the path: "/" → "home", "/bookings" → "bookings", etc. For a full URL of another app, use the app name (e.g. "todomvc"), never "home"; never overwrite an existing sweep file of another app. For Uptime Kuma use the full URL http://localhost:3000/dashboard as path, start="TOP", slug "uptime-kuma".

Call listen with start "TOP", gap 1.5, path=<page>, and key_script "Tab ×25", or the list-app seed script above when the page is a list app that starts empty.
If listen replies "running", call listen_result with that label (never sleep or poll).

Apply the same flagging rules as the earshot-sweep mode:
- NVDA says nothing new on a Tab stop
- NVDA says only a role ("link", "button", "edit", "graphic")
- NVDA reads example or placeholder text as the name
- Focus lands on "[page behind dialog]"
- The same name is given to different targets
- The same control is reached on two consecutive Tabs (button nested inside a link)
- A link's spoken name is a web address such as "github.com" (no text)
Ignore everything after focus leaves the page.

For up to 5 suspicious stops, spawn one explore subagent per item, all in parallel, to
find the component file and line responsible. If Bob declines, find them yourself.

Write sweep/<page-slug>.md with one line per proposed finding in S-NN format:
  S-NN | page | key script to reproduce | what NVDA said | why suspicious | expected announcement | likely file:line

## Step B — Human triage

Use ask_followup_question to present every proposal (one line each: what NVDA said /
why suspicious / expected announcement) and ask which ones to accept.
Wait for the answer. Accept only what the human explicitly accepts.

## Step C — Record accepted findings

For each accepted proposal, append one line to findings.md using the next free F-NN id,
following the existing pipe-delimited format:
  F-NN | <WCAG criteria> | <component / page> | page <path>, from top: <the typing seed, if the sweep used one>, Tab ×N | <expected announcement> | ear
Record one finding per accepted proposal unless the human says to merge them.
The key script is ONE token "Tab ×N", where N is the number of Tabs from the top to the last stop involved ("Tab ×8, Tab ×9" would mean 17 Tabs; write "Tab ×9"). The expected announcement is the exact phrase(s) NVDA should say, in quotes, with no [placeholders]; name things a listener can use (route, date), never bare ids.

## Step D — Fix each accepted finding

For each new F-NN, in sequence (never in parallel — there is one screen reader):
  call start_subtask with mode "earshot" and the message exactly `/hear F-NN` (not "Fix F-NN"; no title or other text). Do not echo or print subtask markers yourself; the subtask ends by itself
Wait for each subtask to finish before starting the next.

## Step E — Summary

Reply with one line per original proposal:
  - Rejected proposals: "S-NN: rejected"
  - Accepted and verified: "F-NN (S-NN): accepted — VERIFIED <commit-id>"
  - Accepted but needs human: "F-NN (S-NN): accepted — NEEDS HUMAN"
Before the summary, confirm each VERIFIED id has a test in hear-tests.json; otherwise report it as NEEDS HUMAN. Finish the task when the summary is written.
