# Vendor note: Meta Pixel, GA4, WhatsApp and consent (October 2026)

Branch `main` now contains Meta domain verification, Meta Pixel and Google Analytics 4 (both behind a cookie
banner), a floating WhatsApp button and ad-source tracking. Please deploy `main` as usual, plus the two
form-handler points below.

## Please do

1. **Deploy `main`**, including the new file `js/consent.js` and the updated `index.html`, all pages, `css/style.css` and `send-enquiry.php`.
2. **Form handler: redirect real successes to `thanks.html?sent=1`.**
   The thank-you page fires the Lead / `generate_lead` conversion **only** when the address ends in `?sent=1`.
   - If you use our `send-enquiry.php`, this is already done. Spam-trap submissions still go to plain `thanks.html` and are not counted.
   - If you use your own handler: after a successful send, redirect to `/thanks.html?sent=1`. Validation errors and spam must not get `?sent=1`.
3. **Form handler: include the ad-source fields in the enquiry email.**
   The form now posts these hidden fields (empty when the visitor didn't come from an ad):
   `utm_source, utm_medium, utm_campaign, utm_content, utm_term, fbclid, gclid, landing_page, referrer`.
   Our `send-enquiry.php` adds them to the email under "Source:". If you use your own handler, please do the same.
4. **Do not strip query strings** (`?utm_…`, `?fbclid=…`, `?gclid=…`) in redirects or caching rules. They currently survive.
5. **Pick one host name.** Both `vsharksolutions.com` and `www.vsharksolutions.com` currently load the site without
   redirecting. Please 301-redirect one to the other (the GA4 stream uses **www**), keeping the query string.
6. **Apply `.htaccess` (or equivalent rules).** Right now `https://www.vsharksolutions.com/DEPLOY.md` opens publicly, so the
   repository's `.htaccess` is not in effect. It blocks internal files (`*.md` notes, `build/`, `data/`, `netlify.toml`,
   `enquiry-config.php`) and adds the www/HTTPS redirect and security headers. If you can't use it, please block those paths another way,
   or don't upload them (see the exclude list in `DEPLOY.md`).
7. **Content-Security-Policy:** if you add or tighten a CSP, allow `connect.facebook.net`, `www.facebook.com`,
   `www.googletagmanager.com`, `*.google-analytics.com`, `*.analytics.google.com` and `stats.g.doubleclick.net`.

## What is installed (for reference)

| Item | Where |
|---|---|
| Meta domain verification `<meta name="facebook-domain-verification" …>` | static `<head>` of `index.html` |
| Meta Pixel `1420702649657907`, GA4 `G-6X3872QB6Q` | `js/consent.js`; loaded only after the visitor clicks **Accept** |
| Events | WhatsApp link click → Pixel `Contact` + GA4 `whatsapp_click` · successful enquiry (`thanks.html?sent=1`) → Pixel `Lead` + GA4 `generate_lead` |
| WhatsApp | floating green button (every page, bottom right), header button, contact rail, contact page. Pre-filled message from the Meta brief. |
| Consent | banner on first visit; Decline keeps the site fully working; "Cookie settings" in the footer reopens it |

## After deploying, please confirm

- [ ] `view-source:https://www.vsharksolutions.com/` shows the `facebook-domain-verification` meta tag. Then tell VShark "done" so Meta can verify.
- [ ] One real test enquiry (with a file) arrives by email, shows a "Source:" block when sent from a link with `?utm_source=test`, and lands on `thanks.html?sent=1`.

Testing tip: add `?analytics_debug=1` to any URL to send GA4 events to DebugView.
