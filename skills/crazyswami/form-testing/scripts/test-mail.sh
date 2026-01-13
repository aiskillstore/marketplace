#!/bin/bash
# Test WordPress email delivery
# Usage: ./test-mail.sh [container-name] [recipient-email]

set -e

CONTAINER="${1:-wordpress-local-wordpress-1}"
TO_EMAIL="${2:-admin@csrdevelopment.com}"

echo ""
echo -e "\033[0;32m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
echo -e "\033[0;32m  WordPress Email Test\033[0m"
echo -e "\033[0;32m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
echo -e "Container: \033[1;33m$CONTAINER\033[0m"
echo -e "Recipient: \033[1;33m$TO_EMAIL\033[0m"
echo ""

# Check if WP Mail SMTP is active
echo "Checking WP Mail SMTP plugin..."
if docker exec "$CONTAINER" wp plugin is-active wp-mail-smtp 2>/dev/null; then
    echo -e "  \033[0;32m✓\033[0m WP Mail SMTP is active"
else
    echo -e "  \033[0;33m⚠\033[0m WP Mail SMTP not active (using PHP mail)"
fi

# Get SMTP configuration
echo ""
echo "SMTP Configuration:"
docker exec "$CONTAINER" wp eval '
$options = get_option("wp_mail_smtp");
if (!empty($options)) {
    if (!empty($options["smtp"]["host"])) {
        echo "  Host: " . $options["smtp"]["host"] . "\n";
        echo "  Port: " . $options["smtp"]["port"] . "\n";
        echo "  Encryption: " . ($options["smtp"]["encryption"] ?: "none") . "\n";
        echo "  Auth: " . ($options["smtp"]["auth"] ? "Yes" : "No") . "\n";
    } elseif (!empty($options["mail"]["mailer"])) {
        echo "  Mailer: " . $options["mail"]["mailer"] . "\n";
    } else {
        echo "  Using PHP mail() function\n";
    }
} else {
    echo "  Not configured - using default PHP mail()\n";
}
' 2>/dev/null || echo "  Unable to read configuration"

# Send test email
echo ""
echo "Sending test email..."
docker exec "$CONTAINER" wp eval "
\$to = '$TO_EMAIL';
\$subject = 'WordPress Email Test - ' . date('Y-m-d H:i:s');
\$message = 'This is a test email from your WordPress site.\\n\\n';
\$message .= 'Site URL: ' . home_url() . '\\n';
\$message .= 'Sent at: ' . current_time('mysql') . '\\n';
\$message .= 'PHP Version: ' . phpversion() . '\\n';
\$message .= 'WordPress Version: ' . get_bloginfo('version') . '\\n';
\$message .= '\\nIf you receive this message, email delivery is working correctly!';

\$headers = array(
    'Content-Type: text/plain; charset=UTF-8',
);

\$result = wp_mail(\$to, \$subject, \$message, \$headers);

if (\$result) {
    echo \"  ✓ Email sent successfully to \$to\\n\";
    echo \"  Subject: \$subject\\n\";
} else {
    echo \"  ✗ Failed to send email\\n\";
    global \$phpmailer;
    if (isset(\$phpmailer) && !empty(\$phpmailer->ErrorInfo)) {
        echo \"  Error: \" . \$phpmailer->ErrorInfo . \"\\n\";
    }
}
"

echo ""
echo -e "\033[0;32m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
echo "Check your inbox for the test email!"
echo -e "\033[0;32m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
