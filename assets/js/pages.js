/* PES Campaigns — page components: accordions, tabs, sliders */
(function () {
  "use strict";

  /* accordions (one open at a time inside each group, like the reference) */
  document.querySelectorAll(".acc").forEach(function (acc) {
    var items = acc.querySelectorAll(":scope > .acc-item");
    items.forEach(function (item) {
      var trigger = item.querySelector(".acc-trigger");
      trigger.addEventListener("click", function () {
        var wasOpen = item.classList.contains("is-open");
        items.forEach(function (o) {
          o.classList.remove("is-open");
          o.querySelector(".acc-trigger").setAttribute("aria-expanded", "false");
        });
        if (!wasOpen) {
          item.classList.add("is-open");
          trigger.setAttribute("aria-expanded", "true");
        }
      });
    });
  });

  /* tabs */
  document.querySelectorAll("[data-tabs]").forEach(function (tabs) {
    var btns = Array.prototype.slice.call(tabs.querySelectorAll(":scope > .tab-list > .tab-btn"));
    var panels = Array.prototype.slice.call(tabs.querySelectorAll(".tab-panel"));
    function select(i, focus) {
      btns.forEach(function (b, k) {
        var on = k === i;
        b.classList.toggle("is-active", on);
        b.setAttribute("aria-selected", on ? "true" : "false");
        b.tabIndex = on ? 0 : -1;
        panels[k].classList.toggle("is-active", on);
      });
      if (focus) btns[i].focus();
    }
    btns.forEach(function (b, i) {
      b.addEventListener("click", function () { select(i); });
      b.addEventListener("keydown", function (e) {
        if (e.key === "ArrowRight") { e.preventDefault(); select((i + 1) % btns.length, true); }
        if (e.key === "ArrowLeft") { e.preventDefault(); select((i - 1 + btns.length) % btns.length, true); }
      });
    });
    var start = btns.findIndex(function (b) { return b.classList.contains("is-active"); });
    select(start < 0 ? 0 : start);
  });

  /* sliders */
  document.querySelectorAll("[data-slider]").forEach(function (s) {
    var track = s.querySelector(".slider-track");
    s.querySelectorAll(".slider-btn").forEach(function (b) {
      b.addEventListener("click", function () {
        var step = (track.querySelector(".slide") || track).getBoundingClientRect().width + 22;
        track.scrollBy({ left: step * Number(b.getAttribute("data-dir")), behavior: "smooth" });
      });
    });
    track.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") track.scrollBy({ left: 320, behavior: "smooth" });
      if (e.key === "ArrowLeft") track.scrollBy({ left: -320, behavior: "smooth" });
    });
  });

  /* logo marquee: highlight the logo nearest the centre */
  document.querySelectorAll(".logo-marquee").forEach(function (m) {
    var tiles = Array.prototype.slice.call(m.querySelectorAll(".logo-tile"));
    var cur = null;
    function tick() {
      var r = m.getBoundingClientRect();
      if (r.bottom > 0 && r.top < window.innerHeight) {
        var mid = r.left + r.width / 2, best = null, bd = 1e9;
        tiles.forEach(function (t) {
          var b = t.getBoundingClientRect(), d = Math.abs(b.left + b.width / 2 - mid);
          if (d < bd) { bd = d; best = t; }
        });
        if (best !== cur) { if (cur) cur.classList.remove("is-center"); best.classList.add("is-center"); cur = best; }
      }
      requestAnimationFrame(tick);
    }
    if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) requestAnimationFrame(tick);
  });

  /* menu links: same behaviour in the desktop bar and the mobile toggle menu - smooth scroll below the sticky header, current section highlighted */
  (function () {
    var links = Array.prototype.slice.call(document.querySelectorAll("#mainNav a[href^='#'], #mobileMenu a[href^='#']"));
    if (!links.length) return;
    var map = {};
    links.forEach(function (a) {
      var id = a.getAttribute("href").slice(1), el = document.getElementById(id);
      if (!el) return;
      (map[id] = map[id] || { el: el, links: [] }).links.push(a);
    });
    var ids = Object.keys(map);
    function headerH() { var h = document.getElementById("siteHeader"); return h ? h.offsetHeight : 0; }
    links.forEach(function (a) {
      a.addEventListener("click", function (e) {
        var t = map[a.getAttribute("href").slice(1)];
        if (!t) return;
        e.preventDefault();
        window.scrollTo({ top: t.el.getBoundingClientRect().top + window.scrollY - headerH() + 1, behavior: "smooth" });
      });
    });
    function spy() {
      var y = headerH() + 40, cur = null;
      ids.forEach(function (id) { if (map[id].el.getBoundingClientRect().top <= y) cur = id; });
      ids.forEach(function (id) { map[id].links.forEach(function (a) { a.classList.toggle("is-current", id === cur); }); });
    }
    window.addEventListener("scroll", spy, { passive: true });
    spy();
  })();
})();
