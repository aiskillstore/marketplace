---
name: form-testing
description: Test WordPress form submissions and email delivery. Validates contact forms, checks WP Mail SMTP configuration, and sends test emails. Use when verifying form functionality or troubleshooting email delivery issues.
allowed-tools: Read, Write, Edit, Bash, WebFetch
---

# Form Testing Skill

Comprehensive form testing for WordPress sites - validates form submissions, email delivery, and SMTP configuration.

## Quick Start

```bash
# Test WP Mail SMTP configuration
/root/.claude/skills/form-testing/scripts/test-mail.sh wordpress-container

# Test contact form submission
/root/.claude/skills/form-testing/scripts/test-form.sh https://site.com/contact/

# Full form audit
/root/.claude/skills/form-testing/scripts/audit-forms.sh wordpress-container
```

---

## What This Skill Tests

### 1. Email Delivery
- WP Mail SMTP plugin configuration
- Email sending capability via `wp_mail()`
- SMTP server connectivity
- Email headers and formatting

### 2. Contact Form Functionality
- Form field validation
- Nonce verification
- Success/error redirects
- Email receipt

### 3. Form Security
- CSRF protection (nonces)
- Input sanitization
- Spam protection (if applicable)

---

## Testing Methods

### Method 1: WP-CLI Email Test

The most reliable way to test email delivery:

```bash
# Send test email via WP-CLI
docker exec wordpress-container wp eval '
$to = "test@example.com";
$subject = "WordPress Test Email";
$message = "This is a test email from WordPress at " . date("Y-m-d H:i:s");
$headers = array("Content-Type: text/plain; charset=UTF-8");

$result = wp_mail($to, $subject, $message, $headers);

if ($result) {
    echo "SUCCESS: Email sent to $to\n";
} else {
    echo "FAILED: Could not send email\n";
    global $phpmailer;
    if (isset($phpmailer)) {
        echo "Error: " . $phpmailer->ErrorInfo . "\n";
    }
}
'
```

### Method 2: Check SMTP Configuration

```bash
# Check WP Mail SMTP options
docker exec wordpress-container wp option get wp_mail_smtp --format=json | jq

# Check if SMTP is configured
docker exec wordpress-container wp eval '
$options = get_option("wp_mail_smtp");
if (!empty($options["smtp"]["host"])) {
    echo "SMTP Host: " . $options["smtp"]["host"] . "\n";
    echo "SMTP Port: " . $options["smtp"]["port"] . "\n";
    echo "SMTP Auth: " . ($options["smtp"]["auth"] ? "Yes" : "No") . "\n";
    echo "Encryption: " . $options["smtp"]["encryption"] . "\n";
} else {
    echo "SMTP not configured - using PHP mail()\n";
}
'
```

### Method 3: HTTP Form Submission Test

```bash
# Test contact form via curl
curl -X POST "https://site.com/contact/" \
  -d "first_name=Test" \
  -d "last_name=User" \
  -d "email=test@example.com" \
  -d "message=This is a test submission" \
  -d "csr_contact_form=1" \
  -L -v 2>&1 | grep -E "(< HTTP|Location:|contact=)"
```

---

## Automated Test Script

### test-mail.sh

```bash
#!/bin/bash
# Test email sending via WordPress

CONTAINER="${1:-wordpress}"
TO_EMAIL="${2:-admin@example.com}"

echo "Testing email delivery..."

docker exec "$CONTAINER" wp eval "
\$to = '$TO_EMAIL';
\$subject = 'Form Test - ' . date('Y-m-d H:i:s');
\$message = 'This is an automated test from the form-testing skill.\\n\\n';
\$message .= 'Site: ' . home_url() . '\\n';
\$message .= 'Time: ' . current_time('mysql') . '\\n';
\$message .= '\\nIf you receive this, email delivery is working!';

\$headers = array(
    'Content-Type: text/plain; charset=UTF-8',
    'From: WordPress <wordpress@' . parse_url(home_url(), PHP_URL_HOST) . '>'
);

echo 'Sending test email to: ' . \$to . \"\\n\";
\$result = wp_mail(\$to, \$subject, \$message, \$headers);

if (\$result) {
    echo \"SUCCESS: Test email sent!\\n\";
    echo \"Check inbox for: \$subject\\n\";
} else {
    echo \"FAILED: Could not send email\\n\";
    global \$phpmailer;
    if (isset(\$phpmailer) && !empty(\$phpmailer->ErrorInfo)) {
        echo \"PHPMailer Error: \" . \$phpmailer->ErrorInfo . \"\\n\";
    }
}
"
```

---

## Troubleshooting

### Email Not Sending

1. **Check WP Mail SMTP is active:**
   ```bash
   docker exec wordpress wp plugin is-active wp-mail-smtp && echo "Active" || echo "Not active"
   ```

2. **Verify SMTP settings:**
   ```bash
   docker exec wordpress wp option get wp_mail_smtp --format=json
   ```

3. **Test with debug logging:**
   ```bash
   docker exec wordpress wp eval '
   define("WP_DEBUG", true);
   define("WP_DEBUG_LOG", true);
   wp_mail("test@example.com", "Debug Test", "Testing");
   '
   ```

4. **Check email log (if using WP Mail SMTP Pro):**
   ```bash
   docker exec wordpress wp db query "SELECT * FROM wp_wpmailsmtp_logs ORDER BY id DESC LIMIT 5"
   ```

### Form Submission Errors

1. **Check nonce verification:**
   - Ensure form has `wp_nonce_field()`
   - Verify nonce name matches in handler

2. **Check redirect after submit:**
   ```bash
   curl -X POST "https://site.com/contact/" \
     -d "form_data=here" \
     -L -w "%{redirect_url}" -o /dev/null -s
   ```

3. **Check for PHP errors:**
   ```bash
   docker exec wordpress tail -50 /var/www/html/wp-content/debug.log
   ```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Emails go to spam | Missing SPF/DKIM | Configure DNS records |
| "Could not instantiate mail function" | PHP mail disabled | Use SMTP plugin |
| Form returns blank page | PHP error | Enable WP_DEBUG |
| Nonce verification failed | Session expired or cache | Check caching plugin |
| Form fields not received | Missing name attributes | Add name to inputs |

---

## WP Mail SMTP Configuration

### Recommended Providers

1. **SMTP.com** - Free tier, reliable
2. **SendGrid** - 100 emails/day free
3. **Mailgun** - Developer-friendly
4. **Amazon SES** - Cheapest for volume
5. **Gmail SMTP** - Quick setup (personal use)

### Configuration via WP-CLI

```bash
# Set up SMTP configuration
docker exec wordpress wp option update wp_mail_smtp '{
  "mail": {
    "from_email": "noreply@yoursite.com",
    "from_name": "Your Site",
    "mailer": "smtp"
  },
  "smtp": {
    "host": "smtp.example.com",
    "port": 587,
    "encryption": "tls",
    "auth": true,
    "user": "smtp-user",
    "pass": "smtp-password"
  }
}' --format=json
```

---

## Form Types Tested

### Contact Form (CSR Theme)
- **Template**: `page-contact.php`
- **Handler**: `csr_handle_contact_form()` in functions.php
- **Fields**: first_name, last_name, email, message
- **Nonce**: `csr_contact_nonce`
- **Success Redirect**: `?contact=success`

### Property Inquiry Form (CSR Theme)
- **Template**: `single-property.php`
- **Handler**: `csr_handle_inquiry_form()` in functions.php
- **Fields**: name, company, email, message, property_title
- **Nonce**: `csr_inquiry_nonce`
- **Success Redirect**: `?inquiry=success`

---

## Audit Report Template

When running a form audit, document:

```markdown
## Form Audit Report - [Site Name]
**Date**: YYYY-MM-DD
**Auditor**: Claude

### Email Delivery
- [ ] WP Mail SMTP installed and active
- [ ] SMTP credentials configured
- [ ] Test email received successfully
- [ ] SPF/DKIM records in place (check via MXToolbox)

### Contact Form
- [ ] Form displays correctly
- [ ] All fields validate properly
- [ ] Nonce verification working
- [ ] Success message shown after submit
- [ ] Email received by admin
- [ ] Reply-to header set correctly

### Security
- [ ] CSRF protection (nonces) in place
- [ ] Input sanitization (sanitize_text_field, etc.)
- [ ] Email header injection prevention
- [ ] Rate limiting (if needed)

### Recommendations
1. ...
2. ...
```

---

## Related Skills

- **wp-docker**: WordPress container management
- **visual-qa**: Visual testing after form changes
- **seo-optimizer**: Check form pages for SEO
- **white-label**: Admin branding for form notifications

---

## Sources

- [WP Mail SMTP Documentation](https://wpmailsmtp.com/docs/)
- [WordPress wp_mail() Function](https://developer.wordpress.org/reference/functions/wp_mail/)
- [Contact Form Security Best Practices](https://developer.wordpress.org/plugins/security/)
