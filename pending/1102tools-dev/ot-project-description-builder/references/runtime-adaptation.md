# Runtime Adaptation

Describe operations by capability. Do not hardcode host-generated tool names, sandbox paths, or delivery functions.

## Questions

- Use the host's structured multi-choice input when available.
- Otherwise present numbered options in chat and accept a number, label, or free-text answer.
- Keep Stage A authority confirmation and the Decision Summary as hard stops in every runtime.

## Source documents

- Use the host's document or PDF reader for supplied files.
- Extract explicit decisions, unresolved terms, milestone candidates, and pricing content that must be excluded.
- Preserve source provenance and distinguish performer assertions from Government-approved facts.

## DOCX generation

- Use the host's native document-authoring capability when available.
- Otherwise use a local standards-compliant DOCX library.
- Use an agency or consortium template when supplied. Do not silently replace it with a generic style.
- Save to a writable task-specific location; never expose internal file-system paths in the artifact.

## Validation and rendering

- Run the bundled validator with Python 3.10 or later and `python-docx`.
- Render with Microsoft Word or LibreOffice when available and identify the engine used.
- If LibreOffice is the only engine, do not claim Microsoft Word validation.
- If rendering is unavailable, do not claim visual QA. Report the missing layer before delivery.

## Delivery

- Present the `.docx` through the host's file-delivery capability.
- For a dynamic TOC, state: `Open the document in Word, press Ctrl+A (Cmd+A on Mac), then F9 (or Fn+F9) to update all fields and page numbers.`
- Emit the milestone handoff in chat only.
- Never create a second handoff file merely because the runtime supports multiple artifacts.
