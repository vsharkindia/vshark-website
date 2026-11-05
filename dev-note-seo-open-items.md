Hi,

Thanks for the SEO fixes on `seo/coimbatore-page` (canonicals, og/twitter tags, llms.txt, the Coimbatore page). I checked the branch and those look good. Before this goes to the hosting team, a few items are still open. Please do these on the same branch, then merge to `main`.

**Please fix (in the repo)**

1. **Empty alt text.** Many images still have `alt=""`. Give each a short descriptive alt. Where the file name is descriptive, copy it.
   - `services/*.html`: about 7 service-card images per page. Example: `handheld-3d-laser-scanning-of-an-engine-cylinder-head-16x10.webp` becomes alt "Handheld 3D laser scanning of an engine cylinder head".
   - `industries/*.html`: about 6 per page. If some are purely decorative, leave those empty and tell me which.
   - Product images on `/products/`: "JINUOSH Vertex 3D scanner" plus the model name.
2. **Image width and height.** Add the real width and height attributes to every `<img>` (portfolio has 95, home 25, services up to 29). Keep `loading="lazy"` below the fold, but not on the hero image.
3. **Schema (JSON-LD).**
   - Add `Service` and `BreadcrumbList` to the 7 service pages (provider `/#business`, areaServed IN and AE).
   - Add `FAQPage` to the 6 service pages that lack it, using the FAQ text already on each page.
   - Add an `Organization` node on the home page with logo and sameAs (Facebook, Instagram; LinkedIn company URL to follow).
4. **Titles.** Check that the titles on `/portfolio/`, `/contact` and `/about` show the dash correctly (UTF-8 or `&ndash;`).
5. **Sitemap.** Add the Coimbatore page and any new pages, with a real `lastmod`.

**Later (I will send details)**
- Product schema for the Vertex models (waiting on our spec approval).
- `/blog/` with three launch posts.

**For the hosting team (please pass on)**
- `.htaccess` must be active on the live server. The apex `vsharksolutions.com` should 301 to `https://www.vsharksolutions.com` (it currently returns 200).
- Set `404.html` as the server's 404 page, keeping the HTTP 404 status.
- After the deploy, make sure `/llms.txt` and `/sitemap.xml` open on the live site.

Please tell me when it is merged so I can check the live pages.

Thanks.
