<?php
/**
 * Meta Box Registration Template
 *
 * Replace placeholders:
 * - {{META_BOX_ID}} → meta box ID (e.g., 'property_details')
 * - {{META_BOX_TITLE}} → meta box title (e.g., 'Property Details')
 * - {{POST_TYPE}} → post type slug (e.g., 'property')
 * - {{TEXT_DOMAIN}} → theme/plugin text domain
 * - {{PREFIX}} → meta key prefix (e.g., '_property')
 *
 * @package Theme_Name
 */

// Prevent direct access.
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Register meta box.
 *
 * @since 1.0.0
 */
function theme_name_add_{{META_BOX_ID}}_meta_box() {
	add_meta_box(
		'{{META_BOX_ID}}',
		__( '{{META_BOX_TITLE}}', '{{TEXT_DOMAIN}}' ),
		'theme_name_render_{{META_BOX_ID}}_meta_box',
		'{{POST_TYPE}}',
		'normal', // normal, side, advanced
		'high'    // high, core, default, low
	);
}
add_action( 'add_meta_boxes', 'theme_name_add_{{META_BOX_ID}}_meta_box' );

/**
 * Render meta box content.
 *
 * @since 1.0.0
 *
 * @param WP_Post $post Post object.
 */
function theme_name_render_{{META_BOX_ID}}_meta_box( $post ) {
	// Add nonce for security.
	wp_nonce_field( '{{META_BOX_ID}}_save', '{{META_BOX_ID}}_nonce' );

	// Get existing values.
	$text_field     = get_post_meta( $post->ID, '{{PREFIX}}_text_field', true );
	$textarea_field = get_post_meta( $post->ID, '{{PREFIX}}_textarea', true );
	$number_field   = get_post_meta( $post->ID, '{{PREFIX}}_number', true );
	$select_field   = get_post_meta( $post->ID, '{{PREFIX}}_select', true );
	$checkbox_field = get_post_meta( $post->ID, '{{PREFIX}}_checkbox', true );
	$radio_field    = get_post_meta( $post->ID, '{{PREFIX}}_radio', true );
	$date_field     = get_post_meta( $post->ID, '{{PREFIX}}_date', true );
	$color_field    = get_post_meta( $post->ID, '{{PREFIX}}_color', true );
	$url_field      = get_post_meta( $post->ID, '{{PREFIX}}_url', true );
	$email_field    = get_post_meta( $post->ID, '{{PREFIX}}_email', true );
	?>

	<style>
		.{{META_BOX_ID}}-field {
			margin-bottom: 15px;
		}
		.{{META_BOX_ID}}-field label {
			display: block;
			font-weight: 600;
			margin-bottom: 5px;
		}
		.{{META_BOX_ID}}-field input[type="text"],
		.{{META_BOX_ID}}-field input[type="number"],
		.{{META_BOX_ID}}-field input[type="url"],
		.{{META_BOX_ID}}-field input[type="email"],
		.{{META_BOX_ID}}-field input[type="date"],
		.{{META_BOX_ID}}-field select,
		.{{META_BOX_ID}}-field textarea {
			width: 100%;
			max-width: 400px;
		}
		.{{META_BOX_ID}}-field textarea {
			height: 100px;
		}
		.{{META_BOX_ID}}-field .description {
			font-style: italic;
			color: #666;
			margin-top: 5px;
		}
		.{{META_BOX_ID}}-field-inline label {
			display: inline;
			font-weight: normal;
			margin-left: 5px;
		}
	</style>

	<div class="{{META_BOX_ID}}-fields">
		<!-- Text Field -->
		<div class="{{META_BOX_ID}}-field">
			<label for="{{PREFIX}}_text_field"><?php esc_html_e( 'Text Field', '{{TEXT_DOMAIN}}' ); ?></label>
			<input type="text" id="{{PREFIX}}_text_field" name="{{PREFIX}}_text_field" value="<?php echo esc_attr( $text_field ); ?>">
			<p class="description"><?php esc_html_e( 'Enter some text.', '{{TEXT_DOMAIN}}' ); ?></p>
		</div>

		<!-- Textarea -->
		<div class="{{META_BOX_ID}}-field">
			<label for="{{PREFIX}}_textarea"><?php esc_html_e( 'Textarea', '{{TEXT_DOMAIN}}' ); ?></label>
			<textarea id="{{PREFIX}}_textarea" name="{{PREFIX}}_textarea"><?php echo esc_textarea( $textarea_field ); ?></textarea>
			<p class="description"><?php esc_html_e( 'Enter a longer description.', '{{TEXT_DOMAIN}}' ); ?></p>
		</div>

		<!-- Number Field -->
		<div class="{{META_BOX_ID}}-field">
			<label for="{{PREFIX}}_number"><?php esc_html_e( 'Number', '{{TEXT_DOMAIN}}' ); ?></label>
			<input type="number" id="{{PREFIX}}_number" name="{{PREFIX}}_number" value="<?php echo esc_attr( $number_field ); ?>" min="0" step="1">
			<p class="description"><?php esc_html_e( 'Enter a number.', '{{TEXT_DOMAIN}}' ); ?></p>
		</div>

		<!-- Select Field -->
		<div class="{{META_BOX_ID}}-field">
			<label for="{{PREFIX}}_select"><?php esc_html_e( 'Select', '{{TEXT_DOMAIN}}' ); ?></label>
			<select id="{{PREFIX}}_select" name="{{PREFIX}}_select">
				<option value=""><?php esc_html_e( '— Select —', '{{TEXT_DOMAIN}}' ); ?></option>
				<option value="option1" <?php selected( $select_field, 'option1' ); ?>><?php esc_html_e( 'Option 1', '{{TEXT_DOMAIN}}' ); ?></option>
				<option value="option2" <?php selected( $select_field, 'option2' ); ?>><?php esc_html_e( 'Option 2', '{{TEXT_DOMAIN}}' ); ?></option>
				<option value="option3" <?php selected( $select_field, 'option3' ); ?>><?php esc_html_e( 'Option 3', '{{TEXT_DOMAIN}}' ); ?></option>
			</select>
		</div>

		<!-- Checkbox -->
		<div class="{{META_BOX_ID}}-field {{META_BOX_ID}}-field-inline">
			<input type="checkbox" id="{{PREFIX}}_checkbox" name="{{PREFIX}}_checkbox" value="1" <?php checked( $checkbox_field, '1' ); ?>>
			<label for="{{PREFIX}}_checkbox"><?php esc_html_e( 'Enable this option', '{{TEXT_DOMAIN}}' ); ?></label>
		</div>

		<!-- Radio Buttons -->
		<div class="{{META_BOX_ID}}-field">
			<label><?php esc_html_e( 'Radio Options', '{{TEXT_DOMAIN}}' ); ?></label>
			<div class="{{META_BOX_ID}}-field-inline">
				<input type="radio" id="{{PREFIX}}_radio_1" name="{{PREFIX}}_radio" value="radio1" <?php checked( $radio_field, 'radio1' ); ?>>
				<label for="{{PREFIX}}_radio_1"><?php esc_html_e( 'Radio 1', '{{TEXT_DOMAIN}}' ); ?></label>
			</div>
			<div class="{{META_BOX_ID}}-field-inline">
				<input type="radio" id="{{PREFIX}}_radio_2" name="{{PREFIX}}_radio" value="radio2" <?php checked( $radio_field, 'radio2' ); ?>>
				<label for="{{PREFIX}}_radio_2"><?php esc_html_e( 'Radio 2', '{{TEXT_DOMAIN}}' ); ?></label>
			</div>
		</div>

		<!-- Date Field -->
		<div class="{{META_BOX_ID}}-field">
			<label for="{{PREFIX}}_date"><?php esc_html_e( 'Date', '{{TEXT_DOMAIN}}' ); ?></label>
			<input type="date" id="{{PREFIX}}_date" name="{{PREFIX}}_date" value="<?php echo esc_attr( $date_field ); ?>">
		</div>

		<!-- Color Picker -->
		<div class="{{META_BOX_ID}}-field">
			<label for="{{PREFIX}}_color"><?php esc_html_e( 'Color', '{{TEXT_DOMAIN}}' ); ?></label>
			<input type="color" id="{{PREFIX}}_color" name="{{PREFIX}}_color" value="<?php echo esc_attr( $color_field ?: '#000000' ); ?>">
		</div>

		<!-- URL Field -->
		<div class="{{META_BOX_ID}}-field">
			<label for="{{PREFIX}}_url"><?php esc_html_e( 'URL', '{{TEXT_DOMAIN}}' ); ?></label>
			<input type="url" id="{{PREFIX}}_url" name="{{PREFIX}}_url" value="<?php echo esc_url( $url_field ); ?>" placeholder="https://example.com">
		</div>

		<!-- Email Field -->
		<div class="{{META_BOX_ID}}-field">
			<label for="{{PREFIX}}_email"><?php esc_html_e( 'Email', '{{TEXT_DOMAIN}}' ); ?></label>
			<input type="email" id="{{PREFIX}}_email" name="{{PREFIX}}_email" value="<?php echo esc_attr( $email_field ); ?>" placeholder="email@example.com">
		</div>
	</div>

	<?php
}

/**
 * Save meta box data.
 *
 * @since 1.0.0
 *
 * @param int $post_id Post ID.
 */
function theme_name_save_{{META_BOX_ID}}_meta_box( $post_id ) {
	// Check if nonce is set.
	if ( ! isset( $_POST['{{META_BOX_ID}}_nonce'] ) ) {
		return;
	}

	// Verify nonce.
	if ( ! wp_verify_nonce( $_POST['{{META_BOX_ID}}_nonce'], '{{META_BOX_ID}}_save' ) ) {
		return;
	}

	// Check autosave.
	if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) {
		return;
	}

	// Check permissions.
	if ( ! current_user_can( 'edit_post', $post_id ) ) {
		return;
	}

	// Define fields and their sanitization callbacks.
	$fields = array(
		'{{PREFIX}}_text_field' => 'sanitize_text_field',
		'{{PREFIX}}_textarea'   => 'sanitize_textarea_field',
		'{{PREFIX}}_number'     => 'absint',
		'{{PREFIX}}_select'     => 'sanitize_key',
		'{{PREFIX}}_checkbox'   => 'absint',
		'{{PREFIX}}_radio'      => 'sanitize_key',
		'{{PREFIX}}_date'       => 'sanitize_text_field',
		'{{PREFIX}}_color'      => 'sanitize_hex_color',
		'{{PREFIX}}_url'        => 'esc_url_raw',
		'{{PREFIX}}_email'      => 'sanitize_email',
	);

	// Save each field.
	foreach ( $fields as $field => $sanitize_callback ) {
		if ( isset( $_POST[ $field ] ) ) {
			$value = call_user_func( $sanitize_callback, $_POST[ $field ] );
			update_post_meta( $post_id, $field, $value );
		} else {
			// Handle unchecked checkboxes.
			if ( '{{PREFIX}}_checkbox' === $field ) {
				delete_post_meta( $post_id, $field );
			}
		}
	}
}
add_action( 'save_post_{{POST_TYPE}}', 'theme_name_save_{{META_BOX_ID}}_meta_box' );

/**
 * Register meta fields for REST API.
 *
 * @since 1.0.0
 */
function theme_name_register_{{META_BOX_ID}}_meta() {
	$fields = array(
		'{{PREFIX}}_text_field' => 'string',
		'{{PREFIX}}_textarea'   => 'string',
		'{{PREFIX}}_number'     => 'integer',
		'{{PREFIX}}_select'     => 'string',
		'{{PREFIX}}_checkbox'   => 'boolean',
		'{{PREFIX}}_radio'      => 'string',
		'{{PREFIX}}_date'       => 'string',
		'{{PREFIX}}_color'      => 'string',
		'{{PREFIX}}_url'        => 'string',
		'{{PREFIX}}_email'      => 'string',
	);

	foreach ( $fields as $field => $type ) {
		register_post_meta(
			'{{POST_TYPE}}',
			$field,
			array(
				'type'         => $type,
				'single'       => true,
				'show_in_rest' => true,
			)
		);
	}
}
add_action( 'init', 'theme_name_register_{{META_BOX_ID}}_meta' );
