/**
 * API Client
 *
 * Client for communicating with your backend API.
 * TODO: Replace placeholder implementations with actual API calls.
 */

// ============================================================================
// Types
// ============================================================================

export interface Item {
  id: string;
  title: string;
  description?: string;
  status: "active" | "completed";
  priority: "low" | "medium" | "high";
  dueDate?: string;
  createdAt: string;
  updatedAt: string;
}

export interface GetItemsParams {
  status?: "active" | "completed" | "all";
  limit?: number;
  cursor?: string;
}

export interface CreateItemParams {
  title: string;
  description?: string;
  dueDate?: string;
  priority?: "low" | "medium" | "high";
}

export interface UpdateItemParams {
  title?: string;
  description?: string;
  status?: "active" | "completed";
  dueDate?: string;
  priority?: "low" | "medium" | "high";
}

// ============================================================================
// API Client
// ============================================================================

class ApiClient {
  private baseUrl: string;
  private token: string;

  constructor() {
    this.baseUrl = process.env.API_BASE_URL || "https://api.example.com";
    this.token = process.env.API_TOKEN || "";
  }

  private async request<T>(
    method: string,
    path: string,
    body?: unknown
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`;

    const response = await fetch(url, {
      method,
      headers: {
        Authorization: `Bearer ${this.token}`,
        "Content-Type": "application/json",
      },
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const error = new Error(`API error: ${response.status}`) as Error & {
        response: { status: number; data: unknown };
      };
      error.response = { status: response.status, data: errorData };
      throw error;
    }

    return response.json();
  }

  // =========================================================================
  // Item Operations
  // =========================================================================

  async getItems(params: GetItemsParams): Promise<Item[]> {
    const searchParams = new URLSearchParams();

    if (params.status && params.status !== "all") {
      searchParams.set("status", params.status);
    }
    if (params.limit) {
      searchParams.set("limit", params.limit.toString());
    }
    if (params.cursor) {
      searchParams.set("cursor", params.cursor);
    }

    const queryString = searchParams.toString();
    const path = `/items${queryString ? `?${queryString}` : ""}`;

    const response = await this.request<{ items: Item[] }>("GET", path);
    return response.items;
  }

  async getItem(id: string): Promise<Item> {
    return this.request<Item>("GET", `/items/${id}`);
  }

  async createItem(params: CreateItemParams): Promise<Item> {
    return this.request<Item>("POST", "/items", {
      title: params.title,
      description: params.description,
      due_date: params.dueDate,
      priority: params.priority || "medium",
    });
  }

  async updateItem(id: string, params: UpdateItemParams): Promise<Item> {
    return this.request<Item>("PATCH", `/items/${id}`, params);
  }

  async deleteItem(id: string): Promise<void> {
    await this.request<void>("DELETE", `/items/${id}`);
  }

  async completeItem(id: string): Promise<Item> {
    return this.updateItem(id, { status: "completed" });
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
