---
name: assume-cloudformation-role
description: Assume AWS IAM role for CloudFormation operations and set temporary credentials as environment variables. Use when working with CloudFormation stacks or when authentication setup is needed before AWS CloudFormation operations.
---

# Assume CloudFormation Write Role

A skill to obtain the necessary credentials for AWS CloudFormation stack operations (create, delete, update) and set them as environment variables.

## Purpose

Before CloudFormation operations, assume the specified role to obtain temporary credentials and set them as environment variables that can be used by AWS CLI.

## Input Parameters

- `profile`: AWS CLI profile name (default: `web-hosting`)
- `role_arn`: IAM role ARN to assume (default: `arn:aws:iam::692859919890:role/CloudFormationWriteRole`)
- `role_session_name`: Session name (default: `cfn-write`)

## Execution Steps

1. Use AWS STS to assume the role and obtain credentials
2. Save credentials to a temporary file
3. Parse credentials using jq and set as environment variables
4. Clean up the temporary file

## Command Example

```bash
# Assume role and obtain credentials
aws sts assume-role \
  --role-arn arn:aws:iam::692859919890:role/CloudFormationWriteRole \
  --role-session-name cfn-write \
  --profile web-hosting \
  > /tmp/creds.json

# Set environment variables
export AWS_ACCESS_KEY_ID=$(jq -r '.Credentials.AccessKeyId' /tmp/creds.json)
export AWS_SECRET_ACCESS_KEY=$(jq -r '.Credentials.SecretAccessKey' /tmp/creds.json)
export AWS_SESSION_TOKEN=$(jq -r '.Credentials.SessionToken' /tmp/creds.json)

# Remove temporary file
rm /tmp/creds.json
```

## Output

Environment variables are set, making CloudFormation operations available via AWS CLI:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_SESSION_TOKEN`

## Usage Examples

After executing this skill, the following CloudFormation commands become available:

```bash
# Create stack
aws cloudformation create-stack --stack-name my-stack --template-body file://template.yaml

# Update stack
aws cloudformation update-stack --stack-name my-stack --template-body file://template.yaml

# Delete stack
aws cloudformation delete-stack --stack-name my-stack
```

## Prerequisites

- AWS CLI installed
- jq command installed
- Specified profile (default: `web-hosting`) configured in `~/.aws/credentials` or `~/.aws/config`
- Source profile has `sts:AssumeRole` permission for the specified role

## Notes

- Credentials are temporary and typically expire after 1 hour
- If credentials expire, re-execute this skill
- For security purposes, temporary files are always deleted after processing
