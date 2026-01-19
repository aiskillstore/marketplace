---
name: liquid-glass
description: Implement, review, or improve SwiftUI features using the iOS 26+ Liquid Glass API. Use when asked to adopt Liquid Glass in SwiftUI UI, refactor to Liquid Glass, or review Liquid Glass usage.
---

# SwiftUI Liquid Glass

## Overview

Liquid Glass is a dynamic material in iOS 26+ that combines optical glass properties with fluidity. It blurs content, reflects surrounding color and light, and reacts to touch interactions in real time.

## Workflow Decision Tree

### 1) Review an existing feature
- Inspect where Liquid Glass should/shouldn't be used
- Verify correct modifier order, shape usage, container placement
- Check for iOS 26+ availability handling and fallbacks

### 2) Improve a feature using Liquid Glass
- Identify target components (surfaces, chips, buttons, cards)
- Refactor to use `GlassEffectContainer` for multiple glass elements
- Add interactive glass only for tappable/focusable elements

### 3) Implement a new feature using Liquid Glass
- Design glass surfaces and interactions first (shape, prominence, grouping)
- Add glass modifiers after layout/appearance modifiers
- Add morphing transitions only when view hierarchy changes with animation

## Core Guidelines

- Prefer native Liquid Glass APIs over custom blurs
- Use `GlassEffectContainer` when multiple glass elements coexist
- Apply `.glassEffect(...)` after layout and visual modifiers
- Use `.interactive()` for elements that respond to touch/pointer
- Keep shapes consistent across related elements
- Gate with `#available(iOS 26, *)` and provide non-glass fallback

## Review Checklist

- [ ] **Availability**: `#available(iOS 26, *)` present with fallback UI
- [ ] **Composition**: Multiple glass views wrapped in `GlassEffectContainer`
- [ ] **Modifier order**: `glassEffect` applied after layout/appearance modifiers
- [ ] **Interactivity**: `interactive()` only where user interaction exists
- [ ] **Transitions**: `glassEffectID` used with `@Namespace` for morphing
- [ ] **Consistency**: Shapes, tinting, and spacing align across feature

## Implementation Checklist

- [ ] Define target elements and desired glass prominence
- [ ] Wrap grouped glass elements in `GlassEffectContainer` with spacing
- [ ] Use `.glassEffect(.regular.tint(...).interactive(), in: .rect(cornerRadius: ...))` as needed
- [ ] Use `.buttonStyle(.glass)` / `.buttonStyle(.glassProminent)` for actions
- [ ] Add morphing transitions with `glassEffectID` when hierarchy changes
- [ ] Provide fallback materials for earlier iOS versions

## Quick Snippets

### Basic Glass Effect with Fallback
```swift
if #available(iOS 26, *) {
    Text("Hello")
        .padding()
        .glassEffect(.regular.interactive(), in: .rect(cornerRadius: 16))
} else {
    Text("Hello")
        .padding()
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16))
}
```

### Multiple Glass Elements
```swift
GlassEffectContainer(spacing: 24) {
    HStack(spacing: 24) {
        Image(systemName: "scribble.variable")
            .frame(width: 72, height: 72)
            .font(.system(size: 32))
            .glassEffect()
        Image(systemName: "eraser.fill")
            .frame(width: 72, height: 72)
            .font(.system(size: 32))
            .glassEffect()
    }
}
```

### Glass Buttons
```swift
Button("Confirm") { }
    .buttonStyle(.glassProminent)

Button("Cancel") { }
    .buttonStyle(.glass)
```

### Morphing Transitions
```swift
@State private var isExpanded = false
@Namespace private var namespace

GlassEffectContainer(spacing: 40) {
    HStack(spacing: 40) {
        Image(systemName: "pencil")
            .frame(width: 80, height: 80)
            .glassEffect()
            .glassEffectID("pencil", in: namespace)

        if isExpanded {
            Image(systemName: "eraser")
                .frame(width: 80, height: 80)
                .glassEffect()
                .glassEffectID("eraser", in: namespace)
        }
    }
}

Button("Toggle") {
    withAnimation {
        isExpanded.toggle()
    }
}
.buttonStyle(.glass)
```

### Customizing Glass
```swift
Text("Tinted Glass")
    .padding()
    .glassEffect(.regular.tint(.orange).interactive(), in: .capsule)
```

### Uniting Glass Effects
```swift
@Namespace private var namespace

GlassEffectContainer(spacing: 20) {
    HStack(spacing: 20) {
        ForEach(items.indices, id: \.self) { index in
            ItemView(item: items[index])
                .glassEffect()
                .glassEffectUnion(id: index < 2 ? "group1" : "group2", namespace: namespace)
        }
    }
}
```

## Shape Options

- `.capsule` (default)
- `.rect(cornerRadius: CGFloat)`
- `.circle`

## Best Practices

1. **Container Usage**: Always use `GlassEffectContainer` for multiple glass views
2. **Modifier Order**: Apply `.glassEffect()` after appearance modifiers
3. **Spacing**: Choose spacing values carefully to control effect merging
4. **Animation**: Use animations when changing view hierarchies for smooth morphing
5. **Interactivity**: Add `.interactive()` only to touchable elements
6. **Consistency**: Maintain consistent shapes and styles across your app
