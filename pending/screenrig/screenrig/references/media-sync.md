# Keep a cloud folder in step with the library

Use it when a person's images, videos or audio live in a SharePoint or OneDrive
for work folder, a Dropbox folder or a Google Drive folder, and screens must
follow it without uploading again. A sync imports the files into a media folder,
replaces the bytes of a changed file under the same media ID (every playlist
that plays it updates, with no republish) and takes a file removed at the source
out of play. Office files, PDFs and Google Docs, Sheets and Slides files are not
media: show those with a document link in a playlist.

## Dropbox

```sh
screenrig media sync account add dropbox --name "Marketing Dropbox"
screenrig media sync account show msa_ID          # state ready once the person allowed access
screenrig media sync create dropbox --account-id msa_ID \
  --url "https://www.dropbox.com/home/Signage/Lobby" [--every 15m]
```

- `account add dropbox` prints `authorize_url`, a one-time link with an expiry.
  Send it to the person who owns the Dropbox account; they open it signed in to
  Dropbox and allow read-only access. `media sync account connect msa_ID` makes a
  new link, also when Dropbox stops honoring the connection (`state:
  reconnect_required`, problem `dropbox_reconnect_required`).
- `--url` is the folder's address from dropbox.com (under `/home`), its path
  (`/Signage/Lobby`), or a shared folder link that the account has added to its
  Dropbox. Folders in a team space work. Each run reads only what changed.
- `--app-key KEY` connects through the customer's own Dropbox app instead: it
  needs the scoped permissions files.metadata.read, files.content.read,
  account_info.read and sharing.read, and the redirect URI the command prints.
  `dropbox_not_configured` means this server has no screenRIG Dropbox app: use
  the customer's own app key.

## Google Drive

```sh
screenrig media sync account add google-drive --name "Lobby Drive"
screenrig media sync create google-drive --account-id msa_ID \
  --url "https://drive.google.com/drive/folders/FOLDER-ID" [--every 15m]
```

- `account add google-drive` prints `service_account_email`. The person shares
  the folder with that address as Viewer, from their Google account.
- Through screenRIG's address, the folder syncs only while a member of this
  project with a verified email shared it or owns it, under the same Google
  address. Every run checks again; `sharer_not_member` stops the sync in `state:
  error` until it is shared again, and keeps its media.
- `--key-file key.json` (or `-` for stdin) uses the customer's own Google Cloud
  service account instead: its `client_email` is the address to share with, and
  no member check applies. A folder in a shared drive needs this route.
  `google_drive_not_configured` means this server has no screenRIG service
  account: use the customer's own key. `media sync account update msa_ID
  --key-file new.json` rotates it (same `client_email`).
- Each run lists the folder and compares each file's checksum.

## SharePoint or OneDrive for work

SharePoint reads through the customer's own Microsoft Entra app. Ask a Microsoft
365 administrator to do this once and give you three values, never the secret
in chat if a file will do:

1. Microsoft Entra admin center, App registrations, New registration: one
   tenant only, no redirect URI. Note the **Directory (tenant) ID** and the
   **Application (client) ID**.
2. Certificates & secrets, New client secret. Copy its **Value** (not the
   Secret ID) into a file such as `secret.txt`. A secret expires, so note when.
3. API permissions, Add, Microsoft Graph, **Application permissions**, then
   one of:
   - **Sites.Selected** (the narrow choice). Then grant the app each site with
     `POST https://graph.microsoft.com/v1.0/sites/SITE-ID/permissions` and body
     `{"roles": ["read"], "grantedToIdentities": [{"application": {"id":
     "CLIENT-ID", "displayName": "screenRIG sync"}}]}`, sent by an
     administrator (Graph Explorer or a script).
   - **Files.Read.All**: every site and drive, and the only grant a sharing
     link needs.
4. Grant admin consent for the tenant.

```sh
screenrig media sync account add microsoft365 --name Contoso \
  --tenant-id contoso.onmicrosoft.com --client-id CLIENT-ID --secret-file secret.txt
screenrig media sync account test msa_ID          # credentials and the roles the token carries
screenrig media sync create sharepoint --account-id msa_ID \
  --url "https://TENANT.sharepoint.com/sites/SITE/LIBRARY/FOLDER" [--every 15m]
```

- Paste the folder's address from the browser, or its sharing link (Share, Copy
  link). A site address works with Sites.Selected once the site is granted; a
  sharing link or an OneDrive for work address needs Files.Read.All. Personal
  OneDrive (onedrive.live.com, 1drv.ms) cannot be read.
- Replace an expiring secret with `media sync account update msa_ID
  --secret-file new.txt`.
- A Microsoft connection can stand in for the three values: `media sync account
  add microsoft365 --connection-id pcn_ID` reads through a connection
  (`connection create microsoft`, either mode) that the project's room calendars
  can share too ([connections](sources.md#meeting-rooms-microsoft365-google_calendar)).
  With screenrig_app the customer's administrator approves screenRIG's own
  application once, so you never handle a secret. For files it holds
  `Sites.Selected` only: grant each site to the enterprise application the
  consent adds to the tenant, as above (`connection test` warns when that is all
  the token carries). A sharing link or an OneDrive for work address needs an
  own_app connection whose app holds Files.Read.All.

## Every provider

```sh
screenrig media sync show msy_ID                  # what the last run did
screenrig media sync run msy_ID                   # run one now
```

- Create reads the folder first. `media_sync_source_refused` names what to fix;
  nothing is stored until it works. The first run starts within about 30
  seconds.
- Only files directly in the folder sync; subfolders are skipped. png, jpeg,
  webp, gif, mp4, webm and mp3 import; others appear in `data.last_run.skipped`
  with the reason (`unsupported_type`, `too_large`, `unreadable`, `storage`,
  `download_failed`, `subfolder`, `in_use`). A run is `partial` while a file
  that should sync did not; the next run tries again.
- The sync fills a media folder (`--folder-id mfd_ID`, or a new one named after
  the source). Play it with a `folder` selector in an `image` or `video`
  primitive, once; it then follows the source, and a page of several files needs
  `one_at_a_time: true` unless it is a `media_end` page:
  `"selector": {"by": "folder", "folder_id": "mfd_ID", "one_at_a_time": true}`.
- A file removed at the source is deleted. While a screen still shows it, it
  waits in a `Removed` subfolder (selectors stop playing it) and a later run
  deletes it (`pending_delete` counts these).
- `state: error` needs a repair: the media folder was deleted (`media sync
  update ID --folder-id mfd_ID`), the source folder was deleted or moved (delete
  the sync and create one for its new address), or a Google Drive folder lost
  its sharer (share it again).
- `media sync delete ID` stops the sync and keeps the media; `media sync account
  delete ID` is refused while a sync uses it.
- The dashboard's Media, Sync tab shows the same syncs and accounts, and a person
  can set them up there.

Creating accounts and syncs needs Manage access. Accounts and syncs belong to
one project. Secrets and keys are sealed on the server and shown only as their
last four characters; give them only through `--secret-file` or `--key-file`.
