"""Run axe-core (all WCAG 2.x A/AA rules + best-practice) on Uptime Kuma's dashboard and a monitor's Details page.

usage: python bench/axe_kuma.py <out.json>   (Uptime Kuma dev server on http://localhost:3000, auth disabled)
The original-code scan is taken with the upstream versions of the changed files checked out in the working tree.
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

out = sys.argv[1]
AXE = (Path(__file__).parent / "node_modules" / "axe-core" / "axe.min.js").read_text(encoding="utf8")
TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"]


def scan(page, state):
    page.add_script_tag(content=AXE)
    res = page.evaluate("tags => axe.run(document, {runOnly: {type: 'tag', values: tags}})", TAGS)
    return [{"state": state, "rule": v["id"], "impact": v["impact"], "help": v["help"],
             "targets": [" ".join(n["target"]) if isinstance(n["target"], list) else str(n["target"]) for n in v["nodes"]]}
            for v in res["violations"]]


with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    page = b.new_page(viewport={"width": 1280, "height": 900})
    found = []
    for path, state in (("/dashboard", "dashboard"), ("/dashboard/1", "monitor Details page")):
        page.goto("http://localhost:3000" + path)
        page.wait_for_selector("canvas.heartbeat-canvas")
        page.wait_for_timeout(1500)
        found += scan(page, state)
    b.close()

Path(out).write_text(json.dumps(found, indent=1), encoding="utf8")
for v in found:
    print(f"[{v['state']}] {v['rule']} ({v['impact']}): {v['help']}  x{len(v['targets'])}  e.g. {v['targets'][0][:90]}")
print(len(found), "violations")
