# Schema Research - Technical Reference

This document provides technical details for Schema.org research and Logseq integration.

## Schema.org Type Mapping

### Text Types → Logseq :default

| Schema.org Type | Logseq Type | Cardinality | Examples |
|----------------|-------------|-------------|----------|
| Text | `:default` | `:one` or `:many` | name, description, jobTitle |
| Boolean | `:default` | `:one` | isPartOf, isRelatedTo |
| Integer | `:number` | `:one` | age, numberOfEmployees |
| Float/Number | `:number` | `:one` | price, rating |

### URL Types → Logseq :url

| Schema.org Type | Logseq Type | Cardinality | Examples |
|----------------|-------------|-------------|----------|
| URL | `:url` | `:one` or `:many` | website, sameAs, url |
| URI | `:url` | `:one` | identifier (when URL) |

### Date/Time Types → Logseq :date

| Schema.org Type | Logseq Type | Cardinality | Examples |
|----------------|-------------|-------------|----------|
| Date | `:date` | `:one` | birthDate, datePublished |
| DateTime | `:date` | `:one` | startDate, endDate |
| Time | `:default` | `:one` | openingTime, closingTime |
| Duration | `:default` | `:one` | cookTime, duration |

### Thing Types → Logseq :node

| Schema.org Type | Logseq Type | Cardinality | Examples |
|----------------|-------------|-------------|----------|
| Person | `:node` | `:one` or `:many` | author, employee, spouse |
| Organization | `:node` | `:one` or `:many` | worksFor, publisher, member |
| Place | `:node` | `:one` or `:many` | location, birthPlace |
| Event | `:node` | `:one` or `:many` | subEvent, superEvent |
| CreativeWork | `:node` | `:one` or `:many` | hasPart, isPartOf |
| Product | `:node` | `:one` or `:many` | offers, itemOffered |
| Thing (any) | `:node` | `:one` or `:many` | about, mentions |

### Complex/Structured Types

| Schema.org Type | Logseq Strategy | Notes |
|----------------|-----------------|-------|
| PostalAddress | `:node` | Link to Address page |
| ContactPoint | `:node` | Link to ContactPoint page |
| GeoCoordinates | `:default` | Store as "lat,long" text |
| QuantitativeValue | `:default` | Store as "value unit" text |
| MonetaryAmount | `:default` | Store as "123.45 USD" text |
| ImageObject | `:url` | Link to image URL |
| VideoObject | `:url` | Link to video URL |

---

## Cardinality Guidelines

### Use :db.cardinality/one When:

- Property is inherently singular
- Schema.org shows single value in examples
- Logically only one value makes sense

**Examples:**
- birthDate (one birth date)
- email (primary email - though could be :many)
- jobTitle (current job title)
- description (one main description)

### Use :db.cardinality/many When:

- Property can have multiple values
- Schema.org documentation mentions "or" or lists
- Real-world usage requires multiple values

**Examples:**
- children (multiple children)
- colleague (multiple colleagues)
- knows (multiple acquaintances)
- sameAs (multiple identity URLs)
- award (multiple awards)

### Ambiguous Cases:

| Property | Recommended | Reasoning |
|----------|-------------|-----------|
| email | `:many` | People often have multiple emails |
| telephone | `:many` | Mobile, home, work numbers |
| address | `:many` | Home, work, mailing addresses |
| url | `:many` | Multiple websites/profiles |
| image | `:many` | Multiple photos |
| affiliation | `:many` | Multiple organizational affiliations |

---

## Schema.org Hierarchy Quick Reference

### Top-Level Classes

```
Thing
├── Action
├── CreativeWork
├── Event
├── Intangible
├── MedicalEntity
├── Organization
├── Person
├── Place
└── Product
```

### Common Subclasses

**CreativeWork:**
- Article, Blog, Book, Comment, Course, Dataset, Movie
- MusicRecording, Photograph, Recipe, Review, SoftwareApplication
- TVSeries, VideoGame, WebPage

**Event:**
- BusinessEvent, ChildrensEvent, ComedyEvent, CourseInstance
- DanceEvent, DeliveryEvent, EducationEvent, ExhibitionEvent
- Festival, FoodEvent, LiteraryEvent, MusicEvent, SaleEvent
- ScreeningEvent, SocialEvent, SportsEvent, TheaterEvent

**Intangible:**
- Brand, ComputerLanguage, DefinedTerm, Enumeration
- ItemList, JobPosting, Language, Offer, Order
- Rating, Reservation, Role, Service, Ticket

**Organization:**
- Airline, Consortium, Corporation, EducationalOrganization
- FundingScheme, GovernmentOrganization, LibrarySystem
- LocalBusiness, MedicalOrganization, NGO, NewsMediaOrganization
- PerformingGroup, Project, SportsOrganization, WorkersUnion

**Place:**
- Accommodation, AdministrativeArea, CivicStructure
- Landform, LandmarksOrHistoricalBuildings, LocalBusiness
- Residence, TouristAttraction, TouristDestination

**Product:**
- IndividualProduct, ProductCollection, ProductGroup
- ProductModel, SomeProducts, Vehicle

---

## Property Categories

### Identification Properties

Common across all Thing subclasses:

| Property | Type | Cardinality | Description |
|----------|------|-------------|-------------|
| name | Text | :one | Primary name |
| alternateName | Text | :many | Alternative names |
| description | Text | :one | Description |
| disambiguatingDescription | Text | :one | Disambiguation text |
| identifier | Text/URL | :one/:many | Unique identifier |
| url | URL | :one | Primary URL |
| sameAs | URL | :many | Identity URLs |
| image | URL | :many | Images |

### Temporal Properties

Common time-related properties:

| Property | Type | Cardinality | Common Classes |
|----------|------|-------------|----------------|
| startDate | Date | :one | Event, Role |
| endDate | Date | :one | Event, Role |
| dateCreated | Date | :one | CreativeWork |
| dateModified | Date | :one | CreativeWork |
| datePublished | Date | :one | CreativeWork |
| birthDate | Date | :one | Person |
| deathDate | Date | :one | Person |
| foundingDate | Date | :one | Organization |
| dissolutionDate | Date | :one | Organization |

### Relationship Properties

Properties linking entities:

| Property | Type | Cardinality | Description |
|----------|------|-------------|-------------|
| author | Person/Org | :many | Creator/author |
| contributor | Person/Org | :many | Contributor |
| creator | Person/Org | :many | Creator |
| publisher | Organization | :one | Publisher |
| provider | Person/Org | :one | Provider |
| sponsor | Person/Org | :many | Sponsor |
| funder | Person/Org | :many | Funder |
| organizer | Person/Org | :many | Organizer |
| performer | Person | :many | Performer |
| participant | Person/Org | :many | Participant |

### Location Properties

Place-related properties:

| Property | Type | Cardinality | Common Classes |
|----------|------|-------------|----------------|
| location | Place | :many | Event, Organization, Action |
| address | PostalAddress | :many | Person, Organization, Place |
| birthPlace | Place | :one | Person |
| deathPlace | Place | :one | Person |
| homeLocation | Place | :one | Person |
| workLocation | Place | :one | Person |
| geo | GeoCoordinates | :one | Place |

---

## Module Placement Heuristics

### Decision Tree

```
Is it a person or personal relationship?
  YES → person/
  NO ↓

Is it an organization or business?
  YES → organization/
  NO ↓

Is it a scheduled occurrence?
  YES → event/
  NO ↓

Is it a work of creation (article, book, etc.)?
  YES → creative-work/
  NO ↓

Is it a physical or virtual location?
  YES → place/
  NO ↓

Is it a product, offer, or service?
  YES → product/
  NO ↓

Is it an abstract concept (role, rating, etc.)?
  YES → intangible/
  NO ↓

Is it an action or activity?
  YES → action/
  NO ↓

Is it foundational (Thing, Agent)?
  YES → base/
  NO ↓

Does it fit an existing domain module?
  YES → [domain module]
  NO → misc/ (temporarily, then refactor)
```

### Property Module Placement

**Common Properties** (common/):
- Used by 3+ classes across different modules
- Generic Thing properties (name, description, url)
- Cross-domain properties (location, image, sameAs)

**Module-Specific Properties** (same module as class):
- Used by 1-2 classes in same module
- Domain-specific (recipeIngredient, medicalCode)
- Tightly coupled to class semantics

---

## Schema.org URLs

### Class Lookup
```
https://schema.org/[ClassName]
```
Examples:
- https://schema.org/Person
- https://schema.org/Organization
- https://schema.org/Recipe

### Property Lookup
```
https://schema.org/[propertyName]
```
Examples:
- https://schema.org/birthDate
- https://schema.org/worksFor
- https://schema.org/location

### Full Hierarchy
```
https://schema.org/docs/full.html
```

### JSON-LD Context
```
https://schema.org/docs/jsonldcontext.json
```

---

## Common Research Patterns

### Pattern 1: New Class Addition

1. Fetch class definition from Schema.org
2. Trace hierarchy to Thing
3. List all inherited properties
4. List direct properties
5. Check template for parent class
6. Determine module placement
7. Map property types to Logseq
8. Generate class definition
9. Generate property definitions
10. Document use cases

### Pattern 2: Property Reuse Check

1. Search template for property name
2. If exists:
   - Check current classes using it
   - Check if new class should use it
   - Update property's :build/property-classes
3. If not exists:
   - Fetch Schema.org definition
   - Map to Logseq type
   - Determine cardinality
   - Assign to classes
   - Add to appropriate module

### Pattern 3: Missing Properties Discovery

1. Fetch Schema.org class properties
2. Extract current template class properties
3. Compare lists (Schema.org - template)
4. Prioritize missing properties:
   - High: Commonly used, core functionality
   - Medium: Useful but not essential
   - Low: Specialized or rarely used
5. Recommend additions in phases

---

## Validation Checks

Before recommending any addition:

### Schema.org Validity
- [ ] Class exists on schema.org
- [ ] Property exists on schema.org
- [ ] Using official naming (exact match)
- [ ] Hierarchy is correct
- [ ] Property types are official

### Template Compatibility
- [ ] Not already in template (search)
- [ ] Parent class exists (if applicable)
- [ ] Module exists (or plan to create)
- [ ] Type mapping is clear
- [ ] Cardinality decision is justified

### Best Practices
- [ ] Follows naming conventions
- [ ] Reuses existing properties where possible
- [ ] Groups related additions together
- [ ] Provides use case examples
- [ ] Estimates implementation effort

---

## Integration Examples

### Example: Adding Recipe Class

**Schema.org Research:**
```
Class: Recipe
Parent: CreativeWork
Module: creative-work/
Properties: 15 new (recipeIngredient, cookTime, etc.)
```

**Template Implementation:**
```clojure
;; In source/creative-work/classes.edn
:user.class/Recipe-aB3cD4
{:block/title "Recipe"
 :build/class-parent :user.class/CreativeWork-xY9zK
 :build/class-properties
 [:user.property/recipeIngredient-eF5gH6
  :user.property/recipeInstructions-iJ7kL8
  :user.property/cookTime-mN9oP0
  ...
  :user.property/name-xyz123  ; inherited from Thing
  :user.property/author-abc456]  ; inherited from CreativeWork
 :build/properties
 {:logseq.property/icon {:id "🍳" :type :emoji}
  :logseq.property/description "A recipe with cooking instructions"}}

;; In source/creative-work/properties.edn
:user.property/recipeIngredient-eF5gH6
{:db/cardinality :db.cardinality/many
 :logseq.property/type :default
 :block/title "recipeIngredient"
 :build/property-classes [:user.class/Recipe-aB3cD4]
 :build/properties
 {:logseq.property/icon {:id "🥕" :type :emoji}
  :logseq.property/description "Ingredient for the recipe"}}
```

---

## Resources

### Official Documentation
- [Schema.org](https://schema.org/)
- [Schema.org Full Hierarchy](https://schema.org/docs/full.html)
- [Schema.org Developer Guide](https://schema.org/docs/developers.html)

### Logseq Resources
- [Logseq DB Format](https://docs.logseq.com/#/page/db)
- [Logseq Properties](https://docs.logseq.com/#/page/properties)
- [Logseq Classes](https://docs.logseq.com/#/page/classes)

### Tools
- [Schema.org Validator](https://validator.schema.org/)
- [JSON-LD Playground](https://json-ld.org/playground/)
- [Google Rich Results Test](https://search.google.com/test/rich-results)

---

## Quick Type Reference

```clojure
;; Logseq Property Types
:logseq.property/type :default   ; Text, boolean, general data
:logseq.property/type :node      ; Links to other pages
:logseq.property/type :date      ; Dates and datetimes
:logseq.property/type :url       ; URLs and URIs
:logseq.property/type :number    ; Numbers (integer, float)

;; Cardinality
:db/cardinality :db.cardinality/one   ; Single value
:db/cardinality :db.cardinality/many  ; Multiple values
```
