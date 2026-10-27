# vsharksolutions.com: developer requests (2026-10-27)

Priority order. Please reply with the live URL or "done" per item.

## 1. Meta domain verification (needed for ads)
Already in PR #7 (`index.html`). Merge and deploy PR #7, then tell us so we can click Verify.
Add inside `<head>` of the HOME page, as static HTML (not injected by JavaScript), then publish:
```html
<meta name="facebook-domain-verification" content="tf618gctecrhxihrjaa3xk3t6qvyv9" />
```
Check: view-source of https://vsharksolutions.com/ must show the line.

## 2. Social profile links (Organization schema `sameAs` + footer + /links page)
- YouTube: https://www.youtube.com/@VsharkSolutions
- Instagram: https://www.instagram.com/vshark.solutions/
- Facebook: https://www.facebook.com/vshark.solutions
- IndiaMART: https://www.indiamart.com/vsharkengineeringsolutions/
- LinkedIn: company page not created yet (we will send the URL)
Create a `/links` page (bio-link): website, WhatsApp chat (+91 95142 48525), quote form, YouTube, Instagram, Facebook, IndiaMART. Mark outbound links with `rel="noopener"`.

## 3. Meta Pixel + conversion events (before ads start)
Install the Meta Pixel (ID from Meta Events Manager, we will send it). Events: PageView, Lead (contact form submit), Contact (WhatsApp / phone click), ViewContent (service and product pages). Make sure GA4 key events fire for the same actions. We will test with Meta Pixel Helper.

## 4. AI-search and rich-result basics
- `/llms.txt` at the site root (short description of VShark: services, locations Coimbatore/Tamil Nadu India and Dubai/UAE, product lines, key pages, contact).
- Organization / LocalBusiness JSON-LD on the home page: legal name "VShark Solutions Private Limited", telephone, email info@vsharksolutions.com, areaServed India and United Arab Emirates, `sameAs` from item 2.
- `VideoObject` JSON-LD wherever a YouTube video is embedded. Current videos: MR2sP_ABjds (Vertex3D 3 scan modes demo), bdFCre7VjZY (Vertex3D Series blue laser), uGaiIA9qhYQ (car underbody scan), kvoMhdcHr5c (industrial 3D scanning), iebucFAzS-Y (metrology scanning), DSPXyzju0_0 (on-site crusher liner plate scan). Use the title and description from the YouTube video page.
- `FAQPage` schema on service pages that already show FAQs.

## 5. Technical SEO
- Open Graph + Twitter preview images (1200x630) for every page; canonical URLs; `hreflang` (en-IN, en-AE if separate pages exist).
- Add `width`/`height` to all images (prevents layout shift); keep descriptive file names and alt text.
- XML sitemap + robots.txt submitted in Google Search Console (we will send the verification method).

## 6. Blog
Build the blog section and publish the 10 prepared posts (handoff Part G). Each post: one H1, answer-first intro, author, date, related links, `BlogPosting` schema.

## 7. Contact form test (with us)
Test 3 enquiries on the live host (one with a file attached), confirm the email arrives at info@vsharksolutions.com and the Lead event fires.
