# Security policy

Report suspected vulnerabilities privately through the repository's GitHub security-advisory form; do not open a public issue with exploit details.

The checker does not execute repository content or fetch third-party assets. `--fix` is restricted to regular `.txt`, `.md` and `.markdown` files, honours spelling allowlists, and rejects symbolic links, hard links and — since PDF support — every other format including `.pdf`. It re-checks descriptor identity and link count immediately before writing; this assumes no hostile concurrent filesystem mutation and is not a race-proof sandbox. Profiles may be explicit external local files, but the loader rejects symbolic links, non-regular files and hard-linked files.

## Opening a PDF

PDF support (1.3.0) changes what the tool reads from a file, so it is stated here rather than left to the reader of the source. A PDF is a common malware-delivery format, and the question worth answering is what happens when a hostile document is opened.

The tool **parses bytes and nothing else**. It never renders a page, never runs JavaScript embedded in the document, never follows an action or a launch target, and never fetches a remote resource. Concretely:

- No module in `lib/` or `bin/` imports `node:http`, `node:net`, `node:dns` or `node:tls`, and none calls the global `fetch`. Across the shipped code the only Node built-ins imported are `node:fs`, `node:path`, `node:url`, `node:process` and `node:buffer`. The PDF text engine is permitted one more, `node:zlib`, for stream decompression, and nothing else. There is no code path by which opening a document can cause a network request.
- No module in `lib/` or `bin/` imports `node:child_process`, and none calls `exec` or `spawn`. A document cannot cause a subprocess to start. The one dynamic import in the package, the PDF engine lookup, resolves two fixed module names and takes nothing from the document or the command line.
- No module in `lib/` or `bin/` uses `eval` or the `Function` constructor. The PDF text layer reads text-showing operators, font encodings and cross-reference tables as data; it evaluates nothing a document contains.
- The PDF extraction path (`lib/pdf-extract.mjs`, with `lib/units.mjs` and `lib/position.mjs`) performs no file-system access of its own. The bytes are read once by `lib/cli.mjs` and handed down; nothing in the extraction path can open a second file, follow a link out of the document, or resolve a path the document names.

A PDF is also never written. `--fix` refuses it through the same prose-only gate that refuses HTML, JavaScript and JSON, so opening a document for scanning cannot modify it.

### What the parser does not defend against

Reading untrusted bytes is still parsing untrusted input, and the honest statement is where that confidence stops:

- A malformed or hostile document is expected to **refuse** with exit `2` and a named reason — never to read partially, and never to report a clean run. A document too damaged to parse produces `MALFORMED`; a document whose font encoding cannot be recovered produces `UNDECODABLE_FONT` rather than a best-effort guess at the characters. The guarantee is refusal, not immunity.
- A document crafted to consume a great deal of time or memory while being decompressed is a **denial-of-service** risk. There is no sandbox, no resource cap and no time limit around PDF parsing, and a hostile PDF that parses successfully is still screened like any other input.
- Recovery is fail-closed but not verified against a reference implementation. The tool can prove that an encoding resolved and a structure held; it cannot prove that its reading of a document matches a conforming reader's. A wrong-but-resolvable reading is not detectable by this tool.
