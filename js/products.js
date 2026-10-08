/* =========================================================
   PRODUCTS — 3D scanners for sale.
   ► To update the products, edit only the list below.
     name   : model name, e.g. "Brand Model X"
     type   : short category line
     image  : path to a photo in img/products/ (leave '' to show the drawing)
     specs  : up to 4 [label, value] rows
     price  : e.g. "₹ 4,50,000" or "Price on request"
     placeholder: true shows the yellow "Placeholder" badge — set false (or delete) for real products
   ========================================================= */
window.VSHARK_PRODUCTS = [
  {
    placeholder: true,
    name: 'Scanner model name',
    type: 'Handheld 3D scanner',
    image: '',
    specs: [['Accuracy', '— mm'], ['Resolution', '— mm'], ['Scan speed', '— fps'], ['Weight', '— kg']],
    price: 'Price on request',
  },
  {
    placeholder: true,
    name: 'Scanner model name',
    type: 'Desktop 3D scanner',
    image: '',
    specs: [['Accuracy', '— mm'], ['Scan volume', '— mm'], ['Scan time', '— s'], ['Weight', '— kg']],
    price: 'Price on request',
  },
  {
    placeholder: true,
    name: 'Scanner model name',
    type: 'Long-range laser scanner',
    image: '',
    specs: [['Range', '— m'], ['Accuracy', '— mm'], ['Scan rate', '— pts/s'], ['Weight', '— kg']],
    price: 'Price on request',
  },
];

/* ---------- rendering (no need to edit below) ---------- */
(function () {
  const grid = document.getElementById('productGrid');
  if (!grid) return;
  const WHATSAPP = '919514248525';
  const esc = (t) => String(t).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  // generic handheld-scanner drawing, used until a product photo is supplied
  const drawing = `
    <svg class="prod__draw" viewBox="0 0 240 180" aria-hidden="true">
      <defs><linearGradient id="beam" x1="0" x2="1"><stop offset="0" stop-color="#991b2e" stop-opacity=".55"/><stop offset="1" stop-color="#991b2e" stop-opacity="0"/></linearGradient></defs>
      <path d="M150 62 L232 30 L232 120 Z" fill="url(#beam)"/>
      <g stroke="#991b2e" stroke-width="1" opacity=".7"><path d="M150 62 L232 44"/><path d="M150 62 L232 62"/><path d="M150 62 L232 80"/><path d="M150 62 L232 98"/></g>
      <rect x="62" y="38" width="92" height="50" rx="14" fill="#e3e6e9" stroke="#616b6f" stroke-width="2"/>
      <rect x="140" y="47" width="14" height="32" rx="4" fill="#1c2125"/>
      <circle cx="147" cy="56" r="3" fill="#991b2e"/><circle cx="147" cy="70" r="3" fill="#991b2e"/>
      <path d="M86 88 L74 150 a8 8 0 0 0 8 9 h18 a8 8 0 0 0 8-7 L116 88" fill="#cfd4d8" stroke="#616b6f" stroke-width="2"/>
      <rect x="76" y="48" width="40" height="8" rx="4" fill="#991b2e"/>
    </svg>`;

  grid.innerHTML = window.VSHARK_PRODUCTS.map((p) => {
    const msg = encodeURIComponent(`Hi VShark, I'm interested in the ${p.type}${p.placeholder ? '' : ` "${p.name}"`}. Please share details and a quote.`);
    return `
      <article class="prod" data-reveal>
        ${p.placeholder ? '<span class="prod__badge mono">Placeholder</span>' : ''}
        <div class="prod__media">
          ${p.image ? `<img src="${esc(p.image)}" alt="${esc(p.name)}" loading="lazy">` : drawing}
        </div>
        <div class="prod__body">
          <span class="prod__type mono">${esc(p.type)}</span>
          <h3>${esc(p.name)}</h3>
          <dl class="prod__specs">${p.specs.slice(0, 4).map(([k, v]) => `<div><dt>${esc(k)}</dt><dd>${esc(v)}</dd></div>`).join('')}</dl>
          <div class="prod__foot">
            <span class="prod__price">${esc(p.price)}</span>
            <a class="btn btn--sm btn--accent" href="https://wa.me/${WHATSAPP}?text=${msg}" target="_blank" rel="noopener"><span>Enquire</span></a>
          </div>
        </div>
      </article>`;
  }).join('');
})();
