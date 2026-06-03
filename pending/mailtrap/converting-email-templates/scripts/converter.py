#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mailtrap Email Template Converter

Converts email templates from other providers to Mailtrap-compatible Handlebars syntax.
Supports: SendGrid, Mailgun, Mandrill (Handlebars & merge tags), Postmark, Brevo, Amazon SES.

Usage:
    python converter.py --provider sendgrid --input template.html --output ./converted/
    python converter.py --provider brevo --input ./templates/ --output ./converted/

Exit codes:
    0 = clean conversion (no flags)
    1 = conversion completed with flags (manual review needed)
    2 = error
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Change:
    line: int
    before: str
    after: str
    rule: str


@dataclass
class Flag:
    line: int
    pattern: str
    message: str
    rule: str


@dataclass
class ConversionResult:
    original: str
    converted: str
    changes: list = field(default_factory=list)
    flags: list = field(default_factory=list)


# Flag rules that leave unsupported syntax in the converted output.
# These get commented out to prevent editor errors when pasting.
COMMENTABLE_FLAG_RULES = {
    "SG-F1", "SG-F2", "SG-F3", "SG-F4", "SG-F5", "SG-F6", "SG-F7",
    "MG-F1", "MC-F1", "BR-F2", "BR-F3",
}

# Block helpers with opening and closing tags — the entire block is commented out.
BLOCK_FLAG_RULES = {"SG-F2", "SG-F3", "SG-F4", "SG-F5", "SG-F6"}


# ---------------------------------------------------------------------------
# SendGrid
# ---------------------------------------------------------------------------

def convert_sendgrid(html: str) -> ConversionResult:
    result = ConversionResult(original=html, converted=html)
    lines = html.split("\n")

    # SG-F1 to SG-F7: Flag unsupported helpers (do this BEFORE conversions)
    flag_patterns = [
        (r"\{\{#?formatDate\s", "SG-F1",
         "MANUAL: Replace {{formatDate ...}} with a pre-formatted string variable. Format the date in your application before passing it as a template variable."),
        (r"\{\{#greaterThan\s", "SG-F2",
         "MANUAL: Move greaterThan comparison to your application. Pass a boolean template variable instead."),
        (r"\{\{#lessThan\s", "SG-F3",
         "MANUAL: Move lessThan comparison to your application. Pass a boolean template variable instead."),
        (r"\{\{#notEquals\s", "SG-F4",
         "MANUAL: Move notEquals comparison to your application. Pass a boolean template variable instead."),
        (r"\{\{#and\s", "SG-F5",
         "MANUAL: Move AND logic to your application. Pass a single boolean template variable instead."),
        (r"\{\{#or\s", "SG-F6",
         "MANUAL: Move OR logic to your application. Pass a single boolean template variable instead."),
        (r"\{\{#?length\s", "SG-F7",
         "MANUAL: Move length check to your application. Pass a boolean or count as a template variable instead."),
    ]

    for i, line in enumerate(lines, 1):
        for pattern, rule, message in flag_patterns:
            if re.search(pattern, line):
                result.flags.append(Flag(line=i, pattern=line.strip(), message=message, rule=rule))

    # Also flag closing tags for comparison helpers
    closing_flag_patterns = [
        (r"\{\{/greaterThan\}\}", "SG-F2"),
        (r"\{\{/lessThan\}\}", "SG-F3"),
        (r"\{\{/notEquals\}\}", "SG-F4"),
        (r"\{\{/and\}\}", "SG-F5"),
        (r"\{\{/or\}\}", "SG-F6"),
    ]
    for i, line in enumerate(lines, 1):
        for pattern, rule in closing_flag_patterns:
            if re.search(pattern, line):
                result.flags.append(Flag(line=i, pattern=line.strip(),
                                         message=f"Closing tag for flagged helper (see {rule}).", rule=rule))

    # SG1: {{insert VARNAME "default=FALLBACK"}}
    def sg1_replace(m):
        var = m.group(1)
        fallback = m.group(2)
        return f"{{{{#if {var}}}}}{{{{{var}}}}}{{{{else}}}}{fallback}{{{{/if}}}}"

    converted = re.sub(
        r'\{\{insert\s+(\w[\w.]*)\s+"default=([^"]+)"\}\}',
        sg1_replace,
        result.converted
    )

    # SG2: {{insert VARNAME}} (no default)
    converted = re.sub(
        r'\{\{insert\s+(\w[\w.]*)\}\}',
        r'{{\1}}',
        converted
    )

    # Track changes
    _track_line_changes(result, html, converted, "SG1/SG2")
    result.converted = converted

    return result


# ---------------------------------------------------------------------------
# Mailgun
# ---------------------------------------------------------------------------

def convert_mailgun(html: str) -> ConversionResult:
    result = ConversionResult(original=html, converted=html)
    lines = html.split("\n")

    # MG-F1: Flag %recipient.X% batch syntax
    for i, line in enumerate(lines, 1):
        for m in re.finditer(r'%recipient\.(\w+)%', line):
            result.flags.append(Flag(
                line=i, pattern=m.group(0), rule="MG-F1",
                message="MANUAL: Mailgun batch variable detected. In Mailtrap, send separate API calls per recipient with their own template_variables."
            ))

    return result


# ---------------------------------------------------------------------------
# Mandrill (Handlebars mode)
# ---------------------------------------------------------------------------

def convert_mandrill_handlebars(html: str) -> ConversionResult:
    result = ConversionResult(original=html, converted=html)
    lines = html.split("\n")

    # MD-F1: Flag mc:edit regions
    for i, line in enumerate(lines, 1):
        for m in re.finditer(r'mc:edit="([^"]+)"', line):
            result.flags.append(Flag(
                line=i, pattern=m.group(0), rule="MD-F1",
                message=f'MANUAL: mc:edit region "{m.group(1)}" detected. Mailtrap does not support editable regions. Replace with a Handlebars variable (e.g., {{{{{m.group(1)}}}}}) and pass content via template_variables.'
            ))

    return result


# ---------------------------------------------------------------------------
# Mandrill (Mailchimp merge tags)
# ---------------------------------------------------------------------------

def convert_mandrill_mergetags(html: str) -> ConversionResult:
    result = ConversionResult(original=html, converted=html)
    lines = html.split("\n")

    # MC-F1: Flag date merge tags
    for i, line in enumerate(lines, 1):
        if re.search(r'\*\|DATE:[^|]*\|\*', line):
            result.flags.append(Flag(
                line=i, pattern=line.strip(), rule="MC-F1",
                message="MANUAL: Mailchimp date merge tag detected. Format the date server-side and pass as a string variable."
            ))

    # MD-F1: Flag mc:edit regions (same as Handlebars mode)
    for i, line in enumerate(lines, 1):
        for m in re.finditer(r'mc:edit="([^"]+)"', line):
            result.flags.append(Flag(
                line=i, pattern=m.group(0), rule="MC-F2",
                message=f'MANUAL: mc:edit region "{m.group(1)}" detected. Replace with a Handlebars variable.'
            ))

    converted = result.converted

    # MC2: *|IF:VARNAME|* → {{#if varname}}
    converted = re.sub(
        r'\*\|IF:([A-Z_][A-Z0-9_]*)\|\*',
        lambda m: f'{{{{#if {m.group(1).lower()}}}}}',
        converted
    )

    # MC3: *|ELSE:|* → {{else}}
    converted = re.sub(r'\*\|ELSE:\|\*', '{{else}}', converted)

    # MC4: *|END:IF|* → {{/if}}
    converted = re.sub(r'\*\|END:IF\|\*', '{{/if}}', converted)

    # MC1: *|VARNAME|* → {{varname}} (remaining variables after IF/ELSE/END removed)
    converted = re.sub(
        r'\*\|([A-Z_][A-Z0-9_]*)\|\*',
        lambda m: f'{{{{{m.group(1).lower()}}}}}',
        converted
    )

    _track_line_changes(result, html, converted, "MC1-MC4")
    result.converted = converted

    return result


# ---------------------------------------------------------------------------
# Postmark
# ---------------------------------------------------------------------------

def convert_postmark(html: str) -> ConversionResult:
    result = ConversionResult(original=html, converted=html)

    # Handlebars built-in block names to skip
    hbs_keywords = {'if', 'unless', 'each', 'with', 'else'}

    converted = result.converted

    # PM3: {{&VARNAME}} → {{{VARNAME}}}
    converted = re.sub(
        r'\{\{&(\w[\w.]*)\}\}',
        r'{{{\1}}}',
        converted
    )

    # PM1 and PM2: stateful conversion of Postmark conditionals
    # First pass: find all opening tags and track which are Postmark-style
    postmark_blocks = []  # stack of variable names that were converted

    lines = converted.split("\n")
    new_lines = []

    for line in lines:
        new_line = line

        # PM2: {{^VARNAME}} → {{#unless VARNAME}}
        def replace_inverted(m):
            name = m.group(1)
            if name not in hbs_keywords:
                postmark_blocks.append(("unless", name))
                return f'{{{{#unless {name}}}}}'
            return m.group(0)

        new_line = re.sub(r'\{\{\^(\w[\w.]*)\}\}', replace_inverted, new_line)

        # PM1: {{#VARNAME}} → {{#if VARNAME}} (when not a Handlebars keyword)
        def replace_truthy(m):
            name = m.group(1)
            if name not in hbs_keywords:
                postmark_blocks.append(("if", name))
                return f'{{{{#if {name}}}}}'
            return m.group(0)

        new_line = re.sub(r'\{\{#(\w[\w.]*)\}\}', replace_truthy, new_line)

        # Closing tags: {{/VARNAME}} → {{/if}} or {{/unless}}
        def replace_closing(m):
            name = m.group(1)
            if name not in hbs_keywords:
                # Find the matching opening block
                for i in range(len(postmark_blocks) - 1, -1, -1):
                    if postmark_blocks[i][1] == name:
                        block_type = postmark_blocks[i][0]
                        postmark_blocks.pop(i)
                        return "{{/" + block_type + "}}"
                # No matching opening found - flag it
                result.flags.append(Flag(
                    line=0, pattern=m.group(0), rule="PM-F1",
                    message="WARNING: Closing tag {{/" + name + "}} has no matching converted opening tag. Verify manually."
                ))
                return m.group(0)
            return m.group(0)

        new_line = re.sub(r'\{\{/(\w[\w.]*)\}\}', replace_closing, new_line)

        new_lines.append(new_line)

    converted = "\n".join(new_lines)

    _track_line_changes(result, html, converted, "PM1-PM3")
    result.converted = converted

    return result


# ---------------------------------------------------------------------------
# Brevo
# ---------------------------------------------------------------------------

def convert_brevo(html: str) -> ConversionResult:
    result = ConversionResult(original=html, converted=html)
    lines = html.split("\n")

    # Flag-only patterns first
    # BR-F2: Date filters
    for i, line in enumerate(lines, 1):
        if re.search(r'\{\{\s*params\.\w[\w.]*\s*\|\s*date:"[^"]*"\s*\}\}', line):
            result.flags.append(Flag(
                line=i, pattern=line.strip(), rule="BR-F2",
                message="MANUAL: Brevo date filter detected. Format the date server-side and pass as a string variable."
            ))

    # BR-F3: Unknown filters (not default, not date)
    for i, line in enumerate(lines, 1):
        for m in re.finditer(r'\{\{\s*params\.\w[\w.]*\s*\|\s*(?!default:|date:)(\w+)', line):
            result.flags.append(Flag(
                line=i, pattern=line.strip(), rule="BR-F3",
                message=f'MANUAL: Brevo filter "{m.group(1)}" detected. Mailtrap Handlebars does not support filters. Move this logic to your application.'
            ))

    # BR-F4: Detect nested for loops
    loop_depth = 0
    for i, line in enumerate(lines, 1):
        if re.search(r'\{%\s*for\s+', line):
            loop_depth += 1
            if loop_depth > 1:
                result.flags.append(Flag(
                    line=i, pattern=line.strip(), rule="BR-F4",
                    message="WARNING: Nested loop detected. Verify that {{this}} references resolve correctly in Handlebars context."
                ))
        if re.search(r'\{%\s*endfor\s*%\}', line):
            loop_depth = max(0, loop_depth - 1)

    converted = result.converted

    # BR-F1: Auto-convert default filters
    # {{ params.VAR | default:"VALUE" }} → {{#if VAR}}{{VAR}}{{else}}VALUE{{/if}}
    def brevo_default_replace(m):
        var = m.group(1)
        fallback = m.group(2)
        return f"{{{{#if {var}}}}}{{{{{var}}}}}{{{{else}}}}{fallback}{{{{/if}}}}"

    converted = re.sub(
        r'\{\{\s*params\.(\w[\w.]*)\s*\|\s*default:"([^"]+)"\s*\}\}',
        brevo_default_replace,
        converted
    )

    # Collect loop variable mappings for BR7
    # {% for ITEM in params.LIST %} → track ITEM name
    loop_vars = []
    for m in re.finditer(r'\{%\s*for\s+(\w+)\s+in\s+params\.(\w[\w.]*)\s*%\}', converted):
        loop_vars.append(m.group(1))

    # BR5: {% for ITEM in params.LIST %} → {{#each LIST}}
    converted = re.sub(
        r'\{%\s*for\s+(\w+)\s+in\s+params\.(\w[\w.]*)\s*%\}',
        r'{{#each \2}}',
        converted
    )

    # BR6: {% endfor %} → {{/each}}
    converted = re.sub(r'\{%\s*endfor\s*%\}', '{{/each}}', converted)

    # BR7: Replace loop variable references with this.PROPERTY
    # {{ ITEM.PROPERTY }} → {{this.PROPERTY}}
    for var in loop_vars:
        # Handle {{ var.property }} (with spaces, Brevo style)
        converted = re.sub(
            rf'\{{\{{\s*{re.escape(var)}\.(\w[\w.]*)\s*\}}\}}',
            r'{{this.\1}}',
            converted
        )
        # Handle bare {{ var }} reference
        converted = re.sub(
            rf'\{{\{{\s*{re.escape(var)}\s*\}}\}}',
            '{{this}}',
            converted
        )

    # BR2: {% if params.CONDITION %} → {{#if CONDITION}}
    converted = re.sub(
        r'\{%\s*if\s+params\.(\w[\w.]*)\s*%\}',
        r'{{#if \1}}',
        converted
    )

    # Also handle {% if CONDITION %} without params prefix
    converted = re.sub(
        r'\{%\s*if\s+(\w[\w.]*)\s*%\}',
        r'{{#if \1}}',
        converted
    )

    # BR3: {% else %} → {{else}}
    converted = re.sub(r'\{%\s*else\s*%\}', '{{else}}', converted)

    # BR4: {% endif %} → {{/if}}
    converted = re.sub(r'\{%\s*endif\s*%\}', '{{/if}}', converted)

    # BR1: {{ params.VARNAME }} → {{VARNAME}} (remaining after filter handling)
    converted = re.sub(
        r'\{\{\s*params\.(\w[\w.]*)\s*\}\}',
        r'{{\1}}',
        converted
    )

    _track_line_changes(result, html, converted, "BR1-BR7")
    result.converted = converted

    return result


# ---------------------------------------------------------------------------
# Amazon SES
# ---------------------------------------------------------------------------

def convert_ses(html: str) -> ConversionResult:
    # No template syntax changes needed
    return ConversionResult(original=html, converted=html)


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _track_line_changes(result: ConversionResult, original: str, converted: str, rule: str):
    """Compare original and converted line by line and record changes."""
    orig_lines = original.split("\n")
    conv_lines = converted.split("\n")

    for i, (orig, conv) in enumerate(zip(orig_lines, conv_lines), 1):
        if orig != conv:
            result.changes.append(Change(line=i, before=orig.strip(), after=conv.strip(), rule=rule))


def _comment_out_flagged(converted: str, flags: list) -> str:
    """Wrap flagged unsupported patterns in HTML comments to prevent editor errors."""
    commentable = [f for f in flags if f.rule in COMMENTABLE_FLAG_RULES]
    if not commentable:
        return converted

    lines = converted.split("\n")

    # Identify block ranges (opening + closing flag pairs sharing the same rule)
    block_ranges = {}
    for flag in commentable:
        if flag.rule in BLOCK_FLAG_RULES:
            if flag.rule not in block_ranges:
                block_ranges[flag.rule] = {
                    "start": flag.line, "end": flag.line, "message": flag.message
                }
            else:
                entry = block_ranges[flag.rule]
                entry["start"] = min(entry["start"], flag.line)
                entry["end"] = max(entry["end"], flag.line)
                if "Closing tag" not in flag.message:
                    entry["message"] = flag.message

    # Map block start lines for quick lookup
    block_starts = {}
    block_member_lines = set()
    for rule, info in block_ranges.items():
        block_starts[info["start"]] = {
            "end": info["end"], "message": info["message"], "rule": rule
        }
        for l in range(info["start"], info["end"] + 1):
            block_member_lines.add(l)

    # Collect single-line flags (not part of any block)
    single_flags = {}
    for flag in commentable:
        if flag.rule not in BLOCK_FLAG_RULES and flag.line not in single_flags:
            single_flags[flag.line] = (flag.message, flag.rule)

    # Rebuild the output with comments
    new_lines = []
    i = 0
    while i < len(lines):
        line_num = i + 1

        if line_num in block_starts:
            info = block_starts[line_num]
            new_lines.append(
                f"<!-- FLAGGED [{info['rule']}]: {info['message']}"
            )
            for j in range(line_num, info["end"] + 1):
                new_lines.append(lines[j - 1])
            new_lines.append("-->")
            i = info["end"] - 1  # end is 1-indexed; after i += 1 we resume correctly
        elif line_num in block_member_lines:
            new_lines.append(lines[i])
        elif line_num in single_flags:
            message, rule = single_flags[line_num]
            safe_line = lines[i].replace("--", "- -")
            new_lines.append(f"<!-- FLAGGED [{rule}]: {message} -->")
            new_lines.append(f"<!-- {safe_line} -->")
        else:
            new_lines.append(lines[i])

        i += 1

    return "\n".join(new_lines)


def _add_flag_warning(converted: str, flags: list) -> str:
    """Prepend a warning comment when the converted template has flags."""
    flag_count = sum(1 for f in flags if "Closing tag" not in f.message)
    warning = (
        f"<!-- WARNING: This converted template contains {flag_count} flagged "
        f"pattern(s) that must be resolved before use.\n"
        f"     Unsupported syntax has been commented out to prevent editor "
        f"errors (search for \"FLAGGED\").\n"
        f"     See the .report.txt file for full details and guidance. -->"
    )
    return warning + "\n" + converted


def generate_report(filepath: str, result: ConversionResult) -> str:
    """Generate a human-readable report for a single file conversion."""
    lines = []
    lines.append(f"Conversion Report: {filepath}")
    lines.append("=" * 60)
    lines.append("")

    if not result.changes and not result.flags:
        lines.append("No changes needed. Template is already Mailtrap-compatible.")
        return "\n".join(lines)

    if result.changes:
        lines.append(f"CHANGES ({len(result.changes)}):")
        lines.append("-" * 40)
        for c in result.changes:
            lines.append(f"  Line {c.line} [{c.rule}]:")
            lines.append(f"    - {c.before}")
            lines.append(f"    + {c.after}")
            lines.append("")

    if result.flags:
        lines.append(f"FLAGS ({len(result.flags)}) - Manual review needed:")
        lines.append("-" * 40)
        for f in result.flags:
            lines.append(f"  Line {f.line} [{f.rule}]:")
            lines.append(f"    Pattern: {f.pattern}")
            lines.append(f"    {f.message}")
            lines.append("")

    lines.append(f"Summary: {len(result.changes)} changes, {len(result.flags)} flags")

    return "\n".join(lines)


def generate_summary(file_results: dict) -> str:
    """Generate a bulk conversion summary."""
    lines = []
    lines.append("Bulk Conversion Summary")
    lines.append("=" * 60)
    lines.append("")

    total_files = len(file_results)
    total_changes = sum(len(r.changes) for r in file_results.values())
    total_flags = sum(len(r.flags) for r in file_results.values())
    files_with_flags = [f for f, r in file_results.items() if r.flags]
    clean_files = [f for f, r in file_results.items() if not r.flags]

    lines.append(f"Total files processed: {total_files}")
    lines.append(f"Total changes made:    {total_changes}")
    lines.append(f"Total flags raised:    {total_flags}")
    lines.append(f"Clean conversions:     {len(clean_files)}")
    lines.append(f"Files needing review:  {len(files_with_flags)}")
    lines.append("")

    if files_with_flags:
        lines.append("Files needing manual review:")
        for f in files_with_flags:
            flag_count = len(file_results[f].flags)
            lines.append(f"  - {f} ({flag_count} flag{'s' if flag_count != 1 else ''})")
        lines.append("")

    if clean_files:
        lines.append("Clean conversions (no flags):")
        for f in clean_files:
            change_count = len(file_results[f].changes)
            lines.append(f"  - {f} ({change_count} change{'s' if change_count != 1 else ''})")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Provider dispatch
# ---------------------------------------------------------------------------

PROVIDERS = {
    "sendgrid": convert_sendgrid,
    "mailgun": convert_mailgun,
    "mandrill-handlebars": convert_mandrill_handlebars,
    "mandrill-mergetags": convert_mandrill_mergetags,
    "postmark": convert_postmark,
    "brevo": convert_brevo,
    "ses": convert_ses,
}


def convert_file(provider: str, input_path: Path, output_dir: Path) -> ConversionResult:
    """Convert a single template file."""
    html = input_path.read_text(encoding="utf-8")

    converter = PROVIDERS[provider]
    result = converter(html)

    # Post-process: comment out flagged patterns and add warning header
    output_html = result.converted
    if result.flags:
        output_html = _comment_out_flagged(output_html, result.flags)
        output_html = _add_flag_warning(output_html, result.flags)

    # Write converted file
    output_path = output_dir / input_path.name
    output_path.write_text(output_html, encoding="utf-8")

    # Write report
    report_path = output_dir / f"{input_path.stem}.report.txt"
    report = generate_report(input_path.name, result)
    report_path.write_text(report, encoding="utf-8")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Convert email templates to Mailtrap Handlebars format."
    )
    parser.add_argument(
        "--provider",
        required=True,
        choices=list(PROVIDERS.keys()),
        help="Source email provider."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input file or directory path."
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output directory path."
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        print(f"Error: Input path does not exist: {input_path}", file=sys.stderr)
        sys.exit(2)

    # Determine files to process
    if input_path.is_file():
        files = [input_path]
    elif input_path.is_dir():
        files = sorted(input_path.glob("*.html"))
        if not files:
            print(f"Error: No .html files found in {input_path}", file=sys.stderr)
            sys.exit(2)
    else:
        print(f"Error: Input is neither a file nor directory: {input_path}", file=sys.stderr)
        sys.exit(2)

    # Convert
    file_results = {}
    has_flags = False

    for f in files:
        print(f"Converting: {f.name}")
        result = convert_file(args.provider, f, output_dir)
        file_results[f.name] = result
        if result.flags:
            has_flags = True

    # Bulk summary
    if len(files) > 1:
        summary = generate_summary(file_results)
        summary_path = output_dir / "_summary.txt"
        summary_path.write_text(summary, encoding="utf-8")
        print(f"\nSummary written to: {summary_path}")

    # Print summary to stdout
    total_changes = sum(len(r.changes) for r in file_results.values())
    total_flags = sum(len(r.flags) for r in file_results.values())
    print(f"\nDone. {len(files)} file(s) processed. {total_changes} changes, {total_flags} flags.")

    if has_flags:
        print("Some files need manual review. Check .report.txt files for details.")
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
