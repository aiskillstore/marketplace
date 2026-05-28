# Formula Creation and Editing

## Scope of Application

- Excel only (.xlsx/.xls)
- CSV has no formula capability; must be converted to Excel first

## Configuration Points

- Specify the sheet and target range (e.g., A2:A100)
- Formulas are recommended to use relative references and support row number placeholders (e.g., `=B{row}*C{row}`)
- When writing in bulk, the maximum number of rows shall prevail

## Common Scenarios

- Total Amount: `=B{row}*C{row}`
- Status Judgment: `=IF(D{row}="", "Missing", "OK")`
- Date Difference: `=DATEDIF(A{row}, B{row}, "d")`

## Precautions

- Avoid hard-coding row numbers
- Pay attention to performance when writing formulas over a large range