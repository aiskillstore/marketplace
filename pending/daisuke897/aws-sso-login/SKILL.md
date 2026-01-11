---
name: aws-sso-login
description: Authenticate to AWS using Single Sign-On (SSO). Use when AWS CLI operations require SSO authentication or when SSO session has expired.
---

# AWS SSO Login

A skill to authenticate to AWS using Single Sign-On (SSO) for a specified profile.

## Purpose

Perform SSO authentication before executing AWS CLI operations. SSO sessions typically expire after 8-12 hours, requiring re-authentication.

## Input Parameters

- `profile`: AWS CLI profile name configured for SSO (default: defined by project, e.g., `web-hosting`)
  - If the profile name is not known/available from project docs or prior context, ask the user which AWS CLI profile to use before running this skill.

## Execution Steps

1. Execute `aws sso login` command with the specified profile
2. Open browser automatically (or provide a URL to open manually)
3. Complete authentication in the browser
4. Confirm successful authentication

## Command Example

```bash
# Login with SSO using specified profile
aws sso login --profile <profile-name>
```

## Project Configuration

- Document the default profile name (e.g., `web-hosting`) in a separate project guide such as `.github/skills/README.md` or a skill configuration file.
- Refer to that document when invoking this Skill so the same definition can be reused across repositories without editing the Skill itself.

## Output

After successful authentication:
- SSO session is established and cached locally
- AWS CLI commands can be executed using the specified profile
- Session remains valid for the configured duration (typically 8-12 hours)

## Usage Examples

After executing this skill, AWS CLI commands with the profile become available:

```bash
# Verify authentication
aws sts get-caller-identity --profile web-hosting

# Assume a role (often used after SSO login)
aws sts assume-role --role-arn <role-arn> --role-session-name <session-name> --profile web-hosting
```

## Prerequisites

- AWS CLI v2 installed (SSO support requires v2 or later)
- SSO configuration set up in `~/.aws/config` for the specified profile
- Web browser available for authentication
- Network access to the SSO authentication endpoint

## Notes

- SSO sessions expire after a configured duration (typically 8-12 hours)
- When the session expires, re-execute this skill to re-authenticate
- Browser-based authentication is required; this cannot be fully automated
- For headless environments, consider using `--no-browser` flag and manually opening the provided URL
- This skill should be executed before the `assume-cloudformation-role` skill if role assumption requires SSO authentication
