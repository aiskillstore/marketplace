# Project and file structure

Inspect neighboring features, build conventions, imports, and how tests are found. Follow the existing vocabulary at a consistent layer. Place code near the entry point it belongs to. Name files for a domain behavior or role that a reader can recognize and search.

In a small project, a feature directory with its handlers, domain policy, and tests may suffice. In libraries, align directories with the public API and leave private adapters internal. In a framework with routing-by-file, keep route entry points in the framework's expected paths and move independently tested policy out only when the work benefits.

For a local invoice command, keep argument handling in the existing commands directory and reuse the shared money formatter. Extract a separate calculation module when several callers need the same discount rule or that policy needs independent tests. In a web application with multiple booking entry points, keep common booking rules under the existing booking feature and call them from its routes or jobs.

Keep dependency direction easy to follow. Prefer one route into a feature to aliases scattered across folders. Verify existing imports, public package exports, platform path handling, and test discovery when moving a file.
