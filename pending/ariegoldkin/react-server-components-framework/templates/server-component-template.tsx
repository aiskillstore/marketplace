// Server Component Template
// NO 'use client' directive - this is a Server Component by default

import { db } from '@/lib/database'
import { Suspense } from 'react'

/**
 * Server Component Example
 *
 * Characteristics:
 * - Async function
 * - Direct database/API access
 * - No hooks (useState, useEffect, etc.)
 * - No browser APIs (window, document, etc.)
 * - Zero JavaScript sent to client
 */

interface PageProps {
  params: { id: string }
  searchParams: { [key: string]: string | string[] | undefined }
}

export default async function ServerComponentTemplate({ params, searchParams }: PageProps) {
  // ✅ Server-only data fetching
  const data = await db.resource.findMany({
    where: { categoryId: params.id }
  })

  // ✅ Can use environment variables directly
  const apiKey = process.env.SECRET_API_KEY

  return (
    <div>
      <h1>Server Component</h1>

      {/* ✅ Render data directly */}
      <div>
        {data.map(item => (
          <div key={item.id}>{item.name}</div>
        ))}
      </div>

      {/* ✅ Can include Client Components */}
      <InteractiveClientComponent data={data} />

      {/* ✅ Use Suspense for streaming */}
      <Suspense fallback={<LoadingSkeleton />}>
        <SlowDataComponent />
      </Suspense>
    </div>
  )
}

// ✅ Generate static params for static generation
export async function generateStaticParams() {
  const categories = await db.category.findMany()

  return categories.map(category => ({
    id: category.id
  }))
}

// ✅ Generate metadata for SEO
export async function generateMetadata({ params }: PageProps) {
  const category = await db.category.findUnique({
    where: { id: params.id }
  })

  return {
    title: category?.name,
    description: category?.description
  }
}

// ✅ Route segment config
export const revalidate = 3600 // Revalidate every hour
export const dynamic = 'auto' // or 'force-static' | 'force-dynamic'
