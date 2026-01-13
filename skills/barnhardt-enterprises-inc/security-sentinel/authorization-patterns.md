# Authorization Patterns

Complete reference for implementing authorization (access control) in Next.js 15.

---

## Table of Contents

1. [Role-Based Access Control (RBAC)](#role-based-access-control-rbac)
2. [Attribute-Based Access Control (ABAC)](#attribute-based-access-control-abac)
3. [Middleware Protection](#middleware-protection)
4. [API Route Protection](#api-route-protection)
5. [Server Action Protection](#server-action-protection)
6. [Row-Level Security](#row-level-security)
7. [Permission System](#permission-system)
8. [Resource Ownership](#resource-ownership)

---

## Role-Based Access Control (RBAC)

### Define Roles and Permissions

```typescript
// src/lib/auth/roles.ts
export const ROLES = {
  ADMIN: 'ADMIN',
  MANAGER: 'MANAGER',
  USER: 'USER',
  GUEST: 'GUEST',
} as const

export type Role = typeof ROLES[keyof typeof ROLES]

// Define permissions for each role
export const ROLE_PERMISSIONS = {
  [ROLES.ADMIN]: [
    'user:read',
    'user:create',
    'user:update',
    'user:delete',
    'project:read',
    'project:create',
    'project:update',
    'project:delete',
    'settings:manage',
  ],
  [ROLES.MANAGER]: [
    'user:read',
    'project:read',
    'project:create',
    'project:update',
    'project:delete',
  ],
  [ROLES.USER]: [
    'project:read',
    'project:create',
    'project:update',
  ],
  [ROLES.GUEST]: [
    'project:read',
  ],
} as const

// ✅ Check if role has permission
export function hasPermission(role: Role, permission: string): boolean {
  return ROLE_PERMISSIONS[role]?.includes(permission as any) ?? false
}

// ✅ Check if role has any of the permissions
export function hasAnyPermission(role: Role, permissions: string[]): boolean {
  return permissions.some((permission) => hasPermission(role, permission))
}

// ✅ Check if role has all permissions
export function hasAllPermissions(role: Role, permissions: string[]): boolean {
  return permissions.every((permission) => hasPermission(role, permission))
}

// ✅ Role hierarchy (higher role includes lower role permissions)
const ROLE_HIERARCHY: Record<Role, number> = {
  [ROLES.ADMIN]: 4,
  [ROLES.MANAGER]: 3,
  [ROLES.USER]: 2,
  [ROLES.GUEST]: 1,
}

export function roleLevel(role: Role): number {
  return ROLE_HIERARCHY[role] ?? 0
}

export function isRoleHigherOrEqual(role: Role, targetRole: Role): boolean {
  return roleLevel(role) >= roleLevel(targetRole)
}
```

### Authorization Utilities

```typescript
// src/lib/auth/authorization.ts
import { getCurrentUser } from '@/lib/auth/jwt'
import { hasPermission, Role } from './roles'

// ✅ Require authentication
export async function requireAuth() {
  const user = await getCurrentUser()

  if (!user) {
    throw new Error('Unauthorized')
  }

  return user
}

// ✅ Require specific role
export async function requireRole(allowedRoles: Role[]) {
  const user = await requireAuth()

  if (!allowedRoles.includes(user.role as Role)) {
    throw new Error('Forbidden')
  }

  return user
}

// ✅ Require specific permission
export async function requirePermission(permission: string) {
  const user = await requireAuth()

  if (!hasPermission(user.role as Role, permission)) {
    throw new Error('Forbidden')
  }

  return user
}

// ✅ Require any of the permissions
export async function requireAnyPermission(permissions: string[]) {
  const user = await requireAuth()

  const hasAny = permissions.some((permission) =>
    hasPermission(user.role as Role, permission)
  )

  if (!hasAny) {
    throw new Error('Forbidden')
  }

  return user
}

// ✅ Check if current user can access resource
export async function canAccessResource(
  resourceUserId: string
): Promise<boolean> {
  const user = await getCurrentUser()

  if (!user) {
    return false
  }

  // Admins can access everything
  if (user.role === 'ADMIN') {
    return true
  }

  // User can access their own resources
  return user.userId === resourceUserId
}
```

### Protected API Routes

```typescript
// src/app/api/admin/users/route.ts
import { requireRole, ROLES } from '@/lib/auth/authorization'
import { db } from '@/lib/db'

// ✅ Admin-only endpoint
export async function GET() {
  try {
    // Require ADMIN role
    await requireRole([ROLES.ADMIN])

    const users = await db.user.findMany({
      select: {
        id: true,
        email: true,
        name: true,
        role: true,
        createdAt: true,
      },
    })

    return Response.json({ users })
  } catch (error) {
    if (error.message === 'Unauthorized') {
      return Response.json({ error: 'Unauthorized' }, { status: 401 })
    }

    if (error.message === 'Forbidden') {
      return Response.json({ error: 'Forbidden' }, { status: 403 })
    }

    return Response.json({ error: 'Internal server error' }, { status: 500 })
  }
}

// ✅ Manager or Admin can update user roles
export async function PATCH(request: Request) {
  try {
    await requireRole([ROLES.ADMIN, ROLES.MANAGER])

    const { userId, role } = await request.json()

    // Additional check: only admins can assign ADMIN role
    const currentUser = await requireAuth()
    if (role === ROLES.ADMIN && currentUser.role !== ROLES.ADMIN) {
      return Response.json(
        { error: 'Only admins can assign admin role' },
        { status: 403 }
      )
    }

    const user = await db.user.update({
      where: { id: userId },
      data: { role },
    })

    return Response.json({ user })
  } catch (error) {
    if (error.message === 'Unauthorized') {
      return Response.json({ error: 'Unauthorized' }, { status: 401 })
    }

    if (error.message === 'Forbidden') {
      return Response.json({ error: 'Forbidden' }, { status: 403 })
    }

    return Response.json({ error: 'Internal server error' }, { status: 500 })
  }
}
```

---

## Attribute-Based Access Control (ABAC)

### Policy-Based Authorization

```typescript
// src/lib/auth/policies.ts
import { JWTPayload } from './jwt'

export interface Resource {
  id: string
  userId: string
  organizationId?: string
  visibility?: 'public' | 'private' | 'organization'
  [key: string]: any
}

export interface PolicyContext {
  user: JWTPayload
  resource: Resource
  action: string
  environment: {
    time: Date
    ip: string
  }
}

// ✅ Policy evaluation function
export type Policy = (context: PolicyContext) => boolean

// ✅ Example policies
export const policies: Record<string, Policy> = {
  // User can read their own resources
  'project:read:own': (ctx) => {
    return ctx.resource.userId === ctx.user.userId
  },

  // User can update their own resources
  'project:update:own': (ctx) => {
    return ctx.resource.userId === ctx.user.userId
  },

  // User can delete their own resources
  'project:delete:own': (ctx) => {
    return ctx.resource.userId === ctx.user.userId
  },

  // User can read public resources
  'project:read:public': (ctx) => {
    return ctx.resource.visibility === 'public'
  },

  // User can read organization resources
  'project:read:organization': (ctx) => {
    return (
      ctx.resource.visibility === 'organization' &&
      ctx.resource.organizationId === ctx.user.organizationId
    )
  },

  // Admin can do anything
  'admin:*': (ctx) => {
    return ctx.user.role === 'ADMIN'
  },

  // Business hours only
  'action:businessHours': (ctx) => {
    const hour = ctx.environment.time.getHours()
    return hour >= 9 && hour < 17
  },

  // IP whitelist
  'action:fromWhitelistedIP': (ctx) => {
    const whitelist = ['192.168.1.0/24', '10.0.0.0/8']
    return whitelist.some((range) => ipInRange(ctx.environment.ip, range))
  },
}

// ✅ Evaluate policy
export function evaluatePolicy(
  policyName: string,
  context: PolicyContext
): boolean {
  const policy = policies[policyName]

  if (!policy) {
    throw new Error(`Policy ${policyName} not found`)
  }

  return policy(context)
}

// ✅ Evaluate multiple policies (AND)
export function evaluatePolicies(
  policyNames: string[],
  context: PolicyContext
): boolean {
  return policyNames.every((policyName) => evaluatePolicy(policyName, context))
}

// ✅ Evaluate multiple policies (OR)
export function evaluateAnyPolicy(
  policyNames: string[],
  context: PolicyContext
): boolean {
  return policyNames.some((policyName) => evaluatePolicy(policyName, context))
}

function ipInRange(ip: string, range: string): boolean {
  // Implementation of IP range checking
  // (See OWASP Top 10 - SSRF section for full implementation)
  return true  // Placeholder
}
```

### Using Policies in API Routes

```typescript
// src/app/api/projects/[id]/route.ts
import { requireAuth } from '@/lib/auth/authorization'
import { evaluateAnyPolicy } from '@/lib/auth/policies'
import { db } from '@/lib/db'

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const user = await requireAuth()

    const project = await db.project.findUnique({
      where: { id: params.id },
    })

    if (!project) {
      return Response.json({ error: 'Not found' }, { status: 404 })
    }

    // ✅ Evaluate policies
    const canRead = evaluateAnyPolicy(
      [
        'admin:*',
        'project:read:own',
        'project:read:public',
        'project:read:organization',
      ],
      {
        user,
        resource: project,
        action: 'read',
        environment: {
          time: new Date(),
          ip: request.headers.get('x-forwarded-for') || 'unknown',
        },
      }
    )

    if (!canRead) {
      return Response.json({ error: 'Forbidden' }, { status: 403 })
    }

    return Response.json({ project })
  } catch (error) {
    if (error.message === 'Unauthorized') {
      return Response.json({ error: 'Unauthorized' }, { status: 401 })
    }

    return Response.json({ error: 'Internal server error' }, { status: 500 })
  }
}
```

---

## Middleware Protection

### Route Protection Middleware

```typescript
// src/middleware.ts
import { NextRequest, NextResponse } from 'next/server'
import { verifyToken } from '@/lib/auth/jwt'
import { ROLES } from '@/lib/auth/roles'

// ✅ Define protected routes
const PROTECTED_ROUTES = [
  '/dashboard',
  '/projects',
  '/settings',
]

const ADMIN_ROUTES = [
  '/admin',
]

const PUBLIC_ROUTES = [
  '/',
  '/login',
  '/register',
  '/about',
]

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // ✅ Check if route is protected
  const isProtectedRoute = PROTECTED_ROUTES.some((route) =>
    pathname.startsWith(route)
  )
  const isAdminRoute = ADMIN_ROUTES.some((route) => pathname.startsWith(route))

  if (!isProtectedRoute && !isAdminRoute) {
    return NextResponse.next()
  }

  // ✅ Get token from cookie
  const token = request.cookies.get('auth-token')?.value

  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // ✅ Verify token
  try {
    const payload = await verifyToken(token)

    // ✅ Check admin routes
    if (isAdminRoute && payload.role !== ROLES.ADMIN) {
      return NextResponse.redirect(new URL('/forbidden', request.url))
    }

    // ✅ Add user to request headers (accessible in route handlers)
    const response = NextResponse.next()
    response.headers.set('x-user-id', payload.userId)
    response.headers.set('x-user-email', payload.email)
    response.headers.set('x-user-role', payload.role)

    return response
  } catch {
    return NextResponse.redirect(new URL('/login', request.url))
  }
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (public folder)
     */
    '/((?!api|_next/static|_next/image|favicon.ico|.*\\.png$).*)',
  ],
}
```

---

## API Route Protection

### withAuth Higher-Order Function

```typescript
// src/lib/auth/withAuth.ts
import { NextRequest } from 'next/server'
import { requireAuth, requireRole, requirePermission } from './authorization'
import { Role } from './roles'

type RouteHandler = (
  request: NextRequest,
  context: { params: any }
) => Promise<Response>

type AuthenticatedRouteHandler = (
  request: NextRequest,
  context: { params: any; user: JWTPayload }
) => Promise<Response>

// ✅ Wrap route handler with authentication
export function withAuth(handler: AuthenticatedRouteHandler): RouteHandler {
  return async (request, context) => {
    try {
      const user = await requireAuth()

      // Call handler with user
      return handler(request, { ...context, user })
    } catch (error) {
      if (error.message === 'Unauthorized') {
        return Response.json({ error: 'Unauthorized' }, { status: 401 })
      }

      return Response.json({ error: 'Internal server error' }, { status: 500 })
    }
  }
}

// ✅ Wrap route handler with role check
export function withRole(roles: Role[]) {
  return (handler: AuthenticatedRouteHandler): RouteHandler => {
    return async (request, context) => {
      try {
        const user = await requireRole(roles)

        return handler(request, { ...context, user })
      } catch (error) {
        if (error.message === 'Unauthorized') {
          return Response.json({ error: 'Unauthorized' }, { status: 401 })
        }

        if (error.message === 'Forbidden') {
          return Response.json({ error: 'Forbidden' }, { status: 403 })
        }

        return Response.json({ error: 'Internal server error' }, { status: 500 })
      }
    }
  }
}

// ✅ Wrap route handler with permission check
export function withPermission(permission: string) {
  return (handler: AuthenticatedRouteHandler): RouteHandler => {
    return async (request, context) => {
      try {
        const user = await requirePermission(permission)

        return handler(request, { ...context, user })
      } catch (error) {
        if (error.message === 'Unauthorized') {
          return Response.json({ error: 'Unauthorized' }, { status: 401 })
        }

        if (error.message === 'Forbidden') {
          return Response.json({ error: 'Forbidden' }, { status: 403 })
        }

        return Response.json({ error: 'Internal server error' }, { status: 500 })
      }
    }
  }
}
```

### Using withAuth

```typescript
// src/app/api/projects/route.ts
import { withAuth } from '@/lib/auth/withAuth'
import { db } from '@/lib/db'

// ✅ Protected endpoint
export const GET = withAuth(async (request, { user }) => {
  // user is automatically available and verified

  const projects = await db.project.findMany({
    where: { userId: user.userId },
  })

  return Response.json({ projects })
})

export const POST = withAuth(async (request, { user }) => {
  const data = await request.json()

  const project = await db.project.create({
    data: {
      ...data,
      userId: user.userId,  // Automatically associate with user
    },
  })

  return Response.json({ project }, { status: 201 })
})

// ✅ Admin-only endpoint
import { withRole } from '@/lib/auth/withAuth'
import { ROLES } from '@/lib/auth/roles'

export const DELETE = withRole([ROLES.ADMIN])(async (request, { user, params }) => {
  const { id } = params

  await db.project.delete({ where: { id } })

  return Response.json({ success: true })
})
```

---

## Server Action Protection

### Protected Server Actions

```typescript
// src/app/actions/projects.ts
'use server'

import { revalidatePath } from 'next/cache'
import { requireAuth, requireRole } from '@/lib/auth/authorization'
import { db } from '@/lib/db'
import { ROLES } from '@/lib/auth/roles'

// ✅ Create project (authenticated users)
export async function createProject(formData: FormData) {
  const user = await requireAuth()

  const name = formData.get('name') as string
  const description = formData.get('description') as string

  const project = await db.project.create({
    data: {
      name,
      description,
      userId: user.userId,
    },
  })

  revalidatePath('/projects')

  return { success: true, project }
}

// ✅ Update project (owner only)
export async function updateProject(projectId: string, formData: FormData) {
  const user = await requireAuth()

  // Check ownership
  const project = await db.project.findUnique({
    where: { id: projectId },
  })

  if (!project) {
    throw new Error('Project not found')
  }

  if (project.userId !== user.userId && user.role !== ROLES.ADMIN) {
    throw new Error('Forbidden')
  }

  const updated = await db.project.update({
    where: { id: projectId },
    data: {
      name: formData.get('name') as string,
      description: formData.get('description') as string,
    },
  })

  revalidatePath(`/projects/${projectId}`)

  return { success: true, project: updated }
}

// ✅ Delete project (admin only)
export async function deleteProject(projectId: string) {
  await requireRole([ROLES.ADMIN])

  await db.project.delete({
    where: { id: projectId },
  })

  revalidatePath('/projects')
  revalidatePath('/admin/projects')

  return { success: true }
}
```

---

## Row-Level Security

### Drizzle ORM with RLS

```typescript
// src/lib/db/rls.ts
import { and, eq, or } from 'drizzle-orm'
import { db } from '@/lib/db'
import { projects, users } from '@/lib/db/schema'
import { getCurrentUser } from '@/lib/auth/jwt'

// ✅ Get projects with row-level security
export async function getProjectsRLS() {
  const user = await getCurrentUser()

  if (!user) {
    // Public projects only
    return db.select()
      .from(projects)
      .where(eq(projects.visibility, 'public'))
  }

  if (user.role === 'ADMIN') {
    // Admins see everything
    return db.select().from(projects)
  }

  // Users see: own projects + public + organization projects
  return db.select()
    .from(projects)
    .where(
      or(
        eq(projects.userId, user.userId),  // Own projects
        eq(projects.visibility, 'public'),  // Public projects
        and(
          eq(projects.visibility, 'organization'),
          eq(projects.organizationId, user.organizationId!)
        )  // Organization projects
      )
    )
}

// ✅ Get single project with RLS
export async function getProjectByIdRLS(projectId: string) {
  const user = await getCurrentUser()

  const project = await db.select()
    .from(projects)
    .where(eq(projects.id, projectId))
    .limit(1)

  if (project.length === 0) {
    return null
  }

  const p = project[0]

  // Check access
  if (!user) {
    return p.visibility === 'public' ? p : null
  }

  if (user.role === 'ADMIN') {
    return p
  }

  if (p.userId === user.userId) {
    return p
  }

  if (p.visibility === 'public') {
    return p
  }

  if (p.visibility === 'organization' && p.organizationId === user.organizationId) {
    return p
  }

  return null
}

// ✅ Update project with RLS
export async function updateProjectRLS(projectId: string, data: any) {
  const user = await getCurrentUser()

  if (!user) {
    throw new Error('Unauthorized')
  }

  const project = await getProjectByIdRLS(projectId)

  if (!project) {
    throw new Error('Not found')
  }

  // Only owner or admin can update
  if (project.userId !== user.userId && user.role !== 'ADMIN') {
    throw new Error('Forbidden')
  }

  return db.update(projects)
    .set(data)
    .where(eq(projects.id, projectId))
}

// ✅ Delete project with RLS
export async function deleteProjectRLS(projectId: string) {
  const user = await getCurrentUser()

  if (!user) {
    throw new Error('Unauthorized')
  }

  const project = await getProjectByIdRLS(projectId)

  if (!project) {
    throw new Error('Not found')
  }

  // Only owner or admin can delete
  if (project.userId !== user.userId && user.role !== 'ADMIN') {
    throw new Error('Forbidden')
  }

  return db.delete(projects).where(eq(projects.id, projectId))
}
```

---

## Permission System

### Fine-Grained Permissions

```typescript
// src/lib/auth/permissions.ts
import { db } from '@/lib/db'

export interface Permission {
  resource: string  // e.g., 'project', 'user', 'settings'
  action: string    // e.g., 'read', 'create', 'update', 'delete'
  scope?: string    // e.g., 'own', 'organization', 'all'
}

// ✅ Check user permission
export async function hasUserPermission(
  userId: string,
  permission: Permission
): Promise<boolean> {
  const userPermission = await db.userPermission.findFirst({
    where: {
      userId,
      resource: permission.resource,
      action: permission.action,
      scope: permission.scope || 'own',
    },
  })

  return !!userPermission
}

// ✅ Grant permission to user
export async function grantPermission(userId: string, permission: Permission) {
  return db.userPermission.create({
    data: {
      userId,
      resource: permission.resource,
      action: permission.action,
      scope: permission.scope || 'own',
    },
  })
}

// ✅ Revoke permission from user
export async function revokePermission(userId: string, permission: Permission) {
  return db.userPermission.deleteMany({
    where: {
      userId,
      resource: permission.resource,
      action: permission.action,
      scope: permission.scope || 'own',
    },
  })
}

// ✅ Get all user permissions
export async function getUserPermissions(userId: string): Promise<Permission[]> {
  const permissions = await db.userPermission.findMany({
    where: { userId },
  })

  return permissions.map((p) => ({
    resource: p.resource,
    action: p.action,
    scope: p.scope,
  }))
}

// ✅ Check resource-level permission
export async function canAccessResource(
  userId: string,
  resourceType: string,
  resourceId: string,
  action: string
): Promise<boolean> {
  // Check if user has 'all' scope permission
  const hasAllScope = await hasUserPermission(userId, {
    resource: resourceType,
    action,
    scope: 'all',
  })

  if (hasAllScope) {
    return true
  }

  // Check if user has 'organization' scope permission
  const hasOrgScope = await hasUserPermission(userId, {
    resource: resourceType,
    action,
    scope: 'organization',
  })

  if (hasOrgScope) {
    // Verify resource belongs to user's organization
    const resource = await db[resourceType].findUnique({
      where: { id: resourceId },
      select: { organizationId: true },
    })

    const user = await db.user.findUnique({
      where: { id: userId },
      select: { organizationId: true },
    })

    if (resource?.organizationId === user?.organizationId) {
      return true
    }
  }

  // Check if user has 'own' scope permission
  const hasOwnScope = await hasUserPermission(userId, {
    resource: resourceType,
    action,
    scope: 'own',
  })

  if (hasOwnScope) {
    // Verify resource belongs to user
    const resource = await db[resourceType].findUnique({
      where: { id: resourceId },
      select: { userId: true },
    })

    return resource?.userId === userId
  }

  return false
}
```

---

## Resource Ownership

### Ownership Verification

```typescript
// src/lib/auth/ownership.ts
import { db } from '@/lib/db'
import { getCurrentUser } from './jwt'

// ✅ Verify project ownership
export async function verifyProjectOwnership(projectId: string): Promise<boolean> {
  const user = await getCurrentUser()

  if (!user) {
    return false
  }

  // Admins can access all projects
  if (user.role === 'ADMIN') {
    return true
  }

  const project = await db.project.findUnique({
    where: { id: projectId },
    select: { userId: true },
  })

  return project?.userId === user.userId
}

// ✅ Require project ownership
export async function requireProjectOwnership(projectId: string) {
  const isOwner = await verifyProjectOwnership(projectId)

  if (!isOwner) {
    throw new Error('Forbidden')
  }
}

// ✅ Get owned projects
export async function getOwnedProjects() {
  const user = await getCurrentUser()

  if (!user) {
    return []
  }

  return db.project.findMany({
    where: { userId: user.userId },
  })
}

// ✅ Transfer ownership
export async function transferProjectOwnership(
  projectId: string,
  newOwnerId: string
) {
  await requireProjectOwnership(projectId)

  return db.project.update({
    where: { id: projectId },
    data: { userId: newOwnerId },
  })
}
```

---

## Summary

**Authorization checklist:**

- [ ] RBAC implemented with clear roles
- [ ] Permissions defined for each role
- [ ] Authorization checks on ALL protected routes
- [ ] Middleware protection configured
- [ ] API routes wrapped with withAuth/withRole
- [ ] Server Actions require authentication
- [ ] Row-level security enforced in database queries
- [ ] Ownership verified before updates/deletes
- [ ] Admin actions logged for audit trail
- [ ] Forbidden (403) returned for insufficient permissions
- [ ] Unauthorized (401) returned for missing authentication
