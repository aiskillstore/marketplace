// Server Actions Template
'use server' // ⚠️ REQUIRED for Server Actions

import { revalidatePath, revalidateTag } from 'next/cache'
import { redirect } from 'next/navigation'
import { z } from 'zod' // Recommended for validation
import { db } from '@/lib/database'

/**
 * Server Actions are asynchronous functions that run on the server
 *
 * Characteristics:
 * - MUST have 'use server' directive
 * - Can be called from Server or Client Components
 * - Automatically create POST endpoints
 * - Type-safe with TypeScript
 * - Support progressive enhancement (work without JavaScript)
 */

// ========================================
// Form Action Pattern (Progressive Enhancement)
// ========================================

const createResourceSchema = z.object({
  title: z.string().min(1).max(100),
  description: z.string().min(1).max(500),
  category: z.string(),
})

export async function createResource(formData: FormData) {
  // 1. Extract and validate data
  const rawData = {
    title: formData.get('title'),
    description: formData.get('description'),
    category: formData.get('category'),
  }

  const validated = createResourceSchema.safeParse(rawData)

  if (!validated.success) {
    return {
      error: 'Invalid data',
      errors: validated.error.flatten().fieldErrors
    }
  }

  try {
    // 2. Perform server-side mutation
    const resource = await db.resource.create({
      data: validated.data
    })

    // 3. Revalidate cached data
    revalidatePath('/resources')
    revalidateTag('resources')

    // 4. Redirect to new resource
    redirect(`/resources/${resource.id}`)
  } catch {
    console.error('Database error:', error)
    return {
      error: 'Failed to create resource'
    }
  }
}

// ========================================
// Programmatic Action Pattern (Client Component)
// ========================================

export async function updateResource(id: string, data: Partial<Resource>) {
  try {
    // Authorization check
    const session = await getSession()
    if (!session?.user) {
      throw new Error('Unauthorized')
    }

    // Validate ownership
    const resource = await db.resource.findUnique({
      where: { id }
    })

    if (resource.userId !== session.user.id) {
      throw new Error('Forbidden')
    }

    // Update
    const updated = await db.resource.update({
      where: { id },
      data
    })

    // Revalidate
    revalidatePath(`/resources/${id}`)

    return { success: true, data: updated }
  } catch {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to update'
    }
  }
}

// ========================================
// Delete Action Pattern
// ========================================

export async function deleteResource(id: string) {
  try {
    await db.resource.delete({
      where: { id }
    })

    revalidatePath('/resources')
    return { success: true }
  } catch {
    return {
      success: false,
      error: 'Failed to delete resource'
    }
  }
}

// ========================================
// Optimistic Update Pattern
// ========================================

export async function toggleComplete(id: string) {
  const todo = await db.todo.findUnique({
    where: { id }
  })

  if (!todo) {
    throw new Error('Todo not found')
  }

  await db.todo.update({
    where: { id },
    data: { completed: !todo.completed }
  })

  revalidatePath('/todos')
}

// ========================================
// Bulk Operation Pattern
// ========================================

export async function bulkUpdateResources(ids: string[], data: Partial<Resource>) {
  try {
    await db.resource.updateMany({
      where: {
        id: { in: ids }
      },
      data
    })

    revalidatePath('/resources')
    return { success: true, count: ids.length }
  } catch {
    return {
      success: false,
      error: 'Failed to bulk update'
    }
  }
}

// ========================================
// File Upload Pattern
// ========================================

export async function uploadFile(formData: FormData) {
  const file = formData.get('file') as File

  if (!file) {
    return { error: 'No file provided' }
  }

  // Validate file type and size
  if (!file.type.startsWith('image/')) {
    return { error: 'Only images are allowed' }
  }

  if (file.size > 5 * 1024 * 1024) { // 5MB
    return { error: 'File too large (max 5MB)' }
  }

  try {
    // Convert to buffer and upload to storage
    const bytes = await file.arrayBuffer()
    const buffer = Buffer.from(bytes)

    // Upload to S3, Cloudflare R2, etc.
    const url = await uploadToStorage(buffer, file.name)

    // Save to database
    const upload = await db.upload.create({
      data: {
        filename: file.name,
        url,
        size: file.size,
        mimeType: file.type
      }
    })

    revalidatePath('/uploads')
    return { success: true, url: upload.url }
  } catch {
    return { error: 'Failed to upload file' }
  }
}

// ========================================
// Revalidation Patterns
// ========================================

// Revalidate specific path
export async function revalidateResourcePath(id: string) {
  revalidatePath(`/resources/${id}`)
}

// Revalidate all pages under a path
export async function revalidateAllResources() {
  revalidatePath('/resources', 'layout') // Revalidates layout + all children
}

// Revalidate by tag
export async function revalidateResourceTag() {
  revalidateTag('resources')
}

// Clear all cache and force dynamic
export async function forceRevalidate() {
  revalidatePath('/', 'layout') // Revalidates entire app
}

/**
 * Best Practices for Server Actions:
 *
 * 1. Always validate input data (use Zod or similar)
 * 2. Check authorization before mutations
 * 3. Use try-catch for error handling
 * 4. Return structured responses { success, data?, error? }
 * 5. Revalidate affected paths/tags after mutations
 * 6. Use redirect() only after successful mutations
 * 7. Keep actions focused and single-purpose
 * 8. Use TypeScript for type safety
 */
