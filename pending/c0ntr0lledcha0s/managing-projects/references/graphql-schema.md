# GitHub Projects v2 GraphQL Schema Reference

## Key Types

### Project
```graphql
type ProjectV2 {
  id: ID!
  title: String!
  number: Int!
  shortDescription: String
  public: Boolean!
  closed: Boolean!
  items(first: Int): ProjectV2ItemConnection!
  fields(first: Int): ProjectV2FieldConfigurationConnection!
  views(first: Int): ProjectV2ViewConnection!
}
```

### Item
```graphql
type ProjectV2Item {
  id: ID!
  type: ProjectV2ItemType!
  content: ProjectV2ItemContent
  fieldValues(first: Int): ProjectV2ItemFieldValueConnection!
}

union ProjectV2ItemContent = Issue | PullRequest | DraftIssue
```

### Field Types
```graphql
union ProjectV2FieldConfiguration =
  | ProjectV2Field
  | ProjectV2IterationField
  | ProjectV2SingleSelectField

type ProjectV2SingleSelectField {
  id: ID!
  name: String!
  options: [ProjectV2SingleSelectFieldOption!]!
}
```

## Common Queries

### Get Project
```graphql
query GetProject($owner: String!, $number: Int!) {
  user(login: $owner) {
    projectV2(number: $number) {
      id
      title
      items(first: 100) {
        nodes {
          id
          content {
            ... on Issue { title number }
            ... on PullRequest { title number }
          }
        }
      }
    }
  }
}
```

### Get Project Fields
```graphql
query GetFields($projectId: ID!) {
  node(id: $projectId) {
    ... on ProjectV2 {
      fields(first: 20) {
        nodes {
          ... on ProjectV2SingleSelectField {
            id
            name
            options { id name }
          }
        }
      }
    }
  }
}
```

## Common Mutations

### Add Item
```graphql
mutation AddItem($projectId: ID!, $contentId: ID!) {
  addProjectV2ItemById(input: {
    projectId: $projectId
    contentId: $contentId
  }) {
    item { id }
  }
}
```

### Update Field Value
```graphql
mutation UpdateField($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!) {
  updateProjectV2ItemFieldValue(input: {
    projectId: $projectId
    itemId: $itemId
    fieldId: $fieldId
    value: $value
  }) {
    projectV2Item { id }
  }
}
```

### Delete Item
```graphql
mutation DeleteItem($projectId: ID!, $itemId: ID!) {
  deleteProjectV2Item(input: {
    projectId: $projectId
    itemId: $itemId
  }) {
    deletedItemId
  }
}
```

## Field Value Types

```graphql
input ProjectV2FieldValue {
  text: String
  number: Float
  date: Date
  singleSelectOptionId: ID
  iterationId: ID
}
```

## Pagination

All connections support cursor-based pagination:
```graphql
items(first: 100, after: $cursor) {
  pageInfo {
    hasNextPage
    endCursor
  }
  nodes { ... }
}
```

## Rate Limits

- 5,000 points per hour
- Queries: 1 point
- Mutations: 1-10 points
- Check `X-RateLimit-*` headers
