# Browser uploads

Use this procedure whenever an application requires the canonical resume or another candidate-authorized attachment.

1. Run `node scripts/job-application.mjs resume path` and use the returned absolute path. Stop if the command reports that no canonical resume is imported.
2. Read the selected browser tool's upload documentation. Prefer its privileged path-based upload capability over native UI automation.
3. When the browser exposes a file chooser, start waiting for the chooser before clicking the actual `input[type="file"]` or its associated upload control, then set the absolute path directly. For example:

   ```js
   const chooserPromise = tab.playwright.waitForEvent("filechooser", { timeoutMs: 10000 });
   await tab.playwright.locator('input[type="file"]').click();
   const chooser = await chooserPromise;
   await chooser.setFiles([resumePath]);
   ```

4. Use an equivalent documented primitive such as `setInputFiles` when that is what the selected browser provides. Do not assign `input.value`, synthesize a `DataTransfer`, inject file bytes through page JavaScript, or inspect browser session storage.
5. Use a native file picker only as a fallback after the privileged upload path is unavailable or fails and the browser-specific troubleshooting has been exhausted. Never make Finder, Explorer, or another visible picker the default flow.
6. Wait for the ATS to finish uploading or parsing. Verify the displayed filename, attachment success state, and any fields repopulated from the resume. Restore verified fields that parsing cleared or changed before continuing.
7. Keep the local path, filename, file bytes, and resume metadata out of telemetry, application answers, logs, and third-party messages.
