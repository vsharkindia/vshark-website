/* =========================================================
   REVIEW ONLY — headline font tester.
   Appears on localhost, Netlify deploy previews (…--vshark-preview…)
   or any URL with ?fonts. Delete this file and its <script> tag
   (and fonts/fonts-candidates.css + candidate .woff2 files) at go-live.
   ========================================================= */
(function () {
  const host = location.hostname;
  const enabled = location.protocol === 'file:' || host === 'localhost' || host === '127.0.0.1' ||
    host.includes('--') || /[?&]fonts\b/.test(location.search);
  if (!enabled) return;

  const FONTS = [
    { key: 'space', name: 'Space Grotesk', note: 'current · technical', family: '"Space Grotesk"', weight: 500, track: '-0.045em', size: 1 },
    { key: 'sora', name: 'Sora', note: 'geometric · clean', family: '"Sora"', weight: 600, track: '-0.05em', size: 0.94 },
    { key: 'syne', name: 'Syne', note: 'bold · distinctive', family: '"Syne"', weight: 700, track: '-0.04em', size: 0.96 },
    { key: 'archivo', name: 'Archivo', note: 'industrial · strong', family: '"Archivo"', weight: 600, track: '-0.04em', size: 1 },
    { key: 'manrope', name: 'Manrope', note: 'modern · friendly', family: '"Manrope"', weight: 700, track: '-0.05em', size: 0.97 },
    { key: 'instrument', name: 'Instrument Serif', note: 'editorial · premium', family: '"Instrument Serif"', weight: 400, track: '-0.02em', size: 1.12 },
  ];
  const STORE = 'vshark-font-test';
  const read = (k, d) => { try { return localStorage.getItem(k) || d; } catch (e) { return d; } };
  const write = (k, v) => { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } };

  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = 'fonts/fonts-candidates.css';
  document.head.appendChild(link);

  const css = document.createElement('style');
  css.textContent = `
    html[data-font-scope="hero"] .hero__title,
    html[data-font-scope="all"] .hero__title {
      font-family: var(--ft-family), system-ui, sans-serif; font-weight: var(--ft-weight);
      letter-spacing: var(--ft-track); font-size: calc(clamp(40px, min(6.6vw, 10.5vh), 120px) * var(--ft-size));
    }
    html[data-font-scope] .hero__title em { font-style: var(--ft-em, normal); }
    html[data-font-scope="all"] { --display: var(--ft-family), system-ui, sans-serif; }

    .ft { position: fixed; left: 50%; top: 84px; transform: translateX(-50%); z-index: 950; display: flex; align-items: center; gap: 6px;
      padding: 6px; border-radius: 14px; background: rgba(255,255,255,.95); border: 1px solid rgba(28,33,37,.14);
      box-shadow: 0 16px 40px -18px rgba(28,33,37,.4); backdrop-filter: blur(10px); color: #1c2125; font-family: "Inter", system-ui, sans-serif; }
    .ft__label { padding: 0 8px 0 6px; min-width: 132px; line-height: 1.25; }
    .ft__label small { display: block; font: 500 9.5px "JetBrains Mono", monospace; letter-spacing: .08em; text-transform: uppercase; color: #991b2e; }
    .ft__label b { font-size: 13px; font-weight: 600; white-space: nowrap; }
    .ft__opt { position: relative; width: 46px; height: 42px; border-radius: 10px; border: 1px solid transparent; background: #f1f2f4; cursor: pointer; color: inherit; font-size: 19px; line-height: 1; }
    .ft__opt i { position: absolute; top: 3px; left: 5px; font: 500 8.5px "JetBrains Mono", monospace; font-style: normal; color: #991b2e; }
    .ft__opt:hover { background: #e7e9ec; }
    .ft__opt.is-on { border-color: #991b2e; background: rgba(153,27,46,.08); }
    .ft__sep { width: 1px; height: 28px; background: rgba(28,33,37,.12); margin: 0 2px; }
    .ft__scope { font: 500 11px "Inter", sans-serif; height: 42px; padding: 0 10px; border-radius: 10px; border: 1px solid rgba(28,33,37,.14); background: #fff; cursor: pointer; color: #1c2125; }
    .ft__scope.is-on { background: #1c2125; color: #fff; border-color: #1c2125; }
    @media (max-width: 760px) {
      .ft { left: 8px; right: 8px; top: 74px; bottom: auto; transform: none; overflow-x: auto; gap: 4px; padding: 5px; }
      .ft__label { display: none; }
      .ft__opt { flex: 0 0 40px; width: 40px; height: 38px; font-size: 16px; }
      .ft__scope { height: 38px; padding: 0 8px; flex: 0 0 auto; }
    }
  `;
  document.head.appendChild(css);

  const panel = document.createElement('div');
  panel.className = 'ft';
  panel.setAttribute('aria-label', 'Headline font tester (review only)');
  panel.innerHTML = `
    <div class="ft__label"><small>Headline font · review</small><b class="ft__sel"></b></div>
    ${FONTS.map((f, i) => `<button class="ft__opt" type="button" data-key="${f.key}" title="${String.fromCharCode(65 + i)} — ${f.name} (${f.note})"
      style="font-family:${f.family.replace(/"/g, "'")},sans-serif;font-weight:${f.weight}"><i>${String.fromCharCode(65 + i)}</i>Aa</button>`).join('')}
    <span class="ft__sep"></span>
    <button class="ft__scope" type="button" data-scope="hero">Headline</button>
    <button class="ft__scope" type="button" data-scope="all">All headings</button>`;

  function apply(key, scope) {
    const f = FONTS.find((x) => x.key === key) || FONTS[0];
    const root = document.documentElement;
    root.style.setProperty('--ft-family', f.family);
    root.style.setProperty('--ft-weight', f.weight);
    root.style.setProperty('--ft-track', f.track);
    root.style.setProperty('--ft-size', f.size);
    root.style.setProperty('--ft-em', f.key === 'instrument' ? 'italic' : 'normal');
    root.dataset.fontScope = scope;
    panel.querySelectorAll('.ft__opt').forEach((b) => b.classList.toggle('is-on', b.dataset.key === f.key));
    panel.querySelectorAll('.ft__scope').forEach((b) => b.classList.toggle('is-on', b.dataset.scope === scope));
    panel.querySelector('.ft__sel').textContent = `${String.fromCharCode(65 + FONTS.indexOf(f))} · ${f.name}`;
    write(STORE, f.key); write(STORE + '-scope', scope);
  }

  let key = read(STORE, 'space');
  let scope = read(STORE + '-scope', 'hero');
  panel.addEventListener('click', (e) => {
    const opt = e.target.closest('.ft__opt');
    const sc = e.target.closest('[data-scope]');
    if (opt) { key = opt.dataset.key; apply(key, scope); }
    else if (sc) { scope = sc.dataset.scope; apply(key, scope); }
  });

  const mount = () => { document.body.appendChild(panel); document.body.classList.add('has-ft'); apply(key, scope); };
  if (document.body) mount(); else document.addEventListener('DOMContentLoaded', mount);
})();
