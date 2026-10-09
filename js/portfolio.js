/* =========================================================
   Portfolio — filters (Service × Industry, URL-synced),
   lightbox with scan↔CAD compare slider and image gallery.
   Used on the portfolio page and on service / industry pages.
   ========================================================= */
(function () {
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];

  /* ---------- filters (portfolio page only) ---------- */
  const grid = $('#pfGrid');
  if (grid) {
    const cards = $$('.proj', grid);
    const countEl = $('.pf__count'), empty = $('.pf__empty');
    const state = { service: '', industry: '' };
    const qs = new URLSearchParams(location.search);
    ['service', 'industry'].forEach((k) => {
      const v = qs.get(k) || '';
      if (v && $(`.chip[data-f="${k}"][data-v="${CSS.escape(v)}"]`)) state[k] = v;
    });

    function apply(push) {
      let shown = 0;
      cards.forEach((c) => {
        const ok = (!state.service || c.dataset.services.split(' ').includes(state.service)) &&
                   (!state.industry || c.dataset.industries.split(' ').includes(state.industry));
        c.hidden = !ok;
        if (ok) shown++;
      });
      $$('.pf__chips .chip').forEach((b) => b.classList.toggle('is-on', state[b.dataset.f] === b.dataset.v));
      countEl.textContent = `${shown} project${shown === 1 ? '' : 's'}`;
      empty.hidden = shown > 0;
      if (push) {
        const p = new URLSearchParams();
        if (state.service) p.set('service', state.service);
        if (state.industry) p.set('industry', state.industry);
        history.replaceState(null, '', location.pathname + (p.toString() ? '?' + p : ''));
      }
      if (window.ScrollTrigger) ScrollTrigger.refresh();
    }
    $$('.pf__chips .chip').forEach((b) => b.addEventListener('click', () => {
      state[b.dataset.f] = b.dataset.v;
      apply(true);
      if (window.gsap) gsap.fromTo(cards.filter((c) => !c.hidden), { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: 'expo.out', stagger: 0.04 });
    }));
    apply(false);
  }

  /* ---------- scan/CAD cards: the split line follows the mouse ---------- */
  const fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  if (fine) {
    $$('[data-cmp]').forEach((m) => {
      m.addEventListener('pointermove', (e) => {
        const r = m.getBoundingClientRect();
        m.classList.add('is-tracking');
        m.style.setProperty('--pos', (Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)) * 100).toFixed(1) + '%');
      });
      m.addEventListener('pointerleave', () => { m.classList.remove('is-tracking'); m.style.setProperty('--pos', '50%'); });
    });
  }

  /* ---------- project row (service & industry pages) ----------
     Desktop: the section pins and page scroll moves the row sideways.
     Phones / reduced motion: native swipe. A bar shows progress in both. */
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (window.gsap && window.ScrollTrigger) gsap.registerPlugin(ScrollTrigger);
  $$('.pcar').forEach((car) => {
    const track = $('.pcar__track', car), bar = $('.pcar__bar b', car), sec = car.closest('section');
    sec.classList.add('has-pcar');
    const setBar = (p) => { bar.style.transform = `scaleX(${Math.max(0.08, p).toFixed(3)})`; };
    const onSwipe = () => { const max = track.scrollWidth - track.clientWidth; setBar(max > 0 ? track.scrollLeft / max : 1); };
    track.addEventListener('scroll', onSwipe, { passive: true });
    onSwipe();
    if (!window.gsap || !window.ScrollTrigger || reduce) return;
    gsap.matchMedia().add('(min-width: 901px)', () => {
      car.classList.add('is-pinned');
      track.scrollLeft = 0;
      // last card's right edge + the page gutter (padding isn't counted in scrollWidth while overflow is visible)
      const dist = () => {
        const last = track.lastElementChild;
        const pad = parseFloat(getComputedStyle(track).paddingLeft) || 0;
        return Math.max(0, last.offsetLeft + last.offsetWidth + pad - track.clientWidth);
      };
      if (dist() < 10) { setBar(1); return () => car.classList.remove('is-pinned'); }
      const tween = gsap.to(track, {
        x: () => -dist(), ease: 'none',
        scrollTrigger: {
          trigger: sec, start: 'top top', end: () => '+=' + dist(), pin: true, scrub: 0.6,
          invalidateOnRefresh: true, onUpdate: (st) => setBar(st.progress),
        },
      });
      return () => { tween.scrollTrigger?.kill(); tween.kill(); gsap.set(track, { clearProps: 'transform' }); car.classList.remove('is-pinned'); };
    });
  });
  window.addEventListener('load', () => window.ScrollTrigger && ScrollTrigger.refresh());

  /* ---------- lightbox ---------- */
  const lb = $('#lb');
  if (!lb) return;
  const stage = $('.lb__stage', lb), title = $('.lb__title', lb), sum = $('.lb__sum', lb), count = $('.lb__count', lb);
  let imgs = [], idx = 0, lastFocus = null;

  function compare(before, after) {
    const el = document.createElement('div');
    el.className = 'cmp';
    el.innerHTML = `<img src="${before}" alt="3D scan"><img class="cmp__cad" src="${after}" alt="CAD model">
      <span class="cmp__lab cmp__lab--l mono">CAD</span><span class="cmp__lab cmp__lab--r mono">Scan</span>
      <i class="cmp__line"></i><span class="cmp__knob" aria-hidden="true">⇆</span>
      <input class="cmp__range" type="range" min="0" max="100" value="50" aria-label="Compare CAD and scan">`;
    const range = $('.cmp__range', el);
    let intro = null;
    const set = (v) => { el.style.setProperty('--pos', v + '%'); range.value = v; };
    const fromEvent = (ev) => { const r = el.getBoundingClientRect(); return Math.max(0, Math.min(100, ((ev.clientX - r.left) / r.width) * 100)); };
    range.addEventListener('input', () => set(+range.value));          // keyboard
    // mouse: the line simply follows the cursor; touch/pen: drag with a finger
    el.addEventListener('pointermove', (e) => {
      if (e.pointerType === 'mouse' || el.dataset.dragging) { intro?.kill(); set(fromEvent(e)); }
    });
    el.addEventListener('pointerdown', (e) => {
      if (e.pointerType === 'mouse') return;
      intro?.kill(); el.dataset.dragging = '1'; try { el.setPointerCapture(e.pointerId); } catch (_) {} set(fromEvent(e));
    });
    const stop = () => { delete el.dataset.dragging; };
    el.addEventListener('pointerup', stop); el.addEventListener('pointercancel', stop);
    // intro sweep so visitors see it is interactive
    set(50);
    if (window.gsap) { const o = { v: 82 }; intro = gsap.to(o, { v: 50, duration: 1.1, ease: 'expo.out', delay: 0.15, onUpdate: () => set(o.v) }); }
    return el;
  }

  function showImg() {
    stage.innerHTML = '';
    const im = document.createElement('img');
    im.src = imgs[idx]; im.alt = title.textContent;
    stage.appendChild(im);
    count.textContent = imgs.length > 1 ? `${idx + 1} / ${imgs.length}` : '';
  }

  function open(card) {
    lastFocus = document.activeElement;
    const d = card.dataset;
    title.textContent = d.title; sum.textContent = d.summary;
    lb.classList.remove('is-pair', 'is-single');
    if (d.kind === 'pair') {
      lb.classList.add('is-pair');
      stage.innerHTML = ''; stage.appendChild(compare(d.before, d.after));
      count.textContent = fine ? 'Move the cursor to compare' : 'Drag to compare';
    } else {
      imgs = d.images.split('|'); idx = 0;
      if (imgs.length < 2) lb.classList.add('is-single');
      showImg();
    }
    lb.classList.add('is-open'); lb.setAttribute('aria-hidden', 'false');
    document.documentElement.style.overflow = 'hidden';
    $('.lb__close', lb).focus();
  }
  function close() {
    lb.classList.remove('is-open'); lb.setAttribute('aria-hidden', 'true');
    document.documentElement.style.overflow = '';
    setTimeout(() => { stage.innerHTML = ''; }, 300);
    lastFocus?.focus();
  }
  const step = (d) => { idx = (idx + d + imgs.length) % imgs.length; showImg(); };

  $$('.proj__open').forEach((b) => b.addEventListener('click', () => open(b.closest('.proj'))));
  $('.lb__close', lb).addEventListener('click', close);
  $('.lb__prev', lb).addEventListener('click', () => step(-1));
  $('.lb__next', lb).addEventListener('click', () => step(1));
  lb.addEventListener('click', (e) => { if (e.target === lb) close(); });
  document.addEventListener('keydown', (e) => {
    if (!lb.classList.contains('is-open')) return;
    if (e.key === 'Escape') close();
    if (lb.classList.contains('is-pair') || lb.classList.contains('is-single')) return;
    if (e.key === 'ArrowRight') step(1);
    if (e.key === 'ArrowLeft') step(-1);
  });
})();
