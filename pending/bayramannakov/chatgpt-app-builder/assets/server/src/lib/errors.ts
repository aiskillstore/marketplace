/**
 * Error Handling Utilities
 *
 * Convert errors to actionable user messages.
 */

interface ApiError {
  response?: {
    status?: number;
    data?: {
      message?: string;
    };
  };
  message?: string;
}

/**
 * Convert API errors to user-friendly messages.
 *
 * Returns actionable guidance, not technical details.
 */
export function handleApiError(error: unknown): string {
  const apiError = error as ApiError;

  // Check for HTTP status codes
  if (apiError.response?.status) {
    switch (apiError.response.status) {
      case 400:
        return `Invalid request: ${apiError.response.data?.message || "Check your input and try again."}`;
      case 401:
        return "Authentication required. Please reconnect your account.";
      case 403:
        return "Permission denied. You don't have access to this resource.";
      case 404:
        return "Resource not found. It may have been deleted.";
      case 409:
        return "Conflict: This action conflicts with existing data.";
      case 422:
        return `Validation error: ${apiError.response.data?.message || "Please check your input."}`;
      case 429:
        return "Rate limit exceeded. Please wait a moment and try again.";
      case 500:
      case 502:
      case 503:
        return "Service temporarily unavailable. Please try again later.";
      default:
        return `Request failed: ${apiError.response.data?.message || "An error occurred."}`;
    }
  }

  // Handle network errors
  if (error instanceof Error) {
    if (error.message.includes("ECONNREFUSED")) {
      return "Could not connect to the service. Please try again later.";
    }
    if (error.message.includes("ETIMEDOUT") || error.message.includes("timeout")) {
      return "Request timed out. Please try again.";
    }
    if (error.message.includes("ENOTFOUND")) {
      return "Service not found. Please check your connection.";
    }

    return `An error occurred: ${error.message}`;
  }

  return "An unexpected error occurred. Please try again.";
}

/**
 * Wrap an async function with error handling.
 */
export function withErrorHandling<T extends unknown[], R>(
  fn: (...args: T) => Promise<R>,
  errorHandler: (error: unknown) => R
): (...args: T) => Promise<R> {
  return async (...args: T): Promise<R> => {
    try {
      return await fn(...args);
    } catch (error) {
      return errorHandler(error);
    }
  };
}
