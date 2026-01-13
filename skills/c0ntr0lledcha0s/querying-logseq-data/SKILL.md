---
name: querying-logseq-data
version: 1.0.0
description: >
  Expert in building Datalog queries for Logseq DB graphs. Auto-invokes when users need help
  writing Logseq queries, understanding Datalog syntax, optimizing query performance,
  or working with the Datascript query engine. Covers advanced query patterns, pull syntax,
  aggregations, and DB-specific query techniques.
allowed-tools: Read, Grep, Glob, WebFetch, WebSearch
---

# Querying Logseq Data

## When to Use This Skill

This skill auto-invokes when:
- User wants to build a Datalog query for Logseq
- Questions about `:find`, `:where`, `:in` clauses
- Pull syntax questions (pull ?e [*])
- Query optimization or performance issues
- Aggregation queries (count, sum, avg, min, max)
- Rule definitions or reusable query logic
- Converting simple query syntax to full Datalog
- User mentions "Datalog", "query", "datascript" with Logseq context

**Reference Material**: See `{baseDir}/references/query-patterns.md` for common query examples.

You are an expert in Datalog queries for Logseq's database-based graphs.

## Datalog Query Fundamentals

### Basic Query Structure

```clojure
[:find ?variable          ; What to return
 :in $ ?input-var         ; Inputs ($ = database)
 :where                   ; Conditions
 [?entity :attribute ?value]]
```

### Find Specifications

```clojure
;; Return all matches as tuples
[:find ?title ?author ...]

;; Return as collection (single variable)
[:find [?title ...] ...]

;; Return single value
[:find ?title . ...]

;; Return single tuple
[:find [?title ?author] ...]

;; Pull entity data
[:find (pull ?e [*]) ...]
[:find (pull ?e [:block/title :block/tags]) ...]
```

## Common Query Patterns

### Find All Pages

```clojure
[:find (pull ?p [*])
 :where
 [?p :block/tags ?t]
 [?t :db/ident :logseq.class/Page]]
```

### Find Blocks with Specific Tag/Class

```clojure
[:find (pull ?b [*])
 :where
 [?b :block/tags ?t]
 [?t :block/title "Book"]]
```

### Find by Property Value

```clojure
;; Exact match
[:find (pull ?b [*])
 :where
 [?b :user.property/author "Stephen King"]]

;; With variable binding
[:find ?title ?author
 :where
 [?b :block/title ?title]
 [?b :user.property/author ?author]
 [?b :block/tags ?t]
 [?t :block/title "Book"]]
```

### Find Tasks by Status

```clojure
[:find (pull ?t [*])
 :where
 [?t :block/tags ?tag]
 [?tag :db/ident :logseq.class/Task]
 [?t :logseq.property/status ?s]
 [?s :block/title "In Progress"]]
```

### Find with Date Ranges

```clojure
;; Tasks due this week
[:find (pull ?t [*])
 :in $ ?start ?end
 :where
 [?t :block/tags ?tag]
 [?tag :db/ident :logseq.class/Task]
 [?t :logseq.property/deadline ?d]
 [(>= ?d ?start)]
 [(<= ?d ?end)]]
```

## Advanced Query Techniques

### Aggregations

```clojure
;; Count books by author
[:find ?author (count ?b)
 :where
 [?b :block/tags ?t]
 [?t :block/title "Book"]
 [?b :user.property/author ?author]]

;; Sum, min, max, avg
[:find (sum ?rating) (avg ?rating) (min ?rating) (max ?rating)
 :where
 [?b :block/tags ?t]
 [?t :block/title "Book"]
 [?b :user.property/rating ?rating]]
```

### Rules (Reusable Query Logic)

```clojure
;; Define rules
[[(has-tag ?b ?tag-name)
  [?b :block/tags ?t]
  [?t :block/title ?tag-name]]

 [(is-task ?b)
  [?b :block/tags ?t]
  [?t :db/ident :logseq.class/Task]]]

;; Use rules in query
[:find (pull ?b [*])
 :in $ %
 :where
 (has-tag ?b "Important")
 (is-task ?b)]
```

### Negation

```clojure
;; Find books without rating
[:find (pull ?b [*])
 :where
 [?b :block/tags ?t]
 [?t :block/title "Book"]
 (not [?b :user.property/rating _])]
```

### Or Clauses

```clojure
;; Find high priority or overdue tasks
[:find (pull ?t [*])
 :in $ ?today
 :where
 [?t :block/tags ?tag]
 [?tag :db/ident :logseq.class/Task]
 (or
   [?t :logseq.property/priority "High"]
   (and
     [?t :logseq.property/deadline ?d]
     [(< ?d ?today)]))]
```

### Recursive Queries

```clojure
;; Find all descendants of a block
[[(descendant ?parent ?child)
  [?child :block/parent ?parent]]
 [(descendant ?parent ?child)
  [?child :block/parent ?p]
  (descendant ?parent ?p)]]

[:find (pull ?c [*])
 :in $ % ?root-id
 :where
 [?root :block/uuid ?root-id]
 (descendant ?root ?c)]
```

## Pull Syntax

### Selective Attributes

```clojure
;; Specific attributes
(pull ?e [:block/title :block/tags])

;; Nested pulling for refs
(pull ?e [:block/title {:block/tags [:block/title]}])

;; All attributes
(pull ?e [*])

;; Limit nested results
(pull ?e [:block/title {:block/children [:block/title] :limit 5}])
```

### Reverse References

```clojure
;; Find all blocks referencing this entity
(pull ?e [:block/title {:block/_refs [:block/title]}])
```

## DB-Specific Query Patterns

### Working with Classes

```clojure
;; Find all classes (tags that are themselves tagged as Tag)
[:find (pull ?c [*])
 :where
 [?c :block/tags ?t]
 [?t :db/ident :logseq.class/Tag]]

;; Find class hierarchy
[:find ?parent-name ?child-name
 :where
 [?child :logseq.property.class/extends ?parent]
 [?child :block/title ?child-name]
 [?parent :block/title ?parent-name]]
```

### Working with Properties

```clojure
;; Find all user-defined properties
[:find (pull ?p [*])
 :where
 [?p :block/tags ?t]
 [?t :db/ident :logseq.class/Property]
 [?p :db/ident ?ident]
 [(clojure.string/starts-with? (str ?ident) ":user.property")]]

;; Find property values with type
[:find ?prop-name ?type
 :where
 [?p :block/tags ?t]
 [?t :db/ident :logseq.class/Property]
 [?p :block/title ?prop-name]
 [?p :logseq.property/type ?type]]
```

### Journal Queries

```clojure
;; Find all journal pages
[:find (pull ?j [*])
 :where
 [?j :block/tags ?t]
 [?t :db/ident :logseq.class/Journal]]

;; Find journal for specific date
[:find (pull ?j [*])
 :in $ ?date-str
 :where
 [?j :block/tags ?t]
 [?t :db/ident :logseq.class/Journal]
 [?j :block/title ?date-str]]
```

## Query Optimization Tips

1. **Put most selective clauses first** - Narrow down results early
2. **Use indexed attributes** - `:db/ident`, `:block/uuid` are indexed
3. **Avoid wildcards in pull** - Specify needed attributes
4. **Use rules for complex logic** - Better readability and potential caching
5. **Limit results when possible** - Add limits for large datasets

```clojure
;; Optimized query example
[:find (pull ?b [:block/title :user.property/rating])
 :in $ ?min-rating
 :where
 ;; Most selective first
 [?b :user.property/rating ?r]
 [(>= ?r ?min-rating)]
 ;; Then filter by tag
 [?b :block/tags ?t]
 [?t :block/title "Book"]]
```

## Logseq Query UI vs Raw Datalog

### Simple Query (UI)
```
{{query (and [[Book]] (property :rating 5))}}
```

### Equivalent Datalog
```clojure
[:find (pull ?b [*])
 :where
 [?b :block/tags ?t]
 [?t :block/title "Book"]
 [?b :user.property/rating 5]]
```

### Advanced Query Block
```
#+BEGIN_QUERY
{:title "5-Star Books"
 :query [:find (pull ?b [*])
         :where
         [?b :block/tags ?t]
         [?t :block/title "Book"]
         [?b :user.property/rating 5]]
 :result-transform (fn [result] (sort-by :block/title result))
 :view (fn [rows] [:ul (for [r rows] [:li (:block/title r)])])}
#+END_QUERY
```

## Common Gotchas

1. **MD vs DB attribute differences**
   - MD: `:block/content`, `:block/name`
   - DB: `:block/title`, `:block/tags`

2. **Property namespacing**
   - User properties: `:user.property/name`
   - System properties: `:logseq.property/name`

3. **Tag vs Class terminology**
   - In UI: "Tags"
   - In schema: "Classes" (`:logseq.class/*`)

4. **Date handling**
   - Dates link to journal pages
   - Compare using date functions, not strings
