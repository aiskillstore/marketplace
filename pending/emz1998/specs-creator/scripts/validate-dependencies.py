#!/usr/bin/env python3
"""
Specification Dependency Validation Script

Validates that all dependencies referenced in a specification document exist.
Prevents proceeding with spec creation if required dependencies are not yet created.

Usage:
    python validate-dependencies.py <spec-file.md> [--specs-dir <directory>]

Returns:
    Exit code 0: All dependencies exist
    Exit code 1: Missing dependencies found (cannot proceed)
    Exit code 2: Warning - some optional dependencies missing

Exceptions:
    FileNotFoundError: Specification file not found
    ValueError: File too large or invalid format
    PermissionError: Cannot read file
"""

import re
import sys
import functools
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from enum import Enum


# =============================================================================
# Constants
# =============================================================================

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_SEARCH_DEPTH = 5  # Maximum directory depth for recursive searches
MAX_SEARCH_RESULTS = 1000  # Maximum files to search through
ALLOWED_EXTENSIONS = {'.md', '.markdown'}
FALLBACK_ENCODING = 'latin-1'


# =============================================================================
# Pre-compiled Regex Patterns (Safe - no nested quantifiers)
# =============================================================================

# Section header pattern
SECTION_HEADER_PATTERN = re.compile(
    r'^#{1,3}\s*(?:Dependencies|Depends\s+On|Prerequisites|Requirements)\s*$',
    re.IGNORECASE | re.MULTILINE
)

# Next section pattern
NEXT_SECTION_PATTERN = re.compile(r'^#{1,3}\s+', re.MULTILINE)

# Dependency extraction patterns (safe patterns)
# Only match when explicitly referencing specs/dependencies
INLINE_DEPENDS_PATTERN = re.compile(
    r'depends\s+on\s+(?:the\s+)?["\']?([a-zA-Z0-9_-]+)["\']?\s+(?:spec|prd|document)',
    re.IGNORECASE
)
INLINE_REQUIRES_PATTERN = re.compile(
    r'requires?\s+(?:the\s+)?["\']?([a-zA-Z0-9_-]+)["\']?\s+(?:spec(?:ification)?|prd|document)',
    re.IGNORECASE
)
INLINE_BLOCKED_PATTERN = re.compile(
    r'blocked\s+by\s+(?:the\s+)?["\']?([a-zA-Z0-9_-]+)["\']?\s+(?:spec|prd|document)?',
    re.IGNORECASE
)

# Markdown link pattern (safe - no nested quantifiers)
MARKDOWN_LINK_PATTERN = re.compile(
    r'\[([^\]]{1,100})\]\(([^)]{1,200}\.(?:md|json|yaml|yml))\)',
    re.IGNORECASE
)

# See/refer pattern
SEE_REFER_PATTERN = re.compile(
    r'(?:see|refer(?:\s+to)?)\s+["\']?([a-zA-Z0-9_-]+)["\']?\s+spec',
    re.IGNORECASE
)

# File reference patterns (safe)
FILE_PATH_PATTERN = re.compile(
    r'(?:file|path):\s*["\']?([a-zA-Z0-9_/.-]+\.[a-zA-Z]{2,4})["\']?',
    re.IGNORECASE
)
BACKTICK_FILE_PATTERN = re.compile(
    r'`([a-zA-Z0-9_/.-]+\.(?:md|json|yaml|yml|txt))`'
)

# Feature/system dependency pattern
FEATURE_PATTERN = re.compile(
    r'(?:feature|system|module|component):\s*([^,\n]{1,100})',
    re.IGNORECASE
)

# Spec reference pattern
SPEC_REFERENCE_PATTERN = re.compile(
    r'([a-zA-Z-_]+)\s*(?:spec(?:ification)?|prd)',
    re.IGNORECASE
)

# Bullet point pattern for line cleaning
BULLET_PATTERN = re.compile(r'^[-*]\s*')


# =============================================================================
# Data Classes and Enums
# =============================================================================

class DependencyType(Enum):
    SPEC = "specification"
    FILE = "file"
    SYSTEM = "system"
    API = "api"
    TEAM = "team"
    FEATURE = "feature"


class ValidationStatus(Enum):
    FOUND = "found"
    MISSING = "missing"
    SKIPPED = "skipped"


@dataclass
class Dependency:
    """Represents a dependency found in a spec"""
    name: str
    dep_type: DependencyType
    reference: str
    required: bool = True
    line_number: int = 0


@dataclass
class DependencyResult:
    """Result of dependency validation"""
    dependency: Dependency
    status: ValidationStatus
    path: Optional[str] = None
    message: str = ""

    @property
    def exists(self) -> bool:
        return self.status == ValidationStatus.FOUND


@dataclass
class ExtractedDep:
    """Extracted dependency from content"""
    name: str
    is_spec: bool


# =============================================================================
# Validator Class
# =============================================================================

class DependencyValidator:
    """Validates specification dependencies"""

    # Known spec file patterns
    SPEC_PATTERNS: Dict[str, List[str]] = {
        "prd": ["prd.md", "product-spec.md", "product.md"],
        "product": ["prd.md", "product-spec.md", "product.md"],
        "technical": ["tech-spec.md", "technical-spec.md", "tech.md"],
        "tech": ["tech-spec.md", "technical-spec.md", "tech.md"],
        "design": ["design-spec.md", "design.md", "ui-ux.md", "ux.md"],
        "api": ["api-spec.md", "api.md", "openapi.yaml", "openapi.json"],
        "system": ["system-spec.md", "system.md", "architecture.md"],
        "qa": ["qa-spec.md", "qa.md", "test-spec.md"],
    }

    def __init__(self, file_path: str, specs_dir: Optional[str] = None):
        self.file_path = Path(file_path).resolve()  # Canonical path
        self._validate_file_path()
        self.content = self._read_file()
        self.specs_dir = Path(specs_dir).resolve() if specs_dir else self._detect_specs_dir()
        self.dependencies: List[Dependency] = []
        self.results: List[DependencyResult] = []
        self._spec_files_cache: Optional[List[Path]] = None

    def _validate_file_path(self) -> None:
        """Validate file path before reading"""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Specification file not found: {self.file_path}")

        if not self.file_path.is_file():
            raise ValueError(f"Path is not a file: {self.file_path}")

        if self.file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Invalid file extension. Expected {ALLOWED_EXTENSIONS}, got: {self.file_path.suffix}")

        file_size = self.file_path.stat().st_size
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"File too large: {file_size} bytes (max: {MAX_FILE_SIZE} bytes)")

    def _read_file(self) -> str:
        """Read specification file with proper error handling"""
        try:
            return self.file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                return self.file_path.read_text(encoding=FALLBACK_ENCODING)
            except Exception as e:
                raise ValueError(f"Cannot decode file content: {e}")
        except PermissionError:
            raise PermissionError(f"Permission denied reading file: {self.file_path}")

    def _detect_specs_dir(self) -> Path:
        """Detect the specs directory"""
        possible_dirs = [
            self.file_path.parent,
            self.file_path.parent / "specs",
            self.file_path.parent.parent / "specs",
            self.file_path.parent.parent / "docs" / "specs",
            Path(".claude/docs/specs"),
            Path("docs/specs"),
            Path("specs"),
        ]

        for dir_path in possible_dirs:
            if dir_path.exists() and dir_path.is_dir():
                return dir_path

        return self.file_path.parent

    @functools.cached_property
    def project_root(self) -> Optional[Path]:
        """Find project root by looking for common markers (cached)"""
        markers = ['.git', 'package.json', 'pyproject.toml', 'Cargo.toml', 'go.mod']
        current = self.file_path.parent.resolve()

        for _ in range(20):  # Limit traversal depth
            if current == current.parent:
                break
            for marker in markers:
                if (current / marker).exists():
                    return current
            current = current.parent

        return None

    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is within project boundaries (security)"""
        if not self.project_root:
            return True  # Can't validate without project root

        try:
            resolved = path.resolve()
            # Check for symlinks pointing outside project
            if path.is_symlink():
                resolved = path.resolve()
            resolved.relative_to(self.project_root.resolve())
            return True
        except (ValueError, OSError):
            return False

    def _get_all_spec_files(self) -> List[Path]:
        """Get all spec files with caching and depth limiting"""
        if self._spec_files_cache is not None:
            return self._spec_files_cache

        spec_files: List[Path] = []
        count = 0

        def search_dir(directory: Path, depth: int = 0) -> None:
            nonlocal count
            if depth > MAX_SEARCH_DEPTH or count >= MAX_SEARCH_RESULTS:
                return

            try:
                for item in directory.iterdir():
                    if count >= MAX_SEARCH_RESULTS:
                        break
                    if item.is_symlink():
                        continue  # Skip symlinks for security
                    if item.is_file() and item.suffix.lower() in ALLOWED_EXTENSIONS:
                        spec_files.append(item)
                        count += 1
                    elif item.is_dir() and not item.name.startswith('.'):
                        search_dir(item, depth + 1)
            except PermissionError:
                pass  # Skip directories we can't access

        search_dir(self.specs_dir)
        self._spec_files_cache = spec_files
        return spec_files

    def _extract_from_section(self, content: str) -> List[ExtractedDep]:
        """Extract dependencies from a dependency section"""
        deps: List[ExtractedDep] = []
        lines = content.strip().split('\n')

        for line in lines:
            # Remove bullet points and clean up (using pre-compiled pattern)
            clean_line = BULLET_PATTERN.sub('', line).strip()
            if not clean_line or len(clean_line) < 2:
                continue

            # Check for spec references
            spec_match = SPEC_REFERENCE_PATTERN.search(clean_line)
            if spec_match:
                deps.append(ExtractedDep(name=spec_match.group(1).lower(), is_spec=True))
                continue

            # Check for feature/system dependencies
            feature_match = FEATURE_PATTERN.search(clean_line)
            if feature_match:
                deps.append(ExtractedDep(name=feature_match.group(1).strip(), is_spec=False))
                continue

            # Generic dependency with colon
            if ':' in clean_line:
                name = clean_line.split(':')[0].strip()
                if name and len(name) > 1:
                    deps.append(ExtractedDep(name=name.lower(), is_spec=False))

        return deps

    def _extract_from_sections(self) -> None:
        """Extract dependencies from dedicated sections"""
        lines = self.content.split('\n')
        in_dependency_section = False
        section_content: List[str] = []
        section_start_line = 0

        for i, line in enumerate(lines, 1):
            # Check for dependency section headers
            if SECTION_HEADER_PATTERN.match(line):
                in_dependency_section = True
                section_start_line = i
                continue

            # Check for next section header (end of dependency section)
            if in_dependency_section and NEXT_SECTION_PATTERN.match(line) and not SECTION_HEADER_PATTERN.match(line):
                self._process_section_content(section_content, section_start_line)
                in_dependency_section = False
                section_content = []

            if in_dependency_section:
                section_content.append(line)

        # Process remaining section content
        if section_content:
            self._process_section_content(section_content, section_start_line)

    def _process_section_content(self, content: List[str], line_number: int) -> None:
        """Process content from a dependency section"""
        section_deps = self._extract_from_section('\n'.join(content))
        for dep in section_deps:
            dep_type = DependencyType.SPEC if dep.is_spec else DependencyType.FEATURE
            self.dependencies.append(Dependency(
                name=dep.name,
                dep_type=dep_type,
                reference="Dependencies section",
                required=True,
                line_number=line_number
            ))

    def _extract_inline_patterns(self) -> None:
        """Extract dependencies from inline patterns"""
        patterns_required = [
            (INLINE_DEPENDS_PATTERN, True),
            (INLINE_REQUIRES_PATTERN, True),
            (INLINE_BLOCKED_PATTERN, True),
        ]
        patterns_optional = [
            (MARKDOWN_LINK_PATTERN, False),
            (SEE_REFER_PATTERN, False),
        ]

        for pattern, is_required in patterns_required + patterns_optional:
            for match in pattern.finditer(self.content):
                if pattern == MARKDOWN_LINK_PATTERN:
                    # Link pattern [name](path)
                    name = match.group(1)
                    path = match.group(2)
                    if path.lower().endswith('.md'):
                        self.dependencies.append(Dependency(
                            name=name,
                            dep_type=DependencyType.SPEC,
                            reference=path,
                            required=is_required
                        ))
                else:
                    name = match.group(1).strip()
                    if name and len(name) > 2:
                        self.dependencies.append(Dependency(
                            name=name,
                            dep_type=DependencyType.SPEC,
                            reference=match.group(0),
                            required=is_required
                        ))

    def _extract_file_references(self) -> None:
        """Extract file dependencies"""
        file_patterns = [FILE_PATH_PATTERN, BACKTICK_FILE_PATTERN]

        for pattern in file_patterns:
            for match in pattern.finditer(self.content):
                file_ref = match.group(1)
                # Skip if it's a spec file (already handled)
                if not file_ref.lower().endswith('.md'):
                    self.dependencies.append(Dependency(
                        name=file_ref,
                        dep_type=DependencyType.FILE,
                        reference=match.group(0),
                        required=False
                    ))

    def _deduplicate_dependencies(self) -> None:
        """Remove duplicate dependencies"""
        seen: Set[str] = set()
        unique_deps: List[Dependency] = []

        for dep in self.dependencies:
            key = f"{dep.dep_type.value}:{dep.name.lower()}"
            if key not in seen:
                seen.add(key)
                unique_deps.append(dep)

        self.dependencies = unique_deps

    def _extract_dependencies(self) -> None:
        """Extract all dependencies from the spec content"""
        self._extract_from_sections()
        self._extract_inline_patterns()
        self._extract_file_references()
        self._deduplicate_dependencies()

    def _find_spec_file(self, spec_name: str) -> Optional[Path]:
        """Try to find a spec file by name"""
        spec_name_lower = spec_name.lower().replace(' ', '-').replace('_', '-')

        # Check known patterns first
        for key, patterns in self.SPEC_PATTERNS.items():
            if key in spec_name_lower or spec_name_lower in key:
                for pattern in patterns:
                    spec_path = self.specs_dir / pattern
                    if spec_path.exists():
                        return spec_path

        # Try direct filename matches
        possible_filenames = [
            f"{spec_name_lower}.md",
            f"{spec_name_lower}-spec.md",
            f"{spec_name_lower}-specification.md",
            f"{spec_name_lower.replace('-', '_')}.md",
        ]

        for filename in possible_filenames:
            spec_path = self.specs_dir / filename
            if spec_path.exists():
                return spec_path

        # Search using cached file list
        for md_file in self._get_all_spec_files():
            if spec_name_lower in md_file.stem.lower():
                return md_file

        return None

    def _find_file(self, file_ref: str) -> Optional[Path]:
        """Try to find a referenced file with path traversal protection (TOCTOU-safe)"""
        # Normalize the path
        file_ref_clean = file_ref.strip().strip('"\'')

        # Reject path traversal attempts
        if '..' in file_ref_clean:
            return None

        # For absolute paths, resolve and verify within project
        if file_ref_clean.startswith('/'):
            try:
                abs_path = Path(file_ref_clean).resolve()
                if self._is_safe_path(abs_path) and abs_path.is_file():
                    return abs_path
            except (OSError, ValueError):
                pass
            return None

        # Try paths in order, using resolve() to get canonical path
        candidates = [
            self.file_path.parent / file_ref_clean,
            self.specs_dir / file_ref_clean,
        ]
        if self.project_root:
            candidates.append(self.project_root / file_ref_clean)

        for candidate in candidates:
            try:
                resolved = candidate.resolve()
                if self._is_safe_path(resolved) and resolved.is_file():
                    return resolved
            except (OSError, ValueError):
                continue

        return None

    def _validate_spec_dependency(self, dep: Dependency) -> DependencyResult:
        """Validate a spec dependency"""
        spec_path = self._find_spec_file(dep.name)
        if spec_path:
            return DependencyResult(
                dependency=dep,
                status=ValidationStatus.FOUND,
                path=str(spec_path),
                message=f"Found at {spec_path}"
            )
        return DependencyResult(
            dependency=dep,
            status=ValidationStatus.MISSING,
            message=f"Spec '{dep.name}' not found in {self.specs_dir} (referenced at line {dep.line_number})"
        )

    def _validate_file_dependency(self, dep: Dependency) -> DependencyResult:
        """Validate a file dependency"""
        file_path = self._find_file(dep.name)
        if file_path:
            return DependencyResult(
                dependency=dep,
                status=ValidationStatus.FOUND,
                path=str(file_path),
                message=f"Found at {file_path}"
            )
        return DependencyResult(
            dependency=dep,
            status=ValidationStatus.MISSING,
            message=f"File '{dep.name}' not found"
        )

    def _validate_other_dependency(self, dep: Dependency) -> DependencyResult:
        """Handle dependencies that cannot be automatically validated"""
        return DependencyResult(
            dependency=dep,
            status=ValidationStatus.SKIPPED,
            message=f"Cannot validate {dep.dep_type.value} dependency automatically (manual verification required)"
        )

    def _validate_dependency(self, dep: Dependency) -> DependencyResult:
        """Validate a single dependency"""
        if dep.dep_type == DependencyType.SPEC:
            return self._validate_spec_dependency(dep)
        elif dep.dep_type == DependencyType.FILE:
            return self._validate_file_dependency(dep)
        else:
            return self._validate_other_dependency(dep)

    def validate(self) -> int:
        """Run dependency validation - returns exit code"""
        self._print_header()
        self._extract_dependencies()

        if not self.dependencies:
            print("No dependencies found in specification.")
            print("\n\033[92mDependency validation PASSED\033[0m (no dependencies)")
            return 0

        print(f"Found {len(self.dependencies)} dependencies to validate:\n")

        for dep in self.dependencies:
            result = self._validate_dependency(dep)
            self.results.append(result)

        return self._print_results()

    def _print_header(self) -> None:
        """Print validation header"""
        print(f"\n{'='*60}")
        print(f"DEPENDENCY VALIDATION: {self.file_path.name}")
        print(f"Specs Directory: {self.specs_dir}")
        print(f"{'='*60}\n")

    def _print_results(self) -> int:
        """Print validation results and return exit code"""
        # Categorize results
        missing_required = [r for r in self.results if r.status == ValidationStatus.MISSING and r.dependency.required]
        missing_optional = [r for r in self.results if r.status == ValidationStatus.MISSING and not r.dependency.required]
        skipped = [r for r in self.results if r.status == ValidationStatus.SKIPPED]
        found = [r for r in self.results if r.status == ValidationStatus.FOUND]

        # Print found dependencies
        if found:
            print("\033[92mFOUND DEPENDENCIES:\033[0m")
            print("-" * 60)
            for result in found:
                dep = result.dependency
                print(f"  [OK] {dep.dep_type.value}: {dep.name}")
                if result.path:
                    print(f"       Path: {result.path}")

        # Print skipped dependencies
        if skipped:
            print(f"\n\033[94mSKIPPED (manual verification needed):\033[0m")
            print("-" * 60)
            for result in skipped:
                dep = result.dependency
                print(f"  [?] {dep.dep_type.value}: {dep.name}")
                print(f"      {result.message}")

        # Print missing required
        if missing_required:
            print(f"\n\033[91mMISSING REQUIRED DEPENDENCIES:\033[0m")
            print("-" * 60)
            for result in missing_required:
                dep = result.dependency
                print(f"  [BLOCKED] {dep.dep_type.value}: {dep.name}")
                print(f"            Reference: {dep.reference}")
                print(f"            {result.message}")

        # Print missing optional
        if missing_optional:
            print(f"\n\033[93mMISSING OPTIONAL DEPENDENCIES:\033[0m")
            print("-" * 60)
            for result in missing_optional:
                dep = result.dependency
                print(f"  [WARN] {dep.dep_type.value}: {dep.name}")
                print(f"         {result.message}")

        # Summary
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        print(f"Total dependencies: {len(self.results)}")
        print(f"Found: {len(found)}")
        print(f"Skipped: {len(skipped)}")
        print(f"Missing (required): {len(missing_required)}")
        print(f"Missing (optional): {len(missing_optional)}")

        if missing_required:
            print(f"\n\033[91mDependency validation FAILED\033[0m")
            print("\nYou must create the following specs before proceeding:")
            for result in missing_required:
                print(f"  - {result.dependency.name} ({result.dependency.dep_type.value})")
            print("\nRun the spec creator for each missing dependency first.")
            return 1
        elif missing_optional:
            print(f"\n\033[93mDependency validation PASSED with warnings\033[0m")
            print("Some optional dependencies are missing but you can proceed.")
            return 2
        else:
            print(f"\n\033[92mDependency validation PASSED\033[0m")
            print("All dependencies are satisfied. You may proceed.")
            return 0


# =============================================================================
# Main Entry Point
# =============================================================================

def main() -> int:
    """Main entry point - returns exit code"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate specification dependencies exist before proceeding"
    )
    parser.add_argument(
        "file",
        help="Path to specification file (.md)"
    )
    parser.add_argument(
        "--specs-dir",
        help="Directory containing spec files (auto-detected if not provided)"
    )

    args = parser.parse_args()

    try:
        validator = DependencyValidator(args.file, args.specs_dir)
        return validator.validate()
    except FileNotFoundError as e:
        print(f"\033[91mError:\033[0m {e}")
        return 1
    except ValueError as e:
        print(f"\033[91mValidation Error:\033[0m {e}")
        return 1
    except PermissionError as e:
        print(f"\033[91mPermission Error:\033[0m {e}")
        return 1
    except Exception as e:
        print(f"\033[91mUnexpected Error:\033[0m {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
