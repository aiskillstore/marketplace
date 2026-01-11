# Logseq Datalog Query Patterns

## Basic Patterns

### Find All Pages
```clojure
[:find (pull ?p [*])
 :where
 [?p :block/tags ?t]
 [?t :db/ident :logseq.class/Page]]
```

### Find Blocks by Tag
```clojure
[:find (pull ?b [*])
 :where
 [?b :block/tags ?t]
 [?t :block/title "Book"]]
```

### Find by Property Value
```clojure
[:find (pull ?b [*])
 :where
 [?b :user.property/status "Complete"]]
```

### Find with Multiple Conditions
```clojure
[:find (pull ?b [*])
 :where
 [?b :block/tags ?t]
 [?t :block/title "Task"]
 [?b :logseq.property/priority "High"]
 [?b :logseq.property/status "In Progress"]]
```

## Advanced Patterns

### Aggregations
```clojure
;; Count by group
[:find ?author (count ?b)
 :where
 [?b :block/tags ?t]
 [?t :block/title "Book"]
 [?b :user.property/author ?author]]

;; Statistics
[:find (sum ?r) (avg ?r) (min ?r) (max ?r)
 :where
 [?b :user.property/rating ?r]]
```

### Date Comparisons
```clojure
[:find (pull ?t [*])
 :in $ ?today
 :where
 [?t :block/tags ?tag]
 [?tag :db/ident :logseq.class/Task]
 [?t :logseq.property/deadline ?d]
 [(< ?d ?today)]]
```

### Negation
```clojure
;; Blocks without a property
[:find (pull ?b [*])
 :where
 [?b :block/tags ?t]
 [?t :block/title "Book"]
 (not [?b :user.property/rating _])]
```

### Or Clauses
```clojure
[:find (pull ?b [*])
 :where
 [?b :block/tags ?t]
 [?t :block/title "Task"]
 (or
   [?b :logseq.property/priority "High"]
   [?b :logseq.property/priority "Urgent"])]
```

### Rules
```clojure
;; Define reusable rules
[[(has-tag ?b ?name)
  [?b :block/tags ?t]
  [?t :block/title ?name]]

 [(is-overdue ?b ?today)
  [?b :logseq.property/deadline ?d]
  [(< ?d ?today)]]]

;; Use rules
[:find (pull ?b [*])
 :in $ % ?today
 :where
 (has-tag ?b "Task")
 (is-overdue ?b ?today)]
```

### Recursive Queries
```clojure
;; Find all descendants
[[(descendant ?parent ?child)
  [?child :block/parent ?parent]]
 [(descendant ?parent ?child)
  [?child :block/parent ?mid]
  (descendant ?parent ?mid)]]

[:find (pull ?c [*])
 :in $ % ?root-uuid
 :where
 [?root :block/uuid ?root-uuid]
 (descendant ?root ?c)]
```

## Pull Syntax

### Select Attributes
```clojure
(pull ?e [:block/title :user.property/rating])
```

### Nested Pulls
```clojure
(pull ?e [:block/title {:block/tags [:block/title]}])
```

### Reverse References
```clojure
(pull ?e [:block/title {:block/_refs [:block/title]}])
```

### Limits
```clojure
(pull ?e [:block/title {:block/children [:block/title] :limit 5}])
```

## Query Block Syntax

```
#+BEGIN_QUERY
{:title "Query Title"
 :query [:find (pull ?b [*])
         :where ...]
 :inputs [:today]
 :result-transform (fn [result] ...)
 :view (fn [rows] ...)
 :collapsed? false}
#+END_QUERY
```

## Plugin API

```javascript
// Simple query
const results = await logseq.DB.datascriptQuery(`
  [:find (pull ?b [*])
   :where [?b :block/tags ?t]
          [?t :block/title "Book"]]
`)

// Query with parameters
const results = await logseq.DB.datascriptQuery(`
  [:find (pull ?b [*])
   :in $ ?tag-name
   :where [?b :block/tags ?t]
          [?t :block/title ?tag-name]]
`, ['Book'])
```
