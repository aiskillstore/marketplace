# @neural-ui/core/nav

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuNavComponent

Selector: `neu-nav`

| Input | Required | Type |
| --- | --- | --- |
| items | no | `import("@angular/core").InputSignal<NeuNavItem[]>` |
| collapsed | no | `import("@angular/core").InputSignal<boolean \| undefined>` |
| collapsible | no | `import("@angular/core").InputSignal<boolean>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |
| expandLabel | no | `import("@angular/core").InputSignal<string>` |
| collapseLabel | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |
| collapsedChange | `import("@angular/core").OutputEmitterRef<boolean>` |

## NeuNavItem

```typescript
export interface NeuNavItem {
    id: string;
    label: string;
    icon: NeuIconKey;
    route?: string;
    href?: string;
    children?: NeuNavItem[];
    badge?: string;
    badgeTone?: "neutral" | "success" | "warning" | "danger" | "info";
    disabled?: boolean;
    active?: boolean;
}
```

