# PES Campaigns — redesigned website

Static HTML / CSS / vanilla-JS rebuild of https://campaigns.pes.edu/ using the `mbbs(refferal)` folder as the design reference
(navy + orange palette, Playfair Display / Noto Sans, transparent-to-sticky header, island fact card, pill buttons, rounded cards,
accordion, scroll-reveal). The reference folder itself is untouched.

## Run locally

```
python -m http.server 8000      # from this folder
```
then open http://localhost:8000/ (use a server, not `file://`, so relative links resolve and the embedded forms load).

## Structure

```
index.html                  home (programme list)
<slug>/index.html           one folder per campaign page (39 pages: btech, mbbs, bca, bdes, bba, ... mdes)
assets/css/                 style.css (tokens, header, hero, footer), pages.css (content components), responsive.css,
                            mbbs.css / bbacompare.css / bcom-compare.css (page-specific)
assets/js/                  main.js (header, menu, reveal, analytics), pages.js (accordion, tabs, slider), + 3 page scripts
assets/img/                 logo/ banners/ campaigns/ icons/
tools/                      build + verification scripts, source/ = snapshots of the original pages
```

Each campaign page is a plain HTML file and can be edited independently. `tools/build.py` regenerates the 36 standard pages
from the snapshots in `tools/source/` (`python tools/build.py --fetch`); `tools/build_special.py` ports `mbbs`, `bscjmc`, `bbacompare`
and `bcom-compare`. Re-running them overwrites hand edits to those pages.

## How content was preserved

Pages are produced by transforming the original DOM, never retyping it. Verification (`tools/verify_special.py`) renders each
original page on the live site and the local page in Chrome and compares all visible characters: **40/40 pages match** (the only
local extras are the duplicated "Back To PES" label and ✕ of the mobile menu). Original hero CTA / fact list were moved into the
hero and island card; all words, links and destinations are retained. Internal `campaigns.pes.edu/...` links point to local pages;
external links are unchanged.

## Checklist of pages

home, btech, mbbs, bca, bdes, bba, bbaanalytics, bbacompare, bbasports, bcom, bcom-hons-ca, bcom-hons, bcom-hons-cma,
bcom-hons-cfa, bcom-compare, bsceconomics, bpt, law, llb-hons, bscpsychology, bsccct, bscdtt, bscaot, bscmedical, bscemt, bscmlt,
bscmrit, nursing, bapa, bscjmc, bbahem, allied-health, bpharm, pharmd, mscpsychology, mca, mba, mpharm, mtech, mdes — all built, tested at 1440 / 820 / 390 px
(no console errors, no horizontal overflow, no dead local links).

## Notes / things to know

* **Financial Support section (all standard pages):** the original "Scholarships @ PESU" and "PES University Loyalty Program" blocks are
  shown in the reference's "Merit scholarships, awarded on performance" layout (eyebrow, heading, merit-scholarship cards, loyalty cards,
  footnote). Each page's own figures and wording (50% / 40% / 7.75+ awards, 30 / 20 / 10 / 10 % loyalty concessions, eligibility lists and
  the Note) are carried into the cards; the section heading, eyebrow, intro sentence and group labels come from the reference page. "University
  Highlights" uses the same card style.
* **`bscjmc`** was migrated by PES to the new (reference) template on the live site, so it is ported like `mbbs` (its own CSS/JS in `assets/`).
* The live site is edited continuously; snapshots in `tools/source/` were last refreshed on 2026-10-14.

* **`mbbs`, `bbacompare`, `bcom-compare`** already use the newer single-file template on the live site. `mbbs` *is* the reference design.
  The two comparison pages keep their own bespoke glass design and scripted track switcher (content is JS-rendered); only their CSS/JS
  were moved into `assets/`. Restyling them to the shared system is a possible follow-up.
* **Scholarships / Loyalty Program** blocks are loaded at runtime by the original site from `assets/include/*.html`; they are snapshotted
  in `tools/source/inc-*.html` and built into the pages (home, allied-health).
* The original header contact bar, nav ("Back To PES", "Register for Admissions") and footer are kept with their labels and links.
* Hero images are the original campaign images (blob PNGs) over a navy gradient — the reference's medical stock photos were not used on non-medical pages.
* `bala` is linked in a comment on the source home page and returns 404, so it has no page.

## Missing source assets (404 on the live site as well; the `<img>` was omitted, no text lost)

| Page | Missing file |
|---|---|
| bcom-hons-cfa | img/scholarships.png |
| law | law.pes.edu/wp-content/uploads/2022/03/Supreme-Court.jpg |
| mscpsychology | img/mapp7.jpg, img/mapp8.jpg |
| mba | img/clients/client-1.jpg (logo carousel) |
| mdes | scholarships image (img/scholarships.png) |

## Needs backend / third-party integration

* **Enquiry forms** are the original LeadSquared landing pages embedded as iframes (`pes.viewpage.co/...`); they work only with that service.
* **Analytics**: Google Tag Manager `GTM-N3XVVLXF` and the LeadSquared tracker (`pidTracker('57004')`) are loaded from `main.js`;
  each page's landing-page id is in `<body data-mx-landing-page>`.
* Registration buttons link to https://admissions.pes.edu/registration/ (external).

## Testing

`python tools/test_site.py` (all pages, 3 viewports), `python tools/test_interactions.py`, `python tools/verify_special.py [slug ...]`
(needs `pip install playwright beautifulsoup4 lxml` and Chrome).
