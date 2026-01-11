<?php
/**
 * Custom Post Type Registration Template
 *
 * Replace placeholders:
 * - {{POST_TYPE}} → post type slug (e.g., 'property')
 * - {{POST_TYPE_NAME}} → singular name (e.g., 'Property')
 * - {{POST_TYPE_NAME_PLURAL}} → plural name (e.g., 'Properties')
 * - {{TEXT_DOMAIN}} → theme/plugin text domain
 * - {{MENU_ICON}} → dashicon name (e.g., 'dashicons-building')
 *
 * @package Theme_Name
 */

// Prevent direct access.
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Register {{POST_TYPE_NAME}} Custom Post Type.
 *
 * @since 1.0.0
 */
function theme_name_register_{{POST_TYPE}}_cpt() {
	$labels = array(
		'name'                  => _x( '{{POST_TYPE_NAME_PLURAL}}', 'Post Type General Name', '{{TEXT_DOMAIN}}' ),
		'singular_name'         => _x( '{{POST_TYPE_NAME}}', 'Post Type Singular Name', '{{TEXT_DOMAIN}}' ),
		'menu_name'             => __( '{{POST_TYPE_NAME_PLURAL}}', '{{TEXT_DOMAIN}}' ),
		'name_admin_bar'        => __( '{{POST_TYPE_NAME}}', '{{TEXT_DOMAIN}}' ),
		'archives'              => __( '{{POST_TYPE_NAME}} Archives', '{{TEXT_DOMAIN}}' ),
		'attributes'            => __( '{{POST_TYPE_NAME}} Attributes', '{{TEXT_DOMAIN}}' ),
		'parent_item_colon'     => __( 'Parent {{POST_TYPE_NAME}}:', '{{TEXT_DOMAIN}}' ),
		'all_items'             => __( 'All {{POST_TYPE_NAME_PLURAL}}', '{{TEXT_DOMAIN}}' ),
		'add_new_item'          => __( 'Add New {{POST_TYPE_NAME}}', '{{TEXT_DOMAIN}}' ),
		'add_new'               => __( 'Add New', '{{TEXT_DOMAIN}}' ),
		'new_item'              => __( 'New {{POST_TYPE_NAME}}', '{{TEXT_DOMAIN}}' ),
		'edit_item'             => __( 'Edit {{POST_TYPE_NAME}}', '{{TEXT_DOMAIN}}' ),
		'update_item'           => __( 'Update {{POST_TYPE_NAME}}', '{{TEXT_DOMAIN}}' ),
		'view_item'             => __( 'View {{POST_TYPE_NAME}}', '{{TEXT_DOMAIN}}' ),
		'view_items'            => __( 'View {{POST_TYPE_NAME_PLURAL}}', '{{TEXT_DOMAIN}}' ),
		'search_items'          => __( 'Search {{POST_TYPE_NAME_PLURAL}}', '{{TEXT_DOMAIN}}' ),
		'not_found'             => __( 'No {{POST_TYPE_NAME_PLURAL}} found', '{{TEXT_DOMAIN}}' ),
		'not_found_in_trash'    => __( 'No {{POST_TYPE_NAME_PLURAL}} found in Trash', '{{TEXT_DOMAIN}}' ),
		'featured_image'        => __( 'Featured Image', '{{TEXT_DOMAIN}}' ),
		'set_featured_image'    => __( 'Set featured image', '{{TEXT_DOMAIN}}' ),
		'remove_featured_image' => __( 'Remove featured image', '{{TEXT_DOMAIN}}' ),
		'use_featured_image'    => __( 'Use as featured image', '{{TEXT_DOMAIN}}' ),
		'insert_into_item'      => __( 'Insert into {{POST_TYPE_NAME}}', '{{TEXT_DOMAIN}}' ),
		'uploaded_to_this_item' => __( 'Uploaded to this {{POST_TYPE_NAME}}', '{{TEXT_DOMAIN}}' ),
		'items_list'            => __( '{{POST_TYPE_NAME_PLURAL}} list', '{{TEXT_DOMAIN}}' ),
		'items_list_navigation' => __( '{{POST_TYPE_NAME_PLURAL}} list navigation', '{{TEXT_DOMAIN}}' ),
		'filter_items_list'     => __( 'Filter {{POST_TYPE_NAME_PLURAL}} list', '{{TEXT_DOMAIN}}' ),
	);

	$args = array(
		'label'               => __( '{{POST_TYPE_NAME}}', '{{TEXT_DOMAIN}}' ),
		'description'         => __( '{{POST_TYPE_NAME}} post type.', '{{TEXT_DOMAIN}}' ),
		'labels'              => $labels,
		'supports'            => array( 'title', 'editor', 'thumbnail', 'excerpt', 'custom-fields', 'revisions' ),
		'taxonomies'          => array(),
		'hierarchical'        => false,
		'public'              => true,
		'show_ui'             => true,
		'show_in_menu'        => true,
		'menu_position'       => 5,
		'menu_icon'           => '{{MENU_ICON}}',
		'show_in_admin_bar'   => true,
		'show_in_nav_menus'   => true,
		'can_export'          => true,
		'has_archive'         => true,
		'exclude_from_search' => false,
		'publicly_queryable'  => true,
		'capability_type'     => 'post',
		'show_in_rest'        => true,
		'rest_base'           => '{{POST_TYPE}}s',
	);

	register_post_type( '{{POST_TYPE}}', $args );
}
add_action( 'init', 'theme_name_register_{{POST_TYPE}}_cpt', 0 );

/**
 * Flush rewrite rules on theme activation.
 *
 * @since 1.0.0
 */
function theme_name_{{POST_TYPE}}_rewrite_flush() {
	theme_name_register_{{POST_TYPE}}_cpt();
	flush_rewrite_rules();
}
register_activation_hook( __FILE__, 'theme_name_{{POST_TYPE}}_rewrite_flush' );

/**
 * Add custom admin columns.
 *
 * @since 1.0.0
 *
 * @param array $columns Existing columns.
 * @return array Modified columns.
 */
function theme_name_{{POST_TYPE}}_admin_columns( $columns ) {
	$new_columns = array();

	foreach ( $columns as $key => $value ) {
		$new_columns[ $key ] = $value;

		// Add columns after title.
		if ( 'title' === $key ) {
			$new_columns['{{POST_TYPE}}_featured'] = __( 'Featured', '{{TEXT_DOMAIN}}' );
		}
	}

	// Add thumbnail at start.
	$new_columns = array_merge(
		array( '{{POST_TYPE}}_thumb' => __( 'Image', '{{TEXT_DOMAIN}}' ) ),
		$new_columns
	);

	return $new_columns;
}
add_filter( 'manage_{{POST_TYPE}}_posts_columns', 'theme_name_{{POST_TYPE}}_admin_columns' );

/**
 * Populate custom admin columns.
 *
 * @since 1.0.0
 *
 * @param string $column  Column name.
 * @param int    $post_id Post ID.
 */
function theme_name_{{POST_TYPE}}_admin_column_content( $column, $post_id ) {
	switch ( $column ) {
		case '{{POST_TYPE}}_thumb':
			if ( has_post_thumbnail( $post_id ) ) {
				echo get_the_post_thumbnail( $post_id, array( 50, 50 ) );
			} else {
				echo '—';
			}
			break;

		case '{{POST_TYPE}}_featured':
			$featured = get_post_meta( $post_id, '_featured', true );
			echo $featured ? '★' : '—';
			break;
	}
}
add_action( 'manage_{{POST_TYPE}}_posts_custom_column', 'theme_name_{{POST_TYPE}}_admin_column_content', 10, 2 );

/**
 * Make columns sortable.
 *
 * @since 1.0.0
 *
 * @param array $columns Sortable columns.
 * @return array Modified sortable columns.
 */
function theme_name_{{POST_TYPE}}_sortable_columns( $columns ) {
	$columns['{{POST_TYPE}}_featured'] = 'featured';
	return $columns;
}
add_filter( 'manage_edit-{{POST_TYPE}}_sortable_columns', 'theme_name_{{POST_TYPE}}_sortable_columns' );
