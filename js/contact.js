/* Contact page: pre-select the enquiry topic from ?service=<slug> or ?product=<slug>
   (links from service and product pages pass these). */
(function () {
  const sel = document.getElementById('cInterest');
  if (!sel) return;
  const qs = new URLSearchParams(location.search);
  const slug = qs.get('service') || qs.get('product');
  if (!slug) return;
  const words = slug.replace(/-/g, ' ').toLowerCase();
  const opt = [...sel.options].find((o) => o.value.toLowerCase().replace(/^product:\s*/, '').replace(/-/g, ' ') === words);
  if (opt) sel.value = opt.value;
})();
