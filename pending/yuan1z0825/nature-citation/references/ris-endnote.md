# RIS, EndNote, and Zotero RDF Output

EndNote can import RIS files using the `Reference Manager (RIS)` import option. Use `.ris` as the
default exchange format because it is plain text, widely supported, and easy to inspect.

## RIS mapping for journal articles

Use these tags:

```text
TY  - JOUR
TI  - Article title
AU  - Author, Given
T2  - Journal title
JO  - Journal title
PY  - Publication year
Y1  - YYYY/MM/DD when available
VL  - Volume
IS  - Issue
SP  - First page or article number
EP  - Last page
DO  - DOI
UR  - URL
SN  - ISSN
N2  - Abstract or short metadata note, only when safely available
ER  -
```

Rules:

- Write one `AU` line per author.
- Use `TY  - JOUR` for journal articles.
- End every record with `ER  -`.
- Do not invent missing fields.
- Prefer DOI over URL when both exist.
- Keep notes concise; avoid copying long abstracts into RIS unless the source terms allow it.

## EndNote import instruction

Tell the user:

```text
In EndNote: File > Import > File, choose the `.ris` file, set Import Option to
Reference Manager (RIS), then import.
```

Menu labels vary slightly by EndNote version and operating system, so avoid over-specific UI claims
unless the user gives their exact EndNote version.

## Zotero RDF guidance

Use `.rdf` when the user explicitly asks for Zotero import/export.

Preferred structure:

```xml
<rdf:RDF ...>
  <bib:Article rdf:about="https://doi.org/...">
    <z:itemType>journalArticle</z:itemType>
    <dcterms:isPartOf rdf:resource="urn:..."/>
    <bib:authors>...</bib:authors>
    <dc:title>...</dc:title>
    <dc:date>YYYY-MM-DD</dc:date>
    <dc:identifier>...</dc:identifier>
    <bib:pages>...</bib:pages>
    <z:citationKey>...</z:citationKey>
  </bib:Article>
  <bib:Journal rdf:about="urn:...">...</bib:Journal>
</rdf:RDF>
```

Rules:

- Export one `bib:Article` per citation.
- Represent authors as `foaf:Person` nodes inside `rdf:Seq`.
- Deduplicate journal container nodes by journal/ISSN/volume/issue identity.
- Do not invent abstracts, attachments, or fields that are not present in metadata.
