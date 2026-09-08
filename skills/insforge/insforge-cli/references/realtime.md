# Realtime Backend Configuration

Use migrations to create realtime channel patterns, publish database changes, and restrict channel access before wiring frontend subscriptions.

## Create Channel Patterns

```sql
INSERT INTO realtime.channels (pattern, description, enabled)
VALUES ('order:%', 'Per-order updates', true)
ON CONFLICT (pattern) DO UPDATE
SET description = EXCLUDED.description,
    enabled = EXCLUDED.enabled;
```

## Publish From App-Owned Tables

Attach triggers to app-owned tables, then call `realtime.publish(...)` from the trigger function.

```sql
CREATE OR REPLACE FUNCTION public.notify_order_status()
RETURNS TRIGGER AS $$
BEGIN
  PERFORM realtime.publish(
    'order:' || NEW.id::text,
    'status_changed',
    jsonb_build_object('id', NEW.id, 'status', NEW.status)
  );

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER order_status_trigger
AFTER UPDATE ON public.orders
FOR EACH ROW
WHEN (OLD.status IS DISTINCT FROM NEW.status)
EXECUTE FUNCTION public.notify_order_status();
```

## Restrict Channel Access

`realtime.channels` and `realtime.messages` can be managed with RLS. Put those policies in migrations.

Restrict who can subscribe to order channels:

```sql
ALTER TABLE realtime.channels ENABLE ROW LEVEL SECURITY;

CREATE POLICY users_subscribe_own_orders
ON realtime.channels FOR SELECT
TO authenticated
USING (
  pattern = 'order:%'
  AND EXISTS (
    SELECT 1 FROM public.orders
    WHERE id = NULLIF(split_part(realtime.channel_name(), ':', 2), '')::uuid
      AND user_id = (SELECT auth.uid())
  )
);
```

Restrict who can publish chat messages:

```sql
ALTER TABLE realtime.messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY members_publish_chat
ON realtime.messages FOR INSERT
TO authenticated
WITH CHECK (
  channel_name LIKE 'chat:%'
  AND EXISTS (
    SELECT 1 FROM public.chat_members
    WHERE room_id = NULLIF(split_part(channel_name, ':', 2), '')::uuid
      AND user_id = (SELECT auth.uid())
  )
);
```

Do not attach developer triggers to `realtime.channels` or `realtime.messages`; publish from triggers on `public` tables.
