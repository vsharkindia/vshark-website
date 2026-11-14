# Self-hosting vsharksolutions.com (Netlify + our own contact form)

Goal: every merge to `main` goes live automatically, and the contact form is ours. No vendor step per update.

| Part | Where | Owner |
|---|---|---|
| Domain / DNS | GoDaddy | VShark |
| Email | Microsoft 365 (MX, SPF unchanged by this plan) | VShark |
| Website | Netlify, built from GitHub `main` | VShark |
| Contact form | `netlify/functions/enquiry.mjs`, sends through Microsoft 365 (Graph) | VShark |

Nothing here touches email: only the website records (`@` A record and `www` CNAME) change at the very end.

---

## Step 1 — Microsoft 365: let the website send mail (VShark admin, ~10 minutes)

1. https://entra.microsoft.com → **Applications → App registrations → New registration**
   - Name: `VShark website contact form`, account type: *this organisation only*, no redirect URI → **Register**.
   - Copy **Application (client) ID** and **Directory (tenant) ID**.
2. **Certificates & secrets → New client secret** (24 months). Copy the **Value** immediately (shown once).
   Put a calendar reminder to renew it before it expires.
3. **API permissions → Add a permission → Microsoft Graph → Application permissions → `Mail.Send`** → Add →
   **Grant admin consent**.
4. Recommended — restrict the app to one mailbox (otherwise `Mail.Send` could send as any mailbox).
   In Exchange Online PowerShell:
   ```powershell
   New-DistributionGroup -Name "Website senders" -Type Security -Members info@vsharksolutions.com
   New-ApplicationAccessPolicy -AppId <client-id> -PolicyScopeGroupId "Website senders" -AccessRight RestrictAccess -Description "Contact form may only send as info@"
   Test-ApplicationAccessPolicy -AppId <client-id> -Identity info@vsharksolutions.com   # -> Granted
   ```

## Step 2 — Netlify: settings (VShark, Netlify UI)

**Site configuration → Environment variables** (scope: Functions). Never put these in the repository (it is public).

| Key | Value |
|---|---|
| `MS_TENANT_ID` | Directory (tenant) ID |
| `MS_CLIENT_ID` | Application (client) ID |
| `MS_CLIENT_SECRET` | the secret Value — mark as *secret* |
| `ENQUIRY_FROM` | `info@vsharksolutions.com` (the mailbox that sends) |
| `ENQUIRY_TO` | where enquiries go (comma-separated allowed; defaults to `ENQUIRY_FROM`) |
| `ALLOW_INDEXING` | `1` **only** on the site that serves www.vsharksolutions.com (scope: Builds). Without it every page is `noindex`. |

Without the `MS_*` values, preview copies run the form in **test mode** (checks the fields, shows the thank-you page, sends nothing);
the production site shows "could not be sent" instead of pretending.

## Step 3 — test on Netlify before switching (staging)

- Preview/staging URL: open the pull request, Netlify posts a deploy preview link.
- Form: send an enquiry with and without an attachment (limit **5 MB**; PDF, Word, JPG, PNG, WEBP, HEIC, STL, STEP, IGES, OBJ, PLY, ZIP).
  With the `MS_*` settings in place, the email must arrive at `ENQUIRY_TO` with the "Source:" block when the page was opened with `?utm_source=test`.
- Meta team: GA4 DebugView (`?analytics_debug=1`) and the Lead flow. Pixel events from a non-verified domain may be filtered — final Pixel check after the switch.
- Speed: PageSpeed Insights on the staging URL vs the live site.

## Step 4 — switch the domain (VShark, GoDaddy + Netlify, ~15 minutes, no email impact)

1. Netlify → **Domain management → Add domain** `www.vsharksolutions.com` (primary) and `vsharksolutions.com` (redirects to www automatically).
2. GoDaddy → DNS for vsharksolutions.com — change **only** these:
   - `www` → **CNAME** → `<site-name>.netlify.app`
   - `@` → **A** → `75.2.60.5` (Netlify load balancer; confirm the value shown in Netlify's domain panel)
   - Leave **MX, TXT (SPF, google-site-verification), autodiscover and any other records untouched**.
3. Netlify issues the HTTPS certificate automatically (minutes to an hour). Set `ALLOW_INDEXING=1`, redeploy.
4. Check: `http://`, `https://`, with and without `www` all end on `https://www.vsharksolutions.com/` (301); short URLs (`/contact`) work;
   `/DEPLOY.md` and `/build/build.py` return 404; one real enquiry arrives.
5. Rollback if needed: set the two records back to `147.93.99.170` (Hostinger). TTL 600 s makes this quick — lower the TTL a day before.

After the switch the Hostinger plan can be cancelled (export anything the vendor stored there first).

## Speed test (14 Nov 2026, from India, mobile, cold cache, median of 3)

| Page | Hostinger (live) loaded | Netlify loaded | Server response Hostinger / Netlify |
|---|---|---|---|
| Home | 1.1 s | 2.0 s | 70 / 450 ms |
| 3D scanning service | 0.8 s | 1.6 s | 70 / 300 ms |
| Contact | 0.8 s | 2.0 s | 190 / 470 ms |
| Blog | 1.4 s | 1.7 s | 250 / 560 ms |

Netlify's free network serves India from Singapore, so it is roughly 1.5–2x slower here than Hostinger (India).
Hence the recommended setup below: **keep Hostinger for hosting, take over deployment and the form.**

## Recommended — keep Hostinger (fast in India), remove the vendor from updates and the form

Ask the vendor for **SFTP (or FTP) access to the web folder** only. Store it as GitHub secrets
`DEPLOY_HOST`, `DEPLOY_PORT`, `DEPLOY_USER`, `DEPLOY_PASSWORD`, `DEPLOY_PATH`, set the repository variable `AUTO_DEPLOY=true`:
`.github/workflows/deploy.yml` then uploads every merge to `main`, skipping internal files.
The form runs on Netlify (this repository's function) while the pages stay on Hostinger:
- Netlify site env: the `MS_*` / `ENQUIRY_*` settings plus `SITE_URL=https://www.vsharksolutions.com` (redirects go back to Hostinger).
- Optional: a `forms.vsharksolutions.com` CNAME to the Netlify site, so the form posts to our own domain.
- The contact page's form `action` then points to `https://forms.vsharksolutions.com/send-enquiry.php` (one setting in the build).
