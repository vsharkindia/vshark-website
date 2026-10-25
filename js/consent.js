/* =========================================================
   Cookie consent + analytics (Meta Pixel, Google Analytics 4)
   • Nothing is loaded and no tracking cookies are set until the
     visitor clicks "Accept". Declining keeps the site fully working.
   • The choice is remembered in localStorage; "Cookie settings" links
     (data-cookie-settings) reopen the banner to change it.
   • Events: any WhatsApp link click → Pixel "Contact" + GA4 "whatsapp_click";
     successful enquiry (thanks page reached with ?sent=1) → Pixel "Lead" + GA4 "generate_lead".
   • Ad attribution: utm_* / fbclid / gclid on the landing URL are kept for the visit
     (sessionStorage) and copied into the enquiry form's hidden fields.
   Debug: add ?analytics_debug=1 to any URL to send GA4 events to DebugView.
   ========================================================= */
(function () {
  const PIXEL_ID = '1420702649657907';
  const GA4_ID = 'G-6X3872QB6Q';
  const KEY = 'vshark-consent';          // 'granted' | 'denied'
  const UTM_KEY = 'vshark-utm';
  const UTM_FIELDS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'fbclid', 'gclid'];

  const store = {
    get(k, s = localStorage) { try { return s.getItem(k); } catch (e) { return null; } },
    set(k, v, s = localStorage) { try { s.setItem(k, v); } catch (e) { /* private mode / blocked */ } },
  };
  const qs = new URLSearchParams(location.search);
  const debug = qs.has('analytics_debug') || store.get('vshark-analytics-debug') === '1';
  if (qs.has('analytics_debug')) store.set('vshark-analytics-debug', '1');

  /* ---------- ad attribution (first page of the visit wins) ---------- */
  (function captureUtm() {
    let saved = null;
    try { saved = JSON.parse(store.get(UTM_KEY, sessionStorage) || 'null'); } catch (e) { saved = null; }
    const found = {};
    UTM_FIELDS.forEach((k) => { const v = qs.get(k); if (v) found[k] = v.slice(0, 200); });
    if (!saved || Object.keys(found).length) {
      const data = Object.assign(saved && !Object.keys(found).length ? saved : {}, found);
      if (!data.landing_page) data.landing_page = (location.pathname + location.search).slice(0, 300);
      if (!data.referrer) data.referrer = (document.referrer || '').slice(0, 300);
      store.set(UTM_KEY, JSON.stringify(data), sessionStorage);
    }
  })();

  // every event sent is recorded here (and printed with ?analytics_debug=1) for checking
  const sent = [];
  const log = (pixel, ga, params) => { sent.push({ pixel, ga, params: params || {}, at: new Date().toISOString() }); if (debug) console.info('[VShark analytics]', pixel, '/', ga, params || ''); };

  /* ---------- trackers (loaded only after consent) ---------- */
  let loaded = false;
  function loadTracking() {
    if (loaded) return;
    loaded = true;
    // Meta Pixel base code
    /* eslint-disable */
    !function (f, b, e, v, n, t, s) {
      if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); };
      if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = '2.0'; n.queue = [];
      t = b.createElement(e); t.async = !0; t.src = v; s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s);
    }(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');
    /* eslint-enable */
    window.fbq('init', PIXEL_ID);
    window.fbq('track', 'PageView');
    log('PageView', 'page_view');
    // Google Analytics 4
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', GA4_ID, debug ? { debug_mode: true } : {});
    const g = document.createElement('script');
    g.async = true; g.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA4_ID;
    document.head.appendChild(g);
  }

  function track(pixelEvent, gaEvent, params) {
    if (!loaded) return;                               // no consent → nothing is sent
    window.fbq('track', pixelEvent);
    window.gtag('event', gaEvent, params || {});
    log(pixelEvent, gaEvent, params);
  }

  /* ---------- events ---------- */
  // WhatsApp: one listener catches every WhatsApp link on the page (rail, floating button, cards, CTAs…)
  document.addEventListener('click', (e) => {
    const a = e.target.closest && e.target.closest('a[href*="wa.me/"], a[href*="api.whatsapp.com"], a[href^="whatsapp:"]');
    if (!a) return;
    const where = a.dataset.waLocation || (a.closest('.wa-float') && 'floating_button') || (a.closest('.rail') && 'contact_rail')
      || (a.closest('.mbar') && 'mobile_bar') || (a.closest('.header, .menu') && 'header') || (a.closest('.footer') && 'footer') || 'page';
    track('Contact', 'whatsapp_click', { link_url: a.href.split('?')[0], link_location: where, page_path: location.pathname });
  }, true);

  // Lead: only after a successful submission. The form handler redirects successes to thanks.html?sent=1
  // (on the Netlify preview the form posts to /send-enquiry.php, which Netlify answers with the thanks page).
  const leadPage = /\/thanks(\.html)?$/.test(location.pathname) && qs.get('sent') === '1'
    || /\/send-enquiry\.php$/.test(location.pathname);
  let leadPending = leadPage;
  function fireLead() {
    if (!leadPending || !loaded) return;
    leadPending = false;
    let src = {};
    try { src = JSON.parse(store.get(UTM_KEY, sessionStorage) || '{}'); } catch (e) { src = {}; }
    track('Lead', 'generate_lead', { form_name: 'enquiry', utm_source: src.utm_source || '', utm_campaign: src.utm_campaign || '' });
    // drop ?sent=1 so a reload or back-navigation doesn't count the same enquiry twice
    if (qs.get('sent') === '1') history.replaceState(null, '', location.pathname + location.hash);
  }

  /* ---------- enquiry form: fill hidden attribution fields ---------- */
  function fillForm() {
    const form = document.getElementById('enquiry');
    if (!form) return;
    let src = {};
    try { src = JSON.parse(store.get(UTM_KEY, sessionStorage) || '{}'); } catch (e) { src = {}; }
    form.querySelectorAll('input[data-attr]').forEach((i) => { i.value = src[i.name] || ''; });
  }

  /* ---------- banner ---------- */
  function decide(choice) {
    store.set(KEY, choice);
    if (choice === 'granted') { loadTracking(); fireLead(); }
    else if (loaded) {
      // withdrawn after accepting: reload so no tracker stays active on this page
      location.reload();
      return;
    }
    hideBanner();
  }
  let banner = null;
  function showBanner() {
    if (!banner) {
      banner = document.createElement('div');
      banner.className = 'cookie';
      banner.setAttribute('role', 'dialog');
      banner.setAttribute('aria-live', 'polite');
      banner.setAttribute('aria-label', 'Cookie preferences');
      const root = document.querySelector('link[rel="icon"]')?.getAttribute('href').replace(/favicon\.ico$/, '') || '';
      banner.innerHTML = `
        <p class="cookie__text"><b>Cookies</b> We'd like to use analytics and advertising cookies (Google Analytics, Meta Pixel)
          to understand how the site is used and measure our ads. They load only if you accept.
          <a href="${root}privacy-policy.html#cookies-and-analytics">Privacy Policy</a></p>
        <div class="cookie__actions">
          <button type="button" class="cookie__btn cookie__btn--ghost" data-choice="denied">Decline</button>
          <button type="button" class="cookie__btn" data-choice="granted">Accept</button>
        </div>`;
      banner.addEventListener('click', (e) => {
        const b = e.target.closest('[data-choice]');
        if (b) decide(b.dataset.choice);
      });
      document.body.appendChild(banner);
    }
    requestAnimationFrame(() => banner.classList.add('is-on'));
  }
  function hideBanner() { banner?.classList.remove('is-on'); }

  function init() {
    fillForm();
    const choice = store.get(KEY);
    if (choice === 'granted') { loadTracking(); fireLead(); }
    else if (choice !== 'denied') showBanner();
    document.addEventListener('click', (e) => {
      if (e.target.closest('[data-cookie-settings]')) { e.preventDefault(); e.stopPropagation(); showBanner(); }
    }, true); // capture phase: main.js handles link clicks before they bubble
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();

  window.VSharkAnalytics = { showBanner, consent: () => store.get(KEY), sent };
})();
