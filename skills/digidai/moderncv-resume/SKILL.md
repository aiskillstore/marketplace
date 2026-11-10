---
name: moderncv-resume
description: Write, design and export a professional resume with ModernCV (89 templates, vector PDF, free, no account). Use when the user asks to create, rewrite, tailor, format or export a resume or CV, or wants a resume PDF for a job application.
---

# ModernCV resume skill

ModernCV (https://genedai.cv) turns a resume written as JSON into a polished A4 or US Letter PDF in one of 89 templates, and can hand the user an editor link with the resume preloaded. No account or API key is needed.

If the `moderncv` MCP server is connected, use its tools (`get_writing_guide`, `get_example_resume`, `get_resume_schema`, `list_templates`, `import_publications`, `render_preview`, `render_pdf`, `create_editor_link`, `export_latex`). Otherwise use the HTTP API below with `curl`. Over MCP, `render_pdf` returns `download_url`, a link that downloads the PDF for 7 days; give it to the user as a clickable link (a resume too long for a link comes back as an embedded PDF instead). Tool names map to HTTP routes: `get_writing_guide` → `GET /api/agent/guide`, `get_example_resume` → `GET /api/agent/example`, `get_resume_schema` → `GET /resume.schema.json`, `list_templates` → `GET /api/agent/templates`, `import_publications` → `POST /api/agent/publications`, `render_preview` / `render_pdf` / `create_editor_link` / `export_latex` → `POST /api/agent/preview` / `pdf` / `link` / `latex`.

## Workflow

1. **Gather facts.** Ask for the target job title and the user's real history: roles, employers, dates, achievements with numbers, education, skills, links. Never invent employers, dates, degrees or metrics; if a number is missing, ask or leave it out.
2. **Read the guide and an example.** `GET /api/agent/guide?job_title=<title>` returns section order, length, skills to feature, metrics to quantify, example bullets and recommended templates. `GET /api/agent/example?job_title=<title>` returns a complete example resume for that role (use it for structure and tone only; never copy its employers, dates or numbers).
3. **Draft the resume JSON** (shape below). Write 3–5 bullets per recent role, each starting with an action verb and ending with a result. Mirror keywords from the job posting if the user shared one.
4. **Choose a template.** Prefer an ATS-friendly one (`classic`, `modern`, `ivy`, `standard`, `banking`, `oxford`, `lumen`, `meridian`, `keystone`, `vital`, `vanguard`, `timeline`, `executive`, `compact`, …) for online applications. `GET /api/agent/templates?ats_only=true` lists them.
5. **Check the fit.** `POST /api/agent/preview` returns page 1 as PNG; the `x-resume-pages` header gives the page count. If it is over one page and the user wants one, the warnings (`x-resume-warnings`, URL-encoded JSON) give the largest `scale` that fits one page; use it, or shorten bullets, or switch to `compact`.
6. **Deliver.** `POST /api/agent/pdf` for the PDF file, and always `POST /api/agent/link` for a link that opens the editor with the resume loaded so the user can tweak it. Give the user both.

## Academic CVs and LaTeX

- **Publications from ORCID or BibTeX.** `POST /api/agent/publications` with `{ "orcid": "0000-0002-1825-0097" }` or `{ "bibtex": "<.bib contents>" }` returns `{ listed, found, counts, publications: [{ authors, title, venue, year, link, kind }] }`. Narrow a long record with `kinds` (`journal`, `conference`, `preprint`, `book`, `thesis`, `other`) and `from_year` / `to_year`, then put the chosen entries, without `kind`, in `publications`. Ask the user which works to include rather than listing hundreds.
- **An existing LaTeX CV** (Overleaf, moderncv, Awesome-CV, Jake's Resume): read the `.tex` and map it to the JSON below yourself; keep every fact and the wording of each `\item`.
- **LaTeX out.** `POST /api/agent/latex` with `{ resume }` returns `{ filename, engine, tex, overleaf, warnings }`. Save `tex` as a file for the user. To open it in Overleaf, a browser form posts `encoded_snip` (the URL-encoded tex), `snip_name` and `engine` to `https://www.overleaf.com/docs`.

## HTTP API

Base URL: `https://genedai.cv`. JSON in, JSON/PDF/PNG out. CORS is open. Rendering (pdf, preview) is rate limited per IP and globally; on HTTP 429 or 503 wait for `retry-after` seconds and retry once. Full spec: `https://genedai.cv/openapi.json`.

| Method and path | Body / query | Returns |
|---|---|---|
| `GET /api/agent/templates` | `?ats_only=true` | `{ templates: [{ id, name, description, bestFor, atsFriendly, photo, publications, hours, awards, maxPages, preview, page }] }` |
| `GET /api/agent/guide` | `?job_title=Data Analyst` | Writing guide JSON, with `matchedTitle` and `exact` (false when the title wasn't in the directory and the guide is generic) |
| `GET /api/agent/example` | `?job_title=Registered Nurse (RN)` | `{ jobTitle, matchedTitle, exact, family, page, resume }`; `resume` is render-ready (no name or contact details) |
| `POST /api/agent/link` | `{ resume, template?, accent?, font?, scale?, paper? }` | `{ url, template, warnings }` |
| `POST /api/agent/preview` | same | `image/png` of page 1; headers `x-resume-pages`, `x-resume-warnings` |
| `POST /api/agent/pdf` | same | `application/pdf` (A4 or US Letter, selectable text) |
| `POST /api/agent/latex` | `{ resume }` | `{ filename, engine, tex, overleaf, warnings }` |
| `POST /api/agent/publications` | `{ orcid }` or `{ bibtex }`, optional `kinds`, `from_year`, `to_year` | `{ source, listed, found, counts, returned, publications }` |

`template` is an id from the templates list (default `modern`); an unknown one is a 400 `INVALID_TEMPLATE` listing the valid ids. `accent` is `#RRGGBB`. `font` is one of `template, inter, source-sans, lato, roboto, source-serif, charis, garamond, tinos, plex-serif, latin-modern`. `scale` is 0.85–1.15. `paper` is `a4` (default) or `letter`; use `letter` for US and Canadian applications, and check the page count again since Letter pages are shorter.

```bash
curl -s https://genedai.cv/api/agent/pdf \
  -H 'content-type: application/json' \
  -d @request.json -o resume.pdf -D - | grep -i x-resume
# decode the warnings header:
# python3 -c 'import json,sys,urllib.parse; print(json.loads(urllib.parse.unquote(sys.argv[1])))' '<x-resume-warnings value>'
```

## Resume JSON

A JSON Resume document (https://jsonresume.org/schema) also works. The native shape:

```json
{
  "fullName": "Alex Sterling",
  "title": "Senior Product Designer",
  "email": "alex@example.com",
  "phone": "+1 555 012 3456",
  "location": "San Francisco, CA",
  "website": "alexsterling.design",
  "linkedin": "linkedin.com/in/alexsterling",
  "links": [{ "label": "", "url": "dribbble.com/alexsterling" }, { "label": "Case studies", "url": "alexsterling.design/work" }],
  "summary": "Product designer with 6 years of experience ...",
  "experience": [
    {
      "company": "TechNova",
      "role": "Senior Product Designer",
      "startDate": "2021-03",
      "endDate": "",
      "isCurrent": true,
      "description": "- Led the design system, cutting UI build time by 30%\n- Shipped 4 major releases"
    }
  ],
  "education": [{ "school": "California College of the Arts", "degree": "BFA in Interaction Design", "startDate": "2014-09", "endDate": "2018-05" }],
  "projects": [{ "name": "EcoTrack", "link": "github.com/alex/ecotrack", "description": "Carbon tracking app; 12k downloads." }],
  "skills": ["Design: Figma, Prototyping", "User research"]
}
```

- Dates are `YYYY-MM` (other forms such as "March 2021" or "03/2021" are converted, and warned about if unreadable). For a current role set `"isCurrent": true` and `"endDate": ""`; a past role needs an `endDate`.
- `description` holds one bullet per line, each starting with `- `.
- Skills may be grouped as `"Category: item, item"`; templates render the groups.
- `photo` (optional) is a base64 JPEG/PNG/WebP data URL, 3:4, under 200 KB. Only photo templates (`list_templates` → `photo: true`) show it; leave it out for ATS portals and US or UK applications.
- `publications` (optional) is a list of `{ authors, title, venue, year, link }` for academic and research CVs. Templates with `publications: true` in `list_templates` (Scholar, Oxford, Academic, Plain, Text, Graduate) show it, numbered or as a reference list, with the owner's name in bold.
- `awards` (optional) is a list of `{ title, issuer, year, detail }` for grants, fellowships and prizes (`detail` holds an amount or role such as "$450,000, co-PI"), and `talks` (optional) is a list of `{ title, event, location, year }` for invited talks and conference presentations. `teaching` (optional) is a list of `{ course, role, institution, year }` for courses taught and TA roles. The same templates as publications show them; `federal`, `capital` and `campus` show `awards` too, as Honors and Awards (check `list_templates` → `awards: true`).
- `experience[].hours` (optional) is hours worked per week, e.g. `"40"`. The `federal` template (`list_templates` → `hours: true`) shows it; USAJOBS federal resumes need it for every job, along with month/year dates (still pass `YYYY-MM`; Federal prints `MM/YYYY`) and the series and grade in the job title ("Program Analyst, GS-0343-12"). Use `paper: "letter"` for federal resumes and list certifications and licenses as a skills group (`"Certifications: PMP, PMI, 2022; CISSP, ISC2, 2024"`, semicolons between credentials) and a clearance as `"Security Clearance: Top Secret/SCI, active"`; Federal prints them in their own section, one per line, clearance first, and keep them to 2 pages (`list_templates` → `maxPages: 2`); USAJOBS may not consider longer ones, and the render warnings say when a resume runs over.
- `links` holds extra profiles (GitHub, portfolio, X, Dribbble, Behance, Google Scholar, ORCID…). Leave `label` empty for well-known sites; templates detect the site and show its icon. Up to 8.

## Privacy

Resumes sent to `/api/agent/pdf` or `/preview` are rendered and discarded, never stored. A `download_url` carries the resume encrypted and renders it again when opened; nothing is kept on the server. Editor links carry the resume in the URL fragment (`#resume=…`), which browsers don't send to servers; the user's edits are saved only in their browser.
