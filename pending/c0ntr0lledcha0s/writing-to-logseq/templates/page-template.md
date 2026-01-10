# Logseq Page Templates

Templates for creating pages via the API.

## Basic Page

```python
writer.create_page(
    title="My Page",
    content="Initial content here"
)
```

## Page with Properties

```python
writer.create_page(
    title="Project Alpha",
    properties={
        "status": "Active",
        "owner": "John Doe",
        "priority": "High",
        "created": "2024-01-15"
    },
    content="""
## Overview

Project description goes here.

## Goals

- Goal 1
- Goal 2
- Goal 3

## Timeline

| Phase | Date | Status |
|-------|------|--------|
| Planning | 2024-01 | Complete |
| Development | 2024-02 | In Progress |
| Launch | 2024-03 | Pending |
"""
)
```

## Meeting Notes Template

```python
from datetime import datetime

def create_meeting_page(title, attendees, agenda):
    date = datetime.now().strftime("%Y-%m-%d")
    attendee_list = "\n".join(f"- [[{a}]]" for a in attendees)
    agenda_list = "\n".join(f"- [ ] {item}" for item in agenda)

    content = f"""
type:: Meeting
date:: [[{date}]]
attendees::

## Attendees
{attendee_list}

## Agenda
{agenda_list}

## Notes

## Action Items

## Follow-up
"""
    return writer.create_page(f"Meetings/{title} - {date}", content=content)
```

## Book/Media Template

```python
def create_book_page(title, author, isbn=None):
    content = f"""
type:: Book
author:: [[{author}]]
status:: To Read
rating::
{f'isbn:: {isbn}' if isbn else ''}

## Summary

## Key Takeaways

## Quotes

## Notes
"""
    return writer.create_page(f"Books/{title}", content=content)
```

## Daily Note Template

```python
def create_daily_note(date=None):
    from datetime import datetime
    date = date or datetime.now().strftime("%Y-%m-%d")

    content = f"""
## Morning
- [ ] Review tasks
- [ ] Check calendar
- [ ] Plan priorities

## Tasks
- [ ]

## Notes

## Evening Review
- What went well?
- What could improve?
- Tomorrow's priorities:
"""
    return writer.create_page(date, content=content)
```

## Claude Conversation Template

```python
def create_conversation_page(topic, summary, key_points):
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    points = "\n".join(f"- {p}" for p in key_points)

    content = f"""
type:: Claude Conversation
created:: {timestamp}
topic:: {topic}

## Summary
{summary}

## Key Points
{points}

## Full Conversation
<!-- Add conversation details here -->

## Follow-up Questions

## Related Pages
"""
    return writer.create_page(f"Claude Notes/{topic}", content=content)
```

## Task/Project Template

```python
def create_task(title, description, due_date=None, priority="Medium"):
    content = f"""
type:: Task
status:: TODO
priority:: {priority}
{f'due:: [[{due_date}]]' if due_date else ''}

## Description
{description}

## Subtasks
- [ ]

## Notes

## Related
"""
    return writer.create_page(f"Tasks/{title}", content=content)
```

## Knowledge Base Article Template

```python
def create_kb_article(title, category, content_text):
    from datetime import datetime
    date = datetime.now().strftime("%Y-%m-%d")

    content = f"""
type:: Knowledge
category:: [[{category}]]
created:: {date}
updated:: {date}
tags::

## Overview
{content_text}

## Details

## Examples

## See Also

## References
"""
    return writer.create_page(f"Knowledge/{category}/{title}", content=content)
```

## Empty Templates (for manual use)

### Generic Note
```markdown
type:: Note
created:: {{date}}
tags::

## Content

## Related
```

### Person Profile
```markdown
type:: Person
company::
role::
email::
phone::

## Notes

## Interactions
```

### Decision Record
```markdown
type:: Decision
status:: Proposed
date:: {{date}}
stakeholders::

## Context

## Decision

## Consequences

## Alternatives Considered
```
