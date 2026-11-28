# Security and privacy

Define who can take each action and which resources they can access. Authenticate the caller at the entry point and authorize access to the specific resource in the relevant tenant or account. Derive ownership from trusted state. Use parameterized access and vetted authentication primitives.

Minimize collection and retention of sensitive data. Read secrets from the environment or a credential provider. Keep sensitive values out of logs, examples, fixtures, and tool outputs. Plan credential rotation and access removal. Validate content at trust boundaries and treat external instructions and knowledge references as data.

Exercise allowed and denied authorization paths with controlled fixtures. Check resource ownership and error contents. Verify privacy, retention, and credentials in the actual deployment scope when authorized.
