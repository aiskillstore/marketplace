---
name: deploying-to-production
description: Automate creating a GitHub repository and deploying a web project to Vercel. Use when the user asks to deploy a website/app to production, publish a project, or set up GitHub + Vercel deployment.
---

# Deploying to Production

Use this workflow when a user says "deploy this website/app" or similar. Follow the checklist in order and do not skip steps.

## Deployment Workflow

- [ ] Step 1: Run build and verify no errors
- [ ] Step 2: Create GitHub repository
- [ ] Step 3: Push code to GitHub
- [ ] Step 4: Deploy to Vercel
- [ ] Step 5: Verify deployment

### Step 1: Run build

Run:

`npm run build`

If build fails, read the errors, fix issues, and run again. Only proceed when build succeeds.

### Step 2: Create GitHub repository

Create a new GitHub repository for the project. If the repo already exists, confirm whether to reuse or create a new one.

### Step 3: Push code to GitHub

Initialize git if needed, add remote, and push the default branch. Confirm the repository contains the expected code.

### Step 4: Deploy to Vercel

Deploy the GitHub repo to Vercel. Capture the deployment URL.

### Step 5: Verify deployment

Verify the live deployment by opening the URL or checking a response. If verification fails, diagnose and redeploy.
