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
