#!/usr/bin/env python3
"""
Script to systematically replace datetime.utcnow() with datetime.now(timezone.utc)
throughout the codebase.

This script helps automate the EVE-35 timezone modernization effort.
"""

import os
import re
from pathlib import Path


def fix_datetime_utcnow_in_file(file_path: Path) -> bool:
    """
    Fix datetime.utcnow() usage in a single file.
    
    Returns:
        True if changes were made, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Check if file uses datetime.utcnow()
        if 'datetime.utcnow()' not in content:
            return False
        
        # Add timezone import if datetime is imported but timezone is not
        if 'from datetime import datetime' in content and 'timezone' not in content:
            content = content.replace(
                'from datetime import datetime',
                'from datetime import datetime, timezone'
            )
        elif 'import datetime' in content and 'timezone' not in content:
            content = content.replace(
                'import datetime',
                'import datetime\nfrom datetime import timezone'
            )
        
        # Replace datetime.utcnow() with datetime.now(timezone.utc)
        content = content.replace('datetime.utcnow()', 'datetime.now(timezone.utc)')
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Main function to process all Python files in the project."""
    project_root = Path(__file__).parent.parent
    files_processed = 0
    files_changed = 0
    
    # Find all Python files
    python_files = list(project_root.rglob('*.py'))
    
    print(f"Found {len(python_files)} Python files to process...")
    
    for file_path in python_files:
        # Skip __pycache__ and .git directories
        if '__pycache__' in str(file_path) or '.git' in str(file_path):
            continue
            
        files_processed += 1
        
        if fix_datetime_utcnow_in_file(file_path):
            files_changed += 1
            print(f"✅ Updated: {file_path.relative_to(project_root)}")
    
    print(f"\nSummary:")
    print(f"  Files processed: {files_processed}")
    print(f"  Files changed: {files_changed}")
    
    if files_changed > 0:
        print(f"\nNext steps:")
        print(f"  1. Run tests to verify changes: python -m pytest")
        print(f"  2. Check for any remaining warnings")
        print(f"  3. Review changes before committing")


if __name__ == "__main__":
    main()
