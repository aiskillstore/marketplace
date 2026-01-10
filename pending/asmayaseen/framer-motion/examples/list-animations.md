# List Animation Examples

Animated lists, staggered items, and reorderable lists.

## Basic Staggered List

```tsx
"use client";

import { motion } from "framer-motion";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      type: "spring",
      stiffness: 300,
      damping: 24,
    },
  },
};

export function StaggeredList({ items }: { items: string[] }) {
  return (
    <motion.ul
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-2"
    >
      {items.map((item, index) => (
        <motion.li
          key={index}
          variants={itemVariants}
          className="p-4 bg-card rounded-lg border"
        >
          {item}
        </motion.li>
      ))}
    </motion.ul>
  );
}
```

## List with Entry and Exit Animations

```tsx
"use client";

import { AnimatePresence, motion } from "framer-motion";

interface Item {
  id: string;
  text: string;
}

const itemVariants = {
  initial: { opacity: 0, height: 0, y: -10 },
  animate: {
    opacity: 1,
    height: "auto",
    y: 0,
    transition: {
      type: "spring",
      stiffness: 300,
      damping: 24,
    },
  },
  exit: {
    opacity: 0,
    height: 0,
    y: -10,
    transition: {
      duration: 0.2,
    },
  },
};

export function AnimatedList({ items }: { items: Item[] }) {
  return (
    <ul className="space-y-2">
      <AnimatePresence mode="popLayout">
        {items.map((item) => (
          <motion.li
            key={item.id}
            layout
            variants={itemVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            className="p-4 bg-card rounded-lg border"
          >
            {item.text}
          </motion.li>
        ))}
      </AnimatePresence>
    </ul>
  );
}
```

## Todo List with Add/Remove

```tsx
"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Plus, X } from "lucide-react";

interface Todo {
  id: string;
  text: string;
  completed: boolean;
}

export function AnimatedTodoList() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [newTodo, setNewTodo] = useState("");

  function addTodo() {
    if (!newTodo.trim()) return;
    setTodos([
      ...todos,
      { id: crypto.randomUUID(), text: newTodo, completed: false },
    ]);
    setNewTodo("");
  }

  function removeTodo(id: string) {
    setTodos(todos.filter((t) => t.id !== id));
  }

  function toggleTodo(id: string) {
    setTodos(
      todos.map((t) =>
        t.id === id ? { ...t, completed: !t.completed } : t
      )
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <input
          value={newTodo}
          onChange={(e) => setNewTodo(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && addTodo()}
          placeholder="Add todo..."
          className="flex-1 px-3 py-2 border rounded-lg"
        />
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={addTodo}
          className="p-2 bg-primary text-primary-foreground rounded-lg"
        >
          <Plus className="h-5 w-5" />
        </motion.button>
      </div>

      <ul className="space-y-2">
        <AnimatePresence mode="popLayout">
          {todos.map((todo) => (
            <motion.li
              key={todo.id}
              layout
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8, transition: { duration: 0.2 } }}
              className="flex items-center gap-3 p-4 bg-card rounded-lg border"
            >
              <motion.input
                type="checkbox"
                checked={todo.completed}
                onChange={() => toggleTodo(todo.id)}
                whileTap={{ scale: 0.9 }}
              />
              <motion.span
                animate={{
                  opacity: todo.completed ? 0.5 : 1,
                  textDecoration: todo.completed ? "line-through" : "none",
                }}
                className="flex-1"
              >
                {todo.text}
              </motion.span>
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => removeTodo(todo.id)}
                className="p-1 text-destructive"
              >
                <X className="h-4 w-4" />
              </motion.button>
            </motion.li>
          ))}
        </AnimatePresence>
      </ul>
    </div>
  );
}
```

## Reorderable List (Drag to Reorder)

```tsx
"use client";

import { useState } from "react";
import { Reorder } from "framer-motion";
import { GripVertical } from "lucide-react";

interface Item {
  id: string;
  name: string;
}

export function ReorderableList({ initialItems }: { initialItems: Item[] }) {
  const [items, setItems] = useState(initialItems);

  return (
    <Reorder.Group
      axis="y"
      values={items}
      onReorder={setItems}
      className="space-y-2"
    >
      {items.map((item) => (
        <Reorder.Item
          key={item.id}
          value={item}
          className="flex items-center gap-3 p-4 bg-card rounded-lg border cursor-grab active:cursor-grabbing"
        >
          <GripVertical className="h-5 w-5 text-muted-foreground" />
          <span>{item.name}</span>
        </Reorder.Item>
      ))}
    </Reorder.Group>
  );
}
```

## Reorderable with Custom Handle

```tsx
"use client";

import { useState } from "react";
import { Reorder, useDragControls } from "framer-motion";
import { GripVertical, X } from "lucide-react";

interface Item {
  id: string;
  name: string;
}

function ReorderItem({
  item,
  onRemove,
}: {
  item: Item;
  onRemove: (id: string) => void;
}) {
  const dragControls = useDragControls();

  return (
    <Reorder.Item
      value={item}
      dragControls={dragControls}
      dragListener={false}
      className="flex items-center gap-3 p-4 bg-card rounded-lg border"
    >
      {/* Drag handle */}
      <div
        onPointerDown={(e) => dragControls.start(e)}
        className="cursor-grab active:cursor-grabbing p-1 -m-1"
      >
        <GripVertical className="h-5 w-5 text-muted-foreground" />
      </div>

      {/* Content */}
      <span className="flex-1">{item.name}</span>

      {/* Remove button */}
      <button
        onClick={() => onRemove(item.id)}
        className="p-1 text-muted-foreground hover:text-destructive"
      >
        <X className="h-4 w-4" />
      </button>
    </Reorder.Item>
  );
}

export function ReorderableWithHandle({ initialItems }: { initialItems: Item[] }) {
  const [items, setItems] = useState(initialItems);

  function removeItem(id: string) {
    setItems(items.filter((item) => item.id !== id));
  }

  return (
    <Reorder.Group axis="y" values={items} onReorder={setItems} className="space-y-2">
      {items.map((item) => (
        <ReorderItem key={item.id} item={item} onRemove={removeItem} />
      ))}
    </Reorder.Group>
  );
}
```

## Grid Layout Animation

```tsx
"use client";

import { motion } from "framer-motion";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      type: "spring",
      stiffness: 300,
      damping: 24,
    },
  },
};

export function AnimatedGrid({ items }: { items: any[] }) {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
    >
      {items.map((item) => (
        <motion.div
          key={item.id}
          variants={itemVariants}
          whileHover={{ y: -5, boxShadow: "0 10px 30px -10px rgba(0,0,0,0.2)" }}
          className="p-6 bg-card rounded-xl border"
        >
          {item.content}
        </motion.div>
      ))}
    </motion.div>
  );
}
```

## Filterable List

```tsx
"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

interface Item {
  id: string;
  name: string;
  category: string;
}

export function FilterableList({ items }: { items: Item[] }) {
  const [filter, setFilter] = useState<string | null>(null);

  const categories = [...new Set(items.map((item) => item.category))];
  const filteredItems = filter
    ? items.filter((item) => item.category === filter)
    : items;

  return (
    <div className="space-y-4">
      {/* Filter buttons */}
      <div className="flex gap-2">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setFilter(null)}
          className={`px-4 py-2 rounded-lg ${
            filter === null ? "bg-primary text-primary-foreground" : "bg-muted"
          }`}
        >
          All
        </motion.button>
        {categories.map((category) => (
          <motion.button
            key={category}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setFilter(category)}
            className={`px-4 py-2 rounded-lg ${
              filter === category
                ? "bg-primary text-primary-foreground"
                : "bg-muted"
            }`}
          >
            {category}
          </motion.button>
        ))}
      </div>

      {/* List */}
      <motion.div layout className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        <AnimatePresence mode="popLayout">
          {filteredItems.map((item) => (
            <motion.div
              key={item.id}
              layout
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ duration: 0.3 }}
              className="p-4 bg-card rounded-lg border"
            >
              <p className="font-medium">{item.name}</p>
              <p className="text-sm text-muted-foreground">{item.category}</p>
            </motion.div>
          ))}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
```

## Infinite Scroll List

```tsx
"use client";

import { useRef, useState } from "react";
import { motion, useInView } from "framer-motion";

export function InfiniteScrollList() {
  const [items, setItems] = useState(Array.from({ length: 10 }, (_, i) => i));
  const loadMoreRef = useRef(null);
  const isInView = useInView(loadMoreRef);

  // Load more when sentinel comes into view
  React.useEffect(() => {
    if (isInView) {
      setItems((prev) => [
        ...prev,
        ...Array.from({ length: 10 }, (_, i) => prev.length + i),
      ]);
    }
  }, [isInView]);

  return (
    <div className="space-y-2">
      {items.map((item, index) => (
        <motion.div
          key={item}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: (index % 10) * 0.05 }}
          className="p-4 bg-card rounded-lg border"
        >
          Item {item}
        </motion.div>
      ))}

      {/* Load more trigger */}
      <div ref={loadMoreRef} className="h-10 flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full"
        />
      </div>
    </div>
  );
}
```

## Best Practices

1. **Use `layout` prop**: For smooth position transitions when items change
2. **Use `mode="popLayout"`**: Prevents layout jumps during exit animations
3. **Keep items keyed**: Always use unique, stable keys for list items
4. **Stagger subtly**: 0.05-0.1s between items is usually enough
5. **Spring for snappy**: Use spring animations for interactive lists
6. **Exit animations**: Keep exit animations shorter than enter (0.2s vs 0.3s)
