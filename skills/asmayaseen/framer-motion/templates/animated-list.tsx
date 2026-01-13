/**
 * Animated List Template
 *
 * A comprehensive animated list component with:
 * - Staggered entrance animations
 * - Smooth entry/exit for items
 * - Drag-to-reorder functionality
 * - Item removal animations
 *
 * Usage:
 * ```tsx
 * import { AnimatedList, AnimatedListItem } from "@/components/animated-list";
 *
 * function MyList() {
 *   const [items, setItems] = useState([...]);
 *
 *   return (
 *     <AnimatedList>
 *       {items.map((item) => (
 *         <AnimatedListItem key={item.id}>
 *           {item.content}
 *         </AnimatedListItem>
 *       ))}
 *     </AnimatedList>
 *   );
 * }
 * ```
 */

"use client";

import { ReactNode, useState } from "react";
import {
  AnimatePresence,
  motion,
  Reorder,
  useDragControls,
  Variants,
} from "framer-motion";
import { GripVertical, X } from "lucide-react";

// ============================================================================
// Animation Variants
// ============================================================================

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.1,
    },
  },
};

const itemVariants: Variants = {
  hidden: {
    opacity: 0,
    y: 20,
    scale: 0.95,
  },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      type: "spring",
      stiffness: 300,
      damping: 24,
    },
  },
  exit: {
    opacity: 0,
    scale: 0.9,
    x: -20,
    transition: {
      duration: 0.2,
    },
  },
};

// ============================================================================
// Basic Animated List (No Reordering)
// ============================================================================

interface AnimatedListProps {
  children: ReactNode;
  className?: string;
}

/**
 * AnimatedList - Container with staggered children animation
 *
 * Use with AnimatedListItem for individual item animations.
 */
export function AnimatedList({ children, className }: AnimatedListProps) {
  return (
    <motion.ul
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className={className}
    >
      {children}
    </motion.ul>
  );
}

interface AnimatedListItemProps {
  children: ReactNode;
  className?: string;
  /**
   * Called when remove button is clicked
   */
  onRemove?: () => void;
  /**
   * Show remove button on hover
   * @default false
   */
  showRemove?: boolean;
}

/**
 * AnimatedListItem - Individual list item with animations
 *
 * Features:
 * - Enters with staggered spring animation
 * - Exit animation when removed
 * - Optional remove button on hover
 */
export function AnimatedListItem({
  children,
  className,
  onRemove,
  showRemove = false,
}: AnimatedListItemProps) {
  return (
    <motion.li
      layout
      variants={itemVariants}
      exit="exit"
      className={`group relative ${className || ""}`}
    >
      {children}
      {showRemove && onRemove && (
        <motion.button
          initial={{ opacity: 0, scale: 0.8 }}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity p-1 text-muted-foreground hover:text-destructive"
          onClick={onRemove}
        >
          <X className="h-4 w-4" />
        </motion.button>
      )}
    </motion.li>
  );
}

// ============================================================================
// Animated List with Entry/Exit (AnimatePresence)
// ============================================================================

interface DynamicListProps<T> {
  items: T[];
  keyExtractor: (item: T) => string;
  renderItem: (item: T, index: number) => ReactNode;
  className?: string;
}

/**
 * DynamicList - List with smooth add/remove animations
 *
 * Wraps items in AnimatePresence for exit animations.
 *
 * @example
 * ```tsx
 * <DynamicList
 *   items={todos}
 *   keyExtractor={(todo) => todo.id}
 *   renderItem={(todo) => <TodoItem todo={todo} />}
 * />
 * ```
 */
export function DynamicList<T>({
  items,
  keyExtractor,
  renderItem,
  className,
}: DynamicListProps<T>) {
  return (
    <motion.ul layout className={className}>
      <AnimatePresence mode="popLayout">
        {items.map((item, index) => (
          <motion.li
            key={keyExtractor(item)}
            layout
            initial={{ opacity: 0, scale: 0.8, y: -10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, x: -50 }}
            transition={{
              type: "spring",
              stiffness: 300,
              damping: 24,
            }}
          >
            {renderItem(item, index)}
          </motion.li>
        ))}
      </AnimatePresence>
    </motion.ul>
  );
}

// ============================================================================
// Reorderable List (Drag to Reorder)
// ============================================================================

interface ReorderableListProps<T> {
  items: T[];
  onReorder: (items: T[]) => void;
  keyExtractor: (item: T) => string;
  renderItem: (item: T, dragControls: ReturnType<typeof useDragControls>) => ReactNode;
  className?: string;
  /**
   * Axis for reordering
   * @default "y"
   */
  axis?: "x" | "y";
}

/**
 * ReorderableList - Drag-to-reorder list
 *
 * Uses Framer Motion's Reorder component for smooth reordering.
 *
 * @example
 * ```tsx
 * const [items, setItems] = useState(initialItems);
 *
 * <ReorderableList
 *   items={items}
 *   onReorder={setItems}
 *   keyExtractor={(item) => item.id}
 *   renderItem={(item, dragControls) => (
 *     <ReorderableItem item={item} dragControls={dragControls} />
 *   )}
 * />
 * ```
 */
export function ReorderableList<T>({
  items,
  onReorder,
  keyExtractor,
  renderItem,
  className,
  axis = "y",
}: ReorderableListProps<T>) {
  return (
    <Reorder.Group
      axis={axis}
      values={items}
      onReorder={onReorder}
      className={className}
    >
      {items.map((item) => (
        <ReorderableItemWrapper
          key={keyExtractor(item)}
          item={item}
          renderItem={renderItem}
        />
      ))}
    </Reorder.Group>
  );
}

// Internal wrapper to provide drag controls
function ReorderableItemWrapper<T>({
  item,
  renderItem,
}: {
  item: T;
  renderItem: (item: T, dragControls: ReturnType<typeof useDragControls>) => ReactNode;
}) {
  const dragControls = useDragControls();

  return (
    <Reorder.Item
      value={item}
      dragControls={dragControls}
      dragListener={false}
    >
      {renderItem(item, dragControls)}
    </Reorder.Item>
  );
}

// ============================================================================
// Drag Handle Component
// ============================================================================

interface DragHandleProps {
  dragControls: ReturnType<typeof useDragControls>;
  className?: string;
}

/**
 * DragHandle - Grab handle for reorderable items
 *
 * @example
 * ```tsx
 * renderItem={(item, dragControls) => (
 *   <div className="flex items-center gap-2">
 *     <DragHandle dragControls={dragControls} />
 *     <span>{item.name}</span>
 *   </div>
 * )}
 * ```
 */
export function DragHandle({ dragControls, className }: DragHandleProps) {
  return (
    <div
      onPointerDown={(e) => dragControls.start(e)}
      className={`cursor-grab active:cursor-grabbing touch-none ${className || ""}`}
    >
      <GripVertical className="h-5 w-5 text-muted-foreground" />
    </div>
  );
}

// ============================================================================
// Complete Reorderable Todo List Example
// ============================================================================

interface TodoItem {
  id: string;
  text: string;
  completed: boolean;
}

interface ReorderableTodoListProps {
  initialItems?: TodoItem[];
}

/**
 * ReorderableTodoList - Complete example of an animated, reorderable todo list
 *
 * Features:
 * - Drag to reorder
 * - Add new items
 * - Remove items with animation
 * - Toggle completion state
 */
export function ReorderableTodoList({
  initialItems = [],
}: ReorderableTodoListProps) {
  const [items, setItems] = useState<TodoItem[]>(initialItems);
  const [newItemText, setNewItemText] = useState("");

  function addItem() {
    if (!newItemText.trim()) return;
    setItems([
      ...items,
      {
        id: crypto.randomUUID(),
        text: newItemText.trim(),
        completed: false,
      },
    ]);
    setNewItemText("");
  }

  function removeItem(id: string) {
    setItems(items.filter((item) => item.id !== id));
  }

  function toggleItem(id: string) {
    setItems(
      items.map((item) =>
        item.id === id ? { ...item, completed: !item.completed } : item
      )
    );
  }

  return (
    <div className="space-y-4">
      {/* Add item form */}
      <div className="flex gap-2">
        <input
          type="text"
          value={newItemText}
          onChange={(e) => setNewItemText(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && addItem()}
          placeholder="Add new item..."
          className="flex-1 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary outline-none"
        />
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={addItem}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-lg"
        >
          Add
        </motion.button>
      </div>

      {/* Reorderable list */}
      <Reorder.Group
        axis="y"
        values={items}
        onReorder={setItems}
        className="space-y-2"
      >
        <AnimatePresence mode="popLayout">
          {items.map((item) => (
            <TodoListItem
              key={item.id}
              item={item}
              onToggle={() => toggleItem(item.id)}
              onRemove={() => removeItem(item.id)}
            />
          ))}
        </AnimatePresence>
      </Reorder.Group>

      {/* Empty state */}
      {items.length === 0 && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center text-muted-foreground py-8"
        >
          No items yet. Add one above!
        </motion.p>
      )}
    </div>
  );
}

// Internal todo item component
function TodoListItem({
  item,
  onToggle,
  onRemove,
}: {
  item: TodoItem;
  onToggle: () => void;
  onRemove: () => void;
}) {
  const dragControls = useDragControls();

  return (
    <Reorder.Item
      value={item}
      dragControls={dragControls}
      dragListener={false}
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.9, x: -50 }}
      transition={{ type: "spring", stiffness: 300, damping: 24 }}
      className="flex items-center gap-3 p-4 bg-card rounded-lg border"
    >
      {/* Drag handle */}
      <div
        onPointerDown={(e) => dragControls.start(e)}
        className="cursor-grab active:cursor-grabbing touch-none"
      >
        <GripVertical className="h-5 w-5 text-muted-foreground" />
      </div>

      {/* Checkbox */}
      <motion.input
        type="checkbox"
        checked={item.completed}
        onChange={onToggle}
        whileTap={{ scale: 0.9 }}
        className="h-4 w-4"
      />

      {/* Text */}
      <motion.span
        animate={{
          opacity: item.completed ? 0.5 : 1,
          textDecoration: item.completed ? "line-through" : "none",
        }}
        className="flex-1"
      >
        {item.text}
      </motion.span>

      {/* Remove button */}
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={onRemove}
        className="p-1 text-muted-foreground hover:text-destructive"
      >
        <X className="h-4 w-4" />
      </motion.button>
    </Reorder.Item>
  );
}
