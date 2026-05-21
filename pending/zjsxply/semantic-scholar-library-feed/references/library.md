# Library Workflow

## Goal

Use this workflow for private folder inspection, folder diffing, and adding papers to a Library folder.

## Verified folder entry endpoint

Fetch folder contents with:

- `GET /api/1/library/folders/<folderId>/entries`

Verified query parameters:

- repeated `entrySourceTypeFilter`
- `q`
- `page`
- `pageSize`
- `sort=date_added_to_library`

Known limit:

- `pageSize > 100` returns `400`
- error code: `LibraryBadPaginationRequestError`

Prefer `pageSize=100` and paginate if needed.

## Verified add-to-folder endpoint

Add a paper to a folder with:

- `POST /api/1/library/folders/entries/bulk`

Verified request body shape:

```json
{
  "paperId": "...",
  "paperTitle": "...",
  "folderIds": [13895811],
  "annotationState": null,
  "sourceType": "Library"
}
```

Current verified behavior for the tested account: posting a new `folderIds` list appended the target folder and did not remove the paper from its existing folder. Treat this as an empirical observation, not a documented contract.

## Graph API path for `paperId`

When BibTeX entries already contain arXiv identifiers, prefer:

- `POST https://api.semanticscholar.org/graph/v1/paper/batch?fields=paperId,title,year,url,externalIds`

Pass identifiers like:

- `ARXIV:2602.08234`

This path was more reliable for bulk resolution than title search.

## Search caveats

- `/search` SSR did not include actual search result papers.
- Direct `POST /api/1/search` returned `202` with an empty body in the tested replay.
- `graph/v1/paper/search/match` can return a wrong fuzzy match even on `200`.

Do not trust title search alone. For `search/match`, require an exact title check before using the result.

## Practical folder sync recipe

1. Parse BibTeX and extract `title` plus stable identifiers like `eprint`.
2. Resolve `ARXIV:...` items through `graph-batch`.
3. Fetch folder contents through `folder-entries`.
4. Diff by `paperId` first.
5. Add only missing papers through `folder-add`.
6. Re-fetch the folder and verify counts.

## CLI entry points

- `folder-entries`: dump one folder or all its pages
- `folder-add`: add a paper to one or more folders
- `graph-batch`: resolve arXiv or DOI identifiers to Semantic Scholar records

Typical folder export:

```bash
python3 scripts/semantic_scholar_cli.py folder-entries \
  --folder-id 13895811 \
  --all-pages \
  --output /tmp/folder-13895811.json
```
