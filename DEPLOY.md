# Hosting guide — vsharksolutions.com

For the hosting provider. This repository *is* the website: a static site (HTML, CSS, JavaScript,
images) plus one small PHP script for the contact form. **There is no build step on the server** —
the HTML is generated and committed by the VShark team, so the server only needs the files.

| | |
|---|---|
| Repository | https://github.com/kalimuthu4978/vshark-website (private — ask VShark for read access) |
| Branch to deploy | `main` (the new site is under review in pull request #5 and goes to `main` when approved) |
| Preview of the new site | https://deploy-preview-5--vshark-preview.netlify.app/ |
| Web root | the repository root (`index.html` at the top level) |
| Size | about 60 MB |

## 1. Server requirements

- Apache or LiteSpeed with `.htaccess` enabled (`AllowOverride All`): `mod_rewrite`, `mod_headers`,
  `mod_deflate`, `mod_mime`. *(On Nginx, translate `.htaccess` into the server block — see section 5.)*
- PHP 7.4 or newer (8.x preferred) with `openssl`; `mbstring` recommended.
- PHP upload limits of at least 10 MB / 12 MB — set in `.user.ini` (PHP-FPM/CGI); on mod_php set
  `upload_max_filesize` and `post_max_size` in the panel instead.
- Free SSL (Let's Encrypt) for **vsharksolutions.com and www.vsharksolutions.com**, auto-renewing.
- DNS stays as it is (the domain already points to this server). **Do not change the MX or SPF records
  — company email runs on Microsoft 365.**

## 2. Files

Upload the whole repository **except**: `.git/`, `.github/`, `build/`, `data/`, `collateral/`, `*.md`,
`netlify.toml`, `.gitignore`. (These are also blocked by `.htaccess` if they do get uploaded.)

Server-only file, created by hand and never committed: **`enquiry-config.php`** (section 4).

## 3. Deploying updates automatically — choose one

**Option A — Git deployment from your control panel** (cPanel "Git Version Control", Plesk Git,
Hostinger Git, …): clone `main` into the web root using a read-only deploy key, and pull automatically on
each push (GitHub webhook, or a cron job running `git pull` every few minutes).

**Option B — GitHub Actions uploads the files** (no Git needed on the server). The workflow
`.github/workflows/deploy.yml` mirrors the site over SFTP (or FTP) and never deletes server files.
VShark adds these in GitHub → Settings → Secrets and variables → Actions:

| Name | Type | Value |
|---|---|---|
| `DEPLOY_HOST` | secret | server host name |
| `DEPLOY_PORT` | secret | e.g. `22` for SFTP, `21` for FTP (optional) |
| `DEPLOY_USER` | secret | SFTP/FTP user |
| `DEPLOY_PASSWORD` | secret | its password |
| `DEPLOY_PATH` | secret | web root, e.g. `/home/USER/public_html` |
| `DEPLOY_PROTOCOL` | variable | `sftp` (default) or `ftp` |
| `AUTO_DEPLOY` | variable | `true` to deploy on every push to `main` (leave unset for the first, manual deploy) |

## 4. Contact form

The form on `contact.html` posts to **`send-enquiry.php`**, which emails the enquiry (with an optional
attachment up to 8 MB: PDF, JPG, PNG, STL, STEP, ZIP) to info@vsharksolutions.com and redirects to
`thanks.html`. Problems send the visitor back to the form with a message.

1. Copy `enquiry-config.sample.php` to `enquiry-config.php` **on the server** and fill it in.
2. Recommended: send through Microsoft 365 SMTP (`smtp.office365.com:587`, STARTTLS) with a company
   mailbox. **SMTP AUTH must be enabled for that mailbox** in the Microsoft 365 admin centre
   (Users → the mailbox → Mail → Manage email apps → Authenticated SMTP).
3. Alternatively set `'host' => ''` to use PHP `mail()` — then add this server to the SPF record,
   otherwise enquiries are likely to land in junk.
4. Errors are written to the PHP error log (prefix `send-enquiry:`).

## 5. What `.htaccess` does

- Redirects to **https://www.vsharksolutions.com** (HTTPS + www).
- 301-redirects the old site's pages: `index.php`, `about.php`, `contact.php`, `portfolio.php`,
  `3d-scanning.php`, `3d-printing.php`, `product-development.php`.
- Clean URLs: `/about` serves `about.html`, `/services/3d-scanning` serves `services/3d-scanning.html`.
- Custom 404 page (`404.html`), security headers, compression and browser caching
  (CSS/JS are versioned with `?v=…`, so they are cached for a year).
- Blocks the source folders and `enquiry-config.php`.

If the site is served from a sub-folder, a staging domain or Nginx, the HTTPS/www rule and the
`%{DOCUMENT_ROOT}` clean-URL rule need adjusting.

## 6. Go-live checklist

1. **Back up the current website** (files and any database) before the first deploy.
2. Deploy `main` (Option A or B).
3. Create `enquiry-config.php`; send three test enquiries, one with a file, and confirm they arrive.
4. Check: http → https, vsharksolutions.com → www, an old URL such as `/about.php` → `/about`,
   a missing page shows the custom 404, `/sitemap.xml` and `/robots.txt` load.
5. VShark submits `https://www.vsharksolutions.com/sitemap.xml` in Google Search Console.

Questions or change requests: please raise a GitHub issue on the repository, or contact
info@vsharksolutions.com.
