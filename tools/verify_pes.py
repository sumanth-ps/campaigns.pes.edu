#!/usr/bin/env python3
"""Word check for pages built from pes.edu: words in the source page that are missing from the output."""
import re, sys, os
from collections import Counter
from bs4 import BeautifulSoup, Comment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_pes as bp

DROPPED = ("PES Scholarships", "PES Loyalty Program", "Placements", "Attend a Session", "Study at PES", "You may also be interested in")
for slug in sys.argv[1:] or ["bca", "mca"]:
    soup, raw = bp.clean_soup(slug)
    w = soup.find(class_="kingster-page-wrapper")
    for el in w.select(".gdlr-core-hide-in-desktop-tablet"): el.decompose()
    for el in w.find_all(["details", "nav", "iframe"]): el.decompose()
    for ul in w.find_all("ul"):
        if ul.find_all("li") and all((li.find("a") and li.find("a").get("href") in bp.MENU_HREFS) for li in ul.find_all("li", recursive=False)): ul.decompose()
    # sections replaced on request (scholarships, loyalty, related links)
    for h in w.find_all("h3"):
        if h.get_text(strip=True) in DROPPED or h.get_text(strip=True).startswith("PES B.Tech degree"):
            blk = h.find_parent(class_="gdlr-core-pbf-column")
            if blk: blk.decompose()
    src = re.sub(r"\s+", "", w.get_text(" ")).replace("\xa0", "")
    out = BeautifulSoup(open(os.path.join(os.path.dirname(bp.ROOT) if False else bp.ROOT, slug, "index.html"), encoding="utf-8").read(), "lxml").find("main")
    for t in out(["script", "style", "svg", "iframe"]): t.decompose()
    o = re.sub(r"\s+", "", out.get_text(" ")).replace("\xa0", "")
    miss = Counter(src) - Counter(o)
    print(slug, "source chars", len(src), "| missing chars:", sum(miss.values()), dict(miss.most_common(12)))
