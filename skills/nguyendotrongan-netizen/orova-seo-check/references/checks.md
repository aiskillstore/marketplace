# Orova SEO Check: check reference

Every scan returns 12 groups with a score out of the group maximum (total 100).
Each check has a `code` and a `status`: `pass`, `warn`, `fail` or `skip` (not applicable, for example no images on the page).
Labels below describe what a passing site does. A `fail` or `warn` means the statement is not (fully) true.
The `params` object carries measured values (for example `count`, `score`, `value`, `kb`).
Unknown codes added later by the API are shown with underscores replaced by spaces.

## Groups

| Key | Group | Max points |
|---|---|---:|
| `access` | Access & HTTP | 14 |
| `security` | Security headers | 6 |
| `head` | Head & meta | 12 |
| `content` | Content | 10 |
| `images` | Images | 5 |
| `social` | Social sharing | 5 |
| `structured` | Structured data | 4 |
| `intl` | International | 2 |
| `crawl` | Crawlability | 12 |
| `samples` | Sample pages | 6 |
| `speed` | Speed | 14 |
| `links` | Links & authority | 10 |
| | **Total** | **100** |

## Access & HTTP (`access`, 14 points)

| Code | Check |
|---|---|
| `home_200` | Homepage returns HTTP 200 |
| `response_fast` | Homepage responds quickly |
| `ttfb_fast` | Time to first byte is fast |
| `https_on` | Site is served over HTTPS |
| `cert_valid_30d` | TLS certificate is valid for 30+ more days |
| `http_redirects_https` | HTTP redirects to HTTPS |
| `www_consistent` | www and non-www resolve to one host |
| `no_redirect_chain` | No redirect chain on the homepage |
| `custom_404` | Missing pages return a real 404 |
| `compression_on` | Compression (gzip/brotli) is enabled |
| `charset_declared` | Character encoding is declared |
| `http2_or_h3` | HTTP/2 or HTTP/3 is supported |

## Security headers (`security`, 6 points)

| Code | Check |
|---|---|
| `hsts` | Strict-Transport-Security header is set |
| `x_frame_options` | X-Frame-Options header is set |
| `x_content_type_options` | X-Content-Type-Options header is set |
| `csp_present` | Content-Security-Policy header is set |
| `referrer_policy` | Referrer-Policy header is set |
| `no_mixed_content` | No mixed (HTTP) content on HTTPS pages |

## Head & meta (`head`, 12 points)

| Code | Check |
|---|---|
| `title_present` | Page has a title tag |
| `title_length` | Title length is in the recommended range |
| `meta_desc_present` | Page has a meta description |
| `meta_desc_length` | Meta description length is in the recommended range |
| `canonical_present` | Canonical link is present |
| `canonical_self` | Canonical points to the page itself |
| `lang_declared` | HTML lang attribute is declared |
| `viewport_present` | Mobile viewport meta tag is present |
| `not_noindex` | Page is not set to noindex |
| `no_meta_refresh` | No meta refresh redirect |
| `favicon` | Favicon is present |
| `apple_touch_icon` | Apple touch icon is present |
| `theme_color` | Theme color meta tag is present |

## Content (`content`, 10 points)

| Code | Check |
|---|---|
| `h1_present` | Page has an H1 heading |
| `h1_single` | Page has exactly one H1 |
| `h2_present` | Page has H2 headings |
| `heading_order` | Headings follow a logical order |
| `word_count_300` | Page has at least 300 words |
| `text_html_ratio` | Text-to-HTML ratio is healthy |
| `no_lorem_ipsum` | No placeholder (lorem ipsum) text |
| `no_empty_anchors` | No empty link anchors |
| `internal_links_5` | Page has at least 5 internal links |
| `no_generic_anchors` | No generic anchor text (e.g. 'click here') |

## Images (`images`, 5 points)

| Code | Check |
|---|---|
| `images_alt_all` | All images have alt text |
| `images_alt_descriptive` | Image alt text is descriptive |
| `images_lazy` | Images use lazy loading |
| `images_modern_format` | Images use modern formats (WebP/AVIF) |
| `images_dimensions` | Images declare width and height |

## Social sharing (`social`, 5 points)

| Code | Check |
|---|---|
| `og_title` | Open Graph title is set |
| `og_description` | Open Graph description is set |
| `og_image` | Open Graph image is set |
| `og_type` | Open Graph type is set |
| `og_url` | Open Graph URL is set |
| `twitter_card` | Twitter card is set |

## Structured data (`structured`, 4 points)

| Code | Check |
|---|---|
| `jsonld_present` | JSON-LD structured data is present |
| `jsonld_valid` | JSON-LD parses without errors |
| `jsonld_types` | JSON-LD declares useful schema types |
| `breadcrumb_schema` | Breadcrumb schema is present |

## International (`intl`, 2 points)

| Code | Check |
|---|---|
| `hreflang_present` | hreflang tags are present |
| `hreflang_x_default` | hreflang x-default is set |
| `hreflang_self` | hreflang includes a self reference |

## Crawlability (`crawl`, 12 points)

| Code | Check |
|---|---|
| `robots_exists` | robots.txt exists |
| `robots_not_blocking_all` | robots.txt does not block the whole site |
| `robots_sitemap_ref` | robots.txt references a sitemap |
| `sitemap_exists` | XML sitemap exists |
| `sitemap_valid_xml` | Sitemap is valid XML |
| `sitemap_urls_5` | Sitemap lists at least 5 URLs |
| `sitemap_recent_60d` | Sitemap was updated in the last 60 days |
| `sitemap_same_domain` | Sitemap URLs are on the same domain |
| `sitemap_https_urls` | Sitemap URLs use HTTPS |
| `internal_links_no_broken` | No broken internal links found |

## Sample pages (`samples`, 6 points)

| Code | Check |
|---|---|
| `samples_found` | Sample inner pages were found |
| `samples_fast` | Sample pages respond quickly |
| `samples_title` | Sample pages have titles |
| `samples_h1_single` | Sample pages have exactly one H1 |
| `samples_meta` | Sample pages have meta descriptions |
| `samples_img_alt` | Sample page images have alt text |

## Speed (`speed`, 14 points)

| Code | Check |
|---|---|
| `psi_perf_mobile` | PageSpeed performance (mobile) is good |
| `psi_perf_desktop` | PageSpeed performance (desktop) is good |
| `psi_seo` | PageSpeed SEO score is good |
| `psi_a11y` | PageSpeed accessibility score is good |
| `psi_best_practices` | PageSpeed best-practices score is good |
| `lcp_ok` | Largest Contentful Paint is within target |
| `cls_ok` | Cumulative Layout Shift is within target |
| `tbt_ok` | Total Blocking Time is within target |
| `page_size_ok` | Page weight is reasonable |
| `scripts_count_ok` | Number of scripts is reasonable |
| `inline_css_small` | Inline CSS is small |

## Links & authority (`links`, 10 points)

| Code | Check |
|---|---|
| `external_links_count` | External link count is reasonable |
| `outbound_https` | Outbound links use HTTPS |
| `outbound_nofollow_info` | Outbound nofollow usage (info) |
| `outbound_no_broken` | No broken outbound links found |
| `referring_domains` | Site has referring domains |
| `domain_rank` | Domain has a rank in the link graph |

## Backlinks object

`backlinks` (in a scan result) and the `/u/seo-check/backlinks` endpoint share this shape:

```json
{"source": "commoncrawl", "dataset": "cc-main-2026-jul-aug-sep", "fetched_at": "...", "found": true,
 "referring_domains": 0, "domain_rank": null,
 "referring_domains_list": [{"domain": "...", "in_degree": 0, "rank": 0}]}
```

Data is domain-level, from the Common Crawl host graph (about 133 million domains). It is not a page-level link index and may miss small or new sites, which can show 0 referring domains.
