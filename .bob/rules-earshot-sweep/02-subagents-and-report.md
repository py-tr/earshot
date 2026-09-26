# Subagents and the sweep file

- For up to 5 suspicious items, ask for one explore subagent per item, all at once in parallel, to find the component file and line responsible. If Bob declines to spawn them, find them yourself.
- Write sweep/<page-slug>.md with one line per proposed finding: S-NN | page | key script to reproduce | what NVDA said | why suspicious | expected announcement | likely file:line.
- The key script is ONE token "Tab ×N" (N = Tabs from the top to the last stop involved); the expected announcement is an exact phrase in quotes, never a [placeholder] pattern.
- Never edit application code. Reply with the number of proposed findings and the file path.
