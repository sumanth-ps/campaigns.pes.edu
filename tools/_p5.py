p = "tools/build_special.py"
s = open(p, encoding="utf-8").read()
old = '''    css_blocks = re.findall(r"<style[^>]*>(.*?)</style>", raw, re.S)
    css = "\n\n".join(css_blocks)
    raw = re.sub(r"<style[^>]*>.*?</style>", "", raw, flags=re.S)
'''
new = '''    css_blocks = re.findall(r"<style[^>]*>(.*?)</style>", raw, re.S)
    css = "\n\n".join(css_blocks)
    raw = re.sub(r"<style[^>]*>.*?</style>", "", raw, flags=re.S)
    # pages already migrated to the new template load css/style.css + js/main.js from their own folder
    ext_js = ""
    m = re.search(r'<link rel="stylesheet" href="(css/[^"]+)">', raw)
    if m:
        css += "\n" + fetch_text(page_url + m.group(1))
        raw = raw.replace(m.group(0), "")
    m = re.search(r'<script src="(js/[^"]+)"></script>', raw)
    if m:
        ext_js = fetch_text(page_url + m.group(1))
        raw = raw.replace(m.group(0), f'<script src="../assets/js/{slug}.js"></script>')
'''
assert old in s
s = s.replace(old, new, 1)
old = '''    big = max(scripts, key=lambda s: len(s[2]))
    js = big[2]
    raw = raw[: big[0]] + f'<script src="../assets/js/{slug}.js"></script>' + raw[big[1] :]
'''
new = '''    if ext_js:
        js = ext_js
    else:
        big = max(scripts, key=lambda s: len(s[2]))
        js = big[2]
        raw = raw[: big[0]] + f'<script src="../assets/js/{slug}.js"></script>' + raw[big[1] :]
'''
assert old in s
s = s.replace(old, new, 1)
s = s.replace('def port(slug):', '''def fetch_text(url):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=40).read().decode("utf-8")


def port(slug):''', 1)
s = s.replace('for s in ("mbbs", "bbacompare", "bcom-compare"):', 'for s in ("mbbs", "bbacompare", "bcom-compare", "bscjmc"):')
open(p, "w", encoding="utf-8").write(s)

p = "tools/build.py"
s = open(p, encoding="utf-8").read()
s = s.replace('elif slug in ("mbbs", "bbacompare", "bcom-compare"):', 'elif slug in ("mbbs", "bbacompare", "bcom-compare", "bscjmc"):')
s = s.replace('if not os.path.exists(fp) or slug in ("mbbs", "bbacompare", "bcom-compare"):', 'if not os.path.exists(fp) or slug in ("mbbs", "bbacompare", "bcom-compare", "bscjmc"):')
open(p, "w", encoding="utf-8").write(s)
