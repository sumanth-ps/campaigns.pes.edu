#!/usr/bin/env python3
"""Add Scholarships at PESU, PES University Loyalty Program and University highlights (not 'Before you apply')
to bbacompare. They are sub-page sections (class cmp-only), so the landing view does not show them."""
import os
import re

import port_bcom_sections as pb

ROOT = pb.ROOT
PAGE = os.path.join(ROOT, "bbacompare", "index.html")
CSSF = os.path.join(ROOT, "assets", "css", "bbacompare.css")


def cmp_only(html):
    if 'class="' in html.split(">")[0]:
        return html.replace('<section class="', '<section class="cmp-only ', 1)
    return html.replace("<section ", '<section class="cmp-only" ', 1)


def main():
    old = open(pb.OLD, encoding="utf-8").read()
    shared = [cmp_only(pb.section(old, sid)) for sid in ("scholarships", "loyalty", "rankings")]
    t = open(PAGE, encoding="utf-8").read()
    t = re.sub(re.escape("<!-- ===== extra sections (added) ===== -->") + r".*?" + re.escape("<!-- ===== /extra sections ===== -->") + "\n?", "", t, flags=re.S)
    t = re.sub(re.escape(pb.M1) + r".*?" + re.escape(pb.M2) + "\n?", "", t, flags=re.S)
    anchor = "<!-- ============ FINAL CTA ============ -->"
    assert anchor in t
    t = t.replace(anchor, pb.M1 + "\n" + "\n".join(shared) + "\n" + pb.M2 + "\n" + anchor, 1)
    open(PAGE, "w", encoding="utf-8", newline="\n").write(t)

    c = open(CSSF, encoding="utf-8").read()
    c = re.sub(re.escape(pb.C1) + r".*?" + re.escape(pb.C2) + "\n?", "", c, flags=re.S)
    # remove the earlier "pb-row without image" experiment
    c = re.sub(r"\n/\* extra sections: pb-row cards without an image \*/.*?\.pb-note\{[^}]*\}\n@media \(max-width:900px\)\{[^}]*\{[^}]*\}\}\n", "\n", c, flags=re.S)
    parts = [b for b in pb.blocks(pb.wanted_css()) if "prog-" not in b[: b.index("{")]]
    c += "\n" + pb.C1 + "\n" + "\n".join(parts) + "\n" + pb.C2 + "\n"
    open(CSSF, "w", encoding="utf-8", newline="\n").write(c)
    print("bbacompare: added", len(shared), "sections")


if __name__ == "__main__":
    main()
