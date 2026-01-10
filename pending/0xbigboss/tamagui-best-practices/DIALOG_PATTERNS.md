# Dialog & Sheet Patterns

Prescriptive patterns for modal overlays. Read this before writing Dialog or Sheet code.

## Mandatory Rules

### 1. Title and Description Are Required

Accessibility requirement - always include both, even if hidden:

```tsx
// REQUIRED - use VisuallyHidden if you don't want visible title
<Dialog.Content>
  <VisuallyHidden>
    <Dialog.Title>Edit Profile</Dialog.Title>
    <Dialog.Description>Update your account settings</Dialog.Description>
  </VisuallyHidden>
  {/* visible content */}
</Dialog.Content>
```

Omitting Title/Description breaks screen readers.

### 2. Always Use Adapt for Cross-Platform

Never use `Platform.OS` branching. Use `Adapt` to transform Dialog to Sheet on touch devices:

```tsx
// CORRECT - single Dialog that adapts
<Dialog modal open={open} onOpenChange={setOpen}>
  <Dialog.Portal>
    <Dialog.Overlay
      animation="quick"
      opacity={0.5}
      enterStyle={{ opacity: 0 }}
      exitStyle={{ opacity: 0 }}
    />
    <Dialog.Content
      bordered
      elevate
      animateOnly={['transform', 'opacity']}
      animation={['quick', { opacity: { overshootClamping: true } }]}
      enterStyle={{ y: -20, opacity: 0, scale: 0.9 }}
      exitStyle={{ y: 10, opacity: 0, scale: 0.95 }}
    >
      <VisuallyHidden>
        <Dialog.Title>Title Here</Dialog.Title>
        <Dialog.Description>Describe the dialog purpose</Dialog.Description>
      </VisuallyHidden>
      <DialogBody />
    </Dialog.Content>
  </Dialog.Portal>

  <Adapt when="sm" platform="touch">
    <Sheet modal dismissOnSnapToBottom snapPoints={[80]}>
      <Sheet.Frame padding="$4">
        <Sheet.ScrollView>
          <Adapt.Contents />
        </Sheet.ScrollView>
      </Sheet.Frame>
      <Sheet.Overlay />
    </Sheet>
  </Adapt>
</Dialog>
```

```tsx
// WRONG - manual platform branching
if (Platform.OS === 'web') {
  return <Dialog>...</Dialog>
}
return <Sheet>...</Sheet>
```

### 3. Animation on Content, Not Portal

Apply animation props to `Dialog.Content`, never to `Dialog.Portal`:

```tsx
// CORRECT
<Dialog.Portal>
  <Dialog.Content animation="quick" enterStyle={{...}}>

// WRONG
<Dialog.Portal animation="quick">
```

### 4. Use animateOnly for Performance

Restrict animations to necessary properties:

```tsx
<Dialog.Content
  animateOnly={['transform', 'opacity']}
  animation="quick"
>
```

## Common Dialog Types

### Confirmation Dialog

```tsx
function ConfirmDialog({
  open,
  onOpenChange,
  onConfirm,
  title,
  description
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  onConfirm: () => void
  title: string
  description: string
}) {
  return (
    <Dialog modal open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay
          animation="quick"
          opacity={0.5}
          enterStyle={{ opacity: 0 }}
          exitStyle={{ opacity: 0 }}
        />
        <Dialog.Content
          bordered
          elevate
          animation={['quick', { opacity: { overshootClamping: true } }]}
          animateOnly={['transform', 'opacity']}
          enterStyle={{ y: -20, opacity: 0, scale: 0.9 }}
          exitStyle={{ y: 10, opacity: 0, scale: 0.95 }}
          width="90%"
          maxWidth={400}
          padding="$4"
          gap="$4"
        >
          <Dialog.Title>{title}</Dialog.Title>
          <Dialog.Description>{description}</Dialog.Description>

          <XStack gap="$3" justifyContent="flex-end">
            <Dialog.Close asChild>
              <Button chromeless>Cancel</Button>
            </Dialog.Close>
            <Button theme="active" onPress={onConfirm}>
              Confirm
            </Button>
          </XStack>
        </Dialog.Content>
      </Dialog.Portal>

      <Adapt when="sm" platform="touch">
        <Sheet modal dismissOnSnapToBottom>
          <Sheet.Frame padding="$4">
            <Adapt.Contents />
          </Sheet.Frame>
          <Sheet.Overlay />
        </Sheet>
      </Adapt>
    </Dialog>
  )
}
```

### Form Dialog

```tsx
function FormDialog({ open, onOpenChange }: DialogProps) {
  return (
    <Dialog modal open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay
          animation="quick"
          opacity={0.5}
          enterStyle={{ opacity: 0 }}
          exitStyle={{ opacity: 0 }}
        />
        <Dialog.Content
          bordered
          elevate
          animation={['quick', { opacity: { overshootClamping: true } }]}
          animateOnly={['transform', 'opacity']}
          enterStyle={{ y: -20, opacity: 0, scale: 0.9 }}
          exitStyle={{ y: 10, opacity: 0, scale: 0.95 }}
          width="90%"
          maxWidth={500}
        >
          <Dialog.Title>Create Item</Dialog.Title>
          <VisuallyHidden>
            <Dialog.Description>Fill out the form to create a new item</Dialog.Description>
          </VisuallyHidden>

          <Form onSubmit={handleSubmit}>
            <YStack gap="$3" padding="$4">
              <Label htmlFor="name">Name</Label>
              <Input id="name" placeholder="Enter name" />

              <Label htmlFor="description">Description</Label>
              <TextArea id="description" placeholder="Enter description" />

              <XStack gap="$3" justifyContent="flex-end" marginTop="$2">
                <Dialog.Close asChild>
                  <Button chromeless>Cancel</Button>
                </Dialog.Close>
                <Form.Trigger asChild>
                  <Button theme="active">Create</Button>
                </Form.Trigger>
              </XStack>
            </YStack>
          </Form>
        </Dialog.Content>
      </Dialog.Portal>

      <Adapt when="sm" platform="touch">
        <Sheet modal dismissOnSnapToBottom snapPoints={[85]}>
          <Sheet.Frame>
            <Sheet.ScrollView>
              <Adapt.Contents />
            </Sheet.ScrollView>
          </Sheet.Frame>
          <Sheet.Overlay />
        </Sheet>
      </Adapt>
    </Dialog>
  )
}
```

## Sheet-Only Patterns

When you only need a Sheet (no Dialog on desktop):

```tsx
function BottomSheet({ open, onOpenChange, children }: SheetProps) {
  return (
    <Sheet
      modal
      open={open}
      onOpenChange={onOpenChange}
      snapPoints={[80, 50]}
      dismissOnSnapToBottom
      dismissOnOverlayPress
    >
      <Sheet.Overlay
        animation="quick"
        enterStyle={{ opacity: 0 }}
        exitStyle={{ opacity: 0 }}
      />
      <Sheet.Frame>
        <Sheet.Handle />
        <Sheet.ScrollView>
          {children}
        </Sheet.ScrollView>
      </Sheet.Frame>
    </Sheet>
  )
}
```

### Sheet Props Reference

| Prop | Type | Description |
|------|------|-------------|
| `modal` | boolean | Renders in portal, adds overlay |
| `snapPoints` | number[] | Snap positions as % of screen |
| `dismissOnSnapToBottom` | boolean | Close when dragged to bottom |
| `dismissOnOverlayPress` | boolean | Close on overlay tap |
| `position` | number | Current snap index |
| `onPositionChange` | (pos: number) => void | Snap position changed |

## Preventing Dismiss

Stop dismissal on outside click:

```tsx
<Dialog.Content
  onPointerDownOutside={(e) => e.preventDefault()}
  onEscapeKeyDown={(e) => e.preventDefault()}
>
```

## Controlled vs Uncontrolled

```tsx
// Uncontrolled - Dialog manages state
<Dialog modal>
  <Dialog.Trigger asChild>
    <Button>Open</Button>
  </Dialog.Trigger>
  <Dialog.Portal>...</Dialog.Portal>
</Dialog>

// Controlled - you manage state
const [open, setOpen] = useState(false)

<Dialog modal open={open} onOpenChange={setOpen}>
  <Dialog.Portal>...</Dialog.Portal>
</Dialog>

<Button onPress={() => setOpen(true)}>Open</Button>
```
