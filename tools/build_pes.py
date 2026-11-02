#!/usr/bin/env python3
"""
Build campaign pages whose content comes from the main PES site (https://pes.edu/<slug>/)
instead of campaigns.pes.edu.  The WordPress page is parsed into text-preserving items and
laid out with the same design system and section designer as the other pages.

Currently: bca  (source snapshot: tools/source/pes-bca.html)
"""
import os
import re
import shutil
import sys
import urllib.parse

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402
import designer  # noqa: E402
from build import (  # noqa: E402
    ICONS, ROOT, SRC, Ctx, attr, esc, footer_html, head_html, header_html, hero_slides, render, render_children, tail_html, text_of, write,
)

PES = "https://pes.edu/"
MENU_HREFS = {"/programs/", "/departments/", "/undergraduate/", "/postgraduate/", "/research/", "/executive/", "/wilp/", "/faculty/", "/tools/", "/calendar/"}

EYEBROWS = [
    ("key differentiators", "Why PES University"),
    ("program design", "Learning Approach"),
    ("who should pursue", "Is It For You?"),
    ("focus areas", "Core Subjects"),
    ("pedagogy method", "How We Teach"),
    ("specializations", "Choose Your Path"),
    ("curriculum structure", "Curriculum"),
    ("course structure", "Curriculum"),
    ("extra", "Beyond the Classroom"),
    ("future career prospects", "Careers"),
    ("placement opportunities", "Placements"),
    ("you may also be interested in", "Explore More"),
]


def cls_of(n):
    return n.get("class", []) if isinstance(n, Tag) else []


def has(n, name):
    return any(name in c for c in cls_of(n))


def clean_soup(slug="bca"):
    raw = open(os.path.join(SRC, f"pes-{slug}.html"), encoding="utf-8").read()
    soup = BeautifulSoup(raw, "lxml")
    for t in soup(["script", "style", "noscript", "svg"]):
        t.decompose()
    for c in soup.find_all(string=lambda x: isinstance(x, Comment)):
        c.extract()
    return soup, raw


def walk(n, out):
    """Flatten the WordPress page-builder markup into ordered items."""
    for c in n.children:
        if not isinstance(c, Tag):
            continue
        if c.name in ("details", "nav"):
            continue
        if c.name == "h3":
            out.append(("h2", c))
        elif c.name in ("p", "ul", "ol", "table", "h4"):
            if c.name in ("ul", "ol") and all((li.find("a") and li.find("a").get("href") in MENU_HREFS) for li in c.find_all("li", recursive=False)):
                continue
            if c.name == "p" and not c.get_text(strip=True) and not c.find("img"):
                continue
            out.append(("el", c))
        elif c.name == "div" and any(has(k, "promo-box-item-image") for k in c.children if isinstance(k, Tag)):
            out.append(("promo", c))
        elif c.name == "div" and has(c, "gdlr-core-button-item"):
            a = c.find("a")
            if a is not None and a.get_text(strip=True):
                out.append(("button", a))
        elif c.name == "div" and has(c, "gdlr-core-media-image") and c.find("img"):
            out.append(("img", c))
        elif c.name == "div" and any(isinstance(k, NavigableString) and k.strip() for k in c.children) and not c.find(["h3", "p", "ul", "ol", "table", "img", "iframe"]):
            out.append(("text", c))  # a paragraph the page builder wrote as a bare <div>
        else:
            walk(c, out)



# per-page photos: hero slides and the overview photo fan
PAGE_IMAGES = {
    "bca": {
        "hero": ["img/bca-hero1.jpg", "img/bca-hero2.jpg", "img/bca-4.jpg"],
        "fan": ["img/bca-1.png", "img/bca-2.png", "img/bca-3.jpg", "img/bca-4.jpg"],
    },
    "mca": {
        "hero": ["img/mca-hero1.jpg", "img/mca-hero2.jpg", "img/mca-hero3.jpg"],
        "fan": ["img/mca-1.png", "img/mca-2.jpg", "img/mca-3.jpg", "img/mca-4.jpg"],
    },
}


def slides_html(srcs):
    return "".join(
        f'<div class="hero-slide{" is-active" if i == 0 else ""}"><img src="{n}" alt="" '
        f'{"fetchpriority=\"high\" " if i == 0 else "loading=\"lazy\" "}></div>'
        for i, n in enumerate(srcs)
    )


NAV = [("Overview", "#aboutus"), ("Curriculum", "#curriculum"), ("Careers", "#careers"), ("Fees", "#fees"), ("Highlights", "#highlights")]
REGISTER = "https://admissions.pes.edu/registration/"


def bca_head(meta):
    desc = f'<meta name="description" content="{attr(meta["description"])}">\n' if meta.get("description") else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(meta['title'])}</title>
{desc}<meta name="author" content="PES University">
<link rel="shortcut icon" href="img/pesu_icons/favicon.ico" type="image/x-icon">
<link rel="apple-touch-icon" sizes="57x57" href="img/pesu_icons/apple-icon-57x57.png">
<link rel="apple-touch-icon" sizes="60x60" href="img/pesu_icons/apple-icon-60x60.png">
<link rel="apple-touch-icon" sizes="72x72" href="img/pesu_icons/apple-icon-72x72.png">
<link rel="apple-touch-icon" sizes="76x76" href="img/pesu_icons/apple-icon-76x76.png">
<link rel="apple-touch-icon" sizes="114x114" href="img/pesu_icons/apple-icon-114x114.png">
<link rel="apple-touch-icon" sizes="120x120" href="img/pesu_icons/apple-icon-120x120.png">
<link rel="apple-touch-icon" sizes="144x144" href="img/pesu_icons/apple-icon-144x144.png">
<link rel="apple-touch-icon" sizes="152x152" href="img/pesu_icons/apple-icon-152x152.png">
<link rel="apple-touch-icon" sizes="180x180" href="img/pesu_icons/apple-icon-180x180.png">
<link rel="icon" type="image/png" sizes="192x192" href="img/pesu_icons/android-icon-192x192.png">
<link rel="icon" type="image/png" sizes="32x32" href="img/pesu_icons/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="96x96" href="img/pesu_icons/favicon-96x96.png">
<link rel="icon" type="image/png" sizes="16x16" href="img/pesu_icons/favicon-16x16.png">
<meta name="msapplication-TileColor" content="#ffffff">
<meta name="msapplication-TileImage" content="img/pesu_icons/ms-icon-144x144.png">
<meta name="theme-color" content="#ffffff">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;0,800;0,900;1,400;1,500;1,600&family=Noto+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/style.css">
</head>
"""


def bca_header():
    links = "".join(f'<a href="{h}">{t}</a>' for t, h in NAV)
    return f"""<header class="site" id="siteHeader">
  <a class="logo" href="../index.html" aria-label="PES University">
    <img class="logo-dark" src="../assets/img/logo/pesu_dark_logo.png" alt="PES University" height="48">
    <img class="logo-light" src="../assets/img/logo/PESU-new-logo.png" alt="PES University" height="48">
  </a>
  <nav class="links" id="mainNav" aria-label="Main">{links}</nav>
  <div class="nav-cta">
    <a class="btn solid" href="{REGISTER}" target="_blank" rel="noopener">Apply Now</a>
    <button class="hamburger" id="hamburger" type="button" aria-label="Menu" aria-controls="mobileMenu" aria-expanded="false"><span></span><span></span><span></span></button>
  </div>
</header>
<div id="mobileBackdrop"></div>
<div id="mobileMenu" aria-label="Menu">
  <button class="close" id="closeMenu" type="button" aria-label="Close menu">&#10005;</button>
  {links}
  <a class="btn solid" href="{REGISTER}" target="_blank" rel="noopener">Apply Now</a>
</div>"""


def bca_footer(title_text, campus):
    return f"""<footer class="site bca-footer">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <div class="foot-logo"><img src="../assets/img/logo/pesu_dark_logo.png" alt="PES University" style="height:40px;width:auto;"></div>
        <p class="foot-about">{esc(campus)}, Bengaluru &mdash; NAAC A+ Accredited, UGC approved. Home to the {esc(title_text)} programme.</p>
      </div>
      <div class="foot-col">
        <h4>Programme</h4>
        {"".join(f'<a href="{h}">{t}</a>' for t, h in NAV)}
      </div>
      <div class="foot-col">
        <h4>Admissions</h4>
        <a href="{REGISTER}" target="_blank" rel="noopener">Register</a>
        <a href="#aboutus">Eligibility</a>
        <a href="mailto:admissions@pes.edu">Email Admissions</a>
      </div>
      <div class="foot-col">
        <h4>Contact</h4>
        <div class="contact-line">{esc(campus)},<br>Bengaluru, Karnataka</div>
        <a href="tel:08010297297">080-10-297297</a>
        <a href="mailto:admissions@pes.edu">admissions@pes.edu</a>
      </div>
    </div>
    <div class="foot-bottom">
      <span>&copy; 2026 PES University.</span>
      <span>NAAC A+ Accredited &middot; UGC Approved</span>
    </div>
  </div>
</footer>
<a href="#top" class="to-top" id="toTop" aria-label="Back to top">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
</a>"""


def strip_title_colons(page):
    """No trailing colon on card titles (h4 headings and island titles)."""
    def clean(m):
        inner_html = re.sub(r"\s*:\s*((?:</\w+>)*)\s*$", lambda k: k.group(1), m.group(2))
        return m.group(1) + inner_html + m.group(3)

    page = re.sub(r"(<h4[^>]*>)(.*?)(</h4>)", clean, page, flags=re.S)
    page = re.sub(r'(<div class="h"[^>]*>)(.*?)(</div>)', clean, page, flags=re.S)
    page = re.sub(r'(<div class="h" title="[^"]*?)\s*:\s*(")', lambda k: k.group(1) + k.group(2), page)
    return page


def localise_page_assets(page, slug):
    """Copy every image the page uses into <slug>/img/ and point the HTML there."""
    out_dir = os.path.join(ROOT, slug, "img")
    os.makedirs(out_dir, exist_ok=True)
    seen = {}

    def sub(m):
        rel = m.group(2)
        if rel in seen:
            return m.group(1) + seen[rel]
        src = os.path.join(ROOT, rel)
        name = os.path.basename(rel)
        if os.path.exists(src):
            dest = os.path.join(out_dir, name)
            if os.path.exists(dest) and os.path.getsize(dest) != os.path.getsize(src):
                name = rel.split("/")[-2] + "-" + name
                dest = os.path.join(out_dir, name)
            shutil.copyfile(src, dest)
            seen[rel] = "img/" + name
            return m.group(1) + seen[rel]
        return m.group(0)

    icons = os.path.join(ROOT, "assets", "img", "pesu_icons")
    if os.path.isdir(icons):
        shutil.copytree(icons, os.path.join(out_dir, "pesu_icons"), dirs_exist_ok=True)
    return re.sub(r'(["\'(])(?:\.\./)+(assets/img/[^"\')\s]+)', sub, page)


def bundle_css_js(slug):
    """Page-only stylesheet and script: shared building blocks + the page rules below."""
    css = "\n".join(open(os.path.join(ROOT, "assets", "css", f), encoding="utf-8").read() for f in ("style.css", "pages.css", "responsive.css"))
    css += BCA_CSS
    write(f"{slug}/css/style.css", css)
    js = "\n".join(open(os.path.join(ROOT, "assets", "js", f), encoding="utf-8").read() for f in ("main.js", "pages.js"))
    write(f"{slug}/js/main.js", js)


BCA_CSS = """
/* ===== BCA / MCA: header identical to the mbbs reference (20px 40px, shrinks to 13px on scroll) on desktop and tablet ===== */
header.site { padding: 20px 40px; }
@media (max-width: 600px) { header.site { padding: 18px 22px; } header.site.scrolled { padding: 13px 22px; } }

/* ===== BCA / MCA: tablet + mobile header = menu toggle (hamburger) with the same links and behaviour as desktop ===== */
.links a.is-current, #mobileMenu a.is-current { color: var(--orange); }
nav.links > a.is-current::after { width: 100%; }
@media (max-width: 1040px) { .nav-cta .btn { display: inline-flex; } }
/* smaller buttons on tablet / mobile */
@media (max-width: 640px) {
  .btn { padding: 9px 16px; font-size: 12.5px; gap: 6px; }
  .nav-cta .btn { padding: 8px 14px; font-size: 12.5px; }
  .hero-actions { gap: 10px; margin-top: 22px; }
  .hero-actions .btn { width: auto; }
  .btn svg { width: 15px; height: 15px; }
  .slider-btn { width: 38px; height: 38px; }
  .tab-btn, .ctabs .tab-btn { padding: 8px 14px; font-size: 12.5px; }
  .to-top { width: 40px; height: 40px; }
}

/* ===== BCA page only: reference (mbbs) mobile header: logo, Apply Now and menu button stay visible ===== */
@media (max-width: 1040px) { .nav-cta .btn { display: inline-flex; } }

/* ===== BCA hero: the two labels share one line, separated by a comma ===== */
.eyebrow-one { margin-bottom: 18px; display: block; }
.eyebrow-one::before { display: inline-block; vertical-align: middle; margin-right: 9px; }
.eyebrow-one a { color: inherit; }
.eyebrow-row { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 28px; margin-bottom: 18px; }
.eyebrow-row .eyebrow, .eyebrow-row .eyebrow-caption { margin: 0; }
.eyebrow-row .eyebrow a { color: inherit; }

/* ===== BCA page only: reference-style footer ===== */
.bca-footer { background: var(--navy-deep); color: rgba(255, 255, 255, 0.7); padding: 70px 0 30px; }
.bca-footer .foot-grid { display: grid; grid-template-columns: 1.4fr 1fr 1fr 1fr; gap: 40px; padding-bottom: 50px; border-bottom: 1px solid rgba(255, 255, 255, 0.12); justify-content: stretch; flex-wrap: nowrap; }
.bca-footer .foot-about { margin-top: 16px; font-size: 13.5px; line-height: 1.7; max-width: 34ch; color: rgba(255, 255, 255, 0.55); }
.bca-footer .foot-col { display: block; }
.bca-footer .foot-col h4 { font-size: 12px; font-weight: 800; letter-spacing: 0.06em; text-transform: uppercase; color: rgba(255, 255, 255, 0.4); margin-bottom: 16px; }
.bca-footer .foot-col > a { display: block; font-size: 14px; font-weight: 500; padding: 6px 0; color: rgba(255, 255, 255, 0.75); transition: color 0.2s ease; }
.bca-footer .foot-col > a:hover { color: var(--orange-light); }
.bca-footer .contact-line { font-size: 13.5px; line-height: 1.7; color: rgba(255, 255, 255, 0.75); padding: 6px 0; }
.bca-footer .foot-bottom { padding-top: 26px; display: flex; justify-content: space-between; font-size: 12px; color: rgba(255, 255, 255, 0.4); flex-wrap: wrap; gap: 10px; text-align: left; }
@media (max-width: 850px) { .bca-footer .foot-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 600px) { .bca-footer { padding: 56px 0 26px; } .bca-footer .foot-grid { gap: 36px 28px; } .bca-footer .foot-bottom { flex-direction: column; gap: 8px; padding-right: 60px; } }
"""


def build_page(slug):
    depth = 1
    imgs = PAGE_IMAGES[slug]
    soup, raw = clean_soup(slug)
    wrapper = soup.find(class_="kingster-page-wrapper")
    for el in wrapper.select(".gdlr-core-hide-in-desktop-tablet"):  # mobile-only duplicates
        el.decompose()
    title_text = ""
    cx = Ctx(PES + slug + "/", depth, title_text)
    cx.eyebrows = []

    # ---- hero parts ------------------------------------------------------------------
    h3s = wrapper.find_all("h3", class_=lambda c: c and "gdlr-core-title-item-title" in c)
    eyebrow_h3 = next(h for h in h3s if h.find("a"))
    caption = eyebrow_h3.find_parent(class_="gdlr-core-title-item").find(class_="gdlr-core-title-item-caption")
    title_h3 = h3s[h3s.index(eyebrow_h3) + 1]
    title_txt = text_of(title_h3)
    title_text = title_txt
    cx.title = title_txt
    iframe = wrapper.find("iframe")
    lead_src, lead_h = iframe.get("src", ""), re.sub(r"[^0-9]", "", iframe.get("height") or "") or "450"
    lead_name = iframe.get("name", "")
    btns = [a for a in wrapper.select(".gdlr-core-button-item a")][:2]
    outline = wrapper.find("table", class_=None) if False else wrapper.select_one(".program-outline-table table")
    facts = []
    for tr in outline.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) == 2:
            facts.append((text_of(tds[0]), text_of(tds[1])))
    outline_ps = [text_of(p) for p in outline.find_all("p")]  # ["Program Outline", title]
    outline_box = outline.find_parent(class_="gdlr-core-text-box-item")
    column = outline_box.find_parent(class_="gdlr-core-pbf-column-content") or outline_box.parent
    intro_ps = [p for p in column.find_all("p") if p.find_parent(class_="program-outline-table") is None and p.get_text(strip=True)]
    intro_p = intro_ps[0] if intro_ps else None
    eb_a = eyebrow_h3.find("a")
    hero_eyebrow = f'<a href="{attr(urllib.parse.urljoin(PES, eb_a.get("href")))}">{esc(text_of(eyebrow_h3))}</a>'
    caption_text = text_of(caption) if caption is not None else ""
    btn_html = "".join(
        f'<a href="{attr(urllib.parse.urljoin(PES, b.get("href")))}" class="btn {"solid" if k == 1 else "outline-light"}" target="_blank" rel="noopener">{render_children(b, cx).strip()}</a>'
        for k, b in enumerate(btns)
    )
    register_href = btns[1].get("href") if len(btns) > 1 else "https://admissions.pes.edu/"
    register_text = render_children(btns[1], cx).strip() if len(btns) > 1 else "Register for Admissions"
    intro_html = "".join(render(p, cx) for p in intro_ps)
    campus = next((v for l, v in facts if l.lower() == "campus"), "Ring Road (RR) Campus")

    # remove hero parts so the remaining walk only sees section content
    for node in (eyebrow_h3.find_parent(class_="gdlr-core-title-item"), title_h3.find_parent(class_="gdlr-core-title-item"), iframe, outline.find_parent(class_="gdlr-core-text-box-item")):
        if node is not None:
            node.decompose()
    for p_ in intro_ps:
        p_.decompose()
    for b in btns:
        b.find_parent(class_="gdlr-core-button-item").decompose()

    # ---- ordered content items --------------------------------------------------------
    items = []
    walk(wrapper, items)
    sections, cur = [], None
    for kind, node in items:
        if kind == "h2":
            cur = {"title": node, "items": []}
            sections.append(cur)
        elif cur is not None:
            cur["items"].append((kind, node))
        else:
            sections.append({"title": None, "items": [(kind, node)]})
            cur = sections[-1]

    # key differentiators -> island cells
    diffs = []
    for sec in sections:
        if sec["title"] is not None and text_of(sec["title"]).lower().startswith("key differentiators"):
            for kind, node in sec["items"]:
                if kind == "el" and node.name == "ul":
                    for li in node.find_all("li", recursive=False):
                        st = li.find(["strong", "b"])
                        if st is not None and li.index(st) <= 1:
                            body = text_of(li)[len(text_of(st)):]
                            colon = ":" if body.lstrip().startswith(":") else ""
                            body = re.sub(r"^\s*:\s*", "", body)
                            diffs.append((render_children(st, cx).strip() + colon, esc(body), text_of(st) + colon, body))

    # row 1: the first four facts; row 2: the University Highlights (rankings / accreditation)
    row1 = facts[:4]
    extra_facts = facts[4:]  # e.g. Approval Body -> shown in the hero instead of the island
    cells = [
        f'<div class="isl-item"><div class="s">{esc(l)}</div><div class="h" title="{attr(v)}">{esc(v)}</div></div>' for l, v in row1
    ]
    for k, (tag, label, pct, h, t) in enumerate(build.HIGHLIGHT_CARDS):
        if k == 2 and extra_facts:  # the B-School ranking cell makes room for the Approval Body fact
            l, v = extra_facts[0]
            cells.append(f'<div class="isl-item"><div class="s">{esc(l)}</div><div class="h" title="{attr(v)}">{esc(v)}</div></div>')
            continue
        cells.append(
            f'<div class="isl-item isl-hl"><div class="h" title="{attr(pct + " " + h)}">{esc(pct)}</div><div class="s" title="{attr(t)}">{esc(h)}</div></div>'
        )
    island = (
        '<div class="island-shell"><div class="island-wrap"><div class="island-card" data-reveal>'
        f'<div class="isl-grid" style="--cols:4">{"".join(cells[:8])}</div></div></div></div>'
    )

    # ---- hero + enquire + overview ----------------------------------------------------
    hero = f"""<section class="hero hero-slider" id="home">
    {slides_html(imgs["hero"])}
    <div class="hero-content"><div class="hero-inner">
      <div class="hero-copy-box">
        <div class="eyebrow eyebrow-one">{hero_eyebrow}{f', {esc(caption_text)}' if caption_text else ''}</div>
        <h1 class="hero-title">{esc(title_txt)}</h1>
        <div class="hero-actions">{btn_html}</div>
      </div>
    </div></div>
    <div class="hero-dots" id="heroDots"></div>
  </section>"""

    enquire = f"""<section class="block enquire" id="enquire">
    <div class="wrap split">
      <div data-reveal>
        <p class="eyebrow">Get In Touch</p>
        <h2>Have questions about {esc(title_text)} admissions?</h2>
        <p>Share a few details and our admissions counsellors will walk you through eligibility, fees, scholarships and the application timeline &mdash; no obligation.</p>
        <ul class="community-list">
          <li><span class="dot"></span><span><b>Fast Response</b> &mdash; a counsellor calls back within 24 hours.</span></li>
          <li><span class="dot"></span><span><b>One-on-One Guidance</b> &mdash; personalised help with eligibility and documentation.</span></li>
          <li><span class="dot"></span><span><b>No Obligation</b> &mdash; ask questions before you decide to apply.</span></li>
        </ul>
      </div>
      <div class="enquire-card" data-reveal>
        <div class="enquire-card-head"><span class="program-tag">Enquire Now</span><p>Fill this in and we'll reach out shortly.</p></div>
        <div class="enquire-frame"><iframe{f' name="{attr(lead_name)}"' if lead_name else ''} src="{attr(lead_src)}" title="Enquiry form" width="100%" height="{lead_h}" frameborder="0" marginwidth="0" marginheight="0" scrolling="no" loading="lazy"></iframe></div>
      </div>
    </div>
  </section>"""

    stat_items = [(l, v) for l, v in facts if len(v) <= 26][:3]
    stats = "".join(f'<div class="st"><div class="num">{esc(v)}</div><div class="lbl">{esc(l)}</div></div>' for l, v in stat_items)
    tiles = "".join(f'<div class="ph"><img src="../assets/img/banners/{n}" alt="" loading="lazy"></div>' for n in ("2.jpg", "3.jpg", "4.jpg", "5.jpg"))
    fan = "".join(f'<div class="ovp-photo ovp-{k}"><img src="{n}" alt="" loading="lazy"></div>' for k, n in enumerate(imgs["fan"]))
    overview = f"""<section class="block overview overview-panel" id="aboutus"><div class="wrap">
      <div class="ovp-card" data-reveal>
        <div class="ovp-copy"><p class="eyebrow">Overview</p><h2>{esc(outline_ps[-1] if outline_ps else title_text)}</h2>
          <div class="ovp-text">{intro_html}</div>
          <a href="{attr(register_href)}" class="btn solid" target="_blank" rel="noopener">{register_text}</a></div>
        <div class="ovp-photos">{fan}</div>
      </div></div></section>"""

    # ---- sections ----------------------------------------------------------------------
    out = [enquire, overview]
    state = {"i": 0, "eyebrows": [], "layouts": [("Future Career", "career-grid"), ("Who should pursue", "checklist-split"), ("Key Differentiators", "numbered-summary"), ("Program Design", "credit-bars"), ("Pedagogy Method", "method-rows"), ("PES University provides Placement Assistance", "event-cards")]}
    shade = False
    seen_assist = 0
    pending_h2 = ""

    def eyebrow_html(title):
        t = title.lower()
        if t.startswith("pes university provides placement"):
            nonlocal seen_assist
            seen_assist += 1
            label = "Placement Support" if seen_assist == 1 else "Our Recruiters"
        else:
            label = next((l for p, l in EYEBROWS if t.startswith(p)), "")
        return f'<p class="eyebrow center">{label}</p>' if label else ""

    def render_items(sec_items):
        html, logos = [], []
        for kind, node in sec_items:
            if kind == "el":
                if node.name == "table":
                    first = node.find("tr")
                    if node.find("thead") is None and first is not None and text_of(first).lower().startswith("course"):
                        for td in first.find_all("td"):
                            td.name = "th"
                    html.append(render(node, cx))
                else:
                    html.append(render(node, cx))
            elif kind == "text":
                html.append(f"<p>{render_children(node, cx).strip()}</p>")
            elif kind == "img":
                img = node.find("img")
                logos.append(f'<div class="logo-tile">{build.render_img(img, cx)}</div>')
            elif kind == "button":
                html.append(f'<p class="sec-cta"><a class="btn outline" href="{attr(urllib.parse.urljoin(PES, node.get("href")))}" target="_blank" rel="noopener">{render_children(node, cx).strip()}</a></p>')
        if logos:
            dup = "".join(re.sub(r'alt="[^"]*"', 'alt=""', l) for l in logos)
            html.append(
                '<div class="logo-marquee" aria-label="Recruiters"><div class="logo-track">'
                f'{"".join(logos)}<span class="logo-dup" aria-hidden="true">{dup}</span></div></div>'
            )
        return "".join(html)

    def promo_card(node, wide=False):
        img = node.find(class_=lambda c: c and "promo-box-item-image" in c).find("img")
        h3 = node.find("h3")
        p = node.find("p")
        a = p.find("a") if p is not None else None
        href = urllib.parse.urljoin(PES, a.get("href")) if a is not None and a.get("href") else ""
        # body text = paragraph without the (empty) arrow link
        if a is not None:
            a.decompose()
        body = render_children(p, cx).strip() if p is not None else ""
        body = re.sub(r"(<br>\s*)+$", "", body)
        tag, end = (f'a href="{attr(href)}" target="_blank" rel="noopener"', "a") if href else ("div", "div")
        return (
            f'<{tag} class="promo-card" data-reveal><div class="promo-img">{build.render_img(img, cx)}</div>'
            f'<div class="promo-body"><h3>{render_children(h3, cx).strip()}</h3><p>{body}</p>'
            f'{"<span class=promo-arrow>" + ICONS["arrow"] + "</span>" if href else ""}</div></{end}>'
        )

    info_cards = []  # Placements / Attend a Session / Study at PES

    def flush_info():
        nonlocal shade
        if info_cards:
            out.append(f'<section class="block content{" alt" if shade else ""}"><div class="wrap"><div class="info-row">{"".join(info_cards)}</div></div></section>')
            shade = not shade
            info_cards.clear()

    for sec in sections:
        title = text_of(sec["title"]) if sec["title"] is not None else ""
        kinds = [k for k, _ in sec["items"]]
        tl = title.lower()
        if tl in ("placements", "attend a session", "study at pes") or tl.startswith("you may also be interested") or (kinds and all(k == "promo" for k in kinds) and not title):
            continue  # dropped on request: replaced by the Financial Support and University Highlights sections
        if tl in ("placements", "attend a session", "study at pes"):
            body_html = "".join(render(n, cx) for k, n in sec["items"] if k == "el")
            btn = "".join(
                f'<a class="btn outline" href="{attr(urllib.parse.urljoin(PES, n.get("href")))}" target="_blank" rel="noopener">{render_children(n, cx).strip()}</a>'
                for k, n in sec["items"]
                if k == "button"
            )
            info_cards.append(f'<div class="info-card" data-reveal><h3>{esc(title)}</h3>{body_html}{btn}</div>')
            continue
        flush_info()
        if kinds and all(k == "promo" for k in kinds) and not title:
            cards = "".join(promo_card(n) for _, n in sec["items"])
            out.append(f'<section class="block content{" alt" if shade else ""}"><div class="wrap"><div class="promo-grid promo-2">{cards}</div></div></section>')
            shade = not shade
            continue
        if tl.startswith("you may also be interested"):
            cards = "".join(promo_card(n) for k, n in sec["items"] if k == "promo")
            out.append(
                f'<section class="block content{" alt" if shade else ""}"><div class="wrap prose"><p class="eyebrow center">Explore More</p>'
                f'<h2>{render_children(sec["title"], cx).strip()}</h2><div class="promo-grid promo-3">{cards}</div></div></section>'
            )
            shade = not shade
            continue
        # regular section: split off trailing promos (they follow the recruiter logos)
        reg = [(k, n) for k, n in sec["items"] if k != "promo"]
        if sec["title"] is not None and not reg:
            pending_h2 = f"<h2>{render_children(sec['title'], cx).strip()}</h2>"
            continue
        logo_items = [(k, n) for k, n in reg if k == "img"]
        extra_logo_section = None  # logos stay in the same section as their heading and text
        promos = [n for k, n in sec["items"] if k == "promo"]
        if sec["title"] is None:
            body = render_items(reg)
        else:
            body = pending_h2 + eyebrow_html(title) + f"<h2>{render_children(sec['title'], cx).strip()}</h2>" + render_items(reg)
            pending_h2 = ""
        if body.strip():
            designed, _ = designer.design(body, state)
            warm = False
            career = tl.startswith("future career")  # shares the specialisations background (alt)
            dark = bool(designer.DARK_RE.search(title)) and not career
            assist = tl.startswith("pes university provides placement") and not any(k == "img" for k, _ in sec["items"])
            if assist:
                dark = False
            cls = "" if assist else (" alt" if career else (" dark" if dark else (" alt" if shade else "")))
            sec_id = ' id="curriculum"' if tl.startswith(("curriculum structure", "course structure")) else (' id="careers"' if career else "")
            out.append(f'<section class="block content{cls}"{sec_id}><div class="wrap prose" data-reveal>{designed}</div></section>')
            if not dark and not warm:
                shade = not shade
        if extra_logo_section:
            lg, _ = designer.design('<p class="eyebrow center">Our Recruiters</p>' + render_items(extra_logo_section), state)
            out.append(f'<section class="block content dark"><div class="wrap prose" data-reveal>{lg}</div></section>')
        if False and promos:
            cards = "".join(promo_card(n) for n in promos)
            out.append(f'<section class="block content{" alt" if shade else ""}"><div class="wrap"><div class="promo-grid promo-2">{cards}</div></div></section>')
            shade = not shade
    flush_info()

    # Financial Support (merit scholarships + loyalty) and University Highlights, as on the other pages
    fx = Ctx(build.BASE + slug + "/", depth, title_text)
    for inc in ("inc-scholarships-at-pesu", "inc-loyalty-program"):
        isoup = BeautifulSoup(open(os.path.join(SRC, inc + ".html"), encoding="utf-8").read(), "lxml")
        build.prescan_fees(isoup, fx)
    out.append(build.fees_html(fx))
    hl_cards = "".join(
        f'<div class="imp-card" data-reveal><span class="imp-tag {tag}">{label}</span><div class="pct">{pct}</div><h4>{h}</h4><p>{t}</p></div>'
        for tag, label, pct, h, t in build.HIGHLIGHT_CARDS
    )
    out.append(
        '<section class="block procedure" id="highlights"><div class="wrap">'
        '<div class="section-head"><p class="eyebrow center">University Highlights</p><h2>Recognition beyond the programme</h2>'
        '<p>The accreditations and rankings behind PES University as a whole.</p></div>'
        f'<div class="imp-grid">{hl_cards}</div></div></section>'
    )

    title_tag = soup.title.get_text(strip=True) if soup.title else title_text + " - PES University"
    meta = {"title": title_tag}
    m = soup.find("meta", attrs={"name": "description"})
    if m and m.get("content"):
        meta["description"] = m["content"].strip()
    mx = re.search(r"MXLandingPageId\s*=\s*'([^']+)'", raw)
    page = (
        bca_head(meta)
        + f'<body data-mx-landing-page="{mx.group(1) if mx else ""}" id="top">\n'
        + bca_header()
        + "\n<main>\n  "
        + hero
        + "\n  "
        + island
        + "\n  "
        + "\n  ".join(out)
        + "\n</main>\n"
        + bca_footer(title_text, campus)
        + '\n<script src="js/main.js"></script>\n</body>\n</html>\n'
    )
    page = strip_title_colons(page)
    page = localise_page_assets(page, slug)
    bundle_css_js(slug)
    write(f"{slug}/index.html", page)
    print(f"built {slug} from pes.edu")


if __name__ == "__main__":
    for sl in (sys.argv[1:] or ["bca", "mca"]):
        build_page(sl)
    build.fetch_images()
    build.strip_missing()
    for w in build.warnings:
        print(w)
