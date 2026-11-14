/*
 * VShark Solutions — contact form handler (Netlify Function).
 * Replaces send-enquiry.php: the form still posts to /send-enquiry.php, which this function answers,
 * so the HTML is the same on every host. Emails go out through VShark's own Microsoft 365 mailbox
 * (Microsoft Graph, app-only), with the optional attachment.
 *
 * Settings — Netlify → Site configuration → Environment variables (never in the repository):
 *   MS_TENANT_ID, MS_CLIENT_ID, MS_CLIENT_SECRET   Entra ID app registration with Mail.Send (application)
 *   ENQUIRY_FROM   mailbox that sends, e.g. info@vsharksolutions.com
 *   ENQUIRY_TO     where enquiries go (comma-separated allowed); defaults to ENQUIRY_FROM
 *   SITE_URL       optional, e.g. https://www.vsharksolutions.com — when the website itself is hosted elsewhere
 *                  (Hostinger) and only this form runs on Netlify, redirects go back to that site.
 *   ENQUIRY_MODE   "dry-run" = validate and redirect but do not send (testing only).
 *                  Deploy previews / branch deploys without the MS_* settings run in dry-run automatically.
 *
 * Responses mirror send-enquiry.php: 303 to /thanks.html?sent=1 on success (fires the Lead conversion),
 * 303 to /contact.html?error=<code>#enquiry on problems, plain /thanks.html for the spam trap.
 */

export const MAX_BYTES = 5 * 1024 * 1024;   // Netlify function requests are capped at ~6 MB in total
export const ALLOWED_EXT = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'webp', 'heic', 'stl', 'step', 'stp', 'igs', 'iges', 'obj', 'ply', 'zip'];
const ATTR = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'fbclid', 'gclid', 'landing_page', 'referrer'];
const GRAPH = 'https://graph.microsoft.com/v1.0';
const INLINE_LIMIT = 3 * 1024 * 1024;       // Graph sendMail: larger attachments need an upload session

export const config = { path: '/send-enquiry.php' };

const env = (k) => (typeof Netlify !== 'undefined' ? Netlify.env.get(k) : process.env[k]) || '';
const redirect = (loc) => new Response(null, { status: 303, headers: { Location: (env('SITE_URL') || '').replace(/\/$/, '') + loc, 'Cache-Control': 'no-store' } });
const back = (code) => redirect(`/contact.html?error=${encodeURIComponent(code)}#enquiry`);

function field(fd, k, max = 200) {
  const v = fd.get(k);
  return (typeof v === 'string' ? v : '').replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '').trim().slice(0, max);
}
const oneLine = (v) => v.replace(/[\r\n]+/g, ' ').trim();
const isEmail = (v) => /^[^\s@<>()",;:]+@[^\s@<>()",;:]+\.[A-Za-z]{2,}$/.test(v);

export async function parseEnquiry(fd) {
  if (field(fd, 'company_url') !== '') return { spam: true };
  const e = {
    name: oneLine(field(fd, 'name', 120)), company: oneLine(field(fd, 'company', 160)),
    email: oneLine(field(fd, 'email', 200)), phone: oneLine(field(fd, 'phone', 60)),
    interest: oneLine(field(fd, 'interest', 160)), message: field(fd, 'message', 8000),
    consent: field(fd, 'consent', 10), source: [],
  };
  if (!e.name || !e.interest || !e.message || !isEmail(e.email)) return { error: 'missing' };
  if (e.consent !== 'yes') return { error: 'consent' };
  const f = fd.get('attachment');
  if (f && typeof f === 'object' && f.size > 0) {
    if (f.size > MAX_BYTES) return { error: 'size' };
    const orig = String(f.name || 'attachment').split(/[\\/]/).pop();
    const ext = (orig.match(/\.([A-Za-z0-9]+)$/) || [, ''])[1].toLowerCase();
    if (!ALLOWED_EXT.includes(ext)) return { error: 'type' };
    e.attachment = { name: orig.replace(/[^A-Za-z0-9._-]+/g, '_') || `attachment.${ext}`, type: f.type || 'application/octet-stream', bytes: new Uint8Array(await f.arrayBuffer()) };
  }
  for (const k of ATTR) { const v = oneLine(field(fd, k, 300)); if (v) e.source.push(`${(k + ':').padEnd(14)}${v}`); }
  return { enquiry: e };
}

export function emailText(e, ip = '?') {
  const lines = [
    'New enquiry from vsharksolutions.com', '',
    `Name:        ${e.name}`, `Company:     ${e.company || '-'}`, `Email:       ${e.email}`, `Phone:       ${e.phone || '-'}`,
    `Interested:  ${e.interest}`,
    `Attachment:  ${e.attachment ? `${e.attachment.name} (${(e.attachment.bytes.length / 1048576).toFixed(2)} MB)` : 'none'}`,
    'Consent:     yes (privacy policy accepted)',
    `Sent:        ${new Date().toISOString().slice(0, 16).replace('T', ' ')} UTC from ${ip}`, '',
    'Message:', e.message,
  ];
  if (e.source.length) lines.push('', 'Source:', ...e.source);
  return lines.join('\r\n');
}

const b64 = (bytes) => Buffer.from(bytes).toString('base64');

async function graphToken() {
  const r = await fetch(`https://login.microsoftonline.com/${env('MS_TENANT_ID')}/oauth2/v2.0/token`, {
    method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ client_id: env('MS_CLIENT_ID'), client_secret: env('MS_CLIENT_SECRET'), scope: 'https://graph.microsoft.com/.default', grant_type: 'client_credentials' }),
  });
  if (!r.ok) throw new Error(`token ${r.status}: ${(await r.text()).slice(0, 300)}`);
  return (await r.json()).access_token;
}

async function graph(token, method, path, body) {
  const r = await fetch(GRAPH + path, { method, headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }, body: body && JSON.stringify(body) });
  if (!r.ok) throw new Error(`${method} ${path} ${r.status}: ${(await r.text()).slice(0, 300)}`);
  return r.status === 202 || r.status === 204 ? null : r.json();
}

export async function sendViaGraph(e, text) {
  const from = env('ENQUIRY_FROM');
  const to = (env('ENQUIRY_TO') || from).split(',').map((s) => s.trim()).filter(Boolean);
  const box = `/users/${encodeURIComponent(from)}`;
  const message = {
    subject: `Website enquiry: ${e.interest} — ${e.name}`,
    body: { contentType: 'Text', content: text },
    toRecipients: to.map((address) => ({ emailAddress: { address } })),
    replyTo: [{ emailAddress: { address: e.email, name: e.name } }],
  };
  const token = await graphToken();
  const a = e.attachment;
  if (!a || a.bytes.length <= INLINE_LIMIT) {
    if (a) message.attachments = [{ '@odata.type': '#microsoft.graph.fileAttachment', name: a.name, contentType: a.type, contentBytes: b64(a.bytes) }];
    await graph(token, 'POST', `${box}/sendMail`, { message, saveToSentItems: true });
    return;
  }
  // large attachment: draft -> upload session (chunks) -> send
  const draft = await graph(token, 'POST', `${box}/messages`, message);
  const session = await graph(token, 'POST', `${box}/messages/${draft.id}/attachments/createUploadSession`,
    { AttachmentItem: { attachmentType: 'file', name: a.name, size: a.bytes.length, contentType: a.type } });
  const CHUNK = 320 * 1024 * 10;   // multiple of 320 KiB, under the 4 MB per-request limit
  for (let start = 0; start < a.bytes.length; start += CHUNK) {
    const part = a.bytes.subarray(start, Math.min(start + CHUNK, a.bytes.length));
    const r = await fetch(session.uploadUrl, { method: 'PUT', headers: { 'Content-Length': String(part.length), 'Content-Range': `bytes ${start}-${start + part.length - 1}/${a.bytes.length}` }, body: part });
    if (!r.ok) throw new Error(`upload chunk ${r.status}: ${(await r.text()).slice(0, 200)}`);
  }
  await graph(token, 'POST', `${box}/messages/${draft.id}/send`);
}

export default async (req, context) => {
  if (req.method !== 'POST') return redirect('/contact.html');
  const len = Number(req.headers.get('content-length') || 0);
  if (len > MAX_BYTES + 512 * 1024) return back('size');
  let fd;
  try { fd = await req.formData(); } catch { return back('upload'); }
  const r = await parseEnquiry(fd);
  if (r.spam) return redirect('/thanks.html');
  if (r.error) return back(r.error);
  const text = emailText(r.enquiry, context?.ip || req.headers.get('x-nf-client-connection-ip') || '?');
  // Preview copies without Microsoft 365 settings test the flow without sending; production never fakes a send.
  const deployContext = context?.deploy?.context || env('CONTEXT');
  const isPreview = deployContext === 'deploy-preview' || deployContext === 'branch-deploy';
  const configured = env('MS_TENANT_ID') && env('MS_CLIENT_ID') && env('MS_CLIENT_SECRET') && env('ENQUIRY_FROM');
  if (env('ENQUIRY_MODE') === 'dry-run' || (isPreview && !configured)) {
    console.log('[enquiry dry-run]', JSON.stringify({ to: env('ENQUIRY_TO') || env('ENQUIRY_FROM'), subject: `${r.enquiry.interest} — ${r.enquiry.name}`, attachment: r.enquiry.attachment?.name || null, bytes: r.enquiry.attachment?.bytes.length || 0 }));
    return redirect('/thanks.html?sent=1');
  }
  if (!env('MS_TENANT_ID') || !env('MS_CLIENT_ID') || !env('MS_CLIENT_SECRET') || !env('ENQUIRY_FROM')) {
    console.error('enquiry: Microsoft 365 settings are missing (MS_TENANT_ID, MS_CLIENT_ID, MS_CLIENT_SECRET, ENQUIRY_FROM)');
    return back('config');
  }
  try {
    await sendViaGraph(r.enquiry, text);
  } catch (err) {
    console.error('enquiry: send failed:', err.message);
    return back('send');
  }
  return redirect('/thanks.html?sent=1');
};
