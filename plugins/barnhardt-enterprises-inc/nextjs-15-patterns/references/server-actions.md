# Server Actions Reference

## Basic Pattern

```typescript
// actions/post-actions.ts
'use server';

import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';
import { z } from 'zod';

const PostSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(1),
});

export async function createPost(formData: FormData) {
  // 1. Validate
  const validated = PostSchema.safeParse({
    title: formData.get('title'),
    content: formData.get('content'),
  });

  if (!validated.success) {
    return { error: validated.error.flatten().fieldErrors };
  }

  // 2. Mutate
  const post = await db.insert(posts).values(validated.data).returning();

  // 3. Revalidate
  revalidatePath('/posts');

  // 4. Redirect (optional)
  redirect(`/posts/${post.id}`);
}
```

## With useActionState (React 19)

```typescript
// components/post-form.tsx
'use client';

import { useActionState } from 'react';
import { createPost } from '@/actions/post-actions';

export function PostForm() {
  const [state, action, pending] = useActionState(createPost, null);

  return (
    <form action={action}>
      <input name="title" />
      {state?.error?.title && <p>{state.error.title}</p>}

      <textarea name="content" />
      {state?.error?.content && <p>{state.error.content}</p>}

      <button disabled={pending}>
        {pending ? 'Creating...' : 'Create Post'}
      </button>
    </form>
  );
}
```

## Optimistic Updates

```typescript
'use client';

import { useOptimistic } from 'react';
import { likePost } from '@/actions/post-actions';

export function LikeButton({ likes }: { likes: number }) {
  const [optimisticLikes, addOptimisticLike] = useOptimistic(
    likes,
    (state) => state + 1
  );

  async function handleLike() {
    addOptimisticLike(null);
    await likePost();
  }

  return (
    <button onClick={handleLike}>
      {optimisticLikes} likes
    </button>
  );
}
```

## Error Handling

```typescript
'use server';

type ActionResult<T> =
  | { success: true; data: T }
  | { success: false; error: string };

export async function safeAction(): Promise<ActionResult<Post>> {
  try {
    const post = await createPost();
    return { success: true, data: post };
  } catch (error: unknown) {
    if (error instanceof DatabaseError) {
      return { success: false, error: 'Database error occurred' };
    }
    return { success: false, error: 'Unknown error' };
  }
}
```
