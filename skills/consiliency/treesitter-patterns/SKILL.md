---
name: treesitter-patterns
description: "Universal patterns for tree-sitter code parsing. Covers AST visitors, query patterns, and language plugin development. Framework-agnostic."
---

# Tree-sitter Patterns Skill

Universal patterns for working with tree-sitter in any project. Covers AST parsing, query patterns, visitors, and language plugin development.

## Design Principle

This skill is **framework-generic**. It provides universal tree-sitter patterns:
- NOT tailored to Code-Index-MCP, treesitter-chunker, or any specific project
- Covers common patterns applicable across all tree-sitter projects
- Project-specific queries go in project-specific skills

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| TREE_SITTER_DIR | tree_sitter | Directory for language parsers |
| QUERY_DIR | queries | Directory for .scm query files |
| LANGUAGES | auto | Auto-detect or list of languages |

## Instructions

**MANDATORY** - Follow the Workflow steps below in order.

1. Identify languages to parse
2. Install appropriate language parsers
3. Write queries for extraction needs
4. Handle edge cases and errors

## Red Flags - STOP and Reconsider

If you're about to:
- Parse without error handling (syntax errors are common)
- Assume all files parse successfully
- Write queries without testing on sample code
- Ignore performance for large files

**STOP** -> Add error handling -> Test on edge cases -> Then proceed

## Cookbook

### Language Plugin Development
- IF: Creating a new language parser
- THEN: Read and execute `./cookbook/language-plugin.md`

### AST Visitor Patterns
- IF: Walking the AST to extract information
- THEN: Read and execute `./cookbook/ast-visitor.md`

### Query Patterns
- IF: Writing tree-sitter queries
- THEN: Read and execute `./cookbook/query-patterns.md`

## Quick Reference

### Python Setup

```python
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

# Create parser
parser = Parser(Language(tspython.language()))

# Parse code
source = b"def hello(): pass"
tree = parser.parse(source)

# Access root node
root = tree.root_node
print(root.sexp())
```

### Node Navigation

```python
# Get children
for child in node.children:
    print(child.type, child.text)

# Named children only (skip punctuation)
for child in node.named_children:
    print(child.type)

# Find by type
def find_all(node, type_name):
    results = []
    if node.type == type_name:
        results.append(node)
    for child in node.children:
        results.extend(find_all(child, type_name))
    return results

functions = find_all(root, "function_definition")
```

### Query Language

```scheme
; Match function definitions
(function_definition
  name: (identifier) @function.name
  parameters: (parameters) @function.params
  body: (block) @function.body)

; Match class definitions
(class_definition
  name: (identifier) @class.name
  body: (block) @class.body)

; Match imports
(import_statement
  (dotted_name) @import.module)

; Match decorated functions
(decorated_definition
  (decorator) @decorator
  definition: (function_definition
    name: (identifier) @function.name))
```

### Running Queries

```python
from tree_sitter import Query

query = Query(Language(tspython.language()), """
(function_definition
  name: (identifier) @name
  body: (block) @body)
""")

captures = query.captures(root)
for node, name in captures:
    print(f"{name}: {node.text.decode()}")
```

### Common Node Types

| Language | Functions | Classes | Imports |
|----------|-----------|---------|---------|
| Python | `function_definition` | `class_definition` | `import_statement` |
| JavaScript | `function_declaration` | `class_declaration` | `import_statement` |
| TypeScript | `function_declaration` | `class_declaration` | `import_statement` |
| Go | `function_declaration` | `type_declaration` | `import_declaration` |
| Rust | `function_item` | `impl_item` | `use_declaration` |

### Error Handling

```python
def safe_parse(source: bytes) -> tuple[Tree | None, list[str]]:
    """Parse with error collection."""
    tree = parser.parse(source)
    errors = []

    def collect_errors(node):
        if node.type == "ERROR" or node.is_missing:
            errors.append(f"Error at {node.start_point}: {node.text[:50]}")
        for child in node.children:
            collect_errors(child)

    collect_errors(tree.root_node)
    return tree, errors

tree, errors = safe_parse(source)
if errors:
    print(f"Parse errors: {errors}")
```

## Visitor Pattern

```python
from abc import ABC, abstractmethod

class ASTVisitor(ABC):
    """Base visitor for tree-sitter AST."""

    def visit(self, node):
        method_name = f"visit_{node.type}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for child in node.named_children:
            self.visit(child)

    @abstractmethod
    def visit_function_definition(self, node):
        pass

class FunctionExtractor(ASTVisitor):
    def __init__(self):
        self.functions = []

    def visit_function_definition(self, node):
        name_node = node.child_by_field_name("name")
        if name_node:
            self.functions.append(name_node.text.decode())
        self.generic_visit(node)

extractor = FunctionExtractor()
extractor.visit(tree.root_node)
print(extractor.functions)
```

## Performance Tips

1. **Incremental parsing**: For edits, use `parser.parse(new_source, old_tree)`
2. **Lazy evaluation**: Don't traverse entire tree if you only need specific nodes
3. **Query optimization**: Use more specific queries to reduce matches
4. **Memory management**: Large files can use significant memory
5. **Batch processing**: Process multiple files in parallel

## Integration

### With Code Analysis

```python
def analyze_file(path: Path) -> CodeAnalysis:
    source = path.read_bytes()
    tree = parser.parse(source)

    return CodeAnalysis(
        functions=extract_functions(tree),
        classes=extract_classes(tree),
        imports=extract_imports(tree),
        complexity=calculate_complexity(tree)
    )
```

### With BAML

```baml
class CodeStructure {
  functions FunctionInfo[]
  classes ClassInfo[]
  imports string[]
}

class FunctionInfo {
  name string
  parameters string[]
  return_type string?
  line_start int
  line_end int
}
```

## Best Practices

1. **Error tolerance**: Always handle parse errors gracefully
2. **Use queries**: Prefer queries over manual traversal
3. **Test on real code**: Test with actual codebases, not just samples
4. **Document node types**: Reference language grammar for node types
5. **Version parsers**: Pin tree-sitter language versions
