#!/usr/bin/env python3
"""Add Scholarships @ PESU, PES University Loyalty Program, University highlights and 'Before you apply'
to bcomcompare/index.html, laid out like the "Five ways into commerce." rows (pb-row cards).
Text comes from the original include snapshots (tools/source/inc-*.html) and the page's own FAQ list."""
import html
import os
import re

from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools", "source")
PAGE = os.path.join(ROOT, "bcomcompare", "index.html")
MARK_START, MARK_END = "<!-- ===== extra sections (added) ===== -->", "<!-- ===== /extra sections ===== -->"


def soup_of(name):
    s = BeautifulSoup(open(os.path.join(SRC, f"inc-{name}.html"), encoding="utf-8").read(), "lxml")
    for t in s(["script", "style", "svg"]):
        t.decompose()
    return s


def txt(n):
    return re.sub(r"\s+", " ", n.get_text(" ", strip=True)).strip()


def e(s):
    return html.escape(s, quote=False)


def row(num, title, body_html, meta=()):
    chips = f'<div class="pb-meta">{"".join(f"<span>{e(m)}</span>" for m in meta)}</div>' if meta else ""
    return f'<article class="pb-row noimg reveal"><div class="pb-body"><p class="pb-num">{e(num)}</p><h3>{title}</h3>{body_html}{chips}</div></article>'


def section(sid, eyebrow, h2, lede, rows, cols=2, note=""):
    lede_html = f'<p class="lede">{e(lede)}</p>' if lede else ""
    note_html = f'<p class="pb-note">{note}</p>' if note else ""
    return (
        f'<section class="h-all" id="{sid}"><div class="wrap"><div class="section-head reveal"><div><p class="eyebrow">{e(eyebrow)}</p><h2>{h2}</h2></div>{lede_html}</div>'
        f'<div class="pb-list pb-cols-{cols}">{"".join(rows)}</div>{note_html}</div></section>'
    )


def build(with_faq=True):
    # --- scholarships ---
    sc = soup_of("scholarships-at-pesu")
    tabs = [a for a in sc.select(".nav-tabs a")]
    panes = {p.get("id"): p for p in sc.select(".tab-pane")}
    rows = []
    for k, a in enumerate(tabs):
        pane = panes.get(a.get("href", "").lstrip("#"))
        body = txt(pane) if pane else ""
        pct = re.search(r"(\d+(?:\.\d+)?\s*%|\d+\.\d+\+)", body)
        rows.append(row(f"{k + 1:02d} · Scholarship", e(txt(a)), f"<p>{e(body)}</p>", [pct.group(1)] if pct else []))
    note = " ".join(txt(p) for p in sc.find_all("p") if not p.find_parent(class_="tab-pane") and txt(p))
    s1 = section("pesu-scholarships", "Financial support", "Scholarships <em>@ PESU.</em>", "", rows, 3, e(note))

    # --- loyalty ---
    ly = soup_of("loyalty-program")
    rows = []
    for k, card in enumerate(ly.select(".card")):
        head = txt(card.select_one(".card-header"))
        head = re.sub(r"^\d+\.\s*", "", head)
        body = card.select_one(".card-body")
        paras = []
        for p in body.find_all(["p", "ul"], recursive=False):
            if p.name == "ul":
                paras.append("<ul>" + "".join(f"<li>{e(txt(li))}</li>" for li in p.find_all("li")) + "</ul>")
            elif txt(p):
                paras.append(f"<p>{e(txt(p))}</p>")
        pct = re.search(r"(\d+%)", txt(body))
        rows.append(row(f"{k + 1:02d} · Loyalty", e(head), "".join(paras), [pct.group(1)] if pct else []))
    s2 = section("pesu-loyalty", "Family and alumni", "PES University Loyalty <em>Program.</em>", "", rows, 2)

    # --- university highlights ---
    uh = soup_of("university-highlights")
    rows = []
    for k, h4 in enumerate(uh.find_all("h4")):
        wrap = h4.parent
        p = wrap.find("p")
        rows.append(row(f"{k + 1:02d} · Highlight", e(txt(h4)), f"<p>{e(txt(p)) if p else ''}</p>"))
    s3 = section("pesu-highlights", "Recognition", "University <em>highlights.</em>", "", rows, 2)

    # --- before you apply (the page's FAQ list) ---
    if not with_faq:
        return "\n".join([MARK_START, s1, s2, s3, MARK_END])
    js = open(os.path.join(ROOT, "assets", "js", "bcom-compare.js"), encoding="utf-8").read()
    block = js[js.index("const FAQS = ["): js.index("];", js.index("const FAQS = ["))]
    qa = re.findall(r"\['((?:[^'\\]|\\.)*)','((?:[^'\\]|\\.)*)'\]", block)
    unq = lambda s: s.replace("\\'", "'")
    rows = [row(f"{k + 1:02d} · Question", e(unq(q)), f"<p>{e(unq(a))}</p>") for k, (q, a) in enumerate(qa)]
    s4 = section("before-you-apply", "Questions", "Before you <em>apply.</em>", "The things applicants and parents ask us most often. Anything else, the admissions office picks up on 080-10-297297.", rows, 2)
    return "\n".join([MARK_START, s1, s2, s3, s4, MARK_END])


CSS = """
/* extra sections: pb-row cards without an image */
.pb-row.noimg, .pb-row.noimg:nth-child(even){grid-template-columns:1fr;}
.pb-row.noimg .pb-body{height:100%;justify-content:flex-start;}
.pb-row.noimg ul{margin:0;padding-left:18px;font-size:14px;color:var(--ink-soft);}
.pb-cols-2,.pb-cols-3{display:grid;gap:22px;}
.pb-cols-2{grid-template-columns:repeat(2,1fr);}
.pb-cols-3{grid-template-columns:repeat(3,1fr);}
.pb-note{margin-top:22px;font-size:13px;color:var(--ink-soft);max-width:80ch;}
@media (max-width:900px){.pb-cols-2,.pb-cols-3{grid-template-columns:1fr;}}
"""


def main(which="bcomcompare"):
    page = os.path.join(ROOT, which, "index.html")
    t = open(page, encoding="utf-8").read()
    t = re.sub(re.escape(MARK_START) + r".*?" + re.escape(MARK_END) + r"\n?", "", t, flags=re.S)
    t = t.replace(CSS, "")
    anchor = "<!-- ============ ENQUIRY ============ -->" if which == "bcomcompare" else "<!-- ============ FINAL CTA ============ -->"
    assert anchor in t
    t = t.replace(anchor, build(with_faq=(which == "bcomcompare")) + "\n" + anchor, 1)
    if which == "bcomcompare":
        t = t.replace("</style>", CSS + "</style>", 1)
    else:
        css = os.path.join(ROOT, "assets", "css", "bbacompare.css")
        c = open(css, encoding="utf-8").read().replace(CSS, "")
        open(css, "w", encoding="utf-8", newline="\n").write(c + CSS)
    open(page, "w", encoding="utf-8", newline="\n").write(t)
    print("sections added to", which)


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else "bcomcompare")
