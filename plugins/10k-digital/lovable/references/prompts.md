# Lovable Prompts Reference

Complete reference of Lovable prompts organized by category.

## Edge Functions

### Deployment
| Action | Prompt |
|--------|--------|
| Deploy all | `"Deploy all edge functions"` |
| Deploy specific | `"Deploy the [name] edge function"` |
| Redeploy after secret change | `"Redeploy edge functions to pick up new secrets"` |

### Creation
| Action | Prompt |
|--------|--------|
| Create basic | `"Create an edge function called [name] that [description]"` |
| Create with API | `"Create an edge function called [name] that calls [API] and [action]"` |
| Create webhook handler | `"Create an edge function to handle [service] webhooks"` |

### Debugging
| Action | Prompt |
|--------|--------|
| View logs | `"Show logs for [name] edge function"` |
| Debug error | `"The [name] edge function returns [error]. Check logs and fix it"` |
| Test function | `"Test the [name] edge function with [sample data]"` |

### Management
| Action | Prompt |
|--------|--------|
| Delete | `"Delete the [name] edge function"` |
| List all | `"List all my edge functions"` |

---

## Database Tables

### Creation
| Action | Prompt |
|--------|--------|
| Basic table | `"Create a [name] table with columns: [col1] ([type]), [col2] ([type])"` |
| With timestamps | `"Create a [name] table with columns: id (uuid primary key), [columns], created_at (timestamp default now()), updated_at (timestamp)"` |
| With user relation | `"Create a [name] table with user_id referencing auth.users"` |

### Modification
| Action | Prompt |
|--------|--------|
| Add column | `"Add a [column] column of type [type] to the [table] table"` |
| Add nullable column | `"Add an optional [column] column of type [type] to [table]"` |
| Add with default | `"Add a [column] column to [table] with default value [value]"` |
| Rename column | `"Rename the [old] column to [new] in [table]"` |
| Change type | `"Change the [column] column in [table] from [old_type] to [new_type]"` |
| Remove column | `"Remove the [column] column from [table]"` |
| Drop table | `"Delete the [table] table"` ⚠️ DESTRUCTIVE |

### Relationships
| Action | Prompt |
|--------|--------|
| Foreign key | `"Add foreign key from [table1].[column] to [table2].id"` |
| Cascade delete | `"Add foreign key from [table1].[column] to [table2].id with cascade delete"` |
| Many-to-many | `"Create a junction table [name] linking [table1] and [table2]"` |

### Indexes
| Action | Prompt |
|--------|--------|
| Basic index | `"Add an index on [table].[column]"` |
| Composite | `"Add index on [table] for columns [col1], [col2]"` |
| Unique constraint | `"Add unique constraint on [table].[column]"` |
| Composite unique | `"Add unique constraint on [table] for [col1] and [col2] combined"` |

---

## Migrations

| Action | Prompt |
|--------|--------|
| Apply pending | `"Apply pending Supabase migrations"` |
| Apply specific | `"Apply the migration [filename]"` |
| Review first | `"Review and apply the latest migration"` |
| Show status | `"Show migration status"` |

---

## RLS Policies

### Enable RLS
| Action | Prompt |
|--------|--------|
| Enable | `"Enable RLS on [table]"` |
| Enable with policy | `"Enable RLS on [table] with [policy description]"` |

### Read Policies
| Action | Prompt |
|--------|--------|
| Public read | `"Allow public read access to [table]"` |
| Authenticated read | `"Allow authenticated users to read all rows in [table]"` |
| Own rows only | `"Allow users to only read their own rows in [table] (where user_id = auth.uid())"` |
| Role-based read | `"Allow users with role [role] to read [table]"` |

### Write Policies
| Action | Prompt |
|--------|--------|
| Authenticated insert | `"Allow authenticated users to insert into [table]"` |
| Own rows insert | `"Allow users to insert rows in [table] with their own user_id"` |
| Own rows update | `"Allow users to only update their own rows in [table]"` |
| Own rows delete | `"Allow users to only delete their own rows in [table]"` |

### Combined Policies
| Action | Prompt |
|--------|--------|
| Full own-row access | `"Add RLS policies to [table] allowing users full access to only their own rows"` |
| Read all, write own | `"Allow reading all rows in [table] but only writing own rows"` |

---

## Storage

### Buckets
| Action | Prompt |
|--------|--------|
| Create public | `"Create a public storage bucket called [name]"` |
| Create private | `"Create a private storage bucket called [name]"` |
| Delete bucket | `"Delete the [name] storage bucket"` ⚠️ DESTRUCTIVE |

### Policies
| Action | Prompt |
|--------|--------|
| Auth upload | `"Allow authenticated users to upload to [bucket]"` |
| Auth download | `"Allow authenticated users to download from [bucket]"` |
| Public read | `"Make [bucket] publicly readable"` |
| Own files only | `"Allow users to only access their own files in [bucket]"` |
| Size limit | `"Limit uploads to [bucket] to [size]MB"` |
| Type restriction | `"Only allow [image/pdf/etc] uploads to [bucket]"` |

---

## Authentication

### Providers
| Action | Prompt |
|--------|--------|
| Enable Google | `"Enable Google authentication"` |
| Enable GitHub | `"Enable GitHub authentication"` |
| Enable Apple | `"Enable Apple authentication"` |
| Enable email | `"Enable email/password authentication"` |
| Enable magic link | `"Enable magic link authentication"` |

### Triggers
| Action | Prompt |
|--------|--------|
| Profile on signup | `"When a user signs up, create a row in profiles table with their user_id"` |
| Custom data on signup | `"When a user signs up, create a row in [table] with [columns]"` |
| Delete cascade | `"When a user is deleted, delete their data from [tables]"` |

### Configuration
| Action | Prompt |
|--------|--------|
| Redirect URL | `"Set auth redirect URL to [url]"` |
| Email template | `"Customize the [signup/reset/etc] email template"` |

---

## Database Functions (Postgres)

| Action | Prompt |
|--------|--------|
| Create function | `"Create a Postgres function called [name] that [description]"` |
| Create with params | `"Create a Postgres function [name] that takes [params] and returns [type]"` |
| RPC function | `"Create an RPC function [name] that [description]"` |

---

## Database Triggers

| Action | Prompt |
|--------|--------|
| Updated_at | `"Add updated_at trigger to [table]"` |
| Custom trigger | `"Create a trigger on [table] that [action] when [event]"` |
| Before insert | `"Add a before-insert trigger on [table] that [action]"` |
| After update | `"Add an after-update trigger on [table] that [action]"` |

---

## Secrets (Manual)

Secrets cannot be set via prompts. Instructions:

1. Go to **Cloud** → **Secrets**
2. Click **Add secret**
3. Enter:
   - **Key**: `SECRET_NAME`
   - **Value**: Your secret value
4. Click **Save**
5. Run: `"Redeploy edge functions to pick up new secrets"`

Common secrets:
- `OPENAI_API_KEY`
- `STRIPE_SECRET_KEY`
- `RESEND_API_KEY`
- `TWILIO_AUTH_TOKEN`
- `SENDGRID_API_KEY`
