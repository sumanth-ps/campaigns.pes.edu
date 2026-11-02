const header = document.getElementById('siteHeader');
  window.addEventListener('scroll', () => { header.classList.toggle('scrolled', window.scrollY > 20); }, { passive:true });

  const revealEls = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window){
    const io = new IntersectionObserver((entries) => { entries.forEach(e => { if (e.isIntersecting){ e.target.classList.add('is-visible'); io.unobserve(e.target); } }); }, { threshold: 0.15 });
    revealEls.forEach(el => io.observe(el));
  } else { revealEls.forEach(el => el.classList.add('is-visible')); }

  /* hero rotator */
  (function(){
    var slides = document.querySelectorAll('.hero-slide');
    var dotsWrap = document.getElementById('heroDots');
    if(!slides.length || !dotsWrap) return;
    var dots = [];
    slides.forEach(function(_, i){
      var d = document.createElement('button');
      d.className = 'hero-dot' + (i === 0 ? ' is-active' : '');
      d.setAttribute('aria-label', 'Go to slide ' + (i+1));
      d.addEventListener('click', function(){ goTo(i); });
      dotsWrap.appendChild(d);
      dots.push(d);
    });
    var current = 0, timer;
    function goTo(i){ slides[current].classList.remove('is-active'); dots[current].classList.remove('is-active'); current = i; slides[current].classList.add('is-active'); dots[current].classList.add('is-active'); resetTimer(); }
    function next(){ goTo((current + 1) % slides.length); }
    function resetTimer(){ clearInterval(timer); timer = setInterval(next, 6000); }
    resetTimer();
  })();

  /* mobile menu */
  const hamburger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobileMenu');
  const mobileBackdrop = document.getElementById('mobileBackdrop');
  const closeMenu = document.getElementById('closeMenu');
  function openMenu(){ mobileMenu.classList.add('open'); mobileBackdrop.classList.add('show'); }
  function closeMenuFn(){ mobileMenu.classList.remove('open'); mobileBackdrop.classList.remove('show'); }
  hamburger.addEventListener('click', openMenu);
  closeMenu.addEventListener('click', closeMenuFn);
  mobileBackdrop.addEventListener('click', closeMenuFn);
  mobileMenu.querySelectorAll('a').forEach(a=>a.addEventListener('click', closeMenuFn));

  /* back to top */
  const toTop = document.getElementById('toTop');
  window.addEventListener('scroll', () => { toTop.classList.toggle('show', window.scrollY > 480); }, { passive:true });

  /* curriculum modals + accordions */
  (function(){
    var backdrops = document.querySelectorAll('.modal-backdrop');
    var activeBackdrop = null;

    backdrops.forEach(function(backdrop){
      backdrop.querySelectorAll('.acc-item.is-open .acc-panel').forEach(function(panel){
        panel.style.maxHeight = panel.scrollHeight + 'px';
      });
    });

    function openModal(id){
      var backdrop = document.getElementById(id);
      if (!backdrop) return;
      backdrop.classList.add('show');
      document.body.classList.add('modal-open');
      activeBackdrop = backdrop;
    }
    function closeModal(backdrop){
      backdrop.classList.remove('show');
      document.body.classList.remove('modal-open');
      if (activeBackdrop === backdrop) activeBackdrop = null;
    }

    document.querySelectorAll('[data-modal-open]').forEach(function(btn){
      btn.addEventListener('click', function(){ openModal(btn.getAttribute('data-modal-open')); });
    });

    backdrops.forEach(function(backdrop){
      backdrop.addEventListener('click', function(e){ if (e.target === backdrop) closeModal(backdrop); });
      backdrop.querySelectorAll('[data-modal-close]').forEach(function(btn){
        btn.addEventListener('click', function(){ closeModal(backdrop); });
      });
      backdrop.querySelectorAll('.acc-item').forEach(function(item){
        var trigger = item.querySelector('.acc-trigger');
        var panel = item.querySelector('.acc-panel');
        trigger.addEventListener('click', function(){
          var wasOpen = item.classList.contains('is-open');
          item.parentElement.querySelectorAll('.acc-item').forEach(function(other){
            other.classList.remove('is-open');
            other.querySelector('.acc-trigger').setAttribute('aria-expanded', 'false');
            other.querySelector('.acc-panel').style.maxHeight = null;
          });
          if (!wasOpen){
            item.classList.add('is-open');
            trigger.setAttribute('aria-expanded', 'true');
            panel.style.maxHeight = panel.scrollHeight + 'px';
          }
        });
      });
    });

    document.addEventListener('keydown', function(e){
      if (e.key === 'Escape' && activeBackdrop) closeModal(activeBackdrop);
    });
  })();
