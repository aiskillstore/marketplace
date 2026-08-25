# Runtime Adaptation

## Questions

Use the host's structured question tool when it exists. Otherwise present numbered options in chat and accept numbers, labels, or free text. Never expose a host-specific tool name to the user.

Batch independent questions. Stop at staffing approval and Decision Summary gates. Do not use tool availability as a reason to self-approve.

## Document authoring

Use the host's document capability, Python with python-docx, or direct OOXML. Resolve this skill's references and scripts relative to the skill directory. Do not assume fixed mount paths, file-presentation helpers, or a client-specific document skill exists.

If no `.docx` authoring path exists, stop. Markdown and HTML are not equivalent deliverables.

## Rendering

Use a real office rendering engine, preferably LibreOffice headless, to convert the latest `.docx` to page images. Inspect every page at 100% zoom. A PDF renderer is evidence about layout, not proof of Microsoft Word behavior.

When Word is available, open the final document there for TOC, field, and target-application verification. Record the exact surface tested.

## Table of Contents

Use real heading styles and a dynamic TOC field for documents with more than eight main sections. Set `w:updateFields` in document settings. If the TOC cannot be updated in Word before delivery, keep the field and give the refresh instruction in chat. Do not place the instruction inside the contract document.

## Delivery

Use the host's artifact-presentation capability when available. Otherwise save to the requested or current directory and report the absolute path. Deliver only the SOW/PWS `.docx`; the handoffs remain chat-only.
