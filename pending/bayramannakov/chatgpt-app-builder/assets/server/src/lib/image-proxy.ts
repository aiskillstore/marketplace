/**
 * Image Proxy Utility
 *
 * Converts external image URLs to data URLs for CSP compliance.
 * ChatGPT's Content Security Policy only allows: 'self', data:, and specific CDN domains.
 *
 * Security features:
 * - Domain whitelist (SSRF protection)
 * - Size limits (prevent memory exhaustion)
 * - HTTPS-only (no mixed content)
 * - Internal IP blocking
 */

// Allowed domains for image fetching (SSRF protection)
// Add your trusted image sources here
const ALLOWED_IMAGE_DOMAINS = [
  "linkedin.com",
  "licdn.com",           // LinkedIn CDN
  "media.licdn.com",     // LinkedIn media
  "gravatar.com",
  "githubusercontent.com",
  // Add your API's image domains here
  // "assets.yourservice.com",
];

/**
 * Add a domain to the whitelist
 */
export function allowDomain(domain: string): void {
  if (!ALLOWED_IMAGE_DOMAINS.includes(domain)) {
    ALLOWED_IMAGE_DOMAINS.push(domain);
  }
}

/**
 * Validates a URL is safe to fetch (SSRF protection)
 * - Only allows HTTPS
 * - Only allows whitelisted domains
 * - Blocks internal IPs and localhost
 */
function isValidImageUrl(url: string): boolean {
  try {
    const parsed = new URL(url);

    // Only allow HTTPS
    if (parsed.protocol !== "https:") {
      console.log(`[ImageProxy] Blocked non-HTTPS URL: ${url}`);
      return false;
    }

    // Block localhost and internal IPs
    const hostname = parsed.hostname.toLowerCase();
    if (
      hostname === "localhost" ||
      hostname === "127.0.0.1" ||
      hostname.startsWith("192.168.") ||
      hostname.startsWith("10.") ||
      hostname.startsWith("172.16.") ||
      hostname.startsWith("172.17.") ||
      hostname.startsWith("172.18.") ||
      hostname.startsWith("172.19.") ||
      hostname.startsWith("172.2") ||
      hostname.startsWith("172.30.") ||
      hostname.startsWith("172.31.") ||
      hostname === "169.254.169.254" || // AWS metadata
      hostname.endsWith(".internal") ||
      hostname.endsWith(".local") ||
      hostname === "[::1]"  // IPv6 localhost
    ) {
      console.log(`[ImageProxy] Blocked internal URL: ${url}`);
      return false;
    }

    // Check against allowed domains
    const isAllowed = ALLOWED_IMAGE_DOMAINS.some(
      (domain) => hostname === domain || hostname.endsWith("." + domain)
    );

    if (!isAllowed) {
      console.log(`[ImageProxy] Blocked non-whitelisted domain: ${hostname}`);
      return false;
    }

    return true;
  } catch {
    console.log(`[ImageProxy] Invalid URL: ${url}`);
    return false;
  }
}

/**
 * Validates content type is an image
 */
function isImageContentType(contentType: string | null): boolean {
  if (!contentType) return false;
  const type = contentType.split(";")[0].trim().toLowerCase();
  return type.startsWith("image/");
}

/**
 * Fetches an image from a URL and converts it to a base64 data URL.
 * This is necessary because ChatGPT's Content Security Policy blocks
 * external image domains.
 *
 * Security: Only fetches from whitelisted domains to prevent SSRF
 *
 * @param url - The external image URL to convert
 * @param maxSizeKb - Maximum image size in KB (default: 200KB for profile images)
 * @returns A data URL string or null if conversion fails
 */
export async function imageToDataUrl(
  url: string | null | undefined,
  maxSizeKb: number = 200 // Profile pics typically under 200KB
): Promise<string | null> {
  if (!url) return null;

  // SSRF protection: validate URL before fetching
  if (!isValidImageUrl(url)) {
    return null;
  }

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000); // 10s timeout

    const response = await fetch(url, {
      headers: {
        // Some image servers require a user agent
        "User-Agent": "Mozilla/5.0 (compatible; ChatGPTAppBot/1.0)",
        "Accept": "image/*",
      },
      signal: controller.signal,
    });

    clearTimeout(timeout);

    if (!response.ok) {
      console.log(`[ImageProxy] Failed to fetch image: ${response.status} ${url}`);
      return null;
    }

    // Validate content type
    const contentType = response.headers.get("content-type");
    if (!isImageContentType(contentType)) {
      console.log(`[ImageProxy] Invalid content type: ${contentType} for ${url}`);
      return null;
    }

    const buffer = await response.arrayBuffer();

    // Check size limit
    const sizeKb = buffer.byteLength / 1024;
    if (sizeKb > maxSizeKb) {
      console.log(`[ImageProxy] Image too large: ${sizeKb.toFixed(1)}KB > ${maxSizeKb}KB`);
      return null;
    }

    // Convert to base64
    const base64 = Buffer.from(buffer).toString("base64");
    const mimeType = contentType?.split(";")[0].trim() || "image/jpeg";

    return `data:${mimeType};base64,${base64}`;
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      console.log(`[ImageProxy] Fetch timeout for: ${url}`);
    } else {
      console.log(`[ImageProxy] Error fetching image: ${error}`);
    }
    return null; // Fall back to initials/placeholder if fetch fails
  }
}

/**
 * Batch convert multiple image URLs to data URLs.
 * Useful for converting multiple images in parallel.
 *
 * @param urls - Array of image URLs
 * @param maxSizeKb - Maximum size per image
 * @returns Array of data URLs (null for failed conversions)
 */
export async function imagesToDataUrls(
  urls: (string | null | undefined)[],
  maxSizeKb: number = 200
): Promise<(string | null)[]> {
  return Promise.all(urls.map((url) => imageToDataUrl(url, maxSizeKb)));
}

/**
 * Check if a URL would be allowed by the proxy
 * Useful for pre-validation before attempting fetch
 */
export function isAllowedImageUrl(url: string): boolean {
  return isValidImageUrl(url);
}

/**
 * Get the list of allowed domains
 */
export function getAllowedDomains(): string[] {
  return [...ALLOWED_IMAGE_DOMAINS];
}
