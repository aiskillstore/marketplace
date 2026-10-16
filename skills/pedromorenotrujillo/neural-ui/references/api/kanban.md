# @neural-ui/core/kanban

Verified against @neural-ui/core@2.0.1. Generated; do not edit.

Types below are package contracts, not complete application examples. Referenced Angular/internal declaration types do not authorize imports from internal entrypoints.

## diagnoseKanbanBoard

```typescript
declare function diagnoseKanbanBoard(columns: readonly NeuKanbanColumn[]): NeuKanbanBoardDiagnostic | null;
```

## findKanbanCard

```typescript
declare function findKanbanCard(columns: readonly NeuKanbanColumn[], cardId: string): NeuKanbanCardPosition | null;
```

## NeuKanbanAssignee

```typescript
export interface NeuKanbanAssignee {
    readonly name: string;
    readonly avatar?: string;
    readonly initials?: string;
}
```

## NeuKanbanBoardDiagnostic

```typescript
interface NeuKanbanBoardDiagnostic {
    readonly code: "duplicate-column-id" | "duplicate-card-id";
    readonly id: string;
}
```

## NeuKanbanCard

```typescript
export interface NeuKanbanCard {
    readonly id: string;
    readonly title: string;
    readonly description?: string;
    readonly tags?: readonly string[];
    readonly assignee?: NeuKanbanAssignee;
    readonly dueDate?: string;
    readonly meta?: string;
    readonly priority?: "low" | "medium" | "high" | "urgent";
    readonly disabled?: boolean;
}
```

## NeuKanbanCardMove

```typescript
export type NeuKanbanCardMove = NeuKanbanCardReorder | NeuKanbanCardTransfer;
```

## NeuKanbanCardPosition

```typescript
interface NeuKanbanCardPosition {
    readonly column: NeuKanbanColumn;
    readonly columnIndex: number;
    readonly cardIndex: number;
}
```

## NeuKanbanCardReorder

```typescript
export interface NeuKanbanCardReorder {
    readonly kind: "reorder";
    readonly cardId: string;
    readonly columnId: string;
    readonly fromIndex: number;
    readonly toIndex: number;
}
```

## NeuKanbanCardTransfer

```typescript
export interface NeuKanbanCardTransfer {
    readonly kind: "transfer";
    readonly cardId: string;
    readonly fromColumnId: string;
    readonly toColumnId: string;
    readonly fromIndex: number;
    readonly toIndex: number;
}
```

## NeuKanbanColumn

```typescript
export interface NeuKanbanColumn {
    readonly id: string;
    readonly title: string;
    readonly cards: readonly NeuKanbanCard[];
    readonly color?: string;
    readonly wipLimit?: number;
}
```

## NeuKanbanComponent

Selector: `neu-kanban`

| Input | Required | Type |
| --- | --- | --- |
| columns | no | `import("@angular/core").InputSignal<readonly NeuKanbanColumn[]>` |
| columnWidth | no | `import("@angular/core").InputSignal<string>` |
| showCounts | no | `import("@angular/core").InputSignal<boolean>` |
| showWipLimit | no | `import("@angular/core").InputSignal<boolean>` |
| moveButtonLabel | no | `import("@angular/core").InputSignal<string>` |

| Output | Type |
| --- | --- |
| cardMove | `import("@angular/core").OutputEmitterRef<NeuKanbanCardMove>` |

## NeuKanbanKeyboardMove

```typescript
interface NeuKanbanKeyboardMove {
    readonly cardId: string;
    readonly cardTitle: string;
    readonly fromColumnId: string;
    readonly previousIndex: number;
    readonly toColumnId: string;
    readonly currentIndex: number;
}
```

## NeuKanbanLocaleLabels

```typescript
interface NeuKanbanLocaleLabels {
    readonly instructions: string;
    readonly empty: string;
    readonly move: string;
    readonly cardPosition: (card: string, column: string, position: number, total: number) => string;
    readonly moveGroup: (card: string) => string;
    readonly moveDirection: (card: string, direction: NeuKanbanMoveDirection) => string;
    readonly moveCancelled: (card: string) => string;
    readonly moveRequested: (card: string, column: string, position: number) => string;
    readonly selected: (card: string, column: string, position: number) => string;
}
```

## NeuKanbanMoveDirection

```typescript
type NeuKanbanMoveDirection = 'up' | 'down' | 'left' | 'right';
```

## proposeKanbanCardMove

```typescript
declare function proposeKanbanCardMove(columns: readonly NeuKanbanColumn[], cardId: string, fromColumnId: string, toColumnId: string, toIndex: number): NeuKanbanCardMove | null;
```

