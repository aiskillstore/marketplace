---
name: "Angular 20 Standalone Component"
description: "Create Angular 20 standalone components using modern patterns: Signals for state management, input()/output() functions (not decorators), @if/@for/@switch control flow (not *ngIf/*ngFor), inject() dependency injection (not constructor), and OnPush change detection. Use this skill when scaffolding new UI components that need reactive state, form handling, or integration with services following the three-layer architecture."
license: "MIT"
---

# Angular 20 Standalone Component Skill

This skill helps create Angular 20 components following modern patterns and project standards.

## Core Principles

### Modern Angular 20 Patterns
- **Standalone Components**: 100% standalone, zero NgModules
- **Signals**: Use `signal()`, `computed()`, `effect()` for state
- **New Syntax**: `input()`, `output()`, `@if`, `@for`, `@switch`
- **inject()**: Function-based dependency injection
- **OnPush**: Change detection strategy for performance

### Architecture Integration
- **Presentation Layer**: Components handle UI only
- **Service Integration**: Inject services for business logic
- **No Direct Repository**: Never inject repositories directly
- **Event-Driven**: Use EventBus for cross-module communication

## Component Template

```typescript
import { Component, signal, computed, effect, input, output, inject, ChangeDetectionStrategy } from '@angular/core';
import { SHARED_IMPORTS } from '@shared';
import { YourService } from '@core/services/your.service';

@Component({
  selector: 'app-your-component',
  standalone: true,
  imports: [SHARED_IMPORTS],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="component-container">
      @if (loading()) {
        <nz-spin nzSimple />
      } @else if (hasError()) {
        <nz-alert 
          nzType="error" 
          [nzMessage]="errorMessage()!"
          nzShowIcon
        />
      } @else {
        <div class="content">
          @for (item of items(); track item.id) {
            <app-item-card 
              [item]="item"
              (itemChange)="handleItemChange($event)"
            />
          } @empty {
            <nz-empty nzNotFoundContent="No items found" />
          }
        </div>
      }
    </div>
  `,
  styles: [`
    .component-container {
      padding: 24px;
    }
    
    .content {
      display: grid;
      gap: 16px;
    }
  `]
})
export class YourComponent {
  // ✅ Inject services with inject()
  private yourService = inject(YourService);
  
  // ✅ Use input() for properties (NOT @Input())
  blueprintId = input.required<string>();
  readonly = input(false);
  
  // ✅ Use output() for events (NOT @Output())
  itemChange = output<Item>();
  
  // ✅ Use signal() for mutable state
  loading = signal(false);
  error = signal<string | null>(null);
  items = signal<Item[]>([]);
  
  // ✅ Use computed() for derived state
  hasError = computed(() => this.error() !== null);
  errorMessage = computed(() => this.error());
  totalItems = computed(() => this.items().length);
  
  // ✅ Use effect() for side effects
  constructor() {
    effect(() => {
      const id = this.blueprintId();
      console.log('Blueprint ID changed:', id);
      this.loadItems(id);
    });
  }
  
  ngOnInit(): void {
    this.loadItems(this.blueprintId());
  }
  
  async loadItems(blueprintId: string): Promise<void> {
    this.loading.set(true);
    this.error.set(null);
    
    try {
      const items = await this.yourService.getItems(blueprintId);
      this.items.set(items);
    } catch (err) {
      this.error.set(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      this.loading.set(false);
    }
  }
  
  handleItemChange(item: Item): void {
    // Update local state
    this.items.update(items => 
      items.map(i => i.id === item.id ? item : i)
    );
    
    // Emit to parent
    this.itemChange.emit(item);
  }
}
```

## Key Patterns

### 1. Signal State Management

```typescript
// Writable signals
private _items = signal<Item[]>([]);

// Read-only public access
items = this._items.asReadonly();

// Computed derived state
filteredItems = computed(() => 
  this._items().filter(item => item.status === 'active')
);

// Update signals
this._items.set([...]); // Replace
this._items.update(items => [...items, newItem]); // Transform
```

### 2. Control Flow Syntax

```typescript
// ✅ CORRECT: New @if syntax
@if (condition()) {
  <div>Content</div>
} @else if (otherCondition()) {
  <div>Other</div>
} @else {
  <div>Default</div>
}

// ✅ CORRECT: New @for syntax with track
@for (item of items(); track item.id) {
  <div>{{ item.name }}</div>
} @empty {
  <p>No items</p>
}

// ✅ CORRECT: New @switch syntax
@switch (status()) {
  @case ('active') { <span class="badge-success">Active</span> }
  @case ('inactive') { <span class="badge-danger">Inactive</span> }
  @default { <span class="badge-default">Unknown</span> }
}

// ❌ WRONG: Old syntax (forbidden)
<div *ngIf="condition">...</div>
<div *ngFor="let item of items">...</div>
<div [ngSwitch]="status">...</div>
```

### 3. Input/Output Functions

```typescript
// ✅ CORRECT: Use input()/output() functions
task = input.required<Task>();
readonly = input(false);
taskChange = output<Task>();

// ❌ WRONG: Decorators (forbidden)
@Input() task!: Task;
@Output() taskChange = new EventEmitter<Task>();
```

### 4. Dependency Injection

```typescript
// ✅ CORRECT: Use inject()
private taskService = inject(TaskService);
private router = inject(Router);
private destroyRef = inject(DestroyRef);

// ❌ WRONG: Constructor injection (forbidden)
constructor(
  private taskService: TaskService,
  private router: Router
) {}
```

### 5. Subscriptions

```typescript
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

// ✅ CORRECT: Auto-cleanup with takeUntilDestroyed
private destroyRef = inject(DestroyRef);

ngOnInit(): void {
  this.service.data$
    .pipe(takeUntilDestroyed(this.destroyRef))
    .subscribe(data => this.items.set(data));
}

// ❌ WRONG: Manual subscriptions without cleanup
ngOnInit(): void {
  this.service.data$.subscribe(data => this.items.set(data));
}
```

## Component Types

### Smart Component (Container)

```typescript
@Component({
  selector: 'app-task-list',
  standalone: true,
  imports: [SHARED_IMPORTS, TaskItemComponent],
  template: `
    @for (task of tasks(); track task.id) {
      <app-task-item 
        [task]="task"
        (taskChange)="updateTask($event)"
      />
    }
  `
})
export class TaskListComponent {
  private taskService = inject(TaskService);
  tasks = signal<Task[]>([]);
  
  ngOnInit(): void {
    this.loadTasks();
  }
  
  async loadTasks(): Promise<void> {
    const tasks = await this.taskService.getTasks();
    this.tasks.set(tasks);
  }
  
  async updateTask(task: Task): Promise<void> {
    await this.taskService.updateTask(task.id, task);
    this.tasks.update(tasks => 
      tasks.map(t => t.id === task.id ? task : t)
    );
  }
}
```

### Presentational Component (Pure)

```typescript
@Component({
  selector: 'app-task-item',
  standalone: true,
  imports: [SHARED_IMPORTS],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <nz-card>
      <h3>{{ task().title }}</h3>
      <p>{{ task().description }}</p>
      <button nz-button (click)="handleComplete()">
        Complete
      </button>
    </nz-card>
  `
})
export class TaskItemComponent {
  task = input.required<Task>();
  taskChange = output<Task>();
  
  handleComplete(): void {
    const updated = { ...this.task(), status: 'completed' };
    this.taskChange.emit(updated);
  }
}
```

## Form Handling

```typescript
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-task-form',
  standalone: true,
  imports: [SHARED_IMPORTS, ReactiveFormsModule],
  template: `
    <form nz-form [formGroup]="form" (ngSubmit)="handleSubmit()">
      <nz-form-item>
        <nz-form-label nzRequired>Title</nz-form-label>
        <nz-form-control nzErrorTip="Please enter task title">
          <input nz-input formControlName="title" />
        </nz-form-control>
      </nz-form-item>
      
      <button nz-button nzType="primary" [disabled]="!form.valid">
        Submit
      </button>
    </form>
  `
})
export class TaskFormComponent {
  private fb = inject(FormBuilder);
  
  form = this.fb.group({
    title: ['', [Validators.required, Validators.maxLength(200)]],
    description: [''],
    status: ['pending']
  });
  
  taskSubmit = output<Partial<Task>>();
  
  handleSubmit(): void {
    if (this.form.valid) {
      this.taskSubmit.emit(this.form.value);
      this.form.reset();
    }
  }
}
```

## Checklist

When creating a component:

- [ ] Standalone component with imports
- [ ] Uses signal() for state
- [ ] Uses computed() for derived state
- [ ] Uses input()/output() functions
- [ ] Uses @if/@for/@switch syntax
- [ ] Uses inject() for dependencies
- [ ] OnPush change detection
- [ ] No business logic in component
- [ ] Proper error handling
- [ ] Loading states
- [ ] Empty states
- [ ] TypeScript strict typing

## References

- [Angular Instructions](.github/instructions/angular.instructions.md)
- [Signals State Management](.github/instructions/ng-ng-events(GigHub)-signals-state.instructions.md)
- [Architecture Guide](.github/instructions/ng-ng-events(GigHub)-architecture.instructions.md)
