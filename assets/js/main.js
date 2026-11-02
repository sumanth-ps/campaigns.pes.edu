/* PES Campaigns — shared behaviour: sticky header, mobile menu, reveal, back-to-top, analytics */
(function () {
  "use strict";

  var header = document.getElementById("siteHeader");
  var toTop = document.getElementById("toTop");

  function onScroll() {
    var y = window.scrollY;
    if (header) header.classList.toggle("scrolled", y > 20);
    document.body.classList.toggle("is-scrolled", y > 20);
    if (toTop) toTop.classList.toggle("show", y > 480);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* scroll reveal */
  var revealEls = document.querySelectorAll("[data-reveal]");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("is-visible"); io.unobserve(e.target); }
      });
    }, { threshold: 0.08 });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* mobile menu */
  var hamburger = document.getElementById("hamburger");
  var mobileMenu = document.getElementById("mobileMenu");
  var backdrop = document.getElementById("mobileBackdrop");
  var closeBtn = document.getElementById("closeMenu");
  function setMenu(open) {
    if (!mobileMenu) return;
    mobileMenu.classList.toggle("open", open);
    backdrop.classList.toggle("show", open);
    hamburger.setAttribute("aria-expanded", open ? "true" : "false");
  }
  if (hamburger && mobileMenu) {
    hamburger.addEventListener("click", function () { setMenu(true); });
    closeBtn.addEventListener("click", function () { setMenu(false); });
    backdrop.addEventListener("click", function () { setMenu(false); });
    mobileMenu.querySelectorAll("a").forEach(function (a) { a.addEventListener("click", function () { setMenu(false); }); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") setMenu(false); });
  }

  /* analytics carried over from the original site: Google Tag Manager + LeadSquared tracker */
  (function (w, d, s, l, i) {
    w[l] = w[l] || [];
    w[l].push({ "gtm.start": new Date().getTime(), event: "gtm.js" });
    var f = d.getElementsByTagName(s)[0], j = d.createElement(s);
    j.async = true;
    j.src = "https://www.googletagmanager.com/gtm.js?id=" + i;
    f.parentNode.insertBefore(j, f);
  })(window, document, "script", "dataLayer", "GTM-N3XVVLXF");

  var lp = document.body.getAttribute("data-mx-landing-page");
  if (lp) window.MXLandingPageId = lp;
  var tracker = document.createElement("script");
  tracker.src = "https://web-in21.mxradon.com/t/Tracker.js";
  tracker.async = true;
  tracker.onload = function () { if (typeof window.pidTracker === "function") window.pidTracker("57004"); };
  document.head.appendChild(tracker);
})();

/* hero photo rotator (campaign pages) */
(function () {
  var slides = document.querySelectorAll(".hero-slider .hero-slide");
  var wrap = document.getElementById("heroDots");
  if (slides.length < 2 || !wrap) return;
  var dots = [], current = 0, timer;
  function go(i) {
    slides[current].classList.remove("is-active");
    dots[current].classList.remove("is-active");
    current = i;
    slides[current].classList.add("is-active");
    dots[current].classList.add("is-active");
    reset();
  }
  function reset() { clearInterval(timer); timer = setInterval(function () { go((current + 1) % slides.length); }, 6000); }
  slides.forEach(function (_, i) {
    var d = document.createElement("button");
    d.type = "button";
    d.className = "hero-dot" + (i === 0 ? " is-active" : "");
    d.setAttribute("aria-label", "Go to slide " + (i + 1));
    d.addEventListener("click", function () { go(i); });
    wrap.appendChild(d);
    dots.push(d);
  });
  reset();
})();
