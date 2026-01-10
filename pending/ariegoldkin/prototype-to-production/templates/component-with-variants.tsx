/**
 * [ComponentName]
 *
 * Component with variant and size support. Use this template when the
 * prototype has multiple visual variations of the same element.
 *
 * @example
 * ```tsx
 * <ComponentName variant="primary" size="md">
 *   Click me
 * </ComponentName>
 * ```
 */

import React from 'react';

// ============================================================================
// Utility: className merger
// ============================================================================

function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ');
}

// ============================================================================
// Types & Interfaces
// ============================================================================

/**
 * Visual variants - extracted from prototype color/style patterns
 */
export type ComponentVariant = 'primary' | 'secondary' | 'outline' | 'ghost';

/**
 * Size variants - extracted from prototype sizing patterns
 */
export type ComponentSize = 'sm' | 'md' | 'lg';

export interface ComponentNameProps {
  /**
   * Visual style variant
   * @default 'primary'
   */
  variant?: ComponentVariant;

  /**
   * Component size
   * @default 'md'
   */
  size?: ComponentSize;

  /**
   * Disabled state
   * @default false
   */
  disabled?: boolean;

  /**
   * Loading state - shows loading indicator
   * @default false
   */
  loading?: boolean;

  /**
   * Additional CSS classes
   */
  className?: string;

  /**
   * Content
   */
  children: React.ReactNode;

  /**
   * Click handler
   */
  onClick?: (event: React.MouseEvent<HTMLElement>) => void;

  /**
   * Accessible label
   */
  'aria-label'?: string;
}

// ============================================================================
// Style Definitions (extracted from prototype)
// ============================================================================

const styles = {
  base: [
    'inline-flex items-center justify-center',
    'font-medium transition-colors',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
    'disabled:pointer-events-none disabled:opacity-50',
  ].join(' '),

  variants: {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus-visible:ring-blue-500',
    secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200 focus-visible:ring-gray-500',
    outline: 'border border-gray-300 bg-transparent hover:bg-gray-50 focus-visible:ring-gray-500',
    ghost: 'bg-transparent hover:bg-gray-100 focus-visible:ring-gray-500',
  },

  sizes: {
    sm: 'h-8 px-3 text-sm rounded-md gap-1.5',
    md: 'h-10 px-4 text-base rounded-lg gap-2',
    lg: 'h-12 px-6 text-lg rounded-lg gap-2.5',
  },
};

// ============================================================================
// Component Implementation
// ============================================================================

export const ComponentName = React.forwardRef<HTMLButtonElement, ComponentNameProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      disabled = false,
      loading = false,
      className,
      children,
      onClick,
      'aria-label': ariaLabel,
    },
    ref
  ) => {
    // =========================================================================
    // Render
    // =========================================================================

    return (
      <button
        ref={ref}
        type="button"
        className={cn(
          styles.base,
          styles.variants[variant],
          styles.sizes[size],
          className
        )}
        disabled={disabled || loading}
        onClick={onClick}
        aria-label={ariaLabel}
        aria-busy={loading}
      >
        {loading && (
          <svg
            className="animate-spin h-4 w-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        )}
        {children}
      </button>
    );
  }
);

ComponentName.displayName = 'ComponentName';

// ============================================================================
// Default Export
// ============================================================================

export default ComponentName;
