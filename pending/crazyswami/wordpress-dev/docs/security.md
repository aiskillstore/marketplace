# WordPress Security Best Practices

Comprehensive security guide covering input sanitization, output escaping, nonce verification, and SQL safety.

## The Golden Rule

> **Sanitize input, escape output, verify intent**

Never trust user input. Always validate and sanitize data coming in, and escape data going out.

## Input Sanitization

### Sanitization Functions

| Function | Use For | Example |
|----------|---------|---------|
| `sanitize_text_field()` | Single-line text | Names, titles |
| `sanitize_textarea_field()` | Multi-line text | Descriptions, comments |
| `sanitize_email()` | Email addresses | Contact forms |
| `sanitize_url()` | URLs | Links, redirects |
| `sanitize_file_name()` | File names | Uploads |
| `sanitize_title()` | Slugs | Post slugs, URL segments |
| `sanitize_key()` | Keys, identifiers | Meta keys, option names |
| `absint()` | Positive integers | IDs, counts |
| `intval()` | Any integer | Quantities |
| `wp_kses()` | HTML with allowed tags | Rich content |
| `wp_kses_post()` | Post content HTML | Editor content |

### Examples

```php
// Text fields
$name = sanitize_text_field($_POST['name']);
$bio = sanitize_textarea_field($_POST['bio']);

// Email
$email = sanitize_email($_POST['email']);
if (!is_email($email)) {
	wp_die('Invalid email address');
}

// URL
$website = esc_url_raw($_POST['website']);  // For database
$website = sanitize_url($_POST['website']); // Same as esc_url_raw

// Integer
$post_id = absint($_GET['post_id']);
$quantity = intval($_POST['quantity']);

// Slug
$slug = sanitize_title($_POST['title']);

// Array of values
$ids = array_map('absint', (array) $_POST['ids']);

// HTML content (limited tags)
$allowed = array(
	'a'      => array('href' => array(), 'title' => array()),
	'br'     => array(),
	'em'     => array(),
	'strong' => array(),
);
$content = wp_kses($_POST['content'], $allowed);

// Full post HTML
$content = wp_kses_post($_POST['content']);
```

### Validation vs Sanitization

```php
// Validation: Check if valid (returns true/false)
if (!is_email($email)) {
	$errors[] = 'Invalid email';
}

if (strlen($name) < 2) {
	$errors[] = 'Name too short';
}

// Sanitization: Clean the data (returns cleaned value)
$email = sanitize_email($email);
$name = sanitize_text_field($name);
```

## Output Escaping

### Escaping Functions

| Function | Use For | Context |
|----------|---------|---------|
| `esc_html()` | HTML content | Text between tags |
| `esc_attr()` | Attributes | Inside HTML attributes |
| `esc_url()` | URLs | href, src attributes |
| `esc_js()` | JavaScript strings | Inline JS |
| `esc_textarea()` | Textarea content | Inside textarea tags |
| `wp_kses()` | Controlled HTML | Allow specific tags |

### Escaping with Translation

| Function | Purpose |
|----------|---------|
| `esc_html__()` | Escape + translate |
| `esc_html_e()` | Escape + translate + echo |
| `esc_attr__()` | Escape attribute + translate |
| `esc_attr_e()` | Escape attribute + translate + echo |

### Examples

```php
// HTML content
<p><?php echo esc_html($user_bio); ?></p>

// Attributes
<input type="text" value="<?php echo esc_attr($value); ?>">
<div class="<?php echo esc_attr($class); ?>">

// URLs
<a href="<?php echo esc_url($link); ?>">Click here</a>
<img src="<?php echo esc_url($image_url); ?>">

// JavaScript
<script>
var userName = '<?php echo esc_js($name); ?>';
</script>

// With translation
<h1><?php esc_html_e('Welcome', 'theme-name'); ?></h1>
<input placeholder="<?php esc_attr_e('Enter name', 'theme-name'); ?>">

// Textarea
<textarea><?php echo esc_textarea($content); ?></textarea>

// Allow specific HTML
<?php
$allowed = array(
	'strong' => array(),
	'em'     => array(),
	'a'      => array('href' => array()),
);
echo wp_kses($user_html, $allowed);
?>
```

### Never Trust, Always Escape

```php
// WRONG - XSS vulnerability
<p><?php echo $user_input; ?></p>
<a href="<?php echo $url; ?>">Link</a>

// CORRECT - Always escape
<p><?php echo esc_html($user_input); ?></p>
<a href="<?php echo esc_url($url); ?>">Link</a>
```

## Nonce Verification

Nonces prevent CSRF (Cross-Site Request Forgery) attacks.

### Creating Nonces

```php
// In a form
<form method="post">
	<?php wp_nonce_field('theme_save_settings', 'theme_nonce'); ?>
	<!-- form fields -->
	<button type="submit">Save</button>
</form>

// As a URL
$url = wp_nonce_url(admin_url('admin.php?action=delete&id=123'), 'delete_item_123');

// Just the nonce value
$nonce = wp_create_nonce('my_action');
```

### Verifying Nonces

```php
// Verify form nonce
if (!isset($_POST['theme_nonce']) || !wp_verify_nonce($_POST['theme_nonce'], 'theme_save_settings')) {
	wp_die('Security check failed');
}

// Verify URL nonce
if (!isset($_GET['_wpnonce']) || !wp_verify_nonce($_GET['_wpnonce'], 'delete_item_123')) {
	wp_die('Security check failed');
}

// For AJAX (uses wp_ajax_* action name)
check_ajax_referer('my_ajax_action', 'security');
```

### Complete Form Example

```php
// Display form
function theme_settings_form() {
	?>
	<form method="post" action="">
		<?php wp_nonce_field('theme_settings_save', 'theme_settings_nonce'); ?>

		<label>
			Site Title:
			<input type="text" name="site_title" value="<?php echo esc_attr(get_option('site_title')); ?>">
		</label>

		<button type="submit" name="theme_save_settings">Save Settings</button>
	</form>
	<?php
}

// Process form
function theme_process_settings() {
	if (!isset($_POST['theme_save_settings'])) {
		return;
	}

	// Verify nonce
	if (!wp_verify_nonce($_POST['theme_settings_nonce'], 'theme_settings_save')) {
		wp_die('Security check failed');
	}

	// Check capability
	if (!current_user_can('manage_options')) {
		wp_die('Unauthorized access');
	}

	// Sanitize and save
	$title = sanitize_text_field($_POST['site_title']);
	update_option('site_title', $title);

	// Redirect to prevent resubmission
	wp_safe_redirect(add_query_arg('saved', '1'));
	exit;
}
add_action('admin_init', 'theme_process_settings');
```

## Capability Checks

Always verify the user has permission to perform an action.

### Common Capabilities

| Capability | Who Has It |
|------------|-----------|
| `manage_options` | Administrators |
| `edit_posts` | Contributors+ |
| `publish_posts` | Authors+ |
| `edit_others_posts` | Editors+ |
| `edit_pages` | Editors+ |
| `upload_files` | Authors+ |
| `edit_users` | Administrators |

### Examples

```php
// Check before showing admin menu
if (current_user_can('manage_options')) {
	add_menu_page(/* ... */);
}

// Check before processing form
if (!current_user_can('edit_posts')) {
	wp_die('You do not have permission to edit posts.');
}

// Check specific post capability
if (current_user_can('edit_post', $post_id)) {
	// Allow edit
}

// Check for custom capability
if (current_user_can('edit_properties')) {
	// Allow property management
}
```

## SQL Injection Prevention

### Use $wpdb->prepare()

**Always** use prepared statements for database queries:

```php
global $wpdb;

// WRONG - SQL injection vulnerability
$results = $wpdb->get_results("SELECT * FROM {$wpdb->posts} WHERE post_author = {$_GET['author']}");

// CORRECT - Use prepare()
$results = $wpdb->get_results(
	$wpdb->prepare(
		"SELECT * FROM {$wpdb->posts} WHERE post_author = %d",
		absint($_GET['author'])
	)
);
```

### Placeholder Types

| Placeholder | Type | Example |
|-------------|------|---------|
| `%d` | Integer | IDs, counts |
| `%f` | Float | Prices, percentages |
| `%s` | String | Names, slugs |

### Examples

```php
global $wpdb;

// Single value
$post = $wpdb->get_row(
	$wpdb->prepare(
		"SELECT * FROM {$wpdb->posts} WHERE ID = %d",
		$post_id
	)
);

// Multiple values
$results = $wpdb->get_results(
	$wpdb->prepare(
		"SELECT * FROM {$wpdb->posts}
		 WHERE post_type = %s
		 AND post_status = %s
		 AND post_author = %d",
		'property',
		'publish',
		$user_id
	)
);

// LIKE queries (escape wildcards)
$search = '%' . $wpdb->esc_like($search_term) . '%';
$results = $wpdb->get_results(
	$wpdb->prepare(
		"SELECT * FROM {$wpdb->posts} WHERE post_title LIKE %s",
		$search
	)
);

// IN clause (build placeholders dynamically)
$ids = array(1, 2, 3, 4, 5);
$placeholders = implode(',', array_fill(0, count($ids), '%d'));
$results = $wpdb->get_results(
	$wpdb->prepare(
		"SELECT * FROM {$wpdb->posts} WHERE ID IN ($placeholders)",
		$ids
	)
);
```

### Insert/Update with $wpdb

```php
// Insert (automatically escapes)
$wpdb->insert(
	$wpdb->prefix . 'custom_table',
	array(
		'name'  => $name,  // Escaped automatically
		'email' => $email,
		'count' => $count,
	),
	array('%s', '%s', '%d')  // Format specifiers
);

// Update
$wpdb->update(
	$wpdb->prefix . 'custom_table',
	array('name' => $new_name),  // Data to update
	array('id' => $id),          // WHERE clause
	array('%s'),                  // Data format
	array('%d')                   // WHERE format
);

// Delete
$wpdb->delete(
	$wpdb->prefix . 'custom_table',
	array('id' => $id),
	array('%d')
);
```

## File Upload Security

### Validate Uploads

```php
function theme_handle_upload($file) {
	// Check for upload errors
	if ($file['error'] !== UPLOAD_ERR_OK) {
		return new WP_Error('upload_error', 'Upload failed');
	}

	// Validate file type
	$allowed_types = array('image/jpeg', 'image/png', 'image/gif');
	$file_type = wp_check_filetype($file['name']);

	if (!in_array($file_type['type'], $allowed_types, true)) {
		return new WP_Error('invalid_type', 'Invalid file type');
	}

	// Validate file size (5MB max)
	$max_size = 5 * 1024 * 1024;
	if ($file['size'] > $max_size) {
		return new WP_Error('too_large', 'File too large');
	}

	// Use WordPress upload handler
	require_once ABSPATH . 'wp-admin/includes/file.php';

	$upload = wp_handle_upload($file, array('test_form' => false));

	if (isset($upload['error'])) {
		return new WP_Error('upload_failed', $upload['error']);
	}

	return $upload;
}
```

### Use WordPress Media Library

```php
// Proper way to add media
require_once ABSPATH . 'wp-admin/includes/media.php';
require_once ABSPATH . 'wp-admin/includes/file.php';
require_once ABSPATH . 'wp-admin/includes/image.php';

$attachment_id = media_handle_upload('file_field', $post_id);

if (is_wp_error($attachment_id)) {
	// Handle error
}
```

## AJAX Security

### Frontend AJAX

```php
// PHP - Register AJAX handlers
add_action('wp_ajax_my_action', 'handle_my_action');        // Logged-in users
add_action('wp_ajax_nopriv_my_action', 'handle_my_action'); // Non-logged-in users

function handle_my_action() {
	// Verify nonce
	check_ajax_referer('my_ajax_nonce', 'security');

	// Check capability
	if (!current_user_can('edit_posts')) {
		wp_send_json_error('Unauthorized', 403);
	}

	// Sanitize input
	$data = sanitize_text_field($_POST['data']);

	// Process and respond
	wp_send_json_success(array('result' => $data));
}

// JavaScript
jQuery(function($) {
	$('#my-button').on('click', function() {
		$.ajax({
			url: myAjax.ajaxUrl,
			type: 'POST',
			data: {
				action: 'my_action',
				security: myAjax.nonce,
				data: $('#my-input').val()
			},
			success: function(response) {
				if (response.success) {
					console.log(response.data);
				}
			}
		});
	});
});

// Localize script
wp_localize_script('my-script', 'myAjax', array(
	'ajaxUrl' => admin_url('admin-ajax.php'),
	'nonce'   => wp_create_nonce('my_ajax_nonce'),
));
```

### REST API Security

```php
// Register REST route with permission callback
register_rest_route('theme/v1', '/properties', array(
	'methods'             => 'POST',
	'callback'            => 'create_property',
	'permission_callback' => function() {
		return current_user_can('publish_posts');
	},
	'args'                => array(
		'title' => array(
			'required'          => true,
			'sanitize_callback' => 'sanitize_text_field',
		),
	),
));
```

## Security Checklist

### Forms

- [ ] wp_nonce_field() in form
- [ ] wp_verify_nonce() on processing
- [ ] current_user_can() check
- [ ] All inputs sanitized
- [ ] Redirect after processing

### Output

- [ ] esc_html() for text content
- [ ] esc_attr() for attributes
- [ ] esc_url() for URLs
- [ ] wp_kses() for controlled HTML

### Database

- [ ] $wpdb->prepare() for all queries
- [ ] Use $wpdb->insert/update/delete
- [ ] Never concatenate user input

### Files

- [ ] Validate file type
- [ ] Validate file size
- [ ] Use WordPress upload functions
- [ ] Store outside web root if sensitive

### AJAX/REST

- [ ] Nonce verification
- [ ] Capability checks
- [ ] Input sanitization
- [ ] Proper error responses

## Resources

- [Data Validation](https://developer.wordpress.org/plugins/security/data-validation/)
- [Securing Input](https://developer.wordpress.org/plugins/security/securing-input/)
- [Securing Output](https://developer.wordpress.org/plugins/security/securing-output/)
- [Nonces](https://developer.wordpress.org/plugins/security/nonces/)
- [OWASP WordPress Security](https://owasp.org/www-project-wordpress-security/)
