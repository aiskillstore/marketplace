# Python Reference

## Imports
- **No Function-Local Imports**: All imports should be at the top of the file. Do not use imports inside functions or methods.
- **Avoid `if TYPE_CHECKING:` for Circular Dependencies**: Using `if TYPE_CHECKING:` to hide circular imports is considered an anti-pattern. Instead, refactor the code and move logic/definitions to separate modules to break the circular dependency.
