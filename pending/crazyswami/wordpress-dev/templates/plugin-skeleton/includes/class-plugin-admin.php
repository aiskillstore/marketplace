<?php
/**
 * Plugin Admin Class
 *
 * Handles all admin-side functionality.
 *
 * @package {{PLUGIN_NAMESPACE}}
 * @since 1.0.0
 */

// Prevent direct access.
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Admin class.
 *
 * @since 1.0.0
 */
class {{PLUGIN_CLASS}}_Admin {

	/**
	 * Constructor.
	 *
	 * @since 1.0.0
	 */
	public function __construct() {
		// Constructor code here.
	}

	/**
	 * Enqueue admin styles.
	 *
	 * @since 1.0.0
	 *
	 * @param string $hook Current admin page hook.
	 */
	public function enqueue_styles( $hook ) {
		// Only load on plugin pages.
		if ( strpos( $hook, '{{TEXT_DOMAIN}}' ) === false ) {
			return;
		}

		wp_enqueue_style(
			'{{TEXT_DOMAIN}}-admin',
			{{PLUGIN_CONST}}_URL . 'admin/css/admin.css',
			array(),
			{{PLUGIN_CONST}}_VERSION
		);
	}

	/**
	 * Enqueue admin scripts.
	 *
	 * @since 1.0.0
	 *
	 * @param string $hook Current admin page hook.
	 */
	public function enqueue_scripts( $hook ) {
		// Only load on plugin pages.
		if ( strpos( $hook, '{{TEXT_DOMAIN}}' ) === false ) {
			return;
		}

		wp_enqueue_script(
			'{{TEXT_DOMAIN}}-admin',
			{{PLUGIN_CONST}}_URL . 'admin/js/admin.js',
			array( 'jquery' ),
			{{PLUGIN_CONST}}_VERSION,
			true
		);

		wp_localize_script(
			'{{TEXT_DOMAIN}}-admin',
			'{{TEXT_DOMAIN}}Admin',
			array(
				'ajaxUrl' => admin_url( 'admin-ajax.php' ),
				'nonce'   => wp_create_nonce( '{{TEXT_DOMAIN}}_admin_nonce' ),
			)
		);
	}

	/**
	 * Add admin menu pages.
	 *
	 * @since 1.0.0
	 */
	public function add_admin_menu() {
		add_menu_page(
			__( '{{PLUGIN_NAME}}', '{{TEXT_DOMAIN}}' ),
			__( '{{PLUGIN_NAME}}', '{{TEXT_DOMAIN}}' ),
			'manage_options',
			'{{TEXT_DOMAIN}}',
			array( $this, 'render_main_page' ),
			'dashicons-admin-generic',
			80
		);

		add_submenu_page(
			'{{TEXT_DOMAIN}}',
			__( 'Settings', '{{TEXT_DOMAIN}}' ),
			__( 'Settings', '{{TEXT_DOMAIN}}' ),
			'manage_options',
			'{{TEXT_DOMAIN}}-settings',
			array( $this, 'render_settings_page' )
		);
	}

	/**
	 * Register plugin settings.
	 *
	 * @since 1.0.0
	 */
	public function register_settings() {
		register_setting(
			'{{TEXT_DOMAIN}}_settings',
			'{{TEXT_DOMAIN}}_options',
			array(
				'type'              => 'array',
				'sanitize_callback' => array( $this, 'sanitize_options' ),
				'default'           => array(),
			)
		);

		add_settings_section(
			'{{TEXT_DOMAIN}}_general',
			__( 'General Settings', '{{TEXT_DOMAIN}}' ),
			array( $this, 'render_section_general' ),
			'{{TEXT_DOMAIN}}-settings'
		);

		add_settings_field(
			'{{TEXT_DOMAIN}}_option_one',
			__( 'Option One', '{{TEXT_DOMAIN}}' ),
			array( $this, 'render_option_one' ),
			'{{TEXT_DOMAIN}}-settings',
			'{{TEXT_DOMAIN}}_general'
		);

		add_settings_field(
			'{{TEXT_DOMAIN}}_option_two',
			__( 'Option Two', '{{TEXT_DOMAIN}}' ),
			array( $this, 'render_option_two' ),
			'{{TEXT_DOMAIN}}-settings',
			'{{TEXT_DOMAIN}}_general'
		);
	}

	/**
	 * Sanitize options.
	 *
	 * @since 1.0.0
	 *
	 * @param array $options Options to sanitize.
	 * @return array Sanitized options.
	 */
	public function sanitize_options( $options ) {
		$sanitized = array();

		if ( isset( $options['option_one'] ) ) {
			$sanitized['option_one'] = sanitize_text_field( $options['option_one'] );
		}

		if ( isset( $options['option_two'] ) ) {
			$sanitized['option_two'] = absint( $options['option_two'] );
		}

		return $sanitized;
	}

	/**
	 * Render general section description.
	 *
	 * @since 1.0.0
	 */
	public function render_section_general() {
		echo '<p>' . esc_html__( 'Configure the general plugin settings below.', '{{TEXT_DOMAIN}}' ) . '</p>';
	}

	/**
	 * Render option one field.
	 *
	 * @since 1.0.0
	 */
	public function render_option_one() {
		$options = get_option( '{{TEXT_DOMAIN}}_options', array() );
		$value   = isset( $options['option_one'] ) ? $options['option_one'] : '';
		?>
		<input
			type="text"
			id="{{TEXT_DOMAIN}}_option_one"
			name="{{TEXT_DOMAIN}}_options[option_one]"
			value="<?php echo esc_attr( $value ); ?>"
			class="regular-text"
		>
		<p class="description"><?php esc_html_e( 'Enter option one value.', '{{TEXT_DOMAIN}}' ); ?></p>
		<?php
	}

	/**
	 * Render option two field.
	 *
	 * @since 1.0.0
	 */
	public function render_option_two() {
		$options = get_option( '{{TEXT_DOMAIN}}_options', array() );
		$value   = isset( $options['option_two'] ) ? $options['option_two'] : 0;
		?>
		<input
			type="number"
			id="{{TEXT_DOMAIN}}_option_two"
			name="{{TEXT_DOMAIN}}_options[option_two]"
			value="<?php echo esc_attr( $value ); ?>"
			class="small-text"
			min="0"
		>
		<p class="description"><?php esc_html_e( 'Enter option two value.', '{{TEXT_DOMAIN}}' ); ?></p>
		<?php
	}

	/**
	 * Render main admin page.
	 *
	 * @since 1.0.0
	 */
	public function render_main_page() {
		?>
		<div class="wrap">
			<h1><?php echo esc_html( get_admin_page_title() ); ?></h1>
			<p><?php esc_html_e( 'Welcome to the plugin dashboard.', '{{TEXT_DOMAIN}}' ); ?></p>

			<div class="{{TEXT_DOMAIN}}-dashboard">
				<!-- Dashboard content -->
			</div>
		</div>
		<?php
	}

	/**
	 * Render settings page.
	 *
	 * @since 1.0.0
	 */
	public function render_settings_page() {
		if ( ! current_user_can( 'manage_options' ) ) {
			return;
		}

		// Show settings saved message.
		if ( isset( $_GET['settings-updated'] ) ) {
			add_settings_error(
				'{{TEXT_DOMAIN}}_messages',
				'{{TEXT_DOMAIN}}_saved',
				__( 'Settings saved.', '{{TEXT_DOMAIN}}' ),
				'updated'
			);
		}

		settings_errors( '{{TEXT_DOMAIN}}_messages' );
		?>
		<div class="wrap">
			<h1><?php echo esc_html( get_admin_page_title() ); ?></h1>

			<form action="options.php" method="post">
				<?php
				settings_fields( '{{TEXT_DOMAIN}}_settings' );
				do_settings_sections( '{{TEXT_DOMAIN}}-settings' );
				submit_button();
				?>
			</form>
		</div>
		<?php
	}
}
