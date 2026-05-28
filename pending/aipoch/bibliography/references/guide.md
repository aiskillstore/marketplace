# Literature Cataloging Rules and Field Descriptions

## Input and Preprocessing

- Inputs are `.pdf`, `.md`, `.docx`, and `.txt` files in the specified directory.
- `.pdf`: Must first use `pdf-extract` to generate Markdown; use only the `.md` content.
  - Prioritize searching for the `pdf-extract` skill directory (containing `SKILL.md`) at the same level as the parent directory of this skill.
  - If not found, confirm the actual path of `pdf-extract` with the user.
- `.docx`: Extract body text, preserving heading and paragraph order.
- `.md`/`.txt`: Read directly.
- If garbled characters appear or key fields are not recognized, first attempt to identify and read using the original encoding (commonly GB18030/GBK) before extraction.

## Summary Markdown

- First, generate a summary Markdown file, including for each paper: Title, Abstract, Keywords, Experimental Methods, Conclusion Points, and Comments.

## Abstract and Comments

- Abstract: Use the original abstract from the literature; default to Chinese. If "Abstract" is missing, use the part closest to an abstract from structures like "Summary/Highlights/Objective-Method-Result-Conclusion". If the original is in English, the abstract must be translated into Chinese.
- Comments: A one-sentence evaluation, avoiding harsh criticism; use tactful phrasing if the value is low; default to Chinese. If the original is in English, the comment must be translated into Chinese.

## Classification Fields

- `Keywords (theme)`: Use the original keywords from the literature. If no keywords are identified, summarize 3–5 phrases based on the abstract and append "(Generated based on abstract)" to the end of the keywords field.
- `Experimental Methods (method)`: Write only the names of the methods.
- `Conclusion Points (conclusion)`: One sentence encompassing all key points. If the original is in English, it must be translated into Chinese.
- Use `|` to separate multiple items; prefer phrases over long sentences.

## CSV Output Specifications

- Must be saved in UTF-8 encoding before output to avoid garbled characters; one document per line.
- Field order (headers default to Chinese; headers and content switch to the specified language only when requested by the user):
  1. `Filename`
  2. `File Type`
  3. `Keywords`
  4. `Experimental Methods`
  5. `Conclusion Points`
  6. `Abstract`
  7. `Comments`
- Wrap fields containing commas or line breaks in double quotes.
- In case of parsing failure: Write the reason for failure in `Abstract`, fill `Comments` with "Not generated", and fill classification fields with "Unidentified".
- Output content must have values; if extraction is impossible, fill with "Unidentified" to avoid empty fields.
- Only one CSV file is to be output finally. The summary Markdown must be saved to `outputs/`, and the CSV should be based on the summary Markdown.
- Only 2 files are allowed to be generated (Summary Markdown + CSV); no temporary/intermediate/auxiliary files (including extracted text, cache, logs, images, backups, etc.) may be output. If format conversion or extraction is required, please complete it in memory and ensure it is not saved to disk, or delete all non-target files before output.
- It is strictly forbidden to use PowerShell to directly write or manipulate CSV/Markdown to avoid encoding and line break issues. Must use UTF-8 encoding for generation and saving.
- No script usage is required; the model directly reads the literature content to judge and extract, without relying on rigid rules.