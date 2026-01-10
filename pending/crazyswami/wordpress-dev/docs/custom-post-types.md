# Custom Post Types Guide

Complete reference for registering and managing custom post types in WordPress.

## Basic Registration

### Minimal Example

```php
/**
 * Register Property custom post type.
 */
function theme_name_register_property_cpt() {
	register_post_type('property', array(
		'labels'       => array(
			'name'          => __('Properties', 'theme-name'),
			'singular_name' => __('Property', 'theme-name'),
		),
		'public'       => true,
		'has_archive'  => true,
		'rewrite'      => array('slug' => 'properties'),
		'supports'     => array('title', 'editor', 'thumbnail'),
		'show_in_rest' => true,
	));
}
add_action('init', 'theme_name_register_property_cpt');
```

### Complete Example with All Labels

```php
/**
 * Register Property custom post type with full configuration.
 */
function theme_name_register_property_cpt() {
	$labels = array(
		'name'                  => _x('Properties', 'Post Type General Name', 'theme-name'),
		'singular_name'         => _x('Property', 'Post Type Singular Name', 'theme-name'),
		'menu_name'             => __('Properties', 'theme-name'),
		'name_admin_bar'        => __('Property', 'theme-name'),
		'archives'              => __('Property Archives', 'theme-name'),
		'attributes'            => __('Property Attributes', 'theme-name'),
		'parent_item_colon'     => __('Parent Property:', 'theme-name'),
		'all_items'             => __('All Properties', 'theme-name'),
		'add_new_item'          => __('Add New Property', 'theme-name'),
		'add_new'               => __('Add New', 'theme-name'),
		'new_item'              => __('New Property', 'theme-name'),
		'edit_item'             => __('Edit Property', 'theme-name'),
		'update_item'           => __('Update Property', 'theme-name'),
		'view_item'             => __('View Property', 'theme-name'),
		'view_items'            => __('View Properties', 'theme-name'),
		'search_items'          => __('Search Properties', 'theme-name'),
		'not_found'             => __('No properties found', 'theme-name'),
		'not_found_in_trash'    => __('No properties found in Trash', 'theme-name'),
		'featured_image'        => __('Featured Image', 'theme-name'),
		'set_featured_image'    => __('Set featured image', 'theme-name'),
		'remove_featured_image' => __('Remove featured image', 'theme-name'),
		'use_featured_image'    => __('Use as featured image', 'theme-name'),
		'insert_into_item'      => __('Insert into property', 'theme-name'),
		'uploaded_to_this_item' => __('Uploaded to this property', 'theme-name'),
		'items_list'            => __('Properties list', 'theme-name'),
		'items_list_navigation' => __('Properties list navigation', 'theme-name'),
		'filter_items_list'     => __('Filter properties list', 'theme-name'),
	);

	$args = array(
		'label'               => __('Property', 'theme-name'),
		'description'         => __('Real estate property listings', 'theme-name'),
		'labels'              => $labels,
		'supports'            => array(
			'title',
			'editor',
			'thumbnail',
			'excerpt',
			'custom-fields',
			'revisions',
		),
		'taxonomies'          => array('property_type', 'property_location'),
		'hierarchical'        => false,
		'public'              => true,
		'show_ui'             => true,
		'show_in_menu'        => true,
		'menu_position'       => 5,
		'menu_icon'           => 'dashicons-building',
		'show_in_admin_bar'   => true,
		'show_in_nav_menus'   => true,
		'can_export'          => true,
		'has_archive'         => 'properties',
		'exclude_from_search' => false,
		'publicly_queryable'  => true,
		'capability_type'     => 'post',
		'show_in_rest'        => true,
		'rest_base'           => 'properties',
	);

	register_post_type('property', $args);
}
add_action('init', 'theme_name_register_property_cpt');
```

## Arguments Reference

### Core Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `public` | bool | false | Whether post type is public |
| `hierarchical` | bool | false | Whether hierarchical (like pages) |
| `exclude_from_search` | bool | opposite of public | Exclude from search results |
| `publicly_queryable` | bool | value of public | Allow frontend queries |
| `show_ui` | bool | value of public | Show admin UI |
| `show_in_menu` | bool/string | value of show_ui | Where to show in admin menu |
| `show_in_nav_menus` | bool | value of public | Available for nav menus |
| `show_in_admin_bar` | bool | value of show_in_menu | Show in admin bar |
| `show_in_rest` | bool | false | Enable REST API and block editor |

### Menu Configuration

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `menu_position` | int | null | Menu position (5=below Posts, 20=below Pages) |
| `menu_icon` | string | 'dashicons-admin-post' | Dashicon or URL |

Common menu positions:
- 5: Below Posts
- 10: Below Media
- 15: Below Links
- 20: Below Pages
- 25: Below Comments
- 60: Below first separator
- 65: Below Plugins
- 70: Below Users

### Supports Array

```php
'supports' => array(
	'title',           // Post title
	'editor',          // Content editor
	'author',          // Author metabox
	'thumbnail',       // Featured image
	'excerpt',         // Excerpt field
	'trackbacks',      // Trackback/pingback
	'custom-fields',   // Custom fields metabox
	'comments',        // Comments
	'revisions',       // Revisions
	'page-attributes', // Menu order, parent
	'post-formats',    // Post formats
),
```

### Rewrite Rules

```php
'rewrite' => array(
	'slug'       => 'properties',  // URL slug
	'with_front' => true,          // Prepend blog prefix
	'feeds'      => true,          // RSS feeds
	'pages'      => true,          // Pagination
	'ep_mask'    => EP_PERMALINK,  // Endpoint mask
),
```

## Custom Capabilities

### Basic Capability Mapping

```php
'capability_type' => 'property',
'map_meta_cap'    => true,
```

This creates capabilities like:
- `edit_property`
- `edit_properties`
- `edit_others_properties`
- `publish_properties`
- `read_private_properties`
- `delete_property`
- `delete_properties`

### Custom Capability Names

```php
'capabilities' => array(
	'edit_post'          => 'edit_property',
	'read_post'          => 'read_property',
	'delete_post'        => 'delete_property',
	'edit_posts'         => 'edit_properties',
	'edit_others_posts'  => 'edit_others_properties',
	'publish_posts'      => 'publish_properties',
	'read_private_posts' => 'read_private_properties',
),
```

### Assigning Capabilities to Roles

```php
/**
 * Add property capabilities to administrator role.
 */
function theme_name_add_property_caps() {
	$role = get_role('administrator');

	$caps = array(
		'edit_property',
		'read_property',
		'delete_property',
		'edit_properties',
		'edit_others_properties',
		'publish_properties',
		'read_private_properties',
		'delete_properties',
		'delete_private_properties',
		'delete_published_properties',
		'delete_others_properties',
		'edit_private_properties',
		'edit_published_properties',
	);

	foreach ($caps as $cap) {
		$role->add_cap($cap);
	}
}
add_action('admin_init', 'theme_name_add_property_caps');
```

## REST API Configuration

### Basic REST Support

```php
'show_in_rest'          => true,
'rest_base'             => 'properties',
'rest_controller_class' => 'WP_REST_Posts_Controller',
```

### Accessing via REST API

```bash
# List all properties
GET /wp-json/wp/v2/properties

# Get single property
GET /wp-json/wp/v2/properties/123

# Create property (requires auth)
POST /wp-json/wp/v2/properties

# Update property
POST /wp-json/wp/v2/properties/123

# Delete property
DELETE /wp-json/wp/v2/properties/123
```

## Admin Columns

### Add Custom Columns

```php
/**
 * Add custom columns to property list.
 */
function theme_name_property_columns($columns) {
	$new_columns = array();

	foreach ($columns as $key => $value) {
		$new_columns[$key] = $value;

		// Insert after title
		if ('title' === $key) {
			$new_columns['property_status'] = __('Status', 'theme-name');
			$new_columns['property_price']  = __('Price', 'theme-name');
		}
	}

	// Add featured image at the start
	$new_columns = array_merge(
		array('property_image' => __('Image', 'theme-name')),
		$new_columns
	);

	return $new_columns;
}
add_filter('manage_property_posts_columns', 'theme_name_property_columns');

/**
 * Populate custom columns.
 */
function theme_name_property_column_content($column, $post_id) {
	switch ($column) {
		case 'property_image':
			if (has_post_thumbnail($post_id)) {
				echo get_the_post_thumbnail($post_id, array(50, 50));
			}
			break;

		case 'property_status':
			$status = get_post_meta($post_id, '_property_status', true);
			echo esc_html(ucfirst($status ?: 'N/A'));
			break;

		case 'property_price':
			$price = get_post_meta($post_id, '_property_price', true);
			echo $price ? '$' . number_format($price) : 'N/A';
			break;
	}
}
add_action('manage_property_posts_custom_column', 'theme_name_property_column_content', 10, 2);

/**
 * Make columns sortable.
 */
function theme_name_property_sortable_columns($columns) {
	$columns['property_status'] = 'property_status';
	$columns['property_price']  = 'property_price';
	return $columns;
}
add_filter('manage_edit-property_sortable_columns', 'theme_name_property_sortable_columns');

/**
 * Handle column sorting.
 */
function theme_name_property_orderby($query) {
	if (!is_admin() || !$query->is_main_query()) {
		return;
	}

	$orderby = $query->get('orderby');

	if ('property_price' === $orderby) {
		$query->set('meta_key', '_property_price');
		$query->set('orderby', 'meta_value_num');
	}
}
add_action('pre_get_posts', 'theme_name_property_orderby');
```

## Flush Rewrite Rules

Always flush rewrite rules after registering CPTs:

```php
/**
 * Flush rewrite rules on theme/plugin activation.
 */
function theme_name_flush_rewrites() {
	// Register CPT first
	theme_name_register_property_cpt();

	// Then flush
	flush_rewrite_rules();
}
register_activation_hook(__FILE__, 'theme_name_flush_rewrites');

// Or for themes:
add_action('after_switch_theme', 'theme_name_flush_rewrites');
```

**Manual flush in admin:** Settings → Permalinks → Save Changes

## Template Files

WordPress looks for these templates in order:

### Single Property
1. `single-property-{slug}.php`
2. `single-property.php`
3. `single.php`
4. `singular.php`
5. `index.php`

### Property Archive
1. `archive-property.php`
2. `archive.php`
3. `index.php`

### Example Single Template

```php
<?php
/**
 * Template for displaying single property.
 *
 * @package Theme_Name
 */

get_header();
?>

<main class="property-single">
	<?php while (have_posts()) : the_post(); ?>

		<article id="property-<?php the_ID(); ?>" <?php post_class(); ?>>
			<?php if (has_post_thumbnail()) : ?>
				<div class="property-hero">
					<?php the_post_thumbnail('full'); ?>
				</div>
			<?php endif; ?>

			<div class="property-content">
				<h1><?php the_title(); ?></h1>

				<div class="property-meta">
					<?php
					$status = get_post_meta(get_the_ID(), '_property_status', true);
					$price  = get_post_meta(get_the_ID(), '_property_price', true);
					?>
					<span class="status"><?php echo esc_html($status); ?></span>
					<span class="price">$<?php echo number_format($price); ?></span>
				</div>

				<div class="property-description">
					<?php the_content(); ?>
				</div>
			</div>
		</article>

	<?php endwhile; ?>
</main>

<?php
get_footer();
```

## WP_Query for CPT

```php
// Basic query
$properties = new WP_Query(array(
	'post_type'      => 'property',
	'posts_per_page' => 10,
));

// With meta query
$featured = new WP_Query(array(
	'post_type'      => 'property',
	'posts_per_page' => 6,
	'meta_query'     => array(
		array(
			'key'     => '_featured',
			'value'   => '1',
			'compare' => '=',
		),
	),
));

// With taxonomy query
$commercial = new WP_Query(array(
	'post_type'      => 'property',
	'posts_per_page' => -1,
	'tax_query'      => array(
		array(
			'taxonomy' => 'property_type',
			'field'    => 'slug',
			'terms'    => 'commercial',
		),
	),
));

// Combined filters
$query = new WP_Query(array(
	'post_type'      => 'property',
	'posts_per_page' => 12,
	'meta_query'     => array(
		'relation' => 'AND',
		array(
			'key'     => '_property_price',
			'value'   => array(100000, 500000),
			'type'    => 'NUMERIC',
			'compare' => 'BETWEEN',
		),
	),
	'tax_query'      => array(
		array(
			'taxonomy' => 'property_location',
			'field'    => 'slug',
			'terms'    => 'miami',
		),
	),
	'orderby'        => 'meta_value_num',
	'meta_key'       => '_property_price',
	'order'          => 'DESC',
));
```

## Best Practices

### 1. Always Use Prefixes

```php
// Good
register_post_type('theme_property', $args);

// Bad - too generic, may conflict
register_post_type('property', $args);
```

### 2. Enable REST API

```php
'show_in_rest' => true,  // Required for block editor
```

### 3. Use Text Domains

```php
'name' => __('Properties', 'theme-name'),
```

### 4. Flush Rewrite Rules Properly

Only flush on activation, not on every page load:

```php
// Good - only on activation
register_activation_hook(__FILE__, 'flush_rewrite_rules');

// Bad - performance killer
add_action('init', function() {
	register_post_type('property', $args);
	flush_rewrite_rules();  // NEVER do this!
});
```

### 5. Register Early

Use priority 0-9 on init hook:

```php
add_action('init', 'register_cpts', 0);
```

## Resources

- [register_post_type() Reference](https://developer.wordpress.org/reference/functions/register_post_type/)
- [Custom Post Type Labels](https://developer.wordpress.org/reference/functions/get_post_type_labels/)
- [Post Type Capabilities](https://developer.wordpress.org/plugins/users/roles-and-capabilities/)
