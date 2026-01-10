# GraphQL Recipes

Advanced operations using `linear gql` for functionality not covered by built-in commands.

## Table of Contents

1. [Link Two Issues](#link-two-issues)
2. [Attach URL to Issue](#attach-url-to-issue)
3. [Add Comment](#add-comment)
4. [Upload File](#upload-file)
5. [Set Issue Parent](#set-issue-parent)
6. [Query Issue Relations](#query-issue-relations)
7. [Assign Issue](#assign-issue)
8. [Bulk Query IDs](#bulk-query-ids)

---

## Link Two Issues

**CLI alternative:** `linear issue link ID|IDENTIFIER --blocks|--related|--duplicate OTHER_ID --yes`

Creates relationships between issues. Relation types: `blocks`, `duplicate`, `related`.

```bash
cat > /tmp/link-issues.graphql << 'EOF'
mutation LinkIssues($issueId: String!, $relatedIssueId: String!, $type: IssueRelationType!) {
  issueRelationCreate(input: {
    issueId: $issueId
    relatedIssueId: $relatedIssueId
    type: $type
  }) {
    success
    issueRelation { id type }
  }
}
EOF

# Issue A blocks Issue B
linear gql --query /tmp/link-issues.graphql \
  --vars '{"issueId":"ISSUE-A-UUID","relatedIssueId":"ISSUE-B-UUID","type":"blocks"}' \
  --json

# Mark as duplicate
linear gql --query /tmp/link-issues.graphql \
  --vars '{"issueId":"UUID","relatedIssueId":"UUID","type":"duplicate"}' \
  --json
```

---

## Attach URL to Issue

Links external resources (PRs, docs, designs) to an issue.

```bash
cat > /tmp/attach.graphql << 'EOF'
mutation AttachLink($issueId: String!, $url: String!, $title: String!) {
  attachmentCreate(input: {
    issueId: $issueId
    url: $url
    title: $title
  }) {
    success
    attachment { id url title }
  }
}
EOF

linear gql --query /tmp/attach.graphql \
  --vars '{"issueId":"UUID","url":"https://github.com/org/repo/pull/123","title":"PR: Feature"}' \
  --json
```

Optional fields in input: `subtitle`, `iconUrl`, `metadata`.

---

## Add Comment

Adds a comment to an issue.

```bash
cat > /tmp/comment.graphql << 'EOF'
mutation AddComment($issueId: String!, $body: String!) {
  commentCreate(input: {
    issueId: $issueId
    body: $body
  }) {
    success
    comment { id body createdAt }
  }
}
EOF

linear gql --query /tmp/comment.graphql \
  --vars '{"issueId":"UUID","body":"Root cause identified in auth module."}' \
  --json
```

---

## Upload File

Three-step process: request signed URL, upload file, use asset URL.

### Step 1: Get upload URL

The `fileUpload` mutation returns an `UploadPayload` with a nested `uploadFile` object:

```bash
cat > /tmp/file-upload.graphql << 'EOF'
mutation RequestUpload($filename: String!, $contentType: String!, $size: Int!) {
  fileUpload(filename: $filename, contentType: $contentType, size: $size) {
    success
    uploadFile {
      uploadUrl
      assetUrl
      headers { key value }
    }
  }
}
EOF

linear gql --query /tmp/file-upload.graphql \
  --vars '{"filename":"screenshot.png","contentType":"image/png","size":12345}' \
  --json > /tmp/upload-response.json
```

### Step 2: Upload to signed URL

**Important:** Include ALL headers from the response to avoid 403 Forbidden errors.

```bash
# Extract uploadUrl and headers from response.uploadFile, then:
# Include every header returned (x-goog-*/x-amz-* and Content-Disposition)
curl -X PUT "UPLOAD_URL_FROM_RESPONSE" \
  -H "Content-Type: image/png" \
  -H "HEADER_KEY_FROM_RESPONSE: HEADER_VALUE" \
  --data-binary @screenshot.png
```

### Step 3: Use asset URL

The `assetUrl` from `uploadFile` can be embedded in markdown:
```markdown
![screenshot](ASSET_URL)
```

Use in issue description or comment body.

**Note:** Accessing `assetUrl` outside the Linear app requires an `Authorization: <API key>` header; unauthenticated requests return 401.

---

## Set Issue Parent

**CLI alternative:** `linear issue update CHILD_ID --parent PARENT_UUID --yes`

Makes an issue a sub-issue of another.

```bash
cat > /tmp/set-parent.graphql << 'EOF'
mutation SetParent($issueId: String!, $parentId: String!) {
  issueUpdate(id: $issueId, input: { parentId: $parentId }) {
    success
    issue { id identifier parent { identifier } }
  }
}
EOF

linear gql --query /tmp/set-parent.graphql \
  --vars '{"issueId":"CHILD-UUID","parentId":"PARENT-UUID"}' \
  --json
```

---

## Query Issue Relations

Fetches an issue with its parent, children, and linked issues.

```bash
cat > /tmp/issue-relations.graphql << 'EOF'
query IssueWithRelations($id: String!) {
  issue(id: $id) {
    identifier
    title
    parent { identifier title }
    children(first: 10) { nodes { identifier title } }
    relations(first: 10) {
      nodes {
        type
        relatedIssue { identifier title }
      }
    }
  }
}
EOF

linear gql --query /tmp/issue-relations.graphql \
  --vars '{"id":"UUID"}' \
  --json
```

---

## Assign Issue

**CLI alternative:** `linear issue update ID --assignee me|USER_ID --yes`

Assigns an issue to a user.

```bash
cat > /tmp/assign.graphql << 'EOF'
mutation AssignIssue($issueId: String!, $assigneeId: String!) {
  issueUpdate(id: $issueId, input: { assigneeId: $assigneeId }) {
    success
    issue { identifier assignee { name } }
  }
}
EOF

linear gql --query /tmp/assign.graphql \
  --vars '{"issueId":"UUID","assigneeId":"USER-UUID"}' \
  --json
```

---

## Bulk Query IDs

Useful queries for finding UUIDs needed by mutations.

### Current user
```bash
echo 'query { viewer { id name email } }' | linear gql --json
```

### All teams
```bash
echo 'query { teams { nodes { id key name } } }' | linear gql --json
```

### Issue UUID from identifier
```bash
echo 'query { issue(id: "ENG-123") { id identifier title } }' | linear gql --json
```

### All users in workspace
```bash
echo 'query { users { nodes { id name email } } }' | linear gql --json
```

### All workflow states for a team
```bash
cat << 'EOF' | linear gql --json
query {
  workflowStates {
    nodes { id name type team { key } }
  }
}
EOF
```

---

## Reference

- [Linear GraphQL API](https://linear.app/developers/graphql)
- [Schema Explorer](https://studio.apollographql.com/public/Linear-API/variant/current/schema/reference)
- [File Upload Guide](https://linear.app/developers/how-to-upload-a-file-to-linear)
