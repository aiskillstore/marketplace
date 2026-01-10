---
name: "@delon/cache Caching Strategies"
description: "Implement caching strategies using @delon/cache. Use this skill when adding memory cache, LocalStorage cache, SessionStorage cache, or cache interceptors for HTTP requests. Supports TTL-based expiration, cache invalidation, cache grouping, and persistent storage. Optimizes performance by reducing redundant API calls and database queries."
license: "MIT"
---

# @delon/cache Caching Strategies Skill

This skill helps implement caching using @delon/cache library.

## Core Principles

### Cache Types
- **Memory Cache**: Fast, in-memory caching (lost on page refresh)
- **LocalStorage Cache**: Persistent across sessions
- **SessionStorage Cache**: Persistent within session only

### Features
- TTL-based expiration
- Cache invalidation (manual and automatic)
- Cache grouping and namespacing
- HTTP request caching with interceptors
- Observable support for async data

## Configuration

```typescript
// src/app/app.config.ts
import { ApplicationConfig } from '@angular/core';
import { provideDelonCache } from '@delon/cache';

export const appConfig: ApplicationConfig = {
  providers: [
    provideDelonCache({
      mode: 'promise',  // 'promise' | 'none'
      request_method: 'POST',
      meta_key: '__cache_meta',
      prefix: '',
      expire: 3600000  // Default TTL: 1 hour (ms)
    })
  ]
};
```

## Cache Service

```typescript
// src/app/core/services/cache.service.ts
import { Injectable, inject } from '@angular/core';
import { CacheService as DelonCacheService } from '@delon/cache';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class CacheService {
  private cache = inject(DelonCacheService);
  
  /**
   * Set cache with key
   */
  set<T>(key: string, value: T, options?: { 
    type?: 'memory' | 'localStorage' | 'sessionStorage';
    expire?: number; // TTL in milliseconds
  }): void {
    this.cache.set(key, value, {
      type: options?.type || 'memory',
      expire: options?.expire || 3600000 // 1 hour default
    });
  }
  
  /**
   * Get cache by key
   */
  get<T>(key: string): T | null {
    return this.cache.get<T>(key);
  }
  
  /**
   * Check if cache exists and is not expired
   */
  has(key: string): boolean {
    return this.cache.has(key);
  }
  
  /**
   * Remove cache by key
   */
  remove(key: string): void {
    this.cache.remove(key);
  }
  
  /**
   * Clear all cache
   */
  clear(): void {
    this.cache.clear();
  }
  
  /**
   * Get or set cache (lazy loading pattern)
   */
  getOrSet<T>(
    key: string, 
    factory: () => Observable<T> | Promise<T>,
    options?: {
      type?: 'memory' | 'localStorage' | 'sessionStorage';
      expire?: number;
    }
  ): Observable<T> {
    if (this.has(key)) {
      return new Observable(observer => {
        observer.next(this.get<T>(key)!);
        observer.complete();
      });
    }
    
    const result = factory();
    
    if (result instanceof Observable) {
      return new Observable(observer => {
        result.subscribe({
          next: (value) => {
            this.set(key, value, options);
            observer.next(value);
          },
          error: (err) => observer.error(err),
          complete: () => observer.complete()
        });
      });
    }
    
    return new Observable(observer => {
      result.then(value => {
        this.set(key, value, options);
        observer.next(value);
        observer.complete();
      }).catch(err => observer.error(err));
    });
  }
}
```

## Memory Cache (Default)

```typescript
import { Component, inject, signal } from '@angular/core';
import { CacheService } from '@core/services/cache.service';

@Component({
  selector: 'app-task-list',
  template: `
    <button nz-button (click)="loadTasks()">Load Tasks</button>
    <button nz-button (click)="clearCache()">Clear Cache</button>
    
    @if (loading()) {
      <nz-spin />
    } @else {
      @for (task of tasks(); track task.id) {
        <div>{{ task.title }}</div>
      }
    }
  `
})
export class TaskListComponent {
  private cacheService = inject(CacheService);
  private taskService = inject(TaskService);
  
  loading = signal(false);
  tasks = signal<Task[]>([]);
  
  private readonly CACHE_KEY = 'tasks:list';
  
  async loadTasks(): Promise<void> {
    // Try to get from cache first
    const cached = this.cacheService.get<Task[]>(this.CACHE_KEY);
    
    if (cached) {
      console.log('Loading from cache');
      this.tasks.set(cached);
      return;
    }
    
    // Load from API
    this.loading.set(true);
    try {
      const tasks = await this.taskService.getTasks();
      
      // Cache for 5 minutes
      this.cacheService.set(this.CACHE_KEY, tasks, {
        type: 'memory',
        expire: 5 * 60 * 1000 // 5 minutes
      });
      
      this.tasks.set(tasks);
    } finally {
      this.loading.set(false);
    }
  }
  
  clearCache(): void {
    this.cacheService.remove(this.CACHE_KEY);
    console.log('Cache cleared');
  }
}
```

## LocalStorage Cache (Persistent)

```typescript
import { Injectable, inject } from '@angular/core';
import { CacheService } from '@core/services/cache.service';

@Injectable({ providedIn: 'root' })
export class UserPreferencesService {
  private cacheService = inject(CacheService);
  
  private readonly CACHE_KEY = 'user:preferences';
  
  /**
   * Save user preferences (persists across sessions)
   */
  savePreferences(preferences: UserPreferences): void {
    this.cacheService.set(this.CACHE_KEY, preferences, {
      type: 'localStorage',
      expire: 30 * 24 * 60 * 60 * 1000 // 30 days
    });
  }
  
  /**
   * Load user preferences
   */
  loadPreferences(): UserPreferences | null {
    return this.cacheService.get<UserPreferences>(this.CACHE_KEY);
  }
  
  /**
   * Clear preferences
   */
  clearPreferences(): void {
    this.cacheService.remove(this.CACHE_KEY);
  }
}

interface UserPreferences {
  theme: 'light' | 'dark';
  language: string;
  sidebarCollapsed: boolean;
}
```

## SessionStorage Cache

```typescript
/**
 * Cache search results for current session only
 */
@Injectable({ providedIn: 'root' })
export class SearchService {
  private cacheService = inject(CacheService);
  
  async search(query: string): Promise<SearchResult[]> {
    const cacheKey = `search:${query}`;
    
    // Check session cache
    const cached = this.cacheService.get<SearchResult[]>(cacheKey);
    if (cached) {
      return cached;
    }
    
    // Perform search
    const results = await this.performSearch(query);
    
    // Cache for current session only
    this.cacheService.set(cacheKey, results, {
      type: 'sessionStorage',
      expire: 30 * 60 * 1000 // 30 minutes
    });
    
    return results;
  }
  
  private async performSearch(query: string): Promise<SearchResult[]> {
    // API call
    return [];
  }
}
```

## Lazy Loading with getOrSet

```typescript
@Injectable({ providedIn: 'root' })
export class ConfigService {
  private cacheService = inject(CacheService);
  private http = inject(HttpClient);
  
  /**
   * Load configuration with automatic caching
   */
  loadConfig(): Observable<AppConfig> {
    return this.cacheService.getOrSet(
      'app:config',
      () => this.http.get<AppConfig>('/api/config'),
      {
        type: 'localStorage',
        expire: 24 * 60 * 60 * 1000 // 24 hours
      }
    );
  }
}
```

## Cache Invalidation

### Manual Invalidation

```typescript
@Injectable({ providedIn: 'root' })
export class TaskService {
  private cacheService = inject(CacheService);
  private taskRepository = inject(TaskRepository);
  
  /**
   * Create task and invalidate cache
   */
  async createTask(task: Omit<Task, 'id'>): Promise<Task> {
    const created = await this.taskRepository.create(task);
    
    // Invalidate task list cache
    this.cacheService.remove('tasks:list');
    this.cacheService.remove(`tasks:blueprint:${task.blueprintId}`);
    
    return created;
  }
  
  /**
   * Update task and invalidate cache
   */
  async updateTask(id: string, updates: Partial<Task>): Promise<Task> {
    const updated = await this.taskRepository.update(id, updates);
    
    // Invalidate specific task cache
    this.cacheService.remove(`tasks:${id}`);
    
    // Invalidate list caches
    this.cacheService.remove('tasks:list');
    
    return updated;
  }
}
```

### Group Cache Invalidation

```typescript
@Injectable({ providedIn: 'root' })
export class CacheInvalidationService {
  private cacheService = inject(CacheService);
  
  /**
   * Invalidate all caches with prefix
   */
  invalidateGroup(prefix: string): void {
    // @delon/cache doesn't have built-in group invalidation
    // So we track cache keys manually
    const keys = this.getCacheKeys(prefix);
    keys.forEach(key => this.cacheService.remove(key));
  }
  
  private cacheKeys = new Set<string>();
  
  registerCacheKey(key: string): void {
    this.cacheKeys.add(key);
  }
  
  private getCacheKeys(prefix: string): string[] {
    return Array.from(this.cacheKeys).filter(key => key.startsWith(prefix));
  }
}
```

## HTTP Cache Interceptor

```typescript
// src/app/core/interceptors/cache.interceptor.ts
import { HttpInterceptorFn, HttpResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { CacheService } from '@core/services/cache.service';
import { of, tap } from 'rxjs';

/**
 * Cache GET requests
 */
export const cacheInterceptor: HttpInterceptorFn = (req, next) => {
  const cacheService = inject(CacheService);
  
  // Only cache GET requests
  if (req.method !== 'GET') {
    return next(req);
  }
  
  // Skip cache for certain URLs
  const skipCache = req.headers.has('X-Skip-Cache') || 
                    req.url.includes('/api/realtime');
  
  if (skipCache) {
    return next(req);
  }
  
  // Generate cache key from URL + params
  const cacheKey = `http:${req.urlWithParams}`;
  
  // Check cache
  const cached = cacheService.get<HttpResponse<any>>(cacheKey);
  if (cached) {
    console.log('Serving from cache:', cacheKey);
    return of(cached);
  }
  
  // Make request and cache response
  return next(req).pipe(
    tap(event => {
      if (event instanceof HttpResponse) {
        cacheService.set(cacheKey, event, {
          type: 'memory',
          expire: 5 * 60 * 1000 // 5 minutes
        });
      }
    })
  );
};
```

### Register Interceptor

```typescript
// src/app/app.config.ts
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { cacheInterceptor } from '@core/interceptors/cache.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(
      withInterceptors([cacheInterceptor])
    )
  ]
};
```

## Cache Namespacing

```typescript
@Injectable({ providedIn: 'root' })
export class NamespacedCacheService {
  private cacheService = inject(CacheService);
  
  constructor(private namespace: string) {}
  
  private getKey(key: string): string {
    return `${this.namespace}:${key}`;
  }
  
  set<T>(key: string, value: T, options?: any): void {
    this.cacheService.set(this.getKey(key), value, options);
  }
  
  get<T>(key: string): T | null {
    return this.cacheService.get<T>(this.getKey(key));
  }
  
  remove(key: string): void {
    this.cacheService.remove(this.getKey(key));
  }
}

// Usage
@Injectable({ providedIn: 'root' })
export class TaskCacheService extends NamespacedCacheService {
  constructor() {
    super('tasks');
  }
}
```

## Cache Patterns

### Read-Through Cache

```typescript
async getTask(id: string): Promise<Task> {
  const cacheKey = `tasks:${id}`;
  
  // Try cache
  let task = this.cacheService.get<Task>(cacheKey);
  if (task) {
    return task;
  }
  
  // Load from repository
  task = await this.taskRepository.findById(id);
  
  // Cache result
  if (task) {
    this.cacheService.set(cacheKey, task, {
      type: 'memory',
      expire: 10 * 60 * 1000 // 10 minutes
    });
  }
  
  return task;
}
```

### Write-Through Cache

```typescript
async updateTask(id: string, updates: Partial<Task>): Promise<Task> {
  // Update in repository
  const updated = await this.taskRepository.update(id, updates);
  
  // Update cache
  const cacheKey = `tasks:${id}`;
  this.cacheService.set(cacheKey, updated, {
    type: 'memory',
    expire: 10 * 60 * 1000
  });
  
  return updated;
}
```

### Cache-Aside Pattern

```typescript
async getTasks(blueprintId: string): Promise<Task[]> {
  const cacheKey = `tasks:blueprint:${blueprintId}`;
  
  // Check cache
  if (this.cacheService.has(cacheKey)) {
    return this.cacheService.get<Task[]>(cacheKey)!;
  }
  
  // Load from repository
  const tasks = await this.taskRepository.findByBlueprintId(blueprintId);
  
  // Populate cache
  this.cacheService.set(cacheKey, tasks, {
    type: 'memory',
    expire: 5 * 60 * 1000
  });
  
  return tasks;
}
```

## Best Practices

### Cache Key Naming

```typescript
// Good: Descriptive, hierarchical keys
'users:123'
'tasks:blueprint:abc-123'
'config:app:theme'

// Bad: Generic, flat keys
'user'
'data123'
'cache'
```

### TTL Guidelines

```typescript
// Static data: 1 hour - 1 day
this.cacheService.set('config', data, { expire: 24 * 60 * 60 * 1000 });

// Dynamic data: 1-10 minutes
this.cacheService.set('tasks', data, { expire: 5 * 60 * 1000 });

// User-specific: Session duration
this.cacheService.set('user:prefs', data, { type: 'sessionStorage' });

// Persistent: 30 days
this.cacheService.set('settings', data, { 
  type: 'localStorage',
  expire: 30 * 24 * 60 * 60 * 1000 
});
```

## Checklist

When implementing caching:

- [ ] Choose appropriate cache type (memory/localStorage/sessionStorage)
- [ ] Set reasonable TTL values
- [ ] Implement cache invalidation on data changes
- [ ] Use descriptive, hierarchical cache keys
- [ ] Handle cache misses gracefully
- [ ] Monitor cache hit/miss rates
- [ ] Consider cache size limits
- [ ] Test cache expiration
- [ ] Document caching strategy
- [ ] Implement cache warming for critical data

## References

- [@delon/cache Documentation](https://ng-alain.com/cache)
- [Caching Best Practices](https://aws.amazon.com/caching/best-practices/)
- [Cache Patterns](https://docs.microsoft.com/en-us/azure/architecture/patterns/cache-aside)
