/* =========================================================
   VShark Solutions — interactions
   ========================================================= */
(function () {
  const doc = document.documentElement;
  doc.classList.add('js');
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  const hasGsap = !!window.gsap;
  const yearEl = $('#year'); if (yearEl) yearEl.textContent = new Date().getFullYear();

  if (!hasGsap) { // graceful fallback: show everything
    $('#loader')?.remove();
    document.body.classList.remove('is-loading');
    $$('[data-reveal]').forEach((el) => { el.style.opacity = 1; el.style.transform = 'none'; });
    window.VSharkHero?.start();
    return;
  }

  gsap.registerPlugin(ScrollTrigger);

  /* ---------- Smooth scroll ---------- */
  let lenis = null;
  if (window.Lenis && !reduceMotion) {
    lenis = new Lenis({ duration: 1.15, easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)), smoothWheel: true });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add((time) => lenis.raf(time * 1000));
    gsap.ticker.lagSmoothing(0);
    lenis.stop();
  }
  function scrollTo(target) {
    if (lenis) lenis.scrollTo(target, { offset: 0, duration: 1.4 });
    else (typeof target === 'string' ? $(target) : target)?.scrollIntoView({ behavior: 'smooth' });
  }
  $$('a[href^="#"]').forEach((a) => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href');
      if (id.length < 2) return;
      const el = $(id); if (!el) return;
      e.preventDefault();
      closeMenu();
      scrollTo(el);
    });
  });

  /* ---------- Text helpers ---------- */
  const GLYPHS = '!<>-_\\/[]{}—=+*^?#01ABCDEFXYZ';
  function scramble(el, text, dur = 0.9) {
    const from = el.textContent;
    const len = Math.max(from.length, text.length);
    const o = { p: 0 };
    gsap.killTweensOf(o);
    gsap.to(o, {
      p: 1, duration: dur, ease: 'none',
      onUpdate() {
        let out = '';
        for (let i = 0; i < len; i++) {
          const reveal = o.p * len * 1.4 - i * 0.4;
          if (reveal >= 1) out += text[i] || '';
          else if (reveal > 0) out += GLYPHS[(Math.random() * GLYPHS.length) | 0];
          else out += from[i] || '';
        }
        el.textContent = out;
      },
      onComplete() { el.textContent = text; },
    });
  }

  /* ---------- Hero ---------- */
  const hero = window.VSharkHero;
  const tabs = $$('.svc-tab');
  const hudIdx = $('#hudIdx'), hudShape = $('#hudShape'), hudPts = $('#hudPts');
  let activeTab = tabs[0];
  function setActiveTab(i) {
    tabs.forEach((b, k) => {
      const on = k === i;
      b.classList.toggle('is-active', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      if (!on) b.style.setProperty('--p', 0);
    });
    activeTab = tabs[i];
  }
  if (hero && hero.ok) {
    if (hudPts) hudPts.textContent = 'PTS ' + hero.count.toLocaleString('en-US').padStart(6, '0');
    hero.onShape((i, s) => {
      setActiveTab(i);
      if (hudIdx) hudIdx.textContent = String(i + 1).padStart(2, '0');
      if (hudShape) scramble(hudShape, s.name, 0.6);
    });
    tabs.forEach((b) => b.addEventListener('click', () => hero.select(+b.dataset.scene)));
    gsap.ticker.add(() => { if (activeTab) activeTab.style.setProperty('--p', hero.progress().toFixed(3)); });
    ScrollTrigger.create({
      trigger: '#hero', start: 'top top', end: 'bottom top', scrub: true,
      onUpdate: (self) => hero.setScrollProgress(self.progress),
    });
  } else if (tabs.length) {
    // no WebGL: tabs still highlight on click and auto-cycle
    let ti = 0;
    tabs.forEach((b, k) => b.addEventListener('click', () => { ti = k; setActiveTab(k); }));
    setInterval(() => { ti = (ti + 1) % tabs.length; setActiveTab(ti); }, 4000);
  }
  gsap.to('.hero__content', {
    yPercent: -25, opacity: 0, ease: 'none',
    scrollTrigger: { trigger: '#hero', start: 'top top', end: 'bottom top', scrub: true },
  });

  /* ---------- Preloader ---------- */
  const loader = $('#loader');
  const countEl = $('#loaderCount'), barEl = $('#loaderBar');
  const intro = gsap.timeline({ paused: true });
  intro
    .to(loader, { clipPath: 'inset(0 0 100% 0)', duration: 1.1, ease: 'expo.inOut' })
    .add(() => { document.body.classList.remove('is-loading'); lenis?.start(); hero?.start(); }, '-=0.7')
    .from('.hero .line-mask > span', { yPercent: 110, duration: 1.3, ease: 'expo.out', stagger: 0.08 }, '-=0.5')
    .from('.svc-tab', { y: 24, opacity: 0, duration: 1, ease: 'expo.out', stagger: 0.06 }, '-=1.1')
    .from('.hero__actions .btn', { y: 30, opacity: 0, duration: 1, ease: 'expo.out', stagger: 0.08 }, '-=1')
    .from('.header > *', { y: -40, opacity: 0, duration: 1, ease: 'expo.out', stagger: 0.06 }, '-=1')
    .from('.hud > div', { opacity: 0, duration: 1.2, stagger: 0.1 }, '-=0.9')
    .add(() => loader.remove());

  const prog = { v: 0 };
  let loaded = false;
  window.addEventListener('load', () => { loaded = true; });
  if (document.readyState === 'complete') loaded = true;
  const minTime = reduceMotion ? 0.2 : 1.8;
  gsap.to(prog, {
    v: 90, duration: minTime, ease: 'power2.out',
    onUpdate: renderProg,
    onComplete: function finish() {
      const go = () => gsap.to(prog, { v: 100, duration: 0.4, ease: 'power1.out', onUpdate: renderProg, onComplete: () => intro.play() });
      if (loaded) go();
      else { window.addEventListener('load', go, { once: true }); setTimeout(() => { if (!loaded) { loaded = true; go(); } }, 4000); }
    },
  });
  function renderProg() {
    countEl.textContent = String(Math.round(prog.v)).padStart(3, '0');
    barEl.style.transform = `scaleX(${prog.v / 100})`;
  }

  /* ---------- Header hide/show ---------- */
  const header = $('#header');
  let lastY = 0;
  ScrollTrigger.create({
    start: 0, end: 'max',
    onUpdate: (self) => {
      const y = self.scroll();
      header.classList.toggle('is-scrolled', y > 40);
      header.classList.toggle('is-hidden', y > 300 && y > lastY && !menuOpen);
      lastY = y;
    },
  });
  // active nav link
  $$('.nav__link[href^="#"]').forEach((link) => {
    const id = link.getAttribute('href');
    const sec = id.length > 1 ? $(id) : null;
    if (!sec) return;
    ScrollTrigger.create({
      trigger: sec, start: 'top center', end: 'bottom center',
      onToggle: (self) => link.classList.toggle('is-active', self.isActive),
    });
  });

  /* ---------- Mobile menu ---------- */
  const burger = $('#burger'), menu = $('#menu');
  let menuOpen = false;
  function closeMenu() {
    if (!menuOpen) return;
    menuOpen = false;
    burger.classList.remove('is-open'); menu.classList.remove('is-open');
    burger.setAttribute('aria-expanded', 'false'); menu.setAttribute('aria-hidden', 'true');
    lenis?.start();
  }
  burger?.addEventListener('click', () => {
    if (menuOpen) return closeMenu();
    menuOpen = true;
    burger.classList.add('is-open'); menu.classList.add('is-open');
    burger.setAttribute('aria-expanded', 'true'); menu.setAttribute('aria-hidden', 'false');
    lenis?.stop();
    gsap.fromTo('.menu__nav a', { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: 0.9, ease: 'expo.out', stagger: 0.06, delay: 0.2 });
  });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeMenu(); });

  /* ---------- Generic reveals ---------- */
  ScrollTrigger.batch('[data-reveal]', {
    start: 'top 88%',
    onEnter: (els) => {
      gsap.to(els, { opacity: 1, y: 0, duration: 1.2, ease: 'expo.out', stagger: 0.08 });
      els.forEach((el) => el.classList.add('is-in'));
    },
  });

  /* ---------- Carousels (services, industries) ----------
     Native horizontal scroll with snap (touch swipe for free), plus
     arrows, mouse drag, a progress bar and gentle autoplay. */
  $$('[data-carousel]').forEach((car) => {
    const id = car.dataset.carousel;
    const track = $('.car__track', car);
    const bar = $('.car__bar b', car);
    const slides = $$('.car__slide', track);
    const step = () => (slides[1] ? slides[1].offsetLeft - slides[0].offsetLeft : track.clientWidth);
    const maxX = () => track.scrollWidth - track.clientWidth;
    const go = (dir) => {
      const x = track.scrollLeft;
      if (dir > 0 && x >= maxX() - 4) track.scrollTo({ left: 0 });
      else if (dir < 0 && x <= 4) track.scrollTo({ left: maxX() });
      else track.scrollBy({ left: dir * step() });
    };
    $(`[data-car-next="${id}"]`)?.addEventListener('click', () => { go(1); hold(); });
    $(`[data-car-prev="${id}"]`)?.addEventListener('click', () => { go(-1); hold(); });

    const updateBar = () => {
      const vis = track.clientWidth / track.scrollWidth;
      const p = maxX() > 0 ? track.scrollLeft / maxX() : 1;
      bar.style.transform = `scaleX(${(vis + (1 - vis) * p).toFixed(3)})`;
    };
    track.addEventListener('scroll', updateBar, { passive: true });
    window.addEventListener('resize', updateBar);
    updateBar();

    // autoplay: pauses on hover, touch/drag, when off-screen, and for 6 s after any interaction
    let hovering = false, onScreen = false, heldUntil = 0;
    const hold = () => { heldUntil = Date.now() + 6000; };
    car.addEventListener('pointerenter', () => { hovering = true; });
    car.addEventListener('pointerleave', () => { hovering = false; });
    track.addEventListener('touchstart', hold, { passive: true });
    new IntersectionObserver(([en]) => { onScreen = en.isIntersecting; }).observe(car);
    if (!reduceMotion) {
      setInterval(() => {
        if (onScreen && !hovering && !document.hidden && Date.now() > heldUntil) go(1);
      }, 3500);
    }

    // mouse drag (touch uses native scrolling)
    let down = null, dragged = false;
    track.addEventListener('pointerdown', (e) => {
      if (e.pointerType !== 'mouse' || e.button !== 0) return;
      down = { x: e.clientX, left: track.scrollLeft };
      dragged = false;
    });
    window.addEventListener('pointermove', (e) => {
      if (!down) return;
      const dx = e.clientX - down.x;
      if (!dragged && Math.abs(dx) > 6) { dragged = true; track.classList.add('is-drag'); }
      if (dragged) track.scrollLeft = down.left - dx;
    });
    window.addEventListener('pointerup', () => {
      if (!down) return;
      down = null;
      if (dragged) { track.classList.remove('is-drag'); hold(); }
    });
    // a drag should not also count as a click on the card link
    track.addEventListener('click', (e) => { if (dragged) { e.preventDefault(); e.stopPropagation(); dragged = false; } }, true);
  });

  /* ---------- Services: split view (desktop) / accordion (phones) ---------- */
  const svx = $('#svx');
  if (svx) {
    const items = $$('.svx__item', svx);
    const rows = $$('.svx__row', svx);
    const imgs = $$('.svx__img', svx);
    const scan = $('.svx__scan', svx);
    const info = $('.svx__info', svx);
    const countEl = $('.svx__count b', svx), titleEl = $('.svx__title', svx), descEl = $('.svx__desc', svx), moreEl = $('.svx__more', svx);
    const panel = $('#svxPanel');
    const narrow = window.matchMedia('(max-width: 860px)');
    const AUTOPLAY = 5000;
    let cur = 0, z = 1, startedAt = performance.now(), heldUntil = 0, hovering = false, onScreen = false;

    function show(i, byUser) {
      if (byUser) heldUntil = Date.now() + 9000;
      startedAt = performance.now();
      if (i === cur) return;
      cur = i;
      items.forEach((b, k) => {
        b.classList.toggle('is-active', k === i);
        b.setAttribute('aria-selected', k === i ? 'true' : 'false');
        if (k !== i) b.style.setProperty('--p', 0);
      });
      panel.setAttribute('aria-labelledby', items[i].id);
      // new image wipes in from the top behind the laser line
      const img = imgs[i];
      img.style.zIndex = ++z;
      imgs.forEach((im) => im.classList.toggle('is-on', im === img));
      gsap.killTweensOf([img, scan]);
      gsap.fromTo(img, { clipPath: 'inset(0% 0% 100% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: 0.9, ease: 'power2.inOut' });
      gsap.fromTo(scan, { top: '0%', opacity: 1 }, { top: '100%', duration: 0.9, ease: 'power2.inOut', onComplete: () => gsap.to(scan, { opacity: 0, duration: 0.25 }) });
      // details swap
      const d = items[i].dataset;
      gsap.to(info, {
        opacity: 0, y: -8, duration: 0.18, ease: 'power1.in',
        onComplete: () => {
          countEl.textContent = String(i + 1).padStart(2, '0');
          titleEl.textContent = d.name; descEl.textContent = d.desc; moreEl.setAttribute('href', d.href);
          gsap.fromTo(info, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.5, ease: 'expo.out' });
        },
      });
    }

    items.forEach((b, i) => {
      b.addEventListener('click', () => {
        if (narrow.matches) {                      // phones: accordion
          const row = rows[i];
          const open = !row.classList.contains('is-open');
          rows.forEach((r, k) => { r.classList.toggle('is-open', open && k === i); items[k].classList.toggle('is-open', open && k === i); });
          return;
        }
        show(i, true);
      });
      b.addEventListener('pointerenter', (e) => { if (e.pointerType === 'mouse' && !narrow.matches) show(i, true); });
      b.addEventListener('focus', () => { if (!narrow.matches) show(i, true); });
    });
    svx.addEventListener('pointerenter', () => { hovering = true; });
    svx.addEventListener('pointerleave', () => { hovering = false; startedAt = performance.now(); });
    new IntersectionObserver(([en]) => { onScreen = en.isIntersecting; if (onScreen) startedAt = performance.now(); }).observe(svx);

    // autoplay with a progress bar on the active row (desktop only)
    if (!reduceMotion) {
      gsap.ticker.add(() => {
        if (narrow.matches) return;
        const paused = !onScreen || hovering || Date.now() < heldUntil || document.hidden;
        if (paused) { startedAt = performance.now() - (parseFloat(items[cur].style.getPropertyValue('--p')) || 0) * AUTOPLAY; return; }
        const p = Math.min(1, (performance.now() - startedAt) / AUTOPLAY);
        items[cur].style.setProperty('--p', p.toFixed(3));
        if (p >= 1) show((cur + 1) % items.length, false);
      });
    }
  }

  /* ---------- Testimonials: duplicate cards for a seamless loop ---------- */
  const testiTrack = $('#testiTrack');
  if (testiTrack && !reduceMotion) {
    $$('.tcard', testiTrack).forEach((c) => {
      const clone = c.cloneNode(true);
      clone.setAttribute('aria-hidden', 'true');
      testiTrack.appendChild(clone);
    });
  }

  /* ---------- Contact rail: phone numbers fly-out (tap on touch screens) ---------- */
  const phoneItem = $('.rail__item--phone');
  if (phoneItem) {
    const btn = $('.rail__btn', phoneItem);
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const open = phoneItem.classList.toggle('is-open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('click', (e) => {
      if (!phoneItem.contains(e.target)) { phoneItem.classList.remove('is-open'); btn.setAttribute('aria-expanded', 'false'); }
    });
  }
  gsap.from('.rail', { xPercent: 120, opacity: 0, duration: 1.1, ease: 'expo.out', delay: 2.4, clearProps: 'transform' });

  /* ---------- Footer big text ---------- */
  gsap.from('.footer__big', { yPercent: 40, opacity: 0, ease: 'none', scrollTrigger: { trigger: '.footer', start: 'top bottom', end: 'bottom bottom', scrub: true } });

  /* ---------- Custom cursor ---------- */
  if (finePointer) {
    const cur = $('.cursor'), dot = $('.cursor__dot'), ring = $('.cursor__ring'), label = $('.cursor__text');
    const dx = gsap.quickTo(dot, 'x', { duration: 0.1 }), dy = gsap.quickTo(dot, 'y', { duration: 0.1 });
    const rx = gsap.quickTo(ring, 'x', { duration: 0.45, ease: 'power3' }), ry = gsap.quickTo(ring, 'y', { duration: 0.45, ease: 'power3' });
    gsap.set([dot, ring], { xPercent: -50, yPercent: -50 });
    gsap.set(cur, { opacity: 0 });
    let seen = false;
    window.addEventListener('pointermove', (e) => {
      if (!seen) { // jump straight to the pointer on first move instead of flying in from 0,0
        seen = true;
        gsap.set([dot, ring], { x: e.clientX, y: e.clientY });
        gsap.to(cur, { opacity: 1, duration: 0.3 });
        doc.classList.add('has-cursor');
      }
      dx(e.clientX); dy(e.clientY); rx(e.clientX); ry(e.clientY);
    }, { passive: true });
    document.addEventListener('pointerover', (e) => {
      const l = e.target.closest('[data-cursor]');
      const h = e.target.closest('a, button, .icard');
      cur.classList.toggle('is-label', !!l);
      cur.classList.toggle('is-hover', !l && !!h);
      label.textContent = l ? l.dataset.cursor : '';
    });
    document.documentElement.addEventListener('mouseleave', () => gsap.to(cur, { opacity: 0, duration: 0.3 }));
    document.documentElement.addEventListener('mouseenter', () => gsap.to(cur, { opacity: 1, duration: 0.3 }));
  }

  /* ---------- Magnetic buttons ---------- */
  if (finePointer) {
    $$('.magnetic').forEach((el) => {
      const strength = el.classList.contains('cta__btn') ? 0.45 : 0.3;
      const xTo = gsap.quickTo(el, 'x', { duration: 0.8, ease: 'elastic.out(1, 0.4)' });
      const yTo = gsap.quickTo(el, 'y', { duration: 0.8, ease: 'elastic.out(1, 0.4)' });
      el.addEventListener('pointermove', (e) => {
        const r = el.getBoundingClientRect();
        xTo((e.clientX - (r.left + r.width / 2)) * strength);
        yTo((e.clientY - (r.top + r.height / 2)) * strength);
      });
      el.addEventListener('pointerleave', () => { xTo(0); yTo(0); });
    });
  }

  /* refresh after images load (layout shifts move trigger positions) */
  window.addEventListener('load', () => ScrollTrigger.refresh());
})();
