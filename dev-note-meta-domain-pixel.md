# Developer note: Meta domain verification + Pixel + WhatsApp button (2026-10-25)

Site: https://vsharksolutions.com/ · Meta Business portfolio: VShark Engineering Solutions (ID 635871174563901)

## 1. Domain verification (Meta)
Add this meta tag inside `<head>` of the home page (static HTML, not injected by JavaScript):
`<meta name="facebook-domain-verification" content="tf618gctecrhxihrjaa3xk3t6qvyv9" />`
(Alternative if easier: Meta also offers a DNS TXT record; tell us and we will fetch it.)
Reply "done" once live, then we click Verify in Meta (can take up to 72 hours). Needed so Pixel events and WhatsApp/ad conversions count.

## 2. Meta Pixel (base code in `<head>` on every page)
- Pixel / dataset ID: **1420702649657907** ("VShark Website Pixel", created 2026-10-25).
- Install the base code site-wide; fire `PageView` on every page.

## 3. Events to fire
| Event | When | Code |
|---|---|---|
| `Contact` | click on any WhatsApp button/link | `fbq('track','Contact');` |
| `Lead` | contact form submitted successfully (thank-you state, not on click) | `fbq('track','Lead');` |
Send the same two as GA4 events (`generate_lead`, `whatsapp_click`) and mark them as conversions in GA4.

## 4. WhatsApp button
- Number: +91 95142 48525 (WhatsApp Business app, already linked to our Facebook Page).
- Link: `https://wa.me/919514248525?text=Hi%20VShark%2C%20I%20need%203D%20scanning%20%2F%20reverse%20engineering%20for%3A%20`
- Floating button on all pages, plus one in the header and in the contact section. `target="_blank" rel="noopener"`, aria-label "Chat with VShark on WhatsApp".

## 5. UTM on paid links (we set these in ads; please do not strip them)
`utm_source=meta&utm_medium=paid&utm_campaign=svc-india-oct26&utm_content=<ad>`
Keep UTM values in the form hidden fields so leads show their source.

## 6. Test checklist (please confirm each)
- [ ] Meta Pixel Helper (Chrome extension) shows PageView on home, services, contact
- [ ] WhatsApp click shows `Contact` in Pixel Helper
- [ ] Form submit shows `Lead` (test with a real submission, incl. one with a file)
- [ ] GA4 DebugView shows both events
- [ ] Domain shows "Verified" in Meta Business settings > Brand safety > Domains

## Meta-team review of PR #7 (branch `meta`), 2026-10-25 — reviewer: VShark PA (Claude)

Result: **APPROVE with 4 deploy notes.** Code read: `js/consent.js`, `send-enquiry.php`, `index.html`, `thanks.html`, `.htaccess`, `VENDOR-NOTE-tracking.md`, privacy policy section 6. Nothing was run on the live site.

### Matches the brief
- [x] Domain-verification tag `tf618gctecrhxihrjaa3xk3t6qvyv9` is static in `index.html` `<head>`.
- [x] Pixel `1420702649657907` and GA4 `G-6X3872QB6Q` load only after **Accept**; Decline keeps the site working; footer "Cookie settings" reopens the banner; privacy policy §6 "Cookies and analytics" exists.
- [x] WhatsApp link click → Pixel `Contact` + GA4 `whatsapp_click` (one capture-phase listener covers every wa.me link); real enquiry (`thanks.html?sent=1`) → `Lead` + `generate_lead`, once per enquiry (`?sent=1` removed after firing).
- [x] Green round WhatsApp button bottom-right on every page, header button, rail kept, pre-filled message matches the brief (+91 95142 48525).
- [x] UTM / fbclid / gclid kept per visit, copied into hidden form fields and into the enquiry email ("Source:" block).

### Deploy notes (not blockers for merging, needed before ads start)
1. **Host name:** Meta domain was added as `vsharksolutions.com` (root), GA4 stream is `www`. Vendor must 301 one to the other (keep query string). After that, Meta's Verify must see the tag on the final home page; if Verify fails, we will switch to the DNS TXT method.
2. **Public `.md` files:** `DEPLOY.md` is publicly readable today, so `.htaccess` is not in effect. `dev-note-meta-domain-pixel.md` and `VENDOR-NOTE-tracking.md` would be public too (IDs only, no secrets, but internal wording). Block `*.md` or do not upload them.
3. **CSP:** if the vendor adds a Content-Security-Policy, allow the hosts listed in the vendor note, otherwise Pixel/GA4 silently stop.
4. **Form handler:** the vendor's live handler must redirect successes to `/thanks.html?sent=1` and send the Source fields, otherwise `Lead` never fires.

### Optional later (not requested)
- Track `tel:` and `mailto:` clicks as `Contact` too.
- Add `value`/`currency` to `Lead` once we know a lead's worth.

### After deploy, VShark will test (please keep the site up for this)
1. Meta Events Manager → Test Events and Pixel Helper: `PageView`, `Contact`, `Lead` appear only after Accept.
2. GA4 DebugView (`?analytics_debug=1`): `whatsapp_click`, `generate_lead`; then mark both as key events.
3. One real enquiry with a file: email arrives with Source block, lands on `thanks.html?sent=1`.
4. Meta Business settings → Domains → Verify.
