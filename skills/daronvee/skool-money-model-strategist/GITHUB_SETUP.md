# GitHub Repository Setup Guide

This guide walks you through creating the GitHub repository and publishing your first release.

## Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com)
2. Click "New repository" (green button, top right)
3. Fill in details:
   - **Repository name**: `skool-money-model-strategist`
   - **Description**: "Claude Code skill for designing Skool community money models using Alex Hormozi's frameworks"
   - **Visibility**: **Public** (so people can download freely)
   - **Initialize**:
     - ✅ Add a README file (we'll replace it)
     - ✅ Add .gitignore (choose "Python" template)
     - ✅ Choose a license (MIT License recommended for skills)
4. Click "Create repository"

## Step 2: Clone Repository Locally

```bash
# Navigate to a working directory (NOT your .claude/skills folder)
cd ~/Documents  # or wherever you want to work

# Clone your new repository
git clone https://github.com/[YourUsername]/skool-money-model-strategist.git

# Enter the directory
cd skool-money-model-strategist
```

## Step 3: Copy Skill Files to Repository

```bash
# Copy all files from your .claude/skills directory to the repository
# Windows (PowerShell)
Copy-Item -Path "C:\Users\[YourName]\.claude\skills\skool-money-model-strategist\*" -Destination "." -Recurse -Force

# macOS/Linux
cp -r ~/.claude/skills/skool-money-model-strategist/* .
```

After copying, your repository should have:
```
skool-money-model-strategist/
├── README.md
├── SKILL.md
├── references/
│   └── (all 8 reference files)
└── scripts/
    └── math_helpers.py
```

## Step 4: Create .gitignore (if not already created)

Add this content to `.gitignore`:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Temp
*.tmp
*.bak
```

## Step 5: Commit and Push Files

```bash
# Stage all files
git add .

# Commit with message
git commit -m "Initial release: Skool Money Model Strategist v1.0.0

- Complete Hormozi 15 mechanisms implementation
- 8 reference documents with frameworks
- Math validation helpers
- Progressive disclosure workflow
- Source citation requirements"

# Push to GitHub
git push origin main
```

## Step 6: Create Your First Release

### Option A: Via GitHub Web Interface (Easiest)

1. Go to your repository on GitHub: `https://github.com/[YourUsername]/skool-money-model-strategist`
2. Click "Releases" (right sidebar)
3. Click "Create a new release"
4. Fill in:
   - **Tag version**: `v1.0.0` (click "Create new tag on publish")
   - **Release title**: `v1.0.0 - Initial Release`
   - **Description**:
     ```markdown
     ## First Public Release

     Complete Skool Money Model Strategist skill implementing Alex Hormozi's $100M Money Models frameworks.

     ### Features
     - 15 Hormozi mechanisms with Skool implementation guides
     - 5-stage business evolution framework
     - CAC-based diagnostics and 30-day cash gap analysis
     - Math validation helpers (Python)
     - Progressive disclosure workflow
     - 8 comprehensive reference documents

     ### Installation
     1. Download `skool-money-model-strategist-v1.0.0.zip` below
     2. Extract to `~/.claude/skills/skool-money-model-strategist/`
     3. Restart Claude Code

     ### Requirements
     - Claude Code installed
     - Python 3.x (optional, for math validation)

     ### Documentation
     See [README.md](README.md) for complete installation and usage guide.
     ```
5. Click "Publish release"

GitHub will automatically create a ZIP file of your repository at this tag!

### Option B: Via Command Line

```bash
# Create and push tag
git tag -a v1.0.0 -m "Initial release: Skool Money Model Strategist v1.0.0"
git push origin v1.0.0

# Then complete the release on GitHub web interface (steps above)
```

## Step 7: Get Your Download Link

After creating the release:

1. Go to your repository's Releases page
2. Your release will show a "Source code (zip)" download link
3. Right-click and copy link address
4. The URL format will be:
   ```
   https://github.com/[YourUsername]/skool-money-model-strategist/archive/refs/tags/v1.0.0.zip
   ```

**Share this link** with people who asked for the skill!

## Sharing the Skill

### Professional Message Template

For Skool posts or DMs:

```
Hey! Here's the Skool Money Model Strategist skill 👇

📦 Download: https://github.com/[YourUsername]/skool-money-model-strategist/releases/latest

This Claude Code skill helps you design your Skool money model using Alex Hormozi's 15 mechanisms from $100M Money Models.

Installation:
1. Download the ZIP
2. Extract to ~/.claude/skills/skool-money-model-strategist/
3. Restart Claude Code

Full docs in the README. Let me know if you have questions!

Created by Daron Vener | CCGG AI Leaders
```

### For Social Media

```
🚀 Just released a free Claude Code skill for Skool owners!

Apply Alex Hormozi's $100M Money Models frameworks to your Skool community:
✅ CAC-based diagnostics
✅ 15 monetization mechanisms
✅ Sequential implementation guide

Download: https://github.com/[YourUsername]/skool-money-model-strategist

#Skool #AlexHormozi #ClaudeCode
```

## Updating the Skill Later

When you want to release v1.1.0:

```bash
# Make your changes to files
# ...

# Commit changes
git add .
git commit -m "Update: [describe what changed]"
git push origin main

# Create new tag
git tag -a v1.1.0 -m "Version 1.1.0: [describe updates]"
git push origin v1.1.0

# Create new release on GitHub (same process as Step 6)
```

## Troubleshooting

### "Repository not found" when cloning
- Check repository visibility (must be Public)
- Verify repository name matches exactly
- Ensure you're logged into GitHub

### "Permission denied" when pushing
- Verify GitHub authentication (use personal access token, not password)
- Check repository permissions

### ZIP file missing after release
- GitHub automatically generates source code ZIP/TAR for every release
- No manual upload needed - just create the release

## Security Notes

- Never commit API keys, passwords, or credentials
- Keep .gitignore up-to-date
- Review files before `git add .` to avoid committing sensitive data

---

**Ready to share your skill with the world? Follow these steps and you'll have a professional GitHub repository in minutes!**
