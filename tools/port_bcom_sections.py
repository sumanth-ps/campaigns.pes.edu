#!/usr/bin/env python3
"""Port the original bcom-compare sections into bcomcompare/index.html:
"Explore the programs." (5 program rows), "Scholarships at PESU.", "PES University Loyalty Program.",
"University highlights." and "Before you apply." (FAQ, rendered statically).
Markup and CSS are copied from bcom-compare/index.html and assets/css/bcom-compare.css."""
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLD = os.path.join(ROOT, "bcom-compare", "index.html")
OLDCSS = os.path.join(ROOT, "assets", "css", "bcom-compare.css")
OLDJS = os.path.join(ROOT, "assets", "js", "bcom-compare.js")
NEW = os.path.join(ROOT, "bcomcompare", "index.html")
M1, M2 = "<!-- ===== ported sections ===== -->", "<!-- ===== /ported sections ===== -->"
C1, C2 = "/* ===== ported sections css ===== */", "/* ===== /ported sections css ===== */"
J1, J2 = "<!-- ===== ported js ===== -->", "<!-- ===== /ported js ===== -->"


def section(t, sid):
    i = t.index(f'id="{sid}"')
    i = t.rfind("<section", 0, i)
    return t[i : t.index("</section>", i) + 10]


def blocks(css):
    """Top-level CSS blocks (balanced braces)."""
    out, depth, start = [], 0, 0
    for k, ch in enumerate(css):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                out.append(css[start : k + 1].strip())
                start = k + 1
    return out


SEL = re.compile(r"prog-|sch-card|loy-card|rank-card|card-row|loyalty-row|rank-row|foot-note|faq|\.pct|\.rk\b|\.ck\b|#loyalty|#scholarships|#rankings|#programs|\.arr-ic")


def wanted_css():
    css = open(OLDCSS, encoding="utf-8").read()
    keep = []
    for b in blocks(css):
        head = b[: b.index("{")].strip()
        if head.startswith("@media"):
            inner = b[b.index("{") + 1 : -1]
            parts = [r for r in blocks(inner) if SEL.search(r[: r.index("{")])]
            if parts:
                keep.append(head + "{" + "\n".join(parts) + "}")
        elif not head.startswith("@") and SEL.search(head):
            keep.append(b)
    return "\n".join(keep).replace(":where(html.v-home) ", "")


def faq_section():
    js = open(OLDJS, encoding="utf-8").read()
    block = js[js.index("const FAQS = ["): js.index("];", js.index("const FAQS = ["))]
    qa = re.findall(r"\['((?:[^'\\]|\\.)*)','((?:[^'\\]|\\.)*)'\]", block)
    import html

    items = "".join(
        f'<div class="faq-item"><button class="faq-head" aria-expanded="false" aria-controls="faq-b-{i}"><span>{html.escape(q.replace(chr(92) + chr(39), chr(39)), quote=False)}</span><span class="plus"></span></button>'
        f'<div class="faq-body" id="faq-b-{i}"><div class="faq-body-inner">{html.escape(a.replace(chr(92) + chr(39), chr(39)), quote=False)}</div></div></div>'
        for i, (q, a) in enumerate(qa)
    )
    return (
        '<section class="cmp-only" id="faq"><div class="wrap"><div class="section-head reveal"><div><p class="eyebrow">Questions</p><h2>Before you <em>apply.</em></h2></div>'
        '<p class="lede">The things applicants and parents ask us most often. Anything else, the admissions office picks up on 080-10-297297.</p></div>'
        f'<div class="faq-grid reveal" id="faqMount">{items}</div></div></section>'
    )


FAQ_JS = (
    "<script>document.querySelectorAll('#faqMount .faq-head').forEach(function(b){b.addEventListener('click',function(){"
    "var it=b.closest('.faq-item');var o=it.classList.toggle('open');b.setAttribute('aria-expanded',String(o));});});</script>"
)


def main():
    old = open(OLD, encoding="utf-8").read()
    # the original file holds two views; the programme rows live in the first one
    secs = {}
    for sid in ("programs", "prog-p1", "prog-p2", "prog-p3", "prog-p4", "prog-p5"):
        secs[sid] = section(old, sid)
    shared = [section(old, "scholarships"), section(old, "loyalty"), section(old, "rankings")]

    # images -> bcomcompare/img
    img_dir = os.path.join(ROOT, "bcomcompare", "img")
    os.makedirs(img_dir, exist_ok=True)

    def local_img(m):
        name = os.path.basename(m.group(1))
        src = os.path.join(ROOT, "assets", "img", "campaigns", name)
        if os.path.exists(src):
            shutil.copyfile(src, os.path.join(img_dir, name))
        return f'src="img/{name}"'

    explore = []
    for sid, html_ in secs.items():
        h = re.sub(r'src="\.\./assets/img/campaigns/([^"]+)"', local_img, html_)
        h = re.sub(r'<a class="([^"]*prog-cta[^"]*)" href="#" data-go="(p\d)">(.*?)</a>', r'<button type="button" class="\1 pb-go" data-set="\2">\3</button>', h, flags=re.S)
        h = h.replace("<section class=\"", '<section class="h-all ', 1)
        explore.append(h)
    shared = [s.replace('<section class="', '<section class="cmp-only ', 1) if 'class="' in s.split(">")[0] else s.replace("<section ", '<section class="cmp-only" ', 1) for s in shared]
    tail = "\n".join(shared + [faq_section()])

    t = open(NEW, encoding="utf-8").read()
    # drop previous experiments
    t = re.sub(re.escape("<!-- ===== extra sections (added) ===== -->") + r".*?" + re.escape("<!-- ===== /extra sections ===== -->") + r"\n?", "", t, flags=re.S)
    t = re.sub(re.escape(M1) + r".*?" + re.escape(M2) + r"\n?", "", t, flags=re.S)
    t = re.sub(re.escape(C1) + r".*?" + re.escape(C2) + r"\n?", "", t, flags=re.S)
    t = re.sub(re.escape(J1) + r".*?" + re.escape(J2) + r"\n?", "", t, flags=re.S)
    # replace "Five ways into commerce." with the Explore the programs rows
    i = t.index('id="programs-brief"')
    i = t.rfind("<section", 0, i)
    j = t.index("</section>", i) + 10
    t = t[:i] + M1 + "\n" + "\n".join(explore) + "\n" + M2 + t[j:]
    anchor = "<!-- ============ ENQUIRY ============ -->"
    t = t.replace(anchor, M1 + "\n" + tail + "\n" + M2 + "\n" + anchor, 1)
    t = t.replace("</style>", C1 + "\n" + wanted_css() + "\n" + C2 + "\n</style>", 1)
    t = t.replace("</body>", J1 + FAQ_JS + J2 + "\n</body>", 1)
    open(NEW, "w", encoding="utf-8", newline="\n").write(t)
    print("ported", len(explore), "programme rows +", len(shared) + 1, "sections")


if __name__ == "__main__":
    main()
