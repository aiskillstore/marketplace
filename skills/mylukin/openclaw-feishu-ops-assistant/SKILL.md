---
name: openclaw-feishu-ops-assistant
description: |
  Feishu (Lark) workspace operations for OpenClaw agents. Provides document CRUD, cloud drive management,
  permission control, and knowledge-base navigation through a unified tool surface.
  Activate when user mentions Feishu docs, wiki, drive, permissions, or Lark cloud documents.
metadata:
  openclaw:
    emoji: "📎"
    requires:
      plugins: ["feishu"]
      config:
        - channels.feishu
---

# Feishu Ops Assistant

A skill bundle that teaches OpenClaw agents how to operate Feishu (Lark) workspace resources:
documents, cloud drive, permissions, and knowledge bases.

> **Platform:** OpenClaw with the `feishu` plugin enabled.
> **Trigger keywords:** Feishu, Lark, 飞书, cloud doc, wiki, drive, permissions, 文档, 知识库, 云空间, 权限

---

## Bundled Skills

| # | Skill | Tool | What it does |
|---|-------|------|-------------|
| 1 | [feishu-doc](#1-feishu-doc) | `feishu_doc` | Read, write, append, create documents; manage blocks and tables |
| 2 | [feishu-drive](#2-feishu-drive) | `feishu_drive` | List, create, move, and delete files/folders in cloud storage |
| 3 | [feishu-perm](#3-feishu-perm) | `feishu_perm` | Add/remove collaborators, manage sharing and permissions |
| 4 | [feishu-wiki](#4-feishu-wiki) | `feishu_wiki` | Navigate knowledge bases, create/move/rename wiki pages |

---

## Quick Start

1. Ensure the **feishu** plugin is enabled in your OpenClaw config.
2. Install this skill into your agent workspace:
   ```
   clawhub install openclaw-feishu-ops-assistant
   ```
3. Ask your agent to read a Feishu doc:
   ```
   Read this doc: https://xxx.feishu.cn/docx/ABC123def
   ```

---

## 1. feishu-doc

Single tool `feishu_doc` with an `action` parameter for all document operations.

### Token Extraction

From URL `https://xxx.feishu.cn/docx/ABC123def` → `doc_token` = `ABC123def`

### Core Actions

| Action | Description |
|--------|-------------|
| `read` | Get plain-text content + block statistics |
| `write` | Replace entire document with Markdown |
| `append` | Append Markdown to end of document |
| `create` | Create a new document (optionally in a folder) |
| `list_blocks` | List all blocks (tables, images, code, etc.) |
| `get_block` | Get a single block by ID |
| `update_block` | Update block text content |
| `delete_block` | Delete a block |

### Tables

| Action | Description |
|--------|-------------|
| `create_table` | Create a table in a document |
| `create_table_with_values` | Create a table pre-filled with data |
| `write_table_cells` | Write values into existing table cells |
| `insert_table_row` / `insert_table_column` | Insert rows or columns |
| `delete_table_rows` / `delete_table_columns` | Delete rows or columns |
| `merge_table_cells` | Merge a range of cells |

### Media

| Action | Description |
|--------|-------------|
| `upload_image` | Upload an image (URL, file path, or base64) into a document |
| `upload_file` | Upload a file attachment into a document |

### Reading Workflow

1. Start with `action: "read"` — get plain text + statistics.
2. Check `block_types` in response for Table, Image, Code, etc.
3. If structured content exists, use `action: "list_blocks"` for full data.

### Permissions Required

`docx:document`, `docx:document:readonly`, `docx:document.block:convert`, `drive:drive`

---

## 2. feishu-drive

Single tool `feishu_drive` for cloud storage operations.

### Token Extraction

From URL `https://xxx.feishu.cn/drive/folder/ABC123` → `folder_token` = `ABC123`

### Actions

| Action | Description |
|--------|-------------|
| `list` | List folder contents (root if no token) |
| `info` | Get file metadata |
| `create_folder` | Create a new folder |
| `move` | Move a file/folder |
| `delete` | Delete a file/folder |

### File Types

`doc`, `docx`, `sheet`, `bitable`, `folder`, `file`, `mindnote`, `shortcut`

### Known Limitation

Feishu bots have no root folder. The bot can only access files/folders that have been **shared with it**.
Users must first create a folder and share it with the bot.

### Permissions Required

`drive:drive` (full) or `drive:drive:readonly` (read-only)

---

## 3. feishu-perm

Single tool `feishu_perm` for managing file/document permissions.

> **Disabled by default** — permission management is sensitive. Enable via config:
> ```yaml
> channels:
>   feishu:
>     tools:
>       perm: true
> ```

### Actions

| Action | Description |
|--------|-------------|
| `list` | List collaborators on a resource |
| `add` | Add a collaborator (email, user ID, group, department) |
| `remove` | Remove a collaborator |

### Permission Levels

| Level | Description |
|-------|-------------|
| `view` | View only |
| `edit` | Can edit |
| `full_access` | Full access (can manage permissions) |

### Member Types

`email`, `openid`, `userid`, `unionid`, `openchat`, `opendepartmentid`

### Permissions Required

`drive:permission`

---

## 4. feishu-wiki

Single tool `feishu_wiki` for knowledge-base operations.

### Token Extraction

From URL `https://xxx.feishu.cn/wiki/ABC123def` → `token` = `ABC123def`

### Actions

| Action | Description |
|--------|-------------|
| `spaces` | List all accessible knowledge spaces |
| `nodes` | List child nodes of a space or parent node |
| `get` | Get node details (returns `obj_token` for doc operations) |
| `search` | Search for nodes by keyword |
| `create` | Create a new wiki page (docx, sheet, bitable, etc.) |
| `move` | Move a node within or across spaces |
| `rename` | Rename a node |

### Wiki → Doc Workflow

1. Get node: `feishu_wiki { action: "get", token: "wiki_token" }` → returns `obj_token`
2. Read content: `feishu_doc { action: "read", doc_token: "<obj_token>" }`
3. Edit content: `feishu_doc { action: "write", doc_token: "<obj_token>", content: "..." }`

### Permissions Required

`wiki:wiki` or `wiki:wiki:readonly`

---

## Configuration Reference

```yaml
channels:
  feishu:
    tools:
      doc: true    # default: true
      drive: true  # default: true
      perm: false  # default: false (enable explicitly)
      wiki: true   # default: true
```

## Feishu App Permissions Checklist

| Scope | Required for |
|-------|-------------|
| `docx:document` | Doc read/write |
| `docx:document:readonly` | Doc read-only |
| `docx:document.block:convert` | Block operations |
| `drive:drive` | Drive full access |
| `drive:drive:readonly` | Drive read-only |
| `drive:permission` | Permission management |
| `wiki:wiki` | Wiki full access |
| `wiki:wiki:readonly` | Wiki read-only |
