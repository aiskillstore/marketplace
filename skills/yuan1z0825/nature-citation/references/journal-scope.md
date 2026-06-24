# Journal Scope

The skill's default journal-family boundary is intentionally practical rather than exhaustive. Use it
to find likely Nature/CNS-family candidates, then verify exact journal status on official pages if the
author needs a strict portfolio definition.

## Default families

### Nature Portfolio

Include:

- `Nature`
- journals beginning with `Nature `, such as `Nature Medicine`, `Nature Biotechnology`,
  `Nature Methods`, `Nature Materials`, `Nature Genetics`, `Nature Communications`
- `Communications` journals, such as `Communications Biology`, `Communications Chemistry`,
  `Communications Materials`, `Communications Earth & Environment`, `Communications Medicine`
- `npj` journals
- `Scientific Reports`

Be careful with unrelated titles that include the common word "nature".

### Science family

Include by default:

- `Science`
- `Science Advances`
- `Science Translational Medicine`
- `Science Signaling`
- `Science Immunology`
- `Science Robotics`

The AAAS Science Partner Journal program is not included by default unless the user asks for partner
journals or broader AAAS coverage.

### Cell Press

Include the flagship `Cell`, major primary-research Cell Press journals, Cell Reports titles, and
Trends review journals. The local script recognizes common Cell Press titles and any title beginning
with `Trends in `.

Because Cell Press launches and reorganizes titles over time, verify official pages for exhaustive
coverage or a current journal list.

## Flagship-only scope

Use only:

- `Nature`
- `Science`
- `Cell`

This is appropriate when the user says "只看正刊", "主刊", "flagship only", or explicitly excludes
subjournals.

## Official source notes

- Crossref REST API can retrieve scholarly metadata, search works, and filter exact fields such as
  `container-title` and `issn`.
- NCBI E-utilities provide structured access to PubMed and other Entrez databases; observe request
  frequency guidance.
- EndNote documents `Reference Manager (RIS)` as an import option for RIS files.
- Nature Portfolio, AAAS, and Cell Press official pages should be checked when exact current journal
  coverage matters.
