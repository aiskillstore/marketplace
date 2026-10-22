#!/usr/bin/env python3
"""Build a simple local budget workbook using only Python's standard library."""
import argparse
from datetime import date
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from xml.sax.saxutils import escape


def col(n):
    out = ""
    while n:
        n, rem = divmod(n - 1, 26)
        out = chr(65 + rem) + out
    return out


def cell(ref, value, style=0, formula=False):
    if formula:
        return f'<c r="{ref}" s="{style}"><f>{escape(value)}</f><v>0</v></c>'
    if isinstance(value, (int, float)):
        return f'<c r="{ref}" s="{style}"><v>{value}</v></c>'
    return f'<c r="{ref}" t="inlineStr" s="{style}"><is><t>{escape(str(value))}</t></is></c>'


def sheet(rows):
    xml_rows = []
    for i, row in enumerate(rows, 1):
        cells = "".join(cell(f"{col(j)}{i}", value, style, formula)
                         for j, (value, style, formula) in enumerate(row, 1))
        xml_rows.append(f'<row r="{i}">{cells}</row>')
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>'
            '<sheetFormatPr defaultRowHeight="18"/><sheetData>' + "".join(xml_rows) + '</sheetData></worksheet>')


def build(path, month, kind):
    rows = [[("Monthly Budget", 1, False)], [("Month", 2, False), (month, 3, False)],
            [("Category", 1, False), ("Planned", 1, False), ("Actual", 1, False), ("Remaining", 1, False)]]
    categories = ["Income", "Housing", "Utilities", "Food", "Transport", "Health", "Debt", "Savings", "Personal", "Other"]
    if kind in ("sinking", "combined"):
        categories += ["Sinking fund: annual bills", "Sinking fund: repairs"]
    if kind in ("side-hustle", "combined"):
        categories += ["Side hustle income", "Side hustle expenses"]
    for name in categories:
        rownum = len(rows) + 1
        rows.append([(name, 0, False), (0, 3, False), (0, 3, False), (f"B{rownum}-C{rownum}", 4, True)])
    total = len(rows) + 1
    rows.append([("TOTAL", 1, False), (f"SUM(B4:B{total-1})", 4, True),
                 (f"SUM(C4:C{total-1})", 4, True), (f"SUM(D4:D{total-1})", 4, True)])
    readme = [[("READ ME", 1, False)], [("Workbook created locally; your figures stay on this device.", 0, False)],
              [("Blue cells are inputs. Enter planned and actual amounts in the budget tab.", 0, False)],
              [("Remaining equals planned minus actual. Totals use spreadsheet formulas.", 0, False)],
              [("For sinking funds, estimate an annual target and divide by 12 for the monthly plan.", 0, False)],
              [("This workbook organizes information and is not financial advice.", 0, False)]]
    types = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
      '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
      '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
      '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
      '<Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
      '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>')
    with ZipFile(path, "w", ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", types)
        z.writestr("_rels/.rels", '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        z.writestr("xl/workbook.xml", '<?xml version="1.0"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Budget" sheetId="1" r:id="rId1"/><sheet name="READ ME" sheetId="2" r:id="rId2"/></sheets></workbook>')
        z.writestr("xl/_rels/workbook.xml.rels", '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
        z.writestr("xl/styles.xml", '<?xml version="1.0"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts><fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FFDDEEFF"/></patternFill></fill></fills><borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="5"><xf xfId="0"/><xf xfId="0" applyFont="1"/><xf xfId="0"/><xf xfId="0" fillId="2" applyFill="1"/><xf xfId="0" applyNumberFormat="1" numFmtId="4"/></cellXfs></styleSheet>')
        z.writestr("xl/worksheets/sheet1.xml", sheet(rows))
        z.writestr("xl/worksheets/sheet2.xml", sheet(readme))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--month", default=date.today().strftime("%B %Y"))
    parser.add_argument("--type", choices=("monthly", "sinking", "side-hustle", "combined"), default="monthly")
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    build(args.output, args.month, args.type)
    print(f"Created {args.output}")
