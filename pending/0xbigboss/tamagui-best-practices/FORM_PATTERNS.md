# Form Patterns

Prescriptive patterns for forms, inputs, and validation. Read this before writing form code.

## Cross-Skill: Load typescript-best-practices

Form validation uses type-first patterns. Load the `typescript-best-practices` skill for:
- Zod schema definitions
- Discriminated unions for form state
- Type inference from schemas

The examples below use patterns from that skill.

## Mandatory Rules

### 1. Form.Trigger Is Required

Without `Form.Trigger`, `onSubmit` never fires. This is the most common mistake:

```tsx
// WRONG - onSubmit will never fire
<Form onSubmit={handleSubmit}>
  <Input />
  <Button>Submit</Button>
</Form>

// CORRECT - Form.Trigger enables submission
<Form onSubmit={handleSubmit}>
  <Input />
  <Form.Trigger asChild>
    <Button>Submit</Button>
  </Form.Trigger>
</Form>
```

### 2. Always Use asChild on Form.Trigger

For proper styling and control:

```tsx
<Form.Trigger asChild>
  <Button theme="active">Submit</Button>
</Form.Trigger>
```

### 3. Label htmlFor Must Match Input id

Accessibility requirement - IDs must match exactly:

```tsx
// CORRECT
<Label htmlFor="email">Email</Label>
<Input id="email" />

// WRONG - broken accessibility
<Label htmlFor="email">Email</Label>
<Input id="emailInput" />
```

### 4. No Built-in Validation

Tamagui Form has no validation. Use external libraries:
- `react-hook-form` + `zod` (recommended)
- `formik` + `yup`

## Form State Pattern

Use discriminated unions for form state (from typescript-best-practices):

```tsx
type FormState =
  | { status: 'idle' }
  | { status: 'submitting' }
  | { status: 'error'; error: string }
  | { status: 'success'; data: ResponseData }

const [state, setState] = useState<FormState>({ status: 'idle' })
```

## Complete Form Example

### With react-hook-form + zod

```tsx
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Form, Input, Label, Button, YStack, XStack, Text } from 'tamagui'

// 1. Define schema (type-first)
const createUserSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  age: z.coerce.number().min(18, 'Must be 18 or older').optional(),
})

type CreateUserInput = z.infer<typeof createUserSchema>

// 2. Form state union
type FormState =
  | { status: 'idle' }
  | { status: 'submitting' }
  | { status: 'error'; error: string }
  | { status: 'success' }

function CreateUserForm({ onSuccess }: { onSuccess: () => void }) {
  const [state, setState] = useState<FormState>({ status: 'idle' })

  const {
    control,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<CreateUserInput>({
    resolver: zodResolver(createUserSchema),
    defaultValues: { name: '', email: '' },
  })

  const onSubmit = async (data: CreateUserInput) => {
    setState({ status: 'submitting' })
    try {
      await api.createUser(data)
      setState({ status: 'success' })
      reset()
      onSuccess()
    } catch (err) {
      setState({
        status: 'error',
        error: err instanceof Error ? err.message : 'Unknown error',
      })
    }
  }

  return (
    <Form onSubmit={handleSubmit(onSubmit)}>
      <YStack gap="$3" padding="$4">
        {/* Name field */}
        <YStack gap="$1">
          <Label htmlFor="name">Name</Label>
          <Controller
            control={control}
            name="name"
            render={({ field: { onChange, onBlur, value } }) => (
              <Input
                id="name"
                value={value}
                onChangeText={onChange}
                onBlur={onBlur}
                placeholder="Enter name"
                borderColor={errors.name ? '$red10' : undefined}
              />
            )}
          />
          {errors.name && (
            <Text color="$red10" fontSize="$2">
              {errors.name.message}
            </Text>
          )}
        </YStack>

        {/* Email field */}
        <YStack gap="$1">
          <Label htmlFor="email">Email</Label>
          <Controller
            control={control}
            name="email"
            render={({ field: { onChange, onBlur, value } }) => (
              <Input
                id="email"
                value={value}
                onChangeText={onChange}
                onBlur={onBlur}
                placeholder="Enter email"
                keyboardType="email-address"
                autoCapitalize="none"
                borderColor={errors.email ? '$red10' : undefined}
              />
            )}
          />
          {errors.email && (
            <Text color="$red10" fontSize="$2">
              {errors.email.message}
            </Text>
          )}
        </YStack>

        {/* Form-level error */}
        {state.status === 'error' && (
          <Text color="$red10">{state.error}</Text>
        )}

        {/* Submit button */}
        <Form.Trigger asChild>
          <Button
            theme="active"
            disabled={state.status === 'submitting'}
            opacity={state.status === 'submitting' ? 0.5 : 1}
          >
            {state.status === 'submitting' ? 'Submitting...' : 'Create User'}
          </Button>
        </Form.Trigger>
      </YStack>
    </Form>
  )
}
```

## Field Component Pattern

Extract reusable form fields:

```tsx
type FieldProps = {
  label: string
  id: string
  error?: string
  children: React.ReactNode
}

function Field({ label, id, error, children }: FieldProps) {
  return (
    <YStack gap="$1">
      <Label htmlFor={id}>{label}</Label>
      {children}
      {error && (
        <Text color="$red10" fontSize="$2">
          {error}
        </Text>
      )}
    </YStack>
  )
}

// Usage
<Field label="Email" id="email" error={errors.email?.message}>
  <Controller
    control={control}
    name="email"
    render={({ field: { value, onChange, onBlur } }) => (
      <Input
        id="email"
        value={value}
        onChangeText={onChange}
        onBlur={onBlur}
        borderColor={errors.email ? '$red10' : undefined}
      />
    )}
  />
</Field>
```

## Input Variants

### Text Input

```tsx
<Input
  id="name"
  placeholder="Enter name"
  autoCapitalize="words"
/>
```

### Email Input

```tsx
<Input
  id="email"
  placeholder="Enter email"
  keyboardType="email-address"
  autoCapitalize="none"
  autoComplete="email"
/>
```

### Password Input

```tsx
const [showPassword, setShowPassword] = useState(false)

<XStack alignItems="center">
  <Input
    id="password"
    flex={1}
    placeholder="Enter password"
    secureTextEntry={!showPassword}
    autoCapitalize="none"
    autoComplete="password"
  />
  <Button
    size="$2"
    chromeless
    onPress={() => setShowPassword(!showPassword)}
  >
    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
  </Button>
</XStack>
```

### TextArea

```tsx
<TextArea
  id="description"
  placeholder="Enter description"
  numberOfLines={4}
/>
```

## Checkbox and Switch

```tsx
import { Checkbox, Switch, Label, XStack } from 'tamagui'
import { Check } from '@tamagui/lucide-icons'

// Checkbox
<XStack alignItems="center" gap="$2">
  <Checkbox id="terms" checked={agreed} onCheckedChange={setAgreed}>
    <Checkbox.Indicator>
      <Check />
    </Checkbox.Indicator>
  </Checkbox>
  <Label htmlFor="terms">I agree to the terms</Label>
</XStack>

// Switch
<XStack alignItems="center" gap="$2">
  <Switch id="notifications" checked={enabled} onCheckedChange={setEnabled}>
    <Switch.Thumb animation="quick" />
  </Switch>
  <Label htmlFor="notifications">Enable notifications</Label>
</XStack>
```

## Form in Dialog

See @DIALOG_PATTERNS.md for complete form-in-dialog example. Key points:
- Use controlled Dialog state
- Close dialog on successful submit
- Handle loading/error states
- Use Sheet.ScrollView in Adapt for long forms

## Validation Schemas Reference

Common zod patterns for forms:

```tsx
import { z } from 'zod'

// Required string
z.string().min(1, 'Required')

// Email
z.string().email('Invalid email')

// Password with requirements
z.string()
  .min(8, 'Must be at least 8 characters')
  .regex(/[A-Z]/, 'Must contain uppercase')
  .regex(/[0-9]/, 'Must contain number')

// Optional with transform
z.string().optional().transform(v => v || undefined)

// Number from string input
z.coerce.number().min(0).max(100)

// Enum/select
z.enum(['option1', 'option2', 'option3'])

// Refinement for confirm password
const schema = z.object({
  password: z.string().min(8),
  confirmPassword: z.string(),
}).refine(data => data.password === data.confirmPassword, {
  message: 'Passwords must match',
  path: ['confirmPassword'],
})
```
