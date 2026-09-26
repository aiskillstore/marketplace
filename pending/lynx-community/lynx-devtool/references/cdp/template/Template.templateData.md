# Template.templateData

- `Template.templateData` - Returns the current initial template data exposed by the platform facade.
- Input: None.
- Output: `{content?: string}`. When present, `content` is serialized template data from the platform Lepus value.

## Notes

- The request is dispatched to the UI thread.
- Android reads the saved initial `TemplateData` pointer through the platform reload helper; Darwin delegates to its platform implementation.
- If no template data is available, Lynx returns an empty result object without `content`.
