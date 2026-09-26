# Boundaries

- Never run npm, yarn or any build or install script, and never read or write dist/, build/, node_modules/ or gitignored files: both dev servers reload from src by themselves. If a result looks stale, re-listen once.
