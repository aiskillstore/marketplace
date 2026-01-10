---
name: Angular CDK Integration
description: Create components using Angular CDK utilities including drag-drop, overlay, portal, scrolling, a11y, clipboard, and platform detection for ng-events project
license: MIT
---

# Angular CDK Integration Skill

This skill guides the creation of components and features using Angular CDK (@angular/cdk) utilities in the ng-events construction site management system.

## When to Use This Skill

**Triggers**: "Angular CDK", "drag and drop", "overlay", "portal", "virtual scroll", "accessibility", "clipboard", "platform detection", "CDK utilities"

Use this skill when:
- Implementing drag-and-drop functionality
- Creating overlays, tooltips, or popovers
- Building virtual scrolling lists
- Managing focus and accessibility
- Detecting platform/browser capabilities
- Working with clipboard operations
- Managing scrolling behavior

## Core CDK Modules

### 1. Drag and Drop (@angular/cdk/drag-drop)

**Purpose**: Create draggable elements and drop zones

```typescript
import { Component } from '@angular/core';
import { CdkDragDrop, moveItemInArray, transferArrayItem } from '@angular/cdk/drag-drop';
import { CommonModule } from '@angular/common';
import { CdkDropList, CdkDrag } from '@angular/cdk/drag-drop';

@Component({
  selector: 'app-task-board',
  standalone: true,
  imports: [CommonModule, CdkDropList, CdkDrag],
  template: `
    <div class="task-board">
      <div class="column" cdkDropList #todoList="cdkDropList"
           [cdkDropListData]="todo"
           [cdkDropListConnectedTo]="[inProgressList, doneList]"
           (cdkDropListDropped)="drop($event)">
        <h3>To Do</h3>
        @for (task of todo; track task.id) {
          <div cdkDrag class="task-card">
            {{ task.title }}
            <div *cdkDragPlaceholder class="drag-placeholder"></div>
          </div>
        }
      </div>
      
      <div class="column" cdkDropList #inProgressList="cdkDropList"
           [cdkDropListData]="inProgress"
           [cdkDropListConnectedTo]="[todoList, doneList]"
           (cdkDropListDropped)="drop($event)">
        <h3>In Progress</h3>
        @for (task of inProgress; track task.id) {
          <div cdkDrag class="task-card">{{ task.title }}</div>
        }
      </div>
      
      <div class="column" cdkDropList #doneList="cdkDropList"
           [cdkDropListData]="done"
           [cdkDropListConnectedTo]="[todoList, inProgressList]"
           (cdkDropListDropped)="drop($event)">
        <h3>Done</h3>
        @for (task of done; track task.id) {
          <div cdkDrag class="task-card">{{ task.title }}</div>
        }
      </div>
    </div>
  `,
  styles: [`
    .task-board {
      display: flex;
      gap: 20px;
    }
    
    .column {
      flex: 1;
      min-height: 400px;
      background: #f5f5f5;
      padding: 16px;
      border-radius: 4px;
    }
    
    .task-card {
      background: white;
      padding: 12px;
      margin-bottom: 8px;
      border-radius: 4px;
      cursor: move;
    }
    
    .task-card:active {
      box-shadow: 0 5px 5px -3px rgba(0,0,0,.2);
    }
    
    .drag-placeholder {
      background: #ccc;
      border: dotted 2px #999;
      height: 40px;
      transition: transform 250ms cubic-bezier(0, 0, 0.2, 1);
    }
  `]
})
export class TaskBoardComponent {
  todo = [
    { id: '1', title: 'Task 1' },
    { id: '2', title: 'Task 2' }
  ];
  
  inProgress = [
    { id: '3', title: 'Task 3' }
  ];
  
  done = [
    { id: '4', title: 'Task 4' }
  ];
  
  drop(event: CdkDragDrop<Task[]>) {
    if (event.previousContainer === event.container) {
      moveItemInArray(event.container.data, event.previousIndex, event.currentIndex);
    } else {
      transferArrayItem(
        event.previousContainer.data,
        event.container.data,
        event.previousIndex,
        event.currentIndex
      );
    }
  }
}
```

### 2. Overlay (@angular/cdk/overlay)

**Purpose**: Create floating panels and popups

```typescript
import { Component, inject } from '@angular/core';
import { Overlay, OverlayRef } from '@angular/cdk/overlay';
import { ComponentPortal } from '@angular/cdk/portal';

@Component({
  selector: 'app-menu-trigger',
  standalone: true,
  template: `
    <button (click)="openMenu()">Open Menu</button>
  `
})
export class MenuTriggerComponent {
  private overlay = inject(Overlay);
  private overlayRef: OverlayRef | null = null;
  
  openMenu(): void {
    if (this.overlayRef) {
      this.overlayRef.dispose();
      this.overlayRef = null;
      return;
    }
    
    const positionStrategy = this.overlay
      .position()
      .flexibleConnectedTo(this.elementRef)
      .withPositions([
        {
          originX: 'start',
          originY: 'bottom',
          overlayX: 'start',
          overlayY: 'top'
        }
      ]);
    
    this.overlayRef = this.overlay.create({
      positionStrategy,
      scrollStrategy: this.overlay.scrollStrategies.reposition(),
      hasBackdrop: true,
      backdropClass: 'cdk-overlay-transparent-backdrop'
    });
    
    const menuPortal = new ComponentPortal(MenuComponent);
    this.overlayRef.attach(menuPortal);
    
    // Close on backdrop click
    this.overlayRef.backdropClick().subscribe(() => {
      this.overlayRef?.dispose();
      this.overlayRef = null;
    });
  }
}
```

### 3. Virtual Scrolling (@angular/cdk/scrolling)

**Purpose**: Efficiently render large lists

```typescript
import { Component, signal } from '@angular/core';
import { ScrollingModule } from '@angular/cdk/scrolling';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-task-list-virtual',
  standalone: true,
  imports: [CommonModule, ScrollingModule],
  template: `
    <cdk-virtual-scroll-viewport itemSize="50" class="viewport">
      <div *cdkVirtualFor="let task of tasks()" class="task-item">
        <h4>{{ task.title }}</h4>
        <p>{{ task.description }}</p>
      </div>
    </cdk-virtual-scroll-viewport>
  `,
  styles: [`
    .viewport {
      height: 400px;
      width: 100%;
      border: 1px solid #ccc;
    }
    
    .task-item {
      height: 50px;
      padding: 10px;
      border-bottom: 1px solid #eee;
    }
  `]
})
export class TaskListVirtualComponent {
  tasks = signal(Array.from({ length: 10000 }, (_, i) => ({
    id: `task-${i}`,
    title: `Task ${i}`,
    description: `Description for task ${i}`
  })));
}
```

### 4. Clipboard (@angular/cdk/clipboard)

**Purpose**: Copy text to clipboard

```typescript
import { Component, inject } from '@angular/core';
import { Clipboard, ClipboardModule } from '@angular/cdk/clipboard';

@Component({
  selector: 'app-share-link',
  standalone: true,
  imports: [ClipboardModule],
  template: `
    <div class="share-container">
      <input [value]="shareLink" readonly #linkInput />
      <button 
        [cdkCopyToClipboard]="shareLink"
        (cdkCopyToClipboardCopied)="onCopied($event)">
        Copy Link
      </button>
      @if (copied) {
        <span class="success">Copied!</span>
      }
    </div>
  `
})
export class ShareLinkComponent {
  private clipboard = inject(Clipboard);
  shareLink = 'https://ng-events.com/blueprints/123';
  copied = false;
  
  onCopied(success: boolean): void {
    if (success) {
      this.copied = true;
      setTimeout(() => this.copied = false, 2000);
    }
  }
}
```

### 5. Platform Detection (@angular/cdk/platform)

**Purpose**: Detect browser and platform capabilities

```typescript
import { Component, inject, OnInit } from '@angular/core';
import { Platform } from '@angular/cdk/platform';

@Component({
  selector: 'app-platform-aware',
  standalone: true,
  template: `
    <div class="platform-info">
      <h3>Platform Information</h3>
      <ul>
        <li>Browser: {{ browser }}</li>
        <li>Mobile: {{ isMobile }}</li>
        <li>iOS: {{ isIOS }}</li>
        <li>Android: {{ isAndroid }}</li>
      </ul>
    </div>
  `
})
export class PlatformAwareComponent implements OnInit {
  private platform = inject(Platform);
  
  browser = '';
  isMobile = false;
  isIOS = false;
  isAndroid = false;
  
  ngOnInit(): void {
    this.isMobile = this.platform.IOS || this.platform.ANDROID;
    this.isIOS = this.platform.IOS;
    this.isAndroid = this.platform.ANDROID;
    
    if (this.platform.FIREFOX) this.browser = 'Firefox';
    else if (this.platform.EDGE) this.browser = 'Edge';
    else if (this.platform.SAFARI) this.browser = 'Safari';
    else if (this.platform.WEBKIT) this.browser = 'WebKit';
    else this.browser = 'Unknown';
  }
}
```

## Integration Checklist

When using Angular CDK:
- [ ] Import specific CDK modules (not full @angular/cdk)
- [ ] Use standalone components with CDK directives
- [ ] Implement proper cleanup (subscriptions, overlays)
- [ ] Test accessibility with screen readers
- [ ] Handle mobile/touch interactions
- [ ] Consider performance (virtual scrolling for lists >100 items)
- [ ] Integrate with Blueprint multi-tenancy when needed
- [ ] Follow three-layer architecture (CDK in UI layer only)

## Best Practices

### DO ✅
- Use CDK for complex UI interactions
- Leverage virtual scrolling for large datasets
- Use overlay service for tooltips/menus
- Detect platform for feature support
- Clean up overlays and portals on destroy

### DON'T ❌
- Use CDK in services or repositories (UI layer only)
- Create overlays without disposal logic
- Skip accessibility considerations
- Ignore mobile touch events

## References

- [Angular CDK Documentation](https://material.angular.io/cdk/categories)
- [Drag and Drop Guide](https://material.angular.io/cdk/drag-drop/overview)
- [Virtual Scrolling Guide](https://material.angular.io/cdk/scrolling/overview)

---

**Version**: 1.0.0  
**Compatible with**: @angular/cdk 20.x, Angular 20.3.x  
**Last Updated**: 2025-12-25
