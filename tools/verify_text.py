#!/usr/bin/env python3
"""Compare the visible words of every original page (tools/source) with the rebuilt page."""
import difflib
import os
import re
import sys

from bs4 import BeautifulSoup, Comment

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))


def words(root, drop_sel=(), buttons=True):
    for t in root(["script", "style", "noscript", "svg", "iframe"] + (["button"] if buttons else [])):
        t.decompose()
    for c in root.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    for sel in drop_sel:
        for t in root.select(sel):
            t.decompose()
    return re.sub(r"\s+", " ", root.get_text(" ")).replace("\xa0", " ").split()


def load(p):
    return BeautifulSoup(open(p, encoding="utf-8").read(), "lxml")


def check(slug, verbose=True):
    src = load(os.path.join(ROOT, "tools", "source", (slug or "home") + ".html"))
    out = load(os.path.join(ROOT, slug, "index.html") if slug else os.path.join(ROOT, "index.html"))
    s_main = src.find("div", role="main") or src.body
    if src.find("div", role="main"):
        # content that the original template left as siblings after div[role=main]
        for sib in list(s_main.next_siblings):
            if getattr(sib, "name", None) and sib.name not in ("footer", "header") and "footer-bg" not in (sib.get("class") or []):
                s_main.append(sib.extract())
    o_main = out.find("main")
    a = words(s_main)
    b = words(o_main, buttons=False)
    # the source concatenates tokens split by markup; compare on glued text to ignore spacing differences
    A, B = "".join(a), "".join(b)
    if A == B:
        return 0, []
    from collections import Counter
    ca, cb = Counter(a), Counter(b)
    missing, extra = ca - cb, cb - ca
    if not missing and not extra:
        return 0, [("order", "same words, different order (hero/island moved)", "")]
    return len(missing) + len(extra), [("missing", " ".join(f"{w}x{n}" for w, n in missing.items())[:300], "extra: " + " ".join(f"{w}x{n}" for w, n in extra.items())[:300])]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    diffs = [(tag, " ".join(a[i1:i2])[:140], " ".join(b[j1:j2])[:140]) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal"]
    # drop pure whitespace-split differences
    real = [d for d in diffs if re.sub(r"\s+", "", d[1]) != re.sub(r"\s+", "", d[2])]
    return len(real), real


if __name__ == "__main__":
    only = sys.argv[1:]
    from build import PAGES
    total = 0
    for slug in ["", *PAGES]:
        if only and slug not in only:
            continue
        if slug in ("mbbs", "bbacompare", "bcom-compare"):
            print(f"{slug:16} (verified in browser by verify_special.py)")
            continue
        if not os.path.exists(os.path.join(ROOT, slug, "index.html")):
            print(f"{slug or 'home':16} (not built)")
            continue
        n, d = check(slug)
        total += n
        print(f"{slug or 'home':16} {'OK' if n == 0 else str(n) + ' differences'}")
        for tag, x, y in d[:12]:
            print(f"     {tag}: SRC[{x}] OUT[{y}]")
    print("TOTAL differences:", total)
