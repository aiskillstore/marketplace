---
name: "BlueprintEventBus Integration"
description: "Implement event-driven communication using BlueprintEventBus for cross-module coordination. Use this skill when modules need to communicate without tight coupling, broadcasting domain events (task.created, member.added), subscribing to events with proper lifecycle management, and implementing event-driven workflows. Ensures events follow naming conventions ([module].[action]), include Blueprint context, and use takeUntilDestroyed() for automatic cleanup."
license: "MIT"
---

# BlueprintEventBus Integration Skill

This skill helps implement event-driven architecture using BlueprintEventBus.

## Core Principles

### Event-Driven Architecture
- **Decoupling**: Modules communicate via events, not direct calls
- **Blueprint Context**: All events include Blueprint information
- **Type Safety**: Events are strongly typed with TypeScript
- **Lifecycle Management**: Automatic subscription cleanup

### When to Use EventBus

✅ **DO use EventBus for:**
- Cross-module communication
- Broadcasting state changes to multiple listeners
- Audit logging and activity tracking
- Notification triggers
- Workflow orchestration

❌ **DON'T use EventBus for:**
- Simple parent-child component communication (use @Output)
- Direct service-to-service calls within same module
- Synchronous data fetching
- Request-response patterns (use Services)

## Event Structure

### Base Event Interface

```typescript
interface BlueprintEvent<T = any> {
  type: string; // Format: [module].[action]
  blueprintId: string;
  timestamp: Date;
  actor: string; // User ID who triggered event
  data: T;
  metadata?: Record<string, any>;
}
```

### Event Naming Convention

```
[module].[action]
```

Examples:
- `task.created`
- `task.updated`
- `task.deleted`
- `task.assigned`
- `member.added`
- `member.removed`
- `file.uploaded`
- `blueprint.archived`

## Publishing Events

### Basic Event Publishing

```typescript
import { inject } from '@angular/core';
import { BlueprintEventBus } from '@core/services/blueprint-event-bus.service';

@Injectable({ providedIn: 'root' })
export class TaskService {
  private eventBus = inject(BlueprintEventBus);
  private taskRepository = inject(TaskRepository);
  
  async createTask(blueprintId: string, task: CreateTaskDto): Promise<Task> {
    // 1. Execute business logic
    const created = await this.taskRepository.create(blueprintId, task);
    
    // 2. Publish domain event
    this.eventBus.publish({
      type: 'task.created',
      blueprintId,
      timestamp: new Date(),
      actor: this.getCurrentUserId(),
      data: created
    });
    
    return created;
  }
  
  async updateTask(taskId: string, updates: Partial<Task>): Promise<Task> {
    const task = await this.taskRepository.findById(taskId);
    if (!task) throw new Error('Task not found');
    
    const updated = await this.taskRepository.update(taskId, updates);
    
    // Publish update event with before/after data
    this.eventBus.publish({
      type: 'task.updated',
      blueprintId: task.blueprintId,
      timestamp: new Date(),
      actor: this.getCurrentUserId(),
      data: updated,
      metadata: {
        before: task,
        changes: updates
      }
    });
    
    return updated;
  }
}
```

### Typed Event Publishing

```typescript
// Define event types
interface TaskCreatedEvent extends BlueprintEvent<Task> {
  type: 'task.created';
}

interface TaskAssignedEvent extends BlueprintEvent<{
  task: Task;
  assignee: string;
  assigneeType: 'user' | 'team' | 'partner';
}> {
  type: 'task.assigned';
}

// Publish with type safety
this.eventBus.publish<TaskCreatedEvent>({
  type: 'task.created',
  blueprintId: created.blueprintId,
  timestamp: new Date(),
  actor: this.getCurrentUserId(),
  data: created
});
```

## Subscribing to Events

### Basic Subscription

```typescript
import { Component, inject, signal, DestroyRef } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { BlueprintEventBus } from '@core/services/blueprint-event-bus.service';

@Component({
  selector: 'app-task-list',
  template: `...`
})
export class TaskListComponent {
  private eventBus = inject(BlueprintEventBus);
  private destroyRef = inject(DestroyRef);
  
  tasks = signal<Task[]>([]);
  
  ngOnInit(): void {
    // Subscribe to task.created events
    this.eventBus.subscribe('task.created')
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(event => {
        console.log('New task created:', event.data);
        this.tasks.update(tasks => [...tasks, event.data]);
      });
  }
}
```

### Filtered Subscription (Blueprint-specific)

```typescript
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-blueprint-tasks',
  template: `...`
})
export class BlueprintTasksComponent {
  private eventBus = inject(BlueprintEventBus);
  private destroyRef = inject(DestroyRef);
  
  blueprintId = input.required<string>();
  tasks = signal<Task[]>([]);
  
  ngOnInit(): void {
    // Only listen to events in current Blueprint
    this.eventBus.subscribe('task.created')
      .pipe(
        filter(event => event.blueprintId === this.blueprintId()),
        takeUntilDestroyed(this.destroyRef)
      )
      .subscribe(event => {
        this.tasks.update(tasks => [...tasks, event.data]);
      });
    
    // Listen to updates
    this.eventBus.subscribe('task.updated')
      .pipe(
        filter(event => event.blueprintId === this.blueprintId()),
        takeUntilDestroyed(this.destroyRef)
      )
      .subscribe(event => {
        this.tasks.update(tasks =>
          tasks.map(t => t.id === event.data.id ? event.data : t)
        );
      });
    
    // Listen to deletions
    this.eventBus.subscribe('task.deleted')
      .pipe(
        filter(event => event.blueprintId === this.blueprintId()),
        takeUntilDestroyed(this.destroyRef)
      )
      .subscribe(event => {
        this.tasks.update(tasks =>
          tasks.filter(t => t.id !== event.data.id)
        );
      });
  }
}
```

### Multiple Event Types

```typescript
import { merge } from 'rxjs';

ngOnInit(): void {
  // Listen to multiple event types
  merge(
    this.eventBus.subscribe('task.created'),
    this.eventBus.subscribe('task.updated'),
    this.eventBus.subscribe('task.deleted')
  )
    .pipe(
      filter(event => event.blueprintId === this.blueprintId()),
      takeUntilDestroyed(this.destroyRef)
    )
    .subscribe(event => {
      console.log('Task event:', event.type, event.data);
      this.refreshTasks();
    });
}
```

## Common Use Cases

### 1. Audit Logging

```typescript
@Injectable({ providedIn: 'root' })
export class AuditLogService {
  private eventBus = inject(BlueprintEventBus);
  private auditLogRepository = inject(AuditLogRepository);
  
  constructor() {
    // Listen to ALL events for audit trail
    this.eventBus.subscribeAll()
      .pipe(takeUntilDestroyed())
      .subscribe(event => {
        this.logEvent(event);
      });
  }
  
  private async logEvent(event: BlueprintEvent): Promise<void> {
    await this.auditLogRepository.create({
      eventType: event.type,
      blueprintId: event.blueprintId,
      actor: event.actor,
      timestamp: event.timestamp,
      data: event.data,
      metadata: event.metadata
    });
  }
}
```

### 2. Notification System

```typescript
@Injectable({ providedIn: 'root' })
export class NotificationService {
  private eventBus = inject(BlueprintEventBus);
  private notificationRepository = inject(NotificationRepository);
  
  constructor() {
    // Listen to events that trigger notifications
    this.setupNotificationListeners();
  }
  
  private setupNotificationListeners(): void {
    // Task assigned → notify assignee
    this.eventBus.subscribe('task.assigned')
      .pipe(takeUntilDestroyed())
      .subscribe(async event => {
        await this.notifyUser(event.data.assignee, {
          title: 'New Task Assigned',
          message: `You have been assigned: ${event.data.task.title}`,
          blueprintId: event.blueprintId
        });
      });
    
    // Member added → notify member
    this.eventBus.subscribe('member.added')
      .pipe(takeUntilDestroyed())
      .subscribe(async event => {
        await this.notifyUser(event.data.userId, {
          title: 'Added to Blueprint',
          message: `You have been added to ${event.data.blueprintName}`,
          blueprintId: event.blueprintId
        });
      });
  }
}
```

### 3. Real-time UI Updates

```typescript
@Component({
  selector: 'app-activity-feed',
  template: `
    <div class="activity-feed">
      @for (activity of activities(); track activity.id) {
        <div class="activity-item">
          <span class="timestamp">{{ activity.timestamp | date }}</span>
          <span class="message">{{ activity.message }}</span>
        </div>
      }
    </div>
  `
})
export class ActivityFeedComponent {
  private eventBus = inject(BlueprintEventBus);
  private destroyRef = inject(DestroyRef);
  
  blueprintId = input.required<string>();
  activities = signal<Activity[]>([]);
  
  ngOnInit(): void {
    // Listen to all events in Blueprint
    this.eventBus.subscribeAll()
      .pipe(
        filter(event => event.blueprintId === this.blueprintId()),
        takeUntilDestroyed(this.destroyRef)
      )
      .subscribe(event => {
        this.addActivity({
          id: crypto.randomUUID(),
          type: event.type,
          message: this.formatEventMessage(event),
          timestamp: event.timestamp
        });
      });
  }
  
  private formatEventMessage(event: BlueprintEvent): string {
    switch (event.type) {
      case 'task.created':
        return `Task "${event.data.title}" was created`;
      case 'task.assigned':
        return `Task assigned to ${event.data.assignee}`;
      case 'member.added':
        return `${event.data.userName} joined the Blueprint`;
      default:
        return `Event: ${event.type}`;
    }
  }
  
  private addActivity(activity: Activity): void {
    this.activities.update(activities => [activity, ...activities].slice(0, 50));
  }
}
```

### 4. Workflow Orchestration

```typescript
@Injectable({ providedIn: 'root' })
export class TaskWorkflowService {
  private eventBus = inject(BlueprintEventBus);
  private taskRepository = inject(TaskRepository);
  private notificationService = inject(NotificationService);
  
  constructor() {
    this.setupWorkflows();
  }
  
  private setupWorkflows(): void {
    // When task is completed → trigger follow-up actions
    this.eventBus.subscribe('task.completed')
      .pipe(takeUntilDestroyed())
      .subscribe(async event => {
        const task = event.data;
        
        // 1. Check if task has dependencies
        const dependentTasks = await this.taskRepository
          .findDependentTasks(task.id);
        
        // 2. Update dependent tasks
        for (const depTask of dependentTasks) {
          await this.taskRepository.update(depTask.id, {
            status: 'ready'
          });
        }
        
        // 3. Notify stakeholders
        await this.notificationService.notifyTaskCompletion(task);
      });
  }
}
```

## Event Bus Service Implementation

Reference implementation:

```typescript
import { Injectable } from '@angular/core';
import { Subject, Observable } from 'rxjs';
import { filter } from 'rxjs/operators';

export interface BlueprintEvent<T = any> {
  type: string;
  blueprintId: string;
  timestamp: Date;
  actor: string;
  data: T;
  metadata?: Record<string, any>;
}

@Injectable({ providedIn: 'root' })
export class BlueprintEventBus {
  private eventStream = new Subject<BlueprintEvent>();
  
  /**
   * Publish event to all subscribers
   */
  publish<T = any>(event: BlueprintEvent<T>): void {
    this.eventStream.next(event);
  }
  
  /**
   * Subscribe to specific event type
   */
  subscribe<T = any>(eventType: string): Observable<BlueprintEvent<T>> {
    return this.eventStream.asObservable().pipe(
      filter(event => event.type === eventType)
    );
  }
  
  /**
   * Subscribe to all events
   */
  subscribeAll(): Observable<BlueprintEvent> {
    return this.eventStream.asObservable();
  }
  
  /**
   * Subscribe to events in specific Blueprint
   */
  subscribeToBlueprintEvents(blueprintId: string): Observable<BlueprintEvent> {
    return this.eventStream.asObservable().pipe(
      filter(event => event.blueprintId === blueprintId)
    );
  }
}
```

## Testing EventBus Integration

```typescript
describe('EventBus Integration', () => {
  let eventBus: BlueprintEventBus;
  let taskService: TaskService;
  
  beforeEach(() => {
    eventBus = TestBed.inject(BlueprintEventBus);
    taskService = TestBed.inject(TaskService);
  });
  
  it('should publish event when task is created', (done) => {
    // Subscribe to event
    eventBus.subscribe('task.created').subscribe(event => {
      expect(event.type).toBe('task.created');
      expect(event.data.title).toBe('Test Task');
      done();
    });
    
    // Create task (triggers event)
    taskService.createTask('blueprint1', { title: 'Test Task' });
  });
  
  it('should filter events by Blueprint', (done) => {
    let receivedEvents = 0;
    
    eventBus.subscribeAll()
      .pipe(filter(event => event.blueprintId === 'blueprint1'))
      .subscribe(() => {
        receivedEvents++;
      });
    
    // Publish events to different Blueprints
    eventBus.publish({
      type: 'task.created',
      blueprintId: 'blueprint1',
      timestamp: new Date(),
      actor: 'user1',
      data: {}
    });
    
    eventBus.publish({
      type: 'task.created',
      blueprintId: 'blueprint2',
      timestamp: new Date(),
      actor: 'user1',
      data: {}
    });
    
    setTimeout(() => {
      expect(receivedEvents).toBe(1);
      done();
    }, 100);
  });
});
```

## Checklist

When integrating EventBus:

- [ ] Events follow naming convention ([module].[action])
- [ ] Events include blueprintId
- [ ] Events include timestamp and actor
- [ ] Subscriptions use takeUntilDestroyed()
- [ ] Filter events by Blueprint when needed
- [ ] Use typed events for type safety
- [ ] Publish events AFTER successful operations
- [ ] Don't use EventBus for request-response
- [ ] Test event publishing and subscription
- [ ] Document event types and data structures

## References

- [Architecture Guide](.github/instructions/ng-ng-events(GigHub)-architecture.instructions.md)
- [Blueprint Integration](./blueprint-integration/SKILL.md)
- [Global Event Bus Documentation](docs/⭐️/Global Event Bus.md)
