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

  /* ---------- lightbox ---------- */
  const lb = $('#lb');
  if (!lb) return;
  const stage = $('.lb__stage', lb), title = $('.lb__title', lb), sum = $('.lb__sum', lb), count = $('.lb__count', lb);
  let imgs = [], idx = 0, lastFocus = null;

  function compare(before, after) {
    const el = document.createElement('div');
    el.className = 'cmp';
    el.innerHTML = `<img src="${before}" alt="3D scan"><img class="cmp__after" src="${after}" alt="CAD model">
      <span class="cmp__lab cmp__lab--l mono">Scan</span><span class="cmp__lab cmp__lab--r mono">CAD</span>
      <i class="cmp__line"></i><span class="cmp__knob" aria-hidden="true">⇆</span>
      <input class="cmp__range" type="range" min="0" max="100" value="50" aria-label="Drag to compare scan and CAD">`;
    const range = $('.cmp__range', el);
    const set = (v) => el.style.setProperty('--pos', v + '%');
    range.addEventListener('input', () => set(range.value));
    // drag anywhere on the image (the range input covers it; this adds smooth pointer tracking)
    el.addEventListener('pointerdown', (e) => {
      const move = (ev) => {
        const r = el.getBoundingClientRect();
        const v = Math.max(0, Math.min(100, ((ev.clientX - r.left) / r.width) * 100));
        range.value = v; set(v);
      };
      move(e);
      el.setPointerCapture(e.pointerId);
      el.addEventListener('pointermove', move);
      el.addEventListener('pointerup', () => el.removeEventListener('pointermove', move), { once: true });
    });
    // intro sweep so visitors see it is interactive
    if (window.gsap) { const o = { v: 85 }; gsap.to(o, { v: 50, duration: 1.1, ease: 'expo.out', delay: 0.15, onUpdate: () => { range.value = o.v; set(o.v); } }); }
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
      count.textContent = 'Drag to compare';
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
