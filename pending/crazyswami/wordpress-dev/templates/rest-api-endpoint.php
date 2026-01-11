<?php
/**
 * Custom REST API Endpoint Template
 *
 * Replace placeholders:
 * - {{NAMESPACE}} → API namespace (e.g., 'theme/v1')
 * - {{ROUTE}} → route path (e.g., 'properties')
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
 * Register custom REST API routes.
 *
 * @since 1.0.0
 */
function theme_name_register_rest_routes() {
	// GET /{{NAMESPACE}}/{{ROUTE}}
	register_rest_route(
		'{{NAMESPACE}}',
		'/{{ROUTE}}',
		array(
			'methods'             => WP_REST_Server::READABLE, // GET
			'callback'            => 'theme_name_get_{{ROUTE}}',
			'permission_callback' => '__return_true', // Public
			'args'                => array(
				'per_page' => array(
					'default'           => 10,
					'validate_callback' => function( $param ) {
						return is_numeric( $param ) && $param > 0 && $param <= 100;
					},
					'sanitize_callback' => 'absint',
				),
				'page'     => array(
					'default'           => 1,
					'validate_callback' => function( $param ) {
						return is_numeric( $param ) && $param > 0;
					},
					'sanitize_callback' => 'absint',
				),
				'orderby'  => array(
					'default'           => 'date',
					'validate_callback' => function( $param ) {
						return in_array( $param, array( 'date', 'title', 'modified', 'rand' ), true );
					},
					'sanitize_callback' => 'sanitize_key',
				),
				'order'    => array(
					'default'           => 'DESC',
					'validate_callback' => function( $param ) {
						return in_array( strtoupper( $param ), array( 'ASC', 'DESC' ), true );
					},
					'sanitize_callback' => function( $param ) {
						return strtoupper( sanitize_key( $param ) );
					},
				),
			),
		)
	);

	// GET /{{NAMESPACE}}/{{ROUTE}}/(?P<id>\d+)
	register_rest_route(
		'{{NAMESPACE}}',
		'/{{ROUTE}}/(?P<id>\d+)',
		array(
			'methods'             => WP_REST_Server::READABLE, // GET
			'callback'            => 'theme_name_get_{{ROUTE}}_single',
			'permission_callback' => '__return_true', // Public
			'args'                => array(
				'id' => array(
					'required'          => true,
					'validate_callback' => function( $param ) {
						return is_numeric( $param ) && $param > 0;
					},
					'sanitize_callback' => 'absint',
				),
			),
		)
	);

	// POST /{{NAMESPACE}}/{{ROUTE}}
	register_rest_route(
		'{{NAMESPACE}}',
		'/{{ROUTE}}',
		array(
			'methods'             => WP_REST_Server::CREATABLE, // POST
			'callback'            => 'theme_name_create_{{ROUTE}}',
			'permission_callback' => function() {
				return current_user_can( 'publish_posts' );
			},
			'args'                => array(
				'title'   => array(
					'required'          => true,
					'sanitize_callback' => 'sanitize_text_field',
				),
				'content' => array(
					'required'          => false,
					'sanitize_callback' => 'wp_kses_post',
				),
				'status'  => array(
					'default'           => 'draft',
					'validate_callback' => function( $param ) {
						return in_array( $param, array( 'draft', 'publish', 'pending' ), true );
					},
					'sanitize_callback' => 'sanitize_key',
				),
			),
		)
	);

	// PUT/PATCH /{{NAMESPACE}}/{{ROUTE}}/(?P<id>\d+)
	register_rest_route(
		'{{NAMESPACE}}',
		'/{{ROUTE}}/(?P<id>\d+)',
		array(
			'methods'             => WP_REST_Server::EDITABLE, // PUT, PATCH
			'callback'            => 'theme_name_update_{{ROUTE}}',
			'permission_callback' => function( $request ) {
				return current_user_can( 'edit_post', $request['id'] );
			},
			'args'                => array(
				'id'      => array(
					'required'          => true,
					'validate_callback' => function( $param ) {
						return is_numeric( $param ) && $param > 0;
					},
					'sanitize_callback' => 'absint',
				),
				'title'   => array(
					'sanitize_callback' => 'sanitize_text_field',
				),
				'content' => array(
					'sanitize_callback' => 'wp_kses_post',
				),
			),
		)
	);

	// DELETE /{{NAMESPACE}}/{{ROUTE}}/(?P<id>\d+)
	register_rest_route(
		'{{NAMESPACE}}',
		'/{{ROUTE}}/(?P<id>\d+)',
		array(
			'methods'             => WP_REST_Server::DELETABLE, // DELETE
			'callback'            => 'theme_name_delete_{{ROUTE}}',
			'permission_callback' => function( $request ) {
				return current_user_can( 'delete_post', $request['id'] );
			},
			'args'                => array(
				'id'    => array(
					'required'          => true,
					'validate_callback' => function( $param ) {
						return is_numeric( $param ) && $param > 0;
					},
					'sanitize_callback' => 'absint',
				),
				'force' => array(
					'default'           => false,
					'sanitize_callback' => 'rest_sanitize_boolean',
				),
			),
		)
	);
}
add_action( 'rest_api_init', 'theme_name_register_rest_routes' );

/**
 * GET callback - List items.
 *
 * @since 1.0.0
 *
 * @param WP_REST_Request $request Request object.
 * @return WP_REST_Response Response object.
 */
function theme_name_get_{{ROUTE}}( $request ) {
	$args = array(
		'post_type'      => '{{POST_TYPE}}',
		'posts_per_page' => $request->get_param( 'per_page' ),
		'paged'          => $request->get_param( 'page' ),
		'orderby'        => $request->get_param( 'orderby' ),
		'order'          => $request->get_param( 'order' ),
		'post_status'    => 'publish',
	);

	$query = new WP_Query( $args );
	$items = array();

	foreach ( $query->posts as $post ) {
		$items[] = theme_name_prepare_{{ROUTE}}_for_response( $post );
	}

	$response = rest_ensure_response( $items );

	// Add pagination headers.
	$response->header( 'X-WP-Total', $query->found_posts );
	$response->header( 'X-WP-TotalPages', $query->max_num_pages );

	return $response;
}

/**
 * GET callback - Single item.
 *
 * @since 1.0.0
 *
 * @param WP_REST_Request $request Request object.
 * @return WP_REST_Response|WP_Error Response object or error.
 */
function theme_name_get_{{ROUTE}}_single( $request ) {
	$post = get_post( $request['id'] );

	if ( ! $post || '{{POST_TYPE}}' !== $post->post_type ) {
		return new WP_Error(
			'not_found',
			__( 'Item not found.', '{{TEXT_DOMAIN}}' ),
			array( 'status' => 404 )
		);
	}

	// Check if post is published or user can read it.
	if ( 'publish' !== $post->post_status && ! current_user_can( 'read_post', $post->ID ) ) {
		return new WP_Error(
			'forbidden',
			__( 'You do not have permission to view this item.', '{{TEXT_DOMAIN}}' ),
			array( 'status' => 403 )
		);
	}

	return rest_ensure_response( theme_name_prepare_{{ROUTE}}_for_response( $post ) );
}

/**
 * POST callback - Create item.
 *
 * @since 1.0.0
 *
 * @param WP_REST_Request $request Request object.
 * @return WP_REST_Response|WP_Error Response object or error.
 */
function theme_name_create_{{ROUTE}}( $request ) {
	$post_data = array(
		'post_type'    => '{{POST_TYPE}}',
		'post_title'   => $request->get_param( 'title' ),
		'post_content' => $request->get_param( 'content' ) ?: '',
		'post_status'  => $request->get_param( 'status' ),
		'post_author'  => get_current_user_id(),
	);

	$post_id = wp_insert_post( $post_data, true );

	if ( is_wp_error( $post_id ) ) {
		return new WP_Error(
			'create_failed',
			$post_id->get_error_message(),
			array( 'status' => 500 )
		);
	}

	// Save custom meta fields.
	$meta_fields = array( 'price', 'location', 'featured' );
	foreach ( $meta_fields as $field ) {
		if ( $request->has_param( $field ) ) {
			update_post_meta( $post_id, "_{$field}", $request->get_param( $field ) );
		}
	}

	$post = get_post( $post_id );
	$response = rest_ensure_response( theme_name_prepare_{{ROUTE}}_for_response( $post ) );
	$response->set_status( 201 );
	$response->header( 'Location', rest_url( sprintf( '{{NAMESPACE}}/{{ROUTE}}/%d', $post_id ) ) );

	return $response;
}

/**
 * PUT/PATCH callback - Update item.
 *
 * @since 1.0.0
 *
 * @param WP_REST_Request $request Request object.
 * @return WP_REST_Response|WP_Error Response object or error.
 */
function theme_name_update_{{ROUTE}}( $request ) {
	$post = get_post( $request['id'] );

	if ( ! $post || '{{POST_TYPE}}' !== $post->post_type ) {
		return new WP_Error(
			'not_found',
			__( 'Item not found.', '{{TEXT_DOMAIN}}' ),
			array( 'status' => 404 )
		);
	}

	$post_data = array( 'ID' => $post->ID );

	if ( $request->has_param( 'title' ) ) {
		$post_data['post_title'] = $request->get_param( 'title' );
	}

	if ( $request->has_param( 'content' ) ) {
		$post_data['post_content'] = $request->get_param( 'content' );
	}

	if ( $request->has_param( 'status' ) ) {
		$post_data['post_status'] = $request->get_param( 'status' );
	}

	$result = wp_update_post( $post_data, true );

	if ( is_wp_error( $result ) ) {
		return new WP_Error(
			'update_failed',
			$result->get_error_message(),
			array( 'status' => 500 )
		);
	}

	// Update custom meta fields.
	$meta_fields = array( 'price', 'location', 'featured' );
	foreach ( $meta_fields as $field ) {
		if ( $request->has_param( $field ) ) {
			update_post_meta( $post->ID, "_{$field}", $request->get_param( $field ) );
		}
	}

	$post = get_post( $post->ID );
	return rest_ensure_response( theme_name_prepare_{{ROUTE}}_for_response( $post ) );
}

/**
 * DELETE callback - Delete item.
 *
 * @since 1.0.0
 *
 * @param WP_REST_Request $request Request object.
 * @return WP_REST_Response|WP_Error Response object or error.
 */
function theme_name_delete_{{ROUTE}}( $request ) {
	$post = get_post( $request['id'] );

	if ( ! $post || '{{POST_TYPE}}' !== $post->post_type ) {
		return new WP_Error(
			'not_found',
			__( 'Item not found.', '{{TEXT_DOMAIN}}' ),
			array( 'status' => 404 )
		);
	}

	$force = $request->get_param( 'force' );

	// Get response before deleting.
	$response_data = theme_name_prepare_{{ROUTE}}_for_response( $post );
	$response_data['deleted'] = true;

	if ( $force ) {
		$result = wp_delete_post( $post->ID, true );
	} else {
		$result = wp_trash_post( $post->ID );
	}

	if ( ! $result ) {
		return new WP_Error(
			'delete_failed',
			__( 'Failed to delete item.', '{{TEXT_DOMAIN}}' ),
			array( 'status' => 500 )
		);
	}

	return rest_ensure_response( $response_data );
}

/**
 * Prepare item for response.
 *
 * @since 1.0.0
 *
 * @param WP_Post $post Post object.
 * @return array Prepared item data.
 */
function theme_name_prepare_{{ROUTE}}_for_response( $post ) {
	$data = array(
		'id'            => $post->ID,
		'title'         => $post->post_title,
		'slug'          => $post->post_name,
		'content'       => apply_filters( 'the_content', $post->post_content ),
		'excerpt'       => get_the_excerpt( $post ),
		'status'        => $post->post_status,
		'date'          => mysql_to_rfc3339( $post->post_date ),
		'date_gmt'      => mysql_to_rfc3339( $post->post_date_gmt ),
		'modified'      => mysql_to_rfc3339( $post->post_modified ),
		'modified_gmt'  => mysql_to_rfc3339( $post->post_modified_gmt ),
		'author'        => (int) $post->post_author,
		'featured_media' => (int) get_post_thumbnail_id( $post ),
		'link'          => get_permalink( $post ),
		'meta'          => array(
			'price'    => get_post_meta( $post->ID, '_price', true ),
			'location' => get_post_meta( $post->ID, '_location', true ),
			'featured' => (bool) get_post_meta( $post->ID, '_featured', true ),
		),
	);

	// Add featured image URL if set.
	if ( $data['featured_media'] ) {
		$data['featured_media_url'] = wp_get_attachment_image_url( $data['featured_media'], 'large' );
	}

	// Add terms if taxonomies exist.
	$taxonomies = get_object_taxonomies( '{{POST_TYPE}}' );
	if ( $taxonomies ) {
		$data['terms'] = array();
		foreach ( $taxonomies as $taxonomy ) {
			$terms = get_the_terms( $post, $taxonomy );
			$data['terms'][ $taxonomy ] = $terms ? wp_list_pluck( $terms, 'name' ) : array();
		}
	}

	return $data;
}

/**
 * Add custom meta to REST response for built-in endpoint.
 *
 * @since 1.0.0
 */
function theme_name_register_{{ROUTE}}_rest_fields() {
	register_rest_field(
		'{{POST_TYPE}}',
		'custom_meta',
		array(
			'get_callback'    => function( $object ) {
				return array(
					'price'    => get_post_meta( $object['id'], '_price', true ),
					'location' => get_post_meta( $object['id'], '_location', true ),
					'featured' => (bool) get_post_meta( $object['id'], '_featured', true ),
				);
			},
			'update_callback' => function( $value, $object ) {
				if ( isset( $value['price'] ) ) {
					update_post_meta( $object->ID, '_price', sanitize_text_field( $value['price'] ) );
				}
				if ( isset( $value['location'] ) ) {
					update_post_meta( $object->ID, '_location', sanitize_text_field( $value['location'] ) );
				}
				if ( isset( $value['featured'] ) ) {
					update_post_meta( $object->ID, '_featured', (bool) $value['featured'] );
				}
			},
			'schema'          => array(
				'type'        => 'object',
				'description' => __( 'Custom meta fields.', '{{TEXT_DOMAIN}}' ),
				'properties'  => array(
					'price'    => array( 'type' => 'string' ),
					'location' => array( 'type' => 'string' ),
					'featured' => array( 'type' => 'boolean' ),
				),
			),
		)
	);
}
add_action( 'rest_api_init', 'theme_name_register_{{ROUTE}}_rest_fields' );
