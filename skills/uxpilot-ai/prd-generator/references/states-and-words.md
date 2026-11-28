# States and words

Builders and AI tools handle the happy path well and guess the rest. The state rows are where a PRD saves the most rework, so fill them for every screen.

## The five states

| State | It means | Write down |
|---|---|---|
| First use | The person has just arrived and has never done anything here | What explains the screen in one line, and the single action that gets them started |
| Empty | They have used it before, but there is nothing to show now (all done, filtered out, deleted) | Why it is empty, and the action that fills it, if any |
| Loading | The screen or a part of it is waiting for data or for an action to finish | What stays usable while it waits, and what happens if it takes longer than a stated time |
| Error | Something failed: no connection, rejected input, a server problem, no access | What happened, in plain words, and what the person can do next |
| Success | The action worked | How the person knows it worked, and where they can go next |

Add a row when it applies: **No permission** (someone who may see but not change), **Plan limit** (a free or limited account reaching its limit), **Offline** (when the product is used on the move).

First use and empty are different rows. A person who has never added anything needs to learn what the screen is for; a person who cleared everything does not.

Write "n/a" with a reason when a state cannot happen ("Loading: n/a, the screen shows only text the app already has").

## Words on screen

- **Buttons** say what happens: "Send invite", not "Submit" or "OK".
- **Empty-state lines** say what goes here and how to add it: "No requests yet. New requests from your team appear here."
- **Error messages** say what happened and what to do next: "File is over 10 MB. Choose a smaller one." Never only "Something went wrong".
- **Success messages** confirm the result and, when useful, the next step: "Invite sent to sam@example.com."
- Write the words the person will read, in the product's language, without brand voice. Leave tone to the designer.

## One worked screen block

```markdown
### Request list
- **Purpose:** see open requests and pick one to handle
- **Reached from:** Home, the "Requests" tab, a new-request notification
- **Shows:** open requests, newest first (title, who asked, how long ago); a count of open requests; a filter for "Assigned to me"
- **Actions:** open a request (goes to Request detail); filter; mark as done (stays on this screen)

| State | What the user sees and can do | Words on screen |
|---|---|---|
| First use | A one-line explanation and one action to create a request | "Requests from your team land here." Button: "Create a request" |
| Empty | Shown when all requests are done or the filter matches none; the filter stays visible | "No open requests." With a filter on: "Nothing assigned to you. Show all requests" |
| Loading | The tabs and filter stay usable; the list area waits up to 5 seconds, then shows the error row | none |
| Error | The list could not load; the last loaded list stays visible if there was one | "Requests didn't load. Check your connection and try again." Button: "Try again" |
| Success | After "Mark as done", the request leaves the list and the count drops by one; undo is offered for 5 seconds | "Marked as done." Button: "Undo" |

**Done when:**
- With no requests ever created, the first-use line and "Create a request" show.
- With the connection off, "Try again" reloads the list once the connection is back.
- "Undo" within 5 seconds puts the request back in the same place.
```
