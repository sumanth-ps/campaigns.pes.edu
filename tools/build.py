#!/usr/bin/env python3
"""
PES Campaigns static-site generator.

Reads the original campaigns.pes.edu HTML snapshots in tools/source/ and writes the
redesigned pages (index.html, <slug>/index.html) at the project root.

Text is never retyped: every page is produced by transforming the original DOM, so the
visible wording, order and link destinations come straight from the source.

Usage:  python tools/build.py [--fetch]      (--fetch downloads any missing images)
"""
import html
import os
import re
import sys
import urllib.parse
import urllib.request
from collections import OrderedDict

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import designer  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools", "source")
IMG_DIR = os.path.join(ROOT, "assets", "img")
BASE = "https://campaigns.pes.edu/"

# slug -> source snapshot (home is "")
PAGES = OrderedDict(
    (s, s)
    for s in """btech mbbs bca bdes bba bbaanalytics bbacompare bbasports bcom bcom-hons-ca bcom-hons
bcom-hons-cma bcom-hons-cfa bcom-compare bsceconomics bpt law llb-hons bscpsychology bsccct bscdtt
bscaot bscmedical bscemt bscmlt bscmrit nursing bapa bscjmc bbahem allied-health bpharm pharmd
mscpsychology mca mba mpharm mtech mdes""".split()
)

REGISTER = "https://admissions.pes.edu/registration/"
FETCH = "--fetch" in sys.argv
img_queue = {}  # absolute url -> local path (relative to ROOT)
warnings = []
missing_local = set()  # local asset paths that could not be downloaded (404 on the live site too)


# ----------------------------------------------------------------------------- helpers
def esc(t):
    return html.escape(t, quote=False)


def attr(t):
    return html.escape(t, quote=True)


def prefix(depth):
    return "../" * depth


def local_page(url, depth):
    """Map an absolute campaigns.pes.edu URL to a local relative link, or None."""
    p = urllib.parse.urlparse(url)
    if p.netloc not in ("campaigns.pes.edu",):
        return None
    path = p.path.strip("/")
    frag = ("#" + p.fragment) if p.fragment else ""
    if path == "":
        return prefix(depth) + "index.html" + frag if depth else "index.html" + frag
    if path in PAGES:
        return prefix(depth) + path + "/" + frag
    return None


def safe_name(url):
    name = urllib.parse.unquote(os.path.basename(urllib.parse.urlparse(url).path))
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-")
    return name or "image"


def localize_img(src, page_url, depth):
    """Resolve an <img> source against the page, queue it for download, return local path."""
    src = html.unescape(src).strip()
    if src.startswith("data:"):
        return src
    absu = urllib.parse.urljoin(page_url, src)
    absu = urllib.parse.quote(urllib.parse.unquote(absu), safe=":/?&=%#")
    if absu not in img_queue:
        name = safe_name(absu)
        sub = "icons" if name.endswith(".svg") else "campaigns"
        if "emailer-logo" in name:
            sub = "logo"
        rel = f"assets/img/{sub}/{name}"
        used = {v for v in img_queue.values()}
        n = 1
        base, ext = os.path.splitext(name)
        while rel in used:  # same filename, different source URL
            n += 1
            rel = f"assets/img/{sub}/{base}-{n}{ext}"
        img_queue[absu] = rel
    return prefix(depth) + img_queue[absu]


def fetch_images():
    for url, rel in img_queue.items():
        dest = os.path.join(ROOT, rel)
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=40) as r, open(dest, "wb") as f:
                f.write(r.read())
        except Exception as e:  # noqa
            warnings.append(f"MISSING ASSET {url} ({e})")
            missing_local.add(rel)
            print("  !! missing", url, e)


# ----------------------------------------------------------------------------- DOM -> HTML
SKIP = {"script", "style", "noscript", "svg", "hr", "link", "meta", "form", "input", "select", "textarea", "button", "head"}
KEEP_INLINE = {"strong", "b", "em", "i", "u", "small", "sup", "sub", "br", "span", "mark", "s", "abbr", "cite"}
KEEP_BLOCK = {"p", "ul", "ol", "li", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "dl", "dt", "dd", "pre", "figure", "figcaption"}
TABLE = {"table", "thead", "tbody", "tfoot", "tr", "th", "td", "caption"}


def classes(n):
    return n.get("class", []) if isinstance(n, Tag) else []


def has_class(n, *names):
    c = classes(n)
    return any(x in c for x in names)


def is_col(n):
    return isinstance(n, Tag) and any(re.fullmatch(r"col(-[a-z0-9]+)*", c) for c in classes(n))


def text_of(n):
    return re.sub(r"\s+", " ", n.get_text(" ", strip=True)).strip() if isinstance(n, Tag) else str(n).strip()


def has_content(n):
    if isinstance(n, Comment):
        return False
    if isinstance(n, NavigableString):
        return bool(str(n).strip())
    if n.name in SKIP:
        return False
    return bool(n.get_text(strip=True)) or bool(n.find(["img", "iframe"])) or n.name in ("img", "iframe")


class Ctx:
    def __init__(self, page_url, depth, title):
        self.page_url, self.depth, self.title = page_url, depth, title
        self.uid = 0

    def next_id(self, p):
        self.uid += 1
        return f"{p}{self.uid}"


def render_children(n, cx):
    return "".join(render(c, cx) for c in n.children)


def render_href(a, cx):
    href = (a.get("href") or "").strip()
    if not href:
        return ""
    if href.startswith(("mailto:", "tel:", "#", "javascript")):
        return f' href="{attr(href)}"'
    absu = urllib.parse.urljoin(cx.page_url, html.unescape(href))
    loc = local_page(absu, cx.depth)
    out = f' href="{attr(loc if loc else absu)}"'
    if a.get("target") == "_blank" and not loc:
        out += ' target="_blank" rel="noopener"'
    return out


def render_table(t, cx):
    return '<div class="tbl-wrap"><table class="data-table">' + render_children(t, cx) + "</table></div>"


def render_accordion(acc, cx):
    """Bootstrap accordion -> .acc; stray (non-card) content inside the accordion keeps its source position."""
    out, items = [], []

    def flush():
        if items:
            out.append('<div class="acc sem-acc">' + "".join(items) + "</div>")
            items.clear()

    for card in acc.children:
        if not isinstance(card, Tag) or isinstance(card, Comment):
            if isinstance(card, NavigableString) and str(card).strip() and not isinstance(card, Comment):
                flush()
                out.append(f"<p>{esc(str(card).strip())}</p>")
            continue
        if not has_class(card, "card"):
            if has_content(card):
                flush()
                out.append(render(card, cx))
            continue
        head = card.find(class_="card-header")
        body = card.find(class_="card-body")
        coll = card.find(class_="collapse")
        title_a = head.find("a") if head else None
        title = render_children(title_a, cx).strip() if title_a else (render_children(head, cx) if head else "")
        is_open = bool(coll and "show" in classes(coll))
        i = cx.next_id("acc")
        n = len(items) + 1
        rows = len(body.find_all("tr")) - len(body.find_all("thead")) if body is not None and body.find("table") else 0
        count = f'<span class="sem-count">{rows} {"entry" if rows == 1 else "entries"}</span>' if rows else '<span class="sem-count"></span>'
        wide = " sem-wide" if body is not None and body.find("table") else ""
        panel = render_children(body, cx) if body else ""
        tb = body.find("table") if body is not None else None
        if tb is not None and len(body.find_all("table")) == 1 and not body.find(["p", "ul", "h4", "h5"]):
            trs = [tr for tr in tb.find_all("tr") if tr.find("td")]
            ncols = max((len(tr.find_all("td")) for tr in trs), default=9)
            if trs and ncols <= 2:
                # same look as BCA: subjects as a two-column dash list (serial numbers kept)
                lis = []
                for tr in trs:
                    tds = tr.find_all("td")
                    txt = render_children(tds[-1], cx).strip()
                    sl = text_of(tds[0]) if len(tds) == 2 else ""
                    lis.append(f"<li>{txt}</li>")
                panel = f'<ul class="sem-list">{"".join(lis)}</ul>'
                wide = ""
        items.append(
            f'<div class="acc-item sem-item{" is-open" if is_open else ""}{wide}">'
            f'<h4 class="acc-head"><button type="button" class="acc-trigger sem-trigger" aria-expanded="{"true" if is_open else "false"}" aria-controls="{i}">'
            f'<span class="sem-num">{n:02d}</span><span class="acc-title">{title}</span>{count}<span class="acc-plus" aria-hidden="true"></span></button></h4>'
            f'<div class="acc-panel" id="{i}" role="region"><div class="acc-clip"><div class="acc-panel-inner">'
            f'{panel}</div></div></div></div>'
        )
    flush()
    return "".join(out)


def render_slider(owl, cx):
    items = owl.select(".owl-item:not(.cloned)")
    if not items:
        items = [c for c in owl.find_all(True, recursive=False) if has_content(c)]
    real = [i for i in items if has_content(i)]
    if len(real) >= 3 and all(i.find("img") for i in real):
        # logo / photo strips: same continuously scrolling marquee as the BCA page
        def tile(i, alt):
            h = render_children(i, cx)
            if alt:
                h = re.sub(r'alt="[^"]*"', 'alt=""', h)
            return f'<div class="logo-tile">{h}</div>'
        tiles = "".join(tile(i, False) for i in real)
        dup = "".join(tile(i, True) for i in real)
        return (
            '<div class="logo-marquee"><div class="logo-track">'
            f'{tiles}<span class="logo-dup" aria-hidden="true">{dup}</span></div></div>'
        )
    slides = "".join(f'<div class="slide">{render_children(i, cx)}</div>' for i in items if has_content(i))
    arrow = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="{}"/></svg>'
    return (
        '<div class="slider" data-slider>'
        f'<div class="slider-track" tabindex="0">{slides}</div>'
        '<div class="slider-nav">'
        f'<button type="button" class="slider-btn" data-dir="-1" aria-label="Previous">{arrow.format("M15 18l-6-6 6-6")}</button>'
        f'<button type="button" class="slider-btn" data-dir="1" aria-label="Next">{arrow.format("M9 18l6-6-6-6")}</button>'
        "</div></div>"
    )


def render_tabs(tabs, cx):
    nav = tabs.find(class_="nav-tabs") or tabs.find("ul")
    links = nav.find_all("a") if nav else []
    panes = {p.get("id"): p for p in tabs.find_all(class_="tab-pane")}
    gid = cx.next_id("tabs")
    btns, pns = [], []
    for k, a in enumerate(links):
        pid = (a.get("href") or "").lstrip("#")
        pane = panes.get(pid)
        active = "active" in classes(a) or (pane is not None and "active" in classes(pane))
        btns.append(
            f'<button type="button" role="tab" class="tab-btn{" is-active" if active else ""}" id="{gid}-t{k}" '
            f'aria-controls="{gid}-p{k}" aria-selected="{"true" if active else "false"}">{render_children(a, cx)}</button>'
        )
        pns.append(
            f'<div role="tabpanel" class="tab-panel{" is-active" if active else ""}" id="{gid}-p{k}" aria-labelledby="{gid}-t{k}">'
            f'{render_children(pane, cx) if pane else ""}</div>'
        )
    return f'<div class="tabs" data-tabs><div class="tab-list" role="tablist">{"".join(btns)}</div>{"".join(pns)}</div>'


def render_iframe(f, cx):
    src = f.get("src", "")
    name = f.get("name", "")
    h = f.get("height") or "450"
    h = re.sub(r"[^0-9]", "", h) or "450"
    title = "Enquiry form" if "viewpage" in src else "Embedded content"
    extra = f' name="{attr(name)}"' if name else ""
    if "youtube" in src:
        return (
            f'<div class="video-frame"><iframe src="{attr(src)}" title="{title}" loading="lazy" '
            f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe></div>'
        )
    return (
        f'<div class="enquire-card"><div class="enquire-frame"><iframe{extra} src="{attr(src)}" title="{title}" '
        f'width="100%" height="{h}" frameborder="0" marginwidth="0" marginheight="0" scrolling="no" loading="lazy"></iframe></div></div>'
    )


def render_img(n, cx, cls=""):
    src = n.get("src") or n.get("data-src") or ""
    if not src:
        return ""
    alt = n.get("alt")
    if alt is None or not alt.strip():
        alt = cx.title
    return f'<img src="{attr(localize_img(src, cx.page_url, cx.depth))}" alt="{attr(alt)}" loading="lazy"{cls}>'


def img_only(n):
    """True if a column holds nothing but images."""
    return isinstance(n, Tag) and bool(n.find("img")) and not n.get_text(strip=True) and not n.find("iframe")


def render_cols(row, cx):
    """Render a Bootstrap-style row: grouped columns become a responsive grid; any
    non-column content placed directly in the row (e.g. a heading) is kept in source order."""
    out, group = [], []

    def flush():
        if not group:
            return
        parts, media = [], False
        for c in group:
            if img_only(c):
                media = True
                parts.append(f'<div class="col col-media">{render_children(c, cx)}</div>')
            elif c.find("iframe") and not c.get_text(strip=True):
                parts.append(f'<div class="col col-embed">{render_children(c, cx)}</div>')
            else:
                parts.append(f'<div class="col">{render_children(c, cx)}</div>')
        n = min(len(parts), 4)
        out.append(f'<div class="cols cols-{n}{" has-media" if media else ""}">' + "".join(parts) + "</div>")
        group.clear()

    for c in row.children:
        if isinstance(c, Tag) and is_col(c):
            if has_content(c):
                group.append(c)
        elif has_content(c):
            flush()
            out.append(render(c, cx))
    flush()
    return "".join(out)


def render(n, cx):
    if isinstance(n, Comment):
        return ""
    if isinstance(n, NavigableString):
        t = re.sub(r"[ \t\r\n\f]+", " ", str(n))
        return esc(t)
    name = n.name
    if name in SKIP:
        return ""
    if n.has_attr("data-fees-slot"):
        return FEES_TOKEN
    if n.has_attr("data-html-slot"):
        return cx.slots[int(n["data-html-slot"])]
    if n.get("id") in INCLUDES and not n.get_text(strip=True) and not n.find("img"):
        return "".join(h for h, _ in include_blocks(n["id"], cx))
    if name == "img":
        return render_img(n, cx)
    if name == "iframe":
        return render_iframe(n, cx)
    if name == "br":
        return "<br>"
    if name in TABLE:
        if name == "table":
            return render_table(n, cx)
        a = ""
        for k in ("colspan", "rowspan"):
            if n.get(k):
                a += f' {k}="{attr(n[k])}"'
        if name == "th":
            a += ' scope="col"' if n.find_parent("thead") else ""
        return f"<{name}{a}>{render_children(n, cx)}</{name}>"
    if has_class(n, "accordion") and n.find(class_="card"):
        return render_accordion(n, cx)
    if has_class(n, "owl-carousel"):
        return render_slider(n, cx)
    if has_class(n, "tabs") and n.find(class_="tab-pane"):
        return render_tabs(n, cx)
    if name == "a":
        inner = render_children(n, cx)
        if not inner.strip():
            return ""
        return f"<a{render_href(n, cx)}>{inner}</a>"
    if name == "i":
        # icon fonts (<i class="fas ...">) have no text; text <i> stays
        return f"<i>{render_children(n, cx)}</i>" if n.get_text(strip=True) else ""
    if name in KEEP_INLINE:
        return f"<{name}>{render_children(n, cx)}</{name}>"
    if name in ("ul", "ol"):
        icon = any(li.find("i") and not li.find("i").get_text(strip=True) for li in n.find_all("li", recursive=False))
        return f'<{name}{" class=\"tick-list\"" if icon else ""}>{render_children(n, cx)}</{name}>'
    if name in KEEP_BLOCK:
        inner = render_children(n, cx)
        if name == "p" and not inner.replace("&nbsp;", "").replace("\xa0", "").strip():
            return ""
        return f"<{name}>{inner}</{name}>"
    # layout wrappers
    if has_class(n, "row"):
        cols = [c for c in n.find_all(True, recursive=False) if is_col(c) and has_content(c)]
        if len(cols) >= 2:
            return render_cols(n, cx)
    return render_children(n, cx)


# ----------------------------------------------------------------------------- block flattening
WRAP_STOP = ("accordion", "owl-carousel", "tabs")


LOYALTY_CARDS = [
    ("30%", "PES Employees", "Children of full-time staff, 5+ years employment."),
    ("20%", "PES Institution Students", "Graduates of any PES institution or sister concern."),
    ("10%", "Siblings of Students", "Siblings of currently enrolled PES students."),
    ("10%", "Alumni Family", "Siblings and children of PES University alumni."),
]
HIGHLIGHT_CARDS = [
    ("tag-scholar", "Ranking", "#1", "University in Karnataka", "Among new universities under 5 years, ranked by KSURF."),
    ("tag-loyalty", "Accreditation", "A+", "NAAC Accredited", "PES University holds NAAC's top-grade accreditation nationally."),
    ("tag-scholar", "Ranking", "#1", "B-School in Karnataka", "Times of India B-School Rankings, 2021."),
    ("tag-loyalty", "Recognition", "2nd", "Most Preferred B-School", "Second only to IIM Bangalore among B-School aspirants, per Times of India."),
]
FEES_TOKEN = "@@FEES@@"


def _pct(text):
    m = re.search(r"(\d+(?:\.\d+)?\s*%)", text)
    if m:
        return m.group(1).replace(" ", "")
    m = re.search(r"(\d+\.\d+\+)", text)
    return m.group(1) if m else ""


def capture_fees(n, cx):
    """The 'Scholarships @ PESU' and 'PES University Loyalty Program' sections are re-laid-out in the
    reference style ('Merit scholarships, awarded on performance'); each page's own figures and
    wording are carried into the cards."""
    if not isinstance(n, Tag) or n.name not in ("section", "div"):
        return False
    text = n.get_text(" ", strip=True)
    if not hasattr(cx, "fees"):
        cx.fees = {}
    if "Scholarships @ PESU" in text and "Loyalty Program" not in text and n.find(class_="tab-pane") and len(text) < 1500:
        nav = n.find(class_="nav-tabs")
        panes = {p.get("id"): p for p in n.find_all(class_="tab-pane")}
        cards = []
        for a in nav.find_all("a"):
            pane = panes.get((a.get("href") or "").lstrip("#"))
            body = render_children(pane, cx).strip() if pane else ""
            ptxt = text_of(pane) if pane else ""
            cards.append(
                f'<div class="imp-card" data-reveal><span class="imp-tag tag-scholar">Scholarship</span>'
                f'<div class="pct">{esc(_pct(ptxt))}</div><h4>{render_children(a, cx).strip()}</h4>{body}</div>'
            )
        notes = [render_children(p, cx).strip() for p in n.find_all("p") if not p.find_parent(class_="tab-pane") and p.get_text(strip=True)]
        cx.fees["sch"] = (cards, notes)
        return True
    if "Loyalty Program" in text and "Scholarships @ PESU" not in text and n.find(class_="accordion") and len(text) < 2400:
        cards = [
            f'<div class="imp-card" data-reveal><span class="imp-tag tag-loyalty">Loyalty</span><div class="pct">{pct}</div><h4>{esc(h)}</h4><p>{esc(t)}</p></div>'
            for pct, h, t in LOYALTY_CARDS
        ]
        cx.fees["loy"] = cards
        return True
    return False


def capture_highlights(n, cx):
    """'University Highlights' -> reference-style numbered highlight cards beside the campus photo."""
    if not isinstance(n, Tag) or n.name not in ("section", "div"):
        return None
    text = n.get_text(" ", strip=True)
    if not text.startswith("University Highlights") or len(text) > 1500 or len(n.find_all("h4")) < 3:
        return None
    if n.find_parent(attrs={"data-html-slot": True}):
        return None
    if any(c.name in ("section", "div") and c.get_text(" ", strip=True).startswith("University Highlights") and len(c.find_all("h4")) >= 3 and c is not n and len(c.get_text()) == len(n.get_text()) for c in n.find_all(["section", "div"], recursive=False)):
        return None  # a tighter wrapper exists; take that one
    cards = "".join(
        f'<div class="imp-card" data-reveal><span class="imp-tag {tag}">{label}</span><div class="pct">{pct}</div><h4>{h}</h4><p>{t}</p></div>'
        for tag, label, pct, h, t in HIGHLIGHT_CARDS
    )
    return (
        '<section class="block procedure" id="highlights"><div class="wrap">'
        '<div class="section-head"><p class="eyebrow center">University Highlights</p>'
        "<h2>Recognition beyond the programme</h2>"
        "<p>The accreditations and rankings behind PES University as a whole.</p></div>"
        f'<div class="imp-grid">{cards}</div></div></section>'
    )


def prescan_fees(root, cx):
    """Find the scholarship / loyalty sections anywhere in the tree, capture them, and leave a
    single slot where the combined 'Financial Support' section will be placed."""
    placed = bool(getattr(cx, "fees_placed", False))
    for n in list(root.find_all(["section", "div"])):
        if n.parent is None or not isinstance(n, Tag):
            continue
        hl = capture_highlights(n, cx)
        if hl:
            if not hasattr(cx, "slots"):
                cx.slots = []
            cx.slots.append(hl)
            slot = BeautifulSoup("", "lxml").new_tag("div")
            slot["data-html-slot"] = str(len(cx.slots) - 1)
            slot.string = "."
            n.replace_with(slot)
            continue
        try:
            hit = capture_fees(n, cx)
        except Exception:
            hit = False
        if not hit:
            continue
        if not placed:
            slot = BeautifulSoup("", "lxml").new_tag("div")
            slot["data-fees-slot"] = "1"
            slot.string = "."
            n.replace_with(slot)
            placed = True
            cx.fees_placed = True
        else:
            n.decompose()


def fees_html(cx):
    f = getattr(cx, "fees", {})
    parts = [
        '<div class="section-head"><p class="eyebrow center">Financial Support</p>'
        "<h2>Merit scholarships, awarded on performance</h2>"
        "<p>Over ₹140 crores in merit scholarships have been given to PES University students since 2014.</p></div>"
    ]
    if "sch" in f:
        cards, notes = f["sch"]
        parts.append(
            '<div class="fee-group"><div class="fee-group-head"><p class="eyebrow">Merit Scholarships</p>'
            '<span class="fee-group-note">Awarded on CGPA / SGPA</span></div>'
            f'<div class="imp-grid cols-{min(len(cards), 3)}">{"".join(cards)}</div></div>'
        )
    if "loy" in f:
        parts.append(
            '<div class="fee-group"><div class="fee-group-head"><p class="eyebrow">PES Loyalty Program</p>'
            '<span class="fee-group-note">Awarded on family / institutional ties, every year of study</span></div>'
            f'<div class="imp-grid">{"".join(f["loy"])}</div></div>'
        )
    if "sch" in f and f["sch"][1]:
        parts.append('<p class="fee-foot">' + " &middot; ".join(f["sch"][1]) + "</p>")
    return f'<section class="block fees" id="fees"><div class="wrap">{"".join(parts)}</div></section>'


# per-page eyebrow labels shown above section titles (matched on the start of the title text)
EYEBROWS = {
    "bca": [
        ("Focus Areas", "Core Subjects"),
        ("Extra-Curricular", "Beyond the Classroom"),
        ("Program Design", "Learning Approach"),
        ("Who Should Pursue", "Is It For You?"),
        ("Future Career Prospects", "Careers"),
        ("Specializations", "Choose Your Path"),
        ("Placement Opportunities", "Placements"),
        ("PES University Provides Placement", "Placement Support"),
        ("Key Differentiators", "Why PES University"),
        ("Pedagogy Method", "How We Teach"),
        ("Curriculum Structure", "Curriculum"),
    ],
    "btech": [
        ("B.Tech Major", "Branches of Engineering"),
        ("B.Tech-M.Tech Switch", "Dual Degree"),
        ("Major Minor", "Flexible Learning"),
        ("University Highlights", "Why PES University"),
    ],
}


# per-page layout overrides: (section title prefix, layout name)
GENERIC_LAYOUTS = [  # same section designs as the BCA page, chosen by heading
    ("Future Career", "career-grid"), ("Who should pursue", "checklist-split"), ("Key Differentiators", "numbered-summary"), ("Key Differentiators", "kd-tiles"),
    ("Program Design", "credit-bars"), ("Pedagogy", "ped-rows"), ("Program Focus", "focus-cols"), ("Pedagogy Method", "method-rows"), ("PES University provides Placement Assistance", "event-cards"),
]
def subject_note_below(piece):
    """"*Subject to change" is a footnote: drop its card and set the plain text under the accordion that follows."""
    if "Subject to change" not in piece or 'class="acc' not in piece:
        return piece
    soup = BeautifulSoup(f"<div id='r'>{piece}</div>", "lxml")
    root = soup.find(id="r")
    card = next((c for c in root.select(".pc-card") if "*Subject to change" in c.get_text()), None)
    acc = root.select_one(".acc")
    if card is None or acc is None:
        return piece
    note_txt = card.find("p").get_text(" ", strip=True)
    grid = card.find_parent(class_="pc-grid")
    (grid if grid is not None and len(grid.select(".pc-card")) == 1 else card).decompose()
    n = soup.new_tag("p", attrs={"class": "sub-note"})
    n.string = note_txt
    acc.insert_after(n)
    return "".join(str(c) for c in root.children)


def merge_careers(pieces):
    """bcom-hons: fold the sector sections that follow "Career Prospects" into that one section."""
    out, k = [], 0
    while k < len(pieces):
        html, heading = pieces[k]
        if heading.startswith("Career Prospects"):
            k += 1
            while k < len(pieces) and pieces[k][1] in ("Finance Sector", "Banking Sector", "Research & Consultancy"):
                html += pieces[k][0]
                k += 1
            out.append((html, heading))
            continue
        out.append((html, heading))
        k += 1
    return out


LAYOUTS = {
    "bcom": [("Career Prospects", "bcom-grid")],
    "bba": [("Curriculum Design", "bcom-path"), ("Elective", "bcom-nophoto"), ("Program Focus", "bcom-focusrows"), ("Diverse Job", "bcom-nophoto")],
    "bcom-hons": [("Why ACCA", "bcom-acca"), ("Pedagogy", "bcom-pedcols"), ("Career Prospects", "bcom-careers")],
    "bca": [("Future Career", "role-cards"), ("Focus Areas", "subject-cards"), ("Extra-Curricular", "tiles")],
    "btech": [("B.Tech Major", "vtabs"), ("Major Minor", "split-benefits"), ("B.Tech-M.Tech Switch", "btech-switch")],
    "bapa": [
        ("Key Differentiators", "bapa2-bento"), ("Programme Highlights", "bapa2-vtab"), ("Who should pursue", "bapa2-triptych"),
        ("Placement Opportunities", "bapa2-glass"), ("Specializations Domains", "bapa-domains"), ("Program Design and Delivery", "bapa2-credit"),
        ("Pedagogy Method", "bapa-overlay"), ("Future Career Prospects", "bapa2-roles"),
    ],
}


def eyebrow_for(cx, title):
    for start, label in getattr(cx, "eyebrows", []):
        if title.startswith(start):
            return label
    return ""


def sections_html(secs, cx, shade=False):
    out = []

    state = {"i": 0, "eyebrows": getattr(cx, "eyebrows", []), "layouts": LAYOUTS.get(cx.page_url.rstrip("/").rsplit("/", 1)[-1], []) + GENERIC_LAYOUTS}

    def flush(buf, shade):
        rest = "".join(buf)
        if rest.strip():
            body, _ = designer.design(rest, state)
            pieces = designer.split_sections(body)
            if any(l == "bcom-careers" for _, l in state.get("layouts", [])):
                pieces = merge_careers(pieces)
            for piece, heading in pieces:
                piece = designer.apply_page_layouts(piece, heading, state)
                dark = bool(designer.DARK_RE.search(heading)) and "cg-grid" not in piece and "cs-cols" not in piece
                cls = " dark" if dark else (" ice" if "cg-grid" in piece else (" dark" if "cp-path" in piece else " mint" if "cs-cols" in piece else " mist" if "ac-top" in piece else (" alt" if shade else "")))
                out.append(f'<section class="block content{cls}"><div class="wrap prose" data-reveal>{piece}</div></section>')
                shade = shade if dark else not shade
            return shade
        return shade

    for sec in secs:
        buf = []
        for h, _ in sec:
            if h == FEES_TOKEN or FEES_TOKEN in h:
                shade = flush(buf, shade)
                buf = [h.replace(FEES_TOKEN, "")]
                out.append(fees_html(cx))
                shade = not shade
            elif h.startswith('<section class="block'):
                shade = flush(buf, shade)
                buf = []
                out.append(h)
                shade = not shade
            else:
                buf.append(h)
        shade = flush(buf, shade)
    return out


INCLUDES = {"scholarships-at-pesu": "inc-scholarships-at-pesu", "loyalty-program": "inc-loyalty-program"}


def include_blocks(include_id, cx):
    """The live site fills these placeholder <div>s at runtime from assets/include/*.html; the
    snapshots of those includes live in tools/source/ so the content is part of the page."""
    raw = open(os.path.join(SRC, INCLUDES[include_id] + ".html"), encoding="utf-8").read()
    soup = BeautifulSoup(raw, "lxml")
    prescan_fees(soup, cx)
    out = []
    for c in (soup.body or soup).children:
        if isinstance(c, Tag) and c.name in ("script", "link", "style"):
            continue
        flatten(c, cx, out)
    return out


def flatten(n, cx, out):
    """Flatten wrapper divs/sections into a list of (html, starts_with_heading)."""
    if isinstance(n, Comment):
        return
    if isinstance(n, Tag) and n.get("id") in INCLUDES and not n.get_text(strip=True) and not n.find("img"):
        out.extend(include_blocks(n["id"], cx))
        return
    if isinstance(n, NavigableString):
        if str(n).strip():
            out.append((f"<p>{esc(str(n).strip())}</p>", False))
        return
    if n.name in SKIP or not has_content(n):
        return
    if n.has_attr("data-fees-slot"):
        out.append((FEES_TOKEN, True))
        return
    if n.has_attr("data-html-slot"):
        out.append((cx.slots[int(n["data-html-slot"])], True))
        return
    wrapper = n.name in ("div", "section", "article", "main", "span") and not has_class(n, *WRAP_STOP)
    if wrapper and has_class(n, "row"):
        cols = [c for c in n.find_all(True, recursive=False) if is_col(c) and has_content(c)]
        if len(cols) >= 2:
            wrapper = False
    if wrapper:
        kids = [c for c in n.children if not isinstance(c, Comment)]
        for c in kids:
            flatten(c, cx, out)
        return
    h = render(n, cx)
    if not h.strip():
        return
    first = n if n.name in ("h1", "h2") else n.find(["h1", "h2", "p", "ul", "ol", "table", "img", "iframe", "h3", "h4"])
    starts = bool(first is not None and first.name in ("h1", "h2") and (n.name in ("h1", "h2") or n.name not in ("p",)))
    # a multi-column row only starts a section if its first thing is the h2
    out.append((h, starts))


def split_intro(blocks):
    """Peel heading-less blocks (and heading-less columns of a mixed row) off the front of a section."""
    intro, rest = [], list(blocks)
    while rest:
        h, _ = rest[0]
        if "<h2" not in h:
            intro.append(h)
            rest.pop(0)
            continue
        if h.startswith('<div class="cols'):
            soup = BeautifulSoup(h, "lxml")
            row = soup.find("div", class_="cols")
            cols = row.find_all("div", class_="col", recursive=False)
            plain = [c for c in cols if not c.find("h2")]
            if plain and len(plain) < len(cols):
                intro.extend("".join(str(x) for x in c.children) for c in plain)
                for c in plain:
                    c.decompose()
                left = row.find_all("div", class_="col", recursive=False)
                new = "".join("".join(str(x) for x in c.children) for c in left) if len(left) == 1 else str(row)
                rest[0] = (new, True)
        break
    return "".join(intro), rest


def _bare_heading(h):
    """True when the block is nothing but a single heading element."""
    h = h.strip()
    return bool(re.match(r"^<h[12]>.*</h[12]>$", h, re.S)) and h.count("<h1") + h.count("<h2") == 1


def group_sections(blocks):
    """Every heading-led block opens a new section, unless the section so far is only a bare heading."""
    secs, cur = [], []
    for h, starts in blocks:
        if starts and cur and not all(_bare_heading(x) for x, _ in cur):
            secs.append(cur)
            cur = []
        cur.append((h, starts))
    if cur:
        secs.append(cur)
    return secs


# ----------------------------------------------------------------------------- shared chrome
ICONS = {
    "instagram": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>',
    "twitter": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 5.9c-.7.3-1.5.5-2.4.6a4.1 4.1 0 0 0 1.8-2.3c-.8.5-1.7.8-2.6 1a4.1 4.1 0 0 0-7 3.8A11.6 11.6 0 0 1 3.4 4.8a4.1 4.1 0 0 0 1.3 5.5c-.7 0-1.3-.2-1.9-.5 0 2 1.4 3.7 3.3 4.1-.6.2-1.2.2-1.9.1a4.1 4.1 0 0 0 3.8 2.8A8.2 8.2 0 0 1 2 18.2 11.6 11.6 0 0 0 8.3 20c7.5 0 11.7-6.3 11.7-11.7v-.5c.8-.6 1.5-1.3 2-2.1z"/></svg>',
    "facebook": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/></svg>',
    "share": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 13.5 6.8 4M15.4 6.5l-6.8 4"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>',
    "mouse": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="6" y="2" width="12" height="20" rx="6"/><path d="M12 6v4"/></svg>',
    "up": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m18 15-6-6-6 6"/></svg>',
}

SOCIALS = [
    ("Instagram", "https://www.instagram.com/pesuniversity/", "instagram"),
    ("Twitter", "https://www.twitter.com/pesuniversity", "twitter"),
    ("Facebook", "https://www.facebook.com/pesuniversity", "facebook"),
]


def header_html(depth):
    p = prefix(depth)
    home = (p + "index.html") if depth else "index.html"
    soc = "".join(
        f'<a href="{u}" target="_blank" rel="noopener" title="{t}" aria-label="{t}">{ICONS[i]}</a>' for t, u, i in SOCIALS
    )
    return f"""<header class="site" id="siteHeader">
  <a class="logo" href="{home}" aria-label="PES">
    <img class="logo-dark" src="{p}assets/img/logo/pesu_dark_logo.png" alt="PES" height="48">
    <img class="logo-light" src="{p}assets/img/logo/PESU-new-logo.png" alt="PES" height="48">
  </a>
  <nav class="links" id="mainNav" aria-label="Main">
    <a href="https://pes.edu/" target="_blank" rel="noopener">Back To PES</a>
  </nav>
  <div class="nav-cta">
    <a class="btn solid" href="{REGISTER}" target="_blank" rel="noopener">Apply Now</a>
    <button class="hamburger" id="hamburger" type="button" aria-label="Menu" aria-controls="mobileMenu" aria-expanded="false"><span></span><span></span><span></span></button>
  </div>
</header>
<div id="mobileBackdrop"></div>
<div id="mobileMenu" aria-label="Menu">
  <button class="close" id="closeMenu" type="button" aria-label="Close menu">&#10005;</button>
  <a href="https://pes.edu/" target="_blank" rel="noopener">Back To PES</a>
  <a class="btn solid" href="{REGISTER}" target="_blank" rel="noopener">Apply Now</a>
</div>"""


def footer_html(depth):
    soc = "".join(
        f'<a href="{u}" target="_blank" rel="noopener" title="{t}">{ICONS[i]} {t.upper()}</a>' for t, u, i in SOCIALS
    )
    # source order of the follow-us links is Facebook, Twitter, Instagram
    order = {"Facebook": 0, "Twitter": 1, "Instagram": 2}
    soc = "".join(
        f'<a href="{u}" target="_blank" rel="noopener" title="{t}">{ICONS[i]}<span>{t.upper()}</span></a>'
        for t, u, i in sorted(SOCIALS, key=lambda x: order[x[0]])
    )
    return f"""<footer class="site">
  <div class="wrap">
    <div class="foot-grid">
      <div class="foot-col"><span class="foot-ic">{ICONS['phone']}</span><h4>CALL US NOW</h4><a href="tel:+080-10-297297">080-10-297297</a></div>
      <div class="foot-col"><span class="foot-ic">{ICONS['mail']}</span><h4>ADMISSIONS</h4><a href="mailto:admissions@pes.edu">admissions@pes.edu</a></div>
      <div class="foot-col foot-follow"><span class="foot-ic">{ICONS['share']}</span><h4>FOLLOW US</h4><div class="foot-social">{soc}</div></div>
    </div>
    <div class="foot-bottom"><p>&copy; PES University | Powered by <a href="https://nith.ooo/">NiTH</a></p></div>
  </div>
</footer>
<a class="to-top" id="toTop" href="#top" aria-label="Back to top">{ICONS['up']}</a>"""


def head_html(meta, depth, extra_body=""):
    p = prefix(depth)
    desc = f'<meta name="description" content="{attr(meta["description"])}">\n' if meta.get("description") else ""
    kw = f'<meta name="keywords" content="{attr(meta["keywords"])}">\n' if meta.get("keywords") else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(meta['title'])}</title>
{desc}{kw}<meta name="author" content="PES University">
<link rel="shortcut icon" href="{p}assets/img/icons/favicon.ico" type="image/x-icon">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;0,800;0,900;1,400;1,500;1,600&family=Noto+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{p}assets/css/style.css">
<link rel="stylesheet" href="{p}assets/css/pages.css">
<link rel="stylesheet" href="{p}assets/css/responsive.css">
</head>
"""


def tail_html(depth):
    p = prefix(depth)
    return f"""<script src="{p}assets/js/main.js"></script>
<script src="{p}assets/js/pages.js"></script>
</body>
</html>
"""


def meta_of(soup):
    m = {"title": soup.title.get_text(strip=True) if soup.title else "PES University"}
    for k in ("description", "keywords"):
        t = soup.find("meta", attrs={"name": k})
        if t and t.get("content"):
            m[k] = t["content"].strip()
    return m


def mx_id(raw):
    m = re.search(r"MXLandingPageId\s*=\s*'([^']+)'", raw)
    return m.group(1) if m else ""


# ----------------------------------------------------------------------------- page builders
def find_highlights(soup, cx):
    """The page's own 'University Highlights' items (title + sentence), used to complete the island."""
    for n in soup.find_all(["section", "div"]):
        text = n.get_text(" ", strip=True)
        if text.startswith("University Highlights") and len(text) < 1500 and len(n.find_all("h4")) >= 3:
            cells = []
            for h4 in n.find_all("h4"):
                p = h4.parent.find("p")
                cells.append(
                    f'<div class="isl-item isl-hl"><div class="h" title="{attr(text_of(h4))}">{render_children(h4, cx).strip()}</div>'
                    f'<div class="s" title="{attr(text_of(p)) if p else ""}">{render_children(p, cx).strip() if p else ""}</div></div>'
                )
            return cells
    return []


def facts_to_island(ul, cx, extra_cells=(), note_html=""):
    """Island of 8 cells (2 rows x 4): the page's key facts, completed with highlight text from
    the same page (University Highlights, then the Eligibility note if still short)."""
    items = []
    for li in ul.find_all("li", recursive=False):
        inner = render_children(li, cx).strip()
        m = re.match(r"^([^:<]{1,40}:)\s*(.*)$", inner, re.S)
        if m and m.group(2):
            items.append(f'<div class="isl-item"><div class="s">{m.group(1)}</div><div class="h" title="{attr(text_of(li))}">{m.group(2)}</div></div>')
        else:
            items.append(f'<div class="isl-item"><div class="h">{inner}</div></div>')
    cells = items + list(extra_cells)
    if len(cells) < 8 and note_html:
        cells.append(f'<div class="isl-item isl-note">{note_html}</div>')
    cells = cells[:8]
    return (
        '<div class="island-shell"><div class="island-wrap"><div class="island-card" data-reveal>'
        f'<div class="isl-grid" style="--cols:4">{"".join(cells)}</div></div></div></div>'
    )


HERO_SLIDES = ["mbbs-slider-one.jpg", "mbbs-slider-two.jpg", "mbbs-slider-three.jpg"]  # placeholder hero photos


def hero_slides(depth):
    return "".join(
        f'<div class="hero-slide{" is-active" if i == 0 else ""}"><img src="{prefix(depth)}assets/img/banners/{n}" alt="" '
        f'{"fetchpriority=\"high\" " if i == 0 else "loading=\"lazy\" "}></div>'
        for i, n in enumerate(HERO_SLIDES)
    )


def build_program(slug, soup, raw):
    depth = 1
    cx = Ctx(urllib.parse.urljoin(BASE, slug + "/"), depth, "")
    cx.eyebrows = EYEBROWS.get(slug, [])
    meta = meta_of(soup)
    main = soup.find("div", role="main")
    p = prefix(depth)

    hero_sec = main.find("section", id="home")
    hero_html, island, outline_html, hero_img = "", "", "", ""
    ov_eyebrow, ov_title, ov_stats, ov_cta = "", "", "", ""
    consumed = None

    def finish_title(t):
        cx.title = t

    if hero_sec is not None:
        consumed = hero_sec
        h2s = hero_sec.find_all("h2")
        eyebrow = text_of(h2s[0]) if len(h2s) > 1 else ""
        if eyebrow.strip().lower().startswith("program outline"):
            eyebrow = "Overview"
        title_el = h2s[1] if len(h2s) > 1 else (h2s[0] if h2s else None)
        finish_title(text_of(title_el) if title_el else meta["title"])
        left = None
        for col in hero_sec.find_all(is_col):
            if title_el in col.descendants:
                left = col
                break
        right = [c for c in hero_sec.find_all(is_col) if c is not left and c.find("img")]
        img = right[0].find("img") if right else None
        if img is not None:
            hero_img = render_img(img, cx, ' class="outline-art"')
            # width/height only reserve space; CSS keeps the aspect ratio
        cta = None
        for a in left.find_all("a"):
            if "registration" in (a.get("href") or ""):
                cta = a
        ul = left.find("ul")
        rest = []
        for c in left.children:
            if c is title_el or c is (h2s[0] if len(h2s) > 1 else None) or c is ul or (cta is not None and (c is cta or cta in getattr(c, "descendants", []))):
                continue
            rest.append(c)
        extras = []
        if ul is not None:
            # malformed source markup sometimes nests headings/paragraphs inside the facts <ul>
            extras += [c for c in ul.children if isinstance(c, Tag) and c.name != "li" and not (cta is not None and (c is cta or cta in c.descendants))]
        extras += rest
        note_html = ""
        hl_cells = find_highlights(soup, cx) if ul is not None else []
        n_facts = len(ul.find_all("li", recursive=False)) if ul is not None else 0
        if ul is not None and n_facts + len(hl_cells) < 8:
            # still short of 8 cells: move the first note block (e.g. Eligibility) into the island
            hi = next((i for i, c in enumerate(extras) if isinstance(c, Tag) and c.name == "h4"), None)
            if hi is not None:
                j = hi + 1
                while j < len(extras) and not (isinstance(extras[j], Tag) and extras[j].name == "h4"):
                    j += 1
                note_html = "".join(render(c, cx) for c in extras[hi:j])
                extras = extras[:hi] + extras[j:]
        if ul is not None:
            island = facts_to_island(ul, cx, hl_cells, note_html)
        outline_html = "".join(render(c, cx) for c in extras)
        cta_html = (
            f'<a href="{attr(cta.get("href"))}" class="btn solid" target="_blank" rel="noopener">{render_children(cta, cx).strip()}</a>' if cta is not None else ""
        )
        ov_eyebrow = esc(eyebrow)
        ov_title = render_children(title_el, cx).strip()
        if cta is not None:
            ov_cta = f'<a href="{attr(cta.get("href"))}" class="btn outline" target="_blank" rel="noopener">{render_children(cta, cx).strip()}</a>'
        stat_items = []
        if ul is not None:
            for li in ul.find_all("li", recursive=False):
                m = re.match(r"^([^:]{1,40}:)\s*(.*)$", text_of(li))
                if m and m.group(2) and len(m.group(2)) <= 26 and len(stat_items) < 3:
                    stat_items.append(f'<div class="st"><div class="num">{esc(m.group(2))}</div><div class="lbl">{esc(m.group(1))}</div></div>')
        ov_stats = f'<div class="stat-row">{"".join(stat_items)}</div>' if stat_items else ""
        hero_html = f"""<section class="hero hero-slider" id="home">
    {hero_slides(depth)}
    <div class="hero-content"><div class="hero-inner">
      <div class="hero-copy-box">
        {f'<div class="eyebrow">{esc(eyebrow)}</div>' if eyebrow else ''}
        <h1 class="hero-title">{render_children(title_el, cx).strip()}</h1>
        <div class="hero-actions">{cta_html}</div>
      </div>
    </div></div>
    <div class="hero-dots" id="heroDots"></div>
  </section>"""
    else:
        h1 = main.find("h1")
        consumed = h1.find_parent("section") if h1 else None
        finish_title(text_of(h1) if h1 else meta["title"])
        strong = consumed.find("strong") if consumed else None
        sub = consumed.find("p") if consumed else None
        scroll = None
        if consumed:
            for a in consumed.find_all("a"):
                if "Scroll Down" in a.get_text():
                    scroll = a
        hero_html = f"""<section class="hero hero-slider" id="home">
    {hero_slides(depth)}
    <div class="hero-content"><div class="hero-inner">
      <div class="hero-copy-box">
        <h1 class="hero-title">{render_children(h1, cx).strip()}</h1>
        {f'<div class="eyebrow eyebrow-after">{render_children(strong, cx).strip()}</div>' if strong else ''}
        {f'<p class="hero-sub">{render_children(sub, cx).strip()}</p>' if sub else ''}
        <div class="hero-actions">{'<a href="#aboutus" class="btn outline-light scroll-down">' + ICONS['mouse'] + '<span>Scroll Down</span></a>' if scroll else ''}</div>
      </div>
    </div></div>
    <div class="hero-dots" id="heroDots"></div>
  </section>"""

    # ---- enquiry section (reference "Get in touch" block): the page's own LeadSquared form moves here
    enquire_html = ""
    lead = soup.find("iframe", src=re.compile("viewpage"))
    if lead is not None:
        src = lead.get("src", "")
        height = re.sub(r"[^0-9]", "", lead.get("height") or "") or "450"
        name = lead.get("name", "")
        lead.decompose()
        enquire_html = f"""<section class="block enquire" id="enquire">
    <div class="wrap split">
      <div data-reveal>
        <p class="eyebrow">Get In Touch</p>
        <h2>Have questions about {esc(cx.title)} admissions?</h2>
        <p>Share a few details and our admissions counsellors will walk you through eligibility, fees, scholarships and the application timeline &mdash; no obligation.</p>
        <ul class="community-list">
          <li><span class="dot"></span><span><b>Fast Response</b> &mdash; a counsellor calls back within 24 hours.</span></li>
          <li><span class="dot"></span><span><b>One-on-One Guidance</b> &mdash; personalised help with eligibility and documentation.</span></li>
          <li><span class="dot"></span><span><b>No Obligation</b> &mdash; ask questions before you decide to apply.</span></li>
        </ul>
      </div>
      <div class="enquire-card" data-reveal>
        <div class="enquire-card-head"><span class="program-tag">Enquire Now</span><p>Fill this in and we'll reach out shortly.</p></div>
        <div class="enquire-frame"><iframe{f' name="{attr(name)}"' if name else ''} src="{attr(src)}" title="Enquiry form" width="100%" height="{height}" frameborder="0" marginwidth="0" marginheight="0" scrolling="no" loading="lazy"></iframe></div>
      </div>
    </div>
  </section>"""

    # ---- remaining content
    blocks = []
    prescan_fees(main.parent, cx)
    # the original template leaves a lot of content (and the scholarship / loyalty / highlights
    # includes) as siblings *after* div[role=main]; keep everything except header and footer chrome.
    outer = [c for c in main.parent.next_siblings if isinstance(c, Tag) and c.get("id") in INCLUDES]
    for ch in list(main.children) + list(main.next_siblings) + outer:
        if ch is consumed or not isinstance(ch, Tag):
            continue
        if ch.name in ("header", "footer", "svg", "script", "style", "noscript") or has_class(ch, "footer-bg"):
            continue
        flatten(ch, cx, blocks)
    secs = group_sections(blocks)
    # the heading-less copy directly below the overview belongs to the overview section
    intro_html = ""
    if (outline_html.strip() or hero_img) and secs and not any(st for _, st in secs[0]) and not any(FEES_TOKEN in h for h, _ in secs[0]):
        intro_html, rest_blocks = split_intro(secs[0])
        secs = ([rest_blocks] if rest_blocks else []) + secs[1:]
    # a following section that repeats the programme title (title + copy) is the overview copy: merge it in
    if (outline_html.strip() or hero_img) and secs and secs[0] and re.match(r"<h2[^>]*>", secs[0][0][0].strip()):
        first_title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", secs[0][0][0])).strip().lower()
        if first_title and first_title == re.sub(r"\s+", " ", cx.title).strip().lower():
            body = "".join(h for h, _ in secs[0][1:])
            intro_html += body
            secs = secs[1:]

    out = [enquire_html] if enquire_html else []
    # overview: reference "about" block - title, intro copy, key figures, CTA and a photo collage
    if outline_html.strip() or hero_img:
        fan = []
        if hero_img:
            fan.append(f'<div class="ovp-photo ovp-0 ovp-brand">{hero_img}</div>')
        for n in ("2.jpg", "3.jpg", "4.jpg", "5.jpg")[: 4 - len(fan)]:
            fan.append(f'<div class="ovp-photo ovp-{len(fan)}"><img src="../assets/img/banners/{n}" alt="" loading="lazy"></div>')
        cta = ov_cta.replace("btn outline", "btn solid")
        out.append(
            '<section class="block overview overview-panel" id="aboutus"><div class="wrap"><div class="ovp-card" data-reveal>'
            f'<div class="ovp-copy">{f"<p class=\"eyebrow\">{ov_eyebrow}</p>" if ov_eyebrow else ""}'
            f'{f"<h2>{ov_title}</h2>" if ov_title else ""}'
            f'<div class="ovp-text">{intro_html}</div>{cta}</div>'
            f'<div class="ovp-photos">{"".join(fan)}</div></div>'
            f'{f"<div class=ovp-elig data-reveal>{outline_html}</div>" if outline_html.strip() else ""}</div></section>'
        )
    out.extend(subject_note_below(x) for x in sections_html(secs, cx))
    if not (outline_html.strip() or hero_img) and out:
        out[0] = out[0].replace('<section class="block content"', '<section class="block content" id="aboutus"', 1)

    import build_pes as bp

    body_main = "\n  ".join(out)
    # anchors for the header menu
    def tag_first(html, pattern, sid):
        m = re.search(r'<section class="block[^"]*"(?: id="[^"]*")?>(?:(?!</section>).)*?' + pattern, html, re.S | re.I)
        if not m or f'id="{sid}"' in html:
            return html
        sec = m.group(0)
        start = sec.index("<section")
        head = re.match(r'<section class="[^"]*"', sec[start:]).group(0)
        return html.replace(sec, sec[:start] + head + f' id="{sid}"' + sec[start + len(head):], 1)

    for pat, sid in ((r"<h2[^>]*>[^<]*(?:Curriculum|Course Structure|Semester|Syllabus)", "curriculum"), (r"<h2[^>]*>[^<]*(?:Career|Placement)", "careers")):
        body_main = tag_first(body_main, pat, sid)
    page = (
        bp.bca_head(meta)
        + f'<body data-mx-landing-page="{mx_id(raw)}" id="top">\n'
        + bp.bca_header()
        + "\n<main>\n  "
        + hero_html
        + "\n  "
        + island
        + "\n  "
        + body_main
        + "\n</main>\n"
        + bp.bca_footer(cx.title, next((re.sub(r"^Campus:\s*", "", text_of(li)) for li in soup.find_all("li") if text_of(li).startswith("Campus:")), "PES University"))
        + '\n<script src="js/main.js"></script>\n</body>\n</html>\n'
    )
    for sid, label in (("curriculum", "Curriculum"), ("careers", "Careers")):
        if f'id="{sid}"' not in page:  # no matching section on this page: drop that menu item
            page = re.sub(r'<a href="#%s">%s</a>' % (sid, label), "", page)
    page = bp.strip_title_colons(page)
    page = bp.localise_page_assets(page, slug)
    bp.bundle_css_js(slug)
    return page


def build_home(soup, raw):
    depth = 0
    cx = Ctx(BASE, depth, "PES University")
    meta = meta_of(soup)
    items = []
    agg = soup.find(id="aboutus")
    for a in agg.find_all("a"):
        href = a.get("href")
        loc = local_page(href, depth) or href
        label = re.sub(r"\s+", " ", a.get_text(" ", strip=True))
        items.append(f'<a class="program-link" href="{attr(loc)}" data-reveal><span>{esc(label)}</span>{ICONS["arrow"]}</a>')
    hero_img = ""
    wom = soup.find("img", src=re.compile("background-woman"))
    if wom is not None:
        hero_img = f'<img class="hero-art hero-woman" src="{localize_img(wom["src"], BASE, depth)}" alt="" width="702" height="699">'
    h1 = soup.find("h1")
    strong = soup.find(class_="custom-highlight-text-1")
    heroP = strong.find_parent("strong").find_next("p")
    discover = soup.find("h2", string=re.compile("DISCOVER"))
    ourprog = discover.find_next("h3")
    blocks = []
    for ph in soup.find_all(id=list(INCLUDES)):
        flatten(ph, cx, blocks)
    inc = "\n  ".join(subject_note_below(x) for x in sections_html(group_sections(blocks), cx, shade=True))
    page = (
        head_html(meta, depth)
        + f'<body id="top">\n'
        + header_html(depth)
        + f"""
<main>
  <section class="hero hero-page hero-home" id="home">
    <div class="hero-content"><div class="hero-inner hero-grid">
      <div class="hero-copy-box">
        <div class="eyebrow">{esc(text_of(strong))}</div>
        <h1 class="hero-title">{esc(text_of(h1))}</h1>
        <p class="hero-sub">{esc(text_of(heroP))}</p>
        <div class="hero-actions"><a href="#aboutus" class="btn solid scroll-down">{ICONS['mouse']}<span>Scroll Down</span></a></div>
      </div>
      <div class="hero-media">{hero_img}</div>
    </div></div>
  </section>
  <section class="block" id="aboutus">
    <div class="wrap">
      <div class="section-head">
        <h2 class="eyebrow center">{esc(text_of(discover))}</h2>
        <h3 class="section-title">{esc(text_of(ourprog))}</h3>
      </div>
      <div class="program-list">
        {chr(10).join(items)}
      </div>
    </div>
  </section>
  {inc}
</main>
"""
        + footer_html(depth)
        + "\n"
        + tail_html(depth)
    )
    return page


def build_reference_mbbs(raw):
    """/mbbs/ is the supplied reference design itself: reuse its markup, move its CSS/JS into assets/."""
    return None


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def main():
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    # always-needed shared assets
    for u, rel in [
        ("img/PES/favicon.ico", "assets/img/icons/favicon.ico"),
        ("img/PES/pesu-emailer-logo.png", "assets/img/logo/pesu-emailer-logo.png"),
        ("img/background-woman.png", "assets/img/banners/background-woman.png"),
    ]:
        img_queue[urllib.parse.urljoin(BASE, u)] = rel
    for slug in ["", *PAGES]:
        if only and slug not in only:
            continue
        fn = os.path.join(SRC, (slug or "home") + ".html")
        raw = open(fn, encoding="utf-8").read()
        soup = BeautifulSoup(raw, "lxml")
        if slug == "":
            write("index.html", build_home(soup, raw))
        elif slug in ("mbbs", "bbacompare", "bcom-compare", "bscjmc", "bca", "mca"):  # bca / mca are built from pes.edu by build_pes.py
            continue  # handled by tools/build_special.py
        else:
            write(f"{slug}/index.html", build_program(slug, soup, raw))
        print("built", slug or "home")
    if FETCH:
        fetch_images()
    strip_missing()
    for k, v in missing_report.items():
        print("removed missing images:", k, v)
    for w in warnings:
        print(w)


def strip_missing():
    """Remove <img> tags (and slides left empty) whose local file does not exist, i.e. assets
    that are 404 on the live site too (listed in the README)."""
    for slug in PAGES:
        fp = os.path.join(ROOT, slug, "index.html")
        if not os.path.exists(fp) or slug in ("mbbs", "bbacompare", "bcom-compare", "bscjmc", "bca", "mca"):
            continue
        t = open(fp, encoding="utf-8").read()
        o = t

        def drop(m):
            path = os.path.normpath(os.path.join(ROOT, slug, m.group(1)))
            if os.path.exists(path):
                return m.group(0)
            if slug not in missing_report:
                missing_report[slug] = []
            missing_report[slug].append(m.group(1))
            return ""

        t = re.sub(r'<img[^>]*src="(\.\./assets/img/[^"]+)"[^>]*>', drop, t)
        t = re.sub(r'<div class="slide">\s*</div>', "", t)
        if t != o:
            write(f"{slug}/index.html", t)


missing_report = {}


if __name__ == "__main__":
    main()
