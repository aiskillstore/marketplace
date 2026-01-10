---
name: "@delon/auth Authentication & Authorization"
description: "Implement authentication and authorization using @delon/auth. Use this skill when adding login/logout flows, JWT token management, role-based access control (RBAC), route guards, HTTP interceptors, and session management. Integrates with Firebase Auth and custom permission systems. Ensures secure token storage, automatic token refresh, and consistent authorization checks across components and services."
license: "MIT"
---

# @delon/auth Authentication & Authorization Skill

This skill helps implement authentication and authorization using @delon/auth library.

## Core Principles

### Token Management
- **JWT Storage**: Secure token storage using DA_SERVICE_TOKEN
- **Auto Refresh**: Automatic token renewal before expiration
- **Interceptors**: Automatic token injection in HTTP requests
- **Logout**: Clean token removal and session cleanup

### Authorization
- **RBAC**: Role-based access control
- **Permissions**: Fine-grained permission checking
- **Guards**: Route protection with role/permission checks
- **ACL Integration**: Works with @delon/acl for UI-level controls

## Configuration

### App Config

```typescript
// src/app/app.config.ts
import { ApplicationConfig } from '@angular/core';
import { provideDelonAuth, DA_SERVICE_TOKEN, ITokenService } from '@delon/auth';
import { JWTTokenModel } from '@delon/auth';

export const appConfig: ApplicationConfig = {
  providers: [
    provideDelonAuth({
      token_send_key: 'Authorization',
      token_send_template: 'Bearer ${token}',
      token_send_place: 'header',
      login_url: '/passport/login',
      ignores: [/\/login/, /assets\//],
      allow_anonymous_key: 'allow_anonymous',
      executeOtherInterceptors: true,
      refreshTime: 3000, // Refresh token check interval (ms)
      refreshOffset: 6000 // Refresh token before expiration (ms)
    })
  ]
};
```

### Token Model

```typescript
// src/app/core/models/auth-token.model.ts
import { JWTTokenModel } from '@delon/auth';

export interface AuthTokenModel extends JWTTokenModel {
  token: string;
  uid: string;
  email: string;
  displayName: string;
  role: string;
  permissions: string[];
  exp: number;
}
```

## Authentication Service

```typescript
// src/app/core/services/auth.service.ts
import { Injectable, inject } from '@angular/core';
import { Router } from '@angular/router';
import { DA_SERVICE_TOKEN, ITokenService } from '@delon/auth';
import { Auth, signInWithEmailAndPassword, signOut, User } from '@angular/fire/auth';
import { AuthTokenModel } from '@core/models/auth-token.model';
import { signal, computed } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private auth = inject(Auth);
  private tokenService = inject<ITokenService>(DA_SERVICE_TOKEN);
  private router = inject(Router);
  
  // State
  private currentUser = signal<User | null>(null);
  private authToken = signal<AuthTokenModel | null>(null);
  
  // Computed
  isAuthenticated = computed(() => this.tokenService.get()?.token != null);
  userRole = computed(() => this.authToken()?.role);
  userPermissions = computed(() => this.authToken()?.permissions || []);
  
  constructor() {
    // Listen to Firebase Auth state
    this.auth.onAuthStateChanged(async (user) => {
      this.currentUser.set(user);
      if (user) {
        await this.refreshToken();
      } else {
        this.clearSession();
      }
    });
  }
  
  /**
   * Login with email and password
   */
  async login(email: string, password: string): Promise<void> {
    try {
      const credential = await signInWithEmailAndPassword(this.auth, email, password);
      const token = await credential.user.getIdToken();
      const tokenData = await this.parseToken(token);
      
      // Store token in @delon/auth
      this.tokenService.set(tokenData);
      this.authToken.set(tokenData);
      
      // Navigate to dashboard
      await this.router.navigateByUrl('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }
  
  /**
   * Logout
   */
  async logout(): Promise<void> {
    try {
      await signOut(this.auth);
      this.clearSession();
      await this.router.navigateByUrl('/passport/login');
    } catch (error) {
      console.error('Logout failed:', error);
      throw error;
    }
  }
  
  /**
   * Refresh token
   */
  async refreshToken(): Promise<void> {
    const user = this.currentUser();
    if (!user) return;
    
    try {
      const token = await user.getIdToken(true); // Force refresh
      const tokenData = await this.parseToken(token);
      
      this.tokenService.set(tokenData);
      this.authToken.set(tokenData);
    } catch (error) {
      console.error('Token refresh failed:', error);
      await this.logout();
    }
  }
  
  /**
   * Check if user has specific role
   */
  hasRole(role: string): boolean {
    return this.userRole() === role;
  }
  
  /**
   * Check if user has specific permission
   */
  hasPermission(permission: string): boolean {
    return this.userPermissions().includes(permission);
  }
  
  /**
   * Check if user has any of the specified permissions
   */
  hasAnyPermission(permissions: string[]): boolean {
    const userPerms = this.userPermissions();
    return permissions.some(p => userPerms.includes(p));
  }
  
  /**
   * Check if user has all of the specified permissions
   */
  hasAllPermissions(permissions: string[]): boolean {
    const userPerms = this.userPermissions();
    return permissions.every(p => userPerms.includes(p));
  }
  
  /**
   * Parse JWT token
   */
  private async parseToken(token: string): Promise<AuthTokenModel> {
    // Decode JWT payload
    const payload = JSON.parse(atob(token.split('.')[1]));
    
    // Load user permissions from Firestore (custom claims)
    const permissions = await this.loadUserPermissions(payload.uid);
    
    return {
      token,
      uid: payload.uid,
      email: payload.email,
      displayName: payload.name || payload.email,
      role: payload.role || 'member',
      permissions,
      exp: payload.exp
    };
  }
  
  /**
   * Load user permissions from Firestore
   */
  private async loadUserPermissions(uid: string): Promise<string[]> {
    // Implementation: query user's permissions from Firestore
    // This is placeholder - implement based on your schema
    return ['read:tasks', 'write:tasks'];
  }
  
  /**
   * Clear session
   */
  private clearSession(): void {
    this.tokenService.clear();
    this.authToken.set(null);
    this.currentUser.set(null);
  }
}
```

## Auth Guard

```typescript
// src/app/core/guards/auth.guard.ts
import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '@core/services/auth.service';

/**
 * Guard to protect routes requiring authentication
 */
export const authGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  if (authService.isAuthenticated()) {
    return true;
  }
  
  return router.createUrlTree(['/passport/login']);
};
```

## Role Guard

```typescript
// src/app/core/guards/role.guard.ts
import { inject } from '@angular/core';
import { Router, CanActivateFn, ActivatedRouteSnapshot } from '@angular/router';
import { AuthService } from '@core/services/auth.service';

/**
 * Guard to protect routes by role
 */
export const roleGuard: CanActivateFn = (route: ActivatedRouteSnapshot) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  const requiredRole = route.data['role'] as string;
  
  if (!requiredRole) {
    console.warn('Role guard used without required role');
    return true;
  }
  
  if (authService.hasRole(requiredRole)) {
    return true;
  }
  
  // Redirect to unauthorized page
  return router.createUrlTree(['/exception/403']);
};

/**
 * Usage in routes:
 * {
 *   path: 'admin',
 *   component: AdminComponent,
 *   canActivate: [authGuard, roleGuard],
 *   data: { role: 'admin' }
 * }
 */
```

## Permission Guard

```typescript
// src/app/core/guards/permission.guard.ts
import { inject } from '@angular/core';
import { Router, CanActivateFn, ActivatedRouteSnapshot } from '@angular/router';
import { AuthService } from '@core/services/auth.service';

/**
 * Guard to protect routes by permissions
 */
export const permissionGuard: CanActivateFn = (route: ActivatedRouteSnapshot) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  const requiredPermissions = route.data['permissions'] as string[];
  const requireAll = route.data['requireAll'] as boolean ?? true;
  
  if (!requiredPermissions || requiredPermissions.length === 0) {
    console.warn('Permission guard used without required permissions');
    return true;
  }
  
  const hasAccess = requireAll
    ? authService.hasAllPermissions(requiredPermissions)
    : authService.hasAnyPermission(requiredPermissions);
  
  if (hasAccess) {
    return true;
  }
  
  return router.createUrlTree(['/exception/403']);
};

/**
 * Usage in routes:
 * {
 *   path: 'tasks',
 *   component: TaskListComponent,
 *   canActivate: [authGuard, permissionGuard],
 *   data: { 
 *     permissions: ['read:tasks'], 
 *     requireAll: true 
 *   }
 * }
 */
```

## Login Component

```typescript
// src/app/routes/passport/login/login.component.ts
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '@core/services/auth.service';
import { SHARED_IMPORTS } from '@shared';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [SHARED_IMPORTS],
  template: `
    <div class="login-container">
      <nz-card>
        <h2>Login</h2>
        <form nz-form [formGroup]="loginForm" (ngSubmit)="handleLogin()">
          <nz-form-item>
            <nz-form-control nzErrorTip="Please input your email!">
              <nz-input-group nzPrefixIcon="mail">
                <input 
                  nz-input 
                  formControlName="email" 
                  placeholder="Email"
                  type="email"
                />
              </nz-input-group>
            </nz-form-control>
          </nz-form-item>
          
          <nz-form-item>
            <nz-form-control nzErrorTip="Please input your password!">
              <nz-input-group nzPrefixIcon="lock">
                <input 
                  nz-input 
                  formControlName="password" 
                  placeholder="Password"
                  type="password"
                />
              </nz-input-group>
            </nz-form-control>
          </nz-form-item>
          
          @if (error()) {
            <nz-alert 
              nzType="error" 
              [nzMessage]="error()!" 
              nzShowIcon 
            />
          }
          
          <button 
            nz-button 
            nzType="primary" 
            nzBlock 
            [nzLoading]="loading()"
            [disabled]="loginForm.invalid"
          >
            Login
          </button>
        </form>
      </nz-card>
    </div>
  `
})
export class LoginComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  
  loading = signal(false);
  error = signal<string | null>(null);
  
  loginForm: FormGroup = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(6)]]
  });
  
  async handleLogin(): Promise<void> {
    if (this.loginForm.invalid) return;
    
    this.loading.set(true);
    this.error.set(null);
    
    try {
      const { email, password } = this.loginForm.value;
      await this.authService.login(email, password);
    } catch (err) {
      this.error.set(err instanceof Error ? err.message : 'Login failed');
    } finally {
      this.loading.set(false);
    }
  }
}
```

## HTTP Interceptor (Auto Token Injection)

@delon/auth automatically provides an interceptor when configured. No manual implementation needed!

```typescript
// Automatic token injection in all HTTP requests
// Configured in app.config.ts with provideDelonAuth()

// Example HTTP call - token automatically added
this.http.get('/api/tasks').subscribe(tasks => {
  // Authorization: Bearer {token} header automatically added
});
```

## Component-Level Permission Check

```typescript
import { Component, inject, computed } from '@angular/core';
import { AuthService } from '@core/services/auth.service';

@Component({
  selector: 'app-task-list',
  template: `
    @if (canCreate()) {
      <button nz-button nzType="primary" (click)="createTask()">
        Create Task
      </button>
    }
    
    @if (canEdit()) {
      <button nz-button (click)="editTask()">Edit</button>
    }
    
    @if (canDelete()) {
      <button nz-button nzDanger (click)="deleteTask()">Delete</button>
    }
  `
})
export class TaskListComponent {
  private authService = inject(AuthService);
  
  canCreate = computed(() => this.authService.hasPermission('create:tasks'));
  canEdit = computed(() => this.authService.hasPermission('edit:tasks'));
  canDelete = computed(() => this.authService.hasPermission('delete:tasks'));
}
```

## Integration with @delon/acl

```typescript
// src/app/app.config.ts
import { provideDelonACL } from '@delon/acl';

export const appConfig: ApplicationConfig = {
  providers: [
    provideDelonACL()
  ]
};
```

```typescript
// Sync permissions to ACL
import { ACLService } from '@delon/acl';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private aclService = inject(ACLService);
  
  private syncPermissionsToACL(permissions: string[], role: string): void {
    this.aclService.setRole([role]);
    this.aclService.setAbility(permissions);
  }
}
```

## Routes Configuration

```typescript
// src/app/routes/routes.ts
import { Routes } from '@angular/router';
import { authGuard } from '@core/guards/auth.guard';
import { roleGuard } from '@core/guards/role.guard';
import { permissionGuard } from '@core/guards/permission.guard';

export const routes: Routes = [
  {
    path: '',
    canActivate: [authGuard],
    children: [
      {
        path: 'dashboard',
        loadComponent: () => import('./dashboard/dashboard.component')
      },
      {
        path: 'admin',
        canActivate: [roleGuard],
        data: { role: 'admin' },
        loadComponent: () => import('./admin/admin.component')
      },
      {
        path: 'tasks',
        canActivate: [permissionGuard],
        data: { 
          permissions: ['read:tasks'],
          requireAll: true
        },
        loadComponent: () => import('./tasks/task-list.component')
      }
    ]
  },
  {
    path: 'passport',
    children: [
      {
        path: 'login',
        loadComponent: () => import('./passport/login/login.component')
      }
    ]
  }
];
```

## Checklist

When implementing authentication:

- [ ] Configure @delon/auth in app.config.ts
- [ ] Create AuthService with token management
- [ ] Implement login/logout methods
- [ ] Set up token refresh mechanism
- [ ] Create auth guard for protected routes
- [ ] Create role/permission guards as needed
- [ ] Integrate with Firebase Auth
- [ ] Sync permissions with @delon/acl
- [ ] Handle token expiration
- [ ] Test authentication flow
- [ ] Test authorization checks
- [ ] Handle error states (invalid credentials, network errors)

## References

- [@delon/auth Documentation](https://ng-alain.com/auth)
- [@delon/acl Documentation](https://ng-alain.com/acl)
- [Firebase Auth](https://firebase.google.com/docs/auth)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
