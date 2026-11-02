"""Seven one-off section designs for the BA Performing Arts (bapa) page. Each function receives the
already-designed section body (eyebrow + h2 + content) and returns the replacement markup. Wording is
never changed; only wrappers, numbers and icons are added."""
import re

from bs4 import BeautifulSoup, Tag

import designer as dz


def parts(html):
    soup = BeautifulSoup(f"<div id='root'>{html}</div>", "lxml")
    root = soup.find(id="root")
    head = "".join(str(c) for c in root.find_all(["p", "h2"], recursive=False) if c.name == "h2" or "eyebrow" in c.get("class", []))
    return soup, root, head


def inner(n):
    return "".join(str(c) for c in n.children)


def ribbon(html, state):
    """Programme Highlights: a swipeable ribbon of tall navy cards."""
    soup, root, head = parts(html)
    ul = root.find("ul")
    if ul is None:
        return html
    cards = "".join(
        f'<div class="slide hl-card"><span class="hl-no">{k + 1:02d}</span><p>{inner(li).strip()}</p></div>'
        for k, li in enumerate(ul.find_all("li", recursive=False))
    )
    arrow = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="{}"/></svg>'
    return (
        head
        + '<div class="slider hl-ribbon" data-slider><div class="slider-track" tabindex="0">' + cards + "</div>"
        + '<div class="slider-nav"><button type="button" class="slider-btn" data-dir="-1" aria-label="Previous">' + arrow.format("M15 18l-6-6 6-6")
        + '</button><button type="button" class="slider-btn" data-dir="1" aria-label="Next">' + arrow.format("M9 18l6-6-6-6") + "</button></div></div>"
    )


def editorial(html, state):
    """Who should pursue: large editorial statements with oversized numerals."""
    soup, root, head = parts(html)
    ps = [p for p in root.select(".pc-card p")] or [p for p in root.find_all("p", recursive=False) if "eyebrow" not in p.get("class", [])]
    if not ps:
        return html
    rows = "".join(
        f'<article class="ed-row" data-reveal><span class="ed-no">{k + 1:02d}</span><p>{inner(p)}</p></article>' for k, p in enumerate(ps)
    )
    return head + f'<div class="ed-list">{rows}</div>'


def steps(html, state):
    """Placement: horizontal chevron process on the dark band."""
    soup, root, head = parts(html)
    ps = [p for p in root.select(".pc-card p")] or [p for p in root.find_all("p", recursive=False) if "eyebrow" not in p.get("class", [])]
    if not ps:
        return html
    cols = "".join(
        f'<div class="st-step" data-reveal><div class="st-chev"><span>{k + 1}</span></div><div class="st-body"><p>{inner(p)}</p></div></div>'
        for k, p in enumerate(ps)
    )
    return head + f'<div class="st-flow st-{len(ps)}">{cols}</div>'


def domains(html, state):
    """Specializations Domains: Music / Dance / Theatre tabs, photo beside Major -> Allied pairs."""
    soup, root, head = parts(html)
    intro = "".join(str(p) for p in root.find_all("p", recursive=False) if "eyebrow" not in p.get("class", []))
    imgs = [i.get("src") for i in root.find_all("img")]
    if len(imgs) < 3:
        return html
    # Music: facility cards (Major/Allied pairs); Dance: bold-led list; Theatre: plain list
    music_cards = root.select(".facility-grid .facility")
    music = [(c.find("h4").get_text(strip=True), c.find("p").get_text(" ", strip=True)) for c in music_cards]
    cols = root.select(".cols")
    dance_li = [li for li in cols[0].find_all("li")]
    dance = []
    for li in dance_li:
        st = li.find(["strong", "b"])
        dance.append((st.get_text(strip=True), re.sub(r"^\s*:\s*", "", li.get_text(" ", strip=True)[len(st.get_text(strip=True)):]).strip()))
    th_title = cols[1].find("h4").get_text(" ", strip=True)
    theatre = [li.get_text(" ", strip=True) for li in cols[1].find_all("li")]
    titles = ["Music", re.sub(r"\s+", " ", cols[0].find("h4").get_text(" ", strip=True)), th_title]

    def pairs(items):
        out, k = [], 0
        while k < len(items):
            a = items[k]
            b = items[k + 1] if k + 1 < len(items) else None
            out.append(
                '<div class="dm-pair" data-reveal>'
                f'<div class="dm-cell"><b>{a[0]}</b><span>{a[1]}</span></div>'
                + ('<span class="dm-link" aria-hidden="true"></span>' f'<div class="dm-cell dm-allied"><b>{b[0]}</b><span>{b[1]}</span></div>' if b else "")
                + "</div>"
            )
            k += 2
        return "".join(out)

    body = [pairs(music), pairs(dance), "".join(f'<div class="dm-solo" data-reveal>{t}</div>' for t in theatre)]
    uid = f"dm{state['i']}"
    state["i"] += 1
    btns = "".join(
        f'<button type="button" role="tab" class="tab-btn{" is-active" if k == 0 else ""}" id="{uid}-t{k}" aria-controls="{uid}-p{k}" aria-selected="{"true" if k == 0 else "false"}">{t}</button>'
        for k, t in enumerate(titles)
    )
    panels = "".join(
        f'<div role="tabpanel" class="tab-panel dm-panel{" is-active" if k == 0 else ""}" id="{uid}-p{k}" aria-labelledby="{uid}-t{k}">'
        f'<div class="dm-photo"><img src="{imgs[k]}" alt="" loading="lazy"></div><div class="dm-list">{body[k]}</div></div>'
        for k in range(3)
    )
    return head + f'<div class="dm-intro">{intro}</div><div class="tabs dm-tabs" data-tabs><div class="tab-list" role="tablist">{btns}</div>{panels}</div>'


def ledger(html, state):
    """Program Design and Delivery: lead statement, domain note, photo and a credit ledger with dotted leaders."""
    soup, root, head = parts(html)
    ps = [p for p in root.find_all("p", recursive=False) if "eyebrow" not in p.get("class", [])]
    cols = root.select(".cols")
    if len(ps) < 2 or not cols:
        return html
    col = cols[0]
    img = col.find("img")
    lead_in = col.find("p")
    rows = []
    for li in col.find_all("li"):
        txt = " ".join(li.get_text(" ", strip=True).split())
        m = re.match(r"^(.*?)\s+[–—\-�]\s+(.*)$", txt) or re.match(r"^(.*?)\s*[–—]\s*(.*)$", txt)
        if m:
            rows.append(f'<div class="lg-line" data-reveal><span class="lg-name">{m.group(1)}</span><span class="lg-leader"></span><span class="lg-val">– {m.group(2)}</span></div>')
        else:
            rows.append(f'<div class="lg-line" data-reveal><span class="lg-name">{txt}</span></div>')
    photo = f'<div class="ldg-photo">{img}</div>' if img is not None else ""
    return (
        head
        + f'<div class="ldg-lead" data-reveal>{ps[0]}</div><div class="ldg-note" data-reveal>{ps[1]}</div>'
        + f'<div class="ldg-split">{photo}<div class="ldg-sheet"><div class="ldg-title">{lead_in}</div>{"".join(rows)}</div></div>'
    )


def overlay(html, state):
    """Pedagogy Method: full-width photo with the four methods as glass chips over its lower edge."""
    soup, root, head = parts(html)
    img = root.find("img")
    tiles = root.select(".act-tile")
    if img is None or not tiles:
        return html
    chips = "".join(
        f'<div class="pg-chip" data-reveal><span>{t.find(class_="act-num").get_text(strip=True)}</span><p>{t.find(class_="act-text").decode_contents()}</p></div>' for t in tiles
    )
    return head + f'<div class="pg-stage"><div class="pg-photo">{img}</div><div class="pg-chips">{chips}</div></div>'


def flip(html, state):
    """Future careers (dark band): flip cards - role on the front, description on the back."""
    soup, root, head = parts(html)
    cards = root.select(".facility")
    if len(cards) < 3:
        return html
    out = []
    for k, c in enumerate(cards):
        h4 = c.find("h4")
        p = c.find("p")
        out.append(
            f'<div class="fl-card" tabindex="0" data-reveal><div class="fl-in"><div class="fl-front"><span class="fl-ic">{dz.icon(state["i"] + k)}</span><h4>{inner(h4)}</h4><i class="fl-hint" aria-hidden="true"></i></div>'
            f'<div class="fl-back"><h4>{inner(h4)}</h4><p>{inner(p)}</p></div></div></div>'
        )
    state["i"] += len(cards)
    return head + f'<div class="fl-grid">{"".join(out)}</div>'


APPLY = {
    "bapa-ribbon": ribbon, "bapa-editorial": editorial, "bapa-steps": steps, "bapa-domains": domains,
    "bapa-ledger": ledger, "bapa-overlay": overlay, "bapa-flip": flip,
}


# ====================== second set of designs ======================
def _texts(root, sel):
    return [inner(p).strip() for p in root.select(sel)]


def bento(html, state):
    """Key Differentiators: bento grid - one large navy tile, the rest in mixed sizes."""
    soup, root, head = parts(html)
    ps = _texts(root, ".kd-card p") or [inner(li).strip() for li in root.find_all("li")]
    if len(ps) < 3:
        return html
    spans = ["bn-hero", "bn-wide", "bn-tall", "", "bn-wide", "", "bn-hero"]
    tiles = "".join(
        f'<div class="bn-tile {spans[k % len(spans)]}" data-reveal><span class="bn-ic">{dz.icon(state["i"] + k)}</span><p>{t}</p></div>' for k, t in enumerate(ps)
    )
    state["i"] += len(ps)
    return head + f'<div class="bn-grid">{tiles}</div>'


def vtab_hl(html, state):
    """Programme Highlights: vertical tab selector - numbers on the left, the chosen highlight large on the right."""
    soup, root, head = parts(html)
    ps = _texts(root, ".hl-card p") or [inner(li).strip() for li in root.find_all("li")]
    if len(ps) < 2:
        return html
    uid = f"vh{state['i']}"
    state["i"] += 1
    btns = "".join(
        f'<button type="button" role="tab" class="tab-btn{" is-active" if k == 0 else ""}" id="{uid}-t{k}" aria-controls="{uid}-p{k}" aria-selected="{"true" if k == 0 else "false"}"><span class="vh-n">{k + 1:02d}</span></button>'
        for k in range(len(ps))
    )
    panels = "".join(
        f'<div role="tabpanel" class="tab-panel{" is-active" if k == 0 else ""}" id="{uid}-p{k}" aria-labelledby="{uid}-t{k}"><span class="vh-big">{k + 1:02d}</span><p>{t}</p></div>' for k, t in enumerate(ps)
    )
    return head + f'<div class="tabs vh-tabs" data-tabs><div class="tab-list" role="tablist">{btns}</div><div class="vh-stage">{panels}</div></div>'


def triptych(html, state):
    """Who should pursue: three tall colour panels with a large quote mark."""
    soup, root, head = parts(html)
    ps = _texts(root, ".ed-row p")
    if not ps:
        return html
    tones = ["tp-navy", "tp-orange", "tp-pale"]
    cols = "".join(f'<article class="tp-panel {tones[k % 3]}" data-reveal><span class="tp-q" aria-hidden="true">&ldquo;</span><p>{t}</p><span class="tp-no">{k + 1:02d}</span></article>' for k, t in enumerate(ps))
    return head + f'<div class="tp-grid">{cols}</div>'


def glassrows(html, state):
    """Placement: stacked full-width glass rows with a round icon, on the dark band."""
    soup, root, head = parts(html)
    ps = _texts(root, ".st-body p")
    if not ps:
        return html
    rows = "".join(
        f'<article class="gr-row" data-reveal><span class="gr-ic">{dz.icon(state["i"] + k + 6)}</span><p>{t}</p><span class="gr-arrow" aria-hidden="true"></span></article>' for k, t in enumerate(ps)
    )
    return head + f'<div class="gr-list">{rows}</div>'


def creditgrid(html, state):
    """Program Design and Delivery: banner photo, lead + note, then every item as a card with its credits as a pill."""
    soup, root, head = parts(html)
    ps = [p for p in root.find_all("p", recursive=False) if "eyebrow" not in p.get("class", [])]
    cols = root.select(".cols")
    if len(ps) < 2 or not cols:
        return html
    col = cols[0]
    img = col.find("img")
    lead_in = col.find("p")
    cards = []
    for li in col.find_all("li"):
        txt = " ".join(li.get_text(" ", strip=True).split())
        m = re.match(r"^(.*?)\s+([\u2013\u2014\-\ufffd])\s+(.*)$", txt)
        if m:
            cards.append(f'<div class="cr-card" data-reveal><h4>{m.group(1)}</h4><span class="cr-pill">{m.group(2)} {m.group(3)}</span></div>')
        else:
            cards.append(f'<div class="cr-card" data-reveal><h4>{txt}</h4></div>')
    photo = f'<div class="cr-photo">{img}<div class="cr-over">{ps[0]}</div></div>' if img is not None else str(ps[0])
    return head + photo + f'<div class="cr-note" data-reveal>{ps[1]}</div><div class="cr-title">{lead_in}</div><div class="cr-grid">{"".join(cards)}</div>'


def role_acc(html, state):
    """Future careers: two-column accordion of roles on the dark band."""
    soup, root, head = parts(html)
    cards = root.select(".fl-card")
    if len(cards) < 3:
        return html
    items = []
    for k, c in enumerate(cards):
        h4 = c.select_one(".fl-back h4")
        p = c.select_one(".fl-back p")
        aid = f"ra{state['i']}-{k}"
        items.append(
            f'<div class="acc-item ra-item"><h4 class="acc-head"><button type="button" class="acc-trigger" aria-expanded="false" aria-controls="{aid}">'
            f'<span class="ra-ic">{dz.icon(k)}</span><span class="acc-title">{re.sub(r"\s*:\s*$", "", inner(h4).strip())}</span><span class="acc-plus" aria-hidden="true"></span></button></h4>'
            f'<div class="acc-panel" id="{aid}" role="region"><div class="acc-clip"><div class="acc-panel-inner"><p>{inner(p)}</p></div></div></div></div>'
        )
    state["i"] += 1
    half = (len(items) + 1) // 2
    return head + f'<div class="ra-cols"><div class="acc ra-acc">{"".join(items[:half])}</div><div class="acc ra-acc">{"".join(items[half:])}</div></div>'


APPLY.update({
    "bapa2-bento": bento, "bapa2-vtab": vtab_hl, "bapa2-triptych": triptych, "bapa2-glass": glassrows,
    "bapa2-credit": creditgrid, "bapa2-roles": role_acc,
})


def _chain(first, second):
    return lambda html, state: second(first(html, state), state)


APPLY.update({
    "bapa2-vtab": _chain(ribbon, vtab_hl), "bapa2-triptych": _chain(editorial, triptych),
    "bapa2-glass": _chain(steps, glassrows), "bapa2-roles": _chain(flip, role_acc),
})


def switch_split(html, state):
    """B.Tech-M.Tech Switch Program: lead paragraph + example card on the left, floating illustration on the right."""
    soup, root, head = parts(html)
    ps = [p for p in root.find_all("p", recursive=False) if "eyebrow" not in p.get("class", [])]
    img = root.find("img")
    if len(ps) < 2:
        return html
    lead, example = ps[0], ps[1]
    art = f'<div class="sw-art" data-reveal><span class="sw-blob"></span><span class="sw-ring"></span>{img}</div>' if img is not None else ""
    return (
        head
        + f'<div class="sw-split"><div class="sw-copy" data-reveal><div class="sw-lead">{lead}</div>'
        f'<div class="sw-example">{example}</div></div>{art}</div>'
    )


APPLY["btech-switch"] = switch_split


def directory(html, state):
    """Career Prospects: a numbered directory - role on the left, where it leads on the right, hairline rows."""
    soup, root, head = parts(html)
    cards = root.select(".facility")
    if len(cards) < 4:
        return html
    rows = "".join(
        f'<div class="dr-row" data-reveal><span class="dr-n">{k + 1:02d}</span><h4>{inner(c.find("h4"))}</h4><p>{inner(c.find("p"))}</p><span class="dr-go" aria-hidden="true"></span></div>'
        for k, c in enumerate(cards)
    )
    return head + f'<div class="dr-list">{rows}</div>'


APPLY["bcom-directory"] = directory


def master_detail(html, state):
    """Career Prospects (light): scrollable role list on the left, the selected role's detail card on the right."""
    soup, root, head = parts(html)
    cards = root.select(".facility")
    if len(cards) < 4:
        return html
    uid = f"md{state['i']}"
    state["i"] += 1
    btns, panels = [], []
    for k, c in enumerate(cards):
        t, p = inner(c.find("h4")).strip(), inner(c.find("p")).strip()
        on = " is-active" if k == 0 else ""
        btns.append(f'<button type="button" role="tab" class="tab-btn{on}" id="{uid}-t{k}" aria-controls="{uid}-p{k}" aria-selected="{"true" if k == 0 else "false"}"><span class="md-n">{k + 1:02d}</span><span>{t}</span></button>')
        panels.append(
            f'<div role="tabpanel" class="tab-panel{on}" id="{uid}-p{k}" aria-labelledby="{uid}-t{k}"><span class="md-ic">{dz.icon(k)}</span>'
            f'<h3>{t}</h3><p>{p}</p><span class="md-count">{k + 1:02d} / {len(cards)}</span></div>'
        )
    return head + f'<div class="tabs md-tabs" data-tabs><div class="tab-list md-list" role="tablist">{"".join(btns)}</div><div class="md-stage">{"".join(panels)}</div></div>'


APPLY["bcom-master"] = master_detail


def career_grid(html, state):
    """Career Prospects (light blue): every role as a compact card with a ghost numeral and icon."""
    soup, root, head = parts(html)
    cards = root.select(".facility")
    if len(cards) < 4:
        return html
    items = "".join(
        f'<article class="cg-card" data-reveal><span class="cg-n" aria-hidden="true">{k + 1:02d}</span><span class="cg-ic">{dz.icon(k)}</span>'
        f'<h4>{inner(c.find("h4"))}</h4><p>{inner(c.find("p"))}</p></article>'
        for k, c in enumerate(cards)
    )
    return head + f'<div class="cg-grid">{items}</div>'


APPLY["bcom-grid"] = career_grid


def acca_story(html, state):
    """bcom-hons "Why ACCA?": story + benefit card up top, then the exempted / non-exempted papers as a two-sided ledger."""
    soup, root, head = parts(html)
    kids = [c for c in root.children if isinstance(c, Tag)]
    ps = [c for c in kids if c.name == "p" and "eyebrow" not in c.get("class", [])]
    uls = [c for c in kids if c.name == "ul"]
    key = next((c for c in kids if c.name == "h3" and "Key Subjects" in c.get_text()), None)
    ex_h = root.find("h5")
    non_h = next((c for c in kids if c.name == "h3" and c is not key and "Non-Exempted" in c.get_text()), None)
    pill = root.find("div", class_="pillars")
    if len(ps) < 3 or not uls or key is None or ex_h is None or non_h is None or pill is None:
        return html
    ex_ul = ex_h.find_next("ul")
    key_txt = "".join(str(n) for n in key.children if not (isinstance(n, Tag) and n.name in ("h5", "ul"))).strip()
    benefits = "".join(f'<li data-reveal><span class="ac-ck"></span><span>{inner(li).strip()}</span></li>' for li in uls[0].find_all("li", recursive=False))
    papers = "".join(f'<li data-reveal><span class="ac-no">{k + 1:02d}</span><span>{inner(li).strip()}</span></li>' for k, li in enumerate(ex_ul.find_all("li", recursive=False)))
    pills = pill.select(".pillar")
    boxes = "".join(
        f'<section class="ac-box ac-p{k + 1}" data-reveal><span class="ac-pn">{k + 1}</span><h4>{inner(pl.find("h3")).strip()}</h4><ul>'
        + "".join(f"<li>{inner(li).strip()}</li>" for li in pl.find_all("li"))
        + "</ul></section>"
        for k, pl in enumerate(pills)
    )
    return (
        head
        + f'<div class="ac-top"><div class="ac-story" data-reveal><p class="ac-lead">{inner(ps[0]).strip()}</p><p>{inner(ps[1]).strip()}</p><p>{inner(ps[2]).strip()}</p></div>'
        f'<aside class="ac-card" data-reveal><ul>{benefits}</ul></aside></div>'
        f'<div class="ac-banner" data-reveal><h3>{key_txt}</h3></div>'
        f'<div class="ac-trio"><section class="ac-box ac-ex" data-reveal><h5>{inner(ex_h).strip()}</h5><ol>{papers}</ol></section>{boxes}</div>'
    )


APPLY["bcom-acca"] = acca_story


def curriculum_path(html, state):
    """bba "Curriculum Design": a vertical path - numbered node on a line, a wide text panel beside it."""
    soup, root, head = parts(html)
    cards = root.select(".pc-card")
    if len(cards) < 2:
        return html
    steps = "".join(
        f'<li class="cp-step" data-reveal><span class="cp-node"><b>{k + 1:02d}</b></span>'
        f'<div class="cp-panel"><span class="cp-ic">{dz.icon(k)}</span><p>{inner(c.find("p")).strip()}</p></div></li>'
        for k, c in enumerate(cards)
    )
    return head + f'<ol class="cp-path">{steps}</ol>'


APPLY["bcom-path"] = curriculum_path


def strip_photo(html, state):
    """bba "Elective Courses": same section without the banner photo."""
    soup, root, head = parts(html)
    for n in root.select(".banner-photo"):
        n.decompose()
    return inner(root)


APPLY["bcom-nophoto"] = strip_photo


def focus_rows(html, state):
    """bba "Program Focus": one full-width row per group - number, icon and title on the left, topic chips on the right."""
    soup, root, head = parts(html)
    cards = root.select(".spec-card")
    if len(cards) < 2:
        return html
    rows = "".join(
        f'<div class="pf-row" data-reveal><div class="pf-lab"><span class="pf-n">{k + 1:02d}</span><span class="pf-ic">{dz.icon(k)}</span><h4>{inner(c.find("h4"))}</h4></div>'
        f'<div class="pf-chips">{inner(c.find("div", class_="chip-cloud"))}</div></div>'
        for k, c in enumerate(cards)
    )
    return head + f'<div class="pf-list">{rows}</div>'


APPLY["bcom-focusrows"] = focus_rows


def ped_columns(html, state):
    """bcom-hons "Pedagogy": three tall columns - photo on top, the three methods stacked underneath."""
    soup, root, head = parts(html)
    panels = root.select(".pd-panel")
    if len(panels) < 2:
        return html
    cols = ""
    for k, pn in enumerate(panels):
        img = pn.find("img")
        items = ""
        for h in pn.select(".pd-inner h4"):
            ul = h.find_next_sibling("ul")
            items += f'<div class="pc3-item"><h4>{inner(h).strip()}</h4>{ul if ul is not None else ""}</div>'
        cols += f'<article class="pc3-col" data-reveal><div class="pc3-pic">{img}<span class="pc3-no">{k + 1:02d}</span></div><div class="pc3-body">{items}</div></article>'
    rest = "".join(str(c) for c in root.find_all(recursive=False) if "pd-panel" not in c.get("class", []) and c.name not in ("h2",) and "eyebrow" not in c.get("class", []))
    return head + f'<div class="pc3-grid">{cols}</div>' + rest


APPLY["bcom-pedcols"] = ped_columns


def career_sectors(html, state):
    """bcom-hons "Career Prospects" as one section: intro paragraph, then the three sectors as side-by-side role lists."""
    soup, root, head = parts(html)
    eb = root.find("p", class_="eyebrow")
    h2 = root.find("h2")
    head = f"{eb}{h2}"
    intro = root.select_one(".pc-card p")
    if intro is None:
        return html
    sectors, cur = [], None
    for n in root.find_all(recursive=False):
        if n.name == "h2" and cur is not None or (n.name == "h2" and sectors == [] and "Career" not in n.get_text()):
            cur = None
        if n.name == "h2" and "Career" not in n.get_text():
            cur = [inner(n).strip(), []]
            sectors.append(cur)
        elif cur is not None:
            cur[1] += [inner(x).strip() for x in n.select(".dept-chip")] + [inner(x).strip() for x in n.select("li")]
    if len(sectors) < 2:
        return html
    cols = "".join(
        f'<article class="cs-col cs-c{k + 1}" data-reveal><header class="cs-hd"><span class="cs-ic">{dz.icon(k)}</span><h3>{t}</h3></header>'
        '<div class="cs-pills">' + "".join(f"<span>{i}</span>" for i in items) + "</div></article>"
        for k, (t, items) in enumerate(sectors)
    )
    return head + f'<p class="cs-intro" data-reveal>{inner(intro).strip()}</p><div class="cs-cols">{cols}</div>'


APPLY["bcom-careers"] = career_sectors
