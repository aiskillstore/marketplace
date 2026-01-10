# Gestures Reference

Framer Motion provides gesture recognition for hover, tap, pan, and drag.

## Hover Gestures

### Basic Hover

```tsx
<motion.div
  whileHover={{ scale: 1.1 }}
  onHoverStart={() => console.log("Hover started")}
  onHoverEnd={() => console.log("Hover ended")}
>
  Hover me
</motion.div>
```

### Hover with Transition

```tsx
<motion.button
  whileHover={{
    scale: 1.05,
    backgroundColor: "#3b82f6",
    color: "#ffffff",
  }}
  transition={{ duration: 0.2 }}
>
  Hover Button
</motion.button>
```

### Hover Card Effect

```tsx
<motion.div
  whileHover={{
    y: -5,
    boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)",
  }}
  transition={{ type: "spring", stiffness: 300 }}
  className="p-6 rounded-lg border"
>
  Card content
</motion.div>
```

## Tap Gestures

### Basic Tap

```tsx
<motion.button
  whileTap={{ scale: 0.95 }}
  onTap={() => console.log("Tapped!")}
>
  Click me
</motion.button>
```

### Tap Events

```tsx
<motion.button
  whileTap={{ scale: 0.95 }}
  onTapStart={(event, info) => {
    console.log("Tap started at", info.point);
  }}
  onTap={(event, info) => {
    console.log("Tap completed at", info.point);
  }}
  onTapCancel={() => {
    console.log("Tap cancelled");
  }}
>
  Button
</motion.button>
```

### Combined Hover + Tap

```tsx
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  transition={{ type: "spring", stiffness: 400, damping: 17 }}
>
  Interactive Button
</motion.button>
```

## Focus Gestures

```tsx
<motion.input
  whileFocus={{
    scale: 1.02,
    borderColor: "#3b82f6",
    boxShadow: "0 0 0 2px rgba(59, 130, 246, 0.5)",
  }}
  className="px-4 py-2 border rounded"
/>
```

## Pan Gestures

Pan recognizes movement without dragging.

```tsx
<motion.div
  onPan={(event, info) => {
    console.log("Delta:", info.delta.x, info.delta.y);
    console.log("Offset:", info.offset.x, info.offset.y);
    console.log("Point:", info.point.x, info.point.y);
    console.log("Velocity:", info.velocity.x, info.velocity.y);
  }}
  onPanStart={(event, info) => console.log("Pan started")}
  onPanEnd={(event, info) => console.log("Pan ended")}
>
  Pan me
</motion.div>
```

### Swipe Detection

```tsx
function SwipeCard({ onSwipe }) {
  return (
    <motion.div
      onPanEnd={(event, info) => {
        const threshold = 100;
        const velocity = 500;

        if (info.offset.x > threshold || info.velocity.x > velocity) {
          onSwipe("right");
        } else if (info.offset.x < -threshold || info.velocity.x < -velocity) {
          onSwipe("left");
        }
      }}
    >
      Swipe me
    </motion.div>
  );
}
```

## Drag Gestures

### Basic Drag

```tsx
<motion.div drag>
  Drag me anywhere
</motion.div>

// Constrained to axis
<motion.div drag="x">Horizontal only</motion.div>
<motion.div drag="y">Vertical only</motion.div>
```

### Drag Constraints

```tsx
// Pixel constraints
<motion.div
  drag
  dragConstraints={{
    top: -100,
    left: -100,
    right: 100,
    bottom: 100,
  }}
>
  Constrained drag
</motion.div>

// Reference element
const constraintsRef = useRef(null);

<div ref={constraintsRef} className="w-96 h-96 border">
  <motion.div
    drag
    dragConstraints={constraintsRef}
    className="w-20 h-20 bg-blue-500 rounded"
  />
</div>
```

### Drag Elasticity

```tsx
<motion.div
  drag
  dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
  dragElastic={0.2}  // 0 = no elasticity, 1 = full elasticity
>
  Elastic drag
</motion.div>
```

### Drag Momentum

```tsx
<motion.div
  drag
  dragMomentum={true}  // Enable momentum (default)
  dragTransition={{ bounceStiffness: 600, bounceDamping: 20 }}
>
  Momentum drag
</motion.div>
```

### Drag Snap to Origin

```tsx
<motion.div drag dragSnapToOrigin>
  Snaps back when released
</motion.div>
```

### Drag Events

```tsx
<motion.div
  drag
  onDragStart={(event, info) => {
    console.log("Drag started at", info.point);
  }}
  onDrag={(event, info) => {
    console.log("Dragging:", info.point, info.delta, info.offset, info.velocity);
  }}
  onDragEnd={(event, info) => {
    console.log("Drag ended at", info.point);
    console.log("Velocity:", info.velocity);
  }}
>
  Drag me
</motion.div>
```

### Drag Direction Lock

```tsx
<motion.div
  drag
  dragDirectionLock
  onDirectionLock={(axis) => console.log(`Locked to ${axis}`)}
>
  Locks to first detected direction
</motion.div>
```

### Drag Controls

```tsx
import { motion, useDragControls } from "framer-motion";

function DraggableCard() {
  const dragControls = useDragControls();

  return (
    <>
      {/* Handle to initiate drag */}
      <div
        onPointerDown={(e) => dragControls.start(e)}
        className="cursor-grab"
      >
        Drag handle
      </div>

      <motion.div drag dragControls={dragControls} dragListener={false}>
        Draggable content (only via handle)
      </motion.div>
    </>
  );
}
```

### While Dragging Animation

```tsx
<motion.div
  drag
  whileDrag={{
    scale: 1.1,
    cursor: "grabbing",
    boxShadow: "0 10px 30px rgba(0,0,0,0.2)",
  }}
  className="cursor-grab"
>
  Drag me
</motion.div>
```

## Sortable List (Reorder)

```tsx
import { Reorder } from "framer-motion";

function SortableList() {
  const [items, setItems] = useState([1, 2, 3, 4]);

  return (
    <Reorder.Group
      axis="y"
      values={items}
      onReorder={setItems}
      className="space-y-2"
    >
      {items.map((item) => (
        <Reorder.Item
          key={item}
          value={item}
          className="p-4 bg-white rounded shadow cursor-grab"
        >
          Item {item}
        </Reorder.Item>
      ))}
    </Reorder.Group>
  );
}
```

### Custom Drag Handle for Reorder

```tsx
import { Reorder, useDragControls } from "framer-motion";

function SortableItem({ item }) {
  const dragControls = useDragControls();

  return (
    <Reorder.Item
      value={item}
      dragControls={dragControls}
      dragListener={false}
      className="flex items-center gap-2 p-4 bg-white rounded"
    >
      <div
        onPointerDown={(e) => dragControls.start(e)}
        className="cursor-grab p-1"
      >
        <GripVertical className="h-4 w-4" />
      </div>
      <span>{item.name}</span>
    </Reorder.Item>
  );
}
```

## Gesture Propagation

Control which element responds to gestures:

```tsx
// Stop propagation
<motion.div whileTap={{ scale: 0.95 }}>
  <motion.button
    whileTap={{ scale: 1.1 }}
    // Child tap doesn't trigger parent
  >
    Button
  </motion.button>
</motion.div>
```

## Best Practices

1. **Use springs for interactions**: More natural feel than tween
2. **Keep scale changes subtle**: 0.95-1.05 range for tap/hover
3. **Add visual feedback**: Shadow, color changes for hover
4. **Use drag constraints**: Prevent elements from being lost off-screen
5. **Handle touch devices**: Hover animations may not work on touch
6. **Respect reduced motion**: Skip animations for users who prefer reduced motion
