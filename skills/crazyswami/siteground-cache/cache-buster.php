<?php
/**
 * SiteGround Cache Buster for Development
 * Disables caching for logged-in administrators
 *
 * USAGE: Copy this entire file content to the end of your child theme's functions.php
 * REMOVE OR DISABLE IN PRODUCTION when done testing
 *
 * @package SiteGround_Cache_Buster
 * @version 1.0.0
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// ============================================================================
// DEVELOPMENT MODE BANNER
// Shows theme version to confirm child theme is active (admin only)
// ============================================================================
add_action('wp_head', 'sg_dev_mode_banner');
function sg_dev_mode_banner() {
    if (current_user_can('administrator')) {
        $theme = wp_get_theme();
        $version = $theme->get('Version');
        $name = $theme->get('Name');
        echo '<style>
            .sg-dev-banner {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: #34889A;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                font-size: 12px;
                z-index: 999999;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }
        </style>
        <div class="sg-dev-banner">
            ' . esc_html($name) . ' v' . esc_html($version) . ' - ' . date('M j, H:i') . '
        </div>';
    }
}

// ============================================================================
// DISABLE ALL CACHING FOR ADMINISTRATORS
// Bypasses LiteSpeed Cache + SG CachePress + CDN caching
// ============================================================================
add_action('init', 'sg_disable_cache_for_dev');
function sg_disable_cache_for_dev() {
    if (current_user_can('administrator')) {
        // Disable LiteSpeed Cache
        if (!defined('LSCACHE_NO_CACHE')) {
            define('LSCACHE_NO_CACHE', true);
        }

        // Disable SG Optimizer/CachePress
        if (!defined('SG_CACHEPRESS_NO_CACHE')) {
            define('SG_CACHEPRESS_NO_CACHE', true);
        }

        // Send no-cache headers
        nocache_headers();

        // Additional headers for CDN bypass
        header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
        header('Pragma: no-cache');
        header('Expires: Thu, 01 Jan 1970 00:00:00 GMT');
    }
}

// ============================================================================
// BUST BROWSER CACHE FOR THEME ASSETS
// Adds timestamp to CSS/JS URLs so browsers always fetch fresh files
// ============================================================================
add_filter('style_loader_src', 'sg_bust_asset_cache', 999);
add_filter('script_loader_src', 'sg_bust_asset_cache', 999);
function sg_bust_asset_cache($src) {
    if (current_user_can('administrator')) {
        // Only bust cache for theme assets
        $theme_uri = get_stylesheet_directory_uri();
        $parent_uri = get_template_directory_uri();

        if (strpos($src, $theme_uri) !== false || strpos($src, $parent_uri) !== false) {
            $src = add_query_arg('v', time(), $src);
        }
    }
    return $src;
}
