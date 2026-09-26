# App Methods

App methods are supplied by the host app, so availability varies by platform,
app, build type, and version. This index lists the App request methods
documented for public Lynx DevTool workflows. A host that does not register a
handler for a method returns a failure response for it.

Callback events are documented with the request method that initiates them.

## Navigation

- [App.openPage](App.openPage.md) - Open a page in the host app.
- [App.closePage](App.closePage.md) - Close the current page.

## Host Reflection

- [App.CallStaticVoidMethod](App.CallStaticVoidMethod.md) - Call a static void method via reflection.

## Notes

- App commands are client-scoped and do not take a `sessionId`.
- Read this page before sending an App command so the selected method matches
  what the target host actually registers.
- When a method is missing on the target host, prefer an equivalent CDP method
  from [Supported CDP Methods](../cdp/index.md).
