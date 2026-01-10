/**
 * Example List Component
 *
 * A simple, reusable list component pattern for ChatGPT widgets.
 * Copy and customize for your specific use case.
 */

import React from "react";

// ============================================================================
// Types
// ============================================================================

interface ListItem {
  id: string;
  title: string;
  subtitle?: string;
  status?: string;
}

interface ExampleListProps<T extends ListItem> {
  items: T[];
  selectedId?: string | null;
  onSelect?: (item: T) => void;
  onAction?: (item: T) => void;
  actionLabel?: string;
  emptyMessage?: string;
}

// ============================================================================
// Component
// ============================================================================

export function ExampleList<T extends ListItem>({
  items,
  selectedId,
  onSelect,
  onAction,
  actionLabel = "Select",
  emptyMessage = "No items to display.",
}: ExampleListProps<T>) {
  if (items.length === 0) {
    return (
      <div className="example-list-empty">
        <p>{emptyMessage}</p>
        <style>{styles}</style>
      </div>
    );
  }

  return (
    <ul className="example-list">
      {items.map((item) => (
        <li
          key={item.id}
          className={`example-list-item ${selectedId === item.id ? "selected" : ""}`}
          onClick={() => onSelect?.(item)}
        >
          <div className="example-list-content">
            <span className="example-list-title">{item.title}</span>
            {item.subtitle && (
              <span className="example-list-subtitle">{item.subtitle}</span>
            )}
          </div>

          {item.status && (
            <span className="example-list-status">{item.status}</span>
          )}

          {onAction && (
            <button
              className="example-list-action"
              onClick={(e) => {
                e.stopPropagation();
                onAction(item);
              }}
            >
              {actionLabel}
            </button>
          )}
        </li>
      ))}
      <style>{styles}</style>
    </ul>
  );
}

// ============================================================================
// Styles
// ============================================================================

const styles = `
.example-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.example-list-empty {
  text-align: center;
  padding: 32px 16px;
  color: var(--text-secondary, #666);
}

.example-list-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color, #e0e0e0);
  cursor: pointer;
  transition: background 0.15s;
}

.example-list-item:last-child {
  border-bottom: none;
}

.example-list-item:hover {
  background: var(--bg-secondary, #f5f5f5);
}

.example-list-item.selected {
  background: var(--bg-secondary, #f5f5f5);
}

.example-list-content {
  flex: 1;
  min-width: 0;
}

.example-list-title {
  display: block;
  font-weight: 500;
  color: var(--text-primary, #1a1a1a);
}

.example-list-subtitle {
  display: block;
  font-size: 13px;
  color: var(--text-secondary, #666);
  margin-top: 2px;
}

.example-list-status {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  background: var(--bg-secondary, #f5f5f5);
  color: var(--text-secondary, #666);
}

.example-list-action {
  padding: 6px 12px;
  font-size: 13px;
  border: 1px solid var(--accent-color, #0066cc);
  background: transparent;
  color: var(--accent-color, #0066cc);
  border-radius: 4px;
  cursor: pointer;
}

.example-list-action:hover {
  background: var(--accent-color, #0066cc);
  color: white;
}
`;
