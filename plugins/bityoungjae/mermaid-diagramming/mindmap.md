# Mindmap Reference

Visualize hierarchical ideas and brainstorming in Obsidian.

---

## Basic Structure

Indentation defines hierarchy:

```mermaid
mindmap
    Root
        Branch A
            Leaf 1
            Leaf 2
        Branch B
            Leaf 3
```

**Key points:**
- First node is root
- Use consistent indentation (spaces or tabs, don't mix)
- Deeper indentation = deeper hierarchy

---

## Node Shapes

| Shape | Syntax | Display |
|-------|--------|---------|
| Default | `text` | Plain text |
| Square | `[text]` | Rectangle |
| Rounded | `(text)` | Rounded rectangle |
| Circle | `((text))` | Circle |
| Bang | `))text((` | Explosion shape |
| Cloud | `)text(` | Cloud shape |
| Hexagon | `{{text}}` | Hexagon |

### Shape Examples

```mermaid
mindmap
    root((Central))
        square[Square]
        rounded(Rounded)
        circle((Circle))
        bang))Bang((
        cloud)Cloud(
        hex{{Hexagon}}
```

---

## Icons

Add icons with `::icon()` on the line after the node:

```mermaid
mindmap
    root((Project))
        Code
        ::icon(fa fa-code)
        Database
        ::icon(fa fa-database)
        Cloud
        ::icon(fa fa-cloud)
```

**Note:** Icon support depends on Obsidian's loaded icon libraries. Font Awesome icons may not display in all setups.

---

## Markdown Text

Use `` "`...`" `` for formatted text:

```mermaid
mindmap
    root["`**Bold Root**`"]
        branch1["`*Italic* text`"]
        branch2["`Normal with **emphasis**`"]
```

### Multiline Text

```mermaid
mindmap
    root["`**Topic**
Line 2
Line 3`"]
        child[Regular node]
```

For simple line breaks in regular nodes, use `<br/>`:

```mermaid
mindmap
    root
        First line<br/>Second line
```

---

## CSS Classes

Apply custom styles with `:::`:

```mermaid
mindmap
    Root
        Important
        :::critical
        Normal
        Highlighted
        :::highlight
```

**Note:** Define CSS classes in Obsidian's CSS snippets.

---

## Practical Examples

### Example 1: Project Structure

```mermaid
mindmap
    root((Project))
        Frontend
            React
            TypeScript
            CSS Modules
        Backend
            Node.js
            PostgreSQL
            Redis
        DevOps
            Docker
            CI/CD
            Monitoring
```

### Example 2: Learning Roadmap

```mermaid
mindmap
    root((JavaScript))
        Fundamentals
            Variables
            Functions
            Objects
            Arrays
        Advanced
            Closures
            Promises
            Async/Await
        Frameworks
            React
            Vue
            Angular
```

### Example 3: Decision Analysis

```mermaid
mindmap
    root{{Decision}}
        Option A)Pros(
            Lower cost
            Quick start
        Option A)Cons(
            Limited scale
        Option B)Pros(
            Scalable
            Modern
        Option B)Cons(
            Higher cost
            Longer setup
```

---

## Obsidian Notes

**Indentation**: Use consistent spacing. Mix of tabs and spaces causes parsing errors.

**Icons**: Font Awesome/Material Design icons may not render. Test in your setup.

**CSS Classes**: Requires custom CSS snippets in Obsidian settings.

**Special Characters**: Wrap text with special characters in markdown string syntax.

**Performance**: Deep hierarchies (10+ levels) may render slowly.

---

## Quick Reference

| Element | Syntax | Example |
|---------|--------|---------|
| Root | First indented line | `mindmap` + newline + `Root` |
| Square | `[text]` | `[Topic]` |
| Rounded | `(text)` | `(Topic)` |
| Circle | `((text))` | `((Topic))` |
| Cloud | `)text(` | `)Topic(` |
| Bang | `))text((` | `))Topic((` |
| Hexagon | `{{text}}` | `{{Topic}}` |
| Icon | `::icon(class)` | `::icon(fa fa-star)` |
| Markdown | `` ["`text`"] `` | `` ["`**bold**`"] `` |
| CSS class | `:::class` | `:::important` |
