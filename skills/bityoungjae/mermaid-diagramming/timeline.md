# Timeline Diagram Reference

Complete guide for Mermaid timeline diagrams in Obsidian.

---

## Introduction

Timeline diagrams visualize events or milestones in chronological order. They're ideal for showing historical progressions, product releases, project milestones, or any sequence of time-based events.

---

## Basic Structure

### Simple Timeline

```mermaid
timeline
    title Timeline Title
    2020 : Event 1
    2021 : Event 2
    2022 : Event 3
```

### Key Characteristics

- Time periods can be any text (not just years)
- Events are organized chronologically
- Multiple events per time period are supported
- Automatic color coding by section

---

## Syntax Reference

### Title

```mermaid
timeline
    title History of Social Media
```

### Time Period and Events

```
timeline
    {time-period} : {event}
```

Format options:

```mermaid
timeline
    2020 : Single event
    2021 : Event 1 : Event 2 : Event 3
    2022 : Event A
         : Event B
         : Event C
```

| Component | Details | Example |
|-----------|---------|---------|
| Time period | Any text label | `2020`, `Q1`, `January` |
| Event | Describes what happened | `Product Launch` |
| Multiple events | Use colons or indentation | `2020 : Event1 : Event2` |

---

## Time Periods

### Numeric Years

```mermaid
timeline
    title Product Roadmap
    2022 : Version 1.0
    2023 : Version 2.0
    2024 : Version 3.0
    2025 : Version 4.0
```

### Calendar Quarters

```mermaid
timeline
    title Quarterly Revenue
    Q1 2024 : Strong growth
    Q2 2024 : Peak performance
    Q3 2024 : Seasonal decline
    Q4 2024 : Recovery
```

### Month/Year Format

```mermaid
timeline
    title Project Timeline
    Jan 2024 : Kickoff
    Feb 2024 : Design
    Mar 2024 : Development
    Apr 2024 : Testing
    May 2024 : Launch
```

### Custom Periods

```mermaid
timeline
    title Technology Evolution
    Ancient : Writing invented
    Medieval : Printing press
    Modern : Internet
    Contemporary : AI Revolution
```

---

## Sections

Organize time periods into named sections with shared color schemes:

```mermaid
timeline
    title Company History
    section Founding
        1995 : Company established
        1996 : First product
    section Growth
        2000 : Series A funding
        2005 : IPO
    section Expansion
        2010 : International offices
        2015 : Major acquisition
```

### Multiple Events per Period

```mermaid
timeline
    title Major Tech Releases
    section 2023 Releases
        Jan 2023 : New feature A : Critical bug fix
        Jun 2023 : Redesign : Performance boost
        Dec 2023 : Feature B : End of year sprint
    section 2024 Releases
        Mar 2024 : V2.0 launch
        Aug 2024 : AI integration
```

---

## Practical Examples

### Example 1: Historical Timeline

```mermaid
timeline
    title History of Web Development
    section Early Web
        1989 : World Wide Web invented by Tim Berners-Lee
        1993 : First web browser - Mosaic
        1995 : JavaScript created
    section Browser Wars
        1996 : Internet Explorer launch
        1998 : Mozilla founded
        2003 : Firefox development begins
    section Modern Era
        2004 : Gmail launch (AJAX era)
        2008 : Chrome released
        2009 : Node.js created
    section Current
        2015 : ES6/ES2015 standard
        2016 : React, Vue maturity
        2018 : TypeScript adoption
        2023 : AI-assisted coding
```

### Example 2: Product Release Timeline

```mermaid
timeline
    title Software Product Evolution
    section Alpha Phase
        Jan 2023 : MVP released : Initial testing
        Feb 2023 : Closed beta : User feedback
    section Beta Phase
        Apr 2023 : Public beta launch
        May 2023 : Performance improvements
        Jun 2023 : Security audit
    section Official Release
        Jul 2023 : v1.0 Launch : Full feature set
        Sep 2023 : v1.1 : Bug fixes : Optimization
    section Growth
        Jan 2024 : v2.0 : Major redesign
        Jun 2024 : Enterprise features
        Dec 2024 : AI integration
```

### Example 3: Project Timeline

```mermaid
timeline
    title Construction Project Schedule
    section Planning Phase
        Week 1-2 : Requirements gathering
        Week 3-4 : Design & approval
    section Development Phase
        Week 5-8 : Foundation work
        Week 9-12 : Main construction
        Week 13-16 : Interior finishing
    section Testing Phase
        Week 17 : Final inspections
        Week 18 : Safety testing
    section Launch
        Week 19 : Grand opening
        Week 20+ : Operations
```

### Example 4: Company Milestones

```mermaid
timeline
    title TechCorp Company Journey
    section Startup
        2010 : Founded : 3 founders
        2011 : First 10 employees
        2012 : First paying customer
    section Growth
        2013 : Series A - $2M funding
        2014 : 50 employees milestone
        2015 : $10M ARR
    section Scale
        2016 : Series B - $10M funding
        2017 : International expansion
        2018 : 200+ employees
    section Maturity
        2019 : IPO : Going public
        2020 : Fortune 500 partnership
        2021 : Industry leadership
        2022 : $100M revenue milestone
        2023 : Global presence : 1000+ employees
```

### Example 5: Learning Progression

```mermaid
timeline
    title Web Development Learning Journey
    section Fundamentals
        Month 1 : HTML basics : CSS styling
        Month 2 : JavaScript fundamentals
        Month 3 : DOM manipulation
    section Frontend
        Month 4-5 : React concepts
        Month 6 : State management
        Month 7 : Advanced React patterns
    section Backend
        Month 8 : Node.js & Express
        Month 9 : Database design : SQL
        Month 10 : RESTful APIs
    section Advanced
        Month 11 : Testing & debugging
        Month 12 : Deployment & DevOps
        Month 13 : Project development
```

---

## Advanced Features

### Comments

```mermaid
timeline
    title Commented Timeline
    %% Founding era
    1995 : Company start
    %% Growth period
    2000 : Expansion
    %% Modern age
    2020 : Digital transformation
```

### Multi-Line Events

Use `<br>` for line breaks in events:

```mermaid
timeline
    title Product Roadmap
    2023 : Launch MVP<br>Setup infrastructure
    2024 : Scale operations<br>Add team members
    2025 : AI integration<br>Enterprise features
```

### Different Time Scales

```mermaid
timeline
    title Flexible Timeline
    section Years
        2020 : Year milestone
        2021 : Another milestone
    section Months
        Jan 2022 : Monthly detail
        Feb 2022 : Another month
    section Days
        Day 1 : Daily event
        Day 2 : Another event
```

---

## Styling

### Custom Themes

Use YAML frontmatter to configure themes:

```mermaid
---
config:
  theme: 'dark'
---
timeline
    title Dark Theme Timeline
    2020 : Event 1
    2021 : Event 2
    2022 : Event 3
```

### Color Scheme

Timeline sections automatically get different colors. Customize using theme variables:

```mermaid
---
config:
  theme: 'default'
  themeVariables:
    cScale0: '#ff0000'
    cScaleLabel0: '#ffffff'
    cScale1: '#00ff00'
    cScale2: '#0000ff'
---
timeline
    title Custom Colors Timeline
    2020 : Event 1
    2021 : Event 2
    2022 : Event 3
```

---

## Best Practices

### Time Period Format

- **Years**: `2020`, `2021`, `2022`
- **Quarters**: `Q1 2024`, `Q2 2024`
- **Months**: `January 2024`, `Jan 2024`
- **Custom**: `Phase 1`, `Ancient Era`, `Modern Age`

### Event Description

- Keep descriptions concise (1-5 words)
- Use clear, descriptive action words
- Avoid overly technical language
- Use consistent formatting

### Section Organization

- Group related time periods together
- Use 3-5 sections maximum
- Place most important milestones prominently
- Order chronologically

### Readability

- Limit events per period to 3-5
- Use line breaks for multiple events
- Avoid very long event descriptions
- Keep timeline width reasonable

---

## Common Patterns

### Annual Review

```mermaid
timeline
    title 2024 Company Review
    section Q1
        Jan : Q1 kickoff
        Feb : Product update
        Mar : Team expansion
    section Q2
        Apr : Earnings report
        May : Partnership
        Jun : Summer planning
```

### Milestone Tracking

```mermaid
timeline
    title Development Milestones
    Alpha : Design complete
    Beta : Initial release
    RC : Release candidate
    v1.0 : Official launch
```

---

## Obsidian Notes

**Time Unit**: Not limited to years - use any text as time periods (months, quarters, phases, eras).

**Section Colors**: Sections get automatically assigned different background colors for visual distinction.

**Event Count**: Aim for 2-5 events per time period for optimal readability.

**Performance**: Very long timelines (50+ events) may slow rendering. Consider splitting into multiple diagrams.

**Export**: PDF export renders diagrams as images. For external sharing, capture as PNG/SVG.

**Responsive**: Timeline adapts to Obsidian viewport width. Long event text wraps automatically.

**Code Block Format**:
````
```mermaid
timeline
    title My Timeline
    2020 : Event
    2021 : Event
```
````

---

## Quick Reference Table

| Element | Syntax | Example |
|---------|--------|---------|
| Diagram start | `timeline` | `timeline` |
| Title | `title text` | `title Company History` |
| Time period | `period : event` | `2020 : Founded` |
| Multiple events | `period : event1 : event2` | `2020 : Founded : v1.0` |
| Alternative format | Indented under period | `: Event` on next lines |
| Section | `section name` | `section Growth` |
| Comment | `%% text` | `%% Founding era` |
| Line break | `<br>` | `Founded<br>v1.0` |
| Year format | Text label | `2020`, `Q1 2024` |
| Month format | Full or abbreviated | `January 2024`, `Jan 2024` |
| Custom period | Any text | `Ancient`, `Phase 1` |
| Theme | YAML frontmatter | `---\nconfig:\n  theme: 'dark'\n---` |
