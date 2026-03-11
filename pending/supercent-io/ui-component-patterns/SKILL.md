---
name: ui-component-patterns
description: Build reusable, maintainable UI components following modern design patterns. Use when creating component libraries, implementing design systems, or building scalable frontend architectures. Handles React patterns, composition, prop design, TypeScript, and component best practices.
metadata:
  tags: UI-components, React, design-patterns, composition, TypeScript, reusable
  platforms: Claude, ChatGPT, Gemini
---


# UI Component Patterns


## When to use this skill

- **Building Component Libraries**: Creating reusable UI components
- **Implementing Design Systems**: Applying consistent UI patterns
- **Complex UI**: Components requiring multiple variants (Button, Modal, Dropdown)
- **Refactoring**: Extracting duplicate code into components

## Instructions

### Step 1: Props API Design

Design Props that are easy to use and extensible.

**Principles**:
- Clear names
- Reasonable defaults
- Type definitions with TypeScript
- Optional Props use optional marker (?)

**Example** (Button):
```tsx
interface ButtonProps {
  // Required
  children: React.ReactNode;

  // Optional (with defaults)
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  isLoading?: boolean;

  // Event handlers
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;

  // HTML attribute inheritance
  type?: 'button' | 'submit' | 'reset';
  className?: string;
}

function Button({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  isLoading = false,
  onClick,
  type = 'button',
  className = '',
  ...rest
}: ButtonProps) {
  const baseClasses = 'btn';
  const variantClasses = `btn-${variant}`;
  const sizeClasses = `btn-${size}`;
  const classes = `${baseClasses} ${variantClasses} ${sizeClasses} ${className}`;

  return (
    <button
      type={type}
      className={classes}
      disabled={disabled || isLoading}
      onClick={onClick}
      {...rest}
    >
      {isLoading ? <Spinner /> : children}
    </button>
  );
}

// Usage example
<Button variant="primary" size="lg" onClick={() => alert('Clicked!')}>
  Click Me
</Button>
```

### Step 2: Composition Pattern

Combine small components to build complex UI.

**Example** (Card):
```tsx
// Card component (Container)
interface CardProps {
  children: React.ReactNode;
  className?: string;
}

function Card({ children, className = '' }: CardProps) {
  return <div className={`card ${className}`}>{children}</div>;
}

// Card.Header
function CardHeader({ children }: { children: React.ReactNode }) {
  return <div className="card-header">{children}</div>;
}

// Card.Body
function CardBody({ children }: { children: React.ReactNode }) {
  return <div className="card-body">{children}</div>;
}

// Card.Footer
function CardFooter({ children }: { children: React.ReactNode }) {
  return <div className="card-footer">{children}</div>;
}

// Compound Component pattern
Card.Header = CardHeader;
Card.Body = CardBody;
Card.Footer = CardFooter;

export default Card;

// Usage
import Card from './Card';

function ProductCard() {
  return (
    <Card>
      <Card.Header>
        <h3>Product Name</h3>
      </Card.Header>
      <Card.Body>
        <img src="..." alt="Product" />
        <p>Product description here...</p>
      </Card.Body>
      <Card.Footer>
        <button>Add to Cart</button>
      </Card.Footer>
    </Card>
  );
}
```

### Step 3: Render Props / Children as Function

A pattern for flexible customization.

**Example** (Dropdown):
```tsx
interface DropdownProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  onSelect: (item: T) => void;
  placeholder?: string;
}

function Dropdown<T>({ items, renderItem, onSelect, placeholder }: DropdownProps<T>) {
  const [isOpen, setIsOpen] = useState(false);
  const [selected, setSelected] = useState<T | null>(null);

  const handleSelect = (item: T) => {
    setSelected(item);
    onSelect(item);
    setIsOpen(false);
  };

  return (
    <div className="dropdown">
      <button onClick={() => setIsOpen(!isOpen)}>
        {selected ? renderItem(selected, -1) : placeholder || 'Select...'}
      </button>

      {isOpen && (
        <ul className="dropdown-menu">
          {items.map((item, index) => (
            <li key={index} onClick={() => handleSelect(item)}>
              {renderItem(item, index)}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// Usage
interface User {
  id: string;
  name: string;
  avatar: string;
}

function UserDropdown() {
  const users: User[] = [...];

  return (
    <Dropdown
      items={users}
      placeholder="Select a user"
      renderItem={(user) => (
        <div className="user-item">
          <img src={user.avatar} alt={user.name} />
          <span>{user.name}</span>
        </div>
      )}
      onSelect={(user) => console.log('Selected:', user)}
    />
  );
}
```

### Step 4: Separating Logic with Custom Hooks

Separate UI from business logic.

**Example** (Modal):
```tsx
// hooks/useModal.ts
function useModal(initialOpen = false) {
  const [isOpen, setIsOpen] = useState(initialOpen);

  const open = useCallback(() => setIsOpen(true), []);
  const close = useCallback(() => setIsOpen(false), []);
  const toggle = useCallback(() => setIsOpen(prev => !prev), []);

  return { isOpen, open, close, toggle };
}

// components/Modal.tsx
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

function Modal({ isOpen, onClose, title, children }: ModalProps) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{title}</h2>
          <button onClick={onClose} aria-label="Close">×</button>
        </div>
        <div className="modal-body">{children}</div>
      </div>
    </div>
  );
}

// Usage
function App() {
  const { isOpen, open, close } = useModal();

  return (
    <>
      <button onClick={open}>Open Modal</button>
      <Modal isOpen={isOpen} onClose={close} title="My Modal">
        <p>Modal content here...</p>
      </Modal>
    </>
  );
}
```

### Step 5: Performance Optimization

Prevent unnecessary re-renders.

**React.memo**:
```tsx
// ❌ Bad: child re-renders every time parent re-renders
function ExpensiveComponent({ data }) {
  console.log('Rendering...');
  return <div>{/* Complex UI */}</div>;
}

// ✅ Good: re-renders only when props change
const ExpensiveComponent = React.memo(({ data }) => {
  console.log('Rendering...');
  return <div>{/* Complex UI */}</div>;
});
```

**useMemo & useCallback**:
```tsx
function ProductList({ products, category }: { products: Product[]; category: string }) {
  // ✅ Memoize filtered results
  const filteredProducts = useMemo(() => {
    return products.filter(p => p.category === category);
  }, [products, category]);

  // ✅ Memoize callback
  const handleAddToCart = useCallback((productId: string) => {
    // Add to cart
    console.log('Adding:', productId);
  }, []);

  return (
    <div>
      {filteredProducts.map(product => (
        <ProductCard
          key={product.id}
          product={product}
          onAddToCart={handleAddToCart}
        />
      ))}
    </div>
  );
}

const ProductCard = React.memo(({ product, onAddToCart }) => {
  return (
    <div>
      <h3>{product.name}</h3>
      <button onClick={() => onAddToCart(product.id)}>Add to Cart</button>
    </div>
  );
});
```

## Output format

### Component File Structure

```
components/
├── Button/
│   ├── Button.tsx           # Main component
│   ├── Button.test.tsx      # Tests
│   ├── Button.stories.tsx   # Storybook
│   ├── Button.module.css    # Styles
│   └── index.ts             # Export
├── Card/
│   ├── Card.tsx
│   ├── CardHeader.tsx
│   ├── CardBody.tsx
│   ├── CardFooter.tsx
│   └── index.ts
└── Modal/
    ├── Modal.tsx
    ├── useModal.ts          # Custom hook
    └── index.ts
```

### Component Template

```tsx
import React from 'react';

export interface ComponentProps {
  // Props definition
  children: React.ReactNode;
  className?: string;
}

/**
 * Component description
 *
 * @example
 * ```tsx
 * <Component>Hello</Component>
 * ```
 */
export const Component = React.forwardRef<HTMLDivElement, ComponentProps>(
  ({ children, className = '', ...rest }, ref) => {
    return (
      <div ref={ref} className={`component ${className}`} {...rest}>
        {children}
      </div>
    );
  }
);

Component.displayName = 'Component';

export default Component;
```

## Constraints

### Required Rules (MUST)

1. **Single Responsibility Principle**: One component has one role only
   - Button handles buttons only, Form handles forms only

2. **Props Type Definition**: TypeScript interface required
   - Enables auto-completion
   - Type safety

3. **Accessibility**: aria-*, role, tabindex, etc.

### Prohibited Rules (MUST NOT)

1. **Excessive props drilling**: Prohibited when 5+ levels deep
   - Use Context or Composition

2. **No Business Logic**: Prohibit API calls and complex calculations in UI components
   - Separate into custom hooks

3. **Inline objects/functions**: Performance degradation
   ```tsx
   // ❌ Bad example
   <Component style={{ color: 'red' }} onClick={() => handleClick()} />

   // ✅ Good example
   const style = { color: 'red' };
   const handleClick = useCallback(() => {...}, []);
   <Component style={style} onClick={handleClick} />
   ```

## Examples

### Example 1: Accordion (Compound Component)

```tsx
import React, { createContext, useContext, useState } from 'react';

// Share state with Context
const AccordionContext = createContext<{
  activeIndex: number | null;
  setActiveIndex: (index: number | null) => void;
} | null>(null);

function Accordion({ children }: { children: React.ReactNode }) {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);

  return (
    <AccordionContext.Provider value={{ activeIndex, setActiveIndex }}>
      <div className="accordion">{children}</div>
    </AccordionContext.Provider>
  );
}

function AccordionItem({ index, title, children }: {
  index: number;
  title: string;
  children: React.ReactNode;
}) {
  const context = useContext(AccordionContext);
  if (!context) throw new Error('AccordionItem must be used within Accordion');

  const { activeIndex, setActiveIndex } = context;
  const isActive = activeIndex === index;

  return (
    <div className="accordion-item">
      <button
        className="accordion-header"
        onClick={() => setActiveIndex(isActive ? null : index)}
        aria-expanded={isActive}
      >
        {title}
      </button>
      {isActive && <div className="accordion-body">{children}</div>}
    </div>
  );
}

Accordion.Item = AccordionItem;
export default Accordion;

// Usage
<Accordion>
  <Accordion.Item index={0} title="Section 1">
    Content for section 1
  </Accordion.Item>
  <Accordion.Item index={1} title="Section 2">
    Content for section 2
  </Accordion.Item>
</Accordion>
```

### Example 2: Polymorphic Component (as prop)

```tsx
type PolymorphicComponentProps<C extends React.ElementType> = {
  as?: C;
  children: React.ReactNode;
} & React.ComponentPropsWithoutRef<C>;

function Text<C extends React.ElementType = 'span'>({
  as,
  children,
  ...rest
}: PolymorphicComponentProps<C>) {
  const Component = as || 'span';
  return <Component {...rest}>{children}</Component>;
}

// Usage
<Text>Default span</Text>
<Text as="h1">Heading 1</Text>
<Text as="p" style={{ color: 'blue' }}>Paragraph</Text>
<Text as={Link} href="/about">Link</Text>
```

## Best practices

1. **Composition over Props**: Leverage children instead of many props
2. **Controlled vs Uncontrolled**: Choose based on situation
3. **Default Props**: Provide reasonable defaults
4. **Storybook**: Component documentation and development

## References

- [React Patterns](https://reactpatterns.com/)
- [Compound Components](https://kentcdodds.com/blog/compound-components-with-react-hooks)
- [Radix UI](https://www.radix-ui.com/) - Accessible components
- [Chakra UI](https://chakra-ui.com/) - Component library
- [shadcn/ui](https://ui.shadcn.com/) - Copy-paste components

## Metadata

### Version
- **Current Version**: 1.0.0
- **Last Updated**: 2025-01-01
- **Compatible Platforms**: Claude, ChatGPT, Gemini

### Related Skills
- [web-accessibility](../web-accessibility/SKILL.md): Accessible components
- [state-management](../state-management/SKILL.md): Component state management

### Tags
`#UI-components` `#React` `#design-patterns` `#composition` `#TypeScript` `#frontend`
