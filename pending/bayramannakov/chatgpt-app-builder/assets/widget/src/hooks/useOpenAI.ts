/**
 * React Hooks for window.openai
 *
 * These hooks provide reactive access to the ChatGPT widget API.
 */

import {
  useSyncExternalStore,
  useState,
  useEffect,
  useCallback,
  SetStateAction,
} from "react";

// ============================================================================
// Types
// ============================================================================

type OpenAIKey = keyof typeof window.openai;

interface SetGlobalsEvent extends CustomEvent {
  detail: { globals: Partial<typeof window.openai> };
}

// ============================================================================
// useOpenAI - Base hook for reactive global access
// ============================================================================

/**
 * Subscribe to a specific window.openai property reactively.
 *
 * @example
 * const theme = useOpenAI("theme");
 * const output = useOpenAI("toolOutput");
 */
export function useOpenAI<K extends OpenAIKey>(key: K): (typeof window.openai)[K] {
  return useSyncExternalStore(
    // Subscribe to changes
    (onChange) => {
      const handleSetGlobal = (event: Event) => {
        const customEvent = event as SetGlobalsEvent;
        if (customEvent.detail.globals[key] !== undefined) {
          onChange();
        }
      };

      window.addEventListener("openai:set_globals", handleSetGlobal, {
        passive: true,
      });

      return () => {
        window.removeEventListener("openai:set_globals", handleSetGlobal);
      };
    },
    // Get current value (client)
    () => window.openai?.[key],
    // Get current value (server/SSR - not used in widgets but required)
    () => window.openai?.[key]
  );
}

// ============================================================================
// useToolOutput - Access structured tool response
// ============================================================================

/**
 * Get the structuredContent from the tool response.
 *
 * @example
 * interface MyOutput { items: Item[]; total: number; }
 * const { items, total } = useToolOutput<MyOutput>();
 */
export function useToolOutput<T = Record<string, unknown>>(): T {
  return useOpenAI("toolOutput") as T;
}

// ============================================================================
// useToolMetadata - Access _meta from tool response
// ============================================================================

/**
 * Get the _meta payload from the tool response (widget-only data).
 *
 * @example
 * interface MyMeta { fullItems: Item[]; pagination: { hasMore: boolean }; }
 * const { fullItems, pagination } = useToolMetadata<MyMeta>();
 */
export function useToolMetadata<T = Record<string, unknown>>(): T {
  return useOpenAI("toolResponseMetadata") as T;
}

// ============================================================================
// useWidgetState - Persistent state across widget renders
// ============================================================================

/**
 * Manage widget state that persists across re-renders.
 *
 * State is stored via window.openai.setWidgetState and survives
 * widget interactions, but resets when user types in main composer.
 *
 * @example
 * const [state, setState] = useWidgetState({ selectedId: null });
 * setState({ selectedId: "123" });
 */
export function useWidgetState<T extends Record<string, unknown>>(
  defaultState: T | (() => T)
): readonly [T, (state: SetStateAction<T>) => void] {
  const widgetStateFromWindow = useOpenAI("widgetState") as T | null;

  const [widgetState, _setWidgetState] = useState<T>(() => {
    // Use window state if available, otherwise use default
    if (widgetStateFromWindow) {
      return widgetStateFromWindow;
    }
    return typeof defaultState === "function" ? defaultState() : defaultState;
  });

  // Sync with window state changes
  useEffect(() => {
    if (widgetStateFromWindow) {
      _setWidgetState(widgetStateFromWindow);
    }
  }, [widgetStateFromWindow]);

  // Setter that syncs to window.openai
  const setWidgetState = useCallback((state: SetStateAction<T>) => {
    _setWidgetState((prevState) => {
      const newState =
        typeof state === "function" ? state(prevState) : state;
      // Sync to ChatGPT
      window.openai?.setWidgetState(newState);
      return newState;
    });
  }, []);

  return [widgetState, setWidgetState] as const;
}

// ============================================================================
// useTheme - Current theme (light/dark)
// ============================================================================

/**
 * Get the current ChatGPT theme.
 *
 * @example
 * const theme = useTheme();
 * return <div className={theme === "dark" ? "dark-mode" : ""}>...</div>;
 */
export function useTheme(): "light" | "dark" {
  return useOpenAI("theme") || "light";
}

// ============================================================================
// useDisplayMode - Current display mode
// ============================================================================

/**
 * Get the current display mode.
 *
 * @example
 * const mode = useDisplayMode();
 * if (mode === "fullscreen") { ... }
 */
export function useDisplayMode(): "inline" | "expanded" | "pip" | "fullscreen" {
  return useOpenAI("displayMode") || "inline";
}

// ============================================================================
// useLocale - User's locale
// ============================================================================

/**
 * Get the user's locale for internationalization.
 *
 * @example
 * const locale = useLocale(); // "en-US"
 */
export function useLocale(): string {
  return useOpenAI("locale") || "en-US";
}
