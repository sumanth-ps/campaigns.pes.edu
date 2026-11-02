#!/usr/bin/env python3
"""Browser smoke test: serves the site locally and checks every page at desktop/tablet/mobile widths.

Checks: console/page errors, failed local requests, broken images, horizontal overflow, dead local links.
Needs: pip install playwright   (uses the installed Chrome)
Usage: python tools/test_site.py [--shots DIR] [slug ...]
"""
import functools
import http.server
import os
import socketserver
import sys
import threading
import urllib.parse

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from build import PAGES  # noqa: E402

PORT = 8123
args = sys.argv[1:]
shots = None
if "--shots" in args:
    i = args.index("--shots")
    shots = args[i + 1]
    del args[i : i + 2]
only = args
SIZES = [("desktop", 1440, 900), ("tablet", 820, 1100), ("mobile", 390, 800)]
THIRD_PARTY = ("googletagmanager", "mxradon", "viewpage.co", "youtube", "fonts.g", "google-analytics")


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve():
    h = functools.partial(Quiet, directory=ROOT)
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", PORT), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def main():
    serve()
    slugs = ["", *PAGES]
    if only:
        slugs = [s for s in slugs if s in only]
    problems = 0
    seen_links = {}
    with sync_playwright() as p:
        br = p.chromium.launch(channel="chrome", headless=True)
        for slug in slugs:
            url = f"http://127.0.0.1:{PORT}/{slug + '/' if slug else ''}"
            for label, w, h in SIZES:
                ctx = br.new_context(viewport={"width": w, "height": h})
                pg = ctx.new_page()
                errs = []
                pg.on("pageerror", lambda e: errs.append(f"JS error: {e}"))
                pg.on("console", lambda m: errs.append(f"console.{m.type}: {m.text}") if m.type == "error" and not any(t in m.text for t in THIRD_PARTY) and "Failed to load resource" not in m.text else None)
                pg.on("response", lambda r: errs.append(f"HTTP {r.status} {r.url}") if r.status >= 400 and r.url.startswith(f"http://127.0.0.1:{PORT}") else None)
                pg.goto(url, wait_until="load")
                pg.wait_for_timeout(500)
                # reveal everything so lazy images load and screenshots show content
                pg.evaluate("document.querySelectorAll('[data-reveal]').forEach(e=>e.classList.add('is-visible')); document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')")
                pg.wait_for_timeout(600)
                info = pg.evaluate(
                    """() => {
                      const broken = [...document.images].filter(i => i.complete && i.naturalWidth === 0 && i.src).map(i => i.src);
                      const de = document.documentElement;
                      const over = de.scrollWidth - de.clientWidth;
                      const links = [...document.querySelectorAll('a[href]')].map(a => a.href);
                      return {broken, over, links};
                    }"""
                )
                if info["over"] > 1:
                    # find the offender
                    off = pg.evaluate(
                        """() => [...document.querySelectorAll('body *')].filter(e => e.getBoundingClientRect().right > document.documentElement.clientWidth + 1 && getComputedStyle(e).position !== 'fixed' && !e.closest('.slider-track,.tbl-wrap,#mobileMenu,.to-top')).slice(0,4).map(e => e.tagName + '.' + e.className)"""
                    )
                    errs.append(f"horizontal overflow {info['over']}px: {off}")
                for b in info["broken"]:
                    errs.append(f"broken image {b}")
                for l in info["links"]:
                    if l.startswith(f"http://127.0.0.1:{PORT}") and l not in seen_links:
                        path = urllib.parse.urlparse(l).path
                        fp = os.path.join(ROOT, path.lstrip("/"))
                        if os.path.isdir(fp):
                            fp = os.path.join(fp, "index.html")
                        seen_links[l] = os.path.exists(fp)
                    if seen_links.get(l) is False:
                        errs.append(f"dead local link {l}")
                if shots and (label != "tablet"):
                    os.makedirs(shots, exist_ok=True)
                    pg.screenshot(path=os.path.join(shots, f"{slug or 'home'}-{label}.png"), full_page=True)
                if errs:
                    problems += len(set(errs))
                    print(f"[{slug or 'home'} @ {label}]")
                    for e in sorted(set(errs)):
                        print("   ", e[:220])
                ctx.close()
            print("checked", slug or "home")
        br.close()
    print("PROBLEMS:", problems)


if __name__ == "__main__":
    main()
