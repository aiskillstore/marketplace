# @neural-ui/core/tree

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## buildTreeModel

```typescript
declare function buildTreeModel<T, K extends NeuTreeKey>(nodes: readonly NeuTreeNode<T, K>[], hierarchy: NeuTreeHierarchy<K>): TreeModel<T, K>;
```

## deriveTreeCheckboxStates

```typescript
declare function deriveTreeCheckboxStates<T, K extends NeuTreeKey>(model: TreeModel<T, K>, selection: NeuTreeSelection<K>): ReadonlyMap<unknown, TreeCheckboxState>;
```

## NeuTreeChildrenRelation

```typescript
export type NeuTreeChildrenRelation<K extends NeuTreeKey> = {
    readonly parentKey: K;
    readonly state: 'unloaded';
} | {
    readonly parentKey: K;
    readonly state: 'loading';
    readonly requestId: number;
} | {
    readonly parentKey: K;
    readonly state: 'loaded';
    readonly keys: readonly K[];
} | {
    readonly parentKey: K;
    readonly state: 'error';
    readonly requestId?: number;
};
```

## NeuTreeChildrenRequest

```typescript
export interface NeuTreeChildrenRequest<K extends NeuTreeKey> {
    readonly requestId: number;
    readonly hierarchyRevision: number;
    readonly parentKey: K;
    readonly reason: "expand" | "retry";
}
```

## NeuTreeComponent

Selector: `neu-tree`

| Input | Required | Type |
| --- | --- | --- |
| nodes | yes | `import("@angular/core").InputSignal<readonly NeuTreeNode<T, K>[]>` |
| hierarchy | yes | `import("@angular/core").InputSignal<NeuTreeHierarchy<K>>` |
| expandedKeys | no | `import("@angular/core").InputSignal<readonly K[]>` |
| selection | no | `import("@angular/core").InputSignal<NeuTreeSelection<K>>` |
| searchable | no | `import("@angular/core").InputSignal<boolean>` |
| virtualization | no | `import("@angular/core").InputSignal<NeuTreeVirtualization \| null>` |
| reorderable | no | `import("@angular/core").InputSignal<boolean>` |
| indentSize | no | `import("@angular/core").InputSignal<number>` |
| ariaLabel | no | `import("@angular/core").InputSignal<string>` |
| searchLabel | no | `import("@angular/core").InputSignal<string>` |
| emptyLabel | no | `import("@angular/core").InputSignal<string>` |
| invalidTreeLabel | no | `import("@angular/core").InputSignal<string>` |
| expandLabel | no | `import("@angular/core").InputSignal<string>` |
| collapseLabel | no | `import("@angular/core").InputSignal<string>` |
| retryLabel | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |
| expandedKeysChange | `import("@angular/core").OutputEmitterRef<NeuTreeExpandedKeysChange<K>>` |
| selectionChange | `import("@angular/core").OutputEmitterRef<NeuTreeSelectionChange<K>>` |
| childrenRequest | `import("@angular/core").OutputEmitterRef<NeuTreeChildrenRequest<K>>` |
| nodeAction | `import("@angular/core").OutputEmitterRef<NeuTreeNodeAction<K>>` |
| nodeMove | `import("@angular/core").OutputEmitterRef<NeuTreeNodeMove<K>>` |

## NeuTreeExpandedKeysChange

```typescript
export interface NeuTreeExpandedKeysChange<K extends NeuTreeKey> {
    readonly keys: readonly K[];
    readonly key: K;
    readonly expanded: boolean;
    readonly source: NeuTreeInteractionSource;
}
```

## NeuTreeHierarchy

```typescript
export interface NeuTreeHierarchy<K extends NeuTreeKey> {
    readonly revision: number;
    readonly roots: readonly K[];
    readonly children: readonly NeuTreeChildrenRelation<K>[];
}
```

## NeuTreeInteractionSource

```typescript
export type NeuTreeInteractionSource = 'pointer' | 'keyboard';
```

## NeuTreeKey

```typescript
export type NeuTreeKey = string | number;
```

## NeuTreeMovePosition

```typescript
export type NeuTreeMovePosition = 'before' | 'inside' | 'after';
```

## NeuTreeNode

```typescript
export interface NeuTreeNode<T, K extends NeuTreeKey = string> {
    readonly key: K;
    readonly data: T;
    readonly label: string;
    readonly description?: string;
    readonly badge?: string;
    readonly disabled?: boolean;
}
```

## NeuTreeNodeAction

```typescript
export interface NeuTreeNodeAction<K extends NeuTreeKey> {
    readonly key: K;
}
```

## NeuTreeNodeDirective

Selector: `ng-template[neuTreeNode]`

| Input | Required | Type |
| --- | --- | --- |

| Output | Type |
| --- | --- |

## NeuTreeNodeMove

```typescript
export interface NeuTreeNodeMove<K extends NeuTreeKey> {
    readonly sourceKey: K;
    readonly sourceParentKey: K | null;
    readonly sourceIndex: number;
    readonly targetKey: K;
    readonly targetParentKey: K | null;
    readonly targetIndex: number;
    readonly position: NeuTreeMovePosition;
}
```

## NeuTreeNodeTemplateContext

```typescript
export interface NeuTreeNodeTemplateContext<T, K extends NeuTreeKey = string> {
    readonly $implicit: T;
    readonly key: K;
    readonly level: number;
    readonly expanded: boolean;
    readonly selected: boolean;
    readonly partial: boolean;
    readonly disabled: boolean;
    readonly loading: boolean;
    readonly hasChildren: boolean;
}
```

## NeuTreeSelection

```typescript
export type NeuTreeSelection<K extends NeuTreeKey> = {
    readonly mode: 'none';
} | {
    readonly mode: 'single';
    readonly key: K | null;
} | {
    readonly mode: 'multiple';
    readonly keys: readonly K[];
} | {
    readonly mode: 'checkbox';
    readonly keys: readonly K[];
};
```

## NeuTreeSelectionChange

```typescript
export interface NeuTreeSelectionChange<K extends NeuTreeKey> {
    readonly selection: NeuTreeSelection<K>;
    readonly key: K;
    readonly source: NeuTreeInteractionSource;
}
```

## NeuTreeVirtualization

```typescript
export interface NeuTreeVirtualization {
    readonly itemSize: number;
    readonly viewportHeight: number;
    readonly buffer?: number;
}
```

## normalizeTreeSearch

```typescript
declare function normalizeTreeSearch(value: string): string;
```

## projectVisibleTree

```typescript
declare function projectVisibleTree<T, K extends NeuTreeKey>(model: TreeModel<T, K>, expandedKeys: readonly K[], query: string): readonly VisibleTreeEntry<T, K>[];
```

## proposeTreeExpansion

```typescript
declare function proposeTreeExpansion<K extends NeuTreeKey>(keys: readonly K[], key: K, source: NeuTreeInteractionSource): NeuTreeExpandedKeysChange<K>;
```

## proposeTreeMove

```typescript
declare function proposeTreeMove<T, K extends NeuTreeKey>(model: TreeModel<T, K>, sourceKey: K, targetKey: K, position: NeuTreeMovePosition): NeuTreeNodeMove<K> | null;
```

## proposeTreeSelection

```typescript
declare function proposeTreeSelection<T, K extends NeuTreeKey>(model: TreeModel<T, K>, selection: NeuTreeSelection<K>, key: K, source: NeuTreeInteractionSource): NeuTreeSelectionChange<K> | null;
```

## TreeCheckboxState

```typescript
type TreeCheckboxState = 'checked' | 'mixed' | 'unchecked';
```

## TreeDragData

```typescript
interface TreeDragData<K extends NeuTreeKey> {
    readonly owner: object;
    readonly key: K;
}
```

## TreeDropTarget

```typescript
interface TreeDropTarget<K extends NeuTreeKey> {
    readonly key: K;
    readonly position: NeuTreeMovePosition;
}
```

## TreeEntry

```typescript
interface TreeEntry<T, K extends NeuTreeKey> {
    readonly key: K;
    readonly node: NeuTreeNode<T, K>;
    readonly parentKey: K | null;
    readonly level: number;
    readonly index: number;
    readonly setSize: number;
    readonly relation: NeuTreeChildrenRelation<K> | undefined;
    readonly loadedChildren: readonly K[];
}
```

## TreeIssue

```typescript
interface TreeIssue<K extends NeuTreeKey> {
    readonly code: TreeIssueCode;
    readonly key: K;
}
```

## TreeIssueCode

```typescript
type TreeIssueCode = 'duplicate-key' | 'duplicate-root' | 'duplicate-relation' | 'duplicate-child' | 'duplicate-parentage' | 'missing-node' | 'missing-parent' | 'cycle' | 'orphan';
```

## TreeModel

```typescript
interface TreeModel<T, K extends NeuTreeKey> {
    readonly issue: TreeIssue<K> | null;
    readonly entries: readonly TreeEntry<T, K>[];
    readonly byKey: ReadonlyMap<unknown, TreeEntry<T, K>>;
    readonly roots: readonly K[];
    readonly revision: number;
}
```

## treeSelectedTokens

```typescript
declare function treeSelectedTokens<K extends NeuTreeKey>(selection: NeuTreeSelection<K>): Set<unknown>;
```

## treeToken

```typescript
declare function treeToken(key: NeuTreeKey): unknown;
```

## VisibleTreeEntry

```typescript
interface VisibleTreeEntry<T, K extends NeuTreeKey> extends TreeEntry<T, K> {
    readonly trackToken: unknown;
    readonly visibleIndex: number;
    readonly expanded: boolean;
    readonly hasChildren: boolean;
    readonly loading: boolean;
}
```

