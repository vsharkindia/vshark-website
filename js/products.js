/* =========================================================
   PRODUCTS — 3D scanners shown on the homepage.
   Kept deliberately short: full specifications live on the products page.
   ► To update, edit only this list.
     name   : model name
     type   : one short line
     figure : one headline number, unit : what it measures
     image  : transparent PNG in img/products/
     link   : the product's page
   ========================================================= */
window.VSHARK_PRODUCTS = [
  {
    name: 'Vertex3D',
    type: 'Handheld blue-laser scanner · 26 laser lines',
    figure: '0.020', unit: 'mm precision',
    image: 'img/products/vertex3d.png',
    link: 'products.php#vertex3d',
  },
  {
    name: 'Vertex3D Pro',
    type: 'Handheld blue-laser scanner · 50 laser lines',
    figure: '0.020', unit: 'mm precision',
    image: 'img/products/vertex3d-pro.png',
    link: 'products.php#vertex3d-pro',
  },
  {
    name: 'Vertex Tracker',
    type: 'Optical-tracking scanner · 1100 × 800 mm field',
    figure: '0.025', unit: 'mm precision',
    image: 'img/products/vertex-tracker.png',
    link: 'products.php#vertex-tracker',
  },
];

/* ---------- rendering (no need to edit below) ---------- */
(function () {
  const grid = document.getElementById('productGrid');
  if (!grid) return;
  const esc = (t) => String(t).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  grid.innerHTML = window.VSHARK_PRODUCTS.map((p, i) => `
    <article class="prod" data-reveal>
      <div class="prod__tile">
        <div class="prod__stage" aria-hidden="true">
          <span class="prod__num">${String(i + 1).padStart(2, '0')}</span>
          <i class="prod__slash prod__slash--grey"></i>
          <i class="prod__slash prod__slash--red"></i>
        </div>
        <div class="prod__body">
          <h3>${esc(p.name)}</h3>
          <p class="prod__type">${esc(p.type)}</p>
          <div class="prod__fig"><b>${esc(p.figure)}</b><span class="mono">${esc(p.unit)}</span></div>
          <span class="prod__more">View product <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></span>
        </div>
      </div>
      <img class="prod__img" src="${esc(p.image)}" alt="${esc(p.name)} 3D scanner" loading="lazy" draggable="false">
      <span class="prod__scan" aria-hidden="true"></span>
      <a class="prod__link" href="${esc(p.link)}" aria-label="${esc(p.name)} — view product"></a>
    </article>`).join('');
})();
