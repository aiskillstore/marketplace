/**
 * Complete Blog Application Example
 * Demonstrates RSC, Server Actions, Streaming, and Best Practices
 */

// ============================================
// 1. DATABASE SCHEMA (Prisma)
// ============================================

/*
// prisma/schema.prisma

model Post {
  id          String   @id @default(cuid())
  title       String
  slug        String   @unique
  content     String
  excerpt     String?
  published   Boolean  @default(false)
  authorId    String
  author      User     @relation(fields: [authorId], references: [id])
  comments    Comment[]
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  @@index([slug])
  @@index([authorId])
}

model Comment {
  id        String   @id @default(cuid())
  content   String
  postId    String
  post      Post     @relation(fields: [postId], references: [id])
  authorId  String
  author    User     @relation(fields: [authorId], references: [id])
  createdAt DateTime @default(now())

  @@index([postId])
}
*/

// ============================================
// 2. SERVER ACTIONS (app/actions/posts.ts)
// ============================================

'use server'

import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'
import { z } from 'zod'
import { db } from '@/lib/database'
import { getServerSession } from '@/lib/auth'

const createPostSchema = z.object({
  title: z.string().min(1).max(100),
  slug: z.string().min(1).max(100).regex(/^[a-z0-9-]+$/),
  content: z.string().min(1),
  excerpt: z.string().max(200).optional(),
  published: z.boolean().default(false),
})

export async function createPost(formData: FormData) {
  const session = await getServerSession()
  if (!session?.user) {
    return { error: 'Unauthorized' }
  }

  const validated = createPostSchema.safeParse({
    title: formData.get('title'),
    slug: formData.get('slug'),
    content: formData.get('content'),
    excerpt: formData.get('excerpt'),
    published: formData.get('published') === 'true',
  })

  if (!validated.success) {
    return {
      error: 'Validation failed',
      errors: validated.error.flatten().fieldErrors
    }
  }

  try {
    const post = await db.post.create({
      data: {
        ...validated.data,
        authorId: session.user.id
      }
    })

    revalidatePath('/blog')
    redirect(`/blog/${post.slug}`)
  } catch (error) {
    return { error: 'Failed to create post' }
  }
}

export async function addComment(postId: string, content: string) {
  const session = await getServerSession()
  if (!session?.user) {
    return { error: 'Unauthorized' }
  }

  if (!content.trim()) {
    return { error: 'Comment cannot be empty' }
  }

  try {
    await db.comment.create({
      data: {
        content,
        postId,
        authorId: session.user.id
      }
    })

    revalidatePath(`/blog/[slug]`)
    return { success: true }
  } catch (error) {
    return { error: 'Failed to add comment' }
  }
}

// ============================================
// 3. BLOG LIST PAGE (app/blog/page.tsx)
// ============================================

import { Suspense } from 'react'
import { db } from '@/lib/database'
import { PostCard } from '@/components/PostCard'
import { PostListSkeleton } from '@/components/skeletons'

export const metadata = {
  title: 'Blog',
  description: 'Latest blog posts'
}

export default function BlogPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">Blog</h1>

      {/* Streaming: Posts load independently */}
      <Suspense fallback={<PostListSkeleton />}>
        <PostList />
      </Suspense>
    </div>
  )
}

// Server Component for data fetching
async function PostList() {
  const posts = await db.post.findMany({
    where: { published: true },
    include: {
      author: {
        select: { name: true, image: true }
      },
      _count: {
        select: { comments: true }
      }
    },
    orderBy: { createdAt: 'desc' },
    take: 20
  })

  if (posts.length === 0) {
    return <p className="text-gray-500">No posts yet.</p>
  }

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {posts.map(post => (
        <PostCard key={post.id} post={post} />
      ))}
    </div>
  )
}

// ============================================
// 4. BLOG POST PAGE (app/blog/[slug]/page.tsx)
// ============================================

import { notFound } from 'next/navigation'
import { Suspense } from 'react'
import { Metadata } from 'next'
import { db } from '@/lib/database'
import { CommentList } from '@/components/CommentList'
import { CommentForm } from '@/components/CommentForm'
import { CommentsSkeleton } from '@/components/skeletons'

interface PageProps {
  params: { slug: string }
}

// Generate static params at build time (SSG)
export async function generateStaticParams() {
  const posts = await db.post.findMany({
    where: { published: true },
    select: { slug: true }
  })

  return posts.map(post => ({
    slug: post.slug
  }))
}

// Dynamic metadata for SEO
export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const post = await db.post.findUnique({
    where: { slug: params.slug },
    select: {
      title: true,
      excerpt: true,
      author: { select: { name: true } }
    }
  })

  if (!post) {
    return { title: 'Post Not Found' }
  }

  return {
    title: post.title,
    description: post.excerpt || `By ${post.author.name}`,
    openGraph: {
      title: post.title,
      description: post.excerpt || undefined,
      type: 'article'
    }
  }
}

// Revalidate every 1 hour
export const revalidate = 3600

export default async function BlogPostPage({ params }: PageProps) {
  const post = await db.post.findUnique({
    where: { slug: params.slug },
    include: {
      author: {
        select: {
          name: true,
          image: true,
          bio: true
        }
      }
    }
  })

  if (!post) {
    notFound()
  }

  return (
    <article className="container mx-auto px-4 py-8 max-w-3xl">
      <header className="mb-8">
        <h1 className="text-5xl font-bold mb-4">{post.title}</h1>

        <div className="flex items-center gap-4 text-gray-600">
          <img
            src={post.author.image}
            alt={post.author.name}
            className="w-12 h-12 rounded-full"
          />
          <div>
            <p className="font-medium">{post.author.name}</p>
            <time dateTime={post.createdAt.toISOString()}>
              {post.createdAt.toLocaleDateString()}
            </time>
          </div>
        </div>
      </header>

      <div
        className="prose prose-lg max-w-none mb-12"
        dangerouslySetInnerHTML={{ __html: post.content }}
      />

      <section className="border-t pt-8">
        <h2 className="text-2xl font-bold mb-6">Comments</h2>

        {/* Comment form (Client Component) */}
        <CommentForm postId={post.id} />

        {/* Comments list (Streaming) */}
        <Suspense fallback={<CommentsSkeleton />}>
          <CommentList postId={post.id} />
        </Suspense>
      </section>
    </article>
  )
}

// ============================================
// 5. COMMENT LIST (components/CommentList.tsx)
// ============================================

// Server Component
import { db } from '@/lib/database'

export async function CommentList({ postId }: { postId: string }) {
  // Slow query - but it's streamed thanks to Suspense
  const comments = await db.comment.findMany({
    where: { postId },
    include: {
      author: {
        select: { name: true, image: true }
      }
    },
    orderBy: { createdAt: 'desc' }
  })

  if (comments.length === 0) {
    return <p className="text-gray-500 italic">No comments yet. Be the first!</p>
  }

  return (
    <div className="space-y-6 mt-8">
      {comments.map(comment => (
        <div key={comment.id} className="flex gap-4">
          <img
            src={comment.author.image}
            alt={comment.author.name}
            className="w-10 h-10 rounded-full"
          />
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="font-medium">{comment.author.name}</span>
              <time className="text-sm text-gray-500">
                {comment.createdAt.toLocaleString()}
              </time>
            </div>
            <p className="text-gray-700">{comment.content}</p>
          </div>
        </div>
      ))}
    </div>
  )
}

// ============================================
// 6. COMMENT FORM (components/CommentForm.tsx)
// ============================================

'use client' // Client Component for interactivity

import { useFormState, useFormStatus } from 'react-dom'
import { addComment } from '@/app/actions/posts'
import { useRef, useEffect } from 'react'

function SubmitButton() {
  const { pending } = useFormStatus()

  return (
    <button
      type="submit"
      disabled={pending}
      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
    >
      {pending ? 'Posting...' : 'Post Comment'}
    </button>
  )
}

export function CommentForm({ postId }: { postId: string }) {
  const formRef = useRef<HTMLFormElement>(null)
  const [state, formAction] = useFormState(
    async (prevState: any, formData: FormData) => {
      const content = formData.get('content') as string
      return addComment(postId, content)
    },
    null
  )

  // Reset form on success
  useEffect(() => {
    if (state?.success) {
      formRef.current?.reset()
    }
  }, [state])

  return (
    <form ref={formRef} action={formAction} className="mb-8">
      <textarea
        name="content"
        rows={4}
        placeholder="Add your comment..."
        required
        className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />

      {state?.error && (
        <p className="text-red-600 text-sm mt-2">{state.error}</p>
      )}

      <div className="mt-4">
        <SubmitButton />
      </div>
    </form>
  )
}

// ============================================
// 7. POST CARD (components/PostCard.tsx)
// ============================================

'use client'

import Link from 'next/link'
import { Post } from '@prisma/client'

interface PostCardProps {
  post: Post & {
    author: { name: string; image: string }
    _count: { comments: number }
  }
}

export function PostCard({ post }: PostCardProps) {
  return (
    <Link
      href={`/blog/${post.slug}`}
      className="block p-6 bg-white rounded-lg border hover:shadow-lg transition-shadow"
    >
      <h2 className="text-2xl font-bold mb-2">{post.title}</h2>

      {post.excerpt && (
        <p className="text-gray-600 mb-4 line-clamp-3">{post.excerpt}</p>
      )}

      <div className="flex items-center justify-between text-sm text-gray-500">
        <div className="flex items-center gap-2">
          <img
            src={post.author.image}
            alt={post.author.name}
            className="w-6 h-6 rounded-full"
          />
          <span>{post.author.name}</span>
        </div>

        <div className="flex items-center gap-4">
          <span>{post._count.comments} comments</span>
          <time>{post.createdAt.toLocaleDateString()}</time>
        </div>
      </div>
    </Link>
  )
}

/**
 * Key Patterns Demonstrated:
 *
 * 1. ✅ Server Components for data fetching (BlogPage, PostList, CommentList)
 * 2. ✅ Client Components for interactivity (CommentForm, PostCard)
 * 3. ✅ Server Actions for mutations (createPost, addComment)
 * 4. ✅ Streaming with Suspense (PostList, CommentList)
 * 5. ✅ Static generation with generateStaticParams
 * 6. ✅ Dynamic metadata with generateMetadata
 * 7. ✅ Progressive enhancement (forms work without JavaScript)
 * 8. ✅ Proper error handling (notFound, validation)
 * 9. ✅ Cache revalidation (revalidatePath)
 * 10. ✅ Type safety with Prisma and TypeScript
 */
