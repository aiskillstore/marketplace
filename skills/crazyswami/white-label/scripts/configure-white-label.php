<?php
/**
 * White Label Configuration Script for WP-CLI
 *
 * Usage: wp eval-file configure-white-label.php --config=/path/to/config.json
 *
 * This script programmatically configures:
 * - White Label CMS (dashboard, menus, branding)
 * - ASE (security, admin cleanup)
 * - Branda (login page, admin bar)
 */

// Ensure WP-CLI context
if (!defined('WP_CLI')) {
    echo "This script must be run via WP-CLI\n";
    exit(1);
}

/**
 * White Label Configurator Class
 */
class WhiteLabelConfigurator {

    private $config;
    private $logo_id = null;

    public function __construct($config) {
        $this->config = $config;
    }

    /**
     * Run full white-label configuration
     */
    public function configure() {
        WP_CLI::log("Starting white-label configuration...\n");

        // Upload logo if provided
        if (!empty($this->config['brand']['logo_url'])) {
            $this->upload_logo();
        }

        // Configure each plugin
        $this->configure_wlcms();
        $this->configure_ase();
        $this->configure_branda();

        WP_CLI::success("White-label configuration complete!");
    }

    /**
     * Upload brand logo to media library
     */
    private function upload_logo() {
        $logo_url = $this->config['brand']['logo_url'];

        // Check if it's already a WordPress attachment
        if (is_numeric($logo_url)) {
            $this->logo_id = intval($logo_url);
            WP_CLI::log("Using existing logo ID: {$this->logo_id}");
            return;
        }

        // Download and upload
        require_once(ABSPATH . 'wp-admin/includes/media.php');
        require_once(ABSPATH . 'wp-admin/includes/file.php');
        require_once(ABSPATH . 'wp-admin/includes/image.php');

        $tmp = download_url($logo_url);
        if (is_wp_error($tmp)) {
            WP_CLI::warning("Could not download logo: " . $tmp->get_error_message());
            return;
        }

        $file_array = array(
            'name'     => basename(parse_url($logo_url, PHP_URL_PATH)) ?: 'brand-logo.png',
            'tmp_name' => $tmp,
        );

        $this->logo_id = media_handle_sideload($file_array, 0, $this->config['brand']['company_name'] . ' Logo');

        if (is_wp_error($this->logo_id)) {
            WP_CLI::warning("Could not upload logo: " . $this->logo_id->get_error_message());
            $this->logo_id = null;
            @unlink($tmp);
            return;
        }

        WP_CLI::log("Uploaded logo with ID: {$this->logo_id}");
    }

    /**
     * Get logo URL from ID
     */
    private function get_logo_url() {
        if ($this->logo_id) {
            return wp_get_attachment_url($this->logo_id);
        }
        return $this->config['brand']['logo_url'] ?? '';
    }

    /**
     * Configure White Label CMS plugin
     */
    private function configure_wlcms() {
        WP_CLI::log("Configuring White Label CMS...");

        $brand = $this->config['brand'] ?? [];
        $colors = $brand['colors'] ?? [];
        $login = $this->config['login'] ?? [];
        $dashboard = $this->config['dashboard'] ?? [];
        $menus = $this->config['menus'] ?? [];

        $logo_url = $this->get_logo_url();

        $wlcms_options = array(
            'version' => '2.7.8',

            // Admin Bar Branding
            'admin_bar_logo' => $logo_url,
            'admin_bar_logo_width' => 20,
            'admin_bar_alt_text' => $brand['company_name'] ?? '',
            'admin_bar_howdy_text' => $this->config['greeting'] ?? 'Welcome,',
            'admin_bar_url' => home_url(),
            'hide_wordpress_logo_and_links' => true,
            'hide_wp_version' => true,

            // Side Menu Branding
            'side_menu_image' => $logo_url,
            'collapsed_side_menu_image' => $logo_url,
            'side_menu_link_url' => home_url(),
            'side_menu_alt_text' => $brand['company_name'] ?? '',
            'use_developer_side_menu_image' => !empty($logo_url),

            // Footer Branding
            'footer_html' => sprintf(
                '&copy; %s %s. All rights reserved.',
                date('Y'),
                $brand['company_name'] ?? 'Company'
            ),
            'footer_url' => $brand['website'] ?? home_url(),
            'developer_branding_footer' => true,

            // Dashboard
            'dashboard_title' => $dashboard['title'] ?? 'Dashboard',
            'hide_all_dashboard_panels' => $dashboard['hide_all_widgets'] ?? false,
            'hide_at_a_glance' => $dashboard['hide_at_a_glance'] ?? true,
            'hide_activities' => $dashboard['hide_activities'] ?? false,
            'hide_quick_press' => $dashboard['hide_quick_draft'] ?? true,
            'hide_news_and_events' => $dashboard['hide_news'] ?? true,
            'hide_recent_comments' => $dashboard['hide_comments'] ?? true,
            'remove_empty_dash_panel' => true,

            // Admin cleanup
            'hide_help_box' => true,
            'hide_screen_options' => $dashboard['hide_screen_options'] ?? false,
            'hide_nag_messages' => true,

            // Menu visibility (will be expanded)
            'admin_menus' => $this->build_menu_config($menus),
            'enable_wlcms_admin' => true,

            // Login Page
            'login_logo' => $logo_url,
            'logo_width' => $login['logo_width'] ?? 300,
            'logo_height' => $login['logo_height'] ?? false,
            'logo_bottom_margin' => $login['logo_margin'] ?? 20,
            'background_color' => $login['background_color'] ?? $colors['background'] ?? '#1a1a2e',
            'background_image' => $login['background_image'] ?? '',
            'full_screen_background_image' => !empty($login['background_image']),
            'form_background_color' => $login['form_background'] ?? '#ffffff',
            'form_label_color' => $login['form_label_color'] ?? '#333333',
            'form_button_color' => $login['button_color'] ?? $colors['primary'] ?? '#2271b1',
            'form_button_text_color' => $login['button_text_color'] ?? '#ffffff',
            'form_button_hover_color' => $login['button_hover_color'] ?? $colors['primary_dark'] ?? '#135e96',
            'form_button_text_hover_color' => '#ffffff',
            'hide_register_lost_password' => $login['hide_lost_password'] ?? false,
            'hide_back_to_link' => $login['hide_back_link'] ?? false,

            // Custom CSS
            'settings_custom_css_admin' => $this->config['custom_css'] ?? '',
            'settings_custom_css_login' => $this->config['login_css'] ?? '',
        );

        // Build welcome panel if provided
        if (!empty($dashboard['welcome_message'])) {
            $wlcms_options['welcome_panel'] = array(
                array(
                    'is_active' => true,
                    'show_title' => true,
                    'template_type' => 'html',
                    'title' => $dashboard['welcome_title'] ?? 'Welcome',
                    'html' => $dashboard['welcome_message'],
                    'visible_to' => array('administrator', 'editor', 'author', 'contributor', 'subscriber'),
                ),
            );
        }

        update_option('wlcms_options', $wlcms_options);
        WP_CLI::log("  ✓ White Label CMS configured");
    }

    /**
     * Build menu visibility configuration
     */
    private function build_menu_config($menus) {
        if (empty($menus)) {
            return false;
        }

        $hide_for_editors = $menus['hide_for_editors'] ?? array(
            'plugins.php',
            'themes.php',
            'options-general.php',
            'tools.php',
        );

        // Return menu configuration array
        return array(
            'hide_menus' => $hide_for_editors,
            'visible_roles' => array('administrator'),
        );
    }

    /**
     * Configure ASE (Admin and Site Enhancements)
     */
    private function configure_ase() {
        WP_CLI::log("Configuring ASE...");

        $security = $this->config['security'] ?? [];
        $admin = $this->config['admin'] ?? [];
        $brand = $this->config['brand'] ?? [];

        $ase_options = array(
            // Security
            'change_login_url' => true,
            'custom_login_slug' => $security['login_url'] ?? 'secure-login',
            'disable_xml_rpc' => $security['disable_xmlrpc'] ?? true,
            'obfuscate_author_slugs' => $security['obfuscate_authors'] ?? true,
            'email_address_obfuscation' => $security['obfuscate_emails'] ?? true,

            // Admin Cleanup
            'hide_admin_notices' => $admin['hide_notices'] ?? true,
            'hide_admin_bar' => $admin['hide_admin_bar_frontend'] ?? false,
            'disable_dashboard_widgets' => $admin['disable_widgets'] ?? true,
            'wider_admin_menu' => $admin['wider_menu'] ?? true,

            // Footer
            'custom_admin_footer_text' => sprintf(
                '&copy; %s %s. All rights reserved.',
                date('Y'),
                $brand['company_name'] ?? 'Company'
            ),

            // Performance
            'heartbeat_control' => array(
                'dashboard' => 'disable',
                'post_editor' => 30,
                'frontend' => 'disable',
            ),
            'revisions_control' => $admin['max_revisions'] ?? 5,
        );

        update_option('admin_site_enhancements', $ase_options);
        WP_CLI::log("  ✓ ASE configured");
    }

    /**
     * Configure Branda (Ultimate Branding)
     */
    private function configure_branda() {
        WP_CLI::log("Configuring Branda...");

        $brand = $this->config['brand'] ?? [];
        $colors = $brand['colors'] ?? [];
        $login = $this->config['login'] ?? [];

        $logo_url = $this->get_logo_url();

        // Branda uses multiple options
        $branda_modules = get_option('ub_activated_modules', array());

        // Activate required modules
        $modules_to_activate = array(
            'admin-footer.php',
            'admin-message.php',
            'custom-admin-bar.php',
            'login-screen.php',
            'admin-menu.php',
        );

        foreach ($modules_to_activate as $module) {
            if (!in_array($module, $branda_modules)) {
                $branda_modules[] = $module;
            }
        }
        update_option('ub_activated_modules', $branda_modules);

        // Login screen settings
        $login_settings = array(
            'enabled' => true,
            'logo' => $logo_url,
            'logo_link' => home_url(),
            'logo_title' => $brand['company_name'] ?? '',
            'bg_color' => $login['background_color'] ?? $colors['background'] ?? '#1a1a2e',
            'bg_image' => $login['background_image'] ?? '',
            'box_bg' => $login['form_background'] ?? '#ffffff',
            'button_bg' => $login['button_color'] ?? $colors['primary'] ?? '#2271b1',
            'button_color' => '#ffffff',
            'custom_css' => $this->config['login_css'] ?? '',
        );
        update_option('ub_login_screen', $login_settings);

        // Admin bar settings
        $admin_bar = array(
            'enabled' => true,
            'hide_wp_logo' => true,
            'custom_logo' => $logo_url,
            'logo_link' => home_url(),
        );
        update_option('ub_admin_bar', $admin_bar);

        // Howdy replacement
        update_option('ub_admin_message', array(
            'enabled' => true,
            'message' => $this->config['greeting'] ?? 'Welcome,',
        ));

        // Footer
        update_option('ub_admin_footer', array(
            'enabled' => true,
            'text' => sprintf(
                '&copy; %s %s. All rights reserved.',
                date('Y'),
                $brand['company_name'] ?? 'Company'
            ),
        ));

        WP_CLI::log("  ✓ Branda configured");
    }
}

// Main execution
$config_file = '/tmp/white-label-config.json';

// Check for config file at expected location
if (!file_exists($config_file)) {
    // Use default/example config
    WP_CLI::log("No config file specified. Using default configuration.");

    $config = array(
        'brand' => array(
            'company_name' => get_bloginfo('name'),
            'logo_url' => '',
            'website' => home_url(),
            'colors' => array(
                'primary' => '#2271b1',
                'primary_dark' => '#135e96',
                'background' => '#1a1a2e',
            ),
        ),
        'login' => array(
            'background_color' => '#1a1a2e',
            'form_background' => '#ffffff',
            'button_color' => '#2271b1',
            'logo_width' => 300,
        ),
        'security' => array(
            'login_url' => 'secure-login',
            'disable_xmlrpc' => true,
            'obfuscate_authors' => true,
        ),
        'dashboard' => array(
            'hide_news' => true,
            'hide_quick_draft' => true,
            'hide_at_a_glance' => true,
        ),
        'greeting' => 'Welcome,',
    );
} else {
    if (!file_exists($config_file)) {
        WP_CLI::error("Config file not found: $config_file");
    }

    $config_json = file_get_contents($config_file);
    $config = json_decode($config_json, true);

    if (json_last_error() !== JSON_ERROR_NONE) {
        WP_CLI::error("Invalid JSON in config file: " . json_last_error_msg());
    }
}

// Run configuration
$configurator = new WhiteLabelConfigurator($config);
$configurator->configure();
