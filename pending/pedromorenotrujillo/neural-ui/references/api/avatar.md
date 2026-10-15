# @neural-ui/core/avatar

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuAvatarColor

```typescript
export type NeuAvatarColor = 'blue' | 'violet' | 'green' | 'amber' | 'red' | 'slate';
```

## NeuAvatarComponent

Selector: `neu-avatar`

| Input | Required | Type |
| --- | --- | --- |
| src | no | `import("@angular/core").InputSignal<string>` |
| alt | no | `import("@angular/core").InputSignal<string>` |
| name | no | `import("@angular/core").InputSignal<string>` |
| size | no | `import("@angular/core").InputSignal<NeuAvatarSize>` |
| shape | no | `import("@angular/core").InputSignal<NeuAvatarShape>` |
| color | no | `import("@angular/core").InputSignal<NeuAvatarColor>` |
| status | no | `import("@angular/core").InputSignal<NeuAvatarStatus>` |

| Output | Type |
| --- | --- |

## NeuAvatarShape

```typescript
export type NeuAvatarShape = 'circle' | 'square';
```

## NeuAvatarSize

```typescript
export type NeuAvatarSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';
```

## NeuAvatarStatus

```typescript
export type NeuAvatarStatus = 'online' | 'offline' | 'busy' | 'away' | '';
```

