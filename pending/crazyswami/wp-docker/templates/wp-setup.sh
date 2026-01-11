#!/bin/bash
# WordPress Site Setup Script
# Usage: ./wp-setup.sh [URL] [TITLE] [ADMIN_USER] [ADMIN_PASS] [ADMIN_EMAIL]

set -e

# Configuration
SITE_URL="${1:-http://localhost:8080}"
SITE_TITLE="${2:-New WordPress Site}"
ADMIN_USER="${3:-admin}"
ADMIN_PASSWORD="${4:-password123}"
ADMIN_EMAIL="${5:-admin@example.com}"

echo "=========================================="
echo "WordPress Site Setup"
echo "=========================================="
echo "URL: $SITE_URL"
echo "Title: $SITE_TITLE"
echo "Admin: $ADMIN_USER"
echo "=========================================="

# Wait for containers to be ready
echo "Waiting for containers..."
sleep 5

# Check if WordPress is installed
if docker-compose run --rm wpcli core is-installed 2>/dev/null; then
    echo "WordPress is already installed."
    read -p "Reinstall? (y/N): " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo "Skipping installation."
        exit 0
    fi
fi

# Install WordPress core
echo "Installing WordPress..."
docker-compose run --rm wpcli core install \
  --url="$SITE_URL" \
  --title="$SITE_TITLE" \
  --admin_user="$ADMIN_USER" \
  --admin_password="$ADMIN_PASSWORD" \
  --admin_email="$ADMIN_EMAIL" \
  --skip-email

echo "WordPress installed successfully!"

# Configure permalinks
echo "Configuring permalinks..."
docker-compose run --rm wpcli rewrite structure '/%postname%/' --hard

# Install essential plugins
echo "Installing plugins..."
docker-compose run --rm wpcli plugin install \
  admin-site-enhancements \
  branda-white-labeling \
  admin-menu-editor \
  wordpress-seo \
  litespeed-cache \
  ewww-image-optimizer \
  wp-mail-smtp \
  instant-images \
  duplicate-post \
  --activate

echo "Plugins installed!"

# Configure ASE (Admin and Site Enhancements)
echo "Configuring ASE..."
docker-compose run --rm wpcli option update admin_site_enhancements '{
  "change_login_url": {
    "enabled": true,
    "slug": "secure-login"
  },
  "hide_admin_notices": true,
  "disable_xmlrpc": true,
  "obfuscate_author_slugs": true,
  "disable_dashboard_widgets": {
    "welcome": true,
    "quick_draft": true,
    "wordpress_news": true
  },
  "heartbeat_control": {
    "dashboard": "disable",
    "frontend": "disable",
    "post_editor": 30
  },
  "revisions_control": 5
}' --format=json

# Configure site settings
echo "Configuring site settings..."
docker-compose run --rm wpcli option update blogname "$SITE_TITLE"
docker-compose run --rm wpcli option update blogdescription "Professional WordPress Site"
docker-compose run --rm wpcli option update timezone_string "America/New_York"
docker-compose run --rm wpcli option update date_format "F j, Y"
docker-compose run --rm wpcli option update time_format "g:i a"
docker-compose run --rm wpcli option update start_of_week 1
docker-compose run --rm wpcli option update blog_public 0  # Discourage search engines during development

# Create default pages
echo "Creating default pages..."

# Home page
docker-compose run --rm wpcli post create \
  --post_type=page \
  --post_title="Home" \
  --post_status=publish \
  --post_content="Welcome to $SITE_TITLE"

# About page
docker-compose run --rm wpcli post create \
  --post_type=page \
  --post_title="About" \
  --post_status=publish \
  --post_content="About our company."

# Contact page
docker-compose run --rm wpcli post create \
  --post_type=page \
  --post_title="Contact" \
  --post_status=publish \
  --post_content="Get in touch with us."

# Privacy Policy page
docker-compose run --rm wpcli post create \
  --post_type=page \
  --post_title="Privacy Policy" \
  --post_status=publish \
  --post_content="Our privacy policy."

# Terms of Service page
docker-compose run --rm wpcli post create \
  --post_type=page \
  --post_title="Terms of Service" \
  --post_status=publish \
  --post_content="Our terms of service."

# Set home page as front page
HOME_ID=$(docker-compose run --rm wpcli post list --post_type=page --title="Home" --field=ID)
docker-compose run --rm wpcli option update show_on_front 'page'
docker-compose run --rm wpcli option update page_on_front "$HOME_ID"

# Delete default post and page
echo "Cleaning up defaults..."
docker-compose run --rm wpcli post delete 1 --force 2>/dev/null || true
docker-compose run --rm wpcli post delete 2 --force 2>/dev/null || true

# Flush rewrite rules
docker-compose run --rm wpcli rewrite flush

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo "Site URL: $SITE_URL"
echo "Admin URL: $SITE_URL/wp-admin/"
echo "Login URL: $SITE_URL/secure-login/"
echo "Username: $ADMIN_USER"
echo "Password: $ADMIN_PASSWORD"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Configure white-labeling with Branda"
echo "2. Set up Yoast SEO"
echo "3. Configure LiteSpeed Cache"
echo "4. Upload site logo and favicon"
echo "=========================================="
