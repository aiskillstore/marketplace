# @neural-ui/core/tree-table

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## buildNeuTreeTableQueryProjection

```typescript
declare function buildNeuTreeTableQueryProjection<T extends object, K extends NeuTreeTableKey, F extends string>(options: {
    readonly normalized: NormalizedTreeHierarchy<T, K>;
    readonly query: NeuTreeTableQuery<F>;
    readonly columns: readonly NeuTreeTableColumn<T, F>[];
    readonly filterOptions: NeuTreeTableFilterOptions<T, F>;
    readonly sortOptions: NeuTreeTableSortOptions;
    readonly dataMode: NeuTreeTableDataMode;
}): TreeQueryProjection;
```

## buildNeuTreeTableSelectionModel

```typescript
declare function buildNeuTreeTableSelectionModel<T extends object, K extends NeuTreeTableKey>(projection: TreeProjection<T, K>, selection: NeuTreeTableSelection<K>, options: NeuTreeTableSelectionOptions<T>): TreeSelectionModel<T, K>;
```

## evaluateNeuTreeFilter

```typescript
declare function evaluateNeuTreeFilter<T, F extends string>(constraint: NeuTreeFilterConstraint<F>, candidate: unknown, value: T, options: NeuTreeTableFilterOptions<T, F>): boolean;
```

## IndexedTreeNode

```typescript
interface IndexedTreeNode<T, K extends NeuTreeTableKey> {
    readonly key: K;
    readonly token: string;
    readonly value: T;
}
```

## NeuTreeChildRelation

```typescript
export interface NeuTreeChildRelation<K extends NeuTreeTableKey> {
    readonly parentKey: K;
    readonly relation: NeuTreeRelation<K>;
}
```

## NeuTreeEditColumn

```typescript
export interface NeuTreeEditColumn<T, F extends string> {
    readonly field: F;
    readonly read?: NeuTreeValueAccessor<T>;
    readonly write?: (value: T, candidate: unknown) => T;
}
```

## NeuTreeErrorRelation

```typescript
export interface NeuTreeErrorRelation<K extends NeuTreeTableKey> {
    readonly status: "error";
    readonly keys: readonly K[];
    readonly relationRevision: number;
    readonly appliedRequestId: number | null;
    readonly total: number | null;
    readonly error: unknown;
}
```

## NeuTreeFilterColumn

```typescript
export interface NeuTreeFilterColumn<T, F extends string> {
    readonly field: F;
    readonly value?: NeuTreeValueAccessor<T>;
    readonly rules: readonly NeuTreeFilterConstraint<F>["rule"][];
    readonly defaultRule: NeuTreeFilterConstraint<F>["rule"];
}
```

## NeuTreeFilterConstraint

```typescript
export interface NeuTreeFilterConstraint<F extends string> {
    readonly kind: "condition";
    readonly field: F;
    readonly rule: "equals" | "notEquals" | "contains" | "notContains" | "startsWith" | "endsWith" | "lessThan" | "lessThanOrEqual" | "greaterThan" | "greaterThanOrEqual" | "between" | "in" | "notIn" | "isNull" | "isNotNull" | "isEmpty" | "isNotEmpty";
    readonly value: unknown;
}
```

## NeuTreeFilterExpression

```typescript
export type NeuTreeFilterExpression<F extends string> = NeuTreeFilterConstraint<F> | NeuTreeFilterGroup<F>;
```

## NeuTreeFilterGroup

```typescript
export interface NeuTreeFilterGroup<F extends string> {
    readonly kind: "group";
    readonly operator: NeuTreeFilterOperator;
    readonly children: readonly NeuTreeFilterExpression<F>[];
}
```

## NeuTreeFilterOperator

```typescript
export type NeuTreeFilterOperator = 'and' | 'or';
```

## NeuTreeFilterPredicate

```typescript
export type NeuTreeFilterPredicate<T, F extends string> = (context: NeuTreeFilterPredicateContext<T, F>) => boolean;
```

## NeuTreeFilterPredicateContext

```typescript
export interface NeuTreeFilterPredicateContext<T, F extends string> {
    readonly value: T;
    readonly field: F;
    readonly candidate: unknown;
    readonly filterValue: unknown;
}
```

## NeuTreeFilterSurface

```typescript
export type NeuTreeFilterSurface = 'row' | 'menu' | 'builder';
```

## NeuTreeLoadedRelation

```typescript
export interface NeuTreeLoadedRelation<K extends NeuTreeTableKey> {
    readonly status: "loaded";
    readonly keys: readonly K[];
    readonly relationRevision: number;
    readonly appliedRequestId: number | null;
    readonly total: number | null;
    readonly completeness: NeuTreeRelationCompleteness;
}
```

## NeuTreeLoadingRelation

```typescript
export interface NeuTreeLoadingRelation<K extends NeuTreeTableKey> {
    readonly status: "loading";
    readonly keys: readonly K[];
    readonly relationRevision: number;
    readonly appliedRequestId: number;
    readonly total: number | null;
}
```

## NeuTreeRelation

```typescript
export type NeuTreeRelation<K extends NeuTreeTableKey> = NeuTreeUnloadedRelation<K> | NeuTreeLoadingRelation<K> | NeuTreeErrorRelation<K> | NeuTreeLoadedRelation<K>;
```

## NeuTreeRelationCompleteness

```typescript
export type NeuTreeRelationCompleteness = 'partial' | 'complete';
```

## NeuTreeRelationStatus

```typescript
export type NeuTreeRelationStatus = 'unloaded' | 'loading' | 'error' | 'loaded';
```

## NeuTreeSortColumn

```typescript
export interface NeuTreeSortColumn<T, F extends string> {
    readonly field: F;
    readonly value?: NeuTreeValueAccessor<T>;
    readonly compare?: (left: T, right: T) => number;
}
```

## NeuTreeSortDirection

```typescript
export type NeuTreeSortDirection = 'asc' | 'desc';
```

## NeuTreeSortEntry

```typescript
export interface NeuTreeSortEntry<F extends string> {
    readonly field: F;
    readonly direction: NeuTreeSortDirection;
}
```

## NeuTreeTableAppearance

```typescript
export interface NeuTreeTableAppearance {
    readonly density: "compact" | "normal" | "relaxed";
    readonly borders: "none" | "rows" | "cells";
    readonly striped: boolean;
    readonly stickyHeader: boolean;
    readonly responsive: "contained-scroll" | "stacked";
}
```

## NeuTreeTableCaptionDirective

Selector: `ng-template[neuTreeTableCaption]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTreeTableCellContext

```typescript
export interface NeuTreeTableCellContext<T, K extends NeuTreeTableKey, F extends string> extends NeuTreeTableNodeContext<T, K> {
    readonly column: NeuTreeTableColumn<T, F>;
    readonly columnIndex: number;
    readonly logicalIndex: number;
}
```

## NeuTreeTableCellDirective

Selector: `ng-template[neuTreeTableCell]`

| Input | Required | Type |
| --- | --- | --- |
| neuTreeTableCell | yes | `InputSignal<string>` |

| Output | Type |
| --- | --- |

## NeuTreeTableChildrenRequest

```typescript
export interface NeuTreeTableChildrenRequest<K extends NeuTreeTableKey, F extends string> extends NeuTreeTableRequestBase<F> {
    readonly kind: "children";
    readonly reason: "expand" | "query" | "retry";
    readonly parentKey: K;
    readonly relationRevision: number;
}
```

## NeuTreeTableColumn

```typescript
export interface NeuTreeTableColumn<T, F extends string> {
    readonly id: string;
    readonly header: string;
    readonly field?: F;
    readonly value?: NeuTreeValueAccessor<T>;
    readonly sort?: NeuTreeSortColumn<T, F>;
    readonly filter?: NeuTreeFilterColumn<T, F>;
    readonly edit?: NeuTreeEditColumn<T, F>;
    readonly width?: string;
    readonly minWidth?: string;
    readonly maxWidth?: string;
    readonly align?: "start" | "center" | "end";
}
```

## NeuTreeTableComponent

Selector: `neu-tree-table`

| Input | Required | Type |
| --- | --- | --- |
| dataMode | no | `InputSignal<NeuTreeTableDataMode>` |
| data | no | `InputSignal<readonly T[]>` |
| hierarchy | no | `InputSignal<NeuTreeTableHierarchy<K>>` |
| query | no | `InputSignal<NeuTreeTableQuery<F>>` |
| columns | no | `InputSignal<readonly NeuTreeTableColumn<T, F>[]>` |
| rowKey | yes | `InputSignal<(value: T) => K>` |
| expandedKeys | no | `InputSignal<readonly K[]>` |
| selection | no | `InputSignal<NeuTreeTableSelection<K>>` |
| layout | no | `InputSignal<NeuTreeTableLayoutState>` |
| editState | no | `InputSignal<NeuTreeTableEditState<K>>` |
| sortOptions | no | `InputSignal<NeuTreeTableSortOptions>` |
| filterOptions | no | `InputSignal<NeuTreeTableFilterOptions<T, F>>` |
| paginationOptions | no | `InputSignal<NeuTreeTablePaginationOptions>` |
| selectionOptions | no | `InputSignal<NeuTreeTableSelectionOptions<T>>` |
| virtualizationOptions | no | `InputSignal<NeuTreeTableVirtualizationOptions>` |
| editingOptions | no | `InputSignal<NeuTreeTableEditingOptions<T, K, F>>` |
| hierarchyOptions | yes | `InputSignal<NeuTreeTableHierarchyOptions>` |
| rowOptions | no | `InputSignal<NeuTreeTableRowOptions<T>>` |
| appearance | no | `InputSignal<NeuTreeTableAppearance>` |
| labels | no | `InputSignal<NeuTreeTableLabels>` |
| interactionOptions | no | `InputSignal<NeuTreeTableInteractionOptions>` |
| exportOptions | no | `InputSignal<NeuTreeTableExportOptions>` |

| Output | Type |
| --- | --- |
| queryChange | `OutputEmitterRef<NeuTreeTableQuery<F>>` |
| expandedKeysChange | `OutputEmitterRef<NeuTreeTableExpandedKeysChange<K>>` |
| selectionChange | `OutputEmitterRef<NeuTreeTableSelectionChange<T, K>>` |
| layoutChange | `OutputEmitterRef<NeuTreeTableLayoutChange>` |
| editStateChange | `OutputEmitterRef<NeuTreeTableEditChange<K>>` |
| dataRequest | `OutputEmitterRef<NeuTreeTableDataRequest<K, F>>` |
| rangeChange | `OutputEmitterRef<NeuTreeTableRangeChange>` |
| rowAction | `OutputEmitterRef<NeuTreeTableRowAction<T, K>>` |
| editCommit | `OutputEmitterRef<NeuTreeTableEditCommit<T, K, F>>` |
| editCancel | `OutputEmitterRef<NeuTreeTableEditCancel<T, K>>` |
| exportRequest | `OutputEmitterRef<NeuTreeTableExportRequest<F>>` |
| featureError | `OutputEmitterRef<NeuTreeTableFeatureError>` |

Supported imperative members:

```typescript
scrollTo(target: NeuTreeTableScrollTarget<K>): void;
focus(target: NeuTreeTableFocusTarget<K>): void;
retryData(target: NeuTreeTableRetryTarget<K>): void;
export(request: NeuTreeTableExportRequest<F>): Promise<NeuTreeTableExportOutcome>;
```

## NeuTreeTableDataMode

```typescript
export type NeuTreeTableDataMode = 'client' | 'remote';
```

## NeuTreeTableDataRequest

```typescript
export type NeuTreeTableDataRequest<K extends NeuTreeTableKey, F extends string> = NeuTreeTableRootsRequest<F> | NeuTreeTableChildrenRequest<K, F>;
```

## NeuTreeTableEditCancel

```typescript
export interface NeuTreeTableEditCancel<T, K extends NeuTreeTableKey> {
    readonly key: K;
    readonly value: T;
    readonly reason: "escape" | "gesture" | "hidden" | "destroy";
}
```

## NeuTreeTableEditChange

```typescript
export interface NeuTreeTableEditChange<K extends NeuTreeTableKey> {
    readonly next: NeuTreeTableEditState<K>;
    readonly source: "gesture" | "keyboard" | "commit" | "cancel" | "hidden";
}
```

## NeuTreeTableEditCommit

```typescript
export interface NeuTreeTableEditCommit<T, K extends NeuTreeTableKey, F extends string> {
    readonly key: K;
    readonly value: T;
    readonly field: F | null;
    readonly draft: Readonly<Partial<T>>;
    readonly source: "cell" | "row";
}
```

## NeuTreeTableEditingOptions

```typescript
export interface NeuTreeTableEditingOptions<T, K extends NeuTreeTableKey, F extends string> {
    readonly mode: "none" | "cell" | "row";
    readonly validate?: (context: {
        readonly value: T;
        readonly key: K;
        readonly field: F | null;
        readonly draft: Readonly<Partial<T>>;
    }) => true | string;
}
```

## NeuTreeTableEditorContext

```typescript
export interface NeuTreeTableEditorContext<T, K extends NeuTreeTableKey, F extends string> extends NeuTreeTableCellContext<T, K, F> {
    readonly field: F | null;
    readonly draftValue: unknown;
    readonly update: (value: unknown) => void;
    readonly commit: () => void;
    readonly cancel: () => void;
}
```

## NeuTreeTableEditorDirective

Selector: `ng-template[neuTreeTableEditor]`

| Input | Required | Type |
| --- | --- | --- |
| neuTreeTableEditor | yes | `InputSignal<string>` |

| Output | Type |
| --- | --- |

## NeuTreeTableEditState

```typescript
export type NeuTreeTableEditState<K extends NeuTreeTableKey> = {
    readonly kind: 'none';
} | {
    readonly kind: 'cell';
    readonly key: K;
    readonly columnId: string;
} | {
    readonly kind: 'row';
    readonly key: K;
};
```

## NeuTreeTableEmptyDirective

Selector: `ng-template[neuTreeTableEmpty]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTreeTableErrorDirective

Selector: `ng-template[neuTreeTableError]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTreeTableExpandedKeysChange

```typescript
export interface NeuTreeTableExpandedKeysChange<K extends NeuTreeTableKey> {
    readonly next: readonly K[];
    readonly source: "toggle" | "keyboard";
    readonly changedKey: K;
}
```

## NeuTreeTableExportOptions

```typescript
export interface NeuTreeTableExportOptions {
    readonly formats: readonly ("csv" | "json" | "xlsx")[];
    readonly defaultFilename: string;
}
```

## NeuTreeTableExportOutcome

```typescript
export type NeuTreeTableExportOutcome = {
    readonly status: 'downloaded';
    readonly filename: string;
    readonly rowCount: number;
} | {
    readonly status: 'delegated';
} | {
    readonly status: 'unsupported';
    readonly reason: string;
} | {
    readonly status: 'failed';
    readonly error: unknown;
};
```

## NeuTreeTableExportRequest

```typescript
export interface NeuTreeTableExportRequest<F extends string> {
    readonly format: "csv" | "json" | "xlsx";
    readonly scope: "visible" | "loaded" | "selected";
    readonly filename?: string;
    readonly query: NeuTreeTableQuery<F>;
}
```

## NeuTreeTableFeatureError

```typescript
export type NeuTreeTableFeatureError = {
    readonly feature: 'hierarchy';
    readonly code: 'cycle' | 'duplicate-key' | 'duplicate-parent' | 'missing-root' | 'missing-node' | 'duplicate-child' | 'orphan' | 'invalid-tree-column';
    readonly error: unknown;
} | {
    readonly feature: 'advanced-filter' | 'editor' | 'export';
    readonly error: unknown;
};
```

## NeuTreeTableFilterOptions

```typescript
export interface NeuTreeTableFilterOptions<T, F extends string> {
    readonly surfaces: readonly NeuTreeFilterSurface[];
    readonly globalFields: readonly F[];
    readonly predicates: Readonly<Record<string, NeuTreeFilterPredicate<T, F>>>;
    readonly debounceMs: number;
    readonly commit: "immediate" | "explicit";
    readonly equals?: (left: unknown, right: unknown) => boolean;
}
```

## NeuTreeTableFocusTarget

```typescript
export type NeuTreeTableFocusTarget<K extends NeuTreeTableKey> = {
    readonly kind: 'node';
    readonly key: K;
} | {
    readonly kind: 'cell';
    readonly key: K;
    readonly columnId: string;
} | {
    readonly kind: 'first' | 'last';
};
```

## NeuTreeTableFooterDirective

Selector: `ng-template[neuTreeTableFooter]`

| Input | Required | Type |
| --- | --- | --- |
| neuTreeTableFooter | yes | `InputSignal<string>` |

| Output | Type |
| --- | --- |

## NeuTreeTableHeaderContext

```typescript
export interface NeuTreeTableHeaderContext<T, F extends string> {
    readonly column: NeuTreeTableColumn<T, F>;
    readonly columnIndex: number;
}
```

## NeuTreeTableHeaderDirective

Selector: `ng-template[neuTreeTableHeader]`

| Input | Required | Type |
| --- | --- | --- |
| neuTreeTableHeader | yes | `InputSignal<string>` |

| Output | Type |
| --- | --- |

## NeuTreeTableHierarchy

```typescript
export interface NeuTreeTableHierarchy<K extends NeuTreeTableKey> {
    readonly hierarchyRevision: number;
    readonly queryRevision: number;
    readonly roots: NeuTreeRelation<K>;
    readonly children: readonly NeuTreeChildRelation<K>[];
}
```

## NeuTreeTableHierarchyOptions

```typescript
export interface NeuTreeTableHierarchyOptions {
    readonly treeColumnId: string;
    readonly indentSize: number;
}
```

## NeuTreeTableInteractionOptions

```typescript
export interface NeuTreeTableInteractionOptions {
    readonly navigation: "row";
    readonly wrapFocus: boolean;
    readonly announceChanges: boolean;
    readonly contextMenuAction: boolean;
}
```

## NeuTreeTableKey

```typescript
export type NeuTreeTableKey = string | number;
```

## NeuTreeTableLabels

```typescript
export interface NeuTreeTableLabels {
    readonly ariaLabel: string;
    readonly empty: string;
    readonly loading: string;
    readonly error: string;
    readonly retry: string;
    readonly expand: string;
    readonly collapse: string;
    readonly selection: string;
    readonly pagination: string;
}
```

## NeuTreeTableLayoutChange

```typescript
export interface NeuTreeTableLayoutChange {
    readonly next: NeuTreeTableLayoutState;
    readonly source: "resize" | "reorder" | "visibility" | "pin";
}
```

## NeuTreeTableLayoutState

```typescript
export interface NeuTreeTableLayoutState {
    readonly order: readonly string[];
    readonly hidden: readonly string[];
    readonly widths: Readonly<Record<string, string>>;
    readonly pinnedStart: readonly string[];
    readonly pinnedEnd: readonly string[];
}
```

## NeuTreeTableLoadingDirective

Selector: `ng-template[neuTreeTableLoading]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTreeTableNodeContext

```typescript
export interface NeuTreeTableNodeContext<T, K extends NeuTreeTableKey> {
    readonly $implicit: T;
    readonly value: T;
    readonly key: K;
    readonly parentKey: K | null;
    readonly depth: number;
    readonly siblingIndex: number;
    readonly siblingCount: number | null;
    readonly path: readonly K[];
    readonly expanded: boolean;
    readonly selected: boolean;
    readonly indeterminate: boolean;
    readonly disabled: boolean;
    readonly childStatus: NeuTreeRelationStatus;
    readonly toggleExpansion: () => void;
    readonly toggleSelection: () => void;
}
```

## NeuTreeTableNodeDirective

Selector: `ng-template[neuTreeTableNode]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTreeTablePaginationOptions

```typescript
export interface NeuTreeTablePaginationOptions {
    readonly enabled: boolean;
    readonly pageSizeOptions: readonly number[];
    readonly position: "top" | "bottom" | "both";
    readonly report: "none" | "roots";
}
```

## NeuTreeTableQuery

```typescript
export interface NeuTreeTableQuery<F extends string> {
    readonly page: number;
    readonly pageSize: number;
    readonly search: string;
    readonly sort: readonly NeuTreeSortEntry<F>[];
    readonly filters: NeuTreeFilterExpression<F> | null;
}
```

## NeuTreeTableRange

```typescript
export interface NeuTreeTableRange {
    readonly start: number;
    readonly end: number;
}
```

## NeuTreeTableRangeChange

```typescript
export interface NeuTreeTableRangeChange {
    readonly visible: NeuTreeTableRange;
    readonly render: NeuTreeTableRange;
    readonly projectionRevision: number;
    readonly reason: "scroll" | "resize" | "programmatic" | "hierarchy";
}
```

## NeuTreeTableRequestBase

```typescript
export interface NeuTreeTableRequestBase<F extends string> {
    readonly requestId: number;
    readonly queryRevision: number;
    readonly hierarchyRevision: number;
    readonly query: NeuTreeTableQuery<F>;
}
```

## NeuTreeTableRetryTarget

```typescript
export type NeuTreeTableRetryTarget<K extends NeuTreeTableKey> = {
    readonly kind: 'roots';
} | {
    readonly kind: 'children';
    readonly parentKey: K;
};
```

## NeuTreeTableRootsRequest

```typescript
export interface NeuTreeTableRootsRequest<F extends string> extends NeuTreeTableRequestBase<F> {
    readonly kind: "roots";
    readonly reason: "initial" | "query" | "page" | "retry";
    readonly relationRevision: number;
}
```

## NeuTreeTableRowAction

```typescript
export interface NeuTreeTableRowAction<T, K extends NeuTreeTableKey> {
    readonly key: K;
    readonly value: T;
    readonly source: "click" | "double-click" | "keyboard" | "context-menu";
}
```

## NeuTreeTableRowOptions

```typescript
export interface NeuTreeTableRowOptions<T> {
    readonly className?: (value: T) => string | readonly string[] | null;
}
```

## NeuTreeTableScrollTarget

```typescript
export type NeuTreeTableScrollTarget<K extends NeuTreeTableKey> = {
    readonly kind: 'node';
    readonly key: K;
    readonly behavior?: ScrollBehavior;
} | {
    readonly kind: 'index';
    readonly index: number;
    readonly behavior?: ScrollBehavior;
} | {
    readonly kind: 'offset';
    readonly offset: number;
    readonly behavior?: ScrollBehavior;
};
```

## NeuTreeTableSelection

```typescript
export interface NeuTreeTableSelection<K extends NeuTreeTableKey> {
    readonly kind: "keys";
    readonly keys: readonly K[];
}
```

## NeuTreeTableSelectionChange

```typescript
export interface NeuTreeTableSelectionChange<T, K extends NeuTreeTableKey> {
    readonly next: NeuTreeTableSelection<K>;
    readonly source: "row" | "radio" | "checkbox" | "keyboard" | "toggle-all";
    readonly addedKeys: readonly K[];
    readonly removedKeys: readonly K[];
    readonly loadedValues: readonly T[];
    readonly propagation: "none" | "loaded-subtree";
}
```

## NeuTreeTableSelectionOptions

```typescript
export type NeuTreeTableSelectionOptions<T> = {
    readonly mode: 'none';
} | {
    readonly mode: 'single';
    readonly indicator: 'none' | 'radio';
    readonly selectOnRowClick: boolean;
    readonly allowClear: boolean;
    readonly isNodeDisabled?: (value: T) => boolean;
} | {
    readonly mode: 'multiple' | 'checkbox';
    readonly indicator: 'none' | 'checkbox';
    readonly selectOnRowClick: boolean;
    readonly modifier: 'replace' | 'platform' | 'toggle';
    readonly range: boolean;
    readonly propagation: 'none' | 'loaded-subtree';
    readonly toggleAllScope: 'visible' | 'loaded';
    readonly isNodeDisabled?: (value: T) => boolean;
};
```

## NeuTreeTableSortOptions

```typescript
export interface NeuTreeTableSortOptions {
    readonly mode: "single" | "multiple";
    readonly removable: boolean;
    readonly defaultDirection: NeuTreeSortDirection;
    readonly resetRootPageOnChange: boolean;
}
```

## NeuTreeTableStateContext

```typescript
export interface NeuTreeTableStateContext {
    readonly retry: () => void;
}
```

## NeuTreeTableSummaryDirective

Selector: `ng-template[neuTreeTableSummary]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTreeTableTemplateDirective

```typescript
export interface NeuTreeTableTemplateDirective<C> {
    readonly templateRef: TemplateRef<C>;
}
```

## NeuTreeTableToolbarDirective

Selector: `ng-template[neuTreeTableToolbar]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTreeTableVirtualizationOptions

```typescript
export type NeuTreeTableVirtualizationOptions = {
    readonly enabled: false;
} | {
    readonly enabled: true;
    readonly itemSize: number;
    readonly overscan: number;
};
```

## NeuTreeUnloadedRelation

```typescript
export interface NeuTreeUnloadedRelation<K extends NeuTreeTableKey> {
    readonly status: "unloaded";
    readonly keys: readonly K[];
    readonly relationRevision: number;
    readonly appliedRequestId: number | null;
    readonly total: number | null;
}
```

## NeuTreeValueAccessor

```typescript
export type NeuTreeValueAccessor<T> = (value: T) => unknown;
```

## NormalizedTreeHierarchy

```typescript
interface NormalizedTreeHierarchy<T, K extends NeuTreeTableKey> {
    readonly nodes: ReadonlyMap<string, IndexedTreeNode<T, K>>;
    readonly roots: readonly string[];
    readonly children: ReadonlyMap<string, readonly string[]>;
    readonly parentByToken: ReadonlyMap<string, string | null>;
    readonly relations: ReadonlyMap<string, NeuTreeRelation<K>>;
    readonly blockedEdges: ReadonlySet<string>;
    readonly reachable: ReadonlySet<string>;
    readonly diagnostics: readonly TreeDiagnostic<K>[];
    readonly rootRelation: NeuTreeRelation<K>;
    readonly hierarchyRevision: number;
}
```

## normalizeNeuTreeSearch

```typescript
declare function normalizeNeuTreeSearch(value: string): string;
```

## normalizeNeuTreeTableHierarchy

```typescript
declare function normalizeNeuTreeTableHierarchy<T extends object, K extends NeuTreeTableKey>(data: readonly T[], rowKey: (value: T) => K, hierarchy: NeuTreeTableHierarchy<K>): NormalizedTreeHierarchy<T, K>;
```

## projectNeuTreeTableHierarchy

```typescript
declare function projectNeuTreeTableHierarchy<T extends object, K extends NeuTreeTableKey>(data: readonly T[], rowKey: (value: T) => K, hierarchy: NeuTreeTableHierarchy<K>, expandedKeys: readonly K[]): TreeProjection<T, K>;
```

## projectNormalizedNeuTreeTableHierarchy

```typescript
declare function projectNormalizedNeuTreeTableHierarchy<T extends object, K extends NeuTreeTableKey>(normalized: NormalizedTreeHierarchy<T, K>, expandedKeys: readonly K[], queryProjection?: TreeQueryProjection): TreeProjection<T, K>;
```

## proposeNeuTreeTableSelection

```typescript
declare function proposeNeuTreeTableSelection<T extends object, K extends NeuTreeTableKey>(options: {
    readonly model: TreeSelectionModel<T, K>;
    readonly selection: NeuTreeTableSelection<K>;
    readonly selectionOptions: NeuTreeTableSelectionOptions<T>;
    readonly intent: TreeSelectionIntent<K>;
}): NeuTreeTableSelectionChange<T, K> | null;
```

## proposeNeuTreeTableSort

```typescript
declare function proposeNeuTreeTableSort<F extends string>(query: NeuTreeTableQuery<F>, field: F, options: NeuTreeTableSortOptions): NeuTreeTableQuery<F>;
```

## readNeuTreeTableFilterValue

```typescript
declare function readNeuTreeTableFilterValue<F extends string>(expression: NeuTreeFilterExpression<F> | null, field: F): unknown;
```

## replaceNeuTreeTableFilter

```typescript
declare function replaceNeuTreeTableFilter<F extends string>(expression: NeuTreeFilterExpression<F> | null, field: F, next: NeuTreeFilterConstraint<F> | null): NeuTreeFilterExpression<F> | null;
```

## TreeDiagnostic

```typescript
interface TreeDiagnostic<K extends NeuTreeTableKey> {
    readonly code: TreeDiagnosticCode;
    readonly key: K;
    readonly parentKey: K | null;
    readonly path: readonly K[];
    readonly fingerprint: string;
}
```

## TreeDiagnosticCode

```typescript
type TreeDiagnosticCode = 'cycle' | 'duplicate-key' | 'duplicate-parent' | 'missing-root' | 'missing-node' | 'duplicate-child' | 'orphan';
```

## TreeProjection

```typescript
interface TreeProjection<T, K extends NeuTreeTableKey> {
    readonly projectionRevision: number;
    readonly visible: readonly TreeProjectionNode<T, K>[];
    readonly nodesByToken: ReadonlyMap<string, TreeProjectionNode<T, K>>;
    readonly normalized: NormalizedTreeHierarchy<T, K>;
    readonly diagnostics: readonly TreeDiagnostic<K>[];
}
```

## TreeProjectionNode

```typescript
interface TreeProjectionNode<T, K extends NeuTreeTableKey> {
    readonly key: K;
    readonly token: string;
    readonly value: T;
    readonly parentKey: K | null;
    readonly depth: number;
    readonly siblingIndex: number;
    readonly siblingCount: number | null;
    readonly path: readonly K[];
    readonly relation: NeuTreeRelation<K>;
    readonly expanded: boolean;
    readonly appliedExpanded: boolean;
    readonly transientlyRevealed: boolean;
    readonly expandable: boolean;
    readonly logicalVisibleIndex: number;
}
```

## TreeQueryProjection

```typescript
interface TreeQueryProjection {
    readonly roots: readonly string[];
    readonly children: ReadonlyMap<string, readonly string[]>;
    readonly retained: ReadonlySet<string>;
    readonly transientReveal: ReadonlySet<string>;
    readonly filtering: boolean;
}
```

## TreeSelectionIntent

```typescript
type TreeSelectionIntent<K extends NeuTreeTableKey> = {
    readonly kind: 'node';
    readonly key: K;
    readonly source: 'row' | 'radio' | 'checkbox' | 'keyboard';
    readonly anchorKey: K | null;
    readonly shiftKey: boolean;
    readonly platformModifier: boolean;
} | {
    readonly kind: 'toggle-all';
    readonly source: 'toggle-all';
};
```

## TreeSelectionModel

```typescript
interface TreeSelectionModel<T extends object, K extends NeuTreeTableKey> {
    readonly projection: TreeProjection<T, K>;
    readonly byToken: ReadonlyMap<string, TreeSelectionNodeState>;
    readonly loadedOrder: readonly string[];
    readonly visibleOrder: readonly string[];
    readonly header: TreeSelectionNodeState;
}
```

## TreeSelectionNodeState

```typescript
interface TreeSelectionNodeState {
    readonly selected: boolean;
    readonly checked: boolean;
    readonly indeterminate: boolean;
    readonly disabled: boolean;
    readonly selectableCount: number;
    readonly selectedCount: number;
    readonly complete: boolean;
}
```

