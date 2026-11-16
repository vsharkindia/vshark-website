<?php
/*
 * Copy this file to enquiry-config.php ON THE SERVER and fill it in. Never commit real secrets (the repository is public).
 * Best place: one folder ABOVE the web root, e.g. on Hostinger  domains/<site>/enquiry-config.php
 * (next to public_html, not inside it). send-enquiry.php looks there first, then next to itself.
 *
 * Recommended: 'graph' — Microsoft 365 through the Entra app "VShark website contact form"
 * (Mail.Send, restricted to info@ by an application access policy). Same values as the Netlify settings
 * MS_TENANT_ID / MS_CLIENT_ID / MS_CLIENT_SECRET. Attachments up to 3 MB.
 * Leave 'graph' => [] to use SMTP instead, and 'smtp' host '' to use PHP mail().
 */
return [
    'to'   => 'info@vsharksolutions.com',          // where enquiries are delivered (comma-separated allowed for Graph)
    'from' => 'info@vsharksolutions.com',          // the mailbox that sends
    'graph' => [
        'tenant_id'     => '',                     // Directory (tenant) ID
        'client_id'     => '',                     // Application (client) ID
        'client_secret' => '',                     // client secret VALUE (renew before it expires)
    ],
    'smtp' => [                                    // only used when 'graph' is empty
        'host'   => '',                            // e.g. smtp.office365.com ('' = PHP mail())
        'port'   => 587,
        'secure' => 'tls',
        'user'   => '',
        'pass'   => '',
    ],
];
