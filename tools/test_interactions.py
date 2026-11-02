import functools, http.server, os, socketserver, threading
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
threading.Thread(target=socketserver.ThreadingTCPServer(("127.0.0.1", 8128), functools.partial(Q, directory=ROOT)).serve_forever, daemon=True).start()
B = "http://127.0.0.1:8128/"
with sync_playwright() as p:
    br = p.chromium.launch(channel="chrome")
    pg = br.new_page(viewport={"width": 1440, "height": 900}); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(B + "bca/"); pg.wait_for_timeout(500)
    t = pg.locator(".acc-trigger").nth(1); t.scroll_into_view_if_needed(); t.click(); pg.wait_for_timeout(500)
    print("accordion opens:", pg.locator(".acc-item.is-open").count() >= 1, "aria-expanded:", t.get_attribute("aria-expanded"))
    pg.goto(B + "btech/"); pg.wait_for_timeout(500)
    tb = pg.locator(".tab-btn").nth(2); tb.scroll_into_view_if_needed(); tb.click()
    print("tab switches:", pg.locator(".tab-panel.is-active .vt-head").first.inner_text()[:50])
    pg.goto(B + "mba/"); pg.wait_for_timeout(500)
    s = pg.locator(".slider-track").first; s.scroll_into_view_if_needed(); before = s.evaluate("e=>e.scrollLeft")
    pg.locator(".slider-btn[data-dir='1']").first.click(); pg.wait_for_timeout(900)
    print("slider scrolls:", s.evaluate("e=>e.scrollLeft") > before)
    pg.goto(B + "btech/"); pg.mouse.wheel(0, 800); pg.wait_for_timeout(500)
    print("sticky header scrolled class:", pg.evaluate("document.getElementById('siteHeader').classList.contains('scrolled')"))
    m = br.new_page(viewport={"width": 390, "height": 800}); m.goto(B + "btech/"); m.wait_for_timeout(500)
    m.click("#hamburger"); m.wait_for_timeout(500)
    print("mobile menu open:", m.evaluate("document.getElementById('mobileMenu').classList.contains('open')"))
    m.click("#closeMenu"); m.wait_for_timeout(500)
    print("mobile menu closes:", not m.evaluate("document.getElementById('mobileMenu').classList.contains('open')"))
    m.goto(B); m.click("a.program-link >> nth=0"); m.wait_for_timeout(500); print("home->btech link:", m.url)
    print("JS errors:", errs or "none")
