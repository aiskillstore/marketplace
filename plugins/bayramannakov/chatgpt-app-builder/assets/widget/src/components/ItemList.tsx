/**
 * Item List Component
 *
 * Displays a list of items with selection and completion actions.
 */

import React from "react";

// ============================================================================
// Types
// ============================================================================

interface Item {
  id: string;
  title: string;
  status: "active" | "completed";
  due_date?: string;
  priority: "low" | "medium" | "high";
}

interface ItemListProps {
  items: Item[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onComplete: (id: string) => void;
}

// ============================================================================
// Component
// ============================================================================

export function ItemList({
  items,
  selectedId,
  onSelect,
  onComplete,
}: ItemListProps) {
  if (items.length === 0) {
    return (
      <div className="item-list-empty">
        <p>No items to display.</p>
      </div>
    );
  }

  return (
    <ul className="item-list">
      {items.map((item) => (
        <ItemRow
          key={item.id}
          item={item}
          isSelected={selectedId === item.id}
          onSelect={() => onSelect(item.id)}
          onComplete={() => onComplete(item.id)}
        />
      ))}
      <style>{styles}</style>
    </ul>
  );
}

// ============================================================================
// Item Row
// ============================================================================

interface ItemRowProps {
  item: Item;
  isSelected: boolean;
  onSelect: () => void;
  onComplete: () => void;
}

function ItemRow({ item, isSelected, onSelect, onComplete }: ItemRowProps) {
  const isCompleted = item.status === "completed";

  return (
    <li
      className={`item-row ${isSelected ? "selected" : ""} ${isCompleted ? "completed" : ""}`}
      onClick={onSelect}
    >
      <input
        type="checkbox"
        checked={isCompleted}
        onChange={(e) => {
          e.stopPropagation();
          if (!isCompleted) {
            onComplete();
          }
        }}
        disabled={isCompleted}
        className="item-checkbox"
      />

      <div className="item-content">
        <span className="item-title">{item.title}</span>

        <div className="item-meta">
          {item.due_date && (
            <span className="item-due-date">
              Due: {formatDate(item.due_date)}
            </span>
          )}
          <span className={`item-priority priority-${item.priority}`}>
            {item.priority}
          </span>
        </div>
      </div>
    </li>
  );
}

// ============================================================================
// Helpers
// ============================================================================

function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
    });
  } catch {
    return dateString;
  }
}

// ============================================================================
// Styles
// ============================================================================

const styles = `
.item-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.item-list-empty {
  text-align: center;
  padding: 24px;
  color: var(--text-secondary, #666);
}

.item-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
}

.item-row:hover {
  background: var(--bg-secondary, #f5f5f5);
}

.item-row.selected {
  background: var(--bg-secondary, #f5f5f5);
  outline: 2px solid var(--accent-color, #0066cc);
}

.item-row.completed .item-title {
  text-decoration: line-through;
  color: var(--text-secondary, #666);
}

.item-checkbox {
  width: 18px;
  height: 18px;
  margin-top: 2px;
  cursor: pointer;
  accent-color: var(--accent-color, #0066cc);
}

.item-checkbox:disabled {
  cursor: default;
}

.item-content {
  flex: 1;
  min-width: 0;
}

.item-title {
  display: block;
  font-weight: 500;
  color: var(--text-primary, #1a1a1a);
  word-break: break-word;
}

.item-meta {
  display: flex;
  gap: 8px;
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-secondary, #666);
}

.item-due-date {
  color: var(--text-secondary, #666);
}

.item-priority {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
}

.priority-low {
  background: #e8f5e9;
  color: #2e7d32;
}

.priority-medium {
  background: #fff3e0;
  color: #e65100;
}

.priority-high {
  background: #ffebee;
  color: #c62828;
}

/* Dark mode adjustments */
.dark-mode .priority-low {
  background: #1b5e20;
  color: #a5d6a7;
}

.dark-mode .priority-medium {
  background: #e65100;
  color: #ffcc80;
}

.dark-mode .priority-high {
  background: #b71c1c;
  color: #ef9a9a;
}
`;
