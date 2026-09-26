---
argument-hint: <page-path>
---

Call switch_mode with mode_slug "earshot-run" (not "agent" or "code"). If that fails, stop and say so; never continue in another mode. The page to run is "$1" (use "/" if it is empty).
Then follow the earshot-run mode instructions with path="$1", and pass start="TOP" and path="$1" to every sweep listen call.
