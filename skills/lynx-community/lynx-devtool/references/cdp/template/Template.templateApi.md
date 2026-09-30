# Template.templateApi

- `Template.templateApi` - Reports template data-processor API information for the current template.
- Input: None.
- Output:
  - `useDefault` (boolean): Whether the current template has a default data-processor closure.
  - `processMapKeys` (string array, optional): Names of registered data-processor entries. Omitted when the processor map is empty.

## Notes

- The request is dispatched to the TASM thread.
- If TASM is unavailable, Lynx returns `{useDefault: false}`.
