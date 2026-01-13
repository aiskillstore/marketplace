# Quick Start: Publishing to GitHub (5 Minutes)

This is the fast-track guide to get your skill on GitHub and generate a download link.

## Prerequisites

- GitHub account (free): [Sign up here](https://github.com/signup)
- Git installed on your computer: [Download here](https://git-scm.com/downloads)

---

## Step 1: Create Repository (2 minutes)

1. Go to [github.com/new](https://github.com/new)
2. Fill in:
   - **Repository name**: `skool-money-model-strategist`
   - **Description**: "Claude Code skill for Skool money models using Alex Hormozi frameworks"
   - **Public** (so people can download)
   - ✅ Add a README file
   - ✅ Add .gitignore: Python
   - ✅ Choose a license: MIT License
3. Click **Create repository**

---

## Step 2: Upload Your Files (2 minutes)

### Option A: Via Web Interface (Easiest - No Git Knowledge Required)

1. On your new repository page, click **"uploading an existing file"** (in the setup instructions)
2. Drag and drop these folders/files from `C:\Users\Raphael\.claude\skills\skool-money-model-strategist\`:
   - `SKILL.md`
   - `README.md` (replace the auto-generated one)
   - `CHANGELOG.md`
   - `LICENSE` (replace if needed)
   - `.gitignore` (replace if needed)
   - `references/` folder (all 8 files inside)
   - `scripts/` folder (math_helpers.py)
3. Scroll down, add commit message: "Initial release: v1.0.0"
4. Click **Commit changes**

### Option B: Via Command Line (If You Know Git)

```bash
# Clone your repository
git clone https://github.com/DaronVee/skool-money-model-strategist.git
cd skool-money-model-strategist

# Copy skill files
cp -r "C:/Users/Raphael/.claude/skills/skool-money-model-strategist/"* .

# Commit and push
git add .
git commit -m "Initial release: v1.0.0"
git push origin main
```

---

## Step 3: Create Release (1 minute)

1. On your repository page, click **"Releases"** (right sidebar)
2. Click **"Create a new release"**
3. Fill in:
   - **Choose a tag**: Type `v1.0.0` and click "Create new tag: v1.0.0 on publish"
   - **Release title**: `v1.0.0 - Initial Release`
   - **Description**:
     ```
     Complete Skool Money Model Strategist skill implementing Alex Hormozi's frameworks.

     Download the ZIP below and extract to ~/.claude/skills/skool-money-model-strategist/

     See README.md for full installation instructions.
     ```
4. Click **"Publish release"**

Done! GitHub automatically creates a ZIP file.

---

## Step 4: Get Your Download Link

Your download link will be:

```
https://github.com/DaronVee/skool-money-model-strategist/archive/refs/tags/v1.0.0.zip
```

**Or use the "latest release" link** (always points to newest version):

```
https://github.com/DaronVee/skool-money-model-strategist/releases/latest
```

---

## Share This Message Template

Copy-paste this into Skool posts or DMs:

```
Hey! Here's the Skool Money Model Strategist skill for Claude Code 👇

📦 Download: https://github.com/DaronVee/skool-money-model-strategist/releases/latest

This skill helps you design your Skool money model using Alex Hormozi's 15 mechanisms.

Installation:
1. Download the ZIP
2. Extract to ~/.claude/skills/skool-money-model-strategist/
3. Restart Claude Code

Full docs: https://github.com/DaronVee/skool-money-model-strategist

Let me know if you have questions!

Created by Daron Vener | CCGG AI Leaders: https://www.skool.com/ccgg-ai-leaders
```

---

## Why This Approach Works

✅ **Trustworthy**: GitHub is a recognized platform, no virus concerns
✅ **Easy**: One-click ZIP download, no tech skills needed
✅ **Professional**: Shows commit history, documentation, your authorship
✅ **Free**: No hosting costs, unlimited downloads
✅ **Version Control**: Update to v1.1.0 later with new releases
✅ **Attribution**: Your name as author, link to your community

---

## Need Help?

- **Can't upload files?** Try Option A (web interface) - no Git needed
- **Forgot to add something?** Just upload more files using "Add file" button
- **Want to update later?** Create a new release with v1.1.0

---

**That's it! Your skill is now publicly available with a professional download link.**
