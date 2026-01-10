---
name: "ng-alain Component Development"
description: "Create components using ng-alain (@delon/abc) and ng-zorro-antd UI libraries. Use this skill when building enterprise UI features with ST (Simple Table), SF (Schema Form), ACL (Access Control), PageHeader, ReuseTab, and other @delon components. Ensures proper integration with ng-alain architecture, theming system, responsive layouts, and accessibility standards while following Angular 20 patterns."
license: "MIT"
---

# ng-alain Component Development Skill

This skill helps create enterprise UI components using ng-alain and ng-zorro-antd.

## Core Libraries

### @delon Packages
- **@delon/abc**: Business components (ST, SV, SEModule, etc.)
- **@delon/form**: Dynamic schema-based forms (SF)
- **@delon/auth**: Authentication and authorization
- **@delon/acl**: Access Control List
- **@delon/theme**: Theming and layout system
- **@delon/util**: Utility functions

### ng-zorro-antd
- Complete Ant Design component library
- Icons, layouts, forms, tables, modals, etc.

## Common Patterns

### 1. ST (Simple Table) Component

```typescript
import { Component, signal, inject } from '@angular/core';
import { STColumn, STData, STComponent } from '@delon/abc/st';
import { SHARED_IMPORTS } from '@shared';

@Component({
  selector: 'app-task-table',
  standalone: true,
  imports: [SHARED_IMPORTS, STComponent],
  template: `
    <st 
      [data]="tasks()" 
      [columns]="columns"
      [loading]="loading()"
      [page]="{ show: true, showSize: true }"
      (change)="handleChange($event)"
    />
  `
})
export class TaskTableComponent {
  private taskService = inject(TaskService);
  
  loading = signal(false);
  tasks = signal<STData[]>([]);
  
  columns: STColumn[] = [
    { 
      title: 'ID', 
      index: 'id', 
      width: 80,
      fixed: 'left'
    },
    { 
      title: 'Title', 
      index: 'title',
      width: 200
    },
    { 
      title: 'Status', 
      index: 'status', 
      type: 'badge',
      badge: {
        pending: { text: 'Pending', color: 'processing' },
        'in-progress': { text: 'In Progress', color: 'warning' },
        completed: { text: 'Completed', color: 'success' }
      }
    },
    {
      title: 'Assignee',
      index: 'assigneeName',
      width: 150
    },
    {
      title: 'Due Date',
      index: 'dueDate',
      type: 'date',
      dateFormat: 'yyyy-MM-dd'
    },
    {
      title: 'Actions',
      buttons: [
        {
          text: 'Edit',
          icon: 'edit',
          click: (record: any) => this.edit(record)
        },
        {
          text: 'Delete',
          icon: 'delete',
          type: 'del',
          pop: {
            title: 'Confirm delete?',
            okType: 'danger'
          },
          click: (record: any) => this.delete(record)
        }
      ]
    }
  ];
  
  ngOnInit(): void {
    this.loadTasks();
  }
  
  async loadTasks(): Promise<void> {
    this.loading.set(true);
    try {
      const tasks = await this.taskService.getTasks();
      this.tasks.set(tasks);
    } finally {
      this.loading.set(false);
    }
  }
  
  handleChange(event: any): void {
    console.log('Table change:', event);
  }
  
  edit(record: any): void {
    console.log('Edit:', record);
  }
  
  delete(record: any): void {
    console.log('Delete:', record);
  }
}
```

### 2. SF (Schema Form) Component

```typescript
import { Component, signal, inject, output } from '@angular/core';
import { SFSchema, SFComponent } from '@delon/form';
import { SHARED_IMPORTS } from '@shared';

@Component({
  selector: 'app-task-form',
  standalone: true,
  imports: [SHARED_IMPORTS, SFComponent],
  template: `
    <sf 
      [schema]="schema" 
      [loading]="loading()"
      (formSubmit)="handleSubmit($event)"
      (formChange)="handleChange($event)"
    />
  `
})
export class TaskFormComponent {
  loading = signal(false);
  taskSubmit = output<any>();
  
  schema: SFSchema = {
    properties: {
      title: {
        type: 'string',
        title: 'Task Title',
        maxLength: 200,
        ui: {
          placeholder: 'Enter task title',
          grid: { span: 24 }
        }
      },
      description: {
        type: 'string',
        title: 'Description',
        ui: {
          widget: 'textarea',
          autosize: { minRows: 3, maxRows: 6 },
          grid: { span: 24 }
        }
      },
      status: {
        type: 'string',
        title: 'Status',
        enum: [
          { label: 'Pending', value: 'pending' },
          { label: 'In Progress', value: 'in-progress' },
          { label: 'Completed', value: 'completed' }
        ],
        default: 'pending',
        ui: {
          widget: 'select',
          grid: { span: 12 }
        }
      },
      priority: {
        type: 'string',
        title: 'Priority',
        enum: [
          { label: 'Low', value: 'low' },
          { label: 'Medium', value: 'medium' },
          { label: 'High', value: 'high' }
        ],
        default: 'medium',
        ui: {
          widget: 'radio',
          grid: { span: 12 }
        }
      },
      assignee: {
        type: 'string',
        title: 'Assignee',
        ui: {
          widget: 'select',
          asyncData: () => this.loadUsers(),
          grid: { span: 12 }
        }
      },
      dueDate: {
        type: 'string',
        title: 'Due Date',
        format: 'date',
        ui: {
          widget: 'date',
          grid: { span: 12 }
        }
      },
      tags: {
        type: 'array',
        title: 'Tags',
        items: {
          type: 'string'
        },
        ui: {
          widget: 'select',
          mode: 'tags',
          grid: { span: 24 }
        }
      }
    },
    required: ['title', 'assignee'],
    ui: {
      grid: { gutter: 16 }
    }
  };
  
  handleSubmit(value: any): void {
    console.log('Form submitted:', value);
    this.taskSubmit.emit(value);
  }
  
  handleChange(value: any): void {
    console.log('Form changed:', value);
  }
  
  private async loadUsers(): Promise<any[]> {
    // Load users for assignee dropdown
    return [
      { label: 'User 1', value: 'user1' },
      { label: 'User 2', value: 'user2' }
    ];
  }
}
```

### 3. Page Header with Actions

```typescript
import { Component } from '@angular/core';
import { PageHeaderComponent } from '@delon/abc/page-header';
import { SHARED_IMPORTS } from '@shared';

@Component({
  selector: 'app-task-page',
  standalone: true,
  imports: [SHARED_IMPORTS, PageHeaderComponent],
  template: `
    <page-header 
      [title]="'Task Management'"
      [subtitle]="'Manage tasks for ' + blueprintName()"
      [breadcrumb]="breadcrumb"
    >
      <ng-template #extra>
        <button nz-button nzType="primary" (click)="createTask()">
          <i nz-icon nzType="plus"></i>
          New Task
        </button>
        <button nz-button (click)="refresh()">
          <i nz-icon nzType="reload"></i>
          Refresh
        </button>
      </ng-template>
    </page-header>
    
    <nz-card>
      <app-task-table />
    </nz-card>
  `
})
export class TaskPageComponent {
  blueprintName = signal('My Blueprint');
  
  breadcrumb = [
    { title: 'Home', link: '/' },
    { title: 'Blueprints', link: '/blueprints' },
    { title: 'Tasks' }
  ];
  
  createTask(): void {
    console.log('Create new task');
  }
  
  refresh(): void {
    console.log('Refresh tasks');
  }
}
```

### 4. ACL (Access Control)

```typescript
import { Component, inject } from '@angular/core';
import { ACLService } from '@delon/acl';
import { SHARED_IMPORTS } from '@shared';

@Component({
  selector: 'app-task-actions',
  standalone: true,
  imports: [SHARED_IMPORTS],
  template: `
    <nz-space>
      <!-- Show button only if user has permission -->
      <button 
        *nzSpaceItem
        *aclIf="'task:create'"
        nz-button 
        nzType="primary"
        (click)="create()"
      >
        Create Task
      </button>
      
      <button 
        *nzSpaceItem
        *aclIf="'task:delete'"
        nz-button 
        nzDanger
        (click)="delete()"
      >
        Delete
      </button>
      
      <!-- Check permission in code -->
      @if (canEdit()) {
        <button 
          *nzSpaceItem
          nz-button 
          (click)="edit()"
        >
          Edit
        </button>
      }
    </nz-space>
  `
})
export class TaskActionsComponent {
  private aclService = inject(ACLService);
  
  canEdit = signal(false);
  
  ngOnInit(): void {
    // Check permission programmatically
    this.canEdit.set(this.aclService.can('task:edit'));
  }
  
  create(): void {
    console.log('Create task');
  }
  
  edit(): void {
    console.log('Edit task');
  }
  
  delete(): void {
    console.log('Delete task');
  }
}
```

### 5. Responsive Layout

```typescript
import { Component } from '@angular/core';
import { SHARED_IMPORTS } from '@shared';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [SHARED_IMPORTS],
  template: `
    <div nz-row [nzGutter]="[16, 16]">
      <!-- Responsive columns -->
      <div nz-col [nzXs]="24" [nzSm]="12" [nzMd]="8" [nzLg]="6">
        <nz-card nzTitle="Total Tasks">
          <nz-statistic 
            [nzValue]="totalTasks()" 
            [nzPrefix]="prefixTpl"
          />
          <ng-template #prefixTpl>
            <i nz-icon nzType="check-circle"></i>
          </ng-template>
        </nz-card>
      </div>
      
      <div nz-col [nzXs]="24" [nzSm]="12" [nzMd]="8" [nzLg]="6">
        <nz-card nzTitle="Completed">
          <nz-statistic 
            [nzValue]="completedTasks()" 
            [nzValueStyle]="{ color: '#52c41a' }"
          />
        </nz-card>
      </div>
      
      <div nz-col [nzXs]="24" [nzSm]="12" [nzMd]="8" [nzLg]="6">
        <nz-card nzTitle="In Progress">
          <nz-statistic 
            [nzValue]="inProgressTasks()" 
            [nzValueStyle]="{ color: '#faad14' }"
          />
        </nz-card>
      </div>
      
      <div nz-col [nzXs]="24" [nzSm]="12" [nzMd]="8" [nzLg]="6">
        <nz-card nzTitle="Pending">
          <nz-statistic [nzValue]="pendingTasks()" />
        </nz-card>
      </div>
    </div>
  `
})
export class DashboardComponent {
  totalTasks = signal(100);
  completedTasks = signal(60);
  inProgressTasks = signal(25);
  pendingTasks = signal(15);
}
```

### 6. Modal and Drawer

```typescript
import { Component, inject } from '@angular/core';
import { NzModalService } from 'ng-zorro-antd/modal';
import { NzDrawerService } from 'ng-zorro-antd/drawer';
import { SHARED_IMPORTS } from '@shared';
import { TaskFormComponent } from './task-form.component';

@Component({
  selector: 'app-task-manager',
  standalone: true,
  imports: [SHARED_IMPORTS],
  template: `
    <button nz-button nzType="primary" (click)="openModal()">
      Open Modal
    </button>
    <button nz-button (click)="openDrawer()">
      Open Drawer
    </button>
  `
})
export class TaskManagerComponent {
  private modal = inject(NzModalService);
  private drawer = inject(NzDrawerService);
  
  openModal(): void {
    const modalRef = this.modal.create({
      nzTitle: 'Create Task',
      nzContent: TaskFormComponent,
      nzWidth: 720,
      nzFooter: null
    });
    
    // Listen to form submission
    modalRef.componentInstance!.taskSubmit.subscribe((task: any) => {
      console.log('Task submitted:', task);
      modalRef.close();
    });
  }
  
  openDrawer(): void {
    const drawerRef = this.drawer.create({
      nzTitle: 'Task Details',
      nzContent: TaskFormComponent,
      nzWidth: 640,
      nzClosable: true
    });
    
    drawerRef.afterClose.subscribe(() => {
      console.log('Drawer closed');
    });
  }
}
```

## ng-alain Theming

### Using Theme Variables

```scss
// Use ng-alain theme variables
@import '@delon/theme/system/index';

.task-card {
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  padding: var(--padding-lg);
  
  .title {
    color: var(--text-color);
    font-size: var(--font-size-lg);
  }
}
```

### Dark Mode Support

```typescript
import { Component, inject } from '@angular/core';
import { SettingsService } from '@delon/theme';

@Component({
  selector: 'app-theme-toggle',
  template: `
    <button nz-button (click)="toggleTheme()">
      <i nz-icon [nzType]="isDark() ? 'sun' : 'moon'"></i>
      {{ isDark() ? 'Light' : 'Dark' }} Mode
    </button>
  `
})
export class ThemeToggleComponent {
  private settings = inject(SettingsService);
  
  isDark = signal(false);
  
  ngOnInit(): void {
    this.isDark.set(this.settings.layout.theme === 'dark');
  }
  
  toggleTheme(): void {
    const newTheme = this.isDark() ? 'light' : 'dark';
    this.settings.setLayout('theme', newTheme);
    this.isDark.set(newTheme === 'dark');
  }
}
```

## Best Practices

### 1. Use SHARED_IMPORTS

```typescript
// Define in shared module
export const SHARED_IMPORTS = [
  CommonModule,
  ReactiveFormsModule,
  // ng-zorro-antd
  NzButtonModule,
  NzCardModule,
  NzFormModule,
  NzInputModule,
  // @delon
  STComponent,
  SFComponent,
  PageHeaderComponent
];
```

### 2. Responsive Design

```typescript
// Use ng-zorro responsive utilities
<div nz-row [nzGutter]="16">
  <div nz-col 
    [nzXs]="24"  // Mobile: full width
    [nzSm]="12"  // Tablet: half width
    [nzMd]="8"   // Desktop: one third
    [nzLg]="6"   // Large: one quarter
  >
    Content
  </div>
</div>
```

### 3. Accessibility

```html
<!-- Use proper ARIA attributes -->
<button 
  nz-button 
  aria-label="Create new task"
  [attr.aria-disabled]="loading()"
>
  Create
</button>

<!-- Proper form labels -->
<nz-form-item>
  <nz-form-label nzFor="title" nzRequired>
    Task Title
  </nz-form-label>
  <nz-form-control>
    <input nz-input id="title" name="title" />
  </nz-form-control>
</nz-form-item>
```

## Checklist

When creating ng-alain components:

- [ ] Use standalone components
- [ ] Import SHARED_IMPORTS
- [ ] Use STComponent for data tables
- [ ] Use SFComponent for complex forms
- [ ] Implement responsive layout
- [ ] Add ACL permissions where needed
- [ ] Use PageHeader for page titles
- [ ] Implement proper loading states
- [ ] Add error handling
- [ ] Follow ng-alain theming system
- [ ] Support dark mode
- [ ] Ensure accessibility (ARIA)
- [ ] Test on mobile devices

## References

- [ng-alain Documentation](https://ng-alain.com)
- [ng-zorro-antd Documentation](https://ng.ant.design)
- [@delon/abc Components](https://ng-alain.com/components)
- [ng-alain Instructions](.github/instructions/ng-alain-delon.instructions.md)
- [Angular Component Skill](./angular-component/SKILL.md)
