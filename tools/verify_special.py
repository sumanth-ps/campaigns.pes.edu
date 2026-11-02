#!/usr/bin/env python3
"""Browser-rendered text comparison (live site vs local) for the three JS-driven pages."""
import functools, http.server, os, re, socketserver, sys, threading
from collections import Counter
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.ThreadingTCPServer(("127.0.0.1", 8126), functools.partial(Q, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()
JS = "() => document.documentElement.textContent"


def words(pg, url):
    pg.goto(url, wait_until="load")
    pg.wait_for_timeout(1500)
    t = pg.evaluate("""() => { const c = document.body.cloneNode(true);
        c.querySelectorAll('script,style,noscript,iframe,svg').forEach(e => e.remove());
        return c.textContent; }""")
    return re.sub(r"\s+", " ", t).split()


with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    for slug in sys.argv[1:] or ["mbbs", "bbacompare", "bcom-compare"]:
        a = words(pg, f"https://campaigns.pes.edu/{slug}/")
        o = words(pg, f"http://127.0.0.1:8126/{slug}/")
        # compare as sorted character multisets: immune to spacing and to the hero/CTA moving
        ca, co = Counter("".join(a)), Counter("".join(o))
        miss, extra = ca - co, co - ca
        print(f"{slug or 'home':16} live chars {sum(ca.values()):6} local chars {sum(co.values()):6} | live-only: {sum(miss.values())} {dict(miss.most_common(8)) or ''} | local-only: {sum(extra.values())} {dict(extra.most_common(8)) or ''}")
