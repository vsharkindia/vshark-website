<?php
/*
 * Copy this file to enquiry-config.php ON THE SERVER and fill it in.
 * enquiry-config.php is listed in .gitignore and blocked by .htaccess — never commit real passwords.
 *
 * Recommended: send through the company's Microsoft 365 mailbox (SMTP AUTH must be enabled for that
 * mailbox in the Microsoft 365 admin centre). Mail sent this way passes SPF, so it won't land in spam.
 * To use PHP mail() instead, set 'host' => '' — then the hosting server's IP must be added to the
 * domain's SPF record, or enquiries may go to junk.
 */
return [
    'to'   => 'info@vsharksolutions.com',          // where enquiries are delivered
    'from' => 'info@vsharksolutions.com',          // must be a mailbox the SMTP account is allowed to send as
    'smtp' => [
        'host'   => 'smtp.office365.com',          // '' = use PHP mail()
        'port'   => 587,
        'secure' => 'tls',                         // 'tls' (STARTTLS on 587) or 'ssl' (465)
        'user'   => 'info@vsharksolutions.com',
        'pass'   => '',                            // the mailbox password (or app password)
    ],
];
