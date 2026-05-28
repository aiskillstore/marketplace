BioGRID ORCS REST Service
=======================

Base URL: https://orcsws.thebiogrid.org/

Authentication
--------------
All queries must include `accesskey=[ACCESSKEY]`.

Endpoints
---------

### 1. Fetch Supported Organisms
- **URL**: `/organisms/`
- **Params**: `accessKey`, `format` (tab/json)

### 2. Fetch Controlled Vocabulary Categories
- **URL**: `/vocabs/`
- **Params**: `accessKey`, `format`

### 3. Fetch Vocabulary Terms
- **URL**: `/vocab/<VOCAB_CATEGORY_ID>`
- **Params**: `accessKey`, `format`

### 4. Fetch Screens
- **URL**: `/screens/`
- **Params**:
  - `start`, `max` (Pagination)
  - `screenType`, `throughput`, `experimentalSetup`, `conditionName`
  - `libraryName`, `libraryType`, `libraryMethodology`, `screenFormat`
  - `enzyme`, `cellLine`, `cellType`, `phenotype`, `statisticalAnalysis`
  - `organismID`, `pubmedID`, `screenID`

### 5. Fetch Screen Scores
- **URL**: `/screen/<SCREEN_ID>`
- **Params**:
  - `hit` (yes/no/all)
  - `score[X]Min`, `score[X]Max`
  - `idType`, `geneID`, `name`

### 6. Fetch Gene Scores (Single Gene)
- **URL**: `/gene/<GENE_ID>`
- **Params**: `hit`, `score[X]Min`, `score[X]Max`

### 7. Fetch Gene Scores (Multiple Genes)
- **URL**: `/genes/`
- **Params**:
  - `geneID` OR `name` (Required)
  - `organismID`
  - `hit`, `score[X]Min`, `score[X]Max`

Valid Params Notes
------------------
- `accessKey`: 32 char alphanumeric string.
- `format`: "tab" or "json" (default "tab" in API, "json" in this skill).
- `header`: "yes" or "no" (tab only).
