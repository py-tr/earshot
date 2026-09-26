"""Bake the finding cards into index.html, so the page reads fully without JavaScript
(search engines, AI readers, text browsers). report.js skips rendering when cards are already there.
usage: python report/bake.py   (run after editing data.js)"""
import os, pathlib, re
from playwright.sync_api import sync_playwright

here = pathlib.Path(__file__).parent
page_path = here / "index.html"
html = page_path.read_text(encoding="utf8")
m = re.search(r'(<div id="findings-list"[^>]*>)(.*?)(</div><!-- /findings-list -->)', html, re.S)
assert m, "findings-list markers not found"
tmp = here / "_bake_tmp.html"
tmp.write_text(html[:m.end(1)] + "<p>Loading findings…</p>" + html[m.start(3):], encoding="utf8")
try:
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        pg = b.new_page()
        pg.goto(tmp.resolve().as_uri())
        pg.wait_for_selector("#findings-list .card")
        cards = pg.inner_html("#findings-list")
        b.close()
finally:
    os.remove(tmp)
page_path.write_text(html[:m.end(1)] + cards + html[m.start(3):], encoding="utf8")
print("baked", cards.count('class="card"'), "cards,", cards.count("<audio"), "audio players into index.html")
