/* Behaviour reused from the mbbs(refferal) reference: header state, reveal-on-scroll, mobile menu, back-to-top, accordion. */
(function () {
  var header = document.getElementById('siteHeader');
  var toTop = document.getElementById('toTop');
  var bar = document.getElementById('mobileBar');
  function onScroll() {
    if (header && !document.body.classList.contains('notes')) header.classList.toggle('scrolled', window.scrollY > 20);
    if (toTop) toTop.classList.toggle('show', window.scrollY > 480);
    if (bar) bar.classList.toggle('show', window.scrollY > 300);
    spy();
  }

  /* scroll-spy for the in-page navigation */
  var navLinks = Array.prototype.slice.call(document.querySelectorAll('#mainNav a[href^="#"], #mobileMenu a[href^="#"]'));
  var targets = [];
  navLinks.forEach(function (a) {
    var el = document.getElementById(a.getAttribute('href').slice(1));
    if (el && targets.indexOf(el) === -1) targets.push(el);
  });
  targets.sort(function (a, b) { return a.offsetTop - b.offsetTop; });
  function spy() {
    if (!targets.length) return;
    var current = null;
    targets.forEach(function (t) { if (t.getBoundingClientRect().top <= 140) current = t; });
    navLinks.forEach(function (a) {
      a.classList.toggle('active', !!current && a.getAttribute('href') === '#' + current.id);
    });
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* island card straddles the hero edge: half inside, half outside */
  var islandWrap = document.querySelector('.island-wrap');
  var islandCard = document.querySelector('.island-card');
  function placeIsland() {
    if (islandWrap && islandCard) islandWrap.style.marginTop = (-islandCard.offsetHeight / 2) + 'px';
  }
  placeIsland();
  window.addEventListener('resize', placeIsland);
  window.addEventListener('load', placeIsland);


  /* scroll progress bar + parallax photo bands */
  var progress = document.getElementById('progress');
  var bands = Array.prototype.slice.call(document.querySelectorAll('.px-band'));
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function fx() {
    if (progress) {
      var h = document.documentElement.scrollHeight - window.innerHeight;
      progress.style.width = (h > 0 ? (window.scrollY / h) * 100 : 0) + '%';
    }
    if (reduce) return;
    bands.forEach(function (b) {
      var r = b.getBoundingClientRect();
      if (r.bottom < 0 || r.top > window.innerHeight) return;
      var p = (r.top + r.height / 2 - window.innerHeight / 2) / window.innerHeight;
      b.firstElementChild.style.transform = 'translateY(' + (p * -60) + 'px)';
    });
  }
  window.addEventListener('scroll', fx, { passive: true });
  window.addEventListener('resize', fx);
  fx();


  /* "A week on this course": expanding panels (hover, focus or tap) with gentle auto-play until touched */
  var wk = document.querySelector('.wk-acc');
  if (wk) {
    var panels = Array.prototype.slice.call(wk.querySelectorAll('.wk-panel'));
    var wkIdx = 0, wkTimer, wkTouched = false;
    var activate = function (i) { panels.forEach(function (p, k) { p.classList.toggle('is-active', k === i); }); wkIdx = i; };
    panels.forEach(function (p, i) {
      p.addEventListener('mouseenter', function () { wkTouched = true; activate(i); });
      p.addEventListener('focus', function () { wkTouched = true; activate(i); });
      p.addEventListener('click', function () { wkTouched = true; activate(i); });
    });
    wk.addEventListener('mouseleave', function () { wkTouched = false; });
    wkTimer = setInterval(function () {
      if (wkTouched || reduce) return;
      var r = wk.getBoundingClientRect();
      if (r.bottom < 0 || r.top > window.innerHeight) return;
      activate((wkIdx + 1) % panels.length);
    }, 3200);
  }


  /* Studios and labs console: tabs that auto-advance (the progress bar drives the timing; hover pauses) */
  document.querySelectorAll('.sl-console').forEach(function (con) {
    var tabs = Array.prototype.slice.call(con.querySelectorAll('.sl-tab'));
    var panels = Array.prototype.slice.call(con.querySelectorAll('.sl-panel'));
    function show(i) {
      tabs.forEach(function (t) { t.classList.remove('is-active'); t.setAttribute('aria-selected', 'false'); });
      panels.forEach(function (p, k) { p.classList.toggle('is-active', k === i); });
      void tabs[i].offsetWidth;
      tabs[i].classList.add('is-active'); tabs[i].setAttribute('aria-selected', 'true');
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { show(i); });
      t.addEventListener('mouseenter', function () { show(i); });
      t.querySelector('.sl-prog').addEventListener('animationend', function () { show((i + 1) % tabs.length); });
    });
  });

  /* automatic stagger for sibling reveal elements */
  document.querySelectorAll('.pillars, .facility-grid, .campus-strip, .gallery, .isl-grid, .tbl-wrap tbody').forEach(function (g) {
    Array.prototype.slice.call(g.children).forEach(function (c, i) {
      if (!c.style.getPropertyValue('--d')) c.style.transitionDelay = Math.min(i, 5) * 90 + 'ms';
    });
  });

  /* reveal */
  var revealEls = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('is-visible'); io.unobserve(e.target); } });
    }, { threshold: 0.12 });
    revealEls.forEach(function (el) { io.observe(el); });
  } else { revealEls.forEach(function (el) { el.classList.add('is-visible'); }); }

  /* hero rotator (dots appear only when there is more than one slide) */
  var slides = document.querySelectorAll('.hero-slide');
  var dotsWrap = document.getElementById('heroDots');
  if (slides.length > 1 && dotsWrap) {
    var dots = [], current = 0, timer;
    slides.forEach(function (_, i) {
      var d = document.createElement('button');
      d.className = 'hero-dot' + (i === 0 ? ' is-active' : '');
      d.setAttribute('aria-label', 'Go to slide ' + (i + 1));
      d.addEventListener('click', function () { goTo(i); });
      dotsWrap.appendChild(d); dots.push(d);
    });
    var goTo = function (i) {
      slides[current].classList.remove('is-active'); dots[current].classList.remove('is-active');
      current = i;
      slides[current].classList.add('is-active'); dots[current].classList.add('is-active');
      clearInterval(timer); timer = setInterval(function () { goTo((current + 1) % slides.length); }, 6000);
    };
    timer = setInterval(function () { goTo((current + 1) % slides.length); }, 6000);
  }

  /* mobile menu */
  var hamburger = document.getElementById('hamburger');
  var mobileMenu = document.getElementById('mobileMenu');
  var mobileBackdrop = document.getElementById('mobileBackdrop');
  var closeMenu = document.getElementById('closeMenu');
  function openMenu() { mobileMenu.classList.add('open'); mobileBackdrop.classList.add('show'); }
  function closeMenuFn() { mobileMenu.classList.remove('open'); mobileBackdrop.classList.remove('show'); }
  if (hamburger) {
    hamburger.addEventListener('click', openMenu);
    closeMenu.addEventListener('click', closeMenuFn);
    mobileBackdrop.addEventListener('click', closeMenuFn);
    mobileMenu.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', closeMenuFn); });
  }

  /* accordion (FAQ) — same open/close behaviour as the reference curriculum accordion */
  document.querySelectorAll('.acc').forEach(function (acc) {
    acc.querySelectorAll('.acc-item').forEach(function (item) {
      var trigger = item.querySelector('.acc-trigger');
      var panel = item.querySelector('.acc-panel');
      trigger.addEventListener('click', function () {
        var wasOpen = item.classList.contains('is-open');
        acc.querySelectorAll('.acc-item').forEach(function (other) {
          other.classList.remove('is-open');
          other.querySelector('.acc-trigger').setAttribute('aria-expanded', 'false');
          other.querySelector('.acc-panel').style.maxHeight = null;
        });
        if (!wasOpen) {
          item.classList.add('is-open');
          trigger.setAttribute('aria-expanded', 'true');
          panel.style.maxHeight = panel.scrollHeight + 'px';
        }
      });
    });
  });
  window.addEventListener('resize', function () {
    document.querySelectorAll('.acc-item.is-open .acc-panel').forEach(function (p) { p.style.maxHeight = p.scrollHeight + 'px'; });
  });
})();
