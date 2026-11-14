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
    size: 'The attachment is larger than 5 MB. Please attach a smaller file, or send it by WhatsApp or to info@vsharksolutions.com.',
    type: 'That file type can’t be attached. Please use PDF, Word, JPG, PNG, WEBP, HEIC, STL, STEP, IGES, OBJ, PLY or ZIP.',
    upload: 'The file didn’t upload completely. Please try again.',
  };
  const note = document.createElement('p');
  note.className = 'cform__error';
  note.setAttribute('role', 'alert');
  note.textContent = MSG[code] || 'Sorry, your enquiry could not be sent. Please email info@vsharksolutions.com or message us on WhatsApp.';
  form.prepend(note);
})();

/* Contact page: check the attachment before upload. The server limit is 5 MB; a larger request would be
   rejected by the host with a bare error page, so stop it here and show the friendly message instead. */
(function () {
  const form = document.getElementById('enquiry');
  const input = form && form.querySelector('input[type="file"][name="attachment"]');
  if (!input) return;
  const MAX = 5 * 1024 * 1024;
  const OK = /\.(pdf|docx?|jpe?g|png|webp|heic|stl|step|stp|igs|iges|obj|ply|zip)$/i;
  function check() {
    const f = input.files && input.files[0];
    let msg = '';
    if (f && f.size > MAX) msg = 'This file is larger than 5 MB. Please attach a smaller file, or send it by WhatsApp or to info@vsharksolutions.com.';
    else if (f && !OK.test(f.name)) msg = 'That file type can’t be attached. Please use PDF, Word, JPG, PNG, WEBP, HEIC, STL, STEP, IGES, OBJ, PLY or ZIP.';
    input.setCustomValidity(msg);
    return !msg;
  }
  input.addEventListener('change', () => { if (!check()) input.reportValidity(); });
  form.addEventListener('submit', (e) => { if (!check()) { e.preventDefault(); input.reportValidity(); } });
})();
