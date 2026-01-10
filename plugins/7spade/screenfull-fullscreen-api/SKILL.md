---
name: Screenfull Fullscreen API
description: Implement fullscreen functionality using screenfull library for cross-browser fullscreen support in ng-events project
license: MIT
---

# Screenfull Fullscreen API Skill

This skill guides the implementation of fullscreen functionality using the screenfull library in the ng-events construction site management system.

## When to Use This Skill

**Triggers**: "fullscreen", "screenfull", "full screen mode", "toggle fullscreen", "exit fullscreen"

Use this skill when:
- Adding fullscreen toggle buttons
- Creating fullscreen viewers (images, videos, dashboards)
- Implementing presentation modes
- Building immersive UI experiences
- Providing fullscreen for specific components

## Installation & Setup

```bash
# Already installed in package.json
yarn add screenfull@^6.0.2
```

## Core Patterns

### 1. Basic Fullscreen Toggle

```typescript
import { Component, inject, signal } from '@angular/core';
import screenfull from 'screenfull';

@Component({
  selector: 'app-fullscreen-toggle',
  standalone: true,
  template: `
    <button (click)="toggleFullscreen()" class="fullscreen-btn">
      @if (isFullscreen()) {
        <i nz-icon nzType="fullscreen-exit" nzTheme="outline"></i>
        Exit Fullscreen
      } @else {
        <i nz-icon nzType="fullscreen" nzTheme="outline"></i>
        Enter Fullscreen
      }
    </button>
  `
})
export class FullscreenToggleComponent {
  isFullscreen = signal(false);
  
  toggleFullscreen(): void {
    if (screenfull.isEnabled) {
      screenfull.toggle();
      this.updateFullscreenState();
      
      // Listen for fullscreen changes
      screenfull.on('change', () => {
        this.updateFullscreenState();
      });
    } else {
      console.warn('Fullscreen API not supported');
    }
  }
  
  private updateFullscreenState(): void {
    this.isFullscreen.set(screenfull.isFullscreen);
  }
}
```

### 2. Fullscreen Specific Element

```typescript
import { Component, ElementRef, ViewChild, signal } from '@angular/core';
import screenfull from 'screenfull';

@Component({
  selector: 'app-dashboard-fullscreen',
  standalone: true,
  template: `
    <div #dashboardContainer class="dashboard-container">
      <div class="dashboard-header">
        <h2>Construction Progress Dashboard</h2>
        <button (click)="toggleFullscreen()" class="btn-fullscreen">
          @if (isFullscreen()) {
            <i nz-icon nzType="fullscreen-exit"></i>
          } @else {
            <i nz-icon nzType="fullscreen"></i>
          }
        </button>
      </div>
      
      <div class="dashboard-content">
        <app-progress-charts />
        <app-task-summary />
        <app-recent-activities />
      </div>
    </div>
  `,
  styles: [`
    .dashboard-container {
      position: relative;
      background: white;
      padding: 20px;
    }
    
    .dashboard-container:-webkit-full-screen {
      background: #1f1f1f;
      color: white;
    }
    
    .dashboard-container:fullscreen {
      background: #1f1f1f;
      color: white;
    }
    
    .btn-fullscreen {
      position: absolute;
      top: 20px;
      right: 20px;
    }
  `]
})
export class DashboardFullscreenComponent {
  @ViewChild('dashboardContainer', { static: true }) container!: ElementRef;
  isFullscreen = signal(false);
  
  toggleFullscreen(): void {
    if (screenfull.isEnabled) {
      screenfull.toggle(this.container.nativeElement);
      
      screenfull.on('change', () => {
        this.isFullscreen.set(screenfull.isFullscreen);
      });
    }
  }
}
```

### 3. Image Gallery Fullscreen

```typescript
import { Component, signal } from '@angular/core';
import screenfull from 'screenfull';
import { NzImageModule } from 'ng-zorro-antd/image';

@Component({
  selector: 'app-construction-photos',
  standalone: true,
  imports: [NzImageModule],
  template: `
    <div class="photo-gallery">
      <h3>Construction Site Photos</h3>
      
      <div class="photo-grid">
        @for (photo of photos(); track photo.id) {
          <div class="photo-item" (click)="viewFullscreen(photo)">
            <img [src]="photo.thumbnailUrl" [alt]="photo.title" />
            <div class="photo-overlay">
              <i nz-icon nzType="fullscreen" nzTheme="outline"></i>
            </div>
          </div>
        }
      </div>
    </div>
    
    @if (currentPhoto()) {
      <div class="fullscreen-viewer" #viewer>
        <button class="close-btn" (click)="exitFullscreen()">
          <i nz-icon nzType="close"></i>
        </button>
        <img [src]="currentPhoto()!.fullUrl" [alt]="currentPhoto()!.title" />
        <div class="photo-info">
          <h4>{{ currentPhoto()!.title }}</h4>
          <p>{{ currentPhoto()!.description }}</p>
          <span>{{ currentPhoto()!.date | date }}</span>
        </div>
      </div>
    }
  `,
  styles: [`
    .photo-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 16px;
    }
    
    .photo-item {
      position: relative;
      cursor: pointer;
      overflow: hidden;
      border-radius: 4px;
    }
    
    .photo-item img {
      width: 100%;
      height: 200px;
      object-fit: cover;
      transition: transform 0.3s;
    }
    
    .photo-item:hover img {
      transform: scale(1.1);
    }
    
    .photo-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      opacity: 0;
      transition: opacity 0.3s;
    }
    
    .photo-item:hover .photo-overlay {
      opacity: 1;
    }
    
    .fullscreen-viewer {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.95);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 9999;
    }
    
    .fullscreen-viewer img {
      max-width: 90%;
      max-height: 90%;
      object-fit: contain;
    }
    
    .close-btn {
      position: absolute;
      top: 20px;
      right: 20px;
      background: rgba(255, 255, 255, 0.2);
      border: none;
      color: white;
      font-size: 24px;
      cursor: pointer;
      padding: 10px;
      border-radius: 4px;
    }
    
    .photo-info {
      position: absolute;
      bottom: 20px;
      left: 20px;
      color: white;
      text-align: left;
    }
  `]
})
export class ConstructionPhotosComponent {
  photos = signal([
    {
      id: '1',
      title: 'Foundation Work',
      description: 'Foundation concrete pouring',
      thumbnailUrl: 'assets/photos/thumb1.jpg',
      fullUrl: 'assets/photos/full1.jpg',
      date: new Date()
    }
    // ... more photos
  ]);
  
  currentPhoto = signal<Photo | null>(null);
  
  viewFullscreen(photo: Photo): void {
    this.currentPhoto.set(photo);
    
    if (screenfull.isEnabled) {
      const viewer = document.querySelector('.fullscreen-viewer');
      if (viewer) {
        screenfull.request(viewer as HTMLElement);
        
        screenfull.on('change', () => {
          if (!screenfull.isFullscreen) {
            this.currentPhoto.set(null);
          }
        });
      }
    }
  }
  
  exitFullscreen(): void {
    if (screenfull.isEnabled && screenfull.isFullscreen) {
      screenfull.exit();
    }
    this.currentPhoto.set(null);
  }
}
```

### 4. Presentation Mode

```typescript
import { Component, signal, OnInit, OnDestroy } from '@angular/core';
import screenfull from 'screenfull';

@Component({
  selector: 'app-presentation-mode',
  standalone: true,
  template: `
    <div class="presentation-container" [class.presentation-active]="isPresenting()">
      <div class="presentation-header">
        <h2>{{ currentSlide().title }}</h2>
        <div class="controls">
          <button (click)="previousSlide()" [disabled]="currentSlideIndex() === 0">
            <i nz-icon nzType="left"></i> Previous
          </button>
          <span>{{ currentSlideIndex() + 1 }} / {{ slides().length }}</span>
          <button (click)="nextSlide()" [disabled]="currentSlideIndex() === slides().length - 1">
            Next <i nz-icon nzType="right"></i>
          </button>
          <button (click)="togglePresentation()" class="btn-present">
            @if (isPresenting()) {
              <i nz-icon nzType="fullscreen-exit"></i> Exit
            } @else {
              <i nz-icon nzType="fullscreen"></i> Present
            }
          </button>
        </div>
      </div>
      
      <div class="slide-content">
        <div [innerHTML]="currentSlide().content"></div>
      </div>
    </div>
  `,
  styles: [`
    .presentation-container {
      background: white;
      padding: 20px;
    }
    
    .presentation-active {
      background: #1a1a1a;
      color: white;
      padding: 40px;
    }
    
    .presentation-active .slide-content {
      font-size: 1.5em;
    }
  `]
})
export class PresentationModeComponent implements OnInit, OnDestroy {
  slides = signal([
    {
      title: 'Project Overview',
      content: '<h1>Construction Site Progress</h1><p>Q4 2025 Update</p>'
    },
    {
      title: 'Milestones Achieved',
      content: '<ul><li>Foundation Complete</li><li>Structural Work 75%</li></ul>'
    }
    // ... more slides
  ]);
  
  currentSlideIndex = signal(0);
  isPresenting = signal(false);
  
  currentSlide = computed(() => this.slides()[this.currentSlideIndex()]);
  
  ngOnInit(): void {
    // Listen for keyboard shortcuts
    document.addEventListener('keydown', this.handleKeyPress.bind(this));
  }
  
  ngOnDestroy(): void {
    document.removeEventListener('keydown', this.handleKeyPress.bind(this));
    
    if (screenfull.isEnabled) {
      screenfull.off('change');
    }
  }
  
  togglePresentation(): void {
    if (screenfull.isEnabled) {
      screenfull.toggle();
      
      screenfull.on('change', () => {
        this.isPresenting.set(screenfull.isFullscreen);
      });
    }
  }
  
  nextSlide(): void {
    if (this.currentSlideIndex() < this.slides().length - 1) {
      this.currentSlideIndex.update(i => i + 1);
    }
  }
  
  previousSlide(): void {
    if (this.currentSlideIndex() > 0) {
      this.currentSlideIndex.update(i => i - 1);
    }
  }
  
  private handleKeyPress(event: KeyboardEvent): void {
    if (!this.isPresenting()) return;
    
    switch (event.key) {
      case 'ArrowRight':
      case 'PageDown':
        this.nextSlide();
        break;
      case 'ArrowLeft':
      case 'PageUp':
        this.previousSlide();
        break;
      case 'Escape':
        if (screenfull.isEnabled && screenfull.isFullscreen) {
          screenfull.exit();
        }
        break;
    }
  }
}
```

## API Reference

### screenfull Methods

```typescript
// Check if fullscreen API is supported
screenfull.isEnabled // boolean

// Toggle fullscreen
screenfull.toggle() // Toggle document
screenfull.toggle(element) // Toggle specific element

// Request fullscreen
screenfull.request() // Request for document
screenfull.request(element) // Request for specific element

// Exit fullscreen
screenfull.exit()

// Check if currently fullscreen
screenfull.isFullscreen // boolean

// Get fullscreen element
screenfull.element // Element | null

// Event listeners
screenfull.on('change', () => {})
screenfull.on('error', (event) => {})
screenfull.off('change', handler)
```

## Integration Checklist

When using screenfull:
- [ ] Check `screenfull.isEnabled` before using API
- [ ] Handle browser compatibility gracefully
- [ ] Clean up event listeners on component destroy
- [ ] Provide exit fullscreen button
- [ ] Test on different browsers (Chrome, Firefox, Safari)
- [ ] Handle keyboard shortcuts (Escape to exit)
- [ ] Style fullscreen mode appropriately
- [ ] Consider mobile browsers (limited support)

## Best Practices

### DO ✅
- Always check `screenfull.isEnabled` before use
- Provide clear UI to exit fullscreen
- Use Escape key to exit fullscreen
- Style fullscreen elements appropriately
- Clean up event listeners
- Handle errors gracefully

### DON'T ❌
- Assume fullscreen API is always available
- Force fullscreen without user interaction
- Forget to remove event listeners
- Ignore mobile browser limitations
- Use fullscreen for sensitive actions

## Browser Compatibility

| Browser | Support |
|---------|---------|
| Chrome | ✅ Full support |
| Firefox | ✅ Full support |
| Safari | ✅ Full support (iOS limited) |
| Edge | ✅ Full support |
| iOS Safari | ⚠️ Limited (video only) |
| Android Chrome | ✅ Full support |

## References

- [screenfull.js GitHub](https://github.com/sindresorhus/screenfull.js)
- [Fullscreen API MDN](https://developer.mozilla.org/en-US/docs/Web/API/Fullscreen_API)
- [Can I Use Fullscreen](https://caniuse.com/fullscreen)

---

**Version**: 1.0.0  
**Compatible with**: screenfull 6.0.x  
**Last Updated**: 2025-12-25
