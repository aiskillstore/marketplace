#!/usr/bin/env python3
"""
Auto-fix engine with rollback support
Safely applies security fixes with the ability to undo changes
"""
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
import re


class AutoFixEngine:
    """
    Automatically applies security fixes with rollback capability
    """
    
    def __init__(self, project_path: str = '.'):
        self.project_path = Path(project_path)
        self.backup_dir = self.project_path / '.vibe-security' / 'backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.backup_dir / 'fix_history.json'
        self.history = self._load_history()
        
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load fix history"""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_history(self):
        """Save fix history"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def _create_backup(self, filepath: Path) -> str:
        """Create backup of file before modification"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_hash = hashlib.md5(filepath.read_bytes()).hexdigest()[:8]
        
        backup_name = f"{filepath.name}.{timestamp}.{file_hash}.backup"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(filepath, backup_path)
        
        return str(backup_path)
    
    def apply_fix(self,
                  filepath: str,
                  vulnerability_type: str,
                  line_number: int,
                  original_code: str,
                  fixed_code: str,
                  dry_run: bool = False) -> Dict[str, Any]:
        """
        Apply a security fix to a file
        
        Args:
            filepath: Path to file to fix
            vulnerability_type: Type of vulnerability being fixed
            line_number: Line number of vulnerable code
            original_code: Expected original code (for verification)
            fixed_code: Fixed code to apply
            dry_run: If True, only simulate the fix
        
        Returns:
            Result dictionary with success status and details
        """
        file_path = Path(filepath)
        
        if not file_path.exists():
            return {
                'success': False,
                'error': f'File not found: {filepath}'
            }
        
        # Read file content
        content = file_path.read_text()
        lines = content.split('\n')
        
        # Verify line number is valid
        if line_number < 1 or line_number > len(lines):
            return {
                'success': False,
                'error': f'Invalid line number: {line_number}'
            }
        
        # Get the actual line (1-indexed to 0-indexed)
        actual_line = lines[line_number - 1]
        
        # Verify original code matches (fuzzy match)
        if not self._fuzzy_match(actual_line, original_code):
            return {
                'success': False,
                'error': 'Original code does not match expected',
                'expected': original_code,
                'actual': actual_line
            }
        
        if dry_run:
            return {
                'success': True,
                'dry_run': True,
                'file': str(file_path),
                'line': line_number,
                'original': actual_line,
                'fixed': fixed_code,
                'message': 'Dry run - no changes made'
            }
        
        # Create backup
        backup_path = self._create_backup(file_path)
        
        # Apply fix
        lines[line_number - 1] = fixed_code
        new_content = '\n'.join(lines)
        
        # Write fixed content
        file_path.write_text(new_content)
        
        # Record in history
        fix_record = {
            'timestamp': datetime.now().isoformat(),
            'file': str(file_path),
            'line': line_number,
            'vulnerability_type': vulnerability_type,
            'original_code': actual_line,
            'fixed_code': fixed_code,
            'backup_path': backup_path
        }
        
        self.history.append(fix_record)
        self._save_history()
        
        return {
            'success': True,
            'file': str(file_path),
            'line': line_number,
            'vulnerability_type': vulnerability_type,
            'backup': backup_path,
            'fix_id': len(self.history) - 1
        }
    
    def rollback_fix(self, fix_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Rollback a previously applied fix
        
        Args:
            fix_id: ID of fix to rollback (None = last fix)
        
        Returns:
            Result dictionary
        """
        if not self.history:
            return {
                'success': False,
                'error': 'No fixes to rollback'
            }
        
        if fix_id is None:
            fix_id = len(self.history) - 1
        
        if fix_id < 0 or fix_id >= len(self.history):
            return {
                'success': False,
                'error': f'Invalid fix ID: {fix_id}'
            }
        
        fix_record = self.history[fix_id]
        backup_path = Path(fix_record['backup_path'])
        target_file = Path(fix_record['file'])
        
        if not backup_path.exists():
            return {
                'success': False,
                'error': f'Backup file not found: {backup_path}'
            }
        
        # Restore from backup
        shutil.copy2(backup_path, target_file)
        
        # Mark as rolled back in history
        fix_record['rolled_back'] = True
        fix_record['rollback_timestamp'] = datetime.now().isoformat()
        self._save_history()
        
        return {
            'success': True,
            'file': str(target_file),
            'fix_id': fix_id,
            'restored_from': str(backup_path)
        }
    
    def batch_apply_fixes(self,
                         fixes: List[Dict[str, Any]],
                         dry_run: bool = False,
                         stop_on_error: bool = False) -> Dict[str, Any]:
        """
        Apply multiple fixes in batch
        
        Args:
            fixes: List of fix dictionaries
            dry_run: Simulate fixes without applying
            stop_on_error: Stop on first error
        
        Returns:
            Summary of results
        """
        results = {
            'total': len(fixes),
            'successful': 0,
            'failed': 0,
            'fixes': []
        }
        
        for fix in fixes:
            result = self.apply_fix(
                filepath=fix['file'],
                vulnerability_type=fix['type'],
                line_number=fix['line'],
                original_code=fix['original'],
                fixed_code=fix['fixed'],
                dry_run=dry_run
            )
            
            results['fixes'].append(result)
            
            if result['success']:
                results['successful'] += 1
            else:
                results['failed'] += 1
                if stop_on_error:
                    break
        
        return results
    
    def _fuzzy_match(self, actual: str, expected: str, threshold: float = 0.8) -> bool:
        """
        Fuzzy match between actual and expected code
        Ignores whitespace differences
        """
        # Normalize whitespace
        actual_normalized = ' '.join(actual.split())
        expected_normalized = ' '.join(expected.split())
        
        # Exact match after normalization
        if actual_normalized == expected_normalized:
            return True
        
        # Check if expected is substring of actual
        if expected_normalized in actual_normalized:
            return True
        
        # Calculate similarity ratio
        actual_set = set(actual_normalized.split())
        expected_set = set(expected_normalized.split())
        
        if not expected_set:
            return False
        
        intersection = actual_set & expected_set
        similarity = len(intersection) / len(expected_set)
        
        return similarity >= threshold
    
    def list_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent fix history"""
        return self.history[-limit:]
    
    def rollback_all(self, since: Optional[str] = None) -> Dict[str, Any]:
        """
        Rollback all fixes since a timestamp
        
        Args:
            since: ISO timestamp (None = all fixes)
        
        Returns:
            Summary of rollbacks
        """
        fixes_to_rollback = []
        
        for i, fix in enumerate(self.history):
            if fix.get('rolled_back'):
                continue
            
            if since is None or fix['timestamp'] >= since:
                fixes_to_rollback.append(i)
        
        results = {
            'total': len(fixes_to_rollback),
            'successful': 0,
            'failed': 0
        }
        
        # Rollback in reverse order
        for fix_id in reversed(fixes_to_rollback):
            result = self.rollback_fix(fix_id)
            
            if result['success']:
                results['successful'] += 1
            else:
                results['failed'] += 1
        
        return results
    
    def cleanup_backups(self, days: int = 30) -> Dict[str, Any]:
        """
        Clean up old backup files
        
        Args:
            days: Delete backups older than this many days
        
        Returns:
            Cleanup summary
        """
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        deleted = 0
        
        for backup_file in self.backup_dir.glob('*.backup'):
            mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
            
            if mtime < cutoff:
                backup_file.unlink()
                deleted += 1
        
        return {
            'deleted': deleted,
            'cutoff_date': cutoff.isoformat()
        }


def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-fix engine with rollback support')
    parser.add_argument('command', choices=['apply', 'rollback', 'history', 'cleanup'])
    parser.add_argument('--file', help='File to fix')
    parser.add_argument('--type', help='Vulnerability type')
    parser.add_argument('--line', type=int, help='Line number')
    parser.add_argument('--original', help='Original code')
    parser.add_argument('--fixed', help='Fixed code')
    parser.add_argument('--fix-id', type=int, help='Fix ID to rollback')
    parser.add_argument('--dry-run', action='store_true', help='Simulate without applying')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    engine = AutoFixEngine()
    
    if args.command == 'apply':
        result = engine.apply_fix(
            filepath=args.file,
            vulnerability_type=args.type,
            line_number=args.line,
            original_code=args.original,
            fixed_code=args.fixed,
            dry_run=args.dry_run
        )
    
    elif args.command == 'rollback':
        result = engine.rollback_fix(args.fix_id)
    
    elif args.command == 'history':
        result = {'history': engine.list_history()}
    
    elif args.command == 'cleanup':
        result = engine.cleanup_backups()
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
