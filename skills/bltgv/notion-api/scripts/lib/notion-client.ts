import type { ScriptResponse } from "./types";

const NOTION_API_BASE = "https://api.notion.com/v1";
const NOTION_VERSION = "2022-06-28";

export type AuthCheckResult =
  | { ok: true; token: string }
  | { ok: false; response: ScriptResponse<never> };

/**
 * Check for Notion token and return auth result
 */
export function checkAuth(): AuthCheckResult {
  const token = process.env.NOTION_TOKEN;

  if (!token) {
    return {
      ok: false,
      response: {
        status: "auth_required",
        message: "Set NOTION_TOKEN environment variable with your integration token. Create an integration at the setup URL, then share your pages/databases with it.",
        setupUrl: "https://www.notion.so/my-integrations",
      },
    };
  }

  return { ok: true, token };
}

/**
 * Make a request to the Notion API
 */
export async function notionRequest<T>(
  token: string,
  endpoint: string,
  options: {
    method?: "GET" | "POST" | "PATCH" | "DELETE";
    body?: unknown;
  } = {}
): Promise<T> {
  const { method = "GET", body } = options;
  const url = `${NOTION_API_BASE}${endpoint}`;

  const response = await fetch(url, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      "Notion-Version": NOTION_VERSION,
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const errorMessage = (errorData as { message?: string }).message || response.statusText;
    throw new Error(`Notion API error: ${response.status} - ${errorMessage}`);
  }

  return response.json();
}

/**
 * Output helper for consistent JSON responses
 */
export function output<T>(response: ScriptResponse<T>): void {
  console.log(JSON.stringify(response));
  process.exit(response.status === "success" ? 0 : 1);
}

/**
 * Extract plain text from rich text array
 */
export function richTextToPlain(richText: Array<{ plain_text: string }> | undefined): string {
  if (!richText) return "";
  return richText.map((t) => t.plain_text).join("");
}

/**
 * Get page title from properties
 */
export function getPageTitle(properties: Record<string, { type: string; title?: Array<{ plain_text: string }> }>): string {
  for (const prop of Object.values(properties)) {
    if (prop.type === "title" && prop.title) {
      return richTextToPlain(prop.title);
    }
  }
  return "Untitled";
}
