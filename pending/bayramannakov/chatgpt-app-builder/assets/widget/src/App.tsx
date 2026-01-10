/**
 * Main Widget Application
 *
 * Entry point for the ChatGPT widget.
 */

import React, { useEffect, useRef } from "react";
import { createRoot } from "react-dom/client";
import { useOpenAI, useToolOutput, useWidgetState, useTheme } from "./hooks/useOpenAI";
import { ItemList } from "./components/ItemList";
import "./types/openai";

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

interface ToolOutput {
  items: Item[];
  total: number;
  hasMore: boolean;
  error?: boolean;
}

interface WidgetState {
  selectedId: string | null;
  filter: "all" | "active" | "completed";
}

// ============================================================================
// Main App Component
// ============================================================================

function App() {
  const theme = useTheme();
  const output = useToolOutput<ToolOutput>();
  const [state, setState] = useWidgetState<WidgetState>({
    selectedId: null,
    filter: "all",
  });
  const containerRef = useRef<HTMLDivElement>(null);

  // Report height changes to ChatGPT
  useEffect(() => {
    const updateHeight = () => {
      if (containerRef.current) {
        window.openai?.notifyIntrinsicHeight(containerRef.current.scrollHeight);
      }
    };

    updateHeight();

    const observer = new ResizeObserver(updateHeight);
    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => observer.disconnect();
  }, [output]);

  // Handle item completion
  const handleComplete = async (id: string) => {
    try {
      await window.openai?.callTool("{{APP_PREFIX}}_complete_item", { id });
    } catch (error) {
      console.error("Failed to complete item:", error);
    }
  };

  // Handle item selection
  const handleSelect = (id: string) => {
    setState((prev) => ({
      ...prev,
      selectedId: prev.selectedId === id ? null : id,
    }));
  };

  // Handle filter change
  const handleFilterChange = (filter: "all" | "active" | "completed") => {
    setState((prev) => ({ ...prev, filter }));
  };

  // Filter items based on current filter
  const filteredItems = output?.items?.filter((item) => {
    if (state.filter === "all") return true;
    return item.status === state.filter;
  }) || [];

  // Error state
  if (output?.error) {
    return (
      <div ref={containerRef} className={`widget-container ${theme === "dark" ? "dark-mode" : ""}`}>
        <div className="error-state">
          <p>Something went wrong. Please try again.</p>
        </div>
      </div>
    );
  }

  // Empty state
  if (!output?.items || output.items.length === 0) {
    return (
      <div ref={containerRef} className={`widget-container ${theme === "dark" ? "dark-mode" : ""}`}>
        <div className="empty-state">
          <p>No items found.</p>
          <button
            onClick={() => window.openai?.sendFollowUpMessage({ prompt: "Create a new item" })}
          >
            Create your first item
          </button>
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className={`widget-container ${theme === "dark" ? "dark-mode" : ""}`}>
      {/* Filter tabs */}
      <div className="filter-tabs">
        {(["all", "active", "completed"] as const).map((filter) => (
          <button
            key={filter}
            className={`filter-tab ${state.filter === filter ? "active" : ""}`}
            onClick={() => handleFilterChange(filter)}
          >
            {filter.charAt(0).toUpperCase() + filter.slice(1)}
          </button>
        ))}
      </div>

      {/* Item list */}
      <ItemList
        items={filteredItems}
        selectedId={state.selectedId}
        onSelect={handleSelect}
        onComplete={handleComplete}
      />

      {/* Load more */}
      {output.hasMore && (
        <button
          className="load-more"
          onClick={() =>
            window.openai?.sendFollowUpMessage({ prompt: "Show more items" })
          }
        >
          Load more
        </button>
      )}
    </div>
  );
}

// ============================================================================
// Styles
// ============================================================================

const styles = `
.widget-container {
  padding: 16px;
  min-height: 100px;
}

.filter-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--border-color, #e0e0e0);
  padding-bottom: 8px;
}

.filter-tab {
  padding: 6px 12px;
  border: none;
  background: transparent;
  color: var(--text-secondary, #666);
  cursor: pointer;
  border-radius: 4px;
  font-size: 13px;
}

.filter-tab:hover {
  background: var(--bg-secondary, #f5f5f5);
}

.filter-tab.active {
  background: var(--accent-color, #0066cc);
  color: white;
}

.empty-state,
.error-state {
  text-align: center;
  padding: 32px 16px;
  color: var(--text-secondary, #666);
}

.empty-state button,
.load-more {
  margin-top: 12px;
  padding: 8px 16px;
  background: var(--accent-color, #0066cc);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.empty-state button:hover,
.load-more:hover {
  opacity: 0.9;
}

.load-more {
  display: block;
  width: 100%;
  margin-top: 16px;
  background: transparent;
  color: var(--accent-color, #0066cc);
  border: 1px solid var(--accent-color, #0066cc);
}

/* Dark mode */
.dark-mode {
  --bg-primary: #1a1a1a;
  --bg-secondary: #2d2d2d;
  --text-primary: #ffffff;
  --text-secondary: #a0a0a0;
  --border-color: #404040;
}
`;

// ============================================================================
// Mount
// ============================================================================

// Inject styles
const styleEl = document.createElement("style");
styleEl.textContent = styles;
document.head.appendChild(styleEl);

// Mount React app
const root = document.getElementById("root");
if (root) {
  createRoot(root).render(<App />);
}
