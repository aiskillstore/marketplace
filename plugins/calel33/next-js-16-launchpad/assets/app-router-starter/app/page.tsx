import Link from 'next/link'
import { Suspense } from 'react'

async function fetchPosts() {
  'use cache'
  const data = await fetch('https://jsonplaceholder.typicode.com/posts?_limit=3', {
    next: { revalidate: 3600 },
  })
  return data.json()
}

async function FeaturedPosts() {
  const posts = await fetchPosts()
  return (
    <ul className="space-y-3">
      {posts.map((post: { id: number; title: string }) => (
        <li key={post.id} className="rounded border border-gray-200 p-4">
          <h3 className="font-medium">{post.title}</h3>
        </li>
      ))}
    </ul>
  )
}

export default function Page() {
  return (
    <div className="space-y-6">
      <section className="space-y-2">
        <h2 className="text-2xl font-semibold">Ready for Turbopack</h2>
        <p className="text-gray-600">
          This starter uses Server Components by default, Cache Components for predictable freshness,
          and a Suspense boundary for streaming.
        </p>
      </section>

      <Suspense fallback={<p className="text-gray-500">Loading featured posts...</p>}>
        {/* Cached content, streamed when ready */}
        <FeaturedPosts />
      </Suspense>

      <Link
        href="/dashboard"
        className="inline-flex items-center gap-2 rounded border border-gray-300 px-4 py-2 text-sm font-medium"
      >
        Go to dashboard
      </Link>
    </div>
  )
}
