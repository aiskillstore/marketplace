# Server Action Handler Reference

Complete backend pattern for handling widget actions.

## Full Action Handler Implementation

```python
from chatkit.server import ChatKitServer
from chatkit.types import (
    Action,
    WidgetItem,
    ThreadMetadata,
    ThreadItemReplacedEvent,
    ThreadItemDoneEvent,
    AssistantMessageItem,
    HiddenContextItem,
    ClientEffectEvent,
    UserMessageItem,
    UserMessageTextContent,
)
from datetime import datetime
from typing import Any, AsyncIterator

class MyServer(ChatKitServer[RequestContext]):

    async def action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        sender: WidgetItem | None,
        context: RequestContext,  # Already RequestContext, not dict!
    ) -> AsyncIterator[ThreadStreamEvent]:
        """Handle widget actions.

        CRITICAL NOTES:
        - context is RequestContext, not dict (type hint is misleading)
        - Use action.payload, not action.arguments
        - Include all required fields in UserMessageItem
        """

        if action.type == "item.select":
            item_id = action.payload["id"]

            # 1. Update widget with selection state
            updated_widget = build_selector_widget(
                items=self.items,
                selected=item_id,
            )
            yield ThreadItemReplacedEvent(
                item=sender.model_copy(update={"widget": updated_widget})
            )

            # 2. Add hidden context for future agent input
            await self.store.add_thread_item(
                thread.id,
                HiddenContextItem(
                    id=self.store.generate_item_id("ctx", thread, context),
                    thread_id=thread.id,
                    created_at=datetime.now(),
                    content=f"<SELECTED>{item_id}</SELECTED>",
                ),
                context=context,
            )

            # 3. Stream assistant response
            yield ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    id=self.store.generate_item_id("msg", thread, context),
                    thread_id=thread.id,
                    created_at=datetime.now(),
                    content=[{"text": f"Selected {item_id}. What next?"}],
                )
            )

            # 4. Trigger client effect
            yield ClientEffectEvent(
                name="selection_mode",
                data={"itemId": item_id},
            )

        elif action.type == "form.submit":
            form_data = action.payload

            # Process form submission
            result = await process_form(form_data)

            # Create synthetic user message to trigger agent
            synthetic_message = UserMessageItem(
                id=self.store.generate_item_id("message", thread, context),
                thread_id=thread.id,
                created_at=datetime.now(),
                content=[
                    UserMessageTextContent(
                        type="input_text",  # Must be "input_text", not "text"
                        text=f"Form submitted: {result.summary}"
                    )
                ],
                inference_options={},  # Required field
            )

            # Run agent with synthetic message
            async for event in self.respond(thread, synthetic_message, context):
                yield event

        elif action.type == "confirm.accept":
            # Handle confirmation action
            item_id = action.payload["item_id"]

            # Update database
            await self.db.confirm_item(item_id)

            # Replace widget with success state
            success_widget = build_success_widget(item_id)
            yield ThreadItemReplacedEvent(
                item=sender.model_copy(update={"widget": success_widget})
            )

            # Notify client
            yield ClientEffectEvent(
                name="item_confirmed",
                data={"itemId": item_id},
            )
```

## Action Type Definition

```python
from chatkit.types import Action

# Action[str, Any] has these fields:
action.type      # str - action identifier (e.g., "task.start")
action.payload   # dict[str, Any] - action data
action.handler   # "client" | "server" - where processed
```

## Common Patterns

### Selection Actions

```python
if action.type.endswith(".select"):
    entity_id = action.payload["id"]

    # Update widget
    yield ThreadItemReplacedEvent(
        item=sender.model_copy(update={
            "widget": build_widget(selected=entity_id)
        })
    )
```

### Form Actions

```python
if action.type == "form.submit":
    # Create synthetic message
    message = UserMessageItem(
        id=self.store.generate_item_id("message", thread, context),
        thread_id=thread.id,
        created_at=datetime.now(),
        content=[UserMessageTextContent(type="input_text", text="...")],
        inference_options={},
    )

    # Run agent
    async for event in self.respond(thread, message, context):
        yield event
```

### Confirmation Actions

```python
if action.type == "confirm":
    # Perform action
    await self.do_action(action.payload)

    # Replace widget
    yield ThreadItemReplacedEvent(
        item=sender.model_copy(update={
            "widget": build_success_widget()
        })
    )
```

## Error Handling

```python
async def action(self, thread, action, sender, context):
    try:
        if action.type == "dangerous.action":
            # Validate
            if not self.can_perform(action, context):
                yield ThreadItemDoneEvent(
                    item=AssistantMessageItem(
                        id=self.store.generate_item_id("msg", thread, context),
                        thread_id=thread.id,
                        created_at=datetime.now(),
                        content=[{"text": "Permission denied."}],
                    )
                )
                return

            # Proceed
            ...

    except Exception as e:
        # Log error
        logger.error(f"Action failed: {e}")

        # Notify user
        yield ThreadItemDoneEvent(
            item=AssistantMessageItem(
                id=self.store.generate_item_id("msg", thread, context),
                thread_id=thread.id,
                created_at=datetime.now(),
                content=[{"text": f"Action failed: {str(e)}"}],
            )
        )
```