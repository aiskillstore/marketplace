# Streaming Patterns Reference

Complete useChatKit configuration with all streaming handlers.

## Full Configuration

```typescript
import { useChatKit } from "@openai/chatkit-react";

const chatkit = useChatKit({
  api: { url: API_URL, domainKey: DOMAIN_KEY },

  // === Lifecycle Events ===
  onReady: () => {
    console.log("ChatKit initialized");
  },

  onError: ({ error }) => {
    console.error("ChatKit error:", error);
    setIsResponding(false);
    unlockInteraction();
  },

  onResponseStart: () => {
    setIsResponding(true);
    lockInteraction();
  },

  onResponseEnd: () => {
    setIsResponding(false);
    unlockInteraction();
  },

  // === Thread Events ===
  onThreadChange: ({ threadId }) => {
    setThreadId(threadId);
    if (threadId) localStorage.setItem("lastThreadId", threadId);
    clearSelections();
  },

  onThreadLoadStart: ({ threadId }) => {
    console.log("Loading thread:", threadId);
    setIsLoadingThread(true);
  },

  onThreadLoadEnd: ({ threadId }) => {
    console.log("Thread loaded:", threadId);
    setIsLoadingThread(false);
  },

  // === Client Interaction ===
  onEffect: ({ name, data }) => {
    switch (name) {
      case "update_status":
        applyStatusUpdate(data.state);
        if (data.flash) setFlashMessage(data.flash);
        break;

      case "add_marker":
        addMapMarker(data);
        break;

      case "pan_to":
        panToLocation(data.location);
        break;

      case "select_mode":
        setSelectionMode(data.mode);
        break;

      case "show_notification":
        showToast(data.message);
        break;
    }
  },

  onClientTool: ({ name, params }) => {
    switch (name) {
      case "get_selected_items":
        return { itemIds: selectedItemIds };

      case "get_current_viewport":
        return {
          center: mapRef.current.getCenter(),
          zoom: mapRef.current.getZoom(),
        };

      case "get_form_data":
        return { values: formRef.current.getValues() };

      default:
        throw new Error(`Unknown client tool: ${name}`);
    }
  },

  // === Analytics ===
  onLog: ({ name, data }) => {
    if (name === "message.feedback") {
      trackFeedback(data);
    }
    if (name === "message.share") {
      trackShare(data);
    }
  },
});
```

## Effect Catalog

Common effect types and their handling:

| Effect Name | Data Shape | UI Action |
|-------------|------------|-----------|
| `update_status` | `{ state: {...}, flash?: string }` | Update state store, show toast |
| `add_marker` | `{ lat, lng, label }` | Add map marker |
| `pan_to` | `{ location: [lat, lng] }` | Pan map to location |
| `select_mode` | `{ mode: string, lineId?: string }` | Enable selection mode |
| `show_notification` | `{ message: string, type?: string }` | Show toast notification |
| `update_entity` | `{ id, ...props }` | Update entity in store |
| `clear_selection` | `{}` | Clear current selection |

## Backend Effect Emission

```python
from chatkit.types import ClientEffectEvent, ProgressUpdateEvent

async def respond(self, thread, item, context):
    # Progress updates during processing
    yield ProgressUpdateEvent(message="Starting analysis...")

    # Do work
    result = await process_request(item.content)

    yield ProgressUpdateEvent(message="Finalizing...")

    # Fire client effect
    yield ClientEffectEvent(
        name="update_status",
        data={
            "state": result.state,
            "flash": "Analysis complete!"
        }
    )

    # Another effect
    yield ClientEffectEvent(
        name="pan_to",
        data={"location": result.location}
    )
```

## Client Tool Implementation

Client tools allow the AI to query client-side state:

```python
from agents import function_tool
from chatkit.types import ProgressUpdateEvent

@function_tool(name_override="get_viewport_bounds")
async def get_viewport_bounds(ctx: AgentContext) -> dict:
    """Get the current map viewport bounds.

    Returns the northeast and southwest corners of the visible area.
    """
    yield ProgressUpdateEvent(message="Reading viewport...")
    # The actual execution happens on the client
    # The return type documents expected response shape
    pass


@function_tool(name_override="get_selected_features")
async def get_selected_features(ctx: AgentContext) -> list:
    """Get the currently selected map features.

    Returns a list of feature IDs that the user has selected.
    """
    yield ProgressUpdateEvent(message="Reading selection...")
    pass
```

## Error Handling

Always unlock UI on error:

```typescript
onError: ({ error }) => {
  console.error("ChatKit error:", error);

  // Always unlock UI
  setIsResponding(false);
  unlockInteraction();

  // Show user-friendly error
  showErrorToast("Something went wrong. Please try again.");

  // Optionally report to monitoring
  reportError(error);
},
```

## Evidence Sources

Patterns derived from:
- `cat-lounge/backend/app/cat_agent.py`
- `cat-lounge/frontend/src/components/ChatKitPanel.tsx`
- `metro-map/backend/app/agents/metro_map_agent.py`
- `metro-map/frontend/src/components/ChatKitPanel.tsx`
- `news-guide/backend/app/agents/news_agent.py`
- `news-guide/backend/app/agents/title_agent.py`