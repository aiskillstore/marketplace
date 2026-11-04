# Move screens over from another signage system

`migrate` runs in the CLI on the user's machine. The other system's key stays
with you: it is read from the environment or a `--credentials FILE`, goes only to
that system, and never reaches screenRIG. Never put a key in notes, feedback,
chat replies or a command line, and never ask for one to be pasted into chat.

1. `migrate vendors VENDOR` names what the system takes, the variables its key
   goes in, and the steps that make a read-only key. Ask the person to make the
   key and save it as `NAME=VALUE` lines in a file; name it with `--credentials FILE`.
   For a system that is not listed, use `--from files` with a folder or `.zip`
   of the media and optional `playlists.csv` (playlist, file, duration, order) and
   `screens.csv` (name, group, playlist, timezone).
2. `migrate scan --from VENDOR ...` reads the account, prints a report and writes
   `scan.json` into `--dir` (default `./screenrig-migration-VENDOR`). It needs no
   sign-in and sends nothing to screenRIG. Show the person the counts, every
   `not_imported` reason and the `lossy` changes. Where `next` asks for
   originals, have them download the files into one folder and rescan with
   `--files DIR`. Add `--timezone ZONE` when screens have no time zone.
3. `migrate apply --dry-run` prints the plan from the project as it is now.
   `migrate apply` (Manage access) makes the media, playlists, one waiting
   screen per old screen and the campaigns. It is safe to rerun and never
   changes what an earlier run made: after any stop (`data.stopped.next` is the
   command), failure or `waiting` item, run the same command again. A file
   address that no longer works (`vendor_file_gone`) fails that media alone:
   run `migrate scan` again, then the same apply. Do not edit or delete the
   directory's files until the import is done.
4. Each old display waits under its old name. For each one, install the Player,
   then either read its code to `migrate pair CODE --screen ID` (the source id,
   or the exact old name), or open its link on the device (`fleet-links show ID`
   prints the URL, which is a credential: give it only to the device manager) and
   run `migrate apply` again, which finishes the screen. Past the project's 50
   links a screen has no link and pairs by code.
5. Verify each screen with `screen show` and `screen screenshot`. Set what the
   report said was missing: `screen set-timezone` where `no_timezone`,
   `screen assign` where `no_default_playlist`.
6. Tell the person to keep the old system running until every screen matches.
