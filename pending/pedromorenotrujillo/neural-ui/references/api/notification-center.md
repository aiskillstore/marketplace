# @neural-ui/core/notification-center

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuNotification

```typescript
export interface NeuNotification {
    id: string;
    tone: NeuNotificationTone;
    title?: string;
    message: string;
    duration?: number;
    icon?: NeuIconKey;
    timestamp: Date;
    read: boolean;
}
```

## NeuNotificationCenterComponent

Selector: `neu-notification-center`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuNotificationOptions

```typescript
export interface NeuNotificationOptions extends Omit<NeuNotification, "id" | "timestamp" | "read"> {
}
```

## NeuNotificationService

Supported imperative members:

```typescript
readonly notifications: import("@angular/core").WritableSignal<NeuNotification[]>;
readonly unreadCount: import("@angular/core").Signal<number>;
push(opts: Partial<NeuNotificationOptions> & Pick<NeuNotificationOptions, 'message'>): string;
remove(id: string): void;
markAllRead(): void;
clearAll(): void;
```

## NeuNotificationTone

```typescript
export type NeuNotificationTone = 'neutral' | 'success' | 'info' | 'warning' | 'danger';
```

