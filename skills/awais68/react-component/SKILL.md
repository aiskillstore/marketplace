---
name: react-component
description: |
  Use when creating UI components in React - functional components, hooks, custom hooks, or component composition patterns.
  NOT when backend logic, API routes, or non-React frameworks are involved.
  Triggers: "create component", "build widget", "KPI card", "form", "modal", "custom hook", "useContext", "useState", "useEffect".
---

# React Component Skill

## Overview

Expert guidance for building React functional components, hooks, and composition patterns. Focuses on TypeScript, performance, accessibility, and modern React best practices.

## When This Skill Applies

This skill triggers when users request:
- **UI Components**: "Create a student KPI card", "Build a modal", "Form component"
- **Hooks**: "Custom attendance hook", "useContext for theme", "useState for data"
- **Patterns**: "Component composition", "HOC", "render props"
- **ERP Widgets**: KPI cards, forms, data tables, dashboards

## Core Rules

### 1. Functional Components Always

```typescript
// ✅ GOOD: Functional component with TypeScript
interface StudentKPICardProps {
  studentName: string;
  attendance: number;
  loading?: boolean;
}

export const StudentKPICard = React.memo(({ studentName, attendance, loading = false }: StudentKPICardProps) => {
  const [isHovered, setIsHovered] = useState(false);

  if (loading) return <LoadingSkeleton />;

  return <div>{/* content */}</div>;
});
```

**Requirements:**
- Always use functional components (no class components)
- Type all props interfaces explicitly
- Use `React.memo` for components receiving same props frequently
- Use `React.forwardRef` when ref forwarding is needed

### 2. Hooks Usage

```typescript
// ✅ GOOD: Proper hook usage with cleanup
export const AttendanceMonitor = ({ studentId }: { studentId: string }) => {
  const [data, setData] = useState(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const fetchAttendance = async () => {
      try {
        const result = await api.getAttendance(studentId);
        if (isMounted) setData(result);
      } catch (err) {
        if (isMounted) setError(err.message);
      }
    };
    fetchAttendance();

    return () => {
      isMounted = false;
    };
  }, [studentId]);

  return /* JSX */;
};
```

**Requirements:**
- `useState`: For local component state only
- `useEffect`: For side-effects with proper cleanup functions
- `useContext`: For global state (theme, auth, language)
- Always include all dependencies in dependency array
- Use `useCallback`/`useMemo` for expensive operations in lists

### 3. Custom Hooks

```typescript
// ✅ GOOD: Custom hook with proper types
interface UseAttendanceResult {
  data: AttendanceData | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export const useAttendance = (studentId: string): UseAttendanceResult => {
  const [data, setData] = useState<AttendanceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAttendance = useCallback(async () => {
    setLoading(true);
    try {
      const result = await api.getAttendance(studentId);
      setData(result);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [studentId]);

  useEffect(() => {
    fetchAttendance();
  }, [fetchAttendance]);

  return { data, loading, error, refetch: fetchAttendance };
};
```

**Requirements:**
- All custom hooks must start with `use` prefix
- Extract reusable logic into hooks
- Return typed interfaces for hook results
- Include loading, error states, and retry mechanisms
- Keep hooks focused on single responsibility

### 4. Component Composition

```typescript
// ✅ GOOD: Composition via children prop
interface CardProps {
  title: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

export const Card = ({ title, children, footer }: CardProps) => (
  <div className="card">
    <h2>{title}</h2>
    <div className="card-content">{children}</div>
    {footer && <div className="card-footer">{footer}</div>}
  </div>
);

// Usage
<Card title="Student Info" footer={<Button>Save</Button>}>
  <StudentDetails />
</Card>

// ✅ GOOD: Higher-order component pattern
export const withLoading = <P extends object>(WrappedComponent: React.ComponentType<P>) => {
  return (props: P & { loading?: boolean }) => {
    const { loading = false, ...rest } = props;
    if (loading) return <LoadingSpinner />;
    return <WrappedComponent {...(rest as P)} />;
  };
};
```

**Requirements:**
- Prefer composition over inheritance
- Use `children` prop for flexible content
- Use render props when component needs to share data
- Use HOCs sparingly and with proper TypeScript types
- Keep components small and focused (single responsibility)

## Output Requirements

### Code Files

1. **Component file** (`ComponentName.tsx`):
   - Functional component with typed props
   - Hooks applied correctly
   - Exported as named export
   - Default export when appropriate

2. **Test file** (`ComponentName.test.tsx`):
   - Jest/Vitest + React Testing Library
   - Test component renders with props
   - Test user interactions
   - Test loading/error states
   - Accessibility tests

3. **Storybook file** (`ComponentName.stories.tsx`):
   - Default story
   - Variant stories (loading, error, different states)
   - Props table for documentation

### Integration Requirements

- **shadcn/ui**: Use existing shadcn components when available
- **Accessibility**: Follow WCAG 2.1 AA guidelines (use @ui-ux-designer for a11y audit)
- **Styling**: Tailwind CSS with design system tokens
- **i18n**: Prepare components for internationalization (no hardcoded text)

### Documentation

- **PHR**: Create Prompt History Record for each component development
- **ADR**: Document hook pattern decisions for complex custom hooks
- **Comments**: Add comments only for non-obvious logic

## Workflow

1. **Understand Requirements**
   - Clarify component purpose, props, and interactions
   - Identify state needs (local vs global)
   - Determine reusability potential

2. **Design Props Interface**
   - Define TypeScript interface for all props
   - Mark optional props with `?`
   - Use discriminated unions for variant types

3. **Implement Component**
   - Write functional component
   - Apply hooks with proper dependencies
   - Handle loading/error states
   - Ensure accessibility (ARIA attributes)

4. **Test Component**
   - Write unit tests for all code paths
   - Test user interactions
   - Verify accessibility

5. **Create Stories**
   - Document component with Storybook
   - Show all variants and states
   - Add controls for interactive exploration

## Quality Checklist

Before completing any component:

- [ ] **React 19+ Hooks Rules**: No dependency issues, proper cleanup in useEffect
- [ ] **TypeScript Props**: Exhaustive type definitions, no `any` types
- [ ] **Custom Hooks**: All prefixed with 'use', single responsibility
- [ ] **Composition**: Used over inheritance, flexible via children/render props
- [ ] **Performance**: `useCallback`/`useMemo` for expensive operations in lists
- [ ] **Accessibility**: Proper ARIA labels, keyboard navigation support
- [ ] **Error Handling**: Graceful error states, no console errors
- [ ] **Loading States**: Clear loading indicators for async operations
- [ ] **Tests**: Unit tests cover all branches and interactions
- [ ] **Stories**: Storybook stories document component usage

## Common Patterns

### Data Fetching Component

```typescript
export const StudentList = () => {
  const { data: students, loading, error } = useStudents();

  if (loading) return <LoadingSkeleton count={5} />;
  if (error) return <ErrorState message={error} />;

  return (
    <ul>
      {students?.map((student) => (
        <StudentItem key={student.id} student={student} />
      ))}
    </ul>
  );
};
```

### Form Component with Validation

```typescript
interface FormValues {
  name: string;
  email: string;
}

export const StudentForm = () => {
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>();

  const onSubmit = async (data: FormValues) => {
    await api.createStudent(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Input {...register('name', { required: true })} error={errors.name} />
      <Input {...register('email', { required: true })} error={errors.email} />
      <Button type="submit">Save</Button>
    </form>
  );
};
```

## References

- React Documentation: https://react.dev
- TypeScript React Cheatsheet: https://react-typescript-cheatsheet.netlify.app
- React Testing Library: https://testing-library.com/docs/react-testing-library/intro
- shadcn/ui: https://ui.shadcn.com
