#!/usr/bin/env python3
"""
Port the three pages that already ship in the newer single-file template on the live site
(mbbs, bbacompare, bcom-compare). Their markup, copy and scripted behaviour are kept exactly;
the inline <style> and <script> blocks are moved to assets/css and assets/js, image paths are
localised and campaigns.pes.edu links are pointed at the local pages.

mbbs is the supplied reference design itself.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402
from build import BASE, PAGES, ROOT, SRC, img_queue, localize_img, local_page, write  # noqa: E402

REF_IMG = {  # files that already exist in the reference folder -> copied into assets/img
    "pesu_dark_logo.png": "assets/img/logo/pesu_dark_logo.png",
    "PESU-new-logo.png": "assets/img/logo/PESU-new-logo.png",
}
for n in ["mbbs-slider-one.jpg", "mbbs-slider-two.jpg", "mbbs-slider-three.jpg"] + [f"{i}.jpg" for i in range(1, 8)]:
    REF_IMG[n] = f"assets/img/banners/{n}"

IMG_RE = re.compile(r"""(["'(])((?:https?://[^"'()\s]+?|\.\./assets/[^"'()\s]+?|(?:\./)?img/[^"'()\s]+?)\.(?:png|jpe?g|svg|webp|gif|ico))(["')])""", re.I)


def fetch_text(url):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=40).read().decode("utf-8")


def add_fees_highlights(raw, slug):
    """Insert the Financial Support and University Highlights sections before the closing call-to-action band."""
    from bs4 import BeautifulSoup
    fx = build.Ctx(BASE + slug + "/", 1, "")
    for inc in ("inc-scholarships-at-pesu", "inc-loyalty-program"):
        build.prescan_fees(BeautifulSoup(open(os.path.join(SRC, inc + ".html"), encoding="utf-8").read(), "lxml"), fx)
    cards = "".join(
        f'<div class="imp-card" data-reveal><span class="imp-tag {t}">{l}</span><div class="pct">{p}</div><h4>{h}</h4><p>{x}</p></div>'
        for t, l, p, h, x in build.HIGHLIGHT_CARDS
    )
    block = (
        build.fees_html(fx)
        + '<section class="block procedure" id="highlights"><div class="wrap"><div class="section-head"><p class="eyebrow center">University Highlights</p>'
        "<h2>Recognition beyond the programme</h2><p>The accreditations and rankings behind PES University as a whole.</p></div>"
        f'<div class="imp-grid">{cards}</div></div></section>'
    )
    marker = '<section class="cta-band pic">'
    assert marker in raw
    return raw.replace(marker, block + "\n      " + marker, 1)


def port(slug):
    raw = open(os.path.join(SRC, slug + ".html"), encoding="utf-8").read()
    page_url = BASE + slug + "/"

    def img_sub(m):
        q1, url, q2 = m.groups()
        name = os.path.basename(url.split("?")[0])
        if "favicon" in name:
            return f"{q1}../assets/img/icons/favicon.ico{q2}"
        if name in REF_IMG:
            return f"{q1}../{REF_IMG[name]}{q2}"
        if url.startswith("../assets/logo-and-images/"):
            url = BASE + "assets/logo-and-images/" + name
        return f"{q1}{localize_img(url, page_url, 1)}{q2}"

    css_blocks = re.findall(r"<style[^>]*>(.*?)</style>", raw, re.S)
    css = "\n\n".join(css_blocks)
    raw = re.sub(r"<style[^>]*>.*?</style>", "", raw, flags=re.S)

    # pages already migrated to the new template load css/style.css + js/main.js from their own folder
    ext_js = ""
    m = re.search(r'<link rel="stylesheet" href="(css/[^"]+)">', raw)
    if m:
        css += "\n" + fetch_text(page_url + m.group(1))
        raw = raw.replace(m.group(0), "")
    m = re.search(r'<script src="(js/[^"]+)"></script>', raw)
    if m:
        ext_js = fetch_text(page_url + m.group(1))
        raw = raw.replace(m.group(0), f'<script src="../assets/js/{slug}.js"></script>')

    # the large behavioural script (last/longest inline script) moves to assets/js
    if ext_js:
        js = ext_js
    else:
        scripts = [(m.start(), m.end(), m.group(1)) for m in re.finditer(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", raw, re.S)]
        big = max(scripts, key=lambda s: len(s[2]))
        js = big[2]
        raw = raw[: big[0]] + f'<script src="../assets/js/{slug}.js"></script>' + raw[big[1] :]

    css = IMG_RE.sub(img_sub, css).replace("../assets/img/", "../img/")  # css lives in assets/css
    js = IMG_RE.sub(img_sub, js)
    raw = IMG_RE.sub(img_sub, raw)

    # drop references to files the site never shipped (apple-touch / webmanifest)
    raw = re.sub(r'\s*<link rel="(?:apple-touch-icon|manifest)"[^>]*>', "", raw)

    # internal links -> local pages
    def href_sub(m):
        url = m.group(1)
        loc = local_page(url, 1)
        return f'href="{loc}"' if loc else m.group(0)

    raw = re.sub(r'href="(https://campaigns\.pes\.edu/[^"]*)"', href_sub, raw)
    raw = raw.replace("</head>", f'<link rel="stylesheet" href="../assets/css/{slug}.css">\n</head>', 1)

    if slug == "bscjmc":
        raw = add_fees_highlights(raw, slug)

    write(f"assets/css/{slug}.css", css.strip() + "\n")
    write(f"assets/js/{slug}.js", js.strip() + "\n")
    write(f"{slug}/index.html", raw)
    print("ported", slug)


if __name__ == "__main__":
    for s in ("mbbs", "bbacompare", "bcom-compare", "bscjmc"):
        port(s)
    build.fetch_images()
    for w in build.warnings:
        print(w)
