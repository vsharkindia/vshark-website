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
  function splitWords(el) {
    const words = el.textContent.trim().split(/\s+/);
    el.innerHTML = words.map((w) => `<span class="w">${w}</span>`).join(' ');
    return $$('.w', el);
  }
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
  const heroWord = $('#heroWord');
  const hudIdx = $('#hudIdx'), hudShape = $('#hudShape'), hudPts = $('#hudPts');
  if (hero && hero.ok) {
    if (hudPts) hudPts.textContent = 'PTS ' + hero.count.toLocaleString('en-US').padStart(6, '0');
    hero.onShape((i, s) => {
      if (heroWord) scramble(heroWord, s.word);
      if (hudIdx) hudIdx.textContent = String(i + 1).padStart(2, '0');
      if (hudShape) scramble(hudShape, s.name, 0.6);
    });
    ScrollTrigger.create({
      trigger: '#hero', start: 'top top', end: 'bottom top', scrub: true,
      onUpdate: (self) => hero.setScrollProgress(self.progress),
    });
  } else if (heroWord) {
    // no WebGL — still cycle words
    const words = ['3D Scanning Solutions', 'Reverse Engineering', 'Scan to BIM Modelling', 'Class A Surfacing'];
    let wi = 0;
    setInterval(() => { wi = (wi + 1) % words.length; scramble(heroWord, words[wi]); }, 3500);
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

  /* ---------- About statement: word-by-word light-up ---------- */
  const stmt = $('#aboutStatement');
  if (stmt && !reduceMotion) {
    const words = splitWords(stmt);
    gsap.to(words, {
      opacity: 1, stagger: 0.1, ease: 'none',
      scrollTrigger: { trigger: stmt, start: 'top 80%', end: 'bottom 45%', scrub: true },
    });
  }

  /* ---------- Image clip reveal ---------- */
  $$('.reveal-clip').forEach((fig) => {
    const img = $('img', fig);
    gsap.fromTo(fig, { clipPath: 'inset(100% 0 0 0)' }, {
      clipPath: 'inset(0% 0 0 0)', duration: 1.6, ease: 'expo.inOut',
      scrollTrigger: { trigger: fig, start: 'top 80%' },
    });
    gsap.to(img, { scale: 1, ease: 'none', scrollTrigger: { trigger: fig, start: 'top bottom', end: 'bottom top', scrub: true } });
  });

  /* ---------- Counters ---------- */
  $$('[data-count]').forEach((el) => {
    const end = +el.dataset.count;
    const o = { v: 0 };
    ScrollTrigger.create({
      trigger: el, start: 'top 90%', once: true,
      onEnter: () => gsap.to(o, { v: end, duration: 2.2, ease: 'power3.out', onUpdate: () => { el.textContent = Math.round(o.v).toLocaleString('en-US'); } }),
    });
  });

  /* ---------- Services: pinned horizontal scroll (desktop) ---------- */
  const mm = gsap.matchMedia();
  mm.add('(min-width: 901px)', () => {
    const track = $('#servicesTrack');
    const pinEl = $('.services__pin');
    const cards = $$('.card', track);
    const progEl = $('#svcProgress'), bar = $('#svcBar');
    const distance = () => track.scrollWidth - (pinEl.clientWidth - track.offsetLeft) + 56;
    const tween = gsap.to(track, {
      x: () => -distance(), ease: 'none',
      scrollTrigger: {
        trigger: '.services', pin: pinEl, start: 'top top', end: () => '+=' + distance(),
        scrub: 1, invalidateOnRefresh: true,
        onUpdate: (self) => {
          const i = Math.min(cards.length, Math.floor(self.progress * cards.length) + 1);
          progEl.textContent = String(i).padStart(2, '0');
          bar.style.transform = `scaleX(${Math.max(1 / cards.length, self.progress)})`;
        },
      },
    });
    // subtle 3D tilt per card while moving
    cards.forEach((card) => {
      gsap.fromTo(card, { rotateY: -14, z: -80 }, {
        rotateY: 0, z: 0, ease: 'none',
        scrollTrigger: { trigger: card, containerAnimation: tween, start: 'left right', end: 'left 55%', scrub: true },
      });
    });
    return () => gsap.set(track, { clearProps: 'transform' });
  });

  /* card hover tilt */
  if (finePointer) {
    $$('.card').forEach((card) => {
      const media = $('.card__media img', card);
      card.addEventListener('pointermove', (e) => {
        const r = card.getBoundingClientRect();
        const px = (e.clientX - r.left) / r.width - 0.5, py = (e.clientY - r.top) / r.height - 0.5;
        gsap.to(media, { xPercent: -px * 4, yPercent: -py * 4, duration: 0.6, ease: 'power3.out' });
      });
      card.addEventListener('pointerleave', () => gsap.to(media, { xPercent: 0, yPercent: 0, duration: 0.8, ease: 'power3.out' }));
    });
  }

  /* ---------- Industries: floating image follower ---------- */
  const float = $('#indFloat'), floatInner = $('.ind__float-inner', float);
  if (finePointer && float) {
    const xTo = gsap.quickTo(float, 'x', { duration: 0.6, ease: 'power3' });
    const yTo = gsap.quickTo(float, 'y', { duration: 0.6, ease: 'power3' });
    let lastX = 0, px = -1, py = -1, current = null;
    // hit-test rather than enter/leave events, so scrolling under a still pointer also updates
    function hitTest() {
      if (px < 0) return;
      const el = document.elementFromPoint(px, py);
      const row = el && el.closest('.ind__row');
      if (row === current) return;
      current = row;
      if (row) {
        floatInner.style.backgroundImage = `url("${row.dataset.img}")`;
        gsap.to(float, { opacity: 1, scale: 1, duration: 0.5, ease: 'expo.out' });
      } else {
        gsap.to(float, { opacity: 0, scale: 0.6, duration: 0.4, ease: 'power3.out' });
      }
    }
    window.addEventListener('pointermove', (e) => {
      px = e.clientX; py = e.clientY;
      xTo(px); yTo(py);
      const vx = px - lastX; lastX = px;
      gsap.to(float, { rotate: gsap.utils.clamp(-12, 12, vx * 0.6), duration: 0.6, ease: 'power3' });
      hitTest();
    }, { passive: true });
    window.addEventListener('scroll', hitTest, { passive: true });
    // safety net for programmatic/smooth scrolls: re-check while the preview is showing
    gsap.ticker.add(() => { if (current) hitTest(); });
    gsap.set(float, { xPercent: -50, yPercent: -50, scale: 0.6 });
  }
  gsap.from('.ind__row', {
    y: 60, opacity: 0, duration: 1.2, ease: 'expo.out', stagger: 0.08,
    scrollTrigger: { trigger: '#industryList', start: 'top 85%' },
  });

  /* ---------- Testimonials ---------- */
  const slides = $$('.testi__slide');
  const tIdx = $('#testiIdx'), tBar = $('#testiBar');
  let ti = 0, tTimer = null, barTween = null;
  slides.forEach((s) => splitWords($('p', s)));
  function showSlide(n, dir = 1) {
    const prev = slides[ti];
    ti = (n + slides.length) % slides.length;
    const next = slides[ti];
    if (prev !== next) {
      gsap.to($$('.w', prev), { y: -30 * dir, opacity: 0, duration: 0.5, ease: 'power3.in', stagger: 0.006, onComplete: () => prev.classList.remove('is-active') });
      gsap.to($('cite', prev), { opacity: 0, duration: 0.4 });
    }
    next.classList.add('is-active');
    gsap.fromTo($$('.w', next), { y: 40 * dir, opacity: 0 }, { y: 0, opacity: 1, duration: 1, ease: 'expo.out', stagger: 0.012, delay: prev !== next ? 0.45 : 0 });
    gsap.fromTo($('cite', next), { opacity: 0 }, { opacity: 1, duration: 0.8, delay: 0.9 });
    tIdx.textContent = String(ti + 1).padStart(2, '0');
    barTween?.kill();
    barTween = gsap.fromTo(tBar, { scaleX: 0 }, { scaleX: 1, duration: 7, ease: 'none' });
    clearTimeout(tTimer);
    tTimer = setTimeout(() => showSlide(ti + 1), 7000);
  }
  $('#testiNext')?.addEventListener('click', () => showSlide(ti + 1, 1));
  $('#testiPrev')?.addEventListener('click', () => showSlide(ti - 1, -1));
  // swipe
  let sx = null;
  const stage = $('#testi');
  stage?.addEventListener('pointerdown', (e) => { sx = e.clientX; });
  stage?.addEventListener('pointerup', (e) => {
    if (sx === null) return; const dx = e.clientX - sx; sx = null;
    if (Math.abs(dx) > 50) showSlide(ti + (dx < 0 ? 1 : -1), dx < 0 ? 1 : -1);
  });
  ScrollTrigger.create({ trigger: '.testi', start: 'top 70%', once: true, onEnter: () => showSlide(0) });

  /* ---------- CTA title ---------- */
  gsap.from('.cta__title .line-mask > span', {
    yPercent: 110, duration: 1.4, ease: 'expo.out', stagger: 0.1,
    scrollTrigger: { trigger: '.cta', start: 'top 70%' },
  });
  gsap.from('.cta__btn', { scale: 0, rotate: -90, duration: 1.4, ease: 'elastic.out(1, 0.6)', scrollTrigger: { trigger: '.cta__btn', start: 'top 90%' } });

  /* ---------- CTA background: interactive dot field ---------- */
  (function dotField() {
    const c = $('#ctaCanvas'); if (!c) return;
    const ctx = c.getContext('2d');
    let w, h, dpr, dots = [], active = false;
    const m = { x: -9999, y: -9999 };
    function build() {
      dpr = Math.min(devicePixelRatio || 1, 2);
      w = c.clientWidth; h = c.clientHeight;
      c.width = w * dpr; c.height = h * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      dots = [];
      const gap = w < 700 ? 26 : 32;
      for (let y = gap / 2; y < h; y += gap) for (let x = gap / 2; x < w; x += gap) dots.push({ x, y });
    }
    c.parentElement.addEventListener('pointermove', (e) => { const r = c.getBoundingClientRect(); m.x = e.clientX - r.left; m.y = e.clientY - r.top; });
    c.parentElement.addEventListener('pointerleave', () => { m.x = m.y = -9999; });
    new IntersectionObserver(([en]) => { active = en.isIntersecting; }).observe(c);
    window.addEventListener('resize', build);
    build();
    let t = 0;
    (function draw() {
      requestAnimationFrame(draw);
      if (!active) return;
      t += 0.016;
      ctx.clearRect(0, 0, w, h);
      const R = 180;
      for (const d of dots) {
        const dx = d.x - m.x, dy = d.y - m.y, dist = Math.hypot(dx, dy);
        const wave = Math.sin(d.x * 0.012 + d.y * 0.008 + t * 1.4) * 0.5 + 0.5;
        let ox = 0, oy = 0, glow = 0;
        if (dist < R) { const f = 1 - dist / R; ox = (dx / (dist || 1)) * f * 22; oy = (dy / (dist || 1)) * f * 22; glow = f; }
        const r = 0.9 + wave * 0.6 + glow * 2.2;
        ctx.fillStyle = glow > 0.02 ? `rgba(153,27,46,${0.25 + glow * 0.75})` : `rgba(28,33,37,${0.07 + wave * 0.1})`;
        ctx.beginPath(); ctx.arc(d.x + ox, d.y + oy, r, 0, 6.283); ctx.fill();
      }
    })();
  })();

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
      const h = e.target.closest('a, button, .ind__row');
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

  /* refresh after images load (layout shifts affect pin distances) */
  window.addEventListener('load', () => ScrollTrigger.refresh());
})();
