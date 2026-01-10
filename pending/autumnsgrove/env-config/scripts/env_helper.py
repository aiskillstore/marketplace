#!/usr/bin/env python3
"""
Environment Configuration Helper Script

Utilities for managing .env files, validating configuration,
and handling secrets encryption.

Dependencies:
    uv add python-dotenv cryptography

Author: Claude Code
Version: 1.0.0
"""

import os
import sys
import json
import base64
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import argparse


def load_env_file(file_path: str = '.env') -> Dict[str, str]:
    """
    Parse .env file into dictionary.

    Args:
        file_path: Path to .env file

    Returns:
        Dictionary of environment variables

    Example:
        >>> vars = load_env_file('.env.development')
        >>> print(vars.get('APP_NAME'))
    """
    env_vars = {}
    path = Path(file_path)

    if not path.exists():
        print(f"⚠ File not found: {file_path}")
        return env_vars

    with open(path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Parse KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]

                env_vars[key] = value
            else:
                print(f"⚠ Skipping invalid line {line_num}: {line}")

    return env_vars


def validate_env_file(file_path: str, required_vars: List[str] = None) -> Tuple[bool, List[str]]:
    """
    Validate .env file has required variables.

    Args:
        file_path: Path to .env file
        required_vars: List of required variable names

    Returns:
        Tuple of (is_valid, missing_vars)

    Example:
        >>> valid, missing = validate_env_file('.env', ['APP_NAME', 'DATABASE_URL'])
        >>> if not valid:
        ...     print(f"Missing: {missing}")
    """
    if required_vars is None:
        required_vars = []

    env_vars = load_env_file(file_path)
    missing = [var for var in required_vars if var not in env_vars or not env_vars[var]]

    return (len(missing) == 0, missing)


def check_env_security(file_path: str = '.env') -> List[str]:
    """
    Check .env file for potential security issues.

    Args:
        file_path: Path to .env file

    Returns:
        List of security warnings

    Example:
        >>> warnings = check_env_security('.env')
        >>> for warning in warnings:
        ...     print(f"⚠ {warning}")
    """
    warnings = []
    env_vars = load_env_file(file_path)

    # Check for common insecure patterns
    insecure_patterns = [
        'xxx',
        'example',
        'test123',
        'password123',
        'changeme',
        'your-key-here',
        'replace-this',
    ]

    for key, value in env_vars.items():
        value_lower = value.lower()

        # Check for placeholder values
        if any(pattern in value_lower for pattern in insecure_patterns):
            warnings.append(f"{key} appears to contain a placeholder value: {value[:20]}...")

        # Check for empty sensitive keys
        if any(sensitive in key.upper() for sensitive in ['KEY', 'SECRET', 'PASSWORD', 'TOKEN']):
            if not value:
                warnings.append(f"{key} is empty but appears to be sensitive")

        # Check for short passwords/secrets
        if 'PASSWORD' in key.upper() or 'SECRET' in key.upper():
            if len(value) < 12:
                warnings.append(f"{key} seems too short (less than 12 characters)")

    return warnings


def compare_env_files(file1: str, file2: str) -> Dict[str, Dict[str, Optional[str]]]:
    """
    Compare two .env files and show differences.

    Args:
        file1: Path to first .env file
        file2: Path to second .env file

    Returns:
        Dictionary with 'only_in_1', 'only_in_2', 'different'

    Example:
        >>> diff = compare_env_files('.env.development', '.env.production')
        >>> print("Only in dev:", diff['only_in_1'])
    """
    env1 = load_env_file(file1)
    env2 = load_env_file(file2)

    all_keys = set(env1.keys()) | set(env2.keys())

    only_in_1 = {k: env1[k] for k in env1 if k not in env2}
    only_in_2 = {k: env2[k] for k in env2 if k not in env1}
    different = {
        k: {'file1': env1[k], 'file2': env2[k]}
        for k in all_keys
        if k in env1 and k in env2 and env1[k] != env2[k]
    }

    return {
        'only_in_1': only_in_1,
        'only_in_2': only_in_2,
        'different': different,
    }


def generate_env_template(source_file: str, output_file: str, mask_values: bool = True):
    """
    Generate .env.template from existing .env file.

    Args:
        source_file: Source .env file
        output_file: Output template file
        mask_values: If True, replace values with placeholders

    Example:
        >>> generate_env_template('.env', '.env.template')
    """
    env_vars = load_env_file(source_file)

    with open(output_file, 'w') as f:
        f.write(f"# Environment Configuration Template\n")
        f.write(f"# Generated from {source_file} on {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"# Copy to .env and fill in actual values\n\n")

        for key, value in sorted(env_vars.items()):
            if mask_values:
                # Mask sensitive values
                if any(s in key.upper() for s in ['KEY', 'SECRET', 'PASSWORD', 'TOKEN']):
                    if 'URL' in key.upper():
                        # Keep URL structure but mask credentials
                        value = 'your-service-url-here'
                    else:
                        value = 'your-secret-key-here'
                elif 'URL' in key.upper() or 'HOST' in key.upper():
                    value = 'your-service-url-here'
                elif value.lower() in ['true', 'false']:
                    # Keep boolean values
                    pass
                elif value.isdigit():
                    # Keep numeric values
                    pass

            f.write(f"{key}={value}\n")

    print(f"✓ Template generated: {output_file}")


def encrypt_secrets(input_file: str, output_file: str, password: str):
    """
    Encrypt secrets file using Fernet encryption.

    Args:
        input_file: Plain text secrets file
        output_file: Encrypted output file
        password: Encryption password

    Requires: uv add cryptography

    Example:
        >>> encrypt_secrets('secrets.json', 'secrets.encrypted', 'my-password')
    """
    try:
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
        from cryptography.hazmat.backends import default_backend
    except ImportError:
        print("❌ cryptography not installed. Run: uv add cryptography")
        sys.exit(1)

    # Read input file
    with open(input_file, 'rb') as f:
        data = f.read()

    # Derive key from password
    salt = os.urandom(16)
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))

    # Encrypt
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)

    # Write encrypted file with salt
    with open(output_file, 'wb') as f:
        f.write(salt + encrypted)

    print(f"✓ Encrypted {input_file} -> {output_file}")


def decrypt_secrets(input_file: str, password: str) -> dict:
    """
    Decrypt encrypted secrets file.

    Args:
        input_file: Encrypted secrets file
        password: Decryption password

    Returns:
        Dictionary of decrypted secrets

    Example:
        >>> secrets = decrypt_secrets('secrets.encrypted', 'my-password')
        >>> print(secrets.get('api_key'))
    """
    try:
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
        from cryptography.hazmat.backends import default_backend
    except ImportError:
        print("❌ cryptography not installed. Run: uv add cryptography")
        sys.exit(1)

    # Read encrypted file
    with open(input_file, 'rb') as f:
        data = f.read()

    # Extract salt and encrypted data
    salt = data[:16]
    encrypted = data[16:]

    # Derive key from password
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))

    # Decrypt
    fernet = Fernet(key)
    try:
        decrypted = fernet.decrypt(encrypted)
    except Exception as e:
        print(f"❌ Decryption failed: {e}")
        print("   Check password is correct")
        sys.exit(1)

    # Parse JSON
    return json.loads(decrypted)


def merge_env_files(base_file: str, override_file: str, output_file: str):
    """
    Merge two .env files, with override taking precedence.

    Args:
        base_file: Base .env file
        override_file: Override .env file
        output_file: Output merged file

    Example:
        >>> merge_env_files('.env.base', '.env.local', '.env')
    """
    base = load_env_file(base_file)
    override = load_env_file(override_file)

    # Merge (override takes precedence)
    merged = {**base, **override}

    # Write merged file
    with open(output_file, 'w') as f:
        f.write(f"# Merged from {base_file} and {override_file}\n")
        f.write(f"# Generated: {datetime.now().isoformat()}\n\n")

        for key, value in sorted(merged.items()):
            # Add quotes if value contains spaces
            if ' ' in value:
                value = f'"{value}"'
            f.write(f"{key}={value}\n")

    print(f"✓ Merged {base_file} + {override_file} -> {output_file}")


def print_env_diff(diff: Dict[str, Dict[str, Optional[str]]], file1_name: str, file2_name: str):
    """Pretty print environment file differences."""
    print(f"\n{'='*60}")
    print(f"Comparing: {file1_name} vs {file2_name}")
    print(f"{'='*60}\n")

    if diff['only_in_1']:
        print(f"Only in {file1_name}:")
        for key, value in diff['only_in_1'].items():
            print(f"  {key}={value[:50]}...")
        print()

    if diff['only_in_2']:
        print(f"Only in {file2_name}:")
        for key, value in diff['only_in_2'].items():
            print(f"  {key}={value[:50]}...")
        print()

    if diff['different']:
        print("Different values:")
        for key, values in diff['different'].items():
            print(f"  {key}:")
            print(f"    {file1_name}: {values['file1'][:50]}...")
            print(f"    {file2_name}: {values['file2'][:50]}...")
        print()

    if not any(diff.values()):
        print("✓ Files are identical")


# CLI Interface
def main():
    """Command-line interface for env helper utilities."""
    parser = argparse.ArgumentParser(
        description='Environment configuration helper utilities',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate .env file
  python env_helper.py validate .env --required APP_NAME DATABASE_URL

  # Check security issues
  python env_helper.py check .env

  # Compare environments
  python env_helper.py compare .env.development .env.production

  # Generate template
  python env_helper.py template .env .env.template

  # Encrypt secrets
  python env_helper.py encrypt secrets.json secrets.encrypted

  # Decrypt secrets
  python env_helper.py decrypt secrets.encrypted
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate .env file')
    validate_parser.add_argument('file', help='.env file to validate')
    validate_parser.add_argument('--required', nargs='+', help='Required variables')

    # Check command
    check_parser = subparsers.add_parser('check', help='Security check .env file')
    check_parser.add_argument('file', help='.env file to check')

    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare two .env files')
    compare_parser.add_argument('file1', help='First .env file')
    compare_parser.add_argument('file2', help='Second .env file')

    # Template command
    template_parser = subparsers.add_parser('template', help='Generate .env template')
    template_parser.add_argument('source', help='Source .env file')
    template_parser.add_argument('output', help='Output template file')
    template_parser.add_argument('--no-mask', action='store_true', help='Keep original values')

    # Encrypt command
    encrypt_parser = subparsers.add_parser('encrypt', help='Encrypt secrets file')
    encrypt_parser.add_argument('input', help='Input file (plain text)')
    encrypt_parser.add_argument('output', help='Output file (encrypted)')
    encrypt_parser.add_argument('--password', help='Encryption password (or use stdin)')

    # Decrypt command
    decrypt_parser = subparsers.add_parser('decrypt', help='Decrypt secrets file')
    decrypt_parser.add_argument('input', help='Input file (encrypted)')
    decrypt_parser.add_argument('--password', help='Decryption password (or use stdin)')
    decrypt_parser.add_argument('--output', help='Output file (default: stdout)')

    # Merge command
    merge_parser = subparsers.add_parser('merge', help='Merge two .env files')
    merge_parser.add_argument('base', help='Base .env file')
    merge_parser.add_argument('override', help='Override .env file')
    merge_parser.add_argument('output', help='Output merged file')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    if args.command == 'validate':
        valid, missing = validate_env_file(args.file, args.required or [])
        if valid:
            print(f"✓ {args.file} is valid")
        else:
            print(f"❌ {args.file} is missing required variables:")
            for var in missing:
                print(f"  - {var}")
            sys.exit(1)

    elif args.command == 'check':
        warnings = check_env_security(args.file)
        if warnings:
            print(f"⚠ Security issues found in {args.file}:")
            for warning in warnings:
                print(f"  - {warning}")
        else:
            print(f"✓ No security issues found in {args.file}")

    elif args.command == 'compare':
        diff = compare_env_files(args.file1, args.file2)
        print_env_diff(diff, args.file1, args.file2)

    elif args.command == 'template':
        generate_env_template(args.source, args.output, mask_values=not args.no_mask)

    elif args.command == 'encrypt':
        password = args.password
        if not password:
            import getpass
            password = getpass.getpass('Encryption password: ')
        encrypt_secrets(args.input, args.output, password)

    elif args.command == 'decrypt':
        password = args.password
        if not password:
            import getpass
            password = getpass.getpass('Decryption password: ')
        secrets = decrypt_secrets(args.input, password)

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(secrets, f, indent=2)
            print(f"✓ Decrypted to {args.output}")
        else:
            print(json.dumps(secrets, indent=2))

    elif args.command == 'merge':
        merge_env_files(args.base, args.override, args.output)


if __name__ == '__main__':
    main()
