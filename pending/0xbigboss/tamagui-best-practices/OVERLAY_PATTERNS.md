# Overlay Patterns

Prescriptive patterns for Popover, Tooltip, and Select. Read this before using these components.

## Mandatory Rules

### 1. Always Use Adapt for Touch Devices

All overlay components should adapt to Sheet on touch:

```tsx
<Popover>
  <Popover.Trigger asChild>
    <Button>Open</Button>
  </Popover.Trigger>

  {/* Adapt to Sheet on touch devices */}
  <Adapt when="sm" platform="touch">
    <Popover.Sheet modal dismissOnSnapToBottom>
      <Popover.Sheet.Frame padding="$4">
        <Adapt.Contents />
      </Popover.Sheet.Frame>
      <Popover.Sheet.Overlay />
    </Popover.Sheet>
  </Adapt>

  <Popover.Content>
    {/* content */}
  </Popover.Content>
</Popover>
```

### 2. PortalProvider Required

All overlay components need PortalProvider in app root:

```tsx
// App.tsx or _app.tsx
import { PortalProvider } from '@tamagui/portal'

function App() {
  return (
    <PortalProvider shouldAddRootHost>
      <YourApp />
    </PortalProvider>
  )
}
```

### 3. Use asChild on Triggers

For proper styling and event handling:

```tsx
// CORRECT
<Popover.Trigger asChild>
  <Button>Open</Button>
</Popover.Trigger>

// WRONG - wraps Button in another element
<Popover.Trigger>
  <Button>Open</Button>
</Popover.Trigger>
```

## Popover

### Complete Example

```tsx
import { Popover, Adapt, Button, YStack, Text } from 'tamagui'

function PopoverDemo() {
  return (
    <Popover size="$5" allowFlip placement="bottom">
      <Popover.Trigger asChild>
        <Button>Show Info</Button>
      </Popover.Trigger>

      <Adapt when="sm" platform="touch">
        <Popover.Sheet modal dismissOnSnapToBottom>
          <Popover.Sheet.Frame padding="$4">
            <Adapt.Contents />
          </Popover.Sheet.Frame>
          <Popover.Sheet.Overlay />
        </Popover.Sheet>
      </Adapt>

      <Popover.Content
        borderWidth={1}
        borderColor="$borderColor"
        enterStyle={{ y: -10, opacity: 0 }}
        exitStyle={{ y: -10, opacity: 0 }}
        elevate
        animation={['quick', { opacity: { overshootClamping: true } }]}
        padding="$4"
      >
        <Popover.Arrow borderWidth={1} borderColor="$borderColor" />
        <YStack gap="$3">
          <Text>Popover content here</Text>
          <Popover.Close asChild>
            <Button size="$3">Close</Button>
          </Popover.Close>
        </YStack>
      </Popover.Content>
    </Popover>
  )
}
```

### Positioning Props

| Prop | Values | Description |
|------|--------|-------------|
| `placement` | `'top'`, `'bottom'`, `'left'`, `'right'` | Base position |
| | + `-start`, `-end` variants | Alignment |
| `allowFlip` | boolean | Auto-flip when not enough space |
| `offset` | number | Distance from trigger |

### Controlled Popover

```tsx
const [open, setOpen] = useState(false)

<Popover open={open} onOpenChange={setOpen}>
  <Popover.Trigger asChild>
    <Button onPress={() => setOpen(true)}>Open</Button>
  </Popover.Trigger>
  {/* ... */}
</Popover>
```

## Tooltip

Simpler than Popover - for hover hints only:

```tsx
import { Tooltip, Button, Text } from 'tamagui'

function TooltipDemo() {
  return (
    <Tooltip>
      <Tooltip.Trigger asChild>
        <Button>Hover me</Button>
      </Tooltip.Trigger>

      <Tooltip.Content
        enterStyle={{ x: 0, y: -5, opacity: 0, scale: 0.9 }}
        exitStyle={{ x: 0, y: -5, opacity: 0, scale: 0.9 }}
        animation={['quick', { opacity: { overshootClamping: true } }]}
        padding="$2"
        borderRadius="$2"
      >
        <Tooltip.Arrow />
        <Text fontSize="$2">Helpful hint</Text>
      </Tooltip.Content>
    </Tooltip>
  )
}
```

### Tooltip Props

| Prop | Type | Description |
|------|------|-------------|
| `delay` | number | ms before showing |
| `restMs` | number | ms to wait after last pointer move |
| `placement` | string | Same as Popover |

## Select

### Complete Example

```tsx
import { Check, ChevronDown, ChevronUp } from '@tamagui/lucide-icons'
import { Select, Adapt, Sheet } from 'tamagui'

const items = [
  { value: 'apple', label: 'Apple' },
  { value: 'banana', label: 'Banana' },
  { value: 'orange', label: 'Orange' },
]

function SelectDemo() {
  const [value, setValue] = useState('apple')

  return (
    <Select value={value} onValueChange={setValue}>
      <Select.Trigger width={220} iconAfter={ChevronDown}>
        <Select.Value placeholder="Select a fruit" />
      </Select.Trigger>

      <Adapt when="sm" platform="touch">
        <Sheet modal dismissOnSnapToBottom snapPoints={[50]}>
          <Sheet.Frame>
            <Sheet.ScrollView>
              <Adapt.Contents />
            </Sheet.ScrollView>
          </Sheet.Frame>
          <Sheet.Overlay />
        </Sheet>
      </Adapt>

      <Select.Content zIndex={200000}>
        <Select.ScrollUpButton
          alignItems="center"
          justifyContent="center"
          height="$3"
        >
          <ChevronUp size={20} />
        </Select.ScrollUpButton>

        <Select.Viewport minWidth={200}>
          <Select.Group>
            <Select.Label>Fruits</Select.Label>
            {items.map((item, i) => (
              <Select.Item key={item.value} index={i} value={item.value}>
                <Select.ItemText>{item.label}</Select.ItemText>
                <Select.ItemIndicator marginLeft="auto">
                  <Check size={16} />
                </Select.ItemIndicator>
              </Select.Item>
            ))}
          </Select.Group>
        </Select.Viewport>

        <Select.ScrollDownButton
          alignItems="center"
          justifyContent="center"
          height="$3"
        >
          <ChevronDown size={20} />
        </Select.ScrollDownButton>
      </Select.Content>
    </Select>
  )
}
```

### Select Structure

Required components in order:
1. `Select` - root
2. `Select.Trigger` - opens dropdown
3. `Select.Value` - displays selected value
4. `Adapt` - touch device handling
5. `Select.Content` - dropdown container
6. `Select.Viewport` - scrollable area
7. `Select.Group` - groups items
8. `Select.Item` - individual option

### Native Select

Use native picker on mobile:

```tsx
<Select native>
  {/* ... */}
</Select>
```

### Select Item Index

Each item needs an `index` prop for keyboard navigation:

```tsx
{items.map((item, i) => (
  <Select.Item key={item.value} index={i} value={item.value}>
    <Select.ItemText>{item.label}</Select.ItemText>
  </Select.Item>
))}
```

## zIndex Considerations

Overlays need high zIndex to appear above other content:

```tsx
<Select.Content zIndex={200000}>
<Popover.Content zIndex={200000}>
<Dialog.Portal zIndex={200000}>
```

When nesting overlays (e.g., Select inside Dialog), ensure inner overlay has higher zIndex.

## Common Patterns

### Menu Popover

```tsx
function MenuPopover({ items }: { items: MenuItem[] }) {
  return (
    <Popover placement="bottom-start">
      <Popover.Trigger asChild>
        <Button icon={Menu} />
      </Popover.Trigger>

      <Adapt when="sm" platform="touch">
        <Popover.Sheet modal dismissOnSnapToBottom>
          <Popover.Sheet.Frame>
            <Adapt.Contents />
          </Popover.Sheet.Frame>
          <Popover.Sheet.Overlay />
        </Popover.Sheet>
      </Adapt>

      <Popover.Content
        padding={0}
        borderWidth={1}
        borderColor="$borderColor"
        animation="quick"
        enterStyle={{ y: -10, opacity: 0 }}
        exitStyle={{ y: -10, opacity: 0 }}
      >
        <YStack>
          {items.map((item) => (
            <Popover.Close key={item.id} asChild>
              <Button
                chromeless
                justifyContent="flex-start"
                icon={item.icon}
                onPress={item.onPress}
              >
                {item.label}
              </Button>
            </Popover.Close>
          ))}
        </YStack>
      </Popover.Content>
    </Popover>
  )
}
```

### Confirmation Popover

```tsx
function ConfirmPopover({
  trigger,
  onConfirm,
  message,
}: {
  trigger: React.ReactNode
  onConfirm: () => void
  message: string
}) {
  const [open, setOpen] = useState(false)

  const handleConfirm = () => {
    onConfirm()
    setOpen(false)
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <Popover.Trigger asChild>{trigger}</Popover.Trigger>

      <Adapt when="sm" platform="touch">
        <Popover.Sheet modal dismissOnSnapToBottom>
          <Popover.Sheet.Frame padding="$4">
            <Adapt.Contents />
          </Popover.Sheet.Frame>
          <Popover.Sheet.Overlay />
        </Popover.Sheet>
      </Adapt>

      <Popover.Content
        padding="$4"
        borderWidth={1}
        borderColor="$borderColor"
        animation="quick"
        enterStyle={{ y: -10, opacity: 0 }}
        exitStyle={{ y: -10, opacity: 0 }}
        elevate
      >
        <Popover.Arrow borderWidth={1} borderColor="$borderColor" />
        <YStack gap="$3" maxWidth={250}>
          <Text>{message}</Text>
          <XStack gap="$2" justifyContent="flex-end">
            <Popover.Close asChild>
              <Button size="$3" chromeless>Cancel</Button>
            </Popover.Close>
            <Button size="$3" theme="red" onPress={handleConfirm}>
              Confirm
            </Button>
          </XStack>
        </YStack>
      </Popover.Content>
    </Popover>
  )
}
```

### Form Select Field

Note: `Select` does not wire `Label htmlFor` to the trigger. Use `aria-label`/`aria-labelledby` on `Select.Trigger` or wrap the field in a `fieldset`/`legend`.

```tsx
function SelectField({
  label,
  id,
  value,
  onValueChange,
  options,
  error,
}: SelectFieldProps) {
  const labelId = `${id}-label`

  return (
    <YStack gap="$1">
      <Label id={labelId}>{label}</Label>
      <Select value={value} onValueChange={onValueChange}>
        <Select.Trigger
          width="100%"
          iconAfter={ChevronDown}
          borderColor={error ? '$red10' : undefined}
          aria-labelledby={labelId}
        >
          <Select.Value placeholder={`Select ${label.toLowerCase()}`} />
        </Select.Trigger>

        <Adapt when="sm" platform="touch">
          <Sheet modal dismissOnSnapToBottom>
            <Sheet.Frame>
              <Sheet.ScrollView>
                <Adapt.Contents />
              </Sheet.ScrollView>
            </Sheet.Frame>
            <Sheet.Overlay />
          </Sheet>
        </Adapt>

        <Select.Content zIndex={200000}>
          <Select.Viewport>
            {options.map((option, i) => (
              <Select.Item key={option.value} index={i} value={option.value}>
                <Select.ItemText>{option.label}</Select.ItemText>
                <Select.ItemIndicator marginLeft="auto">
                  <Check size={16} />
                </Select.ItemIndicator>
              </Select.Item>
            ))}
          </Select.Viewport>
        </Select.Content>
      </Select>
      {error && (
        <Text color="$red10" fontSize="$2">{error}</Text>
      )}
    </YStack>
  )
}
```
