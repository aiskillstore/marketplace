# @neural-ui/core/data-view

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## NeuDataViewComponent

Selector: `neu-data-view`

| Input | Required | Type |
| --- | --- | --- |
| items | no | `import("@angular/core").InputSignal<readonly unknown[]>` |
| mode | no | `import("@angular/core").InputSignal<NeuDataViewMode>` |
| modes | no | `import("@angular/core").InputSignal<readonly NeuDataViewMode[]>` |
| modeLabels | no | `import("@angular/core").InputSignal<Partial<Record<NeuDataViewMode, string>>>` |
| viewSwitcher | no | `import("@angular/core").InputSignal<boolean>` |
| viewAriaLabel | no | `import("@angular/core").InputSignal<string>` |
| searchable | no | `import("@angular/core").InputSignal<boolean>` |
| searchFields | no | `import("@angular/core").InputSignal<readonly string[]>` |
| searchPlaceholder | no | `import("@angular/core").InputSignal<string>` |
| searchAriaLabel | no | `import("@angular/core").InputSignal<string>` |
| sortOptions | no | `import("@angular/core").InputSignal<readonly NeuDataViewSortOption[]>` |
| sortAriaLabel | no | `import("@angular/core").InputSignal<string>` |
| pagination | no | `import("@angular/core").InputSignal<boolean>` |
| pageSize | no | `import("@angular/core").InputSignal<number>` |
| total | no | `import("@angular/core").InputSignal<number \| undefined>` |
| currentPage | no | `import("@angular/core").InputSignal<number \| undefined>` |
| emptyLabel | no | `import("@angular/core").InputSignal<string>` |
| loading | no | `import("@angular/core").InputSignal<boolean>` |
| loadingLabel | no | `import("@angular/core").InputSignal<string>` |
| previousLabel | no | `import("@angular/core").InputSignal<string>` |
| nextLabel | no | `import("@angular/core").InputSignal<string>` |
| paginationAriaLabel | no | `import("@angular/core").InputSignal<string>` |
| trackBy | no | `import("@angular/core").InputSignal<(index: number, item: unknown) => unknown>` |

| Output | Type |
| --- | --- |
| modeChange | `import("@angular/core").OutputEmitterRef<NeuDataViewMode>` |
| searchChange | `import("@angular/core").OutputEmitterRef<string>` |
| sortChange | `import("@angular/core").OutputEmitterRef<string>` |
| pageChange | `import("@angular/core").OutputEmitterRef<NeuDataViewPageEvent>` |

## NeuDataViewFooterDirective

Selector: `ng-template[neuDataViewFooter]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuDataViewHeaderDirective

Selector: `ng-template[neuDataViewHeader]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuDataViewItemDirective

Selector: `ng-template[neuDataViewItem]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuDataViewMode

```typescript
export type NeuDataViewMode = 'list' | 'grid' | 'table';
```

## NeuDataViewPageEvent

```typescript
export interface NeuDataViewPageEvent {
    page: number;
    pageSize: number;
}
```

## NeuDataViewSortDirection

```typescript
export type NeuDataViewSortDirection = 'asc' | 'desc';
```

## NeuDataViewSortOption

```typescript
export interface NeuDataViewSortOption {
    label: string;
    value: string;
    direction?: NeuDataViewSortDirection;
}
```

