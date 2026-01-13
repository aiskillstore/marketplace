# EDN Analyzer - Technical Reference

This document provides technical details about EDN template structure and analysis methods.

## EDN Structure Overview

### Top-Level Structure

```clojure
{:properties {...}          ; Map of property definitions
 :classes {...}             ; Map of class definitions
 :logseq.db.sqlite.export/export-type :graph-ontology}  ; Required marker
```

### Property Definition

```clojure
:user.property/propertyName-UniqueID
{:db/cardinality :db.cardinality/one   ; or :many
 :logseq.property/type :default         ; :node, :date, :url, :number
 :block/title "propertyName"
 :build/property-classes [:user.class/ClassName-ID ...]
 :build/properties
 {:logseq.property/icon {:id "emoji" :type :emoji}
  :logseq.property/description "Description text"}}
```

#### Property Fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `:db/cardinality` | Yes | Keyword | `:db.cardinality/one` or `:db.cardinality/many` |
| `:logseq.property/type` | Yes | Keyword | `:default`, `:node`, `:date`, `:url`, `:number` |
| `:block/title` | Yes | String | Human-readable property name |
| `:build/property-classes` | Yes | Vector | Classes that use this property |
| `:build/properties` | No | Map | Metadata (icon, description) |

#### Cardinality Types

- **`:db.cardinality/one`** - Single value (e.g., birthDate, email)
- **`:db.cardinality/many`** - Multiple values (e.g., children, colleagues)

#### Property Types

| Type | Description | Example Use |
|------|-------------|-------------|
| `:default` | Plain text/string | Name, description, jobTitle |
| `:node` | Link to another page | worksFor, spouse, parent |
| `:date` | Date value | birthDate, startDate, endDate |
| `:url` | URL/link | website, sameAs |
| `:number` | Numeric value | age, price, quantity |

### Class Definition

```clojure
:user.class/ClassName-UniqueID
{:block/title "ClassName"
 :build/class-properties [:user.property/prop1-ID :user.property/prop2-ID ...]
 :build/class-parent :user.class/ParentClass-ID
 :build/properties
 {:logseq.property/icon {:id "emoji" :type :emoji}
  :logseq.property/description "Description text"}}
```

#### Class Fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `:block/title` | Yes | String | Human-readable class name |
| `:build/class-properties` | Yes | Vector | Properties for this class |
| `:build/class-parent` | No | Keyword | Parent class for inheritance |
| `:build/properties` | No | Map | Metadata (icon, description) |

#### Class Hierarchy Rules

1. **Root Classes**: Thing and Agent don't need `:build/class-parent`
2. **Inheritance**: Child classes inherit parent's properties
3. **Multiple Levels**: Support deep hierarchies (Thing → Person → PersonalRelationship)

### Unique IDs

All classes and properties use unique IDs:

**Format:** `:user.class/ClassName-RandomID` or `:user.property/propertyName-RandomID`

**Examples:**
- `:user.class/Person-xY9zK`
- `:user.property/email-pQ2rS`

**Random ID:**
- 8 characters
- Mixed case alphanumeric
- Ensures uniqueness across all entities

---

## Analysis Methods

### 1. Counting Items

#### Count Classes
```clojure
(count (:classes template))
```

#### Count Properties
```clojure
(count (:properties template))
```

#### Count by Module
```bash
# Count classes in module
grep -c ":user.class/" source/MODULE/classes.edn

# Count properties in module
grep -c ":user.property/" source/MODULE/properties.edn
```

### 2. Finding Orphans

#### Orphaned Classes
Classes without `:build/class-parent` (except Thing and Agent):

```clojure
(filter
  (fn [[id class]]
    (and (not (contains? class :build/class-parent))
         (not= (:block/title class) "Thing")
         (not= (:block/title class) "Agent")))
  (:classes template))
```

#### Orphaned Properties
Properties not in any class's `:build/class-properties`:

```clojure
(let [used-props (set (mapcat :build/class-properties (vals (:classes template))))
      all-props (set (keys (:properties template)))]
  (clojure.set/difference all-props used-props))
```

### 3. Type Distribution

#### Property Type Counts
```clojure
(frequencies
  (map #(get-in % [:logseq.property/type])
       (vals (:properties template))))
```

#### Cardinality Counts
```clojure
(frequencies
  (map #(get-in % [:db/cardinality])
       (vals (:properties template))))
```

### 4. Hierarchy Analysis

#### Find Children of Class
```clojure
(defn find-children [parent-id template]
  (filter
    #(= (:build/class-parent (val %)) parent-id)
    (:classes template)))
```

#### Build Full Hierarchy
```clojure
(defn build-hierarchy [class-id template]
  (let [class (get-in template [:classes class-id])
        children (find-children class-id template)]
    {:id class-id
     :title (:block/title class)
     :properties (count (:build/class-properties class))
     :children (map #(build-hierarchy (key %) template) children)}))
```

### 5. Property Usage

#### Find Classes Using Property
```clojure
(defn find-property-usage [prop-id template]
  (filter
    #(contains? (set (:build/class-properties (val %))) prop-id)
    (:classes template)))
```

### 6. Validation Checks

#### Check for Duplicate IDs
```clojure
(defn find-duplicates [items]
  (let [freqs (frequencies (map :block/title items))]
    (filter #(> (val %) 1) freqs)))
```

#### Check ID Format
```clojure
(defn valid-id? [id]
  (re-matches #":user\.(class|property)/[A-Za-z]+-[A-Za-z0-9]{8}" (str id)))
```

#### Check Required Fields

For properties:
```clojure
(defn validate-property [prop]
  (and (contains? prop :db/cardinality)
       (contains? prop :logseq.property/type)
       (contains? prop :block/title)
       (contains? prop :build/property-classes)))
```

For classes:
```clojure
(defn validate-class [class]
  (and (contains? class :block/title)
       (contains? class :build/class-properties)))
```

---

## File Size Calculations

### Estimate Template Size

**Per Property:**
- Minimal: ~120 bytes
- With metadata: ~200 bytes
- Average: ~180 bytes

**Per Class:**
- Minimal: ~150 bytes
- With properties list: ~300 bytes
- Average: ~250 bytes

**Total Estimate:**
```
Size ≈ (num_properties × 180) + (num_classes × 250) + overhead
```

**Example (632 classes, 1,033 properties):**
```
Size ≈ (1033 × 180) + (632 × 250) + 50000
     ≈ 185,940 + 158,000 + 50,000
     ≈ 394 KB
```

Actual: ~497 KB (due to descriptions, icons, formatting)

---

## Performance Considerations

### Large Template Optimization

For templates > 10,000 lines:

1. **Use streaming** instead of loading entire file
2. **Index by type** for faster lookups
3. **Cache results** of expensive operations
4. **Parallel processing** for independent analyses

### Memory Usage

**Full template in memory:**
- 632 classes: ~158 KB
- 1,033 properties: ~186 KB
- Metadata: ~150 KB
- Total: ~500 KB in memory

**Optimization:**
- Use lazy sequences for large analyses
- Process modules independently
- Clear cache between operations

---

## Common Analysis Patterns

### Pattern 1: Module Statistics

```bash
# For each module
for dir in source/*/; do
  MODULE=$(basename "$dir")
  CLASSES=$(grep -c ":user.class/" "$dir/classes.edn" 2>/dev/null || echo "0")
  PROPS=$(grep -c ":user.property/" "$dir/properties.edn" 2>/dev/null || echo "0")
  echo "$MODULE: $CLASSES classes, $PROPS properties"
done
```

### Pattern 2: Find Large Classes

```clojure
(defn find-large-classes [template threshold]
  (filter
    #(> (count (:build/class-properties (val %))) threshold)
    (:classes template)))
```

### Pattern 3: Property Reuse Analysis

```clojure
(defn property-reuse-score [template]
  (let [usage-counts (frequencies
                       (mapcat :build/class-properties
                               (vals (:classes template))))]
    (/ (apply + (vals usage-counts))
       (count (:properties template)))))
```

### Pattern 4: Type Safety Check

```clojure
(defn check-type-safety [template]
  (for [[prop-id prop] (:properties template)
        class-id (:build/property-classes prop)
        :when (not (contains? (:classes template) class-id))]
    {:property prop-id
     :missing-class class-id
     :issue "Property references non-existent class"}))
```

---

## EDN Parsing Tips

### Reading EDN Files

```clojure
(require '[clojure.edn :as edn])

;; Read entire file
(def template (edn/read-string (slurp "template.edn")))

;; Safe read with error handling
(def template
  (try
    (edn/read-string (slurp "template.edn"))
    (catch Exception e
      (println "Parse error:" (.getMessage e))
      nil)))
```

### Writing EDN Files

```clojure
(require '[clojure.pprint :refer [pprint]])

;; Pretty-print to file
(spit "output.edn"
      (with-out-str (pprint template)))

;; Compact format
(spit "output.edn"
      (pr-str template))
```

---

## Error Handling

### Common Errors

1. **Parse Errors**
   - Missing closing braces
   - Invalid keyword format
   - Unquoted strings

2. **Structure Errors**
   - Missing required fields
   - Invalid cardinality values
   - Broken parent references

3. **Logic Errors**
   - Circular dependencies
   - Orphaned items
   - Duplicate IDs

### Validation Workflow

```
1. Parse EDN → Check syntax
2. Validate structure → Check required fields
3. Check references → Verify IDs exist
4. Analyze relationships → Find orphans/circles
5. Generate report → List issues with line numbers
```

---

## Tools Integration

### Using with Babashka

```clojure
#!/usr/bin/env bb

(require '[clojure.edn :as edn])

(defn analyze [file]
  (let [template (edn/read-string (slurp file))]
    {:classes (count (:classes template))
     :properties (count (:properties template))}))

(println (analyze (first *command-line-args*)))
```

### Using with grep

```bash
# Find all classes
grep -o ':user.class/[^[:space:]]*' template.edn

# Find all :many properties
grep -B2 ':db.cardinality/many' template.edn

# Count by type
grep -o ':logseq.property/type :[^[:space:]]*' template.edn | \
  cut -d: -f3 | sort | uniq -c
```

---

## Schema.org Mapping

### Standard Schema.org Types

| Schema.org Class | Logseq Class | Common Properties |
|-----------------|--------------|-------------------|
| Thing | Thing | name, description, url |
| Person | Person | jobTitle, email, birthDate |
| Organization | Organization | legalName, employee, founder |
| Event | Event | startDate, endDate, attendee |
| CreativeWork | CreativeWork | author, dateCreated, genre |
| Place | Place | address, geo, telephone |

### Property Type Mapping

| Schema.org Type | Logseq Type | Example |
|----------------|-------------|---------|
| Text | `:default` | name, description |
| URL | `:url` | website, sameAs |
| Date | `:date` | birthDate, startDate |
| Number | `:number` | age, price |
| Thing | `:node` | worksFor, knows |

---

## References

- [EDN Specification](https://github.com/edn-format/edn)
- [Schema.org Vocabulary](https://schema.org/)
- [Logseq Database Format](https://docs.logseq.com/)
- [Clojure EDN Reader](https://clojure.org/reference/reader)
