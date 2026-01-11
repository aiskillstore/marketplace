<?php
/**
 * Plugin Name:       {{PLUGIN_NAME}}
 * Plugin URI:        https://example.com/plugins/{{PLUGIN_SLUG}}/
 * Description:       {{PLUGIN_DESCRIPTION}}
 * Version:           1.0.0
 * Requires at least: 6.0
 * Requires PHP:      7.4
 * Author:            {{AUTHOR_NAME}}
 * Author URI:        https://example.com/
 * License:           GPL v2 or later
 * License URI:       https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain:       {{TEXT_DOMAIN}}
 * Domain Path:       /languages
 *
 * @package {{PLUGIN_NAMESPACE}}
 */

// Prevent direct access.
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

// Plugin constants.
define( '{{PLUGIN_CONST}}_VERSION', '1.0.0' );
define( '{{PLUGIN_CONST}}_PATH', plugin_dir_path( __FILE__ ) );
define( '{{PLUGIN_CONST}}_URL', plugin_dir_url( __FILE__ ) );
define( '{{PLUGIN_CONST}}_BASENAME', plugin_basename( __FILE__ ) );

/**
 * Plugin main class.
 *
 * @since 1.0.0
 */
final class {{PLUGIN_CLASS}} {

	/**
	 * Plugin instance.
	 *
	 * @since 1.0.0
	 * @var {{PLUGIN_CLASS}}
	 */
	private static $instance = null;

	/**
	 * Get plugin instance.
	 *
	 * @since 1.0.0
	 *
	 * @return {{PLUGIN_CLASS}}
	 */
	public static function get_instance() {
		if ( null === self::$instance ) {
			self::$instance = new self();
		}
		return self::$instance;
	}

	/**
	 * Constructor.
	 *
	 * @since 1.0.0
	 */
	private function __construct() {
		$this->load_dependencies();
		$this->set_locale();
		$this->define_admin_hooks();
		$this->define_public_hooks();
	}

	/**
	 * Load plugin dependencies.
	 *
	 * @since 1.0.0
	 */
	private function load_dependencies() {
		require_once {{PLUGIN_CONST}}_PATH . 'includes/class-{{PLUGIN_SLUG}}-loader.php';
		require_once {{PLUGIN_CONST}}_PATH . 'includes/class-{{PLUGIN_SLUG}}-i18n.php';
		require_once {{PLUGIN_CONST}}_PATH . 'admin/class-{{PLUGIN_SLUG}}-admin.php';
		require_once {{PLUGIN_CONST}}_PATH . 'public/class-{{PLUGIN_SLUG}}-public.php';
	}

	/**
	 * Set plugin locale for internationalization.
	 *
	 * @since 1.0.0
	 */
	private function set_locale() {
		add_action(
			'plugins_loaded',
			function() {
				load_plugin_textdomain(
					'{{TEXT_DOMAIN}}',
					false,
					dirname( {{PLUGIN_CONST}}_BASENAME ) . '/languages/'
				);
			}
		);
	}

	/**
	 * Register admin hooks.
	 *
	 * @since 1.0.0
	 */
	private function define_admin_hooks() {
		$admin = new {{PLUGIN_CLASS}}_Admin();

		add_action( 'admin_enqueue_scripts', array( $admin, 'enqueue_styles' ) );
		add_action( 'admin_enqueue_scripts', array( $admin, 'enqueue_scripts' ) );
		add_action( 'admin_menu', array( $admin, 'add_admin_menu' ) );
		add_action( 'admin_init', array( $admin, 'register_settings' ) );
	}

	/**
	 * Register public hooks.
	 *
	 * @since 1.0.0
	 */
	private function define_public_hooks() {
		$public = new {{PLUGIN_CLASS}}_Public();

		add_action( 'wp_enqueue_scripts', array( $public, 'enqueue_styles' ) );
		add_action( 'wp_enqueue_scripts', array( $public, 'enqueue_scripts' ) );
	}

	/**
	 * Run on plugin activation.
	 *
	 * @since 1.0.0
	 */
	public static function activate() {
		// Create database tables, set default options, etc.
		add_option( '{{TEXT_DOMAIN}}_version', {{PLUGIN_CONST}}_VERSION );
		add_option( '{{TEXT_DOMAIN}}_activated', time() );

		// Flush rewrite rules.
		flush_rewrite_rules();
	}

	/**
	 * Run on plugin deactivation.
	 *
	 * @since 1.0.0
	 */
	public static function deactivate() {
		// Cleanup tasks.
		flush_rewrite_rules();
	}
}

// Activation/deactivation hooks.
register_activation_hook( __FILE__, array( '{{PLUGIN_CLASS}}', 'activate' ) );
register_deactivation_hook( __FILE__, array( '{{PLUGIN_CLASS}}', 'deactivate' ) );

/**
 * Initialize plugin.
 *
 * @since 1.0.0
 *
 * @return {{PLUGIN_CLASS}}
 */
function {{PLUGIN_FUNC}}() {
	return {{PLUGIN_CLASS}}::get_instance();
}

// Start the plugin.
{{PLUGIN_FUNC}}();
