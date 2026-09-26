<!-- sweep/todomvc.md: http://localhost:7002/ (TodoMVC React). Bob named this file home.md (slug of "/"); renamed so it does not overwrite the Galaxium Home sweep. -->

| ID   | Page | Key script to reproduce | What NVDA said | Why suspicious | Expected announcement | Likely file:line |
|------|------|------------------------|----------------|----------------|----------------------|------------------|
| S-01 | /    | Tab (after New Todo Input, with 2 items present) | "main landmark, ❯ Toggle All Input, check box, not checked" | The raw "❯" unicode arrow from a CSS ::before pseudo-element is being read as part of the label name, polluting the accessible name | "Toggle all, check box, not checked" | todomvc/src/todo/components/main.jsx:39 |
| S-02 | /    | Tab ×2 (after New Todo Input, with 2 items present) | "list, with 2 items, check box, not checked" | Todo item checkbox has no accessible name — NVDA reads only role without the item text ("Buy milk") | "Buy milk, check box, not checked" | todomvc/src/todo/components/item.jsx:36 |
| S-03 | /    | Tab ×3 (after New Todo Input, with 2 items present) | "check box, not checked" | Second todo item checkbox has no accessible name — NVDA reads only role without the item text ("Walk dog") | "Walk dog, check box, not checked" | todomvc/src/todo/components/item.jsx:36 |
