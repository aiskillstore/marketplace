---
name: "RxJS Patterns for Angular"
description: "Implement RxJS patterns for reactive programming in Angular. Use this skill when working with Observables, operators, subscriptions, async data flows, and error handling. Covers common patterns like combineLatest, switchMap, debounceTime, catchError, retry logic, and integration with Angular Signals using toSignal() and toObservable(). Ensures proper subscription cleanup with takeUntilDestroyed()."
license: "MIT"
---

# RxJS Patterns for Angular Skill

This skill helps implement reactive patterns using RxJS in Angular applications.

## Core Principles

### Modern Angular + RxJS
- **Signals First**: Use Signals for state, RxJS for async operations
- **Auto Cleanup**: Use `takeUntilDestroyed()` for subscription management
- **Interop**: Use `toSignal()` and `toObservable()` for Signal/Observable conversion
- **AsyncPipe**: Prefer AsyncPipe in templates when not using Signals

### Key Concepts
- Observables for async data streams
- Operators for data transformation
- Subscription management and cleanup
- Error handling and retry logic

## Signal + RxJS Integration

### toSignal() - Observable to Signal

```typescript
import { Component, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-task-list',
  template: `
    @if (tasks(); as taskList) {
      @for (task of taskList; track task.id) {
        <div>{{ task.title }}</div>
      }
    }
  `
})
export class TaskListComponent {
  private http = inject(HttpClient);
  
  // Convert Observable to Signal
  tasks = toSignal(
    this.http.get<Task[]>('/api/tasks'),
    { initialValue: [] }
  );
}
```

### toObservable() - Signal to Observable

```typescript
import { Component, signal } from '@angular/core';
import { toObservable } from '@angular/core/rxjs-interop';
import { switchMap } from 'rxjs/operators';

@Component({
  selector: 'app-search',
  template: `
    <input 
      nz-input 
      [ngModel]="searchQuery()" 
      (ngModelChange)="searchQuery.set($event)" 
    />
    
    @if (results(); as resultList) {
      @for (result of resultList; track result.id) {
        <div>{{ result.name }}</div>
      }
    }
  `
})
export class SearchComponent {
  searchQuery = signal('');
  
  // Convert Signal to Observable and transform
  private searchQuery$ = toObservable(this.searchQuery);
  
  results = toSignal(
    this.searchQuery$.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      switchMap(query => this.searchService.search(query))
    ),
    { initialValue: [] }
  );
}
```

## Subscription Management

### takeUntilDestroyed() - Auto Cleanup

```typescript
import { Component, inject, signal, DestroyRef } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { interval } from 'rxjs';

@Component({
  selector: 'app-timer',
  template: `<div>Time: {{ time() }}</div>`
})
export class TimerComponent {
  private destroyRef = inject(DestroyRef);
  time = signal(0);
  
  constructor() {
    // Subscription automatically cleaned up on component destroy
    interval(1000)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(value => this.time.set(value));
  }
}
```

### Manual Cleanup (Legacy Pattern - Avoid)

```typescript
// ❌ DON'T: Manual subscription management (old pattern)
export class LegacyComponent implements OnDestroy {
  private subscription = new Subscription();
  
  ngOnInit() {
    this.subscription.add(
      this.dataService.getData().subscribe(data => {
        // handle data
      })
    );
  }
  
  ngOnDestroy() {
    this.subscription.unsubscribe();
  }
}

// ✅ DO: Use takeUntilDestroyed()
export class ModernComponent {
  private destroyRef = inject(DestroyRef);
  data = signal<any>(null);
  
  constructor() {
    this.dataService.getData()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(data => this.data.set(data));
  }
}
```

## Common Operators

### switchMap - Switch to New Observable

```typescript
// Switch to new search on every query change
searchResults$ = this.searchQuery$.pipe(
  debounceTime(300),
  switchMap(query => this.http.get(`/api/search?q=${query}`))
);
```

### mergeMap - Merge Multiple Observables

```typescript
// Process all tasks in parallel
processTasks$ = this.tasks$.pipe(
  mergeMap(tasks => 
    from(tasks).pipe(
      mergeMap(task => this.processTask(task))
    )
  )
);
```

### concatMap - Process Sequentially

```typescript
// Process tasks one by one in order
processTasks$ = this.tasks$.pipe(
  concatMap(tasks =>
    from(tasks).pipe(
      concatMap(task => this.processTask(task))
    )
  )
);
```

### debounceTime - Debounce Input

```typescript
// Wait 300ms after user stops typing
search$ = this.searchInput$.pipe(
  debounceTime(300),
  distinctUntilChanged(),
  switchMap(query => this.searchService.search(query))
);
```

### distinctUntilChanged - Skip Duplicates

```typescript
// Only emit when value actually changes
status$ = this.statusSubject$.pipe(
  distinctUntilChanged()
);
```

### filter - Filter Values

```typescript
// Only emit non-empty strings
nonEmptySearch$ = this.searchQuery$.pipe(
  filter(query => query.trim().length > 0),
  switchMap(query => this.search(query))
);
```

### map - Transform Values

```typescript
// Transform task to display format
taskDisplay$ = this.task$.pipe(
  map(task => ({
    title: task.title,
    status: task.status.toUpperCase(),
    dueDate: formatDate(task.dueDate)
  }))
);
```

### tap - Side Effects

```typescript
// Log without transforming
tasks$ = this.http.get<Task[]>('/api/tasks').pipe(
  tap(tasks => console.log('Loaded tasks:', tasks.length)),
  tap(tasks => this.analyticsService.track('tasks_loaded'))
);
```

## Combining Observables

### combineLatest - Wait for All

```typescript
import { combineLatest } from 'rxjs';

// Combine multiple observables
viewModel$ = combineLatest([
  this.tasks$,
  this.users$,
  this.settings$
]).pipe(
  map(([tasks, users, settings]) => ({
    tasks,
    users,
    settings
  }))
);

// Convert to Signal
viewModel = toSignal(this.viewModel$);
```

### forkJoin - Wait for All to Complete

```typescript
import { forkJoin } from 'rxjs';

// Load multiple resources in parallel
loadAll$ = forkJoin({
  tasks: this.taskService.getTasks(),
  users: this.userService.getUsers(),
  projects: this.projectService.getProjects()
}).pipe(
  map(({ tasks, users, projects }) => ({
    tasks,
    users,
    projects
  }))
);
```

### merge - Merge Multiple Streams

```typescript
import { merge } from 'rxjs';

// Combine multiple event streams
allEvents$ = merge(
  this.createEvent$,
  this.updateEvent$,
  this.deleteEvent$
).pipe(
  tap(event => this.handleEvent(event))
);
```

### zip - Pair Up Values

```typescript
import { zip } from 'rxjs';

// Pair up matching values from two streams
paired$ = zip(
  this.stream1$,
  this.stream2$
).pipe(
  map(([value1, value2]) => ({ value1, value2 }))
);
```

## Error Handling

### catchError - Handle Errors

```typescript
tasks$ = this.http.get<Task[]>('/api/tasks').pipe(
  catchError(error => {
    console.error('Failed to load tasks:', error);
    this.notificationService.error('Failed to load tasks');
    return of([]); // Return empty array as fallback
  })
);
```

### retry - Retry on Failure

```typescript
tasks$ = this.http.get<Task[]>('/api/tasks').pipe(
  retry(3), // Retry up to 3 times
  catchError(error => {
    console.error('Failed after 3 retries:', error);
    return of([]);
  })
);
```

### retryWhen - Conditional Retry with Backoff

```typescript
import { retryWhen, delay, scan, throwError } from 'rxjs';

tasks$ = this.http.get<Task[]>('/api/tasks').pipe(
  retryWhen(errors =>
    errors.pipe(
      scan((retryCount, error) => {
        if (retryCount >= 3) {
          throw error; // Max retries reached
        }
        console.log(`Retry ${retryCount + 1}/3`);
        return retryCount + 1;
      }, 0),
      delay(1000) // Wait 1 second between retries
    )
  ),
  catchError(error => {
    console.error('Failed after retries:', error);
    return of([]);
  })
);
```

## Real-Time Data

### interval - Periodic Updates

```typescript
import { interval, switchMap } from 'rxjs';

// Poll every 30 seconds
liveData$ = interval(30000).pipe(
  startWith(0), // Emit immediately
  switchMap(() => this.http.get('/api/live-data')),
  takeUntilDestroyed(this.destroyRef)
);

liveData = toSignal(this.liveData$);
```

### WebSocket Pattern

```typescript
import { webSocket } from 'rxjs/webSocket';

export class RealtimeService {
  private socket$ = webSocket('wss://api.example.com/ws');
  
  messages$ = this.socket$.pipe(
    catchError(error => {
      console.error('WebSocket error:', error);
      return EMPTY;
    }),
    retry({ delay: 5000 }) // Reconnect after 5 seconds
  );
  
  sendMessage(msg: any): void {
    this.socket$.next(msg);
  }
}
```

## Loading States

### Share Loading State

```typescript
import { shareReplay } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class TaskService {
  private http = inject(HttpClient);
  
  // Cache and share the result
  tasks$ = this.http.get<Task[]>('/api/tasks').pipe(
    shareReplay({ bufferSize: 1, refCount: true })
  );
}
```

### Loading Indicator Pattern

```typescript
@Component({
  selector: 'app-task-list',
  template: `
    @if (loading()) {
      <nz-spin />
    } @else if (error()) {
      <nz-alert nzType="error" [nzMessage]="error()!" />
    } @else {
      @for (task of tasks(); track task.id) {
        <div>{{ task.title }}</div>
      }
    }
  `
})
export class TaskListComponent {
  private taskService = inject(TaskService);
  private destroyRef = inject(DestroyRef);
  
  loading = signal(false);
  error = signal<string | null>(null);
  tasks = signal<Task[]>([]);
  
  constructor() {
    this.loadTasks();
  }
  
  loadTasks(): void {
    this.loading.set(true);
    this.error.set(null);
    
    this.taskService.tasks$
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (tasks) => {
          this.tasks.set(tasks);
          this.loading.set(false);
        },
        error: (err) => {
          this.error.set(err.message || 'Failed to load tasks');
          this.loading.set(false);
        }
      });
  }
}
```

## Advanced Patterns

### Throttle vs Debounce

```typescript
import { throttleTime, debounceTime } from 'rxjs';

// Throttle: Emit first, then ignore for duration
throttled$ = this.clicks$.pipe(
  throttleTime(1000) // Max once per second
);

// Debounce: Wait for quiet period
debounced$ = this.input$.pipe(
  debounceTime(300) // Wait 300ms after last input
);
```

### Scan - Accumulate Values

```typescript
// Running total
total$ = this.amounts$.pipe(
  scan((acc, value) => acc + value, 0)
);

// History accumulation
history$ = this.events$.pipe(
  scan((history, event) => [...history, event], [] as Event[])
);
```

### startWith - Initial Value

```typescript
// Start with loading state
status$ = this.dataLoad$.pipe(
  map(() => 'loaded'),
  startWith('loading')
);
```

### pairwise - Previous + Current

```typescript
// Compare with previous value
changes$ = this.value$.pipe(
  pairwise(),
  map(([prev, curr]) => ({
    previous: prev,
    current: curr,
    diff: curr - prev
  }))
);
```

## Best Practices

### ✅ DO

```typescript
// Use toSignal() for reactive data in templates
data = toSignal(this.data$, { initialValue: [] });

// Use takeUntilDestroyed() for cleanup
this.data$.pipe(takeUntilDestroyed(this.destroyRef)).subscribe();

// Use switchMap for user-triggered requests
search$ = this.query$.pipe(switchMap(q => this.search(q)));

// Handle errors explicitly
data$ = this.http.get('/api/data').pipe(
  catchError(err => of(null))
);
```

### ❌ DON'T

```typescript
// Don't forget to unsubscribe
this.data$.subscribe(); // Memory leak!

// Don't use nested subscribes
this.data$.subscribe(data => {
  this.process(data).subscribe(); // Anti-pattern!
});

// Don't use async pipe with signals
@if (data$ | async) { } // Use signals instead
```

## Checklist

When using RxJS:

- [ ] Use toSignal() to convert Observables to Signals
- [ ] Use takeUntilDestroyed() for subscription cleanup
- [ ] Handle errors with catchError()
- [ ] Debounce user input (300ms)
- [ ] Use switchMap for cancellable requests
- [ ] Share expensive Observables with shareReplay()
- [ ] Provide initial values with startWith()
- [ ] Filter out empty/null values
- [ ] Test async operations
- [ ] Document complex operator chains

## References

- [RxJS Documentation](https://rxjs.dev/)
- [Angular Signals + RxJS Interop](https://angular.dev/guide/signals/rxjs-interop)
- [RxJS Operators](https://rxjs.dev/guide/operators)
- [Learn RxJS](https://www.learnrxjs.io/)
