/**
 * formatDate - Example Module
 *
 * Formats a date into a readable string.
 *
 * @param date - The date to format
 * @returns Formatted date string (e.g., "Jan 15, 2025")
 */
export function formatDate(date: Date): string {
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

/**
 * validateExampleData - Example Module
 *
 * Validates example data structure.
 *
 * @param data - Data to validate
 * @returns True if valid, false otherwise
 */
export function validateExampleData(data: unknown): boolean {
  if (typeof data !== "object" || data === null) {
    return false;
  }

  const obj = data as Record<string, unknown>;

  return (
    typeof obj.id === "string" &&
    typeof obj.title === "string" &&
    typeof obj.description === "string" &&
    obj.createdAt instanceof Date &&
    typeof obj.isActive === "boolean"
  );
}
