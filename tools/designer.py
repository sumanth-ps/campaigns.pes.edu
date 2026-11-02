"""
Content-aware section designer.

Takes the already-converted, text-preserving HTML of one content section and re-lays it out with
the component that suits its structure (reference design system): icon cards for multi-column
copy, feature cards for bold-led lists, chip clouds for long lists of short items, testimonial
cards for quotes, a dark band for career sections.  Wording is never altered; only wrappers and
icons are added.
"""
import re

from bs4 import BeautifulSoup, NavigableString, Tag

ICON_PATHS = [
    '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
    '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M8 2v4M16 2v4M3 10h18"/>',
    '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
    '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    '<circle cx="9" cy="7" r="4"/><path d="M2 21v-2a4 4 0 0 1 4-4h6a4 4 0 0 1 4 4v2M16 3.13a4 4 0 0 1 0 7.75M22 21v-2a4 4 0 0 0-3-3.87"/>',
    '<circle cx="12" cy="8" r="6"/><path d="M15.5 13 17 22l-5-3-5 3 1.5-9"/>',
    '<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/>',
    '<circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15 15 0 0 1 0 20M12 2a15 15 0 0 0 0 20"/>',
    '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    '<path d="m12 3 1.9 5.8L20 10l-5 3.7L16.8 20 12 16.4 7.2 20 9 13.7 4 10l6.1-1.2z"/>',
]


def icon(i):
    return (
        '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        + ICON_PATHS[i % len(ICON_PATHS)]
        + "</svg>"
    )


def inner(n):
    return "".join(str(c) for c in n.children)


def text(n):
    return re.sub(r"\s+", " ", n.get_text(" ", strip=True)).strip()


def real_kids(n):
    return [c for c in n.children if not (isinstance(c, NavigableString) and not str(c).strip())]


def lead_title(n):
    """Heading-like element (h3-h6, or a <p> that is only bold text) -> its inner html, else None."""
    if not isinstance(n, Tag):
        return None
    if n.name in ("h3", "h4", "h5", "h6"):
        return inner(n)
    if n.name == "p":
        kids = real_kids(n)
        if len(kids) == 1 and isinstance(kids[0], Tag) and kids[0].name in ("strong", "b"):
            return inner(kids[0])
    return None


def bold_lead(li):
    """<li><b>Title:</b> rest</li> -> (title_html, rest_html), else None.
    Adjacent bold pieces (source typos like <b>I</b><b>nvited ...</b>) are joined into one title."""
    kids = real_kids(li)
    lead = []
    for c in kids:
        if isinstance(c, Tag) and c.name in ("strong", "b"):
            lead.append(c)
        else:
            break
    if lead and len(kids) > len(lead) and len(re.sub(r"<[^>]+>", "", "".join(inner(c) for c in lead)).strip()) >= 3:
        title = "".join(inner(c) for c in lead).strip()
        rest = "".join(str(c) for c in kids[len(lead):]).strip()
        m = re.match(r"^([a-z][^:<]{0,40}):", rest)
        if m and not rest.startswith(" "):  # the bold part was cut mid-word in the source ("Plac" + "ement ...")
            title += m.group(1)
            rest = rest[m.end() - 1:]
        if re.match(r"^\s*:", rest):
            # keep the source colon: it moves to the end of the title
            rest = re.sub(r"^\s*:\s*", "", rest)
            if not title.endswith(":"):
                title += ":"
        return title, rest
    return None


COMPLEX = ("facility-grid", "chip-cloud", "tbl-wrap", "class=\"acc", "slider", "testi-grid", "<iframe", "pillars", "sem-acc")


def story_rows(cols, state):
    """Columns that each open with their own title -> one flat block per column (so every title gets its own
    section): eyebrow, centred title, then the paragraphs as numbered cards."""
    out = []
    for col in cols:
        kids = real_kids(col)
        h2 = kids[0]
        label = eyebrow_for(state, h2)
        paras = [c for c in kids[1:] if isinstance(c, Tag) and c.name == "p"]
        others = [c for c in kids[1:] if not (isinstance(c, Tag) and c.name == "p")]
        if text(h2).lower().startswith("our legacy"):
            # story layout: copy on one side, two overlapping photos on the other, with scroll animation (no cards)
            body = "".join(f"<p>{inner(c)}</p>" for c in paras)
            out.append(
                f'<p class="eyebrow center">{label}</p>{h2}'
                f'<div class="lg-split" data-reveal><div class="lg-copy">{body}</div>'
                '<div class="lg-photos" aria-hidden="true"><span class="lg-ring"></span><span class="lg-dots"></span>'
                '<img class="lg-a" src="../assets/img/banners/3.jpg" alt="" loading="lazy">'
                '<img class="lg-b" src="../assets/img/banners/4.jpg" alt="" loading="lazy"></div></div>'
            )
            continue
        cards = "".join(
            f'<article class="pc-card" data-reveal><span class="pc-num">{k + 1:02d}</span><div class="pc-ic">{icon(state["i"] + k)}</div><p>{inner(c)}</p></article>'
            for k, c in enumerate(paras)
        )
        state["i"] += len(paras)
        grid_cls = "pc-grid pc-grid-3" if len(paras) % 3 == 0 else "pc-grid"
        grid_html = f'<div class="{grid_cls}">{cards}</div>' if cards else ""
        out.append(f'<p class="eyebrow center">{label}</p>{h2}{grid_html}{render_nodes(others, state)}')
    return "".join(out)


def make_pillars(cols, state):
    # a column that only holds the section title (h2) is the heading, not a card: lift it out, centred
    lifted = ""
    if len(cols) > 2:
        first = real_kids(cols[0])
        if first and all(isinstance(k, Tag) and (k.name == "h2" or "eyebrow" in k.get("class", [])) for k in first) and any(k.name == "h2" for k in first):
            h2 = next(k for k in first if k.name == "h2")
            label = eyebrow_for(state, h2)
            lifted = (f'<p class="eyebrow center">{label}</p>' if label else "") + str(h2)
            cols = cols[1:]
    parts = []
    for col in cols:
        kids = real_kids(col)
        title = lead_title(kids[0]) if kids else None
        idx = state["i"]
        state["i"] += 1
        body = render_nodes(kids[1:] if title is not None else kids, state)
        parts.append((idx, title, body))
    if any(any(c in body for c in COMPLEX) for _, _, body in parts):
        # columns already hold richer components (lists of cards, tables...): stack them full width
        return lifted + "".join(
            (f"<h3 class='sub-h'>{t}</h3>" if t is not None else "") + body for _, t, body in parts
        )
    cards = []
    for idx, title, body in parts:
        head = f"<h3>{title}</h3>" if title is not None else ""
        cards.append(f'<div class="pillar" data-reveal><div class="ic">{icon(idx)}</div>{head}{body}</div>')
    n = 4 if len(cards) == 4 else min(len(cards), 3)
    return lifted + f'<div class="pillars pillars-{n}">{"".join(cards)}</div>'


def design(html, state):
    """Return (section_body_html, is_dark). `state` carries a running icon index."""
    soup = BeautifulSoup(f"<div id='root'>{html}</div>", "lxml")
    root = soup.find(id="root")
    h2 = root.find("h2")
    heading = text(h2) if h2 else ""
    dark = bool(re.search(r"career|placement|recruit|prospect|opportunit|industry connect", heading, re.I))
    for start, layout in state.get("layouts", []):
        if heading.lower().startswith(start.lower()) and layout == "event-cards" and "logo-grid" not in html:
            html = to_event_cards(html)
            soup = BeautifulSoup(f"<div id='root'>{html}</div>", "lxml")
            root = soup.find(id="root")
        if heading.lower().startswith(start.lower()) and layout == "career-grid":
            html = to_career_grid(html, state)
            soup = BeautifulSoup(f"<div id='root'>{html}</div>", "lxml")
            root = soup.find(id="root")
        if heading.lower().startswith(start.lower()) and layout == "career-tabs":
            html = to_career_tabs(html, state)
            soup = BeautifulSoup(f"<div id='root'>{html}</div>", "lxml")
            root = soup.find(id="root")
        if heading.lower().startswith(start.lower()) and layout == "method-rows":
            html = to_method_rows(html, state)
            soup = BeautifulSoup(f"<div id='root'>{html}</div>", "lxml")
            root = soup.find(id="root")
        if heading.lower().startswith(start.lower()) and layout == "numbered-summary":
            html = to_numbered_summary(html)  # needs the raw list, so it runs before the generic card conversion
            soup = BeautifulSoup(f"<div id='root'>{html}</div>", "lxml")
            root = soup.find(id="root")
    body = render_nodes(real_kids(root), state)
    for start, layout in state.get("layouts", []):
        if heading.startswith(start) and layout == "vtabs":
            body = to_vtabs(body, state)
        if heading.startswith(start) and layout == "role-cards":
            body = to_role_cards(body)
        if heading.lower().startswith(start.lower()) and layout == "checklist-split":
            body = to_checklist_split(body)
        if heading.lower().startswith(start.lower()) and layout == "kd-tiles":
            body = to_kd_tiles(body)
        if heading.lower().startswith(start.lower()) and layout == "focus-cols":
            body = to_focus_cols(body)
        if heading.lower().startswith(start.lower()) and layout == "credit-bars":
            body = to_credit_bars(body)
        if heading.startswith(start) and layout == "tiles":
            body = to_tiles(body)
        if heading.startswith(start) and layout == "subject-cards":
            body = to_subject_cards(body, state)
        if heading.lower().startswith(start.lower()) and layout == "ped-rows":
            body = to_ped_rows(body)
        if heading.startswith(start) and layout == "split-benefits":
            body = to_split_benefits(body)
    return body, dark


def to_vtabs(html, state):
    """Replace the icon-card grids of a section with a vertical tab selector (list left, text right)."""
    soup = BeautifulSoup(f"<div id='root'>{html}</div>", "lxml")
    root = soup.find(id="root")
    cards = root.select(".pillar")
    if len(cards) < 3:
        return html
    uid = f"vt{state['i']}"
    btns, panels = [], []
    for k, card in enumerate(cards):
        h3 = card.find("h3")
        title = inner(h3) if h3 else ""
        if h3:
            h3.decompose()
        ic = card.find(class_="ic")
        if ic:
            ic.decompose()
        on = " is-active" if k == 0 else ""
        sel = "true" if k == 0 else "false"
        btns.append(
            f'<button type="button" role="tab" class="tab-btn{on}" id="{uid}-t{k}" aria-controls="{uid}-p{k}" aria-selected="{sel}">'
            f'<span class="vt-num">{k + 1:02d}</span><span class="vt-title">{title}</span></button>'
        )
        panels.append(
            f'<div role="tabpanel" class="tab-panel{on}" id="{uid}-p{k}" aria-labelledby="{uid}-t{k}">'
            f'<h3 class="vt-head">{title}</h3>{inner(card)}</div>'
        )
    block = BeautifulSoup(
        f'<div class="tabs vtabs" data-tabs><div class="tab-list" role="tablist">{"".join(btns)}</div>'
        f'<div class="vt-panels">{"".join(panels)}</div></div>', "lxml"
    ).find(class_="vtabs")
    first = cards[0].find_parent(class_="pillars")
    first.replace_with(block)
    for grp in root.select(".pillars"):
        grp.decompose()
    return inner(root)


GENERIC_EYEBROWS = [
    ("our legacy", "Our Story"), ("curriculum design", "How It Is Built"), ("elective", "Choose Your Path"),
    ("program focus", "What You Study"), ("diverse job", "Careers"), ("program differentiators", "Why PES University"),
    ("key differentiators", "Why PES University"), ("pedagogy", "How We Teach"), ("message from", "From the Dean"),
    ("program structure", "Curriculum"), ("curriculum structure", "Curriculum"), ("course structure", "Curriculum"),
    ("placement opportunities", "Placements"), ("program design", "Learning Approach"), ("who should", "Is It For You?"),
    ("focus areas", "Core Subjects"), ("specializations", "Choose Your Path"), ("future career", "Careers"),
    ("extra", "Beyond the Classroom"), ("pes university provides placement", "Placement Support"),
]


def eyebrow_for(state, h2):
    t = text(h2)
    for start, label in list(state.get("eyebrows", [])) + GENERIC_EYEBROWS:
        if t.lower().startswith(start.lower()):
            return label
    if re.search(r"career|placement|job|recruit", t, re.I):
        return "Careers"
    if re.search(r"curriculum|semester|syllabus|structure", t, re.I):
        return "Curriculum"
    return "About the Programme"


def merge_lists(kids):
    """Consecutive <ul>/<ol> siblings (a list split by the page builder) become one list."""
    merged = []
    for c in kids:
        if merged and isinstance(c, Tag) and c.name in ("ul", "ol") and isinstance(merged[-1], Tag) and merged[-1].name == c.name:
            for li in list(c.find_all("li", recursive=False)):
                merged[-1].append(li)
        else:
            merged.append(c)
    return merged


def render_nodes(kids, state):
    kids = merge_lists(kids)
    out = []
    i = 0
    while i < len(kids):
        n = kids[i]
        if isinstance(n, NavigableString):
            out.append(str(n))
            i += 1
            continue
        cls = n.get("class", [])
        if n.name == "div" and "cols" in cls and "has-media" not in cls:
            cols = n.find_all("div", class_="col", recursive=False)
            if len(cols) >= 2 and all(real_kids(c) and isinstance(real_kids(c)[0], Tag) and real_kids(c)[0].name == "h2" for c in cols):
                out.append(story_rows(cols, state))
                i += 1
                continue
            if len(cols) >= 2 and not any(c.find("iframe") for c in cols):
                out.append(make_pillars(cols, state))
                i += 1
                continue
        if n.name == "p" and lead_title(n) is not None:
            # run of "bold title paragraph + body" pairs -> icon cards
            groups, j = [], i
            while j < len(kids) and isinstance(kids[j], Tag) and kids[j].name == "p" and lead_title(kids[j]) is not None:
                t, body, k = lead_title(kids[j]), [], j + 1
                while k < len(kids) and isinstance(kids[k], Tag) and kids[k].name in ("p", "ul", "ol") and not (kids[k].name == "p" and lead_title(kids[k]) is not None):
                    body.append(kids[k])
                    k += 1
                if not body:
                    break
                groups.append((t, body))
                j = k
            if len(groups) >= 2:
                cards = []
                for t, body in groups:
                    idx = state["i"]
                    state["i"] += 1
                    cards.append(f'<div class="pillar" data-reveal><div class="ic">{icon(idx)}</div><h3>{t}</h3>{render_nodes(body, state)}</div>')
                out.append(f'<div class="pillars pillars-{min(len(cards), 3) if len(cards) != 4 else 4}">{"".join(cards)}</div>')
                i = j
                continue
        if n.name == "p" and bold_lead(n):
            run = []
            j = i
            while j < len(kids) and isinstance(kids[j], Tag) and kids[j].name == "p" and bold_lead(kids[j]):
                run.append(bold_lead(kids[j]))
                j += 1
            if len(run) >= 3:
                cards = "".join(
                    f'<div class="facility" data-reveal><div class="ic">{icon(state["i"] + k)}</div><h4>{t}</h4><p>{r}</p></div>' for k, (t, r) in enumerate(run)
                )
                state["i"] += len(run)
                out.append(f'<div class="facility-grid">{cards}</div>')
                i = j
                continue
        if n.name == "h4" and i + 1 < len(kids) and isinstance(kids[i + 1], Tag) and "tbl-wrap" in kids[i + 1].get("class", []):
            pairs, j = [], i
            while j + 1 < len(kids) and isinstance(kids[j], Tag) and kids[j].name == "h4" and isinstance(kids[j + 1], Tag) and "tbl-wrap" in kids[j + 1].get("class", []):
                pairs.append((kids[j], kids[j + 1]))
                j += 2
            if len(pairs) >= 2:
                items = []
                for k, (h4, tb) in enumerate(pairs):
                    state["i"] += 1
                    aid = f"cacc{state['i']}"
                    on = " is-open" if k == 0 else ""
                    subjects = [inner(td).strip() for td in tb.find_all("td")]
                    caption = " ".join(inner(th).strip() for th in tb.find_all("th"))
                    n = len(subjects)
                    count = f"{n} entry" if n == 1 else f"{n} entries"
                    lis = "".join(f"<li>{x}</li>" for x in subjects)
                    items.append(
                        f'<div class="acc-item sem-item{on}"><h4 class="acc-head"><button type="button" class="acc-trigger sem-trigger" aria-expanded="{"true" if k == 0 else "false"}" aria-controls="{aid}">'
                        f'<span class="sem-num">{k + 1:02d}</span><span class="acc-title">{inner(h4)}</span><span class="sem-count">{count}</span>'
                        f'<span class="acc-plus" aria-hidden="true"></span></button></h4>'
                        f'<div class="acc-panel" id="{aid}" role="region"><div class="acc-clip"><div class="acc-panel-inner">'
                        f'<ul class="sem-list">{lis}</ul></div></div></div></div>'
                    )
                out.append(f'<div class="acc sem-acc">{"".join(items)}</div>')
                i = j
                continue
        if n.name == "div" and "tbl-wrap" in cls and n.find("td", attrs={"rowspan": True}):
            groups, cur = [], None
            head_row = n.find("tr")
            head_cells = [inner(td).strip() for td in head_row.find_all("td")] if head_row is not None and not head_row.find("td", attrs={"rowspan": True}) else []
            for tr in n.find_all("tr"):
                tds = tr.find_all("td")
                for td in tds:
                    if td.has_attr("rowspan"):
                        cur = [inner(td).strip(), []]
                        groups.append(cur)
                    elif cur is not None:
                        cur[1].append(inner(td).strip())
            if len(groups) >= 2:
                cards = "".join(
                    f'<div class="spec-card" data-reveal><div class="ic">{icon(state["i"] + k)}</div><h4>{re.sub(r"</?div>", "", t)}</h4>'
                    f'<div class="chip-cloud">{"".join(f"<span class=dept-chip>{x}</span>" for x in items)}</div></div>'
                    for k, (t, items) in enumerate(groups)
                )
                state["i"] += len(groups)
                spec_head = f'<p class="spec-head">{"".join(f"<span>{c}</span>" for c in head_cells)}</p>' if head_cells else ""
                out.append(f'{spec_head}<div class="spec-grid">{cards}</div>')
                i += 1
                continue
        if n.name == "h2":
            prev = kids[i - 1] if i > 0 else None
            has_ey = isinstance(prev, Tag) and prev.name == "p" and "eyebrow" in prev.get("class", [])
            label = "" if has_ey else eyebrow_for(state, n)
            if label:
                out.append(f'<p class="eyebrow center">{label}</p>')
        if n.name == "div" and "cols" in cls and "has-media" in cls:
            for img in n.find_all("img"):
                if re.search(r"\.jpe?g", img.get("src", ""), re.I):
                    img["class"] = img.get("class", []) + ["ph-img"]
            flat = media_row(n, state)
            out.append(flat if flat is not None else str(n))
            i += 1
            continue
        if n.name in ("ul", "ol"):
            lis = n.find_all("li", recursive=False)
            leads = [bold_lead(li) for li in lis]
            trailing = ""
            if len(lis) >= 4 and leads[-1] is None and all(leads[:-1]):
                # a closing summary item without a bold lead stays as a paragraph under the cards
                trailing = f"<p>{inner(lis[-1]).strip()}</p>"
                lis, leads = lis[:-1], leads[:-1]
            if len(lis) >= 3 and all(leads):
                cards = "".join(
                    f'<div class="facility" data-reveal><div class="ic">{icon(state["i"] + k)}</div><h4>{t}</h4><p>{r}</p></div>'
                    for k, (t, r) in enumerate(leads)
                )
                state["i"] += len(lis)
                out.append(f'<div class="facility-grid">{cards}</div>{trailing}')
                i += 1
                continue
            if len(lis) >= 6 and all(len(text(li)) < 70 and not li.find(["p", "ul", "table"]) for li in lis):
                chips = "".join(f'<span class="dept-chip">{inner(li).strip()}</span>' for li in lis)
                out.append(f'<div class="chip-cloud">{chips}</div>')
                i += 1
                continue
        if n.name == "blockquote":
            qs = []
            while i < len(kids) and isinstance(kids[i], Tag) and kids[i].name == "blockquote":
                qs.append(kids[i])
                i += 1
            cards = "".join(
                f'<div class="testi-card" data-reveal><span class="qm">&ldquo;</span><div class="qtext">{inner(q)}</div></div>' for q in qs
            )
            out.append(f'<div class="testi-grid">{cards}</div>')
            continue
        out.append(str(n))
        i += 1
    return "".join(out)


def to_split_benefits(html):
    """Intro copy + highlighted example on the left, the listed benefits as numbered cards on the right."""
    soup = BeautifulSoup(f"<div id='root'>{html}</div>", "lxml")
    root = soup.find(id="root")
    lis = [li for li in root.select(".pillar li")]
    paras = [c for c in real_kids(root) if isinstance(c, Tag) and c.name == "p" and "eyebrow" not in c.get("class", [])]
    head = [c for c in real_kids(root) if isinstance(c, Tag) and (c.name == "h2" or "eyebrow" in c.get("class", []))]
    if len(lis) < 2 or not paras:
        return html
    copy = []
    for p in paras:
        kids = real_kids(p)
        is_example = bool(kids) and isinstance(kids[0], Tag) and kids[0].name in ("strong", "b") and text(kids[0]).lower().startswith("example")
        copy.append(f'<div class="mm-example">{inner(p)}</div>' if is_example else f"<p>{inner(p)}</p>")
    cards = "".join(
        f'<div class="mm-card" data-reveal><span class="mm-num">{k + 1:02d}</span><p>{inner(li).strip()}</p></div>' for k, li in enumerate(lis)
    )
    return (
        "".join(str(h) for h in head)
        + f'<div class="mm-split"><div class="mm-copy">{"".join(copy)}</div><div class="mm-benefits">{cards}</div></div>'
    )


def to_subject_cards(html, state):
    """Title + description pairs spread over several columns -> one grid of icon subject cards."""
    soup = BeautifulSoup(f"<div id='root'>{html}</div>", "lxml")
    root = soup.find(id="root")
    pillars = root.select(".pillar")
    if not pillars:
        return html
    cards = []
    for pl in pillars:
        cur = None
        for c in real_kids(pl):
            if not isinstance(c, Tag) or "ic" in c.get("class", []):
                continue
            if c.name in ("h3", "h4", "h5"):
                cur = [inner(c), []]
                cards.append(cur)
            elif cur is not None:
                cur[1].append(str(c))
    if len(cards) < 3:
        return html
    grid = "".join(
        f'<div class="facility subject" data-reveal><div class="ic">{icon(k)}</div><h4>{t}</h4>{"".join(b)}</div>' for k, (t, b) in enumerate(cards)
    )
    block = BeautifulSoup(f'<div class="facility-grid subject-grid">{grid}</div>', "lxml").find(class_="subject-grid")
    pillars[0].find_parent(class_="pillars").replace_with(block)
    for grp in root.select(".pillars"):
        grp.decompose()
    return inner(root)


def to_tiles(html):
    """A cloud of short items -> numbered activity tiles."""
    soup = BeautifulSoup(f"<div id='root'>{html}</div>", "lxml")
    root = soup.find(id="root")
    cloud = root.find(class_="chip-cloud")
    if cloud is None:
        return html
    items = cloud.find_all(class_="dept-chip")
    tiles = "".join(
        f'<div class="act-tile" data-reveal><span class="act-num">{k + 1:02d}</span><span class="act-text">{inner(c)}</span></div>' for k, c in enumerate(items)
    )
    block = BeautifulSoup(f'<div class="tile-grid">{tiles}</div>', "lxml").find(class_="tile-grid")
    cloud.replace_with(block)
    return inner(root)


DARK_RE = re.compile(r"career|placement|recruit|prospect|opportunit|industry connect", re.I)


def split_sections(body):
    """Split designed section html at every further top-level title (eyebrow + h2) so that each
    title opens its own section. Returns [(html, heading_text), ...]."""
    soup = BeautifulSoup(f"<div id='root'>{body}</div>", "lxml")
    root = soup.find(id="root")
    kids = [c for c in root.children if not (isinstance(c, NavigableString) and not str(c).strip())]
    pieces, cur, heading = [], [], ""

    def is_eyebrow(n):
        return isinstance(n, Tag) and n.name == "p" and "eyebrow" in n.get("class", [])

    i = 0
    while i < len(kids):
        n = kids[i]
        starts = (isinstance(n, Tag) and n.name == "h2") or (is_eyebrow(n) and i + 1 < len(kids) and isinstance(kids[i + 1], Tag) and kids[i + 1].name == "h2")
        has_body = any(not (is_eyebrow(c) or (isinstance(c, Tag) and c.name == "h2")) for c in cur)
        if starts and cur and has_body:
            pieces.append(("".join(str(c) for c in cur), heading))
            cur, heading = [], ""
        if isinstance(n, Tag) and n.name == "h2" and not heading:
            heading = text(n)
        cur.append(n)
        i += 1
    if cur:
        pieces.append(("".join(str(c) for c in cur), heading))
    return pieces


def to_role_cards(html):
    """Paragraphs that start with a bold role name -> numbered career cards (heading + intro kept on top)."""
    soup = BeautifulSoup(f"<div id='root'>{html}</div>", "lxml")
    root = soup.find(id="root")
    head, cards = [], []
    for el in root.find_all(["p", "h2", "li"]):
        if el.find_parent("p") is not None or (el.name == "p" and el.find_parent("li") is not None):
            continue
        cls = el.get("class", [])
        if el.name == "h2" or "eyebrow" in cls:
            head.append(str(el))
            continue
        kids = real_kids(el)
        if kids and isinstance(kids[0], Tag) and kids[0].name in ("strong", "b") and len(kids) > 1:
            cards.append((inner(kids[0]).strip(), "".join(str(c) for c in kids[1:]).strip()))
        else:
            head.append(str(el))
    if len(cards) < 3:
        return html
    grid = "".join(
        f'<div class="role-card" data-reveal><span class="role-num">{k + 1:02d}</span><h4>{t}</h4><p>{r}</p></div>' for k, (t, r) in enumerate(cards)
    )
    return "".join(head) + f'<div class="role-grid">{grid}</div>'


def to_checklist_split(html):
    """Paragraphs on the left, the bullet list as a highlighted checklist card on the right."""
    soup = BeautifulSoup(f"<div id='root'>{html}</div>", "lxml")
    root = soup.find(id="root")
    kids = real_kids(root)
    ul = next((c for c in kids if isinstance(c, Tag) and c.name in ("ul", "ol")), None)
    if ul is None:
        return html
    head = [str(c) for c in kids if isinstance(c, Tag) and (c.name == "h2" or "eyebrow" in c.get("class", []))]
    copy = [str(c) for c in kids if isinstance(c, Tag) and c.name == "p" and "eyebrow" not in c.get("class", [])]
    items = "".join(f'<li><span class="ck-tick" aria-hidden="true"></span><span>{inner(li).strip()}</span></li>' for li in ul.find_all("li", recursive=False))
    return (
        "".join(head)
        + f'<div class="ck-split{" ck-solo" if len(copy) <= 1 else ""}"><div class="ck-copy">{"".join(copy)}</div><div class="ck-card" data-reveal><ul class="ck-list">{items}</ul></div></div>'
    )


def to_numbered_summary(html):
    """Intro + closing summary on the left (sticky), the bold-led list as a numbered timeline on the right."""
    soup = BeautifulSoup(f"<div id='root'>{html}</div>", "lxml")
    root = soup.find(id="root")
    kids = real_kids(root)
    ul = next((c for c in kids if isinstance(c, Tag) and c.name in ("ul", "ol")), None)
    if ul is None:
        return html
    steps, summary = [], ""
    for li in ul.find_all("li", recursive=False):
        bl = bold_lead(li)
        if bl:
            steps.append(
                f'<li class="dt-step" data-reveal><span class="dt-num">{len(steps) + 1}</span>'
                f'<div class="dt-body"><h4>{bl[0]}</h4><p>{bl[1]}</p></div></li>'
            )
        else:
            summary = inner(li).strip()
    if len(steps) < 3:
        return html
    head = "".join(str(c) for c in kids if isinstance(c, Tag) and (c.name == "h2" or "eyebrow" in c.get("class", [])))
    intro = "".join(str(c) for c in kids if isinstance(c, Tag) and c.name == "p" and "eyebrow" not in c.get("class", []))
    band = f'<div class="dt-summary"><p>{summary}</p></div>' if summary else ""
    return head + f'<div class="dt-split"><div class="dt-left">{intro}{band}</div><ol class="dt-list">{"".join(steps)}</ol></div>'


def to_credit_bars(html):
    """Course / percentage / credits / distribution table -> bar rows (bar length = percentage)."""
    soup = BeautifulSoup(f"<div id='root'>{html}</div>", "lxml")
    root = soup.find(id="root")
    wrap = root.find(class_="tbl-wrap")
    table = wrap.find("table") if wrap else None
    if table is None:
        return html
    rows = [[inner(c).strip() for c in tr.find_all(["th", "td"])] for tr in table.find_all("tr")]
    if len(rows) < 3 or len(rows[0]) < 4:
        return html
    head, body = rows[0], rows[1:]
    total = None
    if re.match(r"total", re.sub(r"<[^>]+>", "", body[-1][0]).strip(), re.I):
        total = body.pop()

    def num(x):
        m = re.search(r"\d+(?:\.\d+)?", re.sub(r"<[^>]+>", "", x))
        return float(m.group(0)) if m else 0.0

    top = max(num(r[1]) for r in body) or 1
    lines = []
    for k, r in enumerate(body):
        pct = num(r[1])
        lines.append(
            f'<div class="pd-row" data-reveal><div class="pd-name"><span class="pd-idx">{k + 1:02d}</span><span>{r[0]}</span></div>'
            f'<div class="pd-bar"><span class="pd-fill" style="width:{pct / top * 100:.1f}%"></span><span class="pd-pct{" pd-low" if pct / top < 0.14 else ""}">{r[1]}</span></div>'
            f'<div class="pd-cred"><b>{r[2]}</b></div><div class="pd-dist">{r[3]}</div></div>'
        )
    cols = f'<div class="pd-head"><span>{head[0]}</span><span>{head[1]}</span><span>{head[2]}</span><span>{head[3]}</span></div>'
    foot = ""
    if total:
        foot = (
            f'<div class="pd-total"><span class="pd-t-name">{total[0]}</span><span>{total[1]}</span>'
            f'<span>{total[2]}</span><span>{total[3]}</span></div>'
        )
    block = BeautifulSoup(f'<div class="pd-card">{cols}{"".join(lines)}{foot}</div>', "lxml").find(class_="pd-card")
    wrap.replace_with(block)
    return inner(root)


def to_method_rows(html, state):
    """Bold-led list -> full-width rows: icon, method name, description."""
    soup = BeautifulSoup(f"<div id='root'>{html}</div>", "lxml")
    root = soup.find(id="root")
    ul = next((c for c in real_kids(root) if isinstance(c, Tag) and c.name in ("ul", "ol")), None)
    if ul is None:
        return plain_para_cards(root, state, html)
    rows = []
    for li in ul.find_all("li", recursive=False):
        bl = bold_lead(li)
        if not bl:
            return html
        idx = state["i"]
        state["i"] += 1
        rows.append(
            f'<div class="mr-row" data-reveal><div class="mr-ic">{icon(idx)}</div><h4>{bl[0]}</h4><p>{bl[1]}</p></div>'
        )
    if len(rows) < 3:
        return html
    ul.replace_with(BeautifulSoup(f'<div class="mr-list">{"".join(rows)}</div>', "lxml").body)
    return inner(root).replace("<body>", "").replace("</body>", "")


def to_career_tabs(html, state):
    """Bold-led list -> horizontal pill tabs (role names) with one detail panel per role."""
    soup = BeautifulSoup(f"<div id='root'>{html}</div>", "lxml")
    root = soup.find(id="root")
    ul = next((c for c in real_kids(root) if isinstance(c, Tag) and c.name in ("ul", "ol")), None)
    if ul is None:
        return html
    roles = []
    for li in ul.find_all("li", recursive=False):
        bl = bold_lead(li)
        if not bl:
            return html
        roles.append(bl)
    if len(roles) < 3:
        return html
    state["i"] += 1
    uid = f"ct{state['i']}"
    btns, panels = [], []
    for k, (t, r) in enumerate(roles):
        on = " is-active" if k == 0 else ""
        btns.append(
            f'<button type="button" role="tab" class="tab-btn{on}" id="{uid}-t{k}" aria-controls="{uid}-p{k}" aria-selected="{"true" if k == 0 else "false"}">{t}</button>'
        )
        panels.append(
            f'<div role="tabpanel" class="tab-panel{on}" id="{uid}-p{k}" aria-labelledby="{uid}-t{k}">'
            f'<div class="ct-ic">{icon(k)}</div><div class="ct-copy"><h4>{t}</h4><p>{r}</p></div></div>'
        )
    block = BeautifulSoup(
        f'<div class="tabs ctabs" data-tabs><div class="tab-list" role="tablist">{"".join(btns)}</div>{"".join(panels)}</div>', "lxml"
    ).find(class_="ctabs")
    ul.replace_with(block)
    return inner(root)


def to_event_cards(html):
    """Run of paragraphs that start with a bold name -> cards with a coloured title band."""
    soup = BeautifulSoup(f"<div id='root'>{html}</div>", "lxml")
    root = soup.find(id="root")
    kids = real_kids(root)
    cards, keep = [], []
    for c in kids:
        bl = bold_lead(c) if isinstance(c, Tag) and c.name == "p" and "eyebrow" not in c.get("class", []) else None
        if bl:
            cards.append(
                f'<div class="ev-card ev-{len(cards) % 2}" data-reveal><div class="ev-band"><span class="ev-num">{len(cards) + 1:02d}</span><h4>{bl[0]}</h4></div>'
                f'<div class="ev-body"><p>{bl[1]}</p></div></div>'
            )
        else:
            keep.append(str(c))
    if len(cards) < 3:
        return html
    return "".join(keep) + f'<div class="ev-grid">{"".join(cards)}</div>'


def to_career_grid(html, state):
    """All roles visible at once: a 3-column grid of icon cards (nothing hidden behind clicks)."""
    soup = BeautifulSoup(f"<div id='root'>{html}</div>", "lxml")
    root = soup.find(id="root")
    ul = next((c for c in real_kids(root) if isinstance(c, Tag) and c.name in ("ul", "ol")), None)
    if ul is None:
        return html
    cards = []
    for li in ul.find_all("li", recursive=False):
        bl = bold_lead(li)
        if not bl:
            return html
        idx = state["i"]
        state["i"] += 1
        cards.append(
            f'<article class="cg-card" data-reveal><div class="cg-top"><span class="cg-ic">{icon(idx)}</span><h4>{bl[0]}</h4></div><p>{bl[1]}</p></article>'
        )
    if len(cards) < 3:
        return html
    ul.replace_with(BeautifulSoup(f'<div class="cg-grid">{"".join(cards)}</div>', "lxml").body)
    return inner(root).replace("<body>", "").replace("</body>", "")


def plain_para_cards(root, state, fallback):
    """Heading + intro paragraph + several plain paragraphs -> intro on top, the rest as numbered cards (2 columns)."""
    kids = real_kids(root)
    paras = [c for c in kids if isinstance(c, Tag) and c.name == "p" and "eyebrow" not in c.get("class", [])]
    if len(paras) < 4:
        return fallback
    head = [str(c) for c in kids if isinstance(c, Tag) and (c.name == "h2" or "eyebrow" in c.get("class", []))]
    intro, rest = paras[0], paras[1:]
    cards = "".join(
        f'<article class="pc-card" data-reveal><span class="pc-num">{k + 1:02d}</span><div class="pc-ic">{icon(state["i"] + k)}</div><p>{inner(c)}</p></article>'
        for k, c in enumerate(rest)
    )
    state["i"] += len(rest)
    return "".join(head) + str(intro) + f'<div class="pc-grid">{cards}</div>'


def media_row(n, state):
    """Image + text row -> flat block: eyebrow, centred title, intro paragraph, wide photo, then the list as cards or tiles."""
    cols = n.find_all("div", class_="col", recursive=False)
    media = [c for c in cols if "col-media" in c.get("class", [])]
    textc = [c for c in cols if "col-media" not in c.get("class", [])]
    if len(media) != 1 or len(textc) != 1:
        return None
    col = textc[0]
    for fig in col.find_all("figure"):
        fig.unwrap()
    kids = real_kids(col)
    if not kids or not (isinstance(kids[0], Tag) and kids[0].name == "h2"):
        return None
    h2 = kids[0]
    label = eyebrow_for(state, h2)
    img = media[0].find("img")
    photo = f'<div class="banner-photo">{img}</div>' if img is not None else ""
    out = [f'<p class="eyebrow center">{label}</p>{h2}']
    rest = kids[1:]
    lead = []
    while rest and isinstance(rest[0], Tag) and rest[0].name == "p":
        lead.append(str(rest.pop(0)))
    out.append("".join(lead))
    out.append(photo)
    for c in rest:
        if not (isinstance(c, Tag) and c.name in ("ul", "ol")):
            out.append(render_nodes([c], state))
            continue
        lis = c.find_all("li", recursive=False)
        leads = [bold_lead(li) for li in lis]
        stray = [x.extract() for x in list(c.children) if isinstance(x, Tag) and x.name != "li"]
        if len(lis) >= 3 and all(leads):
            cards = "".join(
                f'<div class="facility subject" data-reveal><div class="ic">{icon(state["i"] + k)}</div><h4>{t}</h4><p>{r}</p></div>'
                for k, (t, r) in enumerate(leads)
            )
            state["i"] += len(lis)
            out.append(f'<div class="facility-grid subject-grid subject-3">{cards}</div>')
        else:
            tiles = "".join(
                f'<div class="act-tile" data-reveal><span class="act-num">{k + 1:02d}</span><span class="act-text">{inner(li).strip()}</span></div>'
                for k, li in enumerate(lis)
            )
            out.append(f'<div class="tile-grid">{tiles}</div>')
        out.extend(str(x) for x in stray)
    return "".join(out)


def to_focus_cols(html):
    """Multi-column list table (header + short cells) -> one card per column with chips."""
    soup = BeautifulSoup(f"<div id='root'>{html}</div>", "lxml")
    root = soup.find(id="root")
    wrap = root.find(class_="tbl-wrap")
    table = wrap.find("table") if wrap else None
    if table is None or table.find("thead") is None:
        return html
    heads = [inner(th).strip() for th in table.find("thead").find_all("th")]
    rows = [[inner(td).strip() for td in tr.find_all("td")] for tr in table.find("tbody").find_all("tr")]
    if not 3 <= len(heads) <= 4 or any(len(r) != len(heads) for r in rows) or any(len(re.sub(r"<[^>]+>", "", c)) > 60 for r in rows for c in r):
        return html
    cards = []
    for k, h in enumerate(heads):
        items = [r[k] for r in rows if re.sub(r"<[^>]+>|&nbsp;", "", r[k]).strip()]
        chips = "".join(f'<span class="dept-chip">{x}</span>' for x in items)
        cards.append(f'<div class="spec-card" data-reveal><div class="ic">{icon(k)}</div><h4>{h}</h4><div class="chip-cloud">{chips}</div></div>')
    block = BeautifulSoup(f'<div class="spec-grid spec-3">{"".join(cards)}</div>', "lxml").find(class_="spec-grid")
    wrap.replace_with(block)
    return inner(root)


def to_kd_tiles(html):
    """A plain bullet list of full sentences -> two-column numbered tiles (large number, text, accent bar)."""
    soup = BeautifulSoup(f"<div id='root'>{html}</div>", "lxml")
    root = soup.find(id="root")
    ul = next((c for c in real_kids(root) if isinstance(c, Tag) and c.name in ("ul", "ol")), None)
    if ul is None:
        return html
    lis = ul.find_all("li", recursive=False)
    if len(lis) < 3 or any(bold_lead(li) for li in lis):
        return html
    tiles = "".join(
        f'<div class="kd-tile {"kd-l" if k % 2 == 0 else "kd-r"}" data-reveal><span class="kd-node">{k + 1}</span><div class="kd-card"><p>{inner(li).strip()}</p></div></div>' for k, li in enumerate(lis)
    )
    ul.replace_with(BeautifulSoup(f'<div class="kd-grid">{tiles}</div>', "lxml").find(class_="kd-grid"))
    for e_ in root.select(".pc-grid:empty"):
        e_.decompose()
    return inner(root)


def apply_page_layouts(piece, heading, state):
    """Page-specific one-off designs, applied per section after the body has been split at every title."""
    for start, layout in state.get("layouts", []):
        if layout.startswith(("bapa-", "bapa2-", "btech-", "bcom-")) and heading.lower().startswith(start.lower()):
            import bapa_designs

            return bapa_designs.APPLY[layout](piece, state)
    return piece


def to_ped_rows(html):
    """Pedagogy: every image + text row becomes a numbered panel; photo and text alternate sides, titles become headings."""
    soup = BeautifulSoup(f"<div id='root'>{html}</div>", "lxml")
    root = soup.find(id="root")
    rows = root.select(".cols.has-media")
    if not rows:
        return html
    for k, row in enumerate(rows):
        cols = row.find_all("div", class_="col", recursive=False)
        media = next((c for c in cols if "col-media" in c.get("class", [])), None)
        textc = next((c for c in cols if c is not media), None)
        if media is None or textc is None:
            continue
        for p_ in textc.find_all("p", recursive=False):
            kids = real_kids(p_)
            if len(kids) == 1 and isinstance(kids[0], Tag) and kids[0].name in ("strong", "b") and text(kids[0]) == text(p_):
                h = soup.new_tag("h4")
                h.string = text(kids[0])
                p_.replace_with(h)
        first_h = textc.find("h4") or textc.find("h3")
        img = media.find("img")
        panel = BeautifulSoup(
            f'<article class="pd-panel{" pd-flip" if k % 2 else ""}" data-reveal><div class="pd-pic"><span class="pd-no">{k + 1:02d}</span></div>'
            f'<div class="pd-txt"></div></article>', "lxml").find("article")
        panel.find(class_="pd-pic").insert(0, img)
        panel.find(class_="pd-txt").append(textc)
        textc.name = "div"
        textc["class"] = ["pd-inner"]
        row.replace_with(panel)
    return inner(root)
