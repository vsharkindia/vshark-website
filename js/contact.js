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

/* Contact page: if the server sent the visitor back (?error=…), say what went wrong above the form. */
(function () {
  const code = new URLSearchParams(location.search).get('error');
  const form = document.getElementById('enquiry');
  if (!code || !form) return;
  const MSG = {
    missing: 'Please fill in your name, a valid email address, what you are interested in and your project details.',
    consent: 'Please tick the consent box so we can respond to your enquiry.',
    size: 'The attachment is larger than 8 MB. Please attach a smaller file, or email it to info@vsharksolutions.com.',
    type: 'That file type can’t be attached. Please use PDF, JPG, PNG, STL, STEP or ZIP.',
    upload: 'The file didn’t upload completely. Please try again.',
  };
  const note = document.createElement('p');
  note.className = 'cform__error';
  note.setAttribute('role', 'alert');
  note.textContent = MSG[code] || 'Sorry, your enquiry could not be sent. Please email info@vsharksolutions.com or message us on WhatsApp.';
  form.prepend(note);
})();
