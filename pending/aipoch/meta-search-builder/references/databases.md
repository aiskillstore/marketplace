# Database Retrieval Syntax Reference

## Contents

1. [PubMed](#1-pubmed)
2. [Cochrane Library](#2-cochrane-library)
3. [Embase](#3-embase)
4. [Web of Science](#4-web-of-science)
5. [CNKI](#5-cnki)
6. [Wanfang](#6-wanfang)
7. [VIP](#7-vip)

---

## 1. PubMed

### Syntax

# Database Search Syntax Reference

## Table of Contents

1. [PubMed](#1-pubmed)
2. [Cochrane Library](#2-cochrane-library)
3. [Embase](#3-embase)
4. [Web of Science](#4-web-of-science)
5. [CNKI (China National Knowledge Infrastructure)](#5-cnki)
6. [Wanfang Data](#6-wanfang-data)
7. [VIP Database](#7-vip-database)

---

## 1. PubMed

### Syntax Rules

- Use MeSH headings and free-text terms
- Connect synonyms with `OR` and different concepts with `AND`
- Enclose multi-word terms in quotes, e.g., "ovarian cancer"
- Add an RCT filter at the end

### MeSH Term Handling

For keywords that have MeSH terms, list the MeSH term and all Entry Terms, connected with `OR`.

### RCT Filter

```
AND ((((((((randomized controlled trial [pt]) OR (controlled clinical trial [pt])) OR (randomized [tiab])) OR (placebo [tiab])) OR (drug therapy [sh])) OR (randomly [tiab])) OR (trial [tiab])) OR (groups [tiab])) NOT ((animals [mh]) NOT (humans [mh]))
```

### Example

```
("Ovarian Neoplasms" OR "Neoplasm, Ovarian" OR "Ovarian Neoplasm" OR "Ovary Cancer" OR "Ovarian Cancer") AND ("Bevacizumab" OR "Avastin" OR "Mvasi") AND ("adverse events" OR "adverse effects" OR "side effects" OR "complications" OR "toxicity")
```

---

## 2. Cochrane Library

### Syntax Rules

- Use MeSH terms and Entry Terms
- Enclose multi-word terms in quotes, e.g., "Pustulosis of Palms and Soles"
- Connect synonyms with `OR` and different concepts with `AND`
- Group each set of keywords with parentheses `()`

### Example

```
(Psoriasis OR Psoriases OR "Pustulosis of Palms and Soles" OR "Pustulosis Palmaris et Plantaris" OR "Palmoplantaris Pustulosis") AND ("Vitamin D")
```

---

## 3. Embase

### Syntax Rules

- Use Emtree subject headings; append `/exp` to explode terms
- Field qualifiers: `:ab,ti` (abstract and title), `:ti` (title), `:ti,ab,kw` (title, abstract, keywords)
- Include at least 5 free-text synonyms when possible
- Use English for queries and terms

### Example

```
'schizophrenia'/exp OR 'schizophrenia' AND 'add on therapy' OR 'adjunctive therapy' OR 'augmentation therapy' OR 'concomitant therapy' OR 'addition therapy' OR 'additional therapy'
```

---

## 4. Web of Science

### Syntax Rules

- Use field tag prefixes: `TS=` (topic), `TI=` (title), `AK=` (author keywords)
- Enclose each search expression with parentheses, e.g., `TS=(ovarian cancer)`
- Connect synonyms with `OR` and different concepts with `AND`

### Example

```
(TS=(pain)) AND ((TS=(agitation) OR TS=(sedation)) AND ((TS=(delirium) OR TS=(immobility)) OR TS=(sleep)))
```

---

## 5. CNKI (China National Knowledge Infrastructure)

### Syntax Rules

- Chinese-language results expected
- Field tags:
  - `SU=` Subject
  - `TKA=` Title/Keywords/Abstract
  - `KY=` Keywords
  - `TI=` Title
  - `FT=` Full text
  - `AB=` Abstract
  - `CO=` Subheading
- Enclose search terms in single quotes, e.g., `SU='osteoporosis'`
- Connect synonyms with `OR` and different concepts with `AND`
- Group each set with parentheses `()`

### Example

```
(SU='osteoporosis' OR SU='decreased bone mineral density' OR SU='bone loss' OR SU='reduced bone mass') AND (SU='education' OR SU='health education' OR SU='educational intervention') AND (SU='random' OR SU='randomized' OR SU='RCT' OR KY='randomized controlled trial')
```

---

## 6. Wanfang Data

### Syntax Rules

- Chinese-language results expected
- Field label formats: `subject:` / `title or keyword:` / `title:` / `abstract:` / `keyword:`
- Enclose search terms in single quotes
- Connect synonyms with `OR` and different concepts with `AND`

### Example

```
subject:('osteoporosis' OR 'decreased bone mineral density' OR 'bone loss' OR 'reduced bone mass') AND subject:('education' OR 'health education' OR 'educational intervention') AND (subject:('random' OR 'randomized' OR 'RCT') OR keyword:('randomized controlled trial'))
```

---

## 7. VIP Database

### Syntax Rules

- Chinese-language results expected
- Field tags:
  - `U=` Subject
  - `M=` Title/Keywords/Abstract
  - `T=` Title
  - `K=` Keywords
  - `R=` Abstract
- Boolean operators: `AND`, `OR`, `NOT`
- Operator precedence: NOT > AND > OR; use `()` to enforce priority
- Enclose search terms with parentheses

### Example

```
(M=(polycystic ovary syndrome) OR M=(PCOS)) AND (M=(obesity) OR M=(overweight) OR M=(BMI)) AND (M=(hypoglycemic agents) OR M=(metformin) OR M=(SGLT2 inhibitors))
```

---

## Synonym Expansion Principles

1. **Disease names**: List all common names, abbreviations, and former terms for the disease
2. **Interventions**: List generic drug names, brand names, and class names
3. **Outcome measures**: Use general terms such as "adverse events", "safety", "efficacy"
4. **Each keyword**: Provide at least five synonyms or near-synonyms when possible

```
