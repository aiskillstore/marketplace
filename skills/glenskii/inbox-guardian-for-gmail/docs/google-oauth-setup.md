# Google OAuth Setup

Inbox Guardian for Gmail uses an OAuth Desktop app client that you create in your own Google Cloud project. Your client file and token remain on your computer and are ignored by Git.

## Before You Start

- Sign in to the Google account that owns the Gmail mailbox.
- Open the [Google Cloud Console](https://console.cloud.google.com/).
- Do not send `credentials.json` or `token.json` to anyone.

## Create the Client

1. Create a Google Cloud project, or choose one you already own.
2. Open **APIs & Services**, then **Library**. Search for **Gmail API** and enable it.
3. Open **OAuth consent screen**. Choose **External** for a personal account, or **Internal** only when your Workspace administrator permits it. Enter the required app and support details.
4. If Google shows a test-user section, add the mailbox owner before continuing.
5. Open **Credentials**, choose **Create Credentials**, then **OAuth client ID**.
6. Choose **Desktop app**. Download the generated JSON file.
7. Rename the downloaded file to `credentials.json` and place it in the same folder as `guardian.py`.

## Connect the Mailbox

Run:

```bash
python guardian.py --setup
```

The command creates `config.json` from the example when needed. It opens a browser window for owner approval, writes `token.json` locally after approval, and prints the connected Gmail address. It does not inspect or change any mail.

## If Setup Fails

- Confirm that the file is named `credentials.json`, not `credentials (1).json`.
- Confirm that the client type is **Desktop app**.
- Confirm that the Gmail API is enabled in the same Google Cloud project.
- Delete only the local `token.json` file if you need to choose a different account, then rerun `python guardian.py --setup`.
