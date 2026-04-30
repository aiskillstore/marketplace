# Quick Check

## Contents

- [What to run](#what-to-run)
  - [Static integrity tests](#static-integrity-tests) — file existence, orphans, syntax, dependencies, paths
  - [Asset and template validation](#asset-and-template-validation) — images, documents, PDFs, fonts, templates
  - [SKILL.md quality checks](#skillmd-quality-checks) — frontmatter, constraint consistency
  - [Cross-reference consistency](#cross-reference-consistency) — script invocation, inter-file references
  - [Multi-skill dependency checking](#multi-skill-dependency-checking) — detection, verification, compatibility
  - [Security review](#security-review) — script scan, instruction security
  - [Best practices review](#best-practices-review)
  - [What to skip](#what-to-skip)
- [Expected test count](#expected-test-count)
- [Report notes](#report-notes)

---

The fastest path — pure static analysis, no execution. Catches structural problems, missing files,
syntax errors, security red flags, best practice violations, and logical inconsistencies. Ideal
for a sanity check before sharing a skill or when you just want to know if the basics are sound.

## What to run

### Static integrity tests

1. **File existence** — Every file referenced in SKILL.md (scripts, references, assets, templates)
   must exist at the specified path. Use bash to verify:
   ```bash
   test -f "<skill-path>/scripts/build_chart.py" && echo "PASS" || echo "FAIL"
   ```

2. **Orphan detection** — Flag any files in the skill directory that aren't referenced by SKILL.md
   or by any script. These aren't necessarily bugs but worth reporting as "unused files."

3. **Script syntax validation** — For every script file, check it parses without errors:
   - Python: `python3 -c "import ast; ast.parse(open('<file>').read())"`
   - JavaScript/Node: `node --check <file>`
   - Bash: `bash -n <file>`

4. **Dependency check** — For Python scripts, extract imports and check availability:
   ```bash
   python3 -c "import <module_name>" 2>&1
   ```
   For Node scripts, check if referenced packages exist in node_modules or are built-in.

5. **Path validation** — Any hardcoded paths in SKILL.md or scripts (e.g., `/mnt/user-data/outputs/`,
   `/mnt/skills/public/`) — verify they're well-formed and follow expected conventions.

### Asset and template validation

File existence checks (test 1) confirm assets are present, but a zero-byte PNG, a corrupted
DOCX template, or a truncated PDF will pass existence checks while breaking the skill at
runtime. These checks verify that asset files are actually valid.

6. **Asset integrity** — For each file in `assets/` (and any other non-code, non-markdown
   files referenced by the skill), verify it's a valid file of its claimed type:

   **Images** (.png, .jpg, .webp, .gif, .svg):
   ```bash
   python3 -c "
   from PIL import Image
   try:
       img = Image.open('<file>')
       img.verify()
       print(f'PASS: {img.format} {img.size[0]}x{img.size[1]}')
   except Exception as e:
       print(f'FAIL: {e}')
   "
   ```
   For SVG, check it's valid XML with an `<svg>` root element:
   ```bash
   python3 -c "
   import xml.etree.ElementTree as ET
   tree = ET.parse('<file>')
   root = tree.getroot()
   assert 'svg' in root.tag.lower(), 'Not an SVG'
   print('PASS: valid SVG')
   "
   ```

   **Documents** (.docx, .pptx, .xlsx):
   These are ZIP-based formats. A quick validity check is to confirm they're openable:
   ```bash
   python3 -c "
   # For .docx
   from docx import Document
   doc = Document('<file>')
   print(f'PASS: {len(doc.paragraphs)} paragraphs')
   "
   ```
   ```bash
   python3 -c "
   # For .pptx
   from pptx import Presentation
   prs = Presentation('<file>')
   print(f'PASS: {len(prs.slides)} slides')
   "
   ```
   ```bash
   python3 -c "
   # For .xlsx
   from openpyxl import load_workbook
   wb = load_workbook('<file>')
   print(f'PASS: {len(wb.sheetnames)} sheets')
   "
   ```
   If the required library isn't available, fall back to checking the file is a valid ZIP
   (since DOCX/PPTX/XLSX are all ZIP containers):
   ```bash
   python3 -c "
   import zipfile
   assert zipfile.is_zipfile('<file>'), 'Not a valid ZIP-based document'
   print('PASS: valid ZIP container')
   "
   ```

   **PDFs** (.pdf):
   Check the file starts with the PDF magic bytes and isn't truncated:
   ```bash
   python3 -c "
   with open('<file>', 'rb') as f:
       header = f.read(5)
       assert header == b'%PDF-', f'Not a PDF (header: {header})'
       f.seek(-32, 2)  # Check near end for EOF marker
       tail = f.read()
       assert b'%%EOF' in tail, 'PDF may be truncated (no %%EOF marker)'
       print('PASS: valid PDF structure')
   "
   ```

   **Fonts** (.ttf, .otf, .woff, .woff2):
   Check the file is non-empty and starts with expected magic bytes:
   ```bash
   python3 -c "
   import os
   size = os.path.getsize('<file>')
   assert size > 0, 'Font file is empty'
   with open('<file>', 'rb') as f:
       header = f.read(4)
   # TTF/OTF start with specific signatures
   valid_headers = [b'\x00\x01\x00\x00', b'OTTO', b'true', b'typ1', b'wOFF', b'wOF2']
   assert any(header.startswith(h) for h in valid_headers), 'Unrecognized font format'
   print(f'PASS: font file, {size} bytes')
   "
   ```

   **JSON/XML config files:**
   If assets include JSON or XML files (configs, data files), verify they parse:
   ```bash
   python3 -c "import json; json.load(open('<file>'))"
   python3 -c "import xml.etree.ElementTree as ET; ET.parse('<file>')"
   ```

   **Catch-all for unknown types:**
   For file types not listed above, check the file is non-empty. A zero-byte file is
   almost always a mistake:
   ```bash
   test -s "<file>" && echo "PASS: non-empty" || echo "FAIL: empty file"
   ```

7. **Template completeness** — If assets include template files (DOCX templates, PPTX
   templates, HTML templates), check for unfilled placeholder content that suggests the
   template was never properly set up:
   - Search for common placeholder patterns: `{{placeholder}}`, `[INSERT HERE]`,
     `Lorem ipsum`, `TODO`, `FIXME`, `SAMPLE`, `REPLACE THIS`
   - For DOCX/PPTX templates, check that placeholder text fields match what the
     skill's scripts or SKILL.md expect to fill in — mismatched placeholder names
     cause silent failures where the script can't find the field to replace

### SKILL.md quality checks

8. **Frontmatter completeness** — The YAML frontmatter must have `name` and `description`.
   Flag if either is missing or empty. Without these, the skill can't be discovered or
   triggered — the name identifies it and the description is the sole mechanism Claude uses
   to decide whether to load it.

9. **Constraint consistency** — Read through all ALWAYS/NEVER/MUST rules and check for
   contradictions. Contradictory constraints force Claude into an impossible situation where
   following one rule means breaking another, leading to unpredictable behavior. Also check
   if the skill's own examples (if any) violate its own rules — this confuses Claude about
   which to follow, the rule or the example.

### Cross-reference consistency

10. **Script invocation matching** — For every place SKILL.md tells Claude to run a script,
   compare the invocation against what the script actually accepts:

   - Read the script's argument parser (argparse, sys.argv, click, etc.) or function signatures
   - Read how SKILL.md says to invoke it
   - Flag any mismatch:
     - Wrong argument names (`--input` vs `--file`)
     - Wrong argument count (too few or too many)
     - Missing required arguments
     - Flags the script doesn't recognize
     - Output path disagreements (SKILL.md says the script writes `output.png` but
       the script writes `chart.png`)

   For Python scripts with argparse, you can extract the expected args programmatically:
   ```bash
   python3 -c "
   import ast, sys
   tree = ast.parse(open('<script>').read())
   for node in ast.walk(tree):
       if isinstance(node, ast.Call) and hasattr(node.func, 'attr'):
           if node.func.attr == 'add_argument':
               args = [a.value for a in node.args if isinstance(a, ast.Constant)]
               print(f'Expected arg: {args}')
   "
   ```

11. **Inter-file references** — Check that:
   - Scripts that call other scripts use the right filenames and arguments
   - SKILL.md references to reference files use the correct filenames
   - Asset paths in scripts match actual asset filenames
   - Any file path in any file points to something that exists

### Multi-skill dependency checking

Some skills depend on other skills as part of their workflow — for example, a reporting
skill might generate a chart using the chart skill, then embed it in a document using the
docx skill. If those dependencies aren't available in the user's environment, the skill
will fail partway through with no clear explanation.

12. **Detect skill references** — Scan SKILL.md, reference files, and scripts for
    references to other skills. Common patterns to look for:

    **Explicit skill paths:**
    - `/mnt/skills/public/<skill-name>/SKILL.md`
    - `/mnt/skills/user/<skill-name>/SKILL.md`
    - `.claude/skills/<skill-name>/`
    - Any path containing `/skills/` followed by a directory and `SKILL.md`

    **Instruction-based references:**
    - "use the [name] skill" / "trigger the [name] skill"
    - "read the [name] skill's SKILL.md"
    - "follow the instructions in the [name] skill"
    - "hand off to the [name] skill"

    **Implicit dependencies:**
    - "generate a .docx file" in a skill that doesn't have its own docx logic —
      this likely depends on the docx skill being available
    - "create a presentation" without bundled pptx scripts — likely needs the
      pptx skill
    - References to skill-creator for eval running or benchmarking

    Collect every detected dependency with its source (which file and line mentioned it).

13. **Verify dependency availability** — For each detected skill dependency:

    **If an explicit path is given:**
    Check whether the referenced path exists. If it's a standard public skill path
    (like `/mnt/skills/public/docx/`), it's likely available in most environments but
    worth noting. If it's a user or private skill path, it may not be available on
    other users' systems.

    **If referenced by name only:**
    Search common skill locations (see "Finding the skill" section) for a skill with
    a matching name. Report whether it was found, and where.

    **For each dependency, report:**
    - Dependency name and where it was referenced from
    - Whether it was found and its location
    - Whether the dependency is a standard Anthropic skill (likely available everywhere)
      or a custom/user skill (may not be portable)

    **Severity:**
    - **Warning** if a dependency wasn't found — the skill may work in the author's
      environment but fail for other users
    - **Info** if a dependency was found — note it for awareness, especially if it's
      a non-standard skill
    - **Warning** if the skill references a user/private skill path — this makes the
      skill non-portable. Suggest the author either bundle the dependency or document
      it as a prerequisite

14. **Check dependency compatibility** — When a dependency is found, do a quick
    compatibility check:

    - Does the dependency skill's declared inputs match what this skill would pass to it?
      For example, if this skill says "pass the CSV to the chart skill" but the chart
      skill expects JSON, that's a mismatch.
    - Does the dependency skill's declared outputs match what this skill expects to receive?
      For example, if this skill says "take the chart image and embed it" but the chart
      skill outputs SVG (not PNG), that could be a problem.

    This is best-effort — if the dependency's I/O isn't clearly declared, note that
    compatibility couldn't be verified rather than guessing.

    **Severity:**
    - **Warning** for detected I/O mismatches between skills
    - **Info** when compatibility can't be verified due to unclear declarations

### Security review

15. **Script security scan** — Read every script and flag:

    **Critical severity:**
    - Shell injection: `os.system(f"...")`, `subprocess.run(f"...", shell=True)` with
      unsanitized input, backtick execution
    - Arbitrary code execution: `eval()`, `exec()`, `compile()` with dynamic input
    - Credential exposure: hardcoded API keys, tokens, passwords, or secrets
    - Path traversal: file operations using unsanitized user input that could escape
      the working directory (e.g., `open(user_input)` without validation)

    **Warning severity:**
    - Writing to sensitive paths: `/etc/`, `/usr/`, `~/.ssh/`, `~/.config/`, system dirs
    - Downloading from arbitrary URLs at runtime without validation
    - Disabling SSL verification (`verify=False`)
    - Reading environment variables that might contain secrets
    - Broad file glob patterns that could match unintended files

    **Info severity:**
    - `subprocess` usage that appears properly sanitized (note it, but don't alarm)
    - Network requests to hardcoded, known-safe URLs
    - File operations within expected directories

16. **SKILL.md instruction security** — Flag instructions that tell Claude to:
    - Run arbitrary commands provided by the user without sanitization
    - Disable safety checks or ignore warnings
    - Access files outside the skill's directory or standard working paths
    - Send data to external services without making the user aware
    - Grant overly broad filesystem access

    These are riskier than script vulnerabilities because they affect Claude's behavior
    directly — a compromised instruction set can turn Claude into an unwitting attack vector.

### Best practices review

17. **Run the full best practices audit** — Read `references/best-practices.md` and evaluate
    the skill against all 22 checks. This covers:

    - **Spec Compliance** (BP-1 through BP-3): name format, description length, portability fields
    - **Structure & Organization** (BP-4 through BP-8): directory layout, SKILL.md length,
      progressive disclosure, reference file quality, domain variant organization
    - **Description Quality** (BP-9 through BP-11): completeness, assertiveness, trigger
      info placement
    - **Writing Quality** (BP-12 through BP-18): imperative form, explaining the why,
      instruction clarity, defaults over menus, generality, examples, gotchas
    - **Efficiency** (BP-19 through BP-20): context window bloat, script bundling opportunities
    - **Completeness** (BP-21 through BP-22): error handling guidance, eval set presence

    Best practices findings are reported in their own section, separate from the main pass/fail
    results. They use advisory/warning severity rather than hard pass/fail, since some deviations
    are intentional.

### What to skip

- Don't execute any scripts or generate mock files
- Don't do end-to-end workflow tests
- Don't test triggering
- Don't generate mock input files
- Don't run existing evals (that's Standard)

## Expected test count

Typically 13-25 tests depending on skill complexity:
- Static integrity: 5-7
- Asset/template validation: 1 per asset file
- SKILL.md quality: 1-2
- Cross-reference consistency: 1 per script invocation
- Multi-skill dependencies: 1 per detected dependency
- Security review: 2 (scripts + instructions)
- Best practices: 22 checks (reported as a separate score)

## Report notes

For Quick Check, the report should emphasize what was NOT tested. End with:
"This was a Quick Check — structural, security, and best practices analysis only. No scripts
were executed and no I/O contracts were tested. Run Standard or Deep for functional testing."

If any security findings are Critical severity, prominently recommend resolving them before
running Standard or Deep (which would actually execute the flagged code).
