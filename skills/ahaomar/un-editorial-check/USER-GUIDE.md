# User Guide — Check Your Document Before You Share It

**For United Nations staff, researchers, students and professionals. No coding knowledge needed.**

This is the simple version of this project. Developers should read [README.md](README.md) instead, which covers installation, all rule identifiers and advanced options.

## What the tool does, in plain words

You point it at an English document. It reads the text the way an editorial reviewer would and reports:

- spelling and grammar problems, such as a word typed twice or a missing space between two sentences;
- wording that may sound impolite, too strong, promotional or one-sided;
- statements about sensitive topics, such as territorial disputes, that take one side — the report suggests neutral wording and treats every side of a claim the same way;
- date, number and United Nations terminology mistakes common in formal reports.

It then writes a PDF report named `un-editorial-review.pdf`. The report shows your current wording next to the suggested wording, so you can see every proposed change before you accept any of them.

**Your document is never changed on its own.** Your AI assistant must stop and ask for your permission first, and it must never invent wording that the report does not contain.

## What you need (one-time setup)

- **An AI assistant that can run tools on your computer.** This guide uses Claude Code as the example. Other assistants work too.
- **Node.js version 18 or newer.** It is a free tool that lets your computer run programmes like this one. If your computer does not have it, ask your IT colleague to install it — it takes a few minutes.
- **Your document.** The tool reads Markdown (`.md`, `.markdown`), plain text (`.txt`), web pages (`.html`, `.htm`), script files (`.js`, `.mjs`, `.cjs`, `.jsx`, `.ts`, `.tsx`), PDF documents (`.pdf`), Word documents (`.docx`) and OpenDocument documents (`.odt`). If the file uses any other format the tool reports exit code 2 and changes nothing.

**If your document is a PDF, read this before you rely on the result.** A PDF is a finished, printed page, not an editable text file. The tool can pull the words out of it and check them, but it cannot tell a quotation from a paragraph of your own writing, so it checks everything as if you had written all of it. You may therefore get a warning about wording that appears inside quotation marks. That is expected, and it is the format, not a mistake in your document. If a warning matters to you, check the quoted part by hand.

Three kinds of PDF are not read at all, and each one is reported as exit code 2 with the reason, never as a clean result: a **scanned PDF** whose pages are pictures of text, because the tool does not read images or recognise handwriting and will not pretend to; an **encrypted PDF** protected by a password; and a PDF whose **fonts hold no way to read the characters**, where the tool will not guess. For any of these, get the text out by other means — export the document as text, or use a tool of your own — and paste it into a `.txt` file. The tool never changes a PDF: it reports what it found and leaves the document exactly as it was.

**Word and OpenDocument documents** (`.docx` and `.odt`) are read directly: the body text is recovered paragraph by paragraph and checked like any prose file. Three honest limits apply. Text boxes, headers, footers, footnotes, endnotes and comments are not read. A paragraph struck out with tracked changes is not checked, because struck copy is not part of the document a reader sees. And the report's line numbers address paragraphs, counted from the top of the document, not printed pages. An encrypted document, a file that is not really a document, and a document whose body holds no text are reported as exit code 2 with the reason, never as a clean result. The tool never changes a Word or OpenDocument file.

To confirm Node.js is ready, ask your AI assistant to run `node --version`. It should answer with version 18 or higher.

## Step 1 — Open your AI assistant in your document folder

Start your assistant inside the folder that holds your document. With Claude Code: open a terminal window, change into your document folder, type `claude`, and press Enter.

## Step 2 — Copy and paste the prompt below

Copy everything inside the box, paste it into your assistant, and replace `<PASTE YOUR FILE NAME HERE>` with the name of your file — for example `statement.md`.

```text
Check a document for me using the tool "un-editorial-check", a free open-source
editorial checker for United Nations style English copy. Follow these steps in order:

1. The tool needs no installation: it runs through npx (Node.js 18 or newer).
2. Check my file and write a PDF report:
   npx -y un-editorial-check "<PASTE YOUR FILE NAME HERE>" --report un-editorial-review.pdf
3. Summarise what was found: how many issues of each severity, the most important
   issues, and for each one the current wording beside the suggested wording.
   Tell me where the PDF report was saved.
4. Stop and ask me exactly one question: Apply these corrections?
   Do not modify any file before I explicitly approve.
5. Only after I approve, for example when I answer "go ahead":
   - apply the automatic corrections:
     npx -y un-editorial-check "<PASTE YOUR FILE NAME HERE>" --fix --apply
   - rewrite the remaining flagged passages using ONLY the suggested wording from the
     report. If the report gives no suggested wording for a finding, do not invent any:
     ask me what should be written instead.
6. Run the check one more time and tell me honestly what is left. Only say the document
   is clean if the tool reports exit code 0: no findings under the enabled, documented local rules.

My document is: <PASTE YOUR FILE NAME HERE>
```

## Step 3 — Read the summary, then decide

Your assistant checks the document, shows you what it found, and points you to the PDF report. It then asks one question: `Apply these corrections?`

- Answer **go ahead** and the suggested changes are applied.
- Answer **no**, or anything else, and it stops without touching your file.

## Step 4 — Review the final result

Your assistant runs the check one more time and tells you which issues remain. It only says your document is clean when the tool reports exit code 0, and a clean result means one thing only: no findings under the enabled, documented local rules.

## You stay in control

- Nothing in your document changes before you approve it.
- Suggested wording comes only from the report. If the report has no suggestion, the assistant asks you instead of writing something of its own.
- The tool reviews how text is written. It does not decide whether a statement is true.
- The tool runs on your own computer and never sends your document anywhere. Your assistant has its own privacy policy, which is separate.
- Keep a copy of your original file if you want to be able to go back.

## Things worth knowing

- **Cost:** the tool itself is free to download and use, under the MIT licence. Your AI assistant subscription is separate.
- **Language:** the checks are written for English copy in United Nations style.
- **File formats:** Markdown (`.md`, `.markdown`), plain text (`.txt`), web pages (`.html`, `.htm`), script files (`.js`, `.mjs`, `.cjs`, `.jsx`, `.ts`, `.tsx`), PDF documents (`.pdf`), Word documents (`.docx`) and OpenDocument documents (`.odt`). Any other format is reported as exit code 2 and nothing is changed.
- **PDF documents:** the words are read out of the PDF and checked, and every part is checked as your own writing because a printed page gives no way to tell a quotation from a paragraph. Scanned pages, password-protected files and files whose fonts cannot be read are reported as exit code 2 with the reason and are never presented as a clean result. Line and page numbers point at the printed page. The tool never writes to a PDF, so paste the text into a `.txt` file if you want corrections applied for you.
- **Slash command:** if your assistant supports commands, a technical colleague can install the `/un-diplomatic-agent` command once by following [README.md](README.md). After that you can start by typing that command instead of pasting the prompt.
- **Where the rules come from:** the full list of checks, with institutional sources, is in [rules/catalogue.json](rules/catalogue.json) and explained in the README.
- **What a clean result means:** the tool reports `No findings under the enabled, documented local rules.` Nothing stronger follows from that sentence.
- **How results are grouped:** clear-cut findings, heuristic items for editorial review, a separate queue for harmful or discriminatory wording, a queue for diplomatic sensitivity, and optional audits. Each finding shows which of the twelve kinds of check it belongs to, where its rule comes from, how confident it is, what its limits are and what a person should do next.
- **Repeated paragraphs:** a long paragraph copied word for word inside the same file is reported once, with the line where the first copy was. A whole paragraph is compared, not the pieces the markup cut it into, so a word in italics, a link, or a word the styling broke in half does not hide the repeat. A picture or a line break inside the paragraph joins the words either side of it with a space, which is what a reader sees there too. A Markdown document has no navigation surface, so a standing paragraph repeated under your own section headings inside one file is reported too; silence it with `ue:ignore` where the repetition is deliberate, the same way you would silence any other finding.
- **A report you can keep:** the assistant can be asked to write a PDF, or a single self-contained HTML page, next to your document. Both begin with a heading saying that this is an editorial review, and both carry page numbers and a credit line at the foot. They open with the scope of the scan and its counts, then list the twelve kinds of check with how many of each this scan found, then set out the findings under their own headings — a heading for a group that found nothing stays in place and says that the group was checked, so a clean group is never mistaken for one that was never looked at. Every finding carries its rule, its limits and what to do about it, and the same issue in several places is listed once, with a count and a table of where each one is, so that one repeated mistake does not fill the report; a technical reader can ask for `--report-detail full` to have one entry per finding instead. Where a section would print more than twenty findings of its own, the report says how many it left out and prints the command that lists the rest; the summary counts and the machine-readable output always carry every finding, and asking for the full layout caps nothing. Paths in a report are written relative to the folder the scan was pointed at, which the report states once, so they still name the right file when somebody else opens it. Neither file changes anything.
- **Your own house words:** if your organisation insists on particular words, you can put them in a small glossary file and the tool will report where the draft disagrees with you. Those results are marked as your own terminology throughout, never as a United Nations rule, and they never change the exit code.
- **Watching a draft while you edit:** a watch mode re-checks whenever you save, until you stop it. It is meant for one person editing, and it deliberately gives no exit code, so it must not be used in an automated build.

## For technical readers

Developers, and anyone who wants the full rule list, CI integration, configuration profiles, the report format, the house glossary or the watch mode, should read [README.md](README.md) and [docs/GLOSSARY-AND-WATCH.md](docs/GLOSSARY-AND-WATCH.md).
