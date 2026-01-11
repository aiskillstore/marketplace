/**
 * Frontend Performance Optimization Patterns
 */

import React, { memo, useCallback, useMemo, useRef, lazy, Suspense } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';

// =============================================
// CODE SPLITTING
// =============================================

const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      {/* Routes would go here */}
    </Suspense>
  );
}

// =============================================
// REACT MEMO AND CALLBACKS
// =============================================

interface Item {
  id: string;
  name: string;
}

interface Props {
  items: Item[];
  onClick: (id: string) => void;
}

// Memoize expensive components
const ExpensiveList = memo(function ExpensiveList({ items, onClick }: Props) {
  return (
    <ul>
      {items.map(item => (
        <li key={item.id} onClick={() => onClick(item.id)}>
          {item.name}
        </li>
      ))}
    </ul>
  );
});

// Memoize callbacks passed to children
function Parent({ items }: { items: Item[] }) {
  const handleClick = useCallback((id: string) => {
    console.log('Clicked:', id);
  }, []);

  return <ExpensiveList items={items} onClick={handleClick} />;
}

// Memoize expensive calculations
function ExpensiveComponent({ data }: { data: number[] }) {
  const processedData = useMemo(() => {
    return data.reduce((sum, n) => sum + n, 0);
  }, [data]);

  return <div>Sum: {processedData}</div>;
}

// =============================================
// VIRTUALIZATION FOR LONG LISTS
// =============================================

function VirtualList({ items }: { items: Item[] }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50, // Estimated row height
  });

  return (
    <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
      <div style={{ height: virtualizer.getTotalSize(), position: 'relative' }}>
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: virtualItem.start,
              height: virtualItem.size,
              width: '100%',
            }}
          >
            {items[virtualItem.index].name}
          </div>
        ))}
      </div>
    </div>
  );
}

// =============================================
// AVOID LAYOUT THRASHING
// =============================================

// BAD: Causes multiple layout recalculations
function layoutThrashingBad(elements: HTMLElement[]) {
  elements.forEach(el => {
    const height = el.offsetHeight; // Read
    el.style.width = height + 'px'; // Write
  });
}

// GOOD: Batch reads, then batch writes
function layoutThrashingGood(elements: HTMLElement[]) {
  const heights = elements.map(el => el.offsetHeight); // All reads
  elements.forEach((el, i) => {
    el.style.width = heights[i] + 'px'; // All writes
  });
}

// =============================================
// TREE SHAKING - IMPORT PATTERNS
// =============================================

// BAD: Import entire library
// import _ from 'lodash';
// _.debounce(fn, 300);

// GOOD: Import only what you need
// import debounce from 'lodash/debounce';
// debounce(fn, 300);

// BEST: Use native or smaller alternatives
export function debounce<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
}

export { App, Parent, ExpensiveComponent, VirtualList };
