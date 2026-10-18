/* =========================================================
   Products page — specification popups (one <dialog> per scanner).
   Opens from the "Specifications" buttons, or directly via
   products/index.html#specs-<slug> (shareable link).
   ========================================================= */
(function () {
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const dialogs = $$('dialog.sd');
  if (!dialogs.length) return;
  let opener = null;

  function open(slug, from) {
    const d = document.getElementById('spec-' + slug);
    if (!d || d.open) return;
    opener = from || null;
    d.showModal();
    window.VSharkLenis?.stop();
    document.documentElement.classList.add('sd-open');
    d.querySelector('.sd__panel').scrollTop = 0;
    if (window.gsap) gsap.fromTo(d.querySelector('.sd__panel'), { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.6, ease: 'expo.out' });
    history.replaceState(null, '', '#specs-' + slug);
  }
  function close(d) {
    if (!d.open) return;
    d.close();
  }

  $$('[data-spec-open]').forEach((b) => b.addEventListener('click', () => open(b.dataset.specOpen, b)));
  dialogs.forEach((d) => {
    d.querySelector('[data-spec-close]').addEventListener('click', () => close(d));
    // click on the dimmed backdrop (outside the panel) closes
    d.addEventListener('click', (e) => { if (e.target === d) close(d); });
    d.addEventListener('close', () => {
      window.VSharkLenis?.start();
      document.documentElement.classList.remove('sd-open');
      d.querySelectorAll('video').forEach((v) => v.pause());
      if (location.hash.startsWith('#specs-')) history.replaceState(null, '', location.pathname + location.search);
      opener?.focus();
    });
  });

  // deep link: products/index.html#specs-vertex3d-pro
  const m = location.hash.match(/^#specs-([\w-]+)/);
  if (m) setTimeout(() => open(m[1]), 400);
})();
