# Chat Completions

Use OpenRouter chat completions for chatbot responses, summarization,
classification, and structured text. Use InsForge for sessions, messages,
permissions, audit history, and realtime UI updates.

Official OpenRouter references:

- [Chat completions](https://openrouter.ai/docs/api-reference/chat-completion)
- [OpenAI SDK with OpenRouter](https://openrouter.ai/docs/guides/community/openai-sdk)
- [Parameters](https://openrouter.ai/docs/api-reference/parameters)
- [Streaming](https://openrouter.ai/docs/api-reference/streaming)

## Setup

Start with [overview.md](overview.md): run `npx -y @insforge/cli ai setup`, keep
`OPENROUTER_API_KEY` server-side, and initialize the OpenAI SDK with
`baseURL: 'https://openrouter.ai/api/v1'`.

## Store a Response

For a chatbot app, keep session/message rows in InsForge and protect them with
RLS. In a server route/action, insert the user message, call OpenRouter, then
insert the assistant response. Derive ownership from the authenticated
server-side context or enforce it through the parent chat session's RLS policy;
never trust a browser-supplied `user_id`. InsForge database inserts use array
format.

```typescript
type ChatRole = 'system' | 'user' | 'assistant'

async function sendChatMessage(sessionId: string, content: string) {
  const { data: userData, error: userError } = await insforge.auth.getCurrentUser()
  if (userError || !userData?.user?.id) {
    throw userError ?? new Error('Authentication required')
  }

  const history = await insforge.database
    .from('chat_messages')
    .select('role, content')
    .eq('session_id', sessionId)
    .order('created_at', { ascending: true })

  if (history.error) {
    throw history.error
  }

  const { error: userInsertError } = await insforge.database
    .from('chat_messages')
    .insert([{
      session_id: sessionId,
      user_id: userData.user.id,
      role: 'user',
      content,
    }])

  if (userInsertError) {
    throw userInsertError
  }

  const previousMessages = (history.data ?? []).map((message: {
    role: ChatRole
    content: string
  }) => ({
    role: message.role,
    content: message.content,
  }))

  const completion = await openai.chat.completions.create({
    model: process.env.OPENROUTER_CHAT_MODEL ?? 'openai/gpt-4o',
    messages: [
      { role: 'system', content: 'Answer clearly and stay on topic.' },
      ...previousMessages,
      { role: 'user', content },
    ],
    max_completion_tokens: 500,
  })

  const answer = completion.choices[0]?.message?.content ?? ''

  const { data, error: assistantInsertError } = await insforge.database
    .from('chat_messages')
    .insert([{
      session_id: sessionId,
      user_id: userData.user.id,
      role: 'assistant',
      content: answer,
      model: completion.model,
      prompt_tokens: completion.usage?.prompt_tokens,
      completion_tokens: completion.usage?.completion_tokens,
    }])
    .select()

  if (assistantInsertError) {
    throw assistantInsertError
  }

  return data?.[0]
}
```

For streaming chat, stream tokens to the browser for UX, buffer the final
assistant text on the server, and insert one final `assistant` row when the
stream completes. Only store token-by-token deltas if the product needs replay
or detailed debugging.

## Best Practices

1. Store chat sessions and messages in InsForge, not local browser state, when
   the app needs history, sync, moderation, billing, or support debugging.
2. Use RLS on chat tables; never trust a client-supplied `user_id` without
   checking session ownership.
3. Save `model`, token usage, and error state on assistant rows for auditing and
   cost analysis.
4. For streaming, persist the final assistant message once; avoid writing every
   token unless replay is a product requirement.
5. Use InsForge Realtime to fan out newly inserted assistant messages to other
   tabs/devices if the chat UI needs live sync.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Calling OpenRouter from the browser | Route through your server so the key stays private |
| Keeping chatbot history only in React state | Store sessions/messages in InsForge and secure them with RLS |
| Inserting a single object instead of an array | Use `.insert([{ ... }])` |
| Using invented or stale model IDs | Query OpenRouter models before implementing |
| Omitting token limits in user-triggered endpoints | Set `max_completion_tokens` for predictable cost |
| Treating OpenAI SDK errors like InsForge `{ data, error }` results | OpenAI SDK calls throw; catch exceptions separately |
