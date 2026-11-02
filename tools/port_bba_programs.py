#!/usr/bin/env python3
"""bbacompare: replace "Three ways into business." (pb-row list) with the "Explore the programs." row design
used on bcom-compare (prog-sec / prog-row), keeping BBA's own text, photos and buttons."""
import html
import os
import re
import shutil

from bs4 import BeautifulSoup

import port_bcom_sections as pb

ROOT = pb.ROOT
PAGE = os.path.join(ROOT, "bbacompare", "index.html")
CSSF = os.path.join(ROOT, "assets", "css", "bbacompare.css")
SNAP = os.path.join(ROOT, "tools", "source", "bbacompare-programs-brief.html")
P1, P2 = "<!-- ===== explore programs (ported) ===== -->", "<!-- ===== /explore programs ===== -->"
K1, K2 = "/* ===== explore programs css ===== */", "/* ===== /explore programs css ===== */"
CHECK = '<span class="ck"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><polyline points="5 12.5 10 17 19 7"/></svg></span>'
ARR = '<span class="arr-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="12" x2="18" y2="12"/><polyline points="13 6 19 12 13 18"/></svg></span>'


def main():
    t = open(PAGE, encoding="utf-8").read()
    if 'id="programs-brief"' in t:
        i = t.rfind("<section", 0, t.index('id="programs-brief"'))
        j = t.index("</section>", i) + 10
        open(SNAP, "w", encoding="utf-8").write(t[i:j])
    brief = open(SNAP, encoding="utf-8").read()
    soup = BeautifulSoup(brief, "lxml")
    h2 = soup.find("h2")
    heading = re.sub(r"\s+", " ", str(h2.decode_contents())).strip()
    img_dir = os.path.join(ROOT, "bbacompare", "img")
    os.makedirs(img_dir, exist_ok=True)
    rows = []
    for k, art in enumerate(soup.select("article.pb-row")):
        num = art.select_one(".pb-num").get_text(" ", strip=True)
        tag = re.sub(r"^\d+\s*\S\s*", "", num)
        name = art.select_one("h3").get_text(" ", strip=True)
        desc = art.select_one(".pb-body > p:not(.pb-num)").get_text(" ", strip=True)
        meta = [s.get_text(" ", strip=True) for s in art.select(".pb-meta span")]
        btn = art.select_one("button")
        setv = btn.get("data-set")
        src = art.select_one("img")["src"]
        name_f = os.path.basename(src)
        sp = os.path.join(ROOT, "assets", "img", "campaigns", name_f)
        if os.path.exists(sp):
            shutil.copyfile(sp, os.path.join(img_dir, name_f))
        hl = "".join(f"<li>{CHECK}{html.escape(m, quote=False)}</li>" for m in meta)
        flip = " flip" if k % 2 else ""
        rows.append(
            f'<section class="h-all prog-sec {setv}{flip}" id="prog-{setv}"><div class="wrap"><article class="prog-row reveal"><div class="prog-body">'
            f'<p class="prog-tag">{html.escape(tag, quote=False)}</p><h3 class="prog-name">{html.escape(name, quote=False)}</h3>'
            f'<p class="prog-desc">{html.escape(desc, quote=False)}</p><ul class="prog-hl" aria-label="Key highlights">{hl}</ul>'
            f'<button type="button" class="btn on-acc sm prog-cta pb-go" data-set="{setv}">Learn More {ARR}</button></div>'
            f'<div class="prog-media"><img src="../assets/img/campaigns/{name_f}" alt="{html.escape(name)}" loading="lazy"></div></article></div></section>'
        )
    # local image paths for the page itself
    rows = [r.replace('src="../assets/img/campaigns/', 'src="img/') for r in rows]
    intro = f'<section class="h-all prog-intro" id="programs"><div class="wrap"><div class="section-head reveal"><div><p class="eyebrow">Programs</p><h2>{heading}</h2></div></div></div></section>'
    block = P1 + "\n" + intro + "\n" + "\n".join(rows) + "\n" + P2

    t = re.sub(re.escape(P1) + r".*?" + re.escape(P2), "", t, flags=re.S)
    # put it where the old section was (or just before the first cmp-only section after the hero)
    if 'id="programs-brief"' in t:
        i = t.rfind("<section", 0, t.index('id="programs-brief"'))
        j = t.index("</section>", i) + 10
        t = t[:i] + block + t[j:]
    else:
        anchor = brief and None
        raise SystemExit("could not find where to place the block")
    open(PAGE, "w", encoding="utf-8", newline="\n").write(t)

    c = open(CSSF, encoding="utf-8").read()
    c = re.sub(re.escape(K1) + r".*?" + re.escape(K2) + "\n?", "", c, flags=re.S)
    parts = [b for b in pb.blocks(pb.wanted_css()) if "prog-" in b[: b.index("{")] or ".ck" in b[: b.index("{")] or ".arr-ic" in b[: b.index("{")]]
    c += "\n" + K1 + "\n" + "\n".join(parts) + "\n" + K2 + "\n"
    open(CSSF, "w", encoding="utf-8", newline="\n").write(c)
    print("rows:", len(rows))


if __name__ == "__main__":
    main()
