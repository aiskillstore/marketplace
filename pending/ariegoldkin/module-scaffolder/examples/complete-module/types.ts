/**
 * Example Module Types
 *
 * Demonstrates proper type definitions with I prefix for interfaces.
 */

// Example interface - always use I prefix
export interface IExampleData {
  id: string;
  title: string;
  description: string;
  createdAt: Date;
  isActive: boolean;
}

// Example type alias - T prefix optional but recommended
export type TExampleStatus = "pending" | "active" | "completed" | "archived";

// Example for component props
export interface IExampleCardProps {
  data: IExampleData;
  onSelect?: (id: string) => void;
  className?: string;
}
