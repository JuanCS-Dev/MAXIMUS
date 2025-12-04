#!/usr/bin/env python3
"""Fix multiline print statements."""
import re
import sys
from pathlib import Path


def fix_multiline_prints(filepath: Path) -> int:
    """
    Fix multiline print statements in a file.

    Returns:
        Number of prints fixed
    """
    content = filepath.read_text()
    original_count = content.count('print(')

    # Pattern for multiline prints: print(\n    "...\n    "...\n)
    # Replace with logger.info(\n    "...\n    "...\n)

    # Multi-line print with parentheses
    content = re.sub(
        r'print\(\s*\n',
        r'logger.info(\n',
        content
    )

    new_count = content.count('print(')
    fixed = original_count - new_count

    if fixed > 0:
        filepath.write_text(content)

    return fixed


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_multiline_prints.py <file_path>")
        sys.exit(1)

    filepath = Path(sys.argv[1])

    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    fixed = fix_multiline_prints(filepath)
    print(f"✅ Fixed {fixed} multiline prints in {filepath.name}")
