<?php
/*
 * VShark Solutions — contact form handler for the production server.
 * Receives the enquiry form from contact.html, emails it (with the optional attachment) and
 * redirects to thanks.html. No external libraries: uses SMTP (recommended) or PHP mail().
 *
 * Settings live in enquiry-config.php on the server (copy enquiry-config.sample.php; never commit it).
 * On the Netlify preview this file is not executed — Netlify Forms handles the form there.
 */

declare(strict_types=1);

const MAX_BYTES = 8 * 1024 * 1024;                       // matches the "max 8 MB" on the form
const ALLOWED_EXT = ['pdf', 'jpg', 'jpeg', 'png', 'stl', 'step', 'stp', 'zip'];

function back(string $code): void {
    header('Location: /contact.html?error=' . rawurlencode($code) . '#enquiry', true, 303);
    exit;
}
function field(string $k, int $max = 200): string {
    $v = trim((string)($_POST[$k] ?? ''));
    $v = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/u', '', $v) ?? '';
    return function_exists('mb_substr') ? mb_substr($v, 0, $max) : substr($v, 0, $max);
}
function one_line(string $v): string {                    // header-injection guard
    return trim(preg_replace('/[\r\n]+/', ' ', $v) ?? '');
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Location: /contact.html', true, 303);
    exit;
}

$cfgFile = __DIR__ . '/enquiry-config.php';
if (!is_file($cfgFile)) {
    error_log('send-enquiry: enquiry-config.php is missing');
    back('config');
}
$cfg = require $cfgFile;

// Spam trap: real visitors never see this field. Pretend success so bots learn nothing.
if (field('company_url') !== '') {
    header('Location: /thanks.html', true, 303);
    exit;
}

$name     = one_line(field('name', 120));
$company  = one_line(field('company', 160));
$email    = one_line(field('email', 200));
$phone    = one_line(field('phone', 60));
$interest = one_line(field('interest', 160));
$message  = field('message', 8000);
$consent  = field('consent', 10);

if ($name === '' || $interest === '' || $message === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) back('missing');
if ($consent !== 'yes') back('consent');

// Optional attachment
$attach = null;
if (!empty($_FILES['attachment']) && ($_FILES['attachment']['error'] ?? UPLOAD_ERR_NO_FILE) !== UPLOAD_ERR_NO_FILE) {
    $f = $_FILES['attachment'];
    if ($f['error'] === UPLOAD_ERR_INI_SIZE || $f['error'] === UPLOAD_ERR_FORM_SIZE || $f['size'] > MAX_BYTES) back('size');
    if ($f['error'] !== UPLOAD_ERR_OK || !is_uploaded_file($f['tmp_name'])) back('upload');
    $orig = basename((string)$f['name']);
    $ext = strtolower(pathinfo($orig, PATHINFO_EXTENSION));
    if (!in_array($ext, ALLOWED_EXT, true)) back('type');
    $safeName = preg_replace('/[^A-Za-z0-9._-]+/', '_', $orig) ?: ('attachment.' . $ext);
    $attach = ['name' => $safeName, 'data' => (string)file_get_contents($f['tmp_name'])];
}

// ---------------------------------------------------------------- build the email
$to      = (string)$cfg['to'];
$from    = (string)$cfg['from'];
$subject = 'Website enquiry: ' . $interest . ' — ' . $name;
$lines = [
    'New enquiry from vsharksolutions.com',
    '',
    'Name:        ' . $name,
    'Company:     ' . ($company ?: '-'),
    'Email:       ' . $email,
    'Phone:       ' . ($phone ?: '-'),
    'Interested:  ' . $interest,
    'Attachment:  ' . ($attach ? $attach['name'] . ' (' . number_format(strlen($attach['data']) / 1048576, 2) . ' MB)' : 'none'),
    'Consent:     yes (privacy policy accepted)',
    'Sent:        ' . gmdate('Y-m-d H:i') . ' UTC from ' . ($_SERVER['REMOTE_ADDR'] ?? '?'),
    '',
    'Message:',
    $message,
];
// Ad attribution (hidden fields filled from the visitor's landing URL)
$attr = [];
foreach (['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'fbclid', 'gclid', 'landing_page', 'referrer'] as $k) {
    $v = one_line(field($k, 300));
    if ($v !== '') $attr[] = str_pad($k . ':', 14) . $v;
}
if ($attr) array_push($lines, '', 'Source:', ...$attr);
$text = implode("\r\n", $lines);

$enc = fn(string $s): string => '=?UTF-8?B?' . base64_encode($s) . '?=';
$boundary = 'vs_' . bin2hex(random_bytes(12));
$headers = [
    'Date: ' . date('r'),
    'From: ' . $enc('VShark website') . ' <' . $from . '>',
    'Reply-To: ' . $enc($name) . ' <' . $email . '>',
    'MIME-Version: 1.0',
    'Content-Type: multipart/mixed; boundary="' . $boundary . '"',
];
$body  = "--$boundary\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: base64\r\n\r\n"
       . chunk_split(base64_encode($text)) . "\r\n";
if ($attach) {
    $body .= "--$boundary\r\nContent-Type: application/octet-stream; name=\"{$attach['name']}\"\r\n"
           . "Content-Transfer-Encoding: base64\r\nContent-Disposition: attachment; filename=\"{$attach['name']}\"\r\n\r\n"
           . chunk_split(base64_encode($attach['data'])) . "\r\n";
}
$body .= "--$boundary--\r\n";

// ---------------------------------------------------------------- send
function smtp_send(array $s, string $from, string $to, string $data): bool {
    $prefix = ($s['secure'] ?? 'tls') === 'ssl' ? 'ssl://' : 'tcp://';
    $fp = @stream_socket_client($prefix . $s['host'] . ':' . (int)$s['port'], $errno, $errstr, 20);
    if (!$fp) { error_log("send-enquiry: SMTP connect failed: $errstr"); return false; }
    stream_set_timeout($fp, 30);
    $read = function () use ($fp): string {                // reads a (multi-line) reply, returns it
        $out = '';
        while (($line = fgets($fp, 1024)) !== false) {
            $out .= $line;
            if (strlen($line) < 4 || $line[3] === ' ') break;
        }
        return $out;
    };
    $cmd = function (string $c, array $ok) use ($fp, $read): bool {
        if ($c !== '') fwrite($fp, $c . "\r\n");
        $r = $read();
        if (!in_array((int)substr($r, 0, 3), $ok, true)) { error_log('send-enquiry: SMTP "' . strtok($c, ' ') . '" -> ' . trim($r)); return false; }
        return true;
    };
    $host = gethostname() ?: 'localhost';
    $ok = $cmd('', [220]) && $cmd("EHLO $host", [250]);
    if ($ok && ($s['secure'] ?? 'tls') === 'tls') {
        $ok = $cmd('STARTTLS', [220])
            && stream_socket_enable_crypto($fp, true, STREAM_CRYPTO_METHOD_TLSv1_2_CLIENT | STREAM_CRYPTO_METHOD_TLSv1_3_CLIENT)
            && $cmd("EHLO $host", [250]);
    }
    if ($ok && !empty($s['user'])) {
        $ok = $cmd('AUTH LOGIN', [334]) && $cmd(base64_encode($s['user']), [334]) && $cmd(base64_encode($s['pass']), [235]);
    }
    $ok = $ok && $cmd("MAIL FROM:<$from>", [250]) && $cmd("RCPT TO:<$to>", [250, 251]) && $cmd('DATA', [354]);
    if ($ok) {
        $data = preg_replace('/^\./m', '..', $data);        // dot-stuffing
        $ok = $cmd($data . "\r\n.", [250]);
    }
    fwrite($fp, "QUIT\r\n");
    fclose($fp);
    return $ok;
}

$smtp = $cfg['smtp'] ?? [];
if (!empty($smtp['host'])) {
    $data = implode("\r\n", array_merge(['To: <' . $to . '>', 'Subject: ' . $enc($subject)], $headers)) . "\r\n\r\n" . $body;
    $sent = smtp_send($smtp, $from, $to, $data);
} else {
    $sent = mail($to, $enc($subject), $body, implode("\r\n", $headers), '-f' . $from);
}

if (!$sent) back('send');
// ?sent=1 marks a real submission: the thanks page fires the Lead / generate_lead conversion only then
header('Location: /thanks.html?sent=1', true, 303);
exit;
