"""Run axe-core (all WCAG 2.x A/AA rules + best-practice) on the Galaxium /flights page and the open Sign In dialog.

usage: python bench/axe_run.py <base_url> <out.json>
e.g.   python bench/axe_run.py http://localhost:5174 bench/axe_baseline.json   (original app)
       python bench/axe_run.py http://localhost:5173 bench/axe_fixed.json      (fixed app)
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

base, out = sys.argv[1], sys.argv[2]
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
    page.goto(base + "/flights")
    page.wait_for_selector("text=/Showing [0-9]+ flights/")
    page.wait_for_timeout(800)
    found = scan(page, "flights page")
    page.get_by_role("button", name="Select Seat Class").first.click()   # opens the Sign In dialog (signed out)
    page.wait_for_selector("[role=dialog]")
    page.wait_for_timeout(800)
    found += scan(page, "Sign In dialog open")
    b.close()

Path(out).write_text(json.dumps(found, indent=1), encoding="utf8")
for v in found:
    print(f"[{v['state']}] {v['rule']} ({v['impact']}): {v['help']}  x{len(v['targets'])}  e.g. {v['targets'][0][:70]}")
print(len(found), "violations")
