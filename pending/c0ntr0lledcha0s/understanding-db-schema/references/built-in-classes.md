# Logseq Built-in Classes Reference

## Class Hierarchy

```
:logseq.class/Root (base class for all)
├── :logseq.class/Page
│   └── Regular pages with unique names
├── :logseq.class/Tag
│   └── Classes (tags) themselves
├── :logseq.class/Property
│   └── Property definitions
├── :logseq.class/Task
│   └── Tasks with status, priority, deadline
├── :logseq.class/Query
│   └── Saved query definitions
├── :logseq.class/Asset
│   └── File attachments
├── :logseq.class/Journal
│   └── Date-based journal pages
├── :logseq.class/Code-block
│   └── Code snippets
└── :logseq.class/Template
    └── Reusable templates
```

## Class Details

### :logseq.class/Root
Base class that all other classes extend.

### :logseq.class/Page
- Regular named pages
- Unique by title + tag combination
- Can have properties and child blocks

### :logseq.class/Tag
- Classes/tags themselves are entities
- Define properties that apply to tagged items
- Support inheritance via `:extends`

### :logseq.class/Property
- Property definition entities
- Specify type, cardinality, UI position
- Can have closed values (choices)

### :logseq.class/Task
Built-in properties:
- `:logseq.property/status` - Todo, In Progress, Done, etc.
- `:logseq.property/priority` - A, B, C or High, Medium, Low
- `:logseq.property/deadline` - Due date
- `:logseq.property/scheduled` - Start date

### :logseq.class/Journal
- Automatically created for dates
- Named by date format (e.g., "Jan 15th, 2025")
- Support natural language date references

### :logseq.class/Query
- Store saved Datalog queries
- Can have custom views and transforms

### :logseq.class/Asset
- File attachments
- Gallery view support
- Metadata storage

## Creating User Classes

```clojure
;; Simple class
{:db/ident :user.class/Book
 :block/title "Book"
 :block/tags [:logseq.class/Tag]
 :logseq.property.class/extends :logseq.class/Root}

;; Class with properties
{:db/ident :user.class/Book
 :block/title "Book"
 :block/tags [:logseq.class/Tag]
 :logseq.property.class/extends :logseq.class/Root
 :logseq.property/schema-classes
   [:user.property/author
    :user.property/isbn
    :user.property/rating]}

;; Inherited class
{:db/ident :user.class/Audiobook
 :block/title "Audiobook"
 :block/tags [:logseq.class/Tag]
 :logseq.property.class/extends :user.class/Book
 :logseq.property/schema-classes
   [:user.property/narrator
    :user.property/duration]}
```

## Querying Classes

```clojure
;; Find all classes
[:find (pull ?c [*])
 :where
 [?c :block/tags ?t]
 [?t :db/ident :logseq.class/Tag]]

;; Find class hierarchy
[:find ?parent ?child
 :where
 [?c :logseq.property.class/extends ?p]
 [?c :block/title ?child]
 [?p :block/title ?parent]]

;; Find all instances of a class
[:find (pull ?b [*])
 :where
 [?b :block/tags ?t]
 [?t :block/title "Book"]]
```
