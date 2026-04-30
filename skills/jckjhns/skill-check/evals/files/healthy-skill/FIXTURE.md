---
name: text-summarizer
description: >
  Summarizes text files into concise bullet points. Use when the user wants to summarize
  a document, extract key points from a text file, or create a brief overview of a long
  piece of writing. Also trigger on "give me the highlights" or "what are the main points".
  Do NOT use for translation, rewriting in a different style, or non-text file types.
---

# Text Summarizer

Produces concise, structured summaries from plain text files.

## Workflow

1. Read the user's text file from /mnt/user-data/uploads/
2. Run the extraction script to identify key sentences:
   `python3 scripts/extract_key_points.py --file <input-path> --max-points 10`
3. Review the extracted points and refine them into a clear summary
4. Save the summary as a markdown file to /mnt/user-data/outputs/

## Input
- A plain text file (.txt) or markdown file (.md)

## Output
- A markdown file with a title, bullet-point summary, and word count

## Guidelines
- Keep summaries under 200 words to ensure they're genuinely concise
- Preserve the original document's key terminology
- If the input is under 100 words, tell the user it's already short enough
  and offer to restructure it instead
