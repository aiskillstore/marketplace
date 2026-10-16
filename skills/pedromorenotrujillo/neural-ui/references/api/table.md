# @neural-ui/core/table

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## alignNeuTableRequestRange

```typescript
declare function alignNeuTableRequestRange(required: NeuTableRange, step: number, total: number | null): NeuTableRange;
```

## areNeuTableLayoutsEqual

```typescript
declare function areNeuTableLayoutsEqual(left: NeuTableLayoutState, right: NeuTableLayoutState): boolean;
```

## areNeuTableQueriesSemanticallyEqual

```typescript
declare function areNeuTableQueriesSemanticallyEqual<F extends string>(left: NeuTableEffectiveQuery<F>, right: NeuTableEffectiveQuery<F>): boolean;
```

## areNeuTableRangesEqual

```typescript
declare function areNeuTableRangesEqual(left: NeuTableRange | null | undefined, right: NeuTableRange | null | undefined): boolean;
```

## areNeuTableSelectionScopesEqual

```typescript
declare function areNeuTableSelectionScopesEqual<F extends string>(left: NeuTableSelectionScope<F>, right: NeuTableSelectionScope<F>): boolean;
```

## areNeuTableSelectionsEqual

```typescript
declare function areNeuTableSelectionsEqual<K extends NeuTableKey, F extends string>(left: NeuTableSelection<K, F>, right: NeuTableSelection<K, F>): boolean;
```

## buildNeuTableEditCommit

```typescript
declare function buildNeuTableEditCommit<T extends object, K extends NeuTableKey, F extends string>(session: NeuTableEditSession<T, K, F>): NeuTableEditCommit<T, K, F>;
```

## classifyNeuTableRemoteCorrelation

```typescript
declare function classifyNeuTableRemoteCorrelation<F extends string>(state: NeuTableRemoteCoordinatorState<F>, metadata: NeuTableMetadata, requiredRange?: NeuTableRange | null): NeuTableRemoteCorrelation;
```

## createNeuTableEditSession

```typescript
declare function createNeuTableEditSession<T extends object, K extends NeuTableKey, F extends string>(args: {
    readonly generation: number;
    readonly state: Exclude<NeuTableEditState<K>, {
        readonly kind: 'none';
    }>;
    readonly row: T;
    readonly columns: readonly NeuTableColumn<T, F>[];
}): NeuTableEditSession<T, K, F> | null;
```

## createNeuTableFieldResolver

```typescript
declare function createNeuTableFieldResolver<T extends object, F extends string>(columns: readonly NeuTableColumn<T, F>[]): NeuTableFieldResolver<T, F>;
```

## createNeuTableRemoteCoordinatorState

```typescript
declare function createNeuTableRemoteCoordinatorState<F extends string>(): NeuTableRemoteCoordinatorState<F>;
```

## createNeuTableSelectionScope

```typescript
declare function createNeuTableSelectionScope<T, F extends string>(query: NeuTableQuery<F>, filterOptions: NeuTableFilterOptions<T, F>): NeuTableSelectionScope<F>;
```

## destroyNeuTableRemoteCoordinator

```typescript
declare function destroyNeuTableRemoteCoordinator<F extends string>(state: NeuTableRemoteCoordinatorState<F>): NeuTableRemoteCoordinatorState<F>;
```

## doesNeuTableRangeCover

```typescript
declare function doesNeuTableRangeCover(available: NeuTableRange | undefined, required: NeuTableRange | null | undefined): boolean;
```

## effectiveNeuTableRequestStep

```typescript
declare function effectiveNeuTableRequestStep(value: number | undefined): number;
```

## evaluateNeuTableFilterRule

```typescript
declare function evaluateNeuTableFilterRule<F extends string>(candidate: unknown, rule: NeuTableFilterRule<F> | string, filterValue: unknown, equals?: (left: unknown, right: unknown) => boolean): boolean;
```

## filterNeuTableRows

```typescript
declare function filterNeuTableRows<T, F extends string>(rows: readonly T[], filters: NeuFilterExpression<F> | null, resolver: NeuTableFieldResolver<T, F>, options: NeuTableFilterOptions<T, F>): readonly T[];
```

## isNeuTableRemoteStateSatisfied

```typescript
declare function isNeuTableRemoteStateSatisfied(metadata: NeuTableMetadata, queryRevision: number, requiredRange?: NeuTableRange | null, latestRequestId?: number | null): boolean;
```

## isNeuTableRowDisabled

```typescript
declare function isNeuTableRowDisabled<T, K extends NeuTableKey>(row: T, selectionOptions: NeuTableSelectionOptions<T>, rowOptions: NeuTableRowOptions<T, K>): boolean;
```

## NeuFilterConstraint

```typescript
export interface NeuFilterConstraint<F extends string> {
    readonly kind: "condition";
    readonly field: F;
    readonly rule: "equals" | "notEquals" | "contains" | "notContains" | "startsWith" | "endsWith" | "lessThan" | "lessThanOrEqual" | "greaterThan" | "greaterThanOrEqual" | "between" | "in" | "notIn" | "isNull" | "isNotNull" | "isEmpty" | "isNotEmpty";
    readonly value: unknown;
}
```

## NeuFilterExpression

```typescript
export type NeuFilterExpression<F extends string> = NeuFilterConstraint<F> | NeuFilterGroup<F>;
```

## NeuFilterGroup

```typescript
export interface NeuFilterGroup<F extends string> {
    readonly kind: "group";
    readonly operator: NeuFilterOperator;
    readonly children: readonly NeuFilterExpression<F>[];
}
```

## NeuFilterOperator

```typescript
export type NeuFilterOperator = 'and' | 'or';
```

## NeuRowKey

```typescript
export type NeuRowKey<T, K extends NeuTableKey> = (row: T) => K;
```

## NeuRowTrackBy

```typescript
export type NeuRowTrackBy<T> = (index: number, row: T) => unknown;
```

## NeuSortDirection

```typescript
export type NeuSortDirection = 'asc' | 'desc';
```

## NeuSortEntry

```typescript
export interface NeuSortEntry<F extends string> {
    readonly field: F;
    readonly direction: NeuSortDirection;
}
```

## NeuTableAppearance

```typescript
export interface NeuTableAppearance {
    readonly density: "compact" | "normal" | "relaxed";
    readonly borders: "none" | "rows" | "cells";
    readonly striped: boolean;
    readonly stickyHeader: boolean;
    readonly responsive: "contained-scroll" | "stacked";
}
```

## NeuTableCaptionDirective

Selector: `ng-template[neuTableCaption]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTableCellContext

```typescript
export interface NeuTableCellContext<T, K extends NeuTableKey> extends NeuTableRowContext<T, K> {
    readonly columnId: string;
    readonly value: unknown;
}
```

## NeuTableCellDirective

Selector: `ng-template[neuTableCell]`

| Input | Required | Type |
| --- | --- | --- |
| neuTableCell | yes | `InputSignal<string>` |

| Output | Type |
| --- | --- |

## NeuTableClientPipelineResult

```typescript
interface NeuTableClientPipelineResult<T, F extends string> {
    readonly rows: readonly T[];
    readonly query: NeuTableEffectiveQuery<F>;
    readonly sourceNormalCount: number;
    readonly matchedNormalCount: number;
    readonly pageNormalCount: number;
    readonly pageCount: number;
    readonly pageStart: number;
    readonly pageEnd: number;
}
```

## NeuTableColumn

```typescript
export interface NeuTableColumn<T, F extends string> {
    readonly id: string;
    readonly header: string;
    readonly field?: F;
    readonly value?: NeuTableValueAccessor<T>;
    readonly sort?: NeuTableSortColumn<T, F>;
    readonly filter?: NeuTableFilterColumn<T, F>;
    readonly edit?: NeuTableEditColumn<T, F>;
    readonly width?: string;
    readonly minWidth?: string;
    readonly maxWidth?: string;
    readonly align?: "start" | "center" | "end";
}
```

## NeuTableColumnOptions

```typescript
export interface NeuTableColumnOptions {
    readonly reorderable?: boolean;
    readonly resizable?: boolean;
    readonly hideable?: boolean;
    readonly pinnable?: boolean;
}
```

## NeuTableColumnPin

```typescript
type NeuTableColumnPin = 'start' | 'end' | null;
```

## NeuTableComponent

Selector: `neu-table`

| Input | Required | Type |
| --- | --- | --- |
| dataMode | no | `InputSignal<NeuTableDataMode>` |
| data | no | `InputSignal<readonly T[]>` |
| metadata | no | `InputSignal<NeuTableMetadata>` |
| columns | no | `InputSignal<readonly NeuTableColumn<T, F>[]>` |
| query | no | `InputSignal<NeuTableQuery<F>>` |
| rowKey | yes | `InputSignal<NeuRowKey<T, K>>` |
| rowTrackBy | no | `InputSignal<NeuRowTrackBy<T> \| undefined>` |
| selection | no | `InputSignal<NeuTableSelection<K, F>>` |
| layout | no | `InputSignal<NeuTableLayoutState>` |
| expandedKeys | no | `InputSignal<readonly K[]>` |
| editState | no | `InputSignal<NeuTableEditState<K>>` |
| grouping | no | `InputSignal<NeuTableGroupingState<F> \| null>` |
| sortOptions | no | `InputSignal<NeuTableSortOptions>` |
| filterOptions | no | `InputSignal<NeuTableFilterOptions<T, F>>` |
| paginationOptions | no | `InputSignal<NeuTablePaginationOptions>` |
| selectionOptions | no | `InputSignal<NeuTableSelectionOptions<T>>` |
| virtualizationOptions | no | `InputSignal<NeuTableVirtualizationOptions>` |
| editingOptions | no | `InputSignal<NeuTableEditingOptions<T, K, F>>` |
| expansionOptions | no | `InputSignal<NeuTableExpansionOptions<T>>` |
| groupingOptions | no | `InputSignal<NeuTableGroupingOptions<T, F>>` |
| columnOptions | no | `InputSignal<NeuTableColumnOptions>` |
| rowOptions | no | `InputSignal<NeuTableRowOptions<T, K>>` |
| appearance | no | `InputSignal<NeuTableAppearance>` |
| labels | no | `InputSignal<NeuTableLabels>` |
| interactionOptions | no | `InputSignal<NeuTableInteractionOptions>` |

| Output | Type |
| --- | --- |
| queryChange | `OutputEmitterRef<NeuTableQuery<F>>` |
| selectionChange | `OutputEmitterRef<NeuTableSelectionChange<T, K, F>>` |
| layoutChange | `OutputEmitterRef<NeuTableLayoutChange>` |
| expandedKeysChange | `OutputEmitterRef<NeuTableExpandedKeysChange<K>>` |
| editStateChange | `OutputEmitterRef<NeuTableEditChange<K>>` |
| groupingChange | `OutputEmitterRef<NeuTableGroupingChange<F>>` |
| dataRequest | `OutputEmitterRef<NeuTableDataRequest<F>>` |
| rangeChange | `OutputEmitterRef<NeuTableRangeChange>` |
| rowAction | `OutputEmitterRef<NeuTableRowAction<T, K>>` |
| editCommit | `OutputEmitterRef<NeuTableEditCommit<T, K, F>>` |
| editCancel | `OutputEmitterRef<NeuTableEditCancel<T, K>>` |
| rowReorder | `OutputEmitterRef<NeuTableRowMove<K>>` |
| exportRequest | `OutputEmitterRef<NeuTableExportRequest<F>>` |
| featureError | `OutputEmitterRef<NeuTableFeatureError>` |

Supported imperative members:

```typescript
focusCell(target: {
    readonly key: K;
    readonly columnId: string;
}): boolean;
scrollTo(target: {
    readonly index?: number;
    readonly key?: K;
}): Promise<void>;
retryData(): void;
export(request: NeuTableExportRequest<F>): Promise<NeuTableExportOutcome>;
```

## NeuTableDataMode

```typescript
export type NeuTableDataMode = 'client' | 'remote';
```

## NeuTableDataRequest

```typescript
export interface NeuTableDataRequest<F extends string> {
    readonly requestId: number;
    readonly queryRevision: number;
    readonly query: NeuTableQuery<F>;
    readonly reason: NeuTableDataRequestReason;
    readonly range?: NeuTableRange;
}
```

## NeuTableDataRequestReason

```typescript
export type NeuTableDataRequestReason = 'initial' | 'query' | 'viewport' | 'retry';
```

## NeuTableDetailContext

```typescript
export interface NeuTableDetailContext<T, K extends NeuTableKey> extends NeuTableRowContext<T, K> {
}
```

## NeuTableEditCancel

```typescript
export interface NeuTableEditCancel<T, K extends NeuTableKey> {
    readonly key: K;
    readonly row: T;
    readonly reason: "escape" | "consumer" | "data-change";
}
```

## NeuTableEditChange

```typescript
export interface NeuTableEditChange<K extends NeuTableKey> {
    readonly next: NeuTableEditState<K>;
    readonly source: "pointer" | "keyboard" | "programmatic" | "commit" | "cancel";
}
```

## NeuTableEditColumn

```typescript
export interface NeuTableEditColumn<T, F extends string> {
    readonly field: F;
    readonly read?: NeuTableValueAccessor<T>;
    readonly write?: (row: T, value: unknown) => T;
}
```

## NeuTableEditCommit

```typescript
export interface NeuTableEditCommit<T, K extends NeuTableKey, F extends string> {
    readonly key: K;
    readonly row: T;
    readonly changes: readonly NeuTableEditValueChange<F>[];
}
```

## NeuTableEditDraftEntry

```typescript
interface NeuTableEditDraftEntry<F extends string> {
    readonly columnId: string;
    readonly field?: F;
    readonly previous: unknown;
    readonly value: unknown;
}
```

## NeuTableEditError

```typescript
export interface NeuTableEditError {
    readonly code: string;
    readonly message: string;
    readonly columnId?: string;
}
```

## NeuTableEditingOptions

```typescript
export type NeuTableEditingOptions<T, K extends NeuTableKey, F extends string> = {
    readonly mode: 'none';
} | {
    readonly mode: 'cell' | 'row';
    readonly activation: 'click' | 'double-click' | 'enter' | 'f2';
    readonly validate?: NeuTableEditValidation<T, K, F>;
    readonly commitOnBlur: boolean;
};
```

## NeuTableEditorContext

```typescript
export interface NeuTableEditorContext<T, K extends NeuTableKey, F extends string> extends NeuTableCellContext<T, K> {
    readonly valueSignal: Signal<unknown>;
    readonly errors: Signal<readonly NeuTableEditError[]>;
    readonly setValue: (value: unknown) => void;
    readonly commit: () => void;
    readonly cancel: () => void;
}
```

## NeuTableEditorDirective

Selector: `ng-template[neuTableEditor]`

| Input | Required | Type |
| --- | --- | --- |
| neuTableEditor | yes | `InputSignal<string>` |

| Output | Type |
| --- | --- |

## NeuTableEditReconciliation

```typescript
type NeuTableEditReconciliation = 'equal' | 'changed';
```

## NeuTableEditSession

```typescript
interface NeuTableEditSession<T extends object, K extends NeuTableKey, F extends string> {
    readonly generation: number;
    readonly state: Exclude<NeuTableEditState<K>, {
        readonly kind: "none";
    }>;
    readonly keyToken: string;
    row: T;
    readonly draft: WritableSignal<ReadonlyMap<string, NeuTableEditDraftEntry<F>>>;
    readonly errors: WritableSignal<readonly NeuTableEditError[]>;
    readonly pending: WritableSignal<boolean>;
    requestPending: boolean;
    validationVersion: number;
}
```

## NeuTableEditState

```typescript
export type NeuTableEditState<K extends NeuTableKey> = {
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

## neuTableEditStateToken

```typescript
declare function neuTableEditStateToken<K extends NeuTableKey>(state: NeuTableEditState<K>): string;
```

## NeuTableEditValidation

```typescript
export type NeuTableEditValidation<T, K extends NeuTableKey, F extends string> = (event: NeuTableEditCommit<T, K, F>) => readonly NeuTableEditError[] | Promise<readonly NeuTableEditError[]>;
```

## NeuTableEditValueChange

```typescript
export interface NeuTableEditValueChange<F extends string> {
    readonly columnId: string;
    readonly field?: F;
    readonly previous: unknown;
    readonly value: unknown;
}
```

## neuTableEditValueSignal

```typescript
declare function neuTableEditValueSignal<F extends string>(session: {
    readonly draft: Signal<ReadonlyMap<string, NeuTableEditDraftEntry<F>>>;
}, columnId: string): Signal<unknown>;
```

## NeuTableEffectiveQuery

```typescript
interface NeuTableEffectiveQuery<F extends string> {
    readonly page: number;
    readonly pageSize: number;
    readonly search: string;
    readonly sort: readonly NeuSortEntry<F>[];
    readonly filters: NeuFilterExpression<F> | null;
}
```

## NeuTableEmptyDirective

Selector: `ng-template[neuTableEmpty]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTableErrorDirective

Selector: `ng-template[neuTableError]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTableExpandedKeysChange

```typescript
export interface NeuTableExpandedKeysChange<K extends NeuTableKey> {
    readonly next: readonly K[];
    readonly key: K;
    readonly expanded: boolean;
    readonly source: "toggle" | "keyboard" | "programmatic";
}
```

## NeuTableExpansionOptions

```typescript
export interface NeuTableExpansionOptions<T> {
    readonly enabled: boolean;
    readonly toggleOnRowClick: boolean;
    readonly isExpandable?: (row: T) => boolean;
}
```

## NeuTableExportFormat

```typescript
export type NeuTableExportFormat = 'csv' | 'json' | 'xlsx';
```

## NeuTableExportOutcome

```typescript
export type NeuTableExportOutcome = {
    readonly kind: 'generated';
    readonly result: NeuTableExportResult;
} | {
    readonly kind: 'delegated';
};
```

## NeuTableExportRequest

```typescript
export interface NeuTableExportRequest<F extends string> {
    readonly format: NeuTableExportFormat;
    readonly scope: NeuTableExportScope;
    readonly fileName: string;
    readonly query: NeuTableQuery<F>;
}
```

## NeuTableExportResult

```typescript
export interface NeuTableExportResult {
    readonly fileName: string;
    readonly mediaType: string;
    readonly bytes: Uint8Array;
}
```

## NeuTableExportScope

```typescript
export type NeuTableExportScope = 'page' | 'loaded' | 'filtered' | 'selected' | 'all';
```

## NeuTableFeatureError

```typescript
export interface NeuTableFeatureError {
    readonly feature: "filters" | "editing" | "virtualization" | "export";
    readonly cause: unknown;
    readonly recoverable: boolean;
}
```

## NeuTableFieldResolver

```typescript
interface NeuTableFieldResolver<T, F extends string> {
    readonly resolve: (row: T, field: F) => unknown;
    readonly comparator: (field: F) => ((left: T, right: T) => number) | undefined;
}
```

## NeuTableFilterColumn

```typescript
export interface NeuTableFilterColumn<T, F extends string> {
    readonly field: F;
    readonly value?: NeuTableValueAccessor<T>;
    readonly rules: readonly NeuFilterConstraint<F>["rule"][];
    readonly defaultRule: NeuFilterConstraint<F>["rule"];
}
```

## NeuTableFilterContext

```typescript
export interface NeuTableFilterContext<T, F extends string> extends NeuTableHeaderContext<T, F> {
    readonly value: unknown;
    readonly rule: NeuFilterConstraint<F>["rule"];
    readonly apply: (value: unknown, rule?: NeuFilterConstraint<F>["rule"]) => void;
    readonly clear: () => void;
}
```

## NeuTableFilterDirective

Selector: `ng-template[neuTableFilter]`

| Input | Required | Type |
| --- | --- | --- |
| neuTableFilter | yes | `InputSignal<string>` |

| Output | Type |
| --- | --- |

## NeuTableFilterOptions

```typescript
export interface NeuTableFilterOptions<T, F extends string> {
    readonly surfaces: readonly NeuTableFilterSurface[];
    readonly globalFields: readonly F[];
    readonly predicates: Readonly<Record<string, NeuTableFilterPredicate<T, F>>>;
    readonly debounceMs: number;
    readonly commit: "immediate" | "explicit";
    readonly equals?: (left: unknown, right: unknown) => boolean;
}
```

## NeuTableFilterPredicate

```typescript
export type NeuTableFilterPredicate<T, F extends string> = (context: NeuTableFilterPredicateContext<T, F>) => boolean;
```

## NeuTableFilterPredicateContext

```typescript
export interface NeuTableFilterPredicateContext<T, F extends string> {
    readonly row: T;
    readonly field: F;
    readonly candidate: unknown;
    readonly filterValue: unknown;
}
```

## NeuTableFilterRule

```typescript
type NeuTableFilterRule<F extends string> = NeuFilterConstraint<F>['rule'];
```

## NeuTableFilterSurface

```typescript
export type NeuTableFilterSurface = 'row' | 'menu' | 'builder';
```

## NeuTableFooterDirective

Selector: `ng-template[neuTableFooter]`

| Input | Required | Type |
| --- | --- | --- |
| neuTableFooter | yes | `InputSignal<string>` |

| Output | Type |
| --- | --- |

## NeuTableGroupContext

```typescript
export interface NeuTableGroupContext<T> {
    readonly id: string;
    readonly level: number;
    readonly value: unknown;
    readonly rows: readonly T[];
    readonly expanded: boolean;
}
```

## NeuTableGroupFooterDirective

Selector: `ng-template[neuTableGroupFooter]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTableGroupHeaderDirective

Selector: `ng-template[neuTableGroupHeader]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTableGroupingChange

```typescript
export interface NeuTableGroupingChange<F extends string> {
    readonly next: NeuTableGroupingState<F>;
    readonly source: "toggle" | "programmatic";
}
```

## NeuTableGroupingOptions

```typescript
export interface NeuTableGroupingOptions<T, F extends string> {
    readonly mode: "subheader" | "rowspan";
    readonly scope: "loaded";
    readonly value?: (row: T, field: F) => unknown;
    readonly aggregate?: (rows: readonly T[], field: F) => unknown;
}
```

## NeuTableGroupingState

```typescript
export interface NeuTableGroupingState<F extends string> {
    readonly by: readonly F[];
    readonly expandedGroupIds: readonly string[];
}
```

## NeuTableHeaderContext

```typescript
export interface NeuTableHeaderContext<T, F extends string> {
    readonly column: NeuTableColumn<T, F>;
    readonly sort: readonly NeuSortEntry<F>[];
}
```

## NeuTableHeaderDirective

Selector: `ng-template[neuTableHeader]`

| Input | Required | Type |
| --- | --- | --- |
| neuTableHeader | yes | `InputSignal<string>` |

| Output | Type |
| --- | --- |

## NeuTableHeaderSelectionState

```typescript
type NeuTableHeaderSelectionState = 'checked' | 'unchecked' | 'indeterminate';
```

## neuTableIdentityToken

```typescript
declare function neuTableIdentityToken(key: NeuTableKey): string;
```

## neuTableIndexForOffset

```typescript
declare function neuTableIndexForOffset(offset: number, itemSize: number): number;
```

## NeuTableInteractionOptions

```typescript
export interface NeuTableInteractionOptions {
    readonly navigation: "native" | "rows" | "cells";
    readonly wrapFocus: boolean;
    readonly announceChanges: boolean;
}
```

## NeuTableKey

```typescript
export type NeuTableKey = string | number;
```

## NeuTableLabels

```typescript
export interface NeuTableLabels {
    readonly ariaLabel: string;
    readonly empty: string;
    readonly loading: string;
    readonly error: string;
    readonly retry: string;
    readonly selection: string;
    readonly pagination: string;
    readonly messages?: Partial<Record<NeuTableMessage, string>>;
}
```

## NeuTableLayoutChange

```typescript
export interface NeuTableLayoutChange {
    readonly next: NeuTableLayoutState;
    readonly source: "resize" | "reorder" | "visibility" | "pin";
}
```

## NeuTableLayoutProjection

```typescript
interface NeuTableLayoutProjection<T, F extends string> {
    readonly columns: readonly NeuTableColumn<T, F>[];
    readonly hiddenColumns: readonly NeuTableColumn<T, F>[];
    readonly pinById: ReadonlyMap<string, NeuTableColumnPin>;
}
```

## NeuTableLayoutState

```typescript
export interface NeuTableLayoutState {
    readonly order: readonly string[];
    readonly hidden: readonly string[];
    readonly widths: Readonly<Record<string, string>>;
    readonly pinnedStart: readonly string[];
    readonly pinnedEnd: readonly string[];
}
```

## NeuTableLoadingDirective

Selector: `ng-template[neuTableLoading]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTableMessage

```typescript
export type NeuTableMessage = 'stateAnnouncement' | 'firstPage' | 'previousPage' | 'nextPage' | 'lastPage' | 'page' | 'of' | 'goToPage' | 'rowsPerPage' | 'searchTable' | 'search' | 'clearSearch' | 'clear' | 'advancedFilters' | 'hiddenColumns' | 'showColumn' | 'expansion' | 'selectAll' | 'filterColumn' | 'filter' | 'moveLeft' | 'moveRight' | 'pinColumn' | 'pin' | 'hideColumn' | 'hide' | 'resizeColumn' | 'rule' | 'value' | 'applyColumnFilter' | 'clearColumnFilter' | 'cancelFilter' | 'filterRule' | 'filterValue' | 'apply' | 'collapseRow' | 'expandRow' | 'selectRow' | 'sortAction' | 'ascending' | 'descending' | 'none' | 'field' | 'join' | 'and' | 'or' | 'applyAdvancedFilter' | 'cancelAdvancedFilter' | 'edit' | 'save' | 'cancel' | 'validating' | NeuFilterConstraint<string>['rule'];
```

## NeuTableMetadata

```typescript
export interface NeuTableMetadata {
    readonly totalItems: number | null;
    readonly loading: boolean;
    readonly error: unknown | null;
    readonly queryRevision: number;
    readonly appliedRequestId: number | null;
    readonly dataRange?: NeuTableRange;
}
```

## neuTableOffsetForIndex

```typescript
declare function neuTableOffsetForIndex(index: number, itemSize: number): number | null;
```

## NeuTablePage

```typescript
interface NeuTablePage<T> {
    readonly rows: readonly T[];
    readonly page: number;
    readonly pageSize: number;
    readonly pageCount: number;
    readonly start: number;
    readonly end: number;
}
```

## NeuTablePaginationOptions

```typescript
export interface NeuTablePaginationOptions {
    readonly enabled: boolean;
    readonly pageSizeOptions: readonly number[];
    readonly position: "top" | "bottom" | "both";
    readonly report: "none" | "summary" | "range";
    readonly showPageJump: boolean;
}
```

## NeuTablePaginatorContext

```typescript
export interface NeuTablePaginatorContext {
    readonly page: number;
    readonly pageSize: number;
    readonly humanPage: number;
    readonly pageCount: number | null;
    readonly total: number | null;
    readonly rangeStart: number;
    readonly rangeEnd: number;
    readonly canFirst: boolean;
    readonly canPrevious: boolean;
    readonly canNext: boolean;
    readonly canLast: boolean;
    readonly pageSizeOptions: readonly number[];
    readonly changePage: (page: number) => void;
    readonly changePageSize: (pageSize: number) => void;
}
```

## NeuTablePaginatorDirective

Selector: `ng-template[neuTablePaginator]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTableQuery

```typescript
export interface NeuTableQuery<F extends string> {
    readonly page: number;
    readonly pageSize: number;
    readonly search: string;
    readonly sort: readonly NeuSortEntry<F>[];
    readonly filters: NeuFilterExpression<F> | null;
}
```

## NeuTableQueryEquality

```typescript
type NeuTableQueryEquality<F extends string> = (left: NeuTableQuery<F>, right: NeuTableQuery<F>) => boolean;
```

## NeuTableRange

```typescript
export interface NeuTableRange {
    readonly start: number;
    readonly end: number;
}
```

## NeuTableRangeChange

```typescript
export interface NeuTableRangeChange {
    readonly visible: NeuTableRange;
    readonly render: NeuTableRange;
    readonly reason: "scroll" | "resize" | "programmatic" | "query";
}
```

## NeuTableRemoteCoordinatorInput

```typescript
interface NeuTableRemoteCoordinatorInput<F extends string> {
    readonly browserActive: boolean;
    readonly dataMode: NeuTableDataMode;
    readonly metadata: NeuTableMetadata;
    readonly query: NeuTableQuery<F>;
    readonly requiredRange?: NeuTableRange | null;
    readonly retryToken: number;
    readonly virtualizationEnabled?: boolean;
}
```

## NeuTableRemoteCoordinatorState

```typescript
interface NeuTableRemoteCoordinatorState<F extends string> {
    readonly browserActive: boolean;
    readonly dataMode: NeuTableDataMode;
    readonly destroyed: boolean;
    readonly latestRequestId: number | null;
    readonly latestRequestRange: NeuTableRange | null;
    readonly nextRequestId: number;
    readonly pendingRange: NeuTableRange | null;
    readonly query: NeuTableQuery<F> | null;
    readonly queryRevision: number;
    readonly remoteSessionHandled: boolean;
    readonly requiredRange: NeuTableRange | null;
    readonly retryToken: number;
    readonly suppressedRange: NeuTableRange | null;
}
```

## NeuTableRemoteCoordinatorTransition

```typescript
interface NeuTableRemoteCoordinatorTransition<F extends string> {
    readonly request: NeuTableDataRequest<F> | null;
    readonly state: NeuTableRemoteCoordinatorState<F>;
}
```

## NeuTableRemoteCorrelation

```typescript
type NeuTableRemoteCorrelation = 'current' | 'unresolved' | 'stale-query' | 'stale-request' | 'stale-range';
```

## NeuTableRenderRow

```typescript
interface NeuTableRenderRow<T, K extends NeuTableKey> {
    readonly row: T;
    readonly key: K;
    readonly index: number;
    readonly track: unknown;
    readonly pin: "start" | "end" | null;
}
```

## NeuTableRowAction

```typescript
export interface NeuTableRowAction<T, K extends NeuTableKey> {
    readonly row: T;
    readonly key: K;
    readonly index: number;
    readonly action: "activate" | "double-activate" | "context-menu";
}
```

## NeuTableRowContext

```typescript
export interface NeuTableRowContext<T, K extends NeuTableKey> {
    readonly $implicit: T;
    readonly row: T;
    readonly key: K;
    readonly index: number;
    readonly selected: boolean;
    readonly expanded: boolean;
    readonly disabled: boolean;
}
```

## NeuTableRowDetailDirective

Selector: `ng-template[neuTableRowDetail]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## neuTableRowMatchesSelectionScope

```typescript
declare function neuTableRowMatchesSelectionScope<T extends object, F extends string>(row: T, scope: NeuTableSelectionScope<F>, columns: readonly NeuTableColumn<T, F>[], filterOptions: NeuTableFilterOptions<T, F>): boolean;
```

## NeuTableRowMove

```typescript
export interface NeuTableRowMove<K extends NeuTableKey> {
    readonly key: K;
    readonly beforeKey: K | null;
    readonly fromIndex: number;
    readonly toIndex: number;
}
```

## NeuTableRowOptions

```typescript
export interface NeuTableRowOptions<T, K extends NeuTableKey> {
    readonly className?: (row: T) => string | readonly string[] | null;
    readonly isDisabled?: (row: T) => boolean;
    readonly pin?: (row: T, key: K) => "start" | "end" | null;
    readonly reorderable: boolean;
}
```

## NeuTableSelection

```typescript
export type NeuTableSelection<K extends NeuTableKey, F extends string> = {
    readonly kind: 'keys';
    readonly keys: readonly K[];
} | {
    readonly kind: 'all-matching';
    readonly scope: NeuTableSelectionScope<F>;
    readonly excludedKeys: readonly K[];
};
```

## NeuTableSelectionChange

```typescript
export interface NeuTableSelectionChange<T, K extends NeuTableKey, F extends string> {
    readonly next: NeuTableSelection<K, F>;
    readonly source: "row" | "radio" | "checkbox" | "keyboard" | "toggle-all";
    readonly addedKeys: readonly K[];
    readonly removedKeys: readonly K[];
    readonly loadedRows: readonly T[];
}
```

## NeuTableSelectionIntent

```typescript
interface NeuTableSelectionIntent<T, K extends NeuTableKey> {
    readonly row: T;
    readonly key: K;
    readonly source: NeuTableSelectionChange<T, K, string>["source"];
    readonly shiftKey: boolean;
    readonly platformModifier: boolean;
}
```

## NeuTableSelectionOptions

```typescript
export type NeuTableSelectionOptions<T> = {
    readonly mode: 'none';
} | {
    readonly mode: 'single';
    readonly indicator: 'none' | 'radio';
    readonly selectOnRowClick: boolean;
    readonly allowClear: boolean;
    readonly isRowDisabled?: (row: T) => boolean;
} | {
    readonly mode: 'multiple';
    readonly indicator: 'none' | 'checkbox';
    readonly selectOnRowClick: boolean;
    readonly modifier: 'replace' | 'platform' | 'toggle';
    readonly range: boolean;
    readonly toggleAllScope: 'rendered' | 'page' | 'loaded' | 'all-matching';
    readonly isRowDisabled?: (row: T) => boolean;
};
```

## NeuTableSelectionProjection

```typescript
interface NeuTableSelectionProjection<K extends NeuTableKey> {
    readonly selectedTokens: ReadonlySet<string>;
    readonly headerState: NeuTableHeaderSelectionState;
    readonly selectedCount: number;
    readonly selectableCount: number;
    readonly isSelected: (key: K) => boolean;
}
```

## NeuTableSelectionRow

```typescript
interface NeuTableSelectionRow<T, K extends NeuTableKey> {
    readonly row: T;
    readonly key: K;
}
```

## NeuTableSelectionScope

```typescript
export interface NeuTableSelectionScope<F extends string> {
    readonly search: string;
    readonly filters: NeuFilterExpression<F> | null;
    readonly globalFields: readonly F[];
}
```

## NeuTableSortColumn

```typescript
export interface NeuTableSortColumn<T, F extends string> {
    readonly field: F;
    readonly value?: NeuTableValueAccessor<T>;
    readonly compare?: (left: T, right: T) => number;
}
```

## NeuTableSortOptions

```typescript
export interface NeuTableSortOptions {
    readonly mode: "single" | "multiple";
    readonly removable: boolean;
    readonly defaultDirection: NeuSortDirection;
    readonly resetPageOnChange: boolean;
}
```

## NeuTableSourcePartition

```typescript
interface NeuTableSourcePartition<T> {
    readonly start: readonly T[];
    readonly normal: readonly T[];
    readonly end: readonly T[];
}
```

## NeuTableStateTemplateContext

```typescript
export interface NeuTableStateTemplateContext {
    readonly loading: boolean;
    readonly error: unknown | null;
    readonly retry: () => void;
}
```

## NeuTableSummaryDirective

Selector: `ng-template[neuTableSummary]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTableToolbarDirective

Selector: `ng-template[neuTableToolbar]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTableValueAccessor

```typescript
export type NeuTableValueAccessor<T> = (row: T) => unknown;
```

## NeuTableViewportGeometry

```typescript
interface NeuTableViewportGeometry {
    readonly measured: boolean;
    readonly scrollTop: number;
    readonly viewportSize: number;
}
```

## NeuTableVirtualizationOptions

```typescript
export type NeuTableVirtualizationOptions = {
    readonly enabled: false;
} | {
    readonly enabled: true;
    readonly itemSize: number;
    readonly overscan: number;
    readonly requestStep?: number;
};
```

## NeuTableVirtualProjection

```typescript
interface NeuTableVirtualProjection {
    readonly itemSize: number;
    readonly measured: boolean;
    readonly render: NeuTableRange;
    readonly request: NeuTableRange;
    readonly step: number;
    readonly visible: NeuTableRange;
}
```

## normalizeNeuTableColumns

```typescript
declare function normalizeNeuTableColumns<T, F extends string>(columns: readonly NeuTableColumn<T, F>[], diagnoseDuplicates: boolean): readonly NeuTableColumn<T, F>[];
```

## normalizeNeuTableItemSize

```typescript
declare function normalizeNeuTableItemSize(value: number): number;
```

## normalizeNeuTableLogicalCount

```typescript
declare function normalizeNeuTableLogicalCount(value: number | null): number | null;
```

## normalizeNeuTableOverscan

```typescript
declare function normalizeNeuTableOverscan(value: number): number;
```

## normalizeNeuTableQuery

```typescript
declare function normalizeNeuTableQuery<F extends string>(query: NeuTableQuery<F>, sortOptions: NeuTableSortOptions): NeuTableEffectiveQuery<F>;
```

## normalizeNeuTableRange

```typescript
declare function normalizeNeuTableRange(range: NeuTableRange): NeuTableRange;
```

## normalizeNeuTableResize

```typescript
declare function normalizeNeuTableResize<T, F extends string>(column: NeuTableColumn<T, F>, width: number): string | null;
```

## normalizeNeuTableText

```typescript
declare function normalizeNeuTableText(value: string): string;
```

## paginateNeuTableRows

```typescript
declare function paginateNeuTableRows<T>(rows: readonly T[], page: number, pageSize: number, enabled: boolean): NeuTablePage<T>;
```

## partitionNeuTableSource

```typescript
declare function partitionNeuTableSource<T, K extends NeuTableKey>(data: readonly T[], rowKey: (row: T) => K, pin: NeuTableRowOptions<T, K>['pin'], diagnoseDuplicateKeys: boolean): NeuTableSourcePartition<T>;
```

## projectNeuTableLayout

```typescript
declare function projectNeuTableLayout<T, F extends string>(columns: readonly NeuTableColumn<T, F>[], layout: NeuTableLayoutState): NeuTableLayoutProjection<T, F>;
```

## projectNeuTableRows

```typescript
declare function projectNeuTableRows<T, K extends NeuTableKey>(data: readonly T[], rowKey: NeuRowKey<T, K>, rowTrackBy: NeuRowTrackBy<T> | undefined, pin: ((row: T, key: K) => 'start' | 'end' | null) | undefined, diagnoseDuplicateKeys: boolean): readonly NeuTableRenderRow<T, K>[];
```

## projectNeuTableSelection

```typescript
declare function projectNeuTableSelection<T extends object, K extends NeuTableKey, F extends string>(options: {
    readonly selection: NeuTableSelection<K, F>;
    readonly selectionOptions: NeuTableSelectionOptions<T>;
    readonly rowOptions: NeuTableRowOptions<T, K>;
    readonly rows: readonly NeuTableSelectionRow<T, K>[];
    readonly headerRows: readonly NeuTableSelectionRow<T, K>[];
    readonly columns: readonly NeuTableColumn<T, F>[];
    readonly filterOptions: NeuTableFilterOptions<T, F>;
    readonly currentScope: NeuTableSelectionScope<F>;
}): NeuTableSelectionProjection<K>;
```

## projectNeuTableSpacerSizes

```typescript
declare function projectNeuTableSpacerSizes(options: {
    readonly itemSize: number;
    readonly mounted: NeuTableRange;
    readonly total: number | null;
}): {
    readonly before: number;
    readonly after: number;
};
```

## projectNeuTableVirtualWindow

```typescript
declare function projectNeuTableVirtualWindow(options: {
    readonly geometry: NeuTableViewportGeometry;
    readonly total: number | null;
    readonly virtualization: Extract<NeuTableVirtualizationOptions, {
        readonly enabled: true;
    }>;
}): NeuTableVirtualProjection;
```

## proposeNeuTableMove

```typescript
declare function proposeNeuTableMove<T, F extends string>(columns: readonly NeuTableColumn<T, F>[], layout: NeuTableLayoutState, columnId: string, delta: -1 | 1): NeuTableLayoutChange | null;
```

## proposeNeuTablePin

```typescript
declare function proposeNeuTablePin(layout: NeuTableLayoutState, columnId: string, pin: NeuTableColumnPin): NeuTableLayoutChange | null;
```

## proposeNeuTableReorder

```typescript
declare function proposeNeuTableReorder<T, F extends string>(columns: readonly NeuTableColumn<T, F>[], layout: NeuTableLayoutState, columnId: string, targetId: string): NeuTableLayoutChange | null;
```

## proposeNeuTableResize

```typescript
declare function proposeNeuTableResize<T, F extends string>(layout: NeuTableLayoutState, column: NeuTableColumn<T, F>, width: number): NeuTableLayoutChange | null;
```

## proposeNeuTableRowSelection

```typescript
declare function proposeNeuTableRowSelection<T extends object, K extends NeuTableKey, F extends string>(options: {
    readonly selection: NeuTableSelection<K, F>;
    readonly selectionOptions: NeuTableSelectionOptions<T>;
    readonly rowOptions: NeuTableRowOptions<T, K>;
    readonly intent: NeuTableSelectionIntent<T, K>;
    readonly rangeRows: readonly NeuTableSelectionRow<T, K>[];
    readonly loadedRows: readonly NeuTableSelectionRow<T, K>[];
    readonly anchor: K | null;
    readonly columns: readonly NeuTableColumn<T, F>[];
    readonly filterOptions: NeuTableFilterOptions<T, F>;
}): {
    readonly change: NeuTableSelectionChange<T, K, F> | null;
    readonly anchor: K | null;
};
```

## proposeNeuTableToggleAll

```typescript
declare function proposeNeuTableToggleAll<T extends object, K extends NeuTableKey, F extends string>(options: {
    readonly selection: NeuTableSelection<K, F>;
    readonly selectionOptions: NeuTableSelectionOptions<T>;
    readonly rowOptions: NeuTableRowOptions<T, K>;
    readonly rows: readonly NeuTableSelectionRow<T, K>[];
    readonly loadedRows: readonly NeuTableSelectionRow<T, K>[];
    readonly currentScope: NeuTableSelectionScope<F>;
    readonly columns: readonly NeuTableColumn<T, F>[];
    readonly filterOptions: NeuTableFilterOptions<T, F>;
}): NeuTableSelectionChange<T, K, F> | null;
```

## proposeNeuTableVisibility

```typescript
declare function proposeNeuTableVisibility(layout: NeuTableLayoutState, columnId: string, visible: boolean): NeuTableLayoutChange | null;
```

## readNeuTableEditValue

```typescript
declare function readNeuTableEditValue<T extends object, F extends string>(row: T, column: NeuTableColumn<T, F>): unknown;
```

## reconcileNeuTableEditSource

```typescript
declare function reconcileNeuTableEditSource<T extends object, K extends NeuTableKey, F extends string>(session: NeuTableEditSession<T, K, F>, row: T, columns: readonly NeuTableColumn<T, F>[], equals?: (left: unknown, right: unknown) => boolean): NeuTableEditReconciliation;
```

## runNeuTableClientPipeline

```typescript
declare function runNeuTableClientPipeline<T extends object, K extends NeuTableKey, F extends string>(options: {
    readonly data: readonly T[];
    readonly dataMode: NeuTableDataMode;
    readonly columns: readonly NeuTableColumn<T, F>[];
    readonly query: NeuTableQuery<F>;
    readonly rowKey: (row: T) => K;
    readonly rowOptions: NeuTableRowOptions<T, K>;
    readonly sortOptions: NeuTableSortOptions;
    readonly filterOptions: NeuTableFilterOptions<T, F>;
    readonly paginationOptions: NeuTablePaginationOptions;
    readonly diagnoseDuplicateKeys?: boolean;
}): NeuTableClientPipelineResult<T, F>;
```

## searchNeuTableRows

```typescript
declare function searchNeuTableRows<T, F extends string>(rows: readonly T[], search: string, fields: readonly F[], resolver: NeuTableFieldResolver<T, F>): readonly T[];
```

## selectionRowsFromData

```typescript
declare function selectionRowsFromData<T, K extends NeuTableKey>(rows: readonly T[], rowKey: NeuRowKey<T, K>): readonly NeuTableSelectionRow<T, K>[];
```

## setNeuTableEditDraftValue

```typescript
declare function setNeuTableEditDraftValue<T extends object, K extends NeuTableKey, F extends string>(session: NeuTableEditSession<T, K, F>, columnId: string, value: unknown): boolean;
```

## sortNeuTableRows

```typescript
declare function sortNeuTableRows<T, F extends string>(rows: readonly T[], sort: readonly NeuSortEntry<F>[], resolver: NeuTableFieldResolver<T, F>): readonly T[];
```

## transitionNeuTableRemoteCoordinator

```typescript
declare function transitionNeuTableRemoteCoordinator<F extends string>(previous: NeuTableRemoteCoordinatorState<F>, input: NeuTableRemoteCoordinatorInput<F>, queriesEqual: NeuTableQueryEquality<F>): NeuTableRemoteCoordinatorTransition<F>;
```

