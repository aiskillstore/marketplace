<?php
/**
 * Custom Taxonomy Registration Template
 *
 * Replace placeholders:
 * - {{TAXONOMY}} → taxonomy slug (e.g., 'property_type')
 * - {{TAXONOMY_NAME}} → singular name (e.g., 'Property Type')
 * - {{TAXONOMY_NAME_PLURAL}} → plural name (e.g., 'Property Types')
 * - {{POST_TYPE}} → associated post type (e.g., 'property')
 * - {{TEXT_DOMAIN}} → theme/plugin text domain
 *
 * @package Theme_Name
 */

// Prevent direct access.
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Register {{TAXONOMY_NAME}} Custom Taxonomy.
 *
 * @since 1.0.0
 */
function theme_name_register_{{TAXONOMY}}_taxonomy() {
	$labels = array(
		'name'                       => _x( '{{TAXONOMY_NAME_PLURAL}}', 'Taxonomy General Name', '{{TEXT_DOMAIN}}' ),
		'singular_name'              => _x( '{{TAXONOMY_NAME}}', 'Taxonomy Singular Name', '{{TEXT_DOMAIN}}' ),
		'menu_name'                  => __( '{{TAXONOMY_NAME_PLURAL}}', '{{TEXT_DOMAIN}}' ),
		'all_items'                  => __( 'All {{TAXONOMY_NAME_PLURAL}}', '{{TEXT_DOMAIN}}' ),
		'parent_item'                => __( 'Parent {{TAXONOMY_NAME}}', '{{TEXT_DOMAIN}}' ),
		'parent_item_colon'          => __( 'Parent {{TAXONOMY_NAME}}:', '{{TEXT_DOMAIN}}' ),
		'new_item_name'              => __( 'New {{TAXONOMY_NAME}} Name', '{{TEXT_DOMAIN}}' ),
		'add_new_item'               => __( 'Add New {{TAXONOMY_NAME}}', '{{TEXT_DOMAIN}}' ),
		'edit_item'                  => __( 'Edit {{TAXONOMY_NAME}}', '{{TEXT_DOMAIN}}' ),
		'update_item'                => __( 'Update {{TAXONOMY_NAME}}', '{{TEXT_DOMAIN}}' ),
		'view_item'                  => __( 'View {{TAXONOMY_NAME}}', '{{TEXT_DOMAIN}}' ),
		'separate_items_with_commas' => __( 'Separate {{TAXONOMY_NAME_PLURAL}} with commas', '{{TEXT_DOMAIN}}' ),
		'add_or_remove_items'        => __( 'Add or remove {{TAXONOMY_NAME_PLURAL}}', '{{TEXT_DOMAIN}}' ),
		'choose_from_most_used'      => __( 'Choose from the most used', '{{TEXT_DOMAIN}}' ),
		'popular_items'              => __( 'Popular {{TAXONOMY_NAME_PLURAL}}', '{{TEXT_DOMAIN}}' ),
		'search_items'               => __( 'Search {{TAXONOMY_NAME_PLURAL}}', '{{TEXT_DOMAIN}}' ),
		'not_found'                  => __( 'Not Found', '{{TEXT_DOMAIN}}' ),
		'no_terms'                   => __( 'No {{TAXONOMY_NAME_PLURAL}}', '{{TEXT_DOMAIN}}' ),
		'items_list'                 => __( '{{TAXONOMY_NAME_PLURAL}} list', '{{TEXT_DOMAIN}}' ),
		'items_list_navigation'      => __( '{{TAXONOMY_NAME_PLURAL}} list navigation', '{{TEXT_DOMAIN}}' ),
		'back_to_items'              => __( '← Back to {{TAXONOMY_NAME_PLURAL}}', '{{TEXT_DOMAIN}}' ),
	);

	$args = array(
		'labels'            => $labels,
		'hierarchical'      => true, // true = category-like, false = tag-like
		'public'            => true,
		'show_ui'           => true,
		'show_admin_column' => true,
		'show_in_nav_menus' => true,
		'show_tagcloud'     => true,
		'show_in_rest'      => true,
		'rest_base'         => '{{TAXONOMY}}',
		'rewrite'           => array(
			'slug'         => '{{TAXONOMY}}',
			'with_front'   => true,
			'hierarchical' => true,
		),
	);

	register_taxonomy( '{{TAXONOMY}}', array( '{{POST_TYPE}}' ), $args );
}
add_action( 'init', 'theme_name_register_{{TAXONOMY}}_taxonomy', 0 );

/**
 * Add default terms on activation.
 *
 * @since 1.0.0
 */
function theme_name_{{TAXONOMY}}_default_terms() {
	// Register taxonomy first.
	theme_name_register_{{TAXONOMY}}_taxonomy();

	// Default terms.
	$default_terms = array(
		'term-one'   => __( 'Term One', '{{TEXT_DOMAIN}}' ),
		'term-two'   => __( 'Term Two', '{{TEXT_DOMAIN}}' ),
		'term-three' => __( 'Term Three', '{{TEXT_DOMAIN}}' ),
	);

	foreach ( $default_terms as $slug => $name ) {
		if ( ! term_exists( $slug, '{{TAXONOMY}}' ) ) {
			wp_insert_term( $name, '{{TAXONOMY}}', array( 'slug' => $slug ) );
		}
	}
}
register_activation_hook( __FILE__, 'theme_name_{{TAXONOMY}}_default_terms' );

/**
 * Add custom fields to taxonomy add form.
 *
 * @since 1.0.0
 */
function theme_name_{{TAXONOMY}}_add_form_fields() {
	?>
	<div class="form-field">
		<label for="{{TAXONOMY}}_icon"><?php esc_html_e( 'Icon', '{{TEXT_DOMAIN}}' ); ?></label>
		<input type="text" name="{{TAXONOMY}}_icon" id="{{TAXONOMY}}_icon" value="">
		<p class="description"><?php esc_html_e( 'Enter a dashicon class (e.g., dashicons-admin-home)', '{{TEXT_DOMAIN}}' ); ?></p>
	</div>

	<div class="form-field">
		<label for="{{TAXONOMY}}_color"><?php esc_html_e( 'Color', '{{TEXT_DOMAIN}}' ); ?></label>
		<input type="color" name="{{TAXONOMY}}_color" id="{{TAXONOMY}}_color" value="#000000">
		<p class="description"><?php esc_html_e( 'Select a color for this term.', '{{TEXT_DOMAIN}}' ); ?></p>
	</div>
	<?php
}
add_action( '{{TAXONOMY}}_add_form_fields', 'theme_name_{{TAXONOMY}}_add_form_fields' );

/**
 * Add custom fields to taxonomy edit form.
 *
 * @since 1.0.0
 *
 * @param WP_Term $term Current taxonomy term object.
 */
function theme_name_{{TAXONOMY}}_edit_form_fields( $term ) {
	$icon  = get_term_meta( $term->term_id, '{{TAXONOMY}}_icon', true );
	$color = get_term_meta( $term->term_id, '{{TAXONOMY}}_color', true );
	?>
	<tr class="form-field">
		<th scope="row">
			<label for="{{TAXONOMY}}_icon"><?php esc_html_e( 'Icon', '{{TEXT_DOMAIN}}' ); ?></label>
		</th>
		<td>
			<input type="text" name="{{TAXONOMY}}_icon" id="{{TAXONOMY}}_icon" value="<?php echo esc_attr( $icon ); ?>">
			<p class="description"><?php esc_html_e( 'Enter a dashicon class (e.g., dashicons-admin-home)', '{{TEXT_DOMAIN}}' ); ?></p>
		</td>
	</tr>

	<tr class="form-field">
		<th scope="row">
			<label for="{{TAXONOMY}}_color"><?php esc_html_e( 'Color', '{{TEXT_DOMAIN}}' ); ?></label>
		</th>
		<td>
			<input type="color" name="{{TAXONOMY}}_color" id="{{TAXONOMY}}_color" value="<?php echo esc_attr( $color ?: '#000000' ); ?>">
			<p class="description"><?php esc_html_e( 'Select a color for this term.', '{{TEXT_DOMAIN}}' ); ?></p>
		</td>
	</tr>
	<?php
}
add_action( '{{TAXONOMY}}_edit_form_fields', 'theme_name_{{TAXONOMY}}_edit_form_fields' );

/**
 * Save custom taxonomy fields.
 *
 * @since 1.0.0
 *
 * @param int $term_id Term ID.
 */
function theme_name_{{TAXONOMY}}_save_fields( $term_id ) {
	if ( isset( $_POST['{{TAXONOMY}}_icon'] ) ) {
		update_term_meta( $term_id, '{{TAXONOMY}}_icon', sanitize_text_field( $_POST['{{TAXONOMY}}_icon'] ) );
	}

	if ( isset( $_POST['{{TAXONOMY}}_color'] ) ) {
		update_term_meta( $term_id, '{{TAXONOMY}}_color', sanitize_hex_color( $_POST['{{TAXONOMY}}_color'] ) );
	}
}
add_action( 'created_{{TAXONOMY}}', 'theme_name_{{TAXONOMY}}_save_fields' );
add_action( 'edited_{{TAXONOMY}}', 'theme_name_{{TAXONOMY}}_save_fields' );

/**
 * Add custom column to taxonomy list.
 *
 * @since 1.0.0
 *
 * @param array $columns Existing columns.
 * @return array Modified columns.
 */
function theme_name_{{TAXONOMY}}_admin_columns( $columns ) {
	$columns['{{TAXONOMY}}_color'] = __( 'Color', '{{TEXT_DOMAIN}}' );
	return $columns;
}
add_filter( 'manage_edit-{{TAXONOMY}}_columns', 'theme_name_{{TAXONOMY}}_admin_columns' );

/**
 * Populate custom column content.
 *
 * @since 1.0.0
 *
 * @param string $content     Column content.
 * @param string $column_name Column name.
 * @param int    $term_id     Term ID.
 * @return string Modified content.
 */
function theme_name_{{TAXONOMY}}_admin_column_content( $content, $column_name, $term_id ) {
	if ( '{{TAXONOMY}}_color' === $column_name ) {
		$color = get_term_meta( $term_id, '{{TAXONOMY}}_color', true );
		if ( $color ) {
			$content = sprintf(
				'<span style="display:inline-block;width:20px;height:20px;background:%s;border-radius:3px;"></span>',
				esc_attr( $color )
			);
		}
	}

	return $content;
}
add_filter( 'manage_{{TAXONOMY}}_custom_column', 'theme_name_{{TAXONOMY}}_admin_column_content', 10, 3 );
